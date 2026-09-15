"""Generates per-PoF evidence collection hints based on PoF text and theme analysis."""

import re
from typing import Any, Dict, List

_WORD = re.compile(r"\b\w+\b")

_RULES: List[tuple[List[str], List[str]]] = [
    (["policy", "policies", "procedure", "procedures", "standard", "standards", "guideline", "guidelines"], [
        "Relevant policy or procedure document",
        "Evidence of policy dissemination and acknowledgment",
    ]),
    (["access", "login", "logins", "mfa", "password", "passwords", "credential", "credentials", "authentication", "authenticate", "authenticates", "identity", "identities", "authorization", "authorize", "authorizes", "role", "roles", "permission", "permissions", "privilege", "privileges", "privileged", "segregation of duties"], [
        "Access control configuration screenshots or exports",
        "Authentication system logs or access review records",
        "Privileged access management documentation",
    ]),
    (["monitor", "monitors", "monitoring", "monitored", "detect", "detects", "detection", "alert", "alerts", "alarming", "log", "logs", "logging", "hunt", "hunts", "hunting", "surveillance"], [
        "Monitoring/alarming dashboard screenshots",
        "Alert rule configuration documentation",
        "Sample monitoring logs demonstrating detection",
    ]),
    (["encrypt", "encrypts", "encryption", "encrypted", "cryptography", "cipher", "ciphers", "key management", "tls", "ssl", "digital signature", "digital signatures"], [
        "Encryption configuration documentation",
        "Key management policy and procedures",
        "Encryption-in-transit and at-rest evidence",
    ]),
    (["training", "trainings", "awareness", "education", "competence"], [
        "Training program documentation and schedule",
        "Training completion records or attestations",
        "Awareness campaign materials",
    ]),
    (["vendor", "vendors", "third party", "third parties", "outsource", "outsources", "outsourcing", "subservice", "subservice organization", "service provider", "service providers"], [
        "Vendor assessment questionnaires",
        "Contractual security requirements documentation",
        "Vendor SOC report review records",
    ]),
    (["incident", "incidents", "breach", "breaches", "response", "containment", "remediation", "corrective", "corrective action"], [
        "Incident response plan",
        "Incident report or post-incident review documentation",
        "Incident handling exercise or tabletop results",
    ]),
    (["change", "changes", "changing", "deploy", "deploys", "deployment", "release", "releases", "patch", "patches", "patching", "configuration management"], [
        "Change request tickets and approval records",
        "Change management policy and procedures",
        "Pre/post change testing results",
    ]),
    (["backup", "backups", "backing up", "recover", "recovers", "recovery", "bcdr", "drp", "bcp", "continuity", "restore", "restores", "restoration", "failover"], [
        "Backup schedule and verification logs",
        "Disaster recovery test results",
        "Business continuity plan documentation",
    ]),
    (["physical", "facility", "facilities", "environmental", "equipment", "visitor", "visitors", "maintenance"], [
        "Physical access control logs",
        "Visitor management records",
        "Environmental monitoring system evidence",
    ]),
    (["review", "reviews", "reviewed", "reviewing", "assess", "assesses", "assessment", "assessments", "audit", "audits", "auditing", "evaluate", "evaluates", "evaluation", "examine", "examines", "examination"], [
        "Completed review or assessment documentation",
        "Review schedule and tracking records",
        "Action items from review with closure evidence",
    ]),
    (["communication", "communications", "report", "reports", "reporting", "disclosure", "disclosures", "notification", "notifications"], [
        "Communication or reporting policy",
        "Sample reports or notifications",
        "Distribution list or acknowledgment records",
    ]),
    (["data", "information", "privacy", "personal", "pii", "consent", "consents"], [
        "Data classification and handling policy",
        "Data flow diagrams or data inventory",
        "Consent collection or privacy notice evidence",
    ]),
    (["inventory", "inventories", "asset inventory", "hardware inventory", "software inventory"], [
        "Asset inventory records",
        "Configuration management database exports",
        "Software license and version documentation",
    ]),
    (["risk", "risks", "risking"], [
        "Risk assessment documentation",
        "Risk register with treatment plans",
        "Risk acceptance or risk review evidence",
    ]),
    (["test", "tests", "testing", "tested", "validate", "validates", "validation", "verification", "verify", "verifies", "quality assurance"], [
        "Test plan and results documentation",
        "Verification or validation evidence",
        "Test schedule and sign-off records",
    ]),
    (["role", "roles", "responsibility", "responsibilities", "owner", "owners", "accountability"], [
        "Role definitions and responsibility matrix",
        "Organizational chart",
        "Delegation of authority documentation",
    ]),
    (["decommission", "decommissions", "decommissioning", "disposal", "sanitization", "removal", "termination", "offboarding"], [
        "Decommissioning or disposal policy",
        "Data sanitization verification certificates",
        "Offboarding checklist completion records",
    ]),
    (["capacity", "capacities", "performance", "throughput", "scalability"], [
        "Capacity management plan",
        "Performance monitoring dashboard screenshots",
        "Capacity trend analysis reports",
    ]),
]


def get_pof_hints(pof: Dict[str, Any]) -> List[str]:
    """Return evidence-collection hint strings for a single Point of Focus."""
    text = (pof.get("text") or "").lower()
    theme = (pof.get("theme") or "").lower()
    combined = f"{text} {theme}"
    words = set(w for w in _WORD.findall(combined))
    hints: List[str] = []
    seen: set[int] = set()
    for keywords, hint_set in _RULES:
        matched = False
        for kw in keywords:
            if " " in kw:
                if kw in combined:
                    matched = True
                    break
            else:
                if kw in words:
                    matched = True
                    break
        if matched:
            for h in hint_set:
                h_id = hash(h)
                if h_id not in seen:
                    hints.append(h)
                    seen.add(h_id)
            if len(hints) >= 4:
                break
    if not hints:
        hints = [
            "Relevant policy or procedure documentation",
            "Configuration records or screenshots",
            "Audit logs demonstrating compliance",
        ]
    return hints[:4]
