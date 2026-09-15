"""Polish SSP narratives with an OpenAI-compatible chat API (BYOK via env)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List

from ai_config import api_key, model, ssp_extra_instructions
from cmmc_collectors.ssp_draft_linter import verified_telemetry_json

_SYSTEM_PROMPT = """You are a strict, literal technical documentation assistant drafting CMMC Level 2 SSP implementation text.

You are a linguistic synthesizer, not a source of facts.

Hard rules:
- Prefer facts from <EXISTING_SSP_FACTS> only when that block contains real prose. If it says none / draft from verified inputs only, ignore any prior narrative — draft only from org context, 171A objectives, mappings, evidence artifacts, and assessment plan.
- Use ONLY products, vendors, and policies explicitly listed in <CONTROL_MAPPINGS_AND_ARTIFACTS> or <VERIFIED_COLLECTOR_TELEMETRY>. If a vendor or product name is not present in these blocks, do not mention it.
- Also use <VERIFIED_COLLECTOR_TELEMETRY>, <CONTROL_MAPPINGS_AND_ARTIFACTS>, and <ASSESSMENT_OBJECTIVES_171A>.
- <ASSESSMENT_OBJECTIVES_171A> is the coverage checklist. When <EXISTING_SSP_FACTS> already describes how the control is implemented, refine that prose to cover the objectives — do NOT add gap or "not documented" sentences.
- Only omit a detail — never invent a gap paragraph, remediation essay, or critique of missing evidence.
- <REGULATORY_REFERENCE_ONLY_DO_NOT_ASSUME_IMPLEMENTED> is generic catalog text — NEVER state anything from it is implemented unless the same detail appears in existing facts or verified telemetry.
- Never invent policy names, product settings, user counts, dates, ticket IDs, or controls. Never substitute a different product or vendor name for one found in the facts — for example, if the evidence mentions Microsoft Entra ID, do not rewrite it as AWS IAM.
- Never invent person names. Only name people who appear in Linked team, owner, or assessment-plan Interview/Examine/Test text. Do not invent roles or staff.
- Never invent or substitute a different organization name. Use exactly the organization name provided. Never write "X utilizes Y" to reconcile two company names.
- Never claim full compliance when assessment_status is PARTIALLY MET, NOT MET, IN PROGRESS, or PLANNED.
- When <EXISTING_SSP_FACTS> contains real implementation prose, tighten it. Also incorporate evidence artifact titles, mapped policies, and assessment plan steps from <CONTROL_MAPPINGS_AND_ARTIFACTS> into the tightened text.
- Mapped policies and linked team are NOT optional. If <CONTROL_MAPPINGS_AND_ARTIFACTS> lists Mapped policies or Linked team, you MUST name every policy title and every team member in the narrative. Assessment-plan interview names do not replace linked team — include linked team members even when Examine/Interview already names other people.
- Compliance attestations (FIPS certificate numbers, cloud authorization status, DFARS 72-hour reporting) are NOT optional. If present in <CONTROL_MAPPINGS_AND_ARTIFACTS> you MUST echo each value VERBATIM in the narrative. Do not skip, paraphrase, summarize, or treat them as "already covered" by existing prose. The exact values (e.g. "FIPS certificate: Cert. #4287") must appear as written.
- Output only final narrative paragraphs — no XML tags, headings, bullets, or markdown.

Meta-commentary rules:
- Never mention assessment status labels (MET, NOT MET, PARTIALLY MET, etc.).
- Never refer to the control by ID, the assessment process, the assessor, or "provided evidence" as a critique.
- Never write that something "is defined but not documented", "is not documented", or "implementation … is also not documented".
- Never write paragraphs about remediation plans, gap closure, or "ongoing efforts".
- The narrative is implementation prose — write as if you are the system owner describing what is in place.

Structure rules:
- Open with what the organization does (implementation detail), naming the organization exactly once up front.
- Cover 171A objectives in order without labeling them as objectives, using only available facts.
- Weave in mapped policies by title/version, every linked team member by name, evidence artifact titles, and Examine/Interview/Test when present.
- Use precise, auditable facts — no "ensuring", "effectively managed", "reinforcing posture".
- No process verbs or transitional hedging (While / Although / Despite).
- Keep 2–4 short paragraphs. Prefer tightening the existing narrative over rewriting from scratch."""


_BANNED_PATTERNS: list[tuple[str, str]] = [
    (r"\boversees\b", "is responsible for"),
    (r"\boverseeing\b", "responsible for"),
    (r"\bactively working\b", "working"),
    (r"\bin the process of\b", ""),
    (r"\bprogressing toward\b", "addressing"),
    (r"\bprogresses toward\b", "addresses"),
    (r"\bcurrently\b ", ""),
    (r"(?i)^\s*While\s", ""),
    (r"(?i)^\s*Although\s", ""),
    (r"(?i)^\s*Despite\s", ""),
    (r"(?i)ensuring compliance\b", ""),
    (r"(?i)managed effectively\b", "managed"),
    (r"(?i)reinforcing (our |the )?posture", ""),
    (r"(?i)maintaining security\b", ""),
    (r"(?i)enhancing protection\b", ""),
    (r"(?i)safeguarding sensitive information\b", ""),
    (r"(?i)upholding (our |the )?commitment", ""),
    (r"(?i)ensure that all cryptographic measures align with regulatory requirements", ""),
    (r"(?i)to ensure that all.*?align with (relevant |applicable )?(regulatory |security )?(requirements|standards)", ""),
    (r"(?i)is responsible for the implementation of these access controls[^.]*\.", ""),
    (r"(?i)the organization has a remediation plan in place[^.]*\.", ""),
    (r"(?i)with ongoing efforts to ensure[^.]*\.", ""),
    (r"(?i)while the means of limiting[^.]*\.", ""),
    (r"(?i)utilizes\s+Trident\b", ""),
    (r"(?i)\bTest Corp\b", ""),
]

# Drop trailing assessor-gap paragraphs the model often appends.
_ASSESSOR_GAP_PARA = re.compile(
    r"(?is)\n\n+(?:"
    r"[^\n]*(?:not documented(?:\s+in(?:\s+the)?\s+provided\s+evidence)?)"
    r"|[^\n]*means of limiting unsuccessful"
    r"|[^\n]*implementation of the defined means"
    r").*$"
)


def _strip_banned(text: str) -> str:
    text = _ASSESSOR_GAP_PARA.sub("", text)
    for pattern, replacement in _BANNED_PATTERNS:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"\s+\.", ".", text)
    return text.strip()


_FOREIGN_ORG_MARKERS = (
    "test corp",
    "acme corp",
    "example corp",
    "contoso",
    "northwind",
    "fabrikam",
)

# Capitalized multi-word spans that look like people but are products/titles.
_NOT_PERSON_PHRASES = frozenset({
    "microsoft authenticator",
    "microsoft entra",
    "microsoft defender",
    "microsoft sharepoint",
    "conditional access",
    "active directory",
    "system security",
    "security officer",
    "information security",
    "controlled unclassified",
    "unclassified information",
    "authentication policy",
    "access control",
    "compliance report",
    "registration status",
    "privileged accounts",
    "remote access",
    "network access",
    "local access",
    "multi factor",
    "factor authentication",
    "assessment plan",
    "configuration exports",
    "ticket review",
    "log review",
    "the identification",
    "identification and",
    "just in",
    "time access",
})

_PERSON_NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")
_PERSON_NAME_ARTICLES = frozenset({"the", "a", "an"})
_TITLE_WORD_TOKENS = frozenset({
    "policy", "report", "access", "directory", "defender", "authenticator",
    "identification", "authentication", "authorization", "conditional",
    "multifactor", "certificate", "compliance", "registration", "organization",
    "microsoft", "amazon", "google", "azure", "sharepoint", "fortigate",
    "system", "security", "information", "officer", "enclave", "boundary",
})


def _looks_like_person_name(name: str) -> bool:
    """Filter Title Case spans that are policy/product phrasing, not people."""
    key = (name or "").strip().lower()
    if not key or key in _NOT_PERSON_PHRASES:
        return False
    tokens = key.split()
    if not tokens or tokens[0] in _PERSON_NAME_ARTICLES:
        return False
    if any(tok in _TITLE_WORD_TOKENS for tok in tokens):
        return False
    # Real person names are usually 2–3 tokens (First Last[, Suffix]).
    if len(tokens) > 3:
        return False
    return True


def _allowed_person_names(bundle: Dict[str, Any]) -> set[str]:
    """Names the draft may mention (linked team, owner, assessment plan, etc.)."""
    allowed: set[str] = set()
    for name in _team_names(bundle):
        allowed.add(name.lower())
    for key in ("owner", "interview", "examine", "test", "remediation_plan", "assessor_notes"):
        val = str(bundle.get(key) or "")
        for match in _PERSON_NAME_RE.finditer(val):
            phrase = match.group(1)
            if _looks_like_person_name(phrase):
                allowed.add(phrase.lower())
    for sub in bundle.get("linked_subcontractors") or []:
        if isinstance(sub, dict) and sub.get("name"):
            allowed.add(str(sub["name"]).lower())
        elif isinstance(sub, str) and sub.strip():
            allowed.add(sub.strip().lower())
    for finding in (bundle.get("findings") or []) + (bundle.get("collector_findings_only") or []):
        for match in _PERSON_NAME_RE.finditer(str(finding)):
            phrase = match.group(1)
            if _looks_like_person_name(phrase):
                allowed.add(phrase.lower())
    # Org profile often names ISO / system owner.
    for finding in bundle.get("org_profile_findings") or []:
        for match in _PERSON_NAME_RE.finditer(str(finding)):
            phrase = match.group(1)
            if _looks_like_person_name(phrase):
                allowed.add(phrase.lower())
    return allowed


def _reject_invented_people(text: str, bundle: Dict[str, Any]) -> None:
    """Reject drafts that name people not present in control inputs."""
    allowed = _allowed_person_names(bundle)
    # Also allow names that appear in linked policy titles only as non-people;
    # policy titles are handled by _looks_like_person_name filtering.
    invented: List[str] = []
    for match in _PERSON_NAME_RE.finditer(text or ""):
        name = match.group(1)
        if not _looks_like_person_name(name):
            continue
        key = name.lower()
        if key in allowed:
            continue
        tokens = key.split()
        if len(tokens) >= 2 and any(all(tok in a for tok in tokens) for a in allowed):
            continue
        if name not in invented:
            invented.append(name)
    if invented:
        raise RuntimeError(
            f'AI invented person name(s) not in control inputs: {", ".join(invented)}; using template draft'
        )


_PRODUCT_CLUSTERS: tuple[frozenset[str], ...] = (
    frozenset({"amazon web services", "amazon", "aws", "aws iam", "ec2", "s3"}),
    frozenset({"microsoft entra id", "entra id", "entra", "microsoft entra"}),
    frozenset({"azure active directory", "azure ad", "azure", "microsoft azure"}),
    frozenset({"google cloud platform", "google cloud", "gcp"}),
    frozenset({"okta"}),
    frozenset({"ping identity", "ping"}),
    frozenset({"sharepoint", "microsoft sharepoint"}),
    frozenset({"microsoft 365", "office 365", "o365"}),
)


def _policy_titles(bundle: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for p in bundle.get("linked_policies") or []:
        if not isinstance(p, dict):
            continue
        title = str(p.get("title") or "").strip()
        if title:
            out.append(title)
    return out


def _team_names(bundle: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for t in bundle.get("linked_team") or []:
        if isinstance(t, str):
            name = t.strip()
        elif isinstance(t, dict):
            name = str(t.get("name") or "").strip()
        else:
            name = ""
        if name and name not in out:
            out.append(name)
    return out


def _name_in_text(name: str, text_l: str) -> bool:
    """True if full name or a distinctive last token appears in the draft."""
    n = (name or "").strip().lower()
    if not n:
        return True
    if n in text_l:
        return True
    parts = [p for p in re.split(r"\s+", n) if p]
    if len(parts) >= 2 and len(parts[-1]) >= 4 and parts[-1] in text_l:
        return True
    return False


def _ensure_required_mappings(text: str, bundle: Dict[str, Any]) -> str:
    """Append any mapped policy/team names the model omitted so drafts stay complete."""
    text_l = text.lower()
    missing_policies = [t for t in _policy_titles(bundle) if t.lower() not in text_l]
    missing_team = [n for n in _team_names(bundle) if not _name_in_text(n, text_l)]
    if not missing_policies and not missing_team:
        return text
    bits: List[str] = []
    if missing_policies:
        bits.append(
            "Mapped policies governing this control include "
            + ", ".join(missing_policies)
            + "."
        )
    if missing_team:
        bits.append(
            "Linked personnel responsible for this control include "
            + ", ".join(missing_team)
            + "."
        )
    return text.rstrip() + "\n\n" + " ".join(bits)


def _control_linking_text(bundle: Dict[str, Any]) -> str:
    lines: List[str] = []
    policies = bundle.get("linked_policies") or []
    if policies:
        lines.append("Mapped policies (MUST name each title in the narrative):")
        for p in policies:
            title = p.get("title", "Untitled") if isinstance(p, dict) else str(p)
            ver = p.get("version", "") if isinstance(p, dict) else ""
            lines.append(f"  - {title}" + (f" v{ver}" if ver else ""))
    assets = bundle.get("linked_assets") or []
    if assets:
        lines.append("Mapped assets:")
        for a in assets:
            name = a.get("name", "Unknown")
            atype = a.get("type", "")
            cui = a.get("cui", False)
            lines.append(f"  - {name} ({atype})" + (" [CUI]" if cui else ""))
    team = _team_names(bundle)
    if team:
        lines.append("Linked team (MUST name each person in the narrative — do not omit even if Interview lists other names):")
        for name in team[:8]:
            lines.append(f"  - {name}")
    subs = bundle.get("linked_subcontractors") or []
    if subs:
        lines.append("Linked subcontractors: " + ", ".join(s.get("name", "") for s in subs[:3]))
    artifacts = bundle.get("evidence_artifacts") or []
    if artifacts:
        lines.append("Evidence artifacts:")
        for e in artifacts[:25]:
            title = e.get("title") or "Unknown"
            etype = e.get("evidence_type") or ""
            summary = e.get("summary") or ""
            label = f"  - {title}" + (f" ({etype})" if etype else "")
            if summary:
                label += f" — {summary[:180]}"
            lines.append(label)
    elif bundle.get("evidence_files"):
        lines.append("Evidence artifacts:")
        for e in (bundle.get("evidence_files") or [])[:25]:
            title = e.get("display_title") or e.get("filename", "Unknown")
            etype = e.get("evidence_type", "")
            lines.append(f"  - {title}" + (f" ({etype})" if etype else ""))
    examine = str(bundle.get("examine") or "").strip()
    interview = str(bundle.get("interview") or "").strip()
    test = str(bundle.get("test") or "").strip()
    if examine or interview or test:
        lines.append("Assessment plan:")
        if examine:
            lines.append(f"  Examine: {examine[:400]}")
        if interview:
            lines.append(f"  Interview: {interview[:400]}")
        if test:
            lines.append(f"  Test: {test[:400]}")
    fips = str(bundle.get("fips_certificate_number") or "").strip()
    cloud = str(bundle.get("cloud_authorization_status") or "").strip()
    dfars = bundle.get("dfars_72hr_reporting_enabled")
    if fips or cloud or dfars:
        lines.append("Compliance details:")
        if fips:
            lines.append(f"  FIPS certificate: {fips[:200]}")
        if cloud:
            lines.append(f"  Cloud authorization: {cloud[:200]}")
        if dfars:
            lines.append("  DFARS 72-hour reporting: enabled")
    return "\n".join(lines) if lines else "(none)"


def _objectives_text(bundle: Dict[str, Any]) -> str:
    objs = bundle.get("objectives") or []
    if not objs:
        return "(none)"
    lines = []
    for o in objs:
        letter = o.get("letter") or "?"
        status = (o.get("status") or "NOT_STARTED").upper().strip()
        text = (o.get("text") or "").strip()
        lines.append(f"[{letter}] {status} — {text}")
    return "\n".join(lines)


def _existing_facts(bundle: Dict[str, Any]) -> str:
    """Only expose current SSP prose when polish mode packed it into the bundle."""
    if not bundle.get("include_current_narrative"):
        return "(none — draft from verified inputs only; do not reuse any prior narrative text)"
    existing = (bundle.get("existing_narrative_facts") or "").strip()
    if existing:
        return existing
    return "(none — draft from verified inputs only)"


def _build_prompt(bundle: Dict[str, Any], deterministic_draft: str) -> str:
    extra = ssp_extra_instructions()
    extra_block = (
        f"\n\n<ADDITIONAL_ORG_INSTRUCTIONS>\n{extra}\n</ADDITIONAL_ORG_INSTRUCTIONS>"
        if extra
        else ""
    )
    catalog = bundle.get("catalog_description") or "(none)"
    telemetry = verified_telemetry_json(bundle)
    linking = _control_linking_text(bundle)
    objectives = _objectives_text(bundle)
    org_name = bundle.get("org_name", "The organization")
    existing = _existing_facts(bundle)

    return f"""Draft 1–3 short paragraphs of SSP implementation prose for {org_name}.

Organization name (mandatory — use exactly this string as the subject; never invent another; never write "{{other}} utilizes {org_name}"): {org_name}

<REGULATORY_REFERENCE_ONLY_DO_NOT_ASSUME_IMPLEMENTED>
{catalog}
</REGULATORY_REFERENCE_ONLY_DO_NOT_ASSUME_IMPLEMENTED>

<ASSESSMENT_OBJECTIVES_171A>
{objectives}
</ASSESSMENT_OBJECTIVES_171A>

<EXISTING_SSP_FACTS>
{existing}
</EXISTING_SSP_FACTS>

<CONTROL_MAPPINGS_AND_ARTIFACTS>
{linking}
</CONTROL_MAPPINGS_AND_ARTIFACTS>

<VERIFIED_COLLECTOR_TELEMETRY>
{telemetry}
</VERIFIED_COLLECTOR_TELEMETRY>

Execution notes:
- If <EXISTING_SSP_FACTS> has concrete implementation detail, tighten it and keep ticket IDs, SOP names, products, retention, and review dates. Also incorporate any facts from <CONTROL_MAPPINGS_AND_ARTIFACTS> (compliance details, newly mapped evidence, policies, assets, assessment plan) into the output.
- If <EXISTING_SSP_FACTS> is empty / "none", draft from objectives, mappings, evidence artifacts, assessment plan, and collector findings — do not invent a prior narrative. Compliance attestations in <CONTROL_MAPPINGS_AND_ARTIFACTS> MUST still be echoed verbatim even when no existing prose exists.
- MUST name every Mapped policy title and every Linked team member listed in <CONTROL_MAPPINGS_AND_ARTIFACTS>. Interview names from the assessment plan do not replace linked team — include both when both are present.
- Never invent person names. If a name is not in Linked team / owner / Interview / Examine / Test, do not mention them.
- Do NOT introduce Test Corp or any company name other than {org_name}.
- Subject must be {org_name} in the first sentence. Never use "The organization" as the subject if {org_name} is a real organization name.
- Never substitute a different product or vendor name. If <CONTROL_MAPPINGS_AND_ARTIFACTS> lists Microsoft Entra ID, do not write Amazon Web Services.
- Do NOT add "not documented" / gap / remediation paragraphs. If facts are thin, stop after what is known.
- Cover 171A objectives only with available facts — no assessor commentary.
- Do NOT paste the control requirement title verbatim as "implements Limit …".

<STYLE_REFERENCE_ONLY_DO_NOT_ADD_FACTS>
{deterministic_draft}
</STYLE_REFERENCE_ONLY_DO_NOT_ADD_FACTS>{extra_block}
"""


def _reject_foreign_org(text: str, org_name: str) -> None:
    org_l = (org_name or "").strip().lower()
    draft_l = text.lower()
    # Always hard-reject placeholder brands unless they ARE the chosen org name.
    for marker in _FOREIGN_ORG_MARKERS:
        if marker in draft_l and marker != org_l and marker not in org_l:
            raise RuntimeError(
                f'AI invented foreign organization name "{marker}" '
                f'(expected "{org_name}"); using template draft'
            )
    if "utilizes trident" in draft_l or "utilizes  trident" in draft_l:
        raise RuntimeError('AI invented "utilizes Trident" bridging; using template draft')
    if re.search(r"(?i)not documented(?:\s+in(?:\s+the)?\s+provided\s+evidence)?", text):
        raise RuntimeError("AI returned assessor gap language; using template draft")
    if org_l and org_l != "the organization" and org_l not in draft_l:
        first = org_l.split()[0]
        if len(first) >= 4 and first not in draft_l:
            raise RuntimeError(
                f'AI omitted organization name "{org_name}"; using template draft'
            )


def _reject_unmapped_products(text: str, bundle: Dict[str, Any]) -> None:
    """Reject if draft mentions a product/vendor not present in any control input.

    Works in product clusters: if the draft mentions any name from a cluster
    (e.g. \"microsoft entra id\"), at least one name from that same cluster
    must appear in the bundle's evidence, assets, policies, or collector findings.
    """
    text_l = text.lower()

    bundle_parts: List[str] = []
    for artifact in bundle.get("evidence_artifacts") or []:
        for key in ("title", "summary", "provenance"):
            val = artifact.get(key)
            if val:
                bundle_parts.append(str(val).lower())
    for asset in bundle.get("linked_assets") or []:
        for key in ("name", "type"):
            val = asset.get(key)
            if val:
                bundle_parts.append(str(val).lower())
    for policy in bundle.get("linked_policies") or []:
        title = policy.get("title") if isinstance(policy, dict) else None
        if title:
            bundle_parts.append(str(title).lower())
    for name in _team_names(bundle):
        bundle_parts.append(name.lower())
    for finding in bundle.get("collector_findings") or []:
        bundle_parts.append(str(finding).lower())
    for source in bundle.get("sources") or []:
        bundle_parts.append(str(source).lower())
    for key in ("examine", "interview", "test"):
        val = bundle.get(key)
        if val:
            bundle_parts.append(str(val).lower())
    for finding in bundle.get("findings") or []:
        bundle_parts.append(str(finding).lower())
    for key in ("catalog_description", "org_name", "profile_org_name"):
        val = bundle.get(key)
        if val:
            bundle_parts.append(str(val).lower())
    bundle_text = " ".join(bundle_parts)

    for cluster in _PRODUCT_CLUSTERS:
        draft_matches = {kw for kw in cluster if kw in text_l}
        if not draft_matches:
            continue
        bundle_matches = {kw for kw in cluster if kw in bundle_text}
        if not bundle_matches:
            example = next(iter(draft_matches))
            raise RuntimeError(
                f'AI invented unmapped product/vendor "{example}" not found in any control input; using template draft'
            )


def polish_ssp_narrative_with_ai(bundle: Dict[str, Any], deterministic_draft: str) -> str:
    key = api_key()
    if not key:
        raise RuntimeError("AI API key not configured")

    body = {
        "model": model(),
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_prompt(bundle, deterministic_draft)},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"AI request failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"AI request failed: {exc.reason}") from exc

    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("AI returned no choices")
    text = (choices[0].get("message") or {}).get("content") or ""
    text = text.strip()
    if not text:
        raise RuntimeError("AI returned empty narrative")
    text = _strip_banned(text)
    if not text:
        raise RuntimeError("AI returned empty narrative after post-processing")
    _reject_foreign_org(text, str(bundle.get("org_name") or ""))
    _reject_unmapped_products(text, bundle)
    _reject_invented_people(text, bundle)
    text = _ensure_required_mappings(text, bundle)
    return text
