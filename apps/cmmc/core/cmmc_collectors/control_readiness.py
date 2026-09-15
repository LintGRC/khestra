"""Per-control readiness checklist — what's done vs missing."""

from __future__ import annotations

from typing import Any, Dict, List

_GAP_STATUSES = {"NOT STARTED", "IN PROGRESS", "INCOMPLETE", "DEFERRED"}


def compute_control_readiness(
    control_id: str,
    answer: Dict[str, Any],
    linking_profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    profile = linking_profile or {}
    items: List[Dict[str, Any]] = []

    status = (answer.get("status") or "NOT STARTED").strip()
    narrative = (answer.get("implementation_narrative") or "").strip()

    # ── Always-shown items ──────────────────────────────

    if status == "NOT APPLICABLE":
        justification = (answer.get("assessor_notes") or "").strip()
        items.append({
            "id": "na_justification",
            "label": "N/A justification",
            "done": len(justification) > 20,
            "required": True,
            "hint": "Explain why this control is not applicable to your environment",
        })
        items.append({
            "id": "narrative",
            "label": "Implementation narrative (optional for N/A)",
            "done": True,
            "required": False,
            "hint": "Helpful context for assessors but not required when marked N/A",
        })

        items.append({
            "id": "status",
            "label": "Status determined",
            "done": True,
            "required": True,
            "hint": "Control marked not applicable",
        })

        required = [it for it in items if it["required"]]
        required_done = [it for it in required if it["done"]]
        pct = round(len(required_done) / len(required) * 100) if required else 100
        label = "Complete" if pct == 100 else "Needs work" if pct >= 50 else "Incomplete"
        return {
            "items": items,
            "readiness_pct": pct,
            "readiness_label": label,
            "required_count": len(required),
            "done_count": len(required_done),
        }

    # ── Not N/A — show standard items ───────────────────

    items.append({
        "id": "narrative",
        "label": "Implementation narrative",
        "done": len(narrative) > 0,
        "required": True,
        "hint": "Write how your organization meets this control",
    })

    evidence = answer.get("evidence") or []
    items.append({
        "id": "evidence",
        "label": f"Evidence uploaded ({len(evidence)})",
        "done": len(evidence) > 0,
        "required": True,
        "hint": "Upload evidence to the Evidence Hub",
    })

    req_policies = profile.get("policies") or []
    if req_policies:
        linked_titles = {p.get("title", "") for p in (answer.get("linked_policies") or [])}
        matched = sum(1 for rp in req_policies if rp in linked_titles)
        items.append({
            "id": "policies",
            "label": f"Policy linked ({matched}/{len(req_policies)})",
            "done": matched >= len(req_policies),
            "required": True,
            "hint": f"Suggested: {', '.join(req_policies[:3])}",
        })

    if profile.get("assets") is not None:
        linked_assets = answer.get("linked_assets") or []
        items.append({
            "id": "assets",
            "label": "Asset linked",
            "done": len(linked_assets) > 0,
            "required": True,
            "hint": "Link an asset to this control",
        })

    if profile.get("team"):
        linked_team = answer.get("linked_team") or []
        items.append({
            "id": "team",
            "label": "Team member linked",
            "done": len(linked_team) > 0,
            "required": True,
            "hint": "Link a team member to this control",
        })

    owner = (answer.get("owner") or "").strip()
    items.append({
        "id": "owner",
        "label": "Owner assigned",
        "done": bool(owner),
        "required": False,
        "hint": "Assign a responsible owner",
    })

    items.append({
        "id": "status",
        "label": "Status determined",
        "done": status != "NOT STARTED",
        "required": True,
        "hint": "Set the control status above",
    })

    if status in _GAP_STATUSES:
        remediation = (answer.get("remediation_plan") or "").strip()
        items.append({
            "id": "poam",
            "label": "POA&M entry",
            "done": len(remediation) > 0,
            "required": True,
            "hint": "Describe the gap, planned remediation, owner, and target date",
        })

    # ── Scoring ─────────────────────────────────────────

    required = [it for it in items if it["required"]]
    required_done = [it for it in required if it["done"]]
    pct = round(len(required_done) / len(required) * 100) if required else 100

    if pct == 100:
        label = "Complete"
    elif pct >= 50:
        label = "Needs work"
    else:
        label = "Incomplete"

    return {
        "items": items,
        "readiness_pct": pct,
        "readiness_label": label,
        "required_count": len(required),
        "done_count": len(required_done),
    }
