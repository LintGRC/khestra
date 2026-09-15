"""Environment scoping flags — inform N/A suggestions and contradiction checks (no auto-scoring)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from controls import CMMC_FRAMEWORK

WIRELESS_CONTROLS = ("AC.L2-3.1.16", "AC.L2-3.1.17", "AC.L2-3.1.18")
REMOTE_CONTROLS = ("AC.L2-3.1.12", "AC.L2-3.1.13", "AC.L2-3.1.14")
MOBILE_CONTROLS = ("AC.L2-3.1.18", "AC.L2-3.1.19")

YES_NO_LABELS = {
    "": "Not answered",
    "yes": "Yes",
    "no": "No",
}

CLOUD_LABELS = {
    "": "Not answered",
    "on_prem_only": "On-premises only (no IaaS/PaaS for CUI)",
    "azure": "Microsoft Azure",
    "aws": "Amazon Web Services",
    "both": "Azure and AWS",
    "other": "Other cloud provider",
}

# Lightweight inheritance hints — review prompts, not auto-INHERITED.
M365_INHERITANCE_HINTS = [
    ("IA.L2-3.5.3", "Microsoft Entra ID", "MFA may be partially inherited — document org Conditional Access and gaps."),
    ("IA.L2-3.5.7", "Microsoft Entra ID", "Password complexity may be enforced via Entra — verify policy matches requirement."),
    ("SC.L2-3.13.8", "Microsoft 365", "Transmission protection for M365 — cite Microsoft compliance artifacts if claiming inheritance."),
    ("SC.L2-3.13.11", "Microsoft 365 / Azure", "FIPS validation — collect Microsoft compliance exports; org still responsible for configuration."),
    ("AU.L2-3.3.1", "Microsoft 365", "Unified audit log / Entra sign-in logs — partial provider responsibility."),
]

AZURE_INHERITANCE_HINTS = [
    ("SC.L2-3.13.8", "Azure", "TLS for Azure PaaS — document shared responsibility and org configuration."),
    ("SC.L2-3.13.16", "Azure", "Data at rest — verify customer-managed keys vs platform defaults."),
    ("CM.L2-3.4.1", "Azure", "Baseline configs for VMs/App Service — org owns guest OS and app settings."),
]

AWS_INHERITANCE_HINTS = [
    ("SC.L2-3.13.8", "AWS", "TLS in transit for AWS services — cite shared responsibility model."),
    ("SC.L2-3.13.16", "AWS", "Encryption at rest — verify KMS usage and key ownership."),
    ("CM.L2-3.4.1", "AWS", "EC2/ECS baselines — org owns AMIs and patch cadence."),
]


def default_env_scope() -> Dict[str, str]:
    return {
        "processes_cui": "",
        "uses_wireless": "",
        "remote_workforce": "",
        "uses_m365": "",
        "uses_google": "",
        "cloud_hosting": "",
    }


def merge_env_scope(stored: Optional[Dict[str, Any]]) -> Dict[str, str]:
    scope = default_env_scope()
    if stored:
        for key in scope:
            val = stored.get(key)
            if val is not None:
                scope[key] = str(val).strip().lower() if key != "cloud_hosting" else str(val).strip().lower()
    return scope


def env_scope_complete(env_scope: Dict[str, str]) -> bool:
    required = ("processes_cui", "uses_wireless", "remote_workforce", "uses_m365", "cloud_hosting")
    return all((env_scope.get(k) or "").strip() for k in required)


def _controls_in_scope(control_ids: tuple[str, ...], scoped_controls: List[str]) -> List[str]:
    scoped = set(scoped_controls)
    return [c for c in control_ids if c in scoped]


def _status_label(status: str) -> str:
    return status or "NOT STARTED"


def scoping_suggestions(
    env_scope: Dict[str, str],
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> List[Dict[str, str]]:
    """Suggest N/A review for controls that may not apply — user must confirm."""
    out: List[Dict[str, str]] = []

    def maybe_na(control_ids: tuple[str, ...], reason: str) -> None:
        for cid in _controls_in_scope(control_ids, scoped_controls):
            status = answers.get(cid, {}).get("status", "NOT STARTED")
            if status in ("NOT STARTED", "PLANNED"):
                out.append(
                    {
                        "control_id": cid,
                        "suggestion": "Review for Not Applicable",
                        "reason": reason,
                    }
                )

    if env_scope.get("uses_wireless") == "no":
        maybe_na(WIRELESS_CONTROLS, "You indicated no corporate Wi-Fi / wireless access to CUI systems.")

    if env_scope.get("remote_workforce") == "no":
        maybe_na(REMOTE_CONTROLS, "You indicated no remote access to CUI — VPN/RDP controls may be N/A.")

    if env_scope.get("uses_m365") == "no" and env_scope.get("cloud_hosting") in ("on_prem_only", "none", ""):
        pass  # no cloud hints

    return out[:12]


def inheritance_hints(
    env_scope: Dict[str, str],
    scoped_controls: List[str],
) -> List[Dict[str, str]]:
    hints: List[Dict[str, str]] = []
    scoped = set(scoped_controls)
    seen: set[str] = set()

    def add_rows(rows: List[tuple[str, str, str]]) -> None:
        for cid, provider, note in rows:
            if cid not in scoped or cid in seen:
                continue
            seen.add(cid)
            hints.append(
                {
                    "control_id": cid,
                    "provider": provider,
                    "note": note,
                    "control_name": CMMC_FRAMEWORK[cid]["name"][:70],
                }
            )

    if env_scope.get("uses_m365") == "yes":
        add_rows(M365_INHERITANCE_HINTS)

    cloud = env_scope.get("cloud_hosting", "")
    if cloud in ("azure", "both"):
        add_rows(AZURE_INHERITANCE_HINTS)
    if cloud in ("aws", "both"):
        add_rows(AWS_INHERITANCE_HINTS)

    return hints[:15]


def control_scope_context(
    control_id: str,
    env_scope: Dict[str, str],
    answers: Dict[str, Any],
    scoped_controls: List[str],
) -> Optional[Dict[str, str]]:
    """Per-control scoping or inheritance note for the assessment editor."""
    if control_id not in scoped_controls:
        return None

    from inheritance_map import inheritance_detail_for_control

    detail = inheritance_detail_for_control(control_id, env_scope, scoped_controls)
    if detail:
        return {
            "kind": "inheritance",
            "title": f"Shared responsibility — {detail['provider']} ({detail['inheritance_level']})",
            "detail": detail["org_responsibility"],
            "org_responsibility": detail["org_responsibility"],
            "provider_responsibility": detail["provider_responsibility"],
            "citation": detail["citation"],
            "inheritance_level": detail["inheritance_level"],
            "provider": detail["provider"],
        }

    for item in inheritance_hints(env_scope, scoped_controls):
        if item["control_id"] == control_id:
            return {
                "kind": "inheritance",
                "title": f"Possible inheritance — {item['provider']}",
                "detail": item["note"],
            }

    for item in scoping_suggestions(env_scope, answers, scoped_controls):
        if item["control_id"] == control_id:
            return {
                "kind": "scoping",
                "title": item["suggestion"],
                "detail": item["reason"],
            }

    return None


def _profile_text_blob(org_profile: Optional[Dict[str, str]]) -> str:
    if not org_profile:
        return ""
    return " ".join(
        (org_profile.get(k) or "").lower()
        for k in ("system_description", "architecture_summary", "boundary_description")
    )


def env_scope_contradictions(
    env_scope: Dict[str, str],
    answers: Dict[str, Any],
    scoped_controls: List[str],
    asset_scope: Optional[Dict[str, Any]] = None,
    org_profile: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Flag mismatches between environment flags and control statuses."""
    findings: List[Dict[str, str]] = []
    closed = frozenset({"MET", "NOT APPLICABLE", "INHERITED"})

    def wireless_statuses() -> List[str]:
        return [
            answers.get(c, {}).get("status", "NOT STARTED")
            for c in _controls_in_scope(WIRELESS_CONTROLS, scoped_controls)
        ]

    def remote_statuses() -> List[str]:
        return [
            answers.get(c, {}).get("status", "NOT STARTED")
            for c in _controls_in_scope(REMOTE_CONTROLS, scoped_controls)
        ]

    w_stats = wireless_statuses()
    if env_scope.get("uses_wireless") == "yes" and w_stats and all(s in ("NOT APPLICABLE", "INHERITED") for s in w_stats):
        findings.append(
            {
                "severity": "high",
                "title": "Wireless in use but 3.1.16–3.1.18 marked N/A",
                "detail": "Environment flags say Wi-Fi is used, but wireless controls are Not Applicable/Inherited.",
            }
        )

    if env_scope.get("uses_wireless") == "no" and any(
        answers.get(c, {}).get("status") in ("MET", "NOT MET", "PARTIALLY MET", "IN PROGRESS")
        for c in _controls_in_scope(WIRELESS_CONTROLS, scoped_controls)
    ):
        findings.append(
            {
                "severity": "medium",
                "title": "No wireless in scope but wireless controls are assessed",
                "detail": "You indicated no wireless — consider Not Applicable for 3.1.16–3.1.18 if accurate.",
            }
        )

    r_stats = remote_statuses()
    if env_scope.get("remote_workforce") == "yes" and r_stats and all(s in ("NOT APPLICABLE", "INHERITED") for s in r_stats):
        findings.append(
            {
                "severity": "high",
                "title": "Remote workforce but remote-access controls marked N/A",
                "detail": "You indicated remote CUI access — review 3.1.12–3.1.14 status and narratives.",
            }
        )

    if env_scope.get("remote_workforce") == "no" and any(
        answers.get(c, {}).get("status") not in closed
        for c in _controls_in_scope(REMOTE_CONTROLS, scoped_controls)
    ):
        findings.append(
            {
                "severity": "medium",
                "title": "No remote access but remote controls show gaps",
                "detail": "Remote workforce = No — VPN/remote session controls may be Not Applicable.",
            }
        )

    if env_scope.get("processes_cui") == "no" and asset_scope:
        cui_pct = asset_scope.get("CUI Assets", 0)
        if cui_pct and int(cui_pct) > 0:
            findings.append(
                {
                    "severity": "medium",
                    "title": "CUI scope mismatch",
                    "detail": "Environment says no CUI processing, but Assessment scope has CUI Assets > 0%.",
                }
            )

    if env_scope.get("processes_cui") == "yes" and asset_scope:
        cui_pct = asset_scope.get("CUI Assets", 0)
        if cui_pct == 0:
            findings.append(
                {
                    "severity": "medium",
                    "title": "CUI scope mismatch",
                    "detail": "You indicated CUI is processed — set CUI Assets % under Assessment scope.",
                }
            )

    if env_scope.get("uses_m365") == "yes":
        mfa = answers.get("IA.L2-3.5.3", {}).get("status", "NOT STARTED")
        if mfa == "INHERITED":
            findings.append(
                {
                    "severity": "medium",
                    "title": "3.5.3 marked Inherited — verify org MFA config",
                    "detail": "M365 does not fully inherit MFA — document Conditional Access and any gaps.",
                }
            )
        elif mfa == "MET" and "IA.L2-3.5.3" in scoped_controls:
            narrative = (
                answers.get("IA.L2-3.5.3", {}).get("implementation_narrative", "")
                or answers.get("IA.L2-3.5.3", {}).get("assessor_notes", "")
            ).lower()
            if narrative and not re.search(r"\b(mfa|multifactor|multi-factor|conditional access)\b", narrative):
                findings.append(
                    {
                        "severity": "medium",
                        "title": "M365 in scope but 3.5.3 narrative omits MFA",
                        "detail": "Environment uses M365 — MFA narrative should reference Entra / Conditional Access.",
                    }
                )

    arch = _profile_text_blob(org_profile)
    if env_scope.get("uses_m365") == "no" and re.search(
        r"\b(m365|microsoft 365|office 365|entra|azure ad)\b", arch
    ):
        findings.append(
            {
                "severity": "medium",
                "title": "Profile mentions M365 but environment flag is No",
                "detail": "Align Organization → Environment scope with architecture text.",
            }
        )

    if env_scope.get("uses_m365") == "yes" and env_scope.get("cloud_hosting") in ("", "on_prem_only"):
        if re.search(r"\b(aws|amazon web services|azure)\b", arch):
            findings.append(
                {
                    "severity": "medium",
                    "title": "Cloud mentioned in profile but hosting flag not set",
                    "detail": "Update cloud hosting under Environment scope to match architecture.",
                }
            )

    if env_scope.get("cloud_hosting") == "on_prem_only" and re.search(
        r"\b(aws|azure|amazon web services)\b", arch
    ):
        findings.append(
            {
                "severity": "medium",
                "title": "On-prem only but profile mentions cloud",
                "detail": "Architecture references cloud services — confirm shared responsibility scope.",
            }
        )

    if env_scope.get("remote_workforce") == "yes":
        mobile_open = [
            c
            for c in _controls_in_scope(MOBILE_CONTROLS, scoped_controls)
            if answers.get(c, {}).get("status") in ("NOT APPLICABLE", "INHERITED")
        ]
        if len(mobile_open) == len(_controls_in_scope(MOBILE_CONTROLS, scoped_controls)) and mobile_open:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Remote workforce but mobile controls all N/A",
                    "detail": "Remote access often involves laptops or mobile devices — review 3.1.18–3.1.19.",
                }
            )

    return findings


def format_env_scope_summary(env_scope: Dict[str, str]) -> str:
    lines = ["Environment scope"]
    for key, label in (
        ("processes_cui", "Processes CUI"),
        ("uses_wireless", "Wireless access"),
        ("remote_workforce", "Remote workforce"),
        ("uses_m365", "Microsoft 365 / Entra"),
        ("uses_google", "Google Workspace"),
        ("cloud_hosting", "Cloud hosting"),
    ):
        val = env_scope.get(key, "")
        if key == "cloud_hosting":
            display = CLOUD_LABELS.get(val, val or "Not answered")
        elif key == "uses_google":
            display = YES_NO_LABELS.get(val, val or "Not answered") if val else "Not answered"
        else:
            display = YES_NO_LABELS.get(val, val or "Not answered")
        lines.append(f"  {label}: {display}")
    return "\n".join(lines)
