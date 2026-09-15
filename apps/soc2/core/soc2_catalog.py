"""SOC 2 Trust Services Criteria — AICPA 2017 TSC (2022 Revised Points of Focus).

Each criterion includes the official AICPA Points of Focus with internal numbering
(e.g., CC6.1.P1) for database-trackable, evidence-mappable compliance tracking.
Points of Focus are illustrative, not all-inclusive — users may mark applicable ones
and justify exclusions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from soc2_pof_paraphrases import POF_PARAPHRASES


def _pof_block(cid: str) -> list:
    """Official-order Points of Focus for a criterion, from faithful paraphrases."""
    if cid not in POF_PARAPHRASES:
        return []
    entries = []
    for n, text in enumerate(POF_PARAPHRASES[cid], 1):
        short = _pof_theme(text)
        entries.append({"id": f"{cid}.P{n}", "theme": short, "text": text})
    return entries


def _pof_theme(text: str) -> str:
    """Short, readable badge label derived from the paraphrase text."""
    words = text.replace(",", "").split()
    head = words[:8]
    short = " ".join(head).strip().rstrip(".")
    if len(words) > 8:
        short += "…"
    return short


SOC2_CONTROLS: Dict[str, Dict[str, Any]] = {
    # ═══════════════════════════════════════════════════════════════
    # CC1 — Control Environment
    # ═══════════════════════════════════════════════════════════════
    "CC1.1": {
        "category": "Security",
        "title": "Integrity and Ethical Values",
        "description": "The entity demonstrates a commitment to integrity and ethical values.",
        "points_of_focus": _pof_block("CC1.1"),
    },
    "CC1.2": {
        "category": "Security",
        "title": "Board Independence and Oversight",
        "description": "The board of directors demonstrates independence from management and exercises oversight of the development and performance of internal control.",
        "points_of_focus": _pof_block("CC1.2"),
    },
    "CC1.3": {
        "category": "Security",
        "title": "Organizational Structure",
        "description": "Management establishes, with board oversight, structures, reporting lines, and appropriate authorities and responsibilities in the pursuit of objectives.",
        "points_of_focus": _pof_block("CC1.3"),
    },
    "CC1.4": {
        "category": "Security",
        "title": "Commitment to Competence",
        "description": "The entity demonstrates a commitment to attract, develop, and retain competent individuals in alignment with objectives.",
        "points_of_focus": _pof_block("CC1.4"),
    },
    "CC1.5": {
        "category": "Security",
        "title": "Accountability",
        "description": "The entity holds individuals accountable for their internal control responsibilities in the pursuit of objectives.",
        "points_of_focus": _pof_block("CC1.5"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC2 — Communication and Information
    # ═══════════════════════════════════════════════════════════════
    "CC2.1": {
        "category": "Security",
        "title": "Use Relevant Information",
        "description": "The entity obtains or generates and uses relevant, quality information to support the functioning of internal control.",
        "points_of_focus": _pof_block("CC2.1"),
    },
    "CC2.2": {
        "category": "Security",
        "title": "Internal Communication",
        "description": "The entity internally communicates information, including objectives and responsibilities for internal control, necessary to support the functioning of internal control.",
        "points_of_focus": _pof_block("CC2.2"),
    },
    "CC2.3": {
        "category": "Security",
        "title": "External Communication",
        "description": "The entity communicates with external parties regarding matters affecting the functioning of internal control.",
        "points_of_focus": _pof_block("CC2.3"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC3 — Risk Assessment
    # ═══════════════════════════════════════════════════════════════
    "CC3.1": {
        "category": "Security",
        "title": "Specified Objectives",
        "description": "The entity specifies objectives with sufficient clarity to enable the identification and assessment of risks relating to objectives.",
        "points_of_focus": _pof_block("CC3.1"),
    },
    "CC3.2": {
        "category": "Security",
        "title": "Risk Identification",
        "description": "The entity identifies risks to the achievement of its objectives across the entity and analyzes risks as a basis for determining how the risks should be managed.",
        "points_of_focus": _pof_block("CC3.2"),
    },
    "CC3.3": {
        "category": "Security",
        "title": "Fraud Consideration",
        "description": "The entity considers the potential for fraud in assessing risks to the achievement of objectives.",
        "points_of_focus": _pof_block("CC3.3"),
    },
    "CC3.4": {
        "category": "Security",
        "title": "Change Identification",
        "description": "The entity identifies and assesses changes that could significantly impact the system of internal control.",
        "points_of_focus": _pof_block("CC3.4"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC4 — Monitoring Activities
    # ═══════════════════════════════════════════════════════════════
    "CC4.1": {
        "category": "Security",
        "title": "Ongoing Monitoring",
        "description": "The entity selects, develops, and performs ongoing and/or separate evaluations to ascertain whether the components of internal control are present and functioning.",
        "points_of_focus": _pof_block("CC4.1"),
    },
    "CC4.2": {
        "category": "Security",
        "title": "Deficiency Communication",
        "description": "The entity evaluates and communicates internal control deficiencies in a timely manner to those parties responsible for taking corrective action, including senior management and the board of directors, as appropriate.",
        "points_of_focus": _pof_block("CC4.2"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC5 — Control Activities
    # ═══════════════════════════════════════════════════════════════
    "CC5.1": {
        "category": "Security",
        "title": "Risk Mitigation Selection",
        "description": "The entity selects and develops control activities that contribute to the mitigation of risks to the achievement of objectives to acceptable levels.",
        "points_of_focus": _pof_block("CC5.1"),
    },
    "CC5.2": {
        "category": "Security",
        "title": "Technology Controls",
        "description": "The entity also selects and develops general control activities over technology to support the achievement of objectives.",
        "points_of_focus": _pof_block("CC5.2"),
    },
    "CC5.3": {
        "category": "Security",
        "title": "Policy Deployment",
        "description": "The entity deploys control activities through policies that establish what is expected and in procedures that put policies into action.",
        "points_of_focus": _pof_block("CC5.3"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC6 — Logical and Physical Access
    # ═══════════════════════════════════════════════════════════════
    "CC6.1": {
        "category": "Security",
        "title": "Logical Access Security",
        "description": "The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives.",
        "points_of_focus": _pof_block("CC6.1"),
    },
    "CC6.2": {
        "category": "Security",
        "title": "User Access Provisioning",
        "description": "Prior to issuing system credentials and granting system access, the entity registers and authorizes new internal and external users whose access is administered by the entity. For those users whose access is administered by the entity, user system credentials are removed when user access is no longer authorized.",
        "points_of_focus": _pof_block("CC6.2"),
    },
    "CC6.3": {
        "category": "Security",
        "title": "Privileged Access Management",
        "description": "The entity authorizes, modifies, or removes access to data, software, functions, and other protected information assets based on roles, responsibilities, or the system design and changes, giving consideration to the concepts of least privilege and segregation of duties, to meet the entity's objectives.",
        "points_of_focus": _pof_block("CC6.3"),
    },
    "CC6.4": {
        "category": "Security",
        "title": "Physical Access Restrictions",
        "description": "The entity restricts physical access to facilities and protected information assets (for example, data center facilities, backup media storage, and other sensitive locations) to authorized personnel to meet the entity's objectives.",
        "points_of_focus": _pof_block("CC6.4"),
    },
    "CC6.5": {
        "category": "Security",
        "title": "Asset Decommissioning",
        "description": "The entity discontinues logical and physical protections over physical assets only after the ability to read or recover data and software from those assets has been diminished and is no longer required to meet the entity's objectives.",
        "points_of_focus": _pof_block("CC6.5"),
    },
    "CC6.6": {
        "category": "Security",
        "title": "External Threats",
        "description": "The entity implements logical access security measures to protect against threats from sources outside its system boundaries.",
        "points_of_focus": _pof_block("CC6.6"),
    },
    "CC6.7": {
        "category": "Security",
        "title": "Data Transmission",
        "description": "The entity restricts the transmission, movement, and removal of information to authorized internal and external users and processes, and protects it during transmission, movement, or removal to meet the entity's objectives.",
        "points_of_focus": _pof_block("CC6.7"),
    },
    "CC6.8": {
        "category": "Security",
        "title": "Malware Prevention",
        "description": "The entity implements controls to prevent or detect and act upon the introduction of unauthorized or malicious software to meet the entity's objectives.",
        "points_of_focus": _pof_block("CC6.8"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC7 — System Operations
    # ═══════════════════════════════════════════════════════════════
    "CC7.1": {
        "category": "Security",
        "title": "Detection and Monitoring",
        "description": "To meet its objectives, the entity uses detection and monitoring procedures to identify (1) changes to configurations that result in the introduction of new vulnerabilities, and (2) susceptibilities to newly discovered vulnerabilities.",
        "points_of_focus": _pof_block("CC7.1"),
    },
    "CC7.2": {
        "category": "Security",
        "title": "Anomaly Monitoring",
        "description": "The entity monitors system components and the operation of those components for anomalies that are indicative of malicious acts, natural disasters, and errors affecting the entity's ability to meet its objectives; anomalies are analyzed to determine whether they represent security events.",
        "points_of_focus": _pof_block("CC7.2"),
    },
    "CC7.3": {
        "category": "Security",
        "title": "Security Event Evaluation",
        "description": "The entity evaluates security events to determine whether they could or have resulted in a failure of the entity to meet its objectives (security incidents) and, if so, takes actions to prevent or address such failures.",
        "points_of_focus": _pof_block("CC7.3"),
    },
    "CC7.4": {
        "category": "Security",
        "title": "Incident Response",
        "description": "The entity responds to identified security incidents by executing a defined incident-response program to understand, contain, remediate, and communicate security incidents, as appropriate.",
        "points_of_focus": _pof_block("CC7.4"),
    },
    "CC7.5": {
        "category": "Security",
        "title": "Recovery from Security Incidents",
        "description": "The entity identifies, develops, and implements activities to recover from identified security incidents.",
        "points_of_focus": _pof_block("CC7.5"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC8 — Change Management
    # ═══════════════════════════════════════════════════════════════
    "CC8.1": {
        "category": "Security",
        "title": "Change Management Process",
        "description": "The entity authorizes, designs, develops or acquires, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures to meet its objectives.",
        "points_of_focus": _pof_block("CC8.1"),
    },
    # ═══════════════════════════════════════════════════════════════
    # CC9 — Risk Mitigation
    # ═══════════════════════════════════════════════════════════════
    "CC9.1": {
        "category": "Security",
        "title": "Business Disruption Risk Mitigation",
        "description": "The entity identifies, selects, and develops risk mitigation activities for risks arising from potential business disruptions.",
        "points_of_focus": _pof_block("CC9.1"),
    },
    "CC9.2": {
        "category": "Security",
        "title": "Vendor and Business Partner Risk",
        "description": "The entity assesses and manages risks associated with vendors and business partners.",
        "points_of_focus": _pof_block("CC9.2"),
    },
    # ═══════════════════════════════════════════════════════════════
    # A1 — Availability
    # ═══════════════════════════════════════════════════════════════
    "A1.1": {
        "category": "Availability",
        "title": "Capacity Management",
        "description": "The entity maintains, monitors, and evaluates current processing capacity and use of system components (infrastructure, data, and software) to manage capacity demand and to enable the implementation of additional capacity to help meet its objectives.",
        "points_of_focus": _pof_block("A1.1"),
    },
    "A1.2": {
        "category": "Availability",
        "title": "Environmental Protections and Recovery Infrastructure",
        "description": "The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections, software, data backup processes, and recovery infrastructure to meet its objectives.",
        "points_of_focus": _pof_block("A1.2"),
    },
    "A1.3": {
        "category": "Availability",
        "title": "Recovery and Testing",
        "description": "The entity tests recovery plan procedures supporting system recovery to meet its objectives.",
        "points_of_focus": _pof_block("A1.3"),
    },
    # ═══════════════════════════════════════════════════════════════
    # C1 — Confidentiality
    # ═══════════════════════════════════════════════════════════════
    "C1.1": {
        "category": "Confidentiality",
        "title": "Confidential Information Identification",
        "description": "The entity identifies and maintains confidential information to meet the entity's objectives related to confidentiality.",
        "points_of_focus": _pof_block("C1.1"),
    },
    "C1.2": {
        "category": "Confidentiality",
        "title": "Confidential Information Disposal",
        "description": "The entity disposes of confidential information to meet the entity's objectives related to confidentiality.",
        "points_of_focus": _pof_block("C1.2"),
    },
    # ═══════════════════════════════════════════════════════════════
    # PI1 — Processing Integrity
    # ═══════════════════════════════════════════════════════════════
    "PI1.1": {
        "category": "Processing Integrity",
        "title": "Quality Information for Processing",
        "description": "The entity obtains or generates, uses, and communicates relevant, quality information regarding the objectives related to processing, including definitions of data processed and product and service specifications, to support the use of products and services.",
        "points_of_focus": _pof_block("PI1.1"),
    },
    "PI1.2": {
        "category": "Processing Integrity",
        "title": "Input Completeness and Accuracy",
        "description": "The entity implements policies and procedures over system inputs, including controls over completeness and accuracy, to result in products, services, and reporting to meet the entity's objectives.",
        "points_of_focus": _pof_block("PI1.2"),
    },
    "PI1.3": {
        "category": "Processing Integrity",
        "title": "Processing Policies and Procedures",
        "description": "The entity implements policies and procedures over system processing to result in products, services, and reporting to meet the entity's objectives.",
        "points_of_focus": _pof_block("PI1.3"),
    },
    "PI1.4": {
        "category": "Processing Integrity",
        "title": "Output Delivery",
        "description": "The entity implements policies and procedures to make available or deliver output completely, accurately, and timely in accordance with specifications to meet the entity's objectives.",
        "points_of_focus": _pof_block("PI1.4"),
    },
    "PI1.5": {
        "category": "Processing Integrity",
        "title": "Storage of Inputs, Processing, and Outputs",
        "description": "The entity implements policies and procedures to store inputs, items in processing, and outputs completely, accurately, and timely in accordance with system specifications to meet the entity's objectives.",
        "points_of_focus": _pof_block("PI1.5"),
    },
    # ═══════════════════════════════════════════════════════════════
    # P1 — Privacy
    # ═══════════════════════════════════════════════════════════════
    "P1.1": {
        "category": "Privacy",
        "title": "Notice to Data Subjects",
        "description": "The entity provides notice to data subjects about its privacy practices to meet the entity's objectives related to privacy. The notice is updated and communicated to data subjects in a timely manner for changes to the entity's privacy practices, including changes in the use of personal information, to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P1.1"),
    },
    "P2.1": {
        "category": "Privacy",
        "title": "Choice and Consent",
        "description": "The entity communicates choices available regarding the collection, use, retention, disclosure, and disposal of personal information to the data subjects and the consequences, if any, of each choice. Explicit consent for the collection, use, retention, disclosure, and disposal of personal information is obtained from data subjects or other authorized persons, if required. Such consent is obtained only for the intended purpose of the information to meet the entity's objectives related to privacy. The entity's basis for determining implicit consent for the collection, use, retention, disclosure, and disposal of personal information is documented.",
        "points_of_focus": _pof_block("P2.1"),
    },
    "P3.1": {
        "category": "Privacy",
        "title": "Collection",
        "description": "Personal information is collected consistent with the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P3.1"),
    },
    "P3.2": {
        "category": "Privacy",
        "title": "Explicit Consent",
        "description": "For information requiring explicit consent, the entity communicates the need for such consent as well as the consequences of a failure to provide consent for the request for personal information and obtains the consent prior to the collection of the information to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P3.2"),
    },
    "P4.1": {
        "category": "Privacy",
        "title": "Use, Retention, and Disposal",
        "description": "The entity limits the use of personal information to the purposes identified in the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P4.1"),
    },
    "P4.2": {
        "category": "Privacy",
        "title": "Retention",
        "description": "The entity retains personal information consistent with the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P4.2"),
    },
    "P4.3": {
        "category": "Privacy",
        "title": "Secure Disposal",
        "description": "The entity securely disposes of personal information to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P4.3"),
    },
    "P5.1": {
        "category": "Privacy",
        "title": "Access",
        "description": "The entity grants identified and authenticated data subjects the ability to access their stored personal information for review and, upon request, provides physical or electronic copies of that information to data subjects to meet the entity's objectives related to privacy. If access is denied, data subjects are informed of the denial and reason for such denial, as required, to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P5.1"),
    },
    "P5.2": {
        "category": "Privacy",
        "title": "Correction",
        "description": "The entity corrects, amends, or appends personal information based on information provided by data subjects and communicates such information to third parties, as committed or required, to meet the entity's objectives related to privacy. If a request for correction is denied, data subjects are informed of the denial and reason for such denial to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P5.2"),
    },
    "P6.1": {
        "category": "Privacy",
        "title": "Disclosure and Notification",
        "description": "The entity discloses personal information to third parties with the explicit consent of data subjects and such consent is obtained prior to disclosure to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P6.1"),
    },
    "P6.2": {
        "category": "Privacy",
        "title": "Record of Authorized Disclosures",
        "description": "The entity creates and retains a complete, accurate, and timely record of authorized disclosures of personal information to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P6.2"),
    },
    "P6.3": {
        "category": "Privacy",
        "title": "Record of Unauthorized Disclosures",
        "description": "The entity creates and retains a complete, accurate, and timely record of detected or reported unauthorized disclosures (including breaches) of personal information to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P6.3"),
    },
    "P6.4": {
        "category": "Privacy",
        "title": "Vendor Privacy Commitments",
        "description": "The entity obtains privacy commitments from vendors and other third parties who have access to personal information to meet the entity's objectives related to privacy. The entity assesses those parties' compliance on a periodic and as-needed basis and takes corrective action, if necessary.",
        "points_of_focus": _pof_block("P6.4"),
    },
    "P6.5": {
        "category": "Privacy",
        "title": "Vendor Breach Notification Commitments",
        "description": "The entity obtains commitments from vendors and other third parties with access to personal information to notify the entity in the event of actual or suspected unauthorized disclosures of personal information. Such notifications are reported to appropriate personnel and acted on in accordance with established incident-response procedures to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P6.5"),
    },
    "P6.6": {
        "category": "Privacy",
        "title": "Breach and Incident Notification",
        "description": "The entity provides notification of breaches and incidents to affected data subjects, regulators, and others to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P6.6"),
    },
    "P6.7": {
        "category": "Privacy",
        "title": "Accounting of Personal Information",
        "description": "The entity provides data subjects with an accounting of the personal information held and disclosure of the data subjects' personal information, upon the data subjects' request, to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P6.7"),
    },
    "P7.1": {
        "category": "Privacy",
        "title": "Quality",
        "description": "The entity collects and maintains accurate, up-to-date, complete, and relevant personal information to meet the entity's objectives related to privacy.",
        "points_of_focus": _pof_block("P7.1"),
    },
    "P8.1": {
        "category": "Privacy",
        "title": "Monitoring and Enforcement",
        "description": "The entity implements a process for receiving, addressing, resolving, and communicating the resolution of inquiries, complaints, and disputes from data subjects and others and periodically monitors compliance to meet the entity's objectives related to privacy. Corrections and other necessary actions related to identified deficiencies are made or taken in a timely manner.",
        "points_of_focus": _pof_block("P8.1"),
    },
}

from tsc_2017_official import TSC_CRITERION_STATEMENTS  # noqa: E402

for _cid, _meta in SOC2_CONTROLS.items():
    _meta["official_title"] = TSC_CRITERION_STATEMENTS[_cid]


def list_controls() -> List[Dict[str, Any]]:
    return [{"id": cid, "code": cid, **meta} for cid, meta in SOC2_CONTROLS.items()]


def get_points_of_focus(criterion_id: str) -> List[Dict[str, str]]:
    entry = SOC2_CONTROLS.get(criterion_id)
    if entry is None:
        return []
    return entry.get("points_of_focus", [])


def list_pof_ids() -> List[str]:
    ids: List[str] = []
    for meta in SOC2_CONTROLS.values():
        for pof in meta.get("points_of_focus", []):
            ids.append(pof["id"])
    return ids


def pof_count() -> int:
    return len(list_pof_ids())


def pof_count_per_criterion(criterion_id: str) -> int:
    return len(get_points_of_focus(criterion_id))
