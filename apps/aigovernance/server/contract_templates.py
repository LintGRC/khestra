CONTRACT_TYPES = {
    "eu_ai_act": [
        "provider_agreements",
        "deployer_agreements",
        "authorized_representative",
        "third_party_licenses",
        "data_processing_agreements",
        "gpa_provider_terms",
    ],
    "nist_ai_rmf": [
        "vendor_contracts",
        "service_level_agreements",
        "data_sharing_agreements",
    ],
    "iso_42001": [
        "interested_party_agreements",
        "external_provider_contracts",
        "service_provider_slas",
        "data_sharing_processing",
    ],
}

CONTRACT_TEMPLATES = {
    "eu_ai_act": {

        "provider_agreements": {
            "name": "Provider Agreements (AI Systems)",
            "description": "Agreements between AI providers and deployers defining responsibilities, compliance obligations, and liability for high-risk AI systems under EU AI Act.",
            "guidance": "This agreement should cover: (1) identification of the provider and deployer roles per Art. 16-26, (2) allocation of conformity assessment responsibilities, (3) technical documentation access rights, (4) incident notification obligations, (5) post-market monitoring responsibilities, (6) liability and indemnification for AI-related harm, (7) term and termination provisions for non-compliance."
        },

        "deployer_agreements": {
            "name": "Deployer Agreements / Terms of Use",
            "description": "Terms of use for AI systems defining deployer obligations including human oversight, transparency notices, and usage restrictions per EU AI Act Art. 26-29.",
            "guidance": "This agreement should cover: (1) deployer's obligation to maintain human oversight per Art. 14, (2) transparency and disclosure requirements per Art. 13, (3) usage restrictions and prohibited practices per Art. 5, (4) record-keeping obligations per Art. 12, (5) data protection responsibilities, (6) deployer's obligation to conduct FRIA where required per Art. 27."
        },

        "authorized_representative": {
            "name": "Authorized Representative Appointment",
            "description": "Appointment of an authorized representative established in the EU by a non-EU AI provider, as required under EU AI Act Art. 16(3) and Art. 22.",
            "guidance": "This appointment should cover: (1) identification of the provider (non-EU) and authorized representative (EU-based), (2) mandate for the representative to act on behalf of the provider before EU authorities, (3) access to technical documentation and conformity assessment records, (4) cooperation with national supervisory authorities, (5) term and termination, (6) notification obligations when either party changes."
        },

        "third_party_licenses": {
            "name": "Third-Party AI Component Licenses",
            "description": "Licensing agreements for third-party AI components, pre-trained models, and AI libraries used within AI systems subject to EU AI Act requirements.",
            "guidance": "This agreement/license review should cover: (1) license type and usage rights for AI components, (2) compliance of third-party component with EU AI Act requirements, (3) access to training data documentation for licensed models, (4) liability for defects or non-compliance in third-party components, (5) update and maintenance commitments, (6) right to audit or verify compliance. For open-source components, document the specific license (MIT, Apache 2.0, etc.) and any restrictions on commercial use."
        },

        "data_processing_agreements": {
            "name": "Data Processing Agreements (AI Training)",
            "description": "Data processing agreements covering personal data used in AI training, fine-tuning, and inference, compliant with GDPR and EU AI Act data governance requirements per Art. 10.",
            "guidance": "This DPA should cover: (1) nature and purpose of data processing for AI training, (2) types of personal data processed, (3) data minimization and purpose limitation measures, (4) data retention and deletion schedules for training data, (5) compliance with Art. 10 data governance requirements, (6) technical and organizational measures for data protection, (7) data subject rights mechanisms, (8) sub-processing authorizations, (9) data breach notification procedures, (10) audit and inspection rights."
        },

        "gpa_provider_terms": {
            "name": "GPAI Provider Terms",
            "description": "Terms and conditions for providers of general-purpose AI (GPAI) models, covering transparency obligations, copyright policy, and systemic risk management per EU AI Act Art. 50-56.",
            "guidance": "This document should cover: (1) provider identity and contact information, (2) model capabilities and limitations disclosure, (3) transparency obligations per Art. 50 (technical documentation, training data summary), (4) copyright policy per Art. 53(1)(c), (5) systemic risk assessment and mitigation per Art. 51-55 for GPAI models with systemic risk, (6) codes of practice adherence per Art. 56, (7) incident reporting to AI Office per Art. 73, (8) authorized representative for non-EU providers."
        },
    },

    "nist_ai_rmf": {

        "vendor_contracts": {
            "name": "AI Vendor / Third-Party Contracts",
            "description": "Contracts with AI vendors and third-party providers, incorporating AI risk management requirements aligned with NIST AI RMF GOVERN and MAP functions.",
            "guidance": "This contract should cover: (1) vendor's AI risk management practices per NIST AI RMF, (2) transparency obligations for AI system capabilities and limitations, (3) testing and evaluation data access, (4) incident notification and response coordination, (5) data governance and protection requirements, (6) audit and inspection rights, (7) performance metrics and SLAs for AI system accuracy and reliability, (8) contractual remedies for AI-related failures or harms, (9) subcontracting restrictions, (10) compliance with applicable regulations."
        },

        "service_level_agreements": {
            "name": "AI Service Level Agreements",
            "description": "Service level agreements defining performance metrics, availability, accuracy targets, and remediation commitments for AI systems and AI-enabled services.",
            "guidance": "This SLA should cover: (1) AI system performance metrics (accuracy, latency, throughput), (2) availability and uptime commitments, (3) model update and retraining frequency, (4) accuracy degradation thresholds and remediation commitments, (5) incident response time commitments (TTD, TTR), (6) bias and fairness monitoring commitments, (7) reporting and dashboard access, (8) credits and remedies for SLA breaches, (9) periodic SLA review and adjustment process."
        },

        "data_sharing_agreements": {
            "name": "Data Sharing Agreements (AI)",
            "description": "Data sharing agreements for AI training data, validation data, and operational data between parties, addressing NIST AI RMF data governance and privacy considerations.",
            "guidance": "This agreement should cover: (1) types and categories of data shared, (2) permitted uses (training, validation, testing, monitoring), (3) data quality requirements (accuracy, completeness, timeliness), (4) data retention and deletion requirements, (5) confidentiality and data protection measures, (6) intellectual property rights in derived data and models, (7) restrictions on data use, (8) breach notification procedures, (9) liability for data-related incidents, (10) termination and data return/destruction provisions."
        },
    },

    "iso_42001": {

        "interested_party_agreements": {
            "name": "Interested Party Agreements",
            "description": "Agreements with interested parties (regulators, customers, affected persons) as required by ISO 42001 Clause 4.2, defining communication, consultation, and engagement processes for AI system impacts.",
            "guidance": "This agreement/communication framework should cover: (1) identification of interested parties per ISO 42001 Clause 4.2, (2) communication channels and frequency, (3) consultation mechanisms for AI system changes affecting interested parties, (4) transparency and disclosure commitments, (5) complaint and feedback mechanisms, (6) escalation procedures for unresolved concerns, (7) documentation and record-keeping requirements, (8) review and update intervals."
        },

        "external_provider_contracts": {
            "name": "External Provider Contracts (AI)",
            "description": "Contracts with external AI service providers and outsource partners, ensuring alignment with AI Management System (AIMS) requirements per ISO 42001 Clause 8.1 and Annex A controls.",
            "guidance": "This contract should cover: (1) scope of outsourced AI services and processes, (2) provider's compliance with AIMS policy and objectives, (3) operational controls for AI system development and operation, (4) risk assessment and treatment responsibilities, (5) competence requirements for provider personnel, (6) documented information access and retention, (7) performance monitoring and evaluation, (8) audit and inspection rights, (9) incident notification and response obligations, (10) nonconformity and corrective action processes."
        },

        "service_provider_slas": {
            "name": "AI Service Provider SLAs",
            "description": "Service level agreements for AI services defining quality, availability, performance, and support commitments aligned with ISO 42001 Clause 8.1 operational planning and control.",
            "guidance": "This SLA should cover: (1) AI service description and scope, (2) performance metrics aligned with AI objectives per Clause 6.2, (3) availability and reliability commitments, (4) model accuracy and performance targets, (5) data processing and handling standards, (6) incident response and resolution times, (7) change management procedures, (8) reporting and performance review cadence, (9) service credits and remedies, (10) termination and transition assistance provisions."
        },

        "data_sharing_processing": {
            "name": "Data Sharing & Processing Agreements (AI)",
            "description": "Data sharing and processing agreements for AI systems covering data quality, governance, and protection requirements per ISO 42001 Annex A controls.",
            "guidance": "This agreement should cover: (1) categories of data shared and processed, (2) data quality requirements (accuracy, completeness, consistency), (3) data governance controls per Annex A.7, (4) data protection and privacy measures, (5) data retention schedules and deletion procedures, (6) intellectual property in shared data and derived AI outputs, (7) restrictions on secondary use of data, (8) data breach notification and response, (9) compliance with applicable data protection regulations, (10) audit and verification rights."
        },
    },
}
