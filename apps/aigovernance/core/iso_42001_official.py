"""Official ISO/IEC 42001:2023 headings extracted from docs/ISO-IEC-42001-2023.pdf.

Source: docs/ISO-IEC-42001-2023.pdf (full standard, 62 pages; "Price based on
51 pages" per the document itself). Extracted via pdftotext on 2026-08-12.

This module is the canonical reference for clause and Annex A objective
wording. The app catalog (ai_controls_catalog.py) keeps short display titles
and carries the official wording in `official_title`; tests assert they match
these tables.

NOTE: Annex A Table A.1 contains 38 controls (A.x.y) under the 9 objectives.
The first control of each objective is numbered .2 (e.g. A.2.2) — the .1
numbering is not used in the printed standard. Objective A.6 is structured
as two sub-objectives (A.6.1 Management guidance for AI system development,
A.6.2 AI system life cycle) whose controls are numbered A.6.1.2–A.6.1.3 and
A.6.2.2–A.6.2.8.
"""

OFFICIAL_ISO_42001_CLAUSES: dict[str, str] = {
    "4.1": "Understanding the organization and its context",
    "4.2": "Understanding the needs and expectations of interested parties",
    "4.3": "Determining the scope of the AI management system",
    "4.4": "AI management system",
    "5.1": "Leadership and commitment",
    "5.2": "AI policy",
    "5.3": "Roles, responsibilities and authorities",
    "6.1": "Actions to address risks and opportunities",
    "6.2": "AI objectives and planning to achieve them",
    "7.1": "Resources",
    "7.2": "Competence",
    "7.3": "Awareness",
    "7.4": "Communication",
    "7.5": "Documented information",
    "8.1": "Operational planning and control",
    "8.2": "AI risk assessment",
    "8.3": "AI risk treatment",
    "8.4": "AI system impact assessment",
    "9.1": "Monitoring, measurement, analysis and evaluation",
    "9.2": "Internal audit",
    "9.3": "Management review",
    "10.1": "Continual improvement",
    "10.2": "Nonconformity and corrective action",
}

OFFICIAL_ISO_42001_ANNEX_A: dict[str, str] = {
    "A.1": "General",
    "A.2": "Policies related to AI",
    "A.3": "Internal organization",
    "A.4": "Resources for AI systems",
    "A.5": "Assessing impacts of AI systems",
    "A.6": "AI system life cycle",
    "A.7": "Data for AI systems",
    "A.8": "Information for interested parties of AI systems",
    "A.9": "Use of AI systems",
    "A.10": "Third-party and customer relationships",
}

# Annex A Table A.1 control topics (38 controls), extracted verbatim from the PDF.
ANNEX_A_CONTROL_TOPICS: dict[str, dict[str, str]] = {
    "A.2": {
        "A.2.2": "AI policy",
        "A.2.3": "Alignment with other organizational policies",
        "A.2.4": "Review of the AI policy",
    },
    "A.3": {
        "A.3.2": "AI roles and responsibilities",
        "A.3.3": "Reporting of concerns",
    },
    "A.4": {
        "A.4.2": "Resource documentation",
        "A.4.3": "Data resources",
        "A.4.4": "Tooling resources",
        "A.4.5": "System and computing resources",
        "A.4.6": "Human resources",
    },
    "A.5": {
        "A.5.2": "AI system impact assessment process",
        "A.5.3": "Documentation of AI system impact assessments",
        "A.5.4": "Assessing AI system impact on individuals or groups of individuals",
        "A.5.5": "Assessing societal impacts of AI systems",
    },
    "A.6": {
        "A.6.1.2": "Objectives for responsible development of AI system",
        "A.6.1.3": "Processes for responsible AI system design and development",
        "A.6.2.2": "AI system requirements and specification",
        "A.6.2.3": "Documentation of AI system design and development",
        "A.6.2.4": "AI system verification and validation",
        "A.6.2.5": "AI system deployment",
        "A.6.2.6": "AI system operation and monitoring",
        "A.6.2.7": "AI system technical documentation",
        "A.6.2.8": "AI system recording of event logs",
    },
    "A.7": {
        "A.7.2": "Data for development and enhancement of AI system",
        "A.7.3": "Acquisition of data",
        "A.7.4": "Quality of data for AI systems",
        "A.7.5": "Data provenance",
        "A.7.6": "Data preparation",
    },
    "A.8": {
        "A.8.2": "System documentation and information for users",
        "A.8.3": "External reporting",
        "A.8.4": "Communication of incidents",
        "A.8.5": "Information for interested parties",
    },
    "A.9": {
        "A.9.2": "Processes for responsible use of AI systems",
        "A.9.3": "Objectives for responsible use of AI system",
        "A.9.4": "Intended use of the AI system",
    },
    "A.10": {
        "A.10.2": "Allocating responsibilities",
        "A.10.3": "Suppliers",
        "A.10.4": "Customers",
    },
}

# Official requirement sentence for each Annex A control (Control column of
# Table A.1), verbatim from the PDF (soft-hyphen line breaks resolved).
ANNEX_A_CONTROL_REQUIREMENTS: dict[str, str] = {
    "A.2.2": "The organization shall document a policy for the development or use of AI systems.",
    "A.2.3": "The organization shall determine where other policies can be affected by or apply to, the organization's objectives with respect to AI systems.",
    "A.2.4": "The AI policy shall be reviewed at planned intervals or additionally as needed to ensure its continuing suitability, adequacy and effectiveness.",
    "A.3.2": "Roles and responsibilities for AI shall be defined and allocated according to the needs of the organization.",
    "A.3.3": "The organization shall define and put in place a process to report concerns about the organization's role with respect to an AI system throughout its life cycle.",
    "A.4.2": "The organization shall identify and document relevant resources required for the activities at given AI system life cycle stages and other AI-related activities relevant for the organization.",
    "A.4.3": "As part of resource identification, the organization shall document information about the data resources utilized for the AI system.",
    "A.4.4": "As part of resource identification, the organization shall document information about the tooling resources utilized for the AI system.",
    "A.4.5": "As part of resource identification, the organization shall document information about the system and computing resources utilized for the AI system.",
    "A.4.6": "As part of resource identification, the organization shall document information about the human resources and their competences utilized for the development, deployment, operation, change management, maintenance, transfer and decommissioning, as well as verification and integration of the AI system.",
    "A.5.2": "The organization shall establish a process to assess the potential consequences for individuals or groups of individuals, or both, and societies that can result from the AI system throughout its life cycle.",
    "A.5.3": "The organization shall document the results of AI system impact assessments and retain results for a defined period.",
    "A.5.4": "The organization shall assess and document the potential impacts of AI systems to individuals or groups of individuals throughout the system's life cycle.",
    "A.5.5": "The organization shall assess and document the potential societal impacts of their AI systems throughout their life cycle.",
    "A.6.1.2": "The organization shall identify and document objectives to guide the responsible development AI systems, and take those objectives into account and integrate measures to achieve them in the development life cycle.",
    "A.6.1.3": "The organization shall define and document the specific processes for the responsible design and development of the AI system.",
    "A.6.2.2": "The organization shall specify and document requirements for new AI systems or material enhancements to existing systems.",
    "A.6.2.3": "The organization shall document the AI system design and development based on organizational objectives, documented requirements and specification criteria.",
    "A.6.2.4": "The organization shall define and document verification and validation measures for the AI system and specify criteria for their use.",
    "A.6.2.5": "The organization shall document a deployment plan and ensure that appropriate requirements are met prior to deployment.",
    "A.6.2.6": "The organization shall define and document the necessary elements for the ongoing operation of the AI system. At the minimum, this should include system and performance monitoring, repairs, updates and support.",
    "A.6.2.7": "The organization shall determine what AI system technical documentation is needed for each relevant category of interested parties, such as users, partners, supervisory authorities, and provide the technical documentation to them in the appropriate form.",
    "A.6.2.8": "The organization shall determine at which phases of the AI system life cycle, record keeping of event logs should be enabled, but at the minimum when the AI system is in use.",
    "A.7.2": "The organization shall define, document and implement data management processes related to the development of AI systems.",
    "A.7.3": "The organization shall determine and document details about the acquisition and selection of the data used in AI systems.",
    "A.7.4": "The organization shall define and document requirements for data quality and ensure that data used to develop and operate the AI system meet those requirements.",
    "A.7.5": "The organization shall define and document a process for recording the provenance of data used in its AI systems over the life cycles of the data and the AI system.",
    "A.7.6": "The organization shall define and document its criteria for selecting data preparations and the data preparation methods to be used.",
    "A.8.2": "The organization shall determine and provide the necessary information to users of the AI system.",
    "A.8.3": "The organization shall provide capabilities for interested parties to report adverse impacts of the AI system.",
    "A.8.4": "The organization shall determine and document a plan for communicating incidents to users of the AI system.",
    "A.8.5": "The organization shall determine and document their obligations to reporting information about the AI system to interested parties.",
    "A.9.2": "The organization shall define and document the processes for the responsible use of AI systems.",
    "A.9.3": "The organization shall identify and document objectives to guide the responsible use of AI systems.",
    "A.9.4": "The organization shall ensure that the AI system is used according to the intended uses of the AI system and its accompanying documentation.",
    "A.10.2": "The organization shall ensure that responsibilities within their AI system life cycle are allocated between the organization, its partners, suppliers, customers and third parties.",
    "A.10.3": "The organization shall establish a process to ensure that its usage of services, products or materials provided by suppliers aligns with the organization's approach to the responsible development and use of AI systems.",
    "A.10.4": "The organization shall ensure that its responsible approach to the development and use of AI systems considers their customer expectations and needs.",
}
