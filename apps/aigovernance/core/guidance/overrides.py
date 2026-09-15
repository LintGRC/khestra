"""Family-level assessment prompts for AI governance frameworks."""

FAMILY_PROMPTS = {
    "eu_ai_act": {
        "name": "EU AI Act",
        "overall_prompt": "The EU AI Act (Regulation 2024/1689) is the European Union's horizontal regulation for AI systems based on a risk-based approach. High-risk AI systems must comply with requirements for risk management, data governance, technical documentation, record-keeping, transparency, human oversight, accuracy, and cybersecurity.",
        "examine_prompt": "Review the following evidence for EU AI Act compliance: technical documentation, risk management records, data governance documentation, transparency disclosures, human oversight procedures, and conformity assessment records.",
        "interview_prompt": "Interview the compliance manager, system owner, and relevant personnel on how the organization demonstrates compliance with EU AI Act requirements for each high-risk AI system.",
        "test_prompt": "Test the compliance documentation for completeness against the applicable EU AI Act articles. Verify that risk management, data governance, technical documentation, record-keeping, transparency, human oversight, accuracy, and cybersecurity controls are implemented and operating effectively.",
    },
    "nist_ai_rmf": {
        "name": "NIST AI RMF",
        "overall_prompt": "The NIST AI Risk Management Framework (AI 100-1) provides a structured approach for managing AI risks across four functions: GOVERN (risk management culture), MAP (context and risk identification), MEASURE (risk assessment and impact evaluation), and MANAGE (risk treatment and response).",
        "examine_prompt": "Review governance documents, risk assessments, measurement results, and risk treatment plans. Verify the organization has established AI risk management policies, identified AI system risks, measured trustworthiness characteristics, and implemented appropriate risk treatments.",
        "interview_prompt": "Interview the AI governance lead, risk owners, and system developers on how the organization implements the NIST AI RMF functions: GOVERN, MAP, MEASURE, and MANAGE.",
        "test_prompt": "Test that AI risk management processes are documented and followed. Verify that risk identification covers the full AI system lifecycle, risk measurement includes appropriate metrics, and risk treatment plans are implemented and monitored.",
    },
    "iso_42001": {
        "name": "ISO 42001",
        "overall_prompt": "ISO 42001:2023 is the international standard for AI management systems following the ISO high-level structure (Annex SL). It specifies requirements for establishing, implementing, maintaining, and continually improving an AI management system within the context of the organization.",
        "examine_prompt": "Review AI management system documentation: scope statement, AI policy, risk assessment records, operational controls, internal audit reports, management review records, and corrective action records.",
        "interview_prompt": "Interview the AI management system manager, internal auditors, and process owners on how the AI management system is implemented, monitored, and improved.",
        "test_prompt": "Test the AI management system by following a sample process from policy through risk assessment through operational control through monitoring through corrective action. Verify the PDCA cycle is implemented.",
    },
}
