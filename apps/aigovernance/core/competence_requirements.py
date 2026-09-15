"""
Required competencies per role across EU AI Act, NIST AI RMF, and ISO 42001.
"""

REQUIRED_COMPETENCIES: dict[str, list[dict]] = {
    "provider": [
        {"qualification": "AI Act Fundamentals", "framework": "EU AI Act", "ref": "Art. 16", "description": "Understanding of provider obligations: conformity assessment, technical documentation, QMS"},
        {"qualification": "AI Literacy", "framework": "EU AI Act", "ref": "Art. 4", "description": "AI literacy to ensure staff understand system capabilities and limitations"},
        {"qualification": "Risk Management for AI", "framework": "EU AI Act", "ref": "Art. 9", "description": "Competence in AI risk management processes: identification, analysis, evaluation, mitigation"},
        {"qualification": "Technical Documentation (AI)", "framework": "EU AI Act", "ref": "Art. 11", "description": "Ability to prepare and maintain technical documentation per Annex IV"},
        {"qualification": "Quality Management for AI", "framework": "EU AI Act", "ref": "Art. 17", "description": "Competence in establishing and maintaining an AI QMS"},
        {"qualification": "AI Risk Management (NIST)", "framework": "NIST AI RMF", "ref": "GOVERN 1.1", "description": "Understanding of AI risk management framework, governance, and accountability structures"},
        {"qualification": "AI Auditing & Measurement", "framework": "NIST AI RMF", "ref": "MEASURE 3.1", "description": "Competence in AI system testing, measurement, and evaluation methodologies"},
        {"qualification": "AI AIMS Implementation", "framework": "ISO 42001", "ref": "5.1, 5.2", "description": "Understanding of AI management system implementation and continual improvement"},
        {"qualification": "AI System Lifecycle Management", "framework": "ISO 42001", "ref": "A.6", "description": "Competence in managing AI systems across their lifecycle: design, development, deployment, retirement"},
    ],
    "deployer": [
        {"qualification": "AI Act Fundamentals", "framework": "EU AI Act", "ref": "Art. 26", "description": "Understanding of deployer obligations: monitoring, human oversight, incident reporting"},
        {"qualification": "AI Literacy", "framework": "EU AI Act", "ref": "Art. 4", "description": "AI literacy to ensure competent use of AI systems in operational context"},
        {"qualification": "Human Oversight of AI", "framework": "EU AI Act", "ref": "Art. 14", "description": "Competence in implementing and exercising human oversight controls"},
        {"qualification": "AI Incident Response", "framework": "EU AI Act", "ref": "Art. 21, 73", "description": "Understanding of serious incident detection, reporting, and response procedures"},
        {"qualification": "Post-Market Monitoring", "framework": "EU AI Act", "ref": "Art. 61", "description": "Competence in establishing and operating post-market monitoring systems"},
        {"qualification": "AI Use Context Assessment", "framework": "NIST AI RMF", "ref": "MAP 2.1", "description": "Ability to assess the intended purpose, use context, and potential impact of AI systems"},
        {"qualification": "Third-Party AI Risk Management", "framework": "NIST AI RMF", "ref": "MAP 2.5", "description": "Competence in evaluating and monitoring third-party AI components and vendors"},
        {"qualification": "AI Operational Controls", "framework": "ISO 42001", "ref": "8.1, A.6", "description": "Understanding of operational planning, control measures, and monitoring for AI systems"},
        {"qualification": "AI Objectives & Performance", "framework": "ISO 42001", "ref": "6.2", "description": "Competence in setting AI objectives, performance indicators, and measurement methods"},
    ],
    "operator": [
        {"qualification": "AI Literacy", "framework": "EU AI Act", "ref": "Art. 4", "description": "AI literacy to understand system output interpretation and limitations"},
        {"qualification": "Human Oversight of AI", "framework": "EU AI Act", "ref": "Art. 14", "description": "Competence in exercising human oversight: override, stop, and intervention procedures"},
        {"qualification": "AI Incident Recognition", "framework": "EU AI Act", "ref": "Art. 73", "description": "Ability to recognize and report serious incidents and system malfunctions"},
        {"qualification": "AI System Operation (NIST)", "framework": "NIST AI RMF", "ref": "MANAGE 4.1", "description": "Understanding of operational procedures and incident response for AI systems"},
        {"qualification": "AI Operational Controls (ISO)", "framework": "ISO 42001", "ref": "8.1, A.6", "description": "Competence in day-to-day operation, monitoring, and control of AI systems"},
    ],
    "reviewer": [
        {"qualification": "AI Auditing & Conformity", "framework": "EU AI Act", "ref": "Art. 19, Annex VI", "description": "Understanding of conformity assessment procedures and declaration of conformity"},
        {"qualification": "AI Evaluation Methods", "framework": "EU AI Act", "ref": "Art. 15", "description": "Competence in evaluating accuracy, robustness, and cybersecurity of AI systems"},
        {"qualification": "AI Bias & Fairness Assessment", "framework": "NIST AI RMF", "ref": "MEASURE 3.2", "description": "Ability to assess bias, fairness, and trustworthiness of AI systems"},
        {"qualification": "AI Internal Audit (ISO)", "framework": "ISO 42001", "ref": "9.2", "description": "Competence in conducting internal audits of AI management systems"},
        {"qualification": "Management Review (ISO)", "framework": "ISO 42001", "ref": "9.3", "description": "Understanding of management review processes and performance evaluation"},
    ],
    "risk_owner": [
        {"qualification": "AI Risk Management (EU)", "framework": "EU AI Act", "ref": "Art. 9", "description": "Competence in AI risk management: risk identification, analysis, evaluation, and treatment"},
        {"qualification": "Fundamental Rights Impact Assessment", "framework": "EU AI Act", "ref": "Art. 27", "description": "Ability to conduct fundamental rights impact assessments for high-risk AI systems"},
        {"qualification": "AI Risk Management (NIST)", "framework": "NIST AI RMF", "ref": "GOVERN 2.4", "description": "Understanding of risk tolerance, risk appetite, and risk treatment decision-making"},
        {"qualification": "AI Risk Assessment (ISO)", "framework": "ISO 42001", "ref": "6.1, 8.2, 8.3", "description": "Competence in AI risk assessment, risk treatment planning, and residual risk evaluation"},
        {"qualification": "Continual Improvement (AI)", "framework": "ISO 42001", "ref": "10.1, 10.2", "description": "Understanding of corrective actions, nonconformity management, and continual improvement"},
    ],
    "provider_repr": [
        {"qualification": "AI Act Fundamentals", "framework": "EU AI Act", "ref": "Art. 23", "description": "Understanding of authorized representative obligations and regulatory communication"},
        {"qualification": "EU Database Management", "framework": "EU AI Act", "ref": "Art. 71", "description": "Competence in registering AI systems in the EU database and maintaining records"},
        {"qualification": "Regulatory Compliance (AI)", "framework": "EU AI Act", "ref": "Art. 22", "description": "Understanding of cooperation obligations with national competent authorities"},
    ],
}
