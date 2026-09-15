"""Common Control Framework — cross-framework control topic mapping.

Each CCF topic represents a control domain that exists across multiple frameworks.
The mapping table links framework-specific control IDs to their CCF topics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ─── Supported frameworks ──────────────────────────────

FRAMEWORK_IDS = ("cmmc", "soc2", "aigovernance")

frameworks: Dict[str, str] = {
    "cmmc": "CMMC 2.0 (NIST SP 800-171 Rev 2)",
    "soc2": "SOC 2 (AICPA TSC 2017)",
    "aigovernance": "AI Governance (EU AI Act / NIST AI RMF / ISO 42001)",
}


def list_frameworks() -> List[Dict[str, str]]:
    return [{"id": k, "name": v} for k, v in frameworks.items()]


# ─── CCF Topic definition ──────────────────────────────


@dataclass
class CCFTopic:
    id: str
    title: str
    description: str
    cmmc: List[str] = field(default_factory=list)
    soc2: List[str] = field(default_factory=list)
    aigovernance: List[str] = field(default_factory=list)


# ─── Topics ────────────────────────────────────────────

_TOPICS: List[CCFTopic] = [
    CCFTopic(
        id="access-control",
        title="Access Control & Identity Management",
        description="Limit system access to authorized users, enforce least privilege, manage identities.",
        cmmc=[
            "AC.L2-3.1.1", "AC.L2-3.1.2", "AC.L2-3.1.3", "AC.L2-3.1.4",
            "AC.L2-3.1.5", "AC.L2-3.1.6", "AC.L2-3.1.7", "AC.L2-3.1.8",
            "AC.L2-3.1.9", "AC.L2-3.1.10", "AC.L2-3.1.11", "AC.L2-3.1.12",
            "AC.L2-3.1.13", "AC.L2-3.1.14", "AC.L2-3.1.15", "AC.L2-3.1.16",
            "AC.L2-3.1.17", "AC.L2-3.1.18", "AC.L2-3.1.19", "AC.L2-3.1.20",
            "AC.L2-3.1.21", "AC.L2-3.1.22",
        ],
        soc2=["CC6.1", "CC6.2", "CC6.3", "CC6.4", "CC6.5", "CC6.6", "CC6.7", "CC6.8"],
        aigovernance=["NIST-GOVERN-1"],
    ),
    CCFTopic(
        id="awareness-training",
        title="Awareness & Training",
        description="Ensure personnel are trained in security and compliance responsibilities.",
        cmmc=["AT.L2-3.2.1", "AT.L2-3.2.2", "AT.L2-3.2.3"],
        soc2=["CC1.1", "CC1.2", "CC1.3", "CC1.4", "CC1.5"],
        aigovernance=["ISO-6.2"],
    ),
    CCFTopic(
        id="audit-logging",
        title="Audit Logging & Monitoring",
        description="Maintain audit logs, monitor for anomalies, and protect log integrity.",
        cmmc=[
            "AU.L2-3.3.1", "AU.L2-3.3.2", "AU.L2-3.3.3", "AU.L2-3.3.4",
            "AU.L2-3.3.5", "AU.L2-3.3.6", "AU.L2-3.3.7", "AU.L2-3.3.8", "AU.L2-3.3.9",
        ],
        soc2=["CC7.1", "CC7.2", "CC7.3", "CC7.4", "CC7.5"],
        aigovernance=["EU-14", "ISO-9.1"],
    ),
    CCFTopic(
        id="configuration-management",
        title="Configuration & Change Management",
        description="Establish baseline configurations, manage changes, and prevent unauthorized modifications.",
        cmmc=[
            "CM.L2-3.4.1", "CM.L2-3.4.2", "CM.L2-3.4.3", "CM.L2-3.4.4",
            "CM.L2-3.4.5", "CM.L2-3.4.6", "CM.L2-3.4.7", "CM.L2-3.4.8", "CM.L2-3.4.9",
        ],
        soc2=["CC8.1"],
        aigovernance=["ISO-8.3"],
    ),
    CCFTopic(
        id="identification-authentication",
        title="Identification & Authentication",
        description="Uniquely identify users and devices; enforce strong authentication.",
        cmmc=[
            "IA.L2-3.5.1", "IA.L2-3.5.2", "IA.L2-3.5.3", "IA.L2-3.5.4",
            "IA.L2-3.5.5", "IA.L2-3.5.6", "IA.L2-3.5.7", "IA.L2-3.5.8",
            "IA.L2-3.5.9", "IA.L2-3.5.10", "IA.L2-3.5.11",
        ],
        soc2=["CC6.1", "CC6.2", "CC6.3"],
        aigovernance=["NIST-GOVERN-1"],
    ),
    CCFTopic(
        id="incident-response",
        title="Incident Response",
        description="Establish incident response procedures, test them, and track resolution.",
        cmmc=["IR.L2-3.6.1", "IR.L2-3.6.2", "IR.L2-3.6.3"],
        soc2=["CC7.1", "CC7.4", "CC7.5"],
        aigovernance=["EU-73"],
    ),
    CCFTopic(
        id="risk-management",
        title="Risk Assessment & Management",
        description="Identify, assess, and mitigate risks to organizational objectives.",
        cmmc=["RA.L2-3.11.1", "RA.L2-3.11.2", "RA.L2-3.11.3"],
        soc2=["CC3.1", "CC3.2", "CC3.3", "CC3.4"],
        aigovernance=["EU-9", "ISO-8.1", "NIST-MAP-1", "NIST-MAP-2"],
    ),
    CCFTopic(
        id="vendor-risk",
        title="Vendor & Third-Party Risk",
        description="Assess and monitor the risk posed by third-party service providers.",
        cmmc=["PS.L2-3.9.1", "PS.L2-3.9.2"],
        soc2=["CC9.1", "CC9.2"],
        aigovernance=["ISO-8.4"],
    ),
    CCFTopic(
        id="data-protection",
        title="Data Protection & Privacy",
        description="Protect data at rest and in transit; manage privacy obligations.",
        cmmc=[
            "MP.L2-3.8.1", "MP.L2-3.8.2", "MP.L2-3.8.3", "MP.L2-3.8.4",
            "MP.L2-3.8.5", "MP.L2-3.8.6", "MP.L2-3.8.7", "MP.L2-3.8.8", "MP.L2-3.8.9",
            "SC.L2-3.13.1", "SC.L2-3.13.2", "SC.L2-3.13.3", "SC.L2-3.13.4",
            "SC.L2-3.13.5", "SC.L2-3.13.6", "SC.L2-3.13.7", "SC.L2-3.13.8",
            "SC.L2-3.13.9", "SC.L2-3.13.10", "SC.L2-3.13.11", "SC.L2-3.13.12",
            "SC.L2-3.13.13", "SC.L2-3.13.14", "SC.L2-3.13.15", "SC.L2-3.13.16",
        ],
        soc2=["C1.1", "C1.2", "P1.1", "P2.1", "P3.1", "P4.1", "P5.1", "P6.1", "P7.1", "P8.1"],
        aigovernance=["EU-50", "ISO-5.2"],
    ),
    CCFTopic(
        id="security-assessment",
        title="Security Assessment & Authorization",
        description="Periodically assess controls and authorize system operation.",
        cmmc=["CA.L2-3.12.1", "CA.L2-3.12.2", "CA.L2-3.12.3", "CA.L2-3.12.4"],
        soc2=["CC4.1", "CC4.2"],
        aigovernance=["ISO-9.1"],
    ),
    CCFTopic(
        id="system-integrity",
        title="System & Information Integrity",
        description="Protect against malware, monitor for intrusions, and manage flaws.",
        cmmc=[
            "SI.L2-3.14.1", "SI.L2-3.14.2", "SI.L2-3.14.3", "SI.L2-3.14.4",
            "SI.L2-3.14.5", "SI.L2-3.14.6", "SI.L2-3.14.7",
        ],
        soc2=["CC7.1", "CC7.2", "PI1.1", "PI1.2", "PI1.3", "PI1.4", "PI1.5"],
        aigovernance=["EU-16", "NIST-MEASURE-1", "NIST-MEASURE-2"],
    ),
    CCFTopic(
        id="physical-security",
        title="Physical & Environmental Security",
        description="Protect physical facilities and equipment from unauthorized access and environmental threats.",
        cmmc=["PE.L2-3.10.1", "PE.L2-3.10.2", "PE.L2-3.10.3", "PE.L2-3.10.4", "PE.L2-3.10.5", "PE.L2-3.10.6"],
        soc2=["CC6.4", "CC6.5"],
        aigovernance=["NIST-GOVERN-1"],
    ),
    CCFTopic(
        id="maintenance",
        title="System Maintenance",
        description="Perform timely maintenance and control remote maintenance sessions.",
        cmmc=["MA.L2-3.7.1", "MA.L2-3.7.2", "MA.L2-3.7.3", "MA.L2-3.7.4", "MA.L2-3.7.5", "MA.L2-3.7.6"],
        soc2=["CC8.1"],
        aigovernance=["ISO-8.3"],
    ),
    CCFTopic(
        id="ai-bias-fairness",
        title="AI Bias & Fairness",
        description="Assess and mitigate algorithmic bias; ensure fair outcomes across demographic groups.",
        cmmc=[],
        soc2=[],
        aigovernance=["NIST-MEASURE-1", "NIST-MEASURE-2"],
    ),
    CCFTopic(
        id="ai-transparency",
        title="AI Transparency & Explainability",
        description="Document AI system purpose, capabilities, and limitations; provide explainability.",
        cmmc=[],
        soc2=[],
        aigovernance=["EU-26", "ISO-8.2"],
    ),
    CCFTopic(
        id="ai-human-oversight",
        title="AI Human Oversight",
        description="Define human-in-the-loop, human-on-the-loop, or human-in-command for AI systems.",
        cmmc=[],
        soc2=[],
        aigovernance=["NIST-GOVERN-3", "ISO-8.3"],
    ),
    CCFTopic(
        id="availability",
        title="Availability & Business Continuity",
        description="Maintain system availability, perform backups, and plan for business continuity.",
        cmmc=[],
        soc2=["A1.1", "A1.2", "A1.3"],
        aigovernance=["NIST-MANAGE-1", "NIST-MANAGE-2"],
    ),
]

# ─── Build reverse index ───────────────────────────────

_control_to_topics: Dict[str, List[str]] = {}


def _build_index():
    """Build reverse map: framework:control_id -> list of CCF topic IDs."""
    _control_to_topics.clear()
    for topic in _TOPICS:
        for framework in FRAMEWORK_IDS:
            for cid in getattr(topic, framework, []):
                key = f"{framework}:{cid}"
                _control_to_topics.setdefault(key, []).append(topic.id)


_build_index()


# ─── Public API ────────────────────────────────────────


def get_ccf_topics() -> List[CCFTopic]:
    return list(_TOPICS)


def get_framework_controls(framework_id: str) -> List[Dict[str, str | List[str]]]:
    """List all CCF topics and which controls in the given framework map to each."""
    result: List[Dict[str, str | List[str]]] = []
    for topic in _TOPICS:
        controls = getattr(topic, framework_id, [])
        if controls:
            result.append({"topic_id": topic.id, "title": topic.title, "controls": controls})
    return result


def map_control_to_ccf(framework_id: str, control_id: str) -> List[Dict[str, str]]:
    """Given a framework-specific control ID, return the CCF topics it maps to."""
    key = f"{framework_id}:{control_id}"
    topic_ids = _control_to_topics.get(key, [])
    return [{"topic_id": tid, "title": next((t.title for t in _TOPICS if t.id == tid), "")} for tid in topic_ids]


def get_mapped_controls(
    source_framework: str,
    target_framework: str,
    control_id: str,
) -> List[Dict[str, str]]:
    """Translate a control from one framework to equivalent controls in another."""
    topic_ids = [t["topic_id"] for t in map_control_to_ccf(source_framework, control_id)]
    targets: List[Dict[str, str]] = []
    for tid in topic_ids:
        topic = next((t for t in _TOPICS if t.id == tid), None)
        if topic is None:
            continue
        for cid in getattr(topic, target_framework, []):
            targets.append({"topic_id": tid, "control_id": cid})
    return targets
