"""Assessment helpers: POA&M, permissions, filtering, snapshots."""

import hashlib
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from app_config import CONTROL_DEPENDENCIES, ROLE_PERMISSIONS, VALIDATION_RULES
from controls import CMMC_FRAMEWORK
from sprs_engine import calculate_detailed_sprs

def hash_file(file) -> str:
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    file.seek(0)
    return sha256_hash.hexdigest()

def calculate_readiness_percentage(answers: Dict[str, Any], scoped_controls: List[str]) -> float:
    if not scoped_controls: return 0.0
    status_weights = {"MET": 1.0, "PARTIALLY MET": 0.5, "IN PROGRESS": 0.25, "PLANNED": 0.1}
    total = sum(status_weights.get(answers[cid]["status"], 0) for cid in scoped_controls)
    return round((total / len(scoped_controls)) * 100, 1)

def generate_poam_entries(answers: Dict[str, Any], scoped_controls: List[str]) -> pd.DataFrame:
    poam_rows = []
    gap_controls = [
        cid for cid in scoped_controls
        if cid in answers and answers[cid]["status"] not in ["MET", "NOT APPLICABLE", "INHERITED"]
    ]
    gap_controls.sort(key=lambda c: (-CMMC_FRAMEWORK[c]["weight"], c))

    for cid in gap_controls:
        ans = answers[cid]
        weight = CMMC_FRAMEWORK[cid]["weight"]
        family = CMMC_FRAMEWORK[cid]["family"]
        if weight >= 5 or family in ["Incident Response", "System and Information Integrity"]:
            severity = "Critical" if weight == 5 else "High"
        elif weight == 3:
            severity = "Moderate"
        else:
            severity = "Low"

        poam_rows.append({
            "Control ID": cid,
            "SPRS Weight": weight,
            "Requirement": CMMC_FRAMEWORK[cid]["name"],
            "Current Status": ans["status"],
            "Deficiency": f"Control not fully implemented: {ans.get('assessor_notes', 'No notes provided')}",
            "Risk Severity": severity,
            "Remediation Steps": ans.get("remediation_plan", "Define implementation roadmap"),
            "Owner": ans.get("owner", "TBD"),
            "Target Date": ans.get("target_date", ""),
            "Estimated Cost": ans.get("estimated_cost", ""),
            "Dependencies": ", ".join(CONTROL_DEPENDENCIES.get(cid, [])),
            "POA&M Status": "Open",
            "Likelihood": ans.get("likelihood", "Medium"),
            "Impact": ans.get("impact", "Medium"),
        })
    return pd.DataFrame(poam_rows)

def log_audit_event(audit_log: List[Dict], control_id: str, field: str, old_val: Any, new_val: Any, role: str):
    entry = {
         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "control_id": control_id,
        "field": field, "old_value": str(old_val), "new_value": str(new_val), "user_role": role
    }
    entry["integrity_hash"] = hashlib.sha256(
        f"{entry['timestamp']}{entry['control_id']}{entry['field']}{entry['old_value']}{entry['new_value']}".encode()
    ).hexdigest()
    audit_log.append(entry)

def validate_evidence_against_rules(content: str, control_id: str) -> Dict[str, Any]:
    if control_id not in VALIDATION_RULES: return {"passed": True, "details": []}
    rules = VALIDATION_RULES[control_id]
    results = [{"rule": r["description"], "passed": bool(re.search(r["pattern"], content, re.IGNORECASE | re.MULTILINE))} for r in rules.get("rules", [])]
    return {"passed": all(r["passed"] for r in results), "details": results}

def resolve_control_dependencies(cid: str, visited: set = None) -> List[str]:
    if visited is None: visited = set()
    if cid in visited: return []
    visited.add(cid)
    deps = list(CONTROL_DEPENDENCIES.get(cid, []))
    for dep in deps: deps.extend(resolve_control_dependencies(dep, visited.copy()))
    return list(set(deps))

def check_permission(permission: str) -> bool:
    import streamlit as st

    return ROLE_PERMISSIONS.get(st.session_state.current_role, {}).get(permission, False)


def save_sprs_snapshot(silent: bool = False):
    """Save current SPRS score for trend analysis automatically"""
    import streamlit as st

    detailed_sprs = calculate_detailed_sprs(st.session_state.answers, st.session_state.scoped_controls)
    
    # Avoid duplicate snapshots with the exact same score/readiness on the same day
    today_str = datetime.now().strftime("%Y-%m-%d")
    if "sprs_history" in st.session_state and st.session_state.sprs_history:
        last_snapshot = st.session_state.sprs_history[-1]
        last_date = last_snapshot["timestamp"][:10]
        if last_date == today_str and last_snapshot["score"] == detailed_sprs["final_score"]:
            return  # Skip redundant snapshotting
            
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "score": detailed_sprs["final_score"],
        "readiness": calculate_readiness_percentage(st.session_state.answers, st.session_state.scoped_controls),
        "critical_gaps": len(detailed_sprs["critical_gaps"]),
        "total_gaps": detailed_sprs["breakdown"]["total_gaps_count"]
    }
    if "sprs_history" not in st.session_state:
        st.session_state.sprs_history = []
    st.session_state.sprs_history.append(snapshot)
    from session_persistence import save_state_to_disk

    save_state_to_disk()
    if not silent:
        st.toast("📸 Compliance snapshot captured automatically!")


def render_assessment_alerts(answers: Dict[str, Any], scoped_controls: List[str]) -> None:
    """POA&M overdue only — gap priorities live in Suggested controls below."""
    import streamlit as st

    poam_df = generate_poam_entries(answers, scoped_controls)
    if poam_df.empty:
        return
    overdue = poam_df[pd.to_datetime(poam_df["Target Date"], errors="coerce") < pd.Timestamp.now()]
    if overdue.empty:
        return
    st.markdown(
        f'<div class="readiness-callout readiness-callout-pending">'
        f"<strong>POA&amp;M:</strong> {len(overdue)} item(s) past target date — "
        f"update dates or status in the controls below."
        f"</div>",
        unsafe_allow_html=True,
    )


def filter_scoped_controls(
    scoped_controls: List[str],
    answers: Dict[str, Any],
    selected_domain: str,
    search_query: str,
    family_mapping: Dict[str, str],
) -> List[str]:
    filtered = list(scoped_controls)
    if selected_domain != "All Controls":
        family_label = selected_domain.split(" (")[0]
        family_name = family_mapping[family_label]
        filtered = [cid for cid in filtered if CMMC_FRAMEWORK[cid]["family"] == family_name]
    q = (search_query or "").strip().lower()
    if not q:
        return filtered
    out = []
    for cid in filtered:
        info = CMMC_FRAMEWORK[cid]
        ans = answers.get(cid, {})
        haystack = f"{cid} {info['family']} {info['name']} {ans.get('assessor_notes', '')}".lower()
        if q in haystack:
            out.append(cid)
    return out
