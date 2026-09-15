"""Environment scoping flags for SOC 2 — inform N/A suggestions and contradiction checks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from soc2_catalog import SOC2_CONTROLS


YES_NO_LABELS = {
    "": "Not answered",
    "yes": "Yes",
    "no": "No",
}

CLOUD_LABELS = {
    "": "Not answered",
    "on_prem_only": "On-premises only",
    "aws": "Amazon Web Services",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "both": "AWS and Azure",
    "other": "Other cloud provider",
}


def default_env_scope() -> Dict[str, str]:
    return {
        "uses_cloud": "",
        "cloud_provider": "",
        "uses_saas": "",
        "remote_workforce": "",
        "uses_wireless": "",
        "processes_pii": "",
    }


def merge_env_scope(stored: Optional[Dict[str, Any]]) -> Dict[str, str]:
    scope = default_env_scope()
    if stored:
        for key in scope:
            val = stored.get(key)
            if val is not None:
                scope[key] = str(val).strip().lower()
    return scope


def env_scope_complete(env_scope: Dict[str, str]) -> bool:
    required = ("uses_cloud", "cloud_provider", "uses_saas", "remote_workforce", "processes_pii")
    return all((env_scope.get(k) or "").strip() for k in required)


def format_env_scope_summary(env_scope: Dict[str, str]) -> str:
    lines = ["Environment scope"]
    for key, label in (
        ("uses_cloud", "Cloud services"),
        ("cloud_provider", "Cloud provider"),
        ("uses_saas", "Third-party SaaS"),
        ("remote_workforce", "Remote workforce"),
        ("uses_wireless", "Wireless access"),
        ("processes_pii", "Processes PII"),
    ):
        val = env_scope.get(key, "")
        if key == "cloud_provider":
            display = CLOUD_LABELS.get(val, val or "Not answered")
        else:
            display = YES_NO_LABELS.get(val, val or "Not answered")
        lines.append(f"  {label}: {display}")
    return "\n".join(lines)


def scoping_suggestions(
    env_scope: Dict[str, str],
    answers: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Suggest N/A review for controls that may not apply based on environment."""
    out: List[Dict[str, str]] = []
    closed = {"MET", "NOT APPLICABLE", "INHERITED"}

    if env_scope.get("uses_wireless") == "no":
        for cid in ("CC6.1", "CC6.6"):
            status = answers.get(cid, {}).get("status", "NOT STARTED")
            if status not in closed:
                out.append({
                    "control_id": cid,
                    "suggestion": "Review for Not Applicable",
                    "reason": "No wireless access — physical access controls may not apply.",
                })

    if env_scope.get("remote_workforce") == "no":
        for cid in ("CC6.1",):
            status = answers.get(cid, {}).get("status", "NOT STARTED")
            if status not in closed:
                out.append({
                    "control_id": cid,
                    "suggestion": "Review for Not Applicable",
                    "reason": "No remote workforce — remote access controls may not apply.",
                })

    if env_scope.get("processes_pii") == "no":
        for cid in ("P1.1", "P2.1", "P3.1"):
            if cid in SOC2_CONTROLS:
                status = answers.get(cid, {}).get("status", "NOT STARTED")
                if status not in closed:
                    out.append({
                        "control_id": cid,
                        "suggestion": "Review for Not Applicable",
                        "reason": "No PII processing — privacy controls may not apply.",
                    })

    return out[:12]
