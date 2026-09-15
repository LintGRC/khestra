from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime, timezone
import io
import json
import os


def _try_parse_tiptap(content: str) -> dict | None:
    if not content:
        return None
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and parsed.get("type") == "doc":
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _is_fresh(date_str: str, max_days: int = 90) -> bool:
    if not date_str:
        return False
    try:
        dt = datetime.strptime(date_str.split(" ")[0] if " " in date_str else date_str[:10], "%Y-%m-%d")
        return (datetime.now() - dt).days <= max_days
    except (ValueError, IndexError):
        return False


router = APIRouter()


# ─── Pydantic request models ──────────────────────────


class PolicyCreateBody(BaseModel):
    title: str = ""
    name: str = ""
    description: str = ""
    content: str = ""
    version: str = "1.0"
    owner: str = ""
    framework_tags: list[str] = []
    mapped_controls: dict[str, list[str]] = {}
    mapped_controls_list: list[str] = []
    workspace_id: str = ""


class PolicyUpdateBody(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    version: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    framework_tags: Optional[list[str]] = None
    mapped_controls: Optional[dict[str, list[str]]] = None
    mapped_controls_list: Optional[list[str]] = None
    sections: Optional[list[dict]] = None
    change_notes: str = ""
    changed_by: str = ""


class AttestationBody(BaseModel):
    policy_id: str = ""
    user_name: str = ""
    notes: str = ""


class GenerateBody(BaseModel):
    template: str = ""


# ─── Routes ───────────────────────────────────────────
# IMPORTANT: static sub-paths (/templates, /attestations) must be
# defined BEFORE /{policy_id} wildcard routes so FastAPI matches
# them first.

@router.get("/api/policies")
def get_policies(framework_tag: Optional[str] = Query(None)):
    from .store import list_documents
    return {"policies": list_documents(framework_tag=framework_tag)}


@router.get("/api/policies/templates")
def get_templates():
    from .store import list_templates
    return {"templates": list_templates()}


@router.get("/api/policies/attestations")
def list_all_attestations():
    from .store import list_attestations
    return {"attestations": list_attestations()}


@router.post("/api/policies")
def create_policy(body: PolicyCreateBody):
    from .store import create_document
    title = body.title or body.name
    mc = body.mapped_controls
    if body.mapped_controls_list:
        mc = {"default": body.mapped_controls_list}
    return {"policy": create_document(
        title=title,
        description=body.description,
        content=body.content,
        owner=body.owner,
        framework_tags=body.framework_tags,
        mapped_controls=mc,
        workspace_id=body.workspace_id,
    )}


# ─── {policy_id} wildcard routes ──────────────────────


@router.get("/api/policies/{policy_id}")
def get_policy(policy_id: str):
    from .store import get_document
    doc = get_document(policy_id)
    if not doc:
        raise HTTPException(404, "Policy not found")
    tiptap_json = _try_parse_tiptap(doc.get("content", ""))
    result = {"policy": doc}
    if tiptap_json:
        result["tiptap_json"] = tiptap_json
    return result


@router.patch("/api/policies/{policy_id}")
def update_policy(policy_id: str, body: PolicyUpdateBody):
    from .store import update_document
    title = body.title or body.name
    mc = body.mapped_controls
    if body.mapped_controls_list:
        mc = {"default": body.mapped_controls_list}
    doc = update_document(
        policy_id,
        title=title,
        description=body.description,
        content=body.content,
        owner=body.owner,
        status=body.status,
        framework_tags=body.framework_tags,
        mapped_controls=body.mapped_controls,
        sections=body.sections,
        change_notes=body.change_notes,
        changed_by=body.changed_by,
    )
    if not doc:
        raise HTTPException(404, "Policy not found")
    return {"policy": doc}


@router.delete("/api/policies/{policy_id}")
def delete_policy(policy_id: str):
    from .store import delete_document
    if not delete_document(policy_id):
        raise HTTPException(404, "Policy not found")
    return {"status": "deleted"}


@router.get("/api/policies/{policy_id}/evidence-insights")
def get_policy_evidence_insights(policy_id: str):
    from .store import get_document
    doc = get_document(policy_id)
    if not doc:
        raise HTTPException(404, "Policy not found")

    mc = doc.get("mapped_controls", {})
    if isinstance(mc, list):
        control_ids = mc
    elif isinstance(mc, dict):
        control_ids = [c for ids in mc.values() for c in (ids if isinstance(ids, list) else [ids])]
    else:
        control_ids = []

    if not control_ids:
        return {"total_controls": 0, "controls_with_evidence": 0, "total_evidence": 0, "evidence_by_control": {}}

    evidence_by_control: dict[str, list[dict]] = {}
    for cid in set(control_ids):
        try:
            from evidence_hub.store import list_evidence
            items = list_evidence(control_id=cid)
        except Exception:
            items = []
        evidence_by_control[cid] = [
            {
                "id": e.get("id", ""),
                "filename": e.get("filename", ""),
                "review_status": e.get("review_status", "pending"),
                "upload_date": e.get("uploaded_at", ""),
                "is_auto": str(e.get("filename", "")).startswith("collector_"),
                "fresh": _is_fresh(e.get("uploaded_at", "")),
            }
            for e in items
        ]

    controls_with_evidence = sum(1 for v in evidence_by_control.values() if v)
    total_evidence = sum(len(v) for v in evidence_by_control.values())
    fresh_count = sum(1 for v in evidence_by_control.values() for e in v if e["fresh"])
    auto_count = sum(1 for v in evidence_by_control.values() for e in v if e["is_auto"])
    reviewed_count = sum(1 for v in evidence_by_control.values() for e in v if e["review_status"] == "approved")

    return {
        "total_controls": len(control_ids),
        "controls_with_evidence": controls_with_evidence,
        "total_evidence": total_evidence,
        "fresh_count": fresh_count,
        "auto_count": auto_count,
        "reviewed_count": reviewed_count,
        "evidence_by_control": evidence_by_control,
    }


@router.post("/api/policies/{policy_id}/generate-ai")
def generate_ai_policy_content(policy_id: str, body: GenerateBody):
    from .store import get_document, list_templates
    import urllib.request

    doc = get_document(policy_id)
    if not doc:
        raise HTTPException(404, "Policy not found")

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(400, "OPENAI_API_KEY not set — configure it in your environment")

    # Build context
    mc = doc.get("mapped_controls", {})
    if isinstance(mc, list):
        control_ids = mc
    elif isinstance(mc, dict):
        control_ids = [c for ids in mc.values() for c in (ids if isinstance(ids, list) else [ids])]
    else:
        control_ids = []

    # Try to get control descriptions from SOC2 catalog or other sources
    control_context = ""
    if control_ids:
        try:
            from soc2_catalog import SOC2_CONTROLS
            for cid in control_ids:
                if cid in SOC2_CONTROLS:
                    meta = SOC2_CONTROLS[cid]
                    control_context += f"- {cid}: {meta['title']} — {meta['description']}\n"
        except ImportError:
            control_context = "\n".join(f"- {cid}" for cid in control_ids)

    current_content = doc.get("content", "")
    if current_content:
        try:
            parsed = json.loads(current_content)
            if isinstance(parsed, dict) and parsed.get("type") == "doc":
                current_content = "Current policy content is already in structured format."
            else:
                current_content = f"Current content: {current_content[:500]}"
        except (json.JSONDecodeError, TypeError):
            current_content = f"Current content: {current_content[:500]}"
    else:
        current_content = "No existing content."

    template_list = list_templates()
    available_templates = "\n".join(f"- {t['name']} ({t['key']}): {t['description']}" for t in template_list[:5])

    system_prompt = f"""You are a compliance policy writer. Write clear, professional policy content for an organization's compliance program.

Organization context:
- Policy title: {doc.get('title', 'Untitled Policy')}
- Description: {doc.get('description', '')}
- Mapped controls: {', '.join(control_ids) if control_ids else 'None yet'}

Control requirements:
{control_context if control_context else 'General compliance best practices apply.'}

{current_content}
"""

    if body.template:
        system_prompt += f"\n\nThe user wants content for the following section/topic: {body.template}"

    user_prompt = """Generate the policy content as structured JSON for a TipTap editor. 
Output ONLY valid JSON with this structure:
{"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "..."}]}]}

Use headings (level 2 and 3), paragraphs, bullet lists, and bold text where appropriate.
Include standard compliance policy sections: Purpose, Scope, Policy, Responsibilities, Enforcement, Related Documents.
Use {{company_name}} and {{system_name}} as placeholders where the company name or system name would appear.
Keep the content concise and actionable — 3-6 paragraphs per section."""

    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt + (f"\n\nSpecific instruction: {body.template}" if body.template else "")},
                ],
                "temperature": 0.3,
                "max_tokens": 4096,
            }).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            raw = result["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(502, f"AI generation failed: {e}")

    # Parse the response — it might be wrapped in markdown code blocks
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
        cleaned = cleaned.rsplit("```", 1)[0].strip()

    try:
        tiptap_json = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: wrap as paragraph text
        tiptap_json = {
            "type": "doc",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": cleaned[:3000]}]}],
        }

    return {"tiptap_json": tiptap_json}


@router.post("/api/policies/{policy_id}/generate")
def generate_from_template(policy_id: str, body: GenerateBody):
    from .store import get_document, update_document, list_templates
    from .md_to_tiptap import markdown_to_tiptap
    doc = get_document(policy_id)
    if not doc:
        raise HTTPException(404, "Policy not found")

    templates = list_templates()
    t = next((t for t in templates if t["key"] == body.template), None)
    if not t:
        raise HTTPException(400, f"Unknown template key: {body.template}")

    from datetime import date
    org_name = doc.get("title", "Your Organization")
    md_content = t["content"].replace("{{ORG_NAME}}", org_name).replace("{{DATE}}", date.today().strftime("%B %d, %Y"))

    ai_controls = list(dict.fromkeys(
        t.get("mapped_controls_eu_ai_act", [])
        + t.get("mapped_controls_nist_ai_rmf", [])
        + t.get("mapped_controls_iso_42001", [])
    ))
    mapped_controls = {
        "soc2": t.get("mapped_controls_soc2", []),
        "cmmc": t.get("mapped_controls_cmmc", []),
        "aigov": ai_controls,
        "eu_ai_act": t.get("mapped_controls_eu_ai_act", []),
        "nist_ai_rmf": t.get("mapped_controls_nist_ai_rmf", []),
        "iso42001": t.get("mapped_controls_iso_42001", []),
        "iso27001": t.get("mapped_controls_iso27001", []),
    }
    mapped_controls = {k: v for k, v in mapped_controls.items() if v}
    if not mapped_controls:
        mapped_controls = {}

    tiptap_content = markdown_to_tiptap(md_content)
    content_json = json.dumps(tiptap_content)

    updated = update_document(
        policy_id,
        content=content_json,
        description=t["description"],
        mapped_controls=mapped_controls,
        change_notes=f"Generated from template: {t['name']}",
        changed_by="system",
    )
    return {"policy": updated, "tiptap_json": tiptap_content}


@router.get("/api/policies/{policy_id}/export")
def export_policy(policy_id: str):
    from .store import get_document
    doc = get_document(policy_id)
    if not doc:
        raise HTTPException(404, "Policy not found")
    content = doc.get("content", "")
    if not content:
        raise HTTPException(400, "Policy has no content to export")

    from .export import generate_docx
    docx_bytes = generate_docx(
        name=doc["title"],
        content=content,
        version=str(doc.get("version", 1)),
    )
    filename = f"{doc['title'].replace(' ', '_')}_v{doc.get('version', 1)}.docx"
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/policies/{policy_id}/versions")
def get_versions(policy_id: str):
    from .store import list_versions
    return {"versions": list_versions(policy_id)}


@router.get("/api/policies/{policy_id}/versions/{version}")
def get_version(policy_id: str, version: int):
    from .store import get_version
    v = get_version(policy_id, version)
    if not v:
        raise HTTPException(404, "Version not found")
    return {"version": v}


@router.get("/api/policies/{policy_id}/attestations")
def get_attestations(policy_id: str):
    from .store import list_attestations
    return {"attestations": list_attestations(policy_id)}


@router.post("/api/policies/{policy_id}/attest")
def attest_policy(policy_id: str, body: AttestationBody):
    from .store import create_attestation
    from entra_auth import auth_enabled, get_auth_user
    user_name = body.user_name
    user_id = ""
    try:
        if auth_enabled():
            user = get_auth_user()
            if user:
                user_name = user.display_name or user.email or user_name
                user_id = user.oid or ""
    except Exception:
        pass
    att = create_attestation(
        policy_id=policy_id,
        user_name=user_name,
        user_id=user_id,
        notes=body.notes,
    )
    if not att:
        raise HTTPException(404, "Policy not found")
    if isinstance(att, dict) and att.get("duplicate"):
        return {"attestation": att["attestation"], "duplicate": True}
    return {"attestation": att}


# ─── Approval Workflow ─────────────────────────────────


class ApprovalBody(BaseModel):
    approved_by: str = ""
    rejection_notes: str = ""


@router.post("/api/policies/{policy_id}/submit")
def submit_policy(policy_id: str):
    from .store import submit_for_review
    try:
        doc = submit_for_review(policy_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not doc:
        raise HTTPException(404, "Policy not found")
    return {"policy": doc}


@router.post("/api/policies/{policy_id}/approve")
def approve_policy(policy_id: str, body: ApprovalBody = ApprovalBody()):
    from .store import approve_document
    from entra_auth import auth_enabled, get_auth_user
    approved_by = body.approved_by
    try:
        if auth_enabled():
            user = get_auth_user()
            if user:
                approved_by = user.display_name or user.email or approved_by
    except Exception:
        pass
    try:
        doc = approve_document(policy_id, approved_by=approved_by)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not doc:
        raise HTTPException(404, "Policy not found")
    return {"policy": doc}


@router.post("/api/policies/{policy_id}/publish")
def publish_policy(policy_id: str):
    from .store import publish_document
    try:
        doc = publish_document(policy_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not doc:
        raise HTTPException(404, "Policy not found")
    return {"policy": doc}


@router.post("/api/policies/{policy_id}/reject")
def reject_policy(policy_id: str, body: ApprovalBody = ApprovalBody()):
    from .store import reject_document
    try:
        doc = reject_document(policy_id, rejection_notes=body.rejection_notes)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not doc:
        raise HTTPException(404, "Policy not found")
    return {"policy": doc}


# ─── Cross-Framework Mappings ─────────────────────────


class MappingCreateBody(BaseModel):
    framework: str
    control_id: str
    control_label: str = ""


@router.get("/api/policies/{policy_id}/mappings")
def get_mappings(policy_id: str):
    from .store import list_mappings
    return {"mappings": list_mappings(policy_id)}


@router.post("/api/policies/{policy_id}/mappings")
def create_mapping(policy_id: str, body: MappingCreateBody):
    from .store import create_mapping
    m = create_mapping(
        policy_id=policy_id,
        framework=body.framework,
        control_id=body.control_id,
        control_label=body.control_label,
    )
    if not m:
        raise HTTPException(404, "Policy not found")
    return {"mapping": m}


@router.delete("/api/policies/{policy_id}/mappings/{mapping_id}")
def delete_mapping(policy_id: str, mapping_id: str):
    from .store import delete_mapping
    if not delete_mapping(mapping_id):
        raise HTTPException(404, "Mapping not found")
    return {"status": "deleted"}


@router.get("/api/policies/due-review")
def get_due_for_review():
    from .review_reminders import get_policies_due_review
    due = get_policies_due_review()
    return {"policies": due, "count": len(due)}
