"""ISO 27001 demo seed — realistic SoA statuses + ISO risks for evaluation.

Deterministic: the same seed always produces the same distribution so demo
and CI behavior is stable.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Foundational controls a typical SaaS ISMS has implemented (2022 edition ids).
_IMPLEMENTED = [
    "A.5.1", "A.5.2", "A.5.3", "A.5.4", "A.5.8", "A.5.9", "A.5.10", "A.5.11",
    "A.5.12", "A.5.13", "A.5.14", "A.5.15", "A.5.16", "A.5.17", "A.5.18",
    "A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23", "A.5.24", "A.5.25",
    "A.5.26", "A.5.27", "A.5.28", "A.5.29", "A.5.30", "A.5.31", "A.5.32",
    "A.5.33", "A.5.34", "A.5.35", "A.5.36", "A.5.37",
    "A.6.1", "A.6.2", "A.6.3", "A.6.4", "A.6.5", "A.6.6", "A.6.7", "A.6.8",
    "A.8.1", "A.8.2", "A.8.3", "A.8.4", "A.8.5", "A.8.6", "A.8.7", "A.8.8",
    "A.8.9", "A.8.10", "A.8.11", "A.8.12", "A.8.13", "A.8.14", "A.8.15",
    "A.8.16", "A.8.17", "A.8.18", "A.8.19", "A.8.20", "A.8.21", "A.8.22",
    "A.8.23", "A.8.24", "A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29",
    "A.8.30", "A.8.31", "A.8.32", "A.8.33", "A.8.34",
    "A.7.1", "A.7.2", "A.7.4", "A.7.7", "A.7.9", "A.7.11", "A.7.13",
]

# Controls with a documented partial implementation.
_PARTIAL = [
    "A.5.5", "A.5.6", "A.5.7", "A.8.20", "A.8.25",
]

# Physically N/A for a cloud-only SaaS organization (no on-premises assets).
_EXCLUDED = [
    "A.7.3", "A.7.5", "A.7.6", "A.7.8", "A.7.10", "A.7.12", "A.7.14",
]

_JUSTIFICATION_EXCLUDED = (
    "Not applicable — the organization operates cloud-hosted services with no "
    "on-premises physical infrastructure to which this control applies."
)

_SEED_RISKS: List[Dict[str, Any]] = [
    {
        "title": "Credential stuffing against admin console",
        "description": "Brute-force and credential-stuffing attempts against the management console could "
                       "lead to unauthorized access to customer data.",
        "category": "Security",
        "framework": "ISO 27001",
        "control_ids": ["A.5.15", "A.8.5", "A.8.11", "A.8.12"],
        "owner": "IT Operations",
        "likelihood": 3,
        "impact": 4,
        "treatment": "mitigate",
        "treatment_plan": "Enforce MFA for all console access (A.8.5), rate-limit login endpoints, "
                          "and require conditional access policies (A.8.11/A.8.12).",
        "status": "open",
        "review_date": "2026-12-01",
    },
    {
        "title": "Third-party vendor supply chain compromise",
        "description": "A compromise of a key SaaS vendor (identity provider or cloud provider) could "
                       "expose ISMS data; monitoring of vendor security posture is manual today.",
        "category": "Supply chain",
        "framework": "ISO 27001",
        "control_ids": ["A.5.19", "A.5.20", "A.5.21", "A.5.22"],
        "owner": "Procurement",
        "likelihood": 2,
        "impact": 4,
        "treatment": "mitigate",
        "treatment_plan": "Complete vendor risk assessments for all Tier 1 suppliers (A.5.21) and "
                          "add contractual security requirements (A.5.19/A.5.20).",
        "status": "open",
        "review_date": "2026-11-15",
    },
    {
        "title": "Unpatched critical vulnerabilities in production services",
        "description": "Patch management relies on scheduled maintenance windows; zero-day exploitation "
                       "could impact confidentiality, integrity, and availability.",
        "category": "Security",
        "framework": "ISO 27001",
        "control_ids": ["A.8.8", "A.8.9", "A.8.10", "A.8.22"],
        "owner": "Platform Engineering",
        "likelihood": 3,
        "impact": 3,
        "treatment": "mitigate",
        "treatment_plan": "Automate vulnerability scanning (A.8.8) with a 72-hour SLA for critical "
                          "findings and weekly patching windows (A.8.9).",
        "status": "open",
        "review_date": "2026-12-15",
    },
]


def seed_demo_soa() -> Dict[str, Any]:
    """Apply the deterministic SoA status distribution; returns the rollup."""
    from soa import list_soa, rollup, update_control

    for ctrl in list_soa():
        cid = ctrl["control_id"]
        if cid in _EXCLUDED:
            fields = {
                "status": "excluded",
                "applicable": False,
                "justification": _JUSTIFICATION_EXCLUDED,
            }
        elif cid in _IMPLEMENTED:
            fields = {"status": "implemented"}
        elif cid in _PARTIAL:
            fields = {"status": "partially implemented"}
        else:
            fields = {"status": "not implemented"}
        try:
            update_control(cid, fields)
        except ValueError:
            pass
    return rollup()


def seed_demo_risks() -> List[str]:
    """Create the ISO risk set (idempotent by title)."""
    try:
        from risks.store import create_risk, list_risks

        existing = {r.get("title") for r in list_risks(framework="ISO 27001") or []}
        created = []
        for spec in _SEED_RISKS:
            if spec["title"] in existing:
                continue
            create_risk(**spec)
            created.append(spec["title"])
        return created
    except Exception:
        return []


def seed_demo_audit_loop() -> Dict[str, Any]:
    """One internal audit + NC/CAPA + management review (idempotent by title)."""
    created: Dict[str, Any] = {"audit": False, "finding": False, "review": False}
    try:
        from audit_center.store import create_audit, list_audits, update_audit

        existing = {a.get("title") for a in list_audits(framework="ISO 27001") or []}
        if "ISMS internal audit 2026-H1" not in existing:
            audit = create_audit(
                title="ISMS internal audit 2026-H1",
                framework="ISO 27001",
                audit_type="internal",
                start_date="2026-03-01",
                end_date="2026-03-15",
                auditor_name="Internal Audit",
                scope_notes="Annex A technical controls and clauses 9.2 / 9.3.",
                preparation_notes="Sampled A.8.8 vulnerability management and A.5.15 access control.",
            )
            update_audit(audit["id"], status="completed")
            created["audit"] = True
    except Exception:
        pass
    try:
        from findings.store import create_action, create_finding, list_findings

        titles = {f.get("title") for f in list_findings(framework="ISO 27001") or []}
        if "Unpatched production image (A.8.8)" not in titles:
            finding = create_finding(
                title="Unpatched production image (A.8.8)",
                description="Quarterly vulnerability scan left a production AMI 32 days past SLA.",
                source="audit",
                severity="medium",
                status="in_remediation",
                owner="IT Operations",
                framework="ISO 27001",
                control_ids=["A.8.8"],
            )
            create_action(
                finding["id"],
                title="Rebuild AMI and verify scanner SLA",
                owner="IT Operations",
                target_date="2026-04-15",
                status="in_progress",
            )
            created["finding"] = True
    except Exception:
        pass
    try:
        from management_review.store import create_review, list_reviews

        titles = {r.get("title") for r in list_reviews() or []}
        if "Q1 2026 ISMS management review" not in titles:
            create_review(
                title="Q1 2026 ISMS management review",
                date="2026-03-28",
                status="completed",
                attendees=[{"name": "CEO"}, {"name": "CISO"}, {"name": "IT Operations"}],
                inputs=[
                    {"key": "audit_results", "label": "Results of internal audits",
                     "notes": "H1 internal audit completed; one medium NC on A.8.8."},
                    {"key": "risk_status", "label": "Risk assessment and treatment",
                     "notes": "Three ISO risks remain in treatment; SoA updated from 6.1.3."},
                ],
                outputs=[
                    {"category": "improvement", "title": "Close A.8.8 NC before surveillance",
                     "notes": "CAPA owner IT Operations, due 2026-04-15."},
                ],
                action_items=[
                    {"title": "Verify AMI rebuild evidence", "owner": "CISO", "due_date": "2026-04-20"},
                ],
                minutes=(
                    "Top management reviewed ISMS performance, the H1 internal audit, "
                    "and residual risk. Resources for vulnerability management were confirmed adequate. "
                    "The A.8.8 nonconformity is accepted as open with a dated CAPA."
                ),
            )
            created["review"] = True
    except Exception:
        pass
    return created


def load_demo() -> Dict[str, Any]:
    """Idempotent demo seed: SoA + risks + 6.1.3 write-back + 9.2/9.3 records."""
    soa = seed_demo_soa()
    risks = seed_demo_risks()
    from soa import sync_soa_from_risks

    linked = sync_soa_from_risks()
    audit_loop = seed_demo_audit_loop()
    return {
        "status": "ok",
        "is_demo": True,
        "soa_rollup": soa,
        "risks_created": risks,
        "soa_from_risks": linked,
        "audit_loop": audit_loop,
    }
