"""Conformity assessment routes — supports EU AI Act, NIST AI RMF, and ISO 42001."""

import os, json, sys
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
router = APIRouter()

def _load() -> dict:
    p = os.path.join(DATA_DIR, "conformity.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt conformity file {p}, returning empty", file=sys.stderr)
        return {}

def _save(data: dict):
    p = os.path.join(DATA_DIR, "conformity.json")
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)

def _id() -> str:
    return uuid4().hex[:12]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

FRAMEWORKS = {
    "eu_ai_act": {
        "label": "EU AI Act",
        "articles": [
            {"id": "5", "control_id": "EU-5", "title": "Prohibited AI Practices", "ref": "Art. 5", "category": "prohibited", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Prohibit AI practices that are unacceptable risk: social scoring, real-time biometric surveillance, manipulation, exploitation of vulnerabilities."},
            {"id": "ANNEX_III", "control_id": "EU-6", "title": "Classification Rules for High-Risk AI Systems", "ref": "Art. 6", "category": "classification", "tiers": ["high", "unacceptable"], "summary": "Determine if AI system falls into high-risk categories per Annex III: biometrics, critical infrastructure, education, employment, essential services, law enforcement, migration, justice."},
            {"id": "8", "control_id": "EU-8", "title": "Compliance with the Requirements", "ref": "Art. 8", "category": "requirements", "tiers": ["high", "unacceptable"], "summary": "High-risk AI systems must comply with the requirements of Chapter 2 (Arts 9-15), taking into account their intended purpose and the risk management system."},
            {"id": "9", "control_id": "EU-9", "title": "Risk Management System", "ref": "Art. 9", "category": "requirements", "tiers": ["high", "unacceptable"], "summary": "Establish, implement, maintain a risk management system throughout AI system lifecycle."},
            {"id": "10", "control_id": "EU-10", "title": "Data and Data Governance", "ref": "Art. 10", "category": "requirements", "tiers": ["high"], "summary": "Training, validation, and test data must meet quality, relevance, and bias criteria."},
            {"id": "11", "control_id": "EU-11", "title": "Technical Documentation", "ref": "Art. 11", "category": "requirements", "tiers": ["high"], "summary": "Draw up technical documentation before placing on market, updated throughout lifecycle."},
            {"id": "12", "control_id": "EU-12", "title": "Record-Keeping", "ref": "Art. 12", "category": "requirements", "tiers": ["high"], "summary": "Automatic logging of events during operation; logs retained for appropriate period."},
            {"id": "13", "control_id": "EU-13", "title": "Transparency and Provision of Information to Deployers", "ref": "Art. 13", "category": "requirements", "tiers": ["high", "limited"], "summary": "Provide deployers with clear information about capabilities, limitations, and intended purpose."},
            {"id": "14", "control_id": "EU-14", "title": "Human Oversight", "ref": "Art. 14", "category": "requirements", "tiers": ["high"], "summary": "Enable effective human oversight during use, including stop button and override."},
            {"id": "15", "control_id": "EU-15", "title": "Accuracy, Robustness and Cybersecurity", "ref": "Art. 15", "category": "requirements", "tiers": ["high"], "summary": "Achieve appropriate accuracy, robustness, and resilience to errors and attacks."},
            {"id": "16", "control_id": "EU-16", "title": "Obligations of Providers of High-Risk AI Systems", "ref": "Art. 16", "category": "provider", "tiers": ["high"], "summary": "Providers must comply with all obligations before placing on market."},
            {"id": "17", "control_id": "EU-17", "title": "Quality Management System", "ref": "Art. 17", "category": "provider", "tiers": ["high"], "summary": "Maintain a documented quality management system covering design, development, production, and post-market."},
            {"id": "18", "control_id": "EU-18", "title": "Documentation Keeping", "ref": "Art. 18", "category": "provider", "tiers": ["high"], "summary": "Retain technical documentation and automatically generated logs for 10 years after placing on market."},
            {"id": "19", "control_id": "EU-19", "title": "Automatically Generated Logs", "ref": "Art. 19", "category": "provider", "tiers": ["high"], "summary": "Providers shall keep automatically generated logs to document system operation throughout the lifetime."},
            {"id": "20", "control_id": "EU-20", "title": "Corrective Actions and Duty of Information", "ref": "Art. 20", "category": "provider", "tiers": ["high"], "summary": "Take corrective actions for non-compliant systems; inform authorities and, where applicable, deployers."},
            {"id": "21", "control_id": "EU-21", "title": "Cooperation with Competent Authorities", "ref": "Art. 21", "category": "provider", "tiers": ["high"], "summary": "Provide competent authorities with information and documentation necessary to demonstrate compliance."},
            {"id": "22", "control_id": "EU-22", "title": "Authorised Representatives of High-Risk AI Providers", "ref": "Art. 22", "category": "provider", "tiers": ["high"], "summary": "Non-EU providers must appoint an authorized representative established in the Union by written mandate."},
            {"id": "23", "control_id": "EU-23", "title": "Obligations of Importers", "ref": "Art. 23", "category": "provider", "tiers": ["high"], "summary": "Importers shall verify conformity assessment, CE marking, technical documentation, and instructions before placing on market."},
            {"id": "24", "control_id": "EU-24", "title": "Obligations of Distributors", "ref": "Art. 24", "category": "provider", "tiers": ["high"], "summary": "Distributors shall verify CE marking, EU declaration of conformity, and instructions for use before making a high-risk AI system available on the market."},
            {"id": "25", "control_id": "EU-25", "title": "Responsibilities along the AI Value Chain", "ref": "Art. 25", "category": "provider", "tiers": ["high"], "summary": "Any distributor, importer, deployer, or other third-party that puts their name or trademark on a high-risk AI system shall be considered a provider subject to all obligations."},
            {"id": "26", "control_id": "EU-26", "title": "Obligations of Deployers of High-Risk AI Systems", "ref": "Art. 26", "category": "deployer", "tiers": ["high"], "summary": "Deployers must use systems per instructions, ensure human oversight, monitor operation, and maintain logs."},
            {"id": "27", "control_id": "EU-27", "title": "Fundamental Rights Impact Assessment", "ref": "Art. 27", "category": "deployer", "tiers": ["high"], "summary": "Conduct a fundamental rights impact assessment before deploying high-risk AI systems, including mitigation measures."},
            {"id": "43", "control_id": "EU-43", "title": "Conformity Assessment", "ref": "Art. 43", "category": "requirements", "tiers": ["high"], "summary": "Carry out conformity assessment using internal control (Annex VI) or notified body (Annex VII) based on system type."},
            {"id": "46", "control_id": "EU-46", "title": "Derogation from Conformity Assessment Procedure", "ref": "Art. 46", "category": "provider", "tiers": ["high"], "summary": "By way of derogation from Article 43, a market surveillance authority may authorise, on duly justified request and for a limited period, the placing on the market of specific high-risk AI systems for exceptional reasons of public security, protection of life and health, environmental protection, or protection of key industrial and infrastructural assets."},
            {"id": "47", "control_id": "EU-47", "title": "EU Declaration of Conformity", "ref": "Art. 47", "category": "provider", "tiers": ["high"], "summary": "Providers must draw up an EU declaration of conformity for each high-risk AI system, keep it for 10 years, and make it available to authorities."},
            {"id": "48", "control_id": "EU-48", "title": "CE Marking", "ref": "Art. 48", "category": "provider", "tiers": ["high"], "summary": "The CE marking shall be affixed visibly, legibly, and indelibly to high-risk AI systems, subject to general principles of Regulation (EC) No 765/2008."},
            {"id": "49", "control_id": "EU-49", "title": "Registration", "ref": "Art. 49", "category": "provider", "tiers": ["high"], "summary": "Before placing on market, providers shall register themselves and each high-risk AI system in the EU database."},
            {"id": "50", "control_id": "EU-50", "title": "Transparency Obligations for Certain AI Systems", "ref": "Art. 50", "category": "limited", "tiers": ["limited"], "summary": "Disclose AI interaction, mark AI-generated content as machine-detectable, and ensure transparency for emotion recognition and biometric categorization."},
            {"id": "51", "control_id": "EU-51", "title": "Classification of GPAI Models with Systemic Risk", "ref": "Art. 51", "category": "gpai", "tiers": ["gpa"], "summary": "Classify a GPAI model as having systemic risk if it has high impact capabilities or equivalent impact based on Commission decision."},
            {"id": "52", "control_id": "EU-52", "title": "Procedure for Systemic Risk Designation", "ref": "Art. 52", "category": "gpai", "tiers": ["gpa"], "summary": "Notify the Commission within two weeks of meeting systemic risk threshold; Commission may also designate models ex officio."},
            {"id": "53", "control_id": "EU-53", "title": "Obligations for Providers of GPAI Models", "ref": "Art. 53", "category": "gpai", "tiers": ["gpa"], "summary": "Draw up technical documentation, provide downstream providers information, implement copyright policy, and publish training data summary."},
            {"id": "54", "control_id": "EU-54", "title": "Authorised Representatives of GPAI Providers", "ref": "Art. 54", "category": "gpai", "tiers": ["gpa"], "summary": "Non-EU GPAI providers must appoint an authorized representative in the Union by written mandate."},
            {"id": "55", "control_id": "EU-55", "title": "GPAI Providers with Systemic Risk Obligations", "ref": "Art. 55", "category": "gpai", "tiers": ["gpa"], "summary": "Providers of GPAI models with systemic risk must perform model evaluations, assess systemic risks, track incidents, and ensure cybersecurity protections."},
            {"id": "56", "control_id": "EU-56", "title": "Codes of Practice", "ref": "Art. 56", "category": "gpai", "tiers": ["gpa"], "summary": "GPAI providers may rely on codes of practice drawn up by the AI Office to demonstrate compliance with obligations under Articles 53 and 55."},
            {"id": "57", "control_id": "EU-57", "title": "AI Regulatory Sandboxes", "ref": "Art. 57", "category": "post_market", "tiers": ["high", "limited", "minimal", "gpa"], "summary": "Member States shall establish at least one AI regulatory sandbox enabling controlled testing and validation of innovative AI systems before placing on the market."},
            {"id": "60", "control_id": "EU-60", "title": "Real-World Testing Conditions for High-Risk AI", "ref": "Art. 60", "category": "post_market", "tiers": ["high"], "summary": "Real-world testing of high-risk AI systems outside sandboxes requires a testing plan, informed consent where applicable, and supervision by competent authorities."},
            {"id": "61", "control_id": "EU-61", "title": "Informed Consent for Real-World Testing", "ref": "Art. 61", "category": "post_market", "tiers": ["high"], "summary": "Obtain informed consent from subjects participating in real-world testing outside AI regulatory sandboxes."},
            {"id": "71", "control_id": "EU-71", "title": "EU Database for High-Risk AI Systems", "ref": "Art. 71", "category": "post_market", "tiers": ["high", "gpa"], "summary": "Set up and maintain an EU database containing information on high-risk AI systems registered under Articles 49 and 60."},
            {"id": "72", "control_id": "EU-72", "title": "Post-Market Monitoring", "ref": "Art. 72", "category": "post_market", "tiers": ["high"], "summary": "Establish a post-market monitoring system proportionate to the nature and risks of the high-risk AI system."},
            {"id": "73", "control_id": "EU-73", "title": "Reporting of Serious Incidents", "ref": "Art. 73", "category": "post_market", "tiers": ["high", "gpa"], "summary": "Providers shall report any serious incident to the market surveillance authorities of the Member State where it occurred."},
        ],
    },
    "nist_ai_rmf": {
        "label": "NIST AI RMF 1.0",
        "articles": [
            # NIST AI RMF 1.0 — 72 subcategories (verbatim from AI 100-1 Tables 1-4)
            {"id": "GOVERN 1.1", "control_id": "NIST-GOVERN-1.1", "title": "Legal and regulatory requirements involving AI are understood, managed, and documented.", "ref": "GOVERN 1.1", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Legal and regulatory requirements involving AI are understood, managed, and documented."},
            {"id": "GOVERN 1.2", "control_id": "NIST-GOVERN-1.2", "title": "The characteristics of trustworthy AI are integrated into organizational policies, processes, procedures, and practices.", "ref": "GOVERN 1.2", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The characteristics of trustworthy AI are integrated into organizational policies, processes, procedures, and practices."},
            {"id": "GOVERN 1.3", "control_id": "NIST-GOVERN-1.3", "title": "Processes, procedures, and practices are in place to determine the needed level of risk management activities based on the organization’s risk tolerance.", "ref": "GOVERN 1.3", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Processes, procedures, and practices are in place to determine the needed level of risk management activities based on the organization’s risk tolerance."},
            {"id": "GOVERN 1.4", "control_id": "NIST-GOVERN-1.4", "title": "The risk management process and its outcomes are established through transparent policies, procedures, and other controls based on organizational risk priorities.", "ref": "GOVERN 1.4", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The risk management process and its outcomes are established through transparent policies, procedures, and other controls based on organizational risk priorities."},
            {"id": "GOVERN 1.5", "control_id": "NIST-GOVERN-1.5", "title": "Ongoing monitoring and periodic review of the risk management process and its outcomes are planned and organizational roles and responsibilities clearly defined, including determining the frequency of periodic review.", "ref": "GOVERN 1.5", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Ongoing monitoring and periodic review of the risk management process and its outcomes are planned and organizational roles and responsibilities clearly defined, including determining the frequency of periodic review."},
            {"id": "GOVERN 1.6", "control_id": "NIST-GOVERN-1.6", "title": "Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities.", "ref": "GOVERN 1.6", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities."},
            {"id": "GOVERN 1.7", "control_id": "NIST-GOVERN-1.7", "title": "Processes and procedures are in place for decommissioning and phasing out AI systems safely and in a manner that does not increase risks or decrease the organization’s trustworthiness.", "ref": "GOVERN 1.7", "category": "GOVERN 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Processes and procedures are in place for decommissioning and phasing out AI systems safely and in a manner that does not increase risks or decrease the organization’s trustworthiness."},
            {"id": "GOVERN 2.1", "control_id": "NIST-GOVERN-2.1", "title": "Roles and responsibilities and lines of communication related to mapping, measuring, and managing AI risks are documented and are clear to individuals and teams throughout the organization.", "ref": "GOVERN 2.1", "category": "GOVERN 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Roles and responsibilities and lines of communication related to mapping, measuring, and managing AI risks are documented and are clear to individuals and teams throughout the organization."},
            {"id": "GOVERN 2.2", "control_id": "NIST-GOVERN-2.2", "title": "The organization’s personnel and partners receive AI risk management training to enable them to perform their duties and responsibilities consistent with related policies, procedures, and agreements.", "ref": "GOVERN 2.2", "category": "GOVERN 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization’s personnel and partners receive AI risk management training to enable them to perform their duties and responsibilities consistent with related policies, procedures, and agreements."},
            {"id": "GOVERN 2.3", "control_id": "NIST-GOVERN-2.3", "title": "Executive leadership of the organization takes responsibility for decisions about risks associated with AI system development and deployment.", "ref": "GOVERN 2.3", "category": "GOVERN 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Executive leadership of the organization takes responsibility for decisions about risks associated with AI system development and deployment."},
            {"id": "GOVERN 3.1", "control_id": "NIST-GOVERN-3.1", "title": "Decision-making related to mapping, measuring, and managing AI risks throughout the lifecycle is informed by a diverse team (e.g., diversity of demographics, disciplines, experience, expertise, and backgrounds).", "ref": "GOVERN 3.1", "category": "GOVERN 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Decision-making related to mapping, measuring, and managing AI risks throughout the lifecycle is informed by a diverse team (e.g., diversity of demographics, disciplines, experience, expertise, and backgrounds)."},
            {"id": "GOVERN 3.2", "control_id": "NIST-GOVERN-3.2", "title": "Policies and procedures are in place to define and differentiate roles and responsibilities for human-AI configurations and oversight of AI systems.", "ref": "GOVERN 3.2", "category": "GOVERN 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Policies and procedures are in place to define and differentiate roles and responsibilities for human-AI configurations and oversight of AI systems."},
            {"id": "GOVERN 4.1", "control_id": "NIST-GOVERN-4.1", "title": "Organizational policies and practices are in place to foster a critical thinking and safety-first mindset in the design, development, deployment, and uses of AI systems to minimize potential negative impacts.", "ref": "GOVERN 4.1", "category": "GOVERN 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Organizational policies and practices are in place to foster a critical thinking and safety-first mindset in the design, development, deployment, and uses of AI systems to minimize potential negative impacts."},
            {"id": "GOVERN 4.2", "control_id": "NIST-GOVERN-4.2", "title": "Organizational teams document the risks and potential impacts of the AI technology they design, develop, deploy, evaluate, and use, and they communicate about the impacts more broadly.", "ref": "GOVERN 4.2", "category": "GOVERN 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Organizational teams document the risks and potential impacts of the AI technology they design, develop, deploy, evaluate, and use, and they communicate about the impacts more broadly."},
            {"id": "GOVERN 4.3", "control_id": "NIST-GOVERN-4.3", "title": "Organizational practices are in place to enable AI testing, identification of incidents, and information sharing.", "ref": "GOVERN 4.3", "category": "GOVERN 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Organizational practices are in place to enable AI testing, identification of incidents, and information sharing."},
            {"id": "GOVERN 5.1", "control_id": "NIST-GOVERN-5.1", "title": "Organizational policies and practices are in place to collect, consider, prioritize, and integrate feedback from those external to the team that developed or deployed the AI system regarding the potential individual and societal impacts related to AI risks.", "ref": "GOVERN 5.1", "category": "GOVERN 5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Organizational policies and practices are in place to collect, consider, prioritize, and integrate feedback from those external to the team that developed or deployed the AI system regarding the potential individual and societal impacts related to AI risks."},
            {"id": "GOVERN 5.2", "control_id": "NIST-GOVERN-5.2", "title": "Mechanisms are established to enable the team that developed or deployed AI systems to regularly incorporate adjudicated feedback from relevant AI actors into system design and implementation.", "ref": "GOVERN 5.2", "category": "GOVERN 5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Mechanisms are established to enable the team that developed or deployed AI systems to regularly incorporate adjudicated feedback from relevant AI actors into system design and implementation."},
            {"id": "GOVERN 6.1", "control_id": "NIST-GOVERN-6.1", "title": "Policies and procedures are in place that address AI risks associated with third-party entities, including risks of infringement of a third-party’s intellectual property or other rights.", "ref": "GOVERN 6.1", "category": "GOVERN 6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Policies and procedures are in place that address AI risks associated with third-party entities, including risks of infringement of a third-party’s intellectual property or other rights."},
            {"id": "GOVERN 6.2", "control_id": "NIST-GOVERN-6.2", "title": "Contingency processes are in place to handle failures or incidents in third-party data or AI systems deemed to be high-risk.", "ref": "GOVERN 6.2", "category": "GOVERN 6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Contingency processes are in place to handle failures or incidents in third-party data or AI systems deemed to be high-risk."},
            {"id": "MANAGE 1.1", "control_id": "NIST-MANAGE-1.1", "title": "A determination is made as to whether the AI system achieves its intended purposes and stated objectives and whether its development or deployment should proceed.", "ref": "MANAGE 1.1", "category": "MANAGE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "A determination is made as to whether the AI system achieves its intended purposes and stated objectives and whether its development or deployment should proceed."},
            {"id": "MANAGE 1.2", "control_id": "NIST-MANAGE-1.2", "title": "Treatment of documented AI risks is prioritized based on impact, likelihood, and available resources or methods.", "ref": "MANAGE 1.2", "category": "MANAGE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Treatment of documented AI risks is prioritized based on impact, likelihood, and available resources or methods."},
            {"id": "MANAGE 1.3", "control_id": "NIST-MANAGE-1.3", "title": "Responses to the AI risks deemed high priority, as identified by the MAP function, are developed, planned, and documented. Risk response options can include mitigating, transferring, avoiding, or accepting.", "ref": "MANAGE 1.3", "category": "MANAGE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Responses to the AI risks deemed high priority, as identified by the MAP function, are developed, planned, and documented. Risk response options can include mitigating, transferring, avoiding, or accepting."},
            {"id": "MANAGE 1.4", "control_id": "NIST-MANAGE-1.4", "title": "Negative residual risks (defined as the sum of all unmitigated risks) to both downstream acquirers of AI systems and end users are documented.", "ref": "MANAGE 1.4", "category": "MANAGE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Negative residual risks (defined as the sum of all unmitigated risks) to both downstream acquirers of AI systems and end users are documented."},
            {"id": "MANAGE 2.1", "control_id": "NIST-MANAGE-2.1", "title": "Resources required to manage AI risks are taken into account – along with viable non-AI alternative systems, approaches, or methods – to reduce the magnitude or likelihood of potential impacts.", "ref": "MANAGE 2.1", "category": "MANAGE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Resources required to manage AI risks are taken into account – along with viable non-AI alternative systems, approaches, or methods – to reduce the magnitude or likelihood of potential impacts."},
            {"id": "MANAGE 2.2", "control_id": "NIST-MANAGE-2.2", "title": "Mechanisms are in place and applied to sustain the value of deployed AI systems.", "ref": "MANAGE 2.2", "category": "MANAGE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Mechanisms are in place and applied to sustain the value of deployed AI systems."},
            {"id": "MANAGE 2.3", "control_id": "NIST-MANAGE-2.3", "title": "Procedures are followed to respond to and recover from a previously unknown risk when it is identified.", "ref": "MANAGE 2.3", "category": "MANAGE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Procedures are followed to respond to and recover from a previously unknown risk when it is identified."},
            {"id": "MANAGE 2.4", "control_id": "NIST-MANAGE-2.4", "title": "Mechanisms are in place and applied, and responsibilities are assigned and understood, to supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use.", "ref": "MANAGE 2.4", "category": "MANAGE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Mechanisms are in place and applied, and responsibilities are assigned and understood, to supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use."},
            {"id": "MANAGE 3.1", "control_id": "NIST-MANAGE-3.1", "title": "AI risks and benefits from third-party resources are regularly monitored, and risk controls are applied and documented.", "ref": "MANAGE 3.1", "category": "MANAGE 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "AI risks and benefits from third-party resources are regularly monitored, and risk controls are applied and documented."},
            {"id": "MANAGE 3.2", "control_id": "NIST-MANAGE-3.2", "title": "Pre-trained models which are used for development are monitored as part of AI system regular monitoring and maintenance.", "ref": "MANAGE 3.2", "category": "MANAGE 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Pre-trained models which are used for development are monitored as part of AI system regular monitoring and maintenance."},
            {"id": "MANAGE 4.1", "control_id": "NIST-MANAGE-4.1", "title": "Post-deployment AI system monitoring plans are implemented, including mechanisms for capturing and evaluating input from users and other relevant AI actors, appeal and override, decommissioning, incident response, recovery, and change management.", "ref": "MANAGE 4.1", "category": "MANAGE 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Post-deployment AI system monitoring plans are implemented, including mechanisms for capturing and evaluating input from users and other relevant AI actors, appeal and override, decommissioning, incident response, recovery, and change management."},
            {"id": "MANAGE 4.2", "control_id": "NIST-MANAGE-4.2", "title": "Measurable activities for continual improvements are integrated into AI system updates and include regular engagement with interested parties, including relevant AI actors.", "ref": "MANAGE 4.2", "category": "MANAGE 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Measurable activities for continual improvements are integrated into AI system updates and include regular engagement with interested parties, including relevant AI actors."},
            {"id": "MANAGE 4.3", "control_id": "NIST-MANAGE-4.3", "title": "Incidents and errors are communicated to relevant AI actors, including affected communities. Processes for tracking, responding to, and recovering from incidents and errors are followed and documented.", "ref": "MANAGE 4.3", "category": "MANAGE 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Incidents and errors are communicated to relevant AI actors, including affected communities. Processes for tracking, responding to, and recovering from incidents and errors are followed and documented."},
            {"id": "MAP 1.1", "control_id": "NIST-MAP-1.1", "title": "Intended purposes, potentially beneficial uses, context- specific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented. Considerations include: the specific set or types of users along with their expectations; potential positive and negative impacts of system uses to individuals, communities, organizations, society, and the planet; assumptions and related limitations about AI system purposes, uses, and risks across the development or product AI lifecycle; and related TEVV and system metrics.", "ref": "MAP 1.1", "category": "MAP 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Intended purposes, potentially beneficial uses, context- specific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented. Considerations include: the specific set or types of users along with their expectations; potential positive and negative impacts of system uses to individuals, communities, organizations, society, and the planet; assumptions and related limitations about AI system purposes, uses, and risks across the development or product AI lifecycle; and related TEVV and system metrics."},
            {"id": "MAP 1.2", "control_id": "NIST-MAP-1.2", "title": "Interdisciplinary AI actors, competencies, skills, and capacities for establishing context reflect demographic diversity and broad domain and user experience expertise, and their participation is documented. Opportunities for interdisciplinary collaboration are prioritized.", "ref": "MAP 1.2", "category": "MAP 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Interdisciplinary AI actors, competencies, skills, and capacities for establishing context reflect demographic diversity and broad domain and user experience expertise, and their participation is documented. Opportunities for interdisciplinary collaboration are prioritized."},
            {"id": "MAP 1.3", "control_id": "NIST-MAP-1.3", "title": "The organization’s mission and relevant goals for AI technology are understood and documented.", "ref": "MAP 1.3", "category": "MAP 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization’s mission and relevant goals for AI technology are understood and documented."},
            {"id": "MAP 1.4", "control_id": "NIST-MAP-1.4", "title": "The business value or context of business use has been clearly defined or – in the case of assessing existing AI systems – re-evaluated.", "ref": "MAP 1.4", "category": "MAP 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The business value or context of business use has been clearly defined or – in the case of assessing existing AI systems – re-evaluated."},
            {"id": "MAP 1.5", "control_id": "NIST-MAP-1.5", "title": "Organizational risk tolerances are determined and documented.", "ref": "MAP 1.5", "category": "MAP 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Organizational risk tolerances are determined and documented."},
            {"id": "MAP 1.6", "control_id": "NIST-MAP-1.6", "title": "System requirements (e.g., “the system shall respect the privacy of its users”) are elicited from and understood by relevant AI actors. Design decisions take socio-technical implications into account to address AI risks.", "ref": "MAP 1.6", "category": "MAP 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "System requirements (e.g., “the system shall respect the privacy of its users”) are elicited from and understood by relevant AI actors. Design decisions take socio-technical implications into account to address AI risks."},
            {"id": "MAP 2.1", "control_id": "NIST-MAP-2.1", "title": "The specific tasks and methods used to implement the tasks that the AI system will support are defined (e.g., classifiers, generative models, recommenders).", "ref": "MAP 2.1", "category": "MAP 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The specific tasks and methods used to implement the tasks that the AI system will support are defined (e.g., classifiers, generative models, recommenders)."},
            {"id": "MAP 2.2", "control_id": "NIST-MAP-2.2", "title": "Information about the AI system’s knowledge limits and how system output may be utilized and overseen by humans is documented. Documentation provides sufficient information to assist relevant AI actors when making decisions and taking subsequent actions.", "ref": "MAP 2.2", "category": "MAP 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Information about the AI system’s knowledge limits and how system output may be utilized and overseen by humans is documented. Documentation provides sufficient information to assist relevant AI actors when making decisions and taking subsequent actions."},
            {"id": "MAP 2.3", "control_id": "NIST-MAP-2.3", "title": "Scientific integrity and TEVV considerations are identified and documented, including those related to experimental design, data collection and selection (e.g., availability, representativeness, suitability), system trustworthiness, and construct validation.", "ref": "MAP 2.3", "category": "MAP 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Scientific integrity and TEVV considerations are identified and documented, including those related to experimental design, data collection and selection (e.g., availability, representativeness, suitability), system trustworthiness, and construct validation."},
            {"id": "MAP 3.1", "control_id": "NIST-MAP-3.1", "title": "Potential benefits of intended AI system functionality and performance are examined and documented.", "ref": "MAP 3.1", "category": "MAP 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Potential benefits of intended AI system functionality and performance are examined and documented."},
            {"id": "MAP 3.2", "control_id": "NIST-MAP-3.2", "title": "Potential costs, including non-monetary costs, which result from expected or realized AI errors or system functionality and trustworthiness – as connected to organizational risk tolerance – are examined and documented.", "ref": "MAP 3.2", "category": "MAP 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Potential costs, including non-monetary costs, which result from expected or realized AI errors or system functionality and trustworthiness – as connected to organizational risk tolerance – are examined and documented."},
            {"id": "MAP 3.3", "control_id": "NIST-MAP-3.3", "title": "Targeted application scope is specified and documented based on the system’s capability, established context, and AI system categorization.", "ref": "MAP 3.3", "category": "MAP 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Targeted application scope is specified and documented based on the system’s capability, established context, and AI system categorization."},
            {"id": "MAP 3.4", "control_id": "NIST-MAP-3.4", "title": "Processes for operator and practitioner proficiency with AI system performance and trustworthiness – and relevant technical standards and certifications – are defined, assessed, and documented.", "ref": "MAP 3.4", "category": "MAP 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Processes for operator and practitioner proficiency with AI system performance and trustworthiness – and relevant technical standards and certifications – are defined, assessed, and documented."},
            {"id": "MAP 3.5", "control_id": "NIST-MAP-3.5", "title": "Processes for human oversight are defined, assessed, and documented in accordance with organizational policies from the GOVERN function.", "ref": "MAP 3.5", "category": "MAP 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Processes for human oversight are defined, assessed, and documented in accordance with organizational policies from the GOVERN function."},
            {"id": "MAP 4.1", "control_id": "NIST-MAP-4.1", "title": "Approaches for mapping AI technology and legal risks of its components – including the use of third-party data or software – are in place, followed, and documented, as are risks of infringement of a third party’s intellectual property or other rights.", "ref": "MAP 4.1", "category": "MAP 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Approaches for mapping AI technology and legal risks of its components – including the use of third-party data or software – are in place, followed, and documented, as are risks of infringement of a third party’s intellectual property or other rights."},
            {"id": "MAP 4.2", "control_id": "NIST-MAP-4.2", "title": "Internal risk controls for components of the AI system, including third-party AI technologies, are identified and documented.", "ref": "MAP 4.2", "category": "MAP 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Internal risk controls for components of the AI system, including third-party AI technologies, are identified and documented."},
            {"id": "MAP 5.1", "control_id": "NIST-MAP-5.1", "title": "Likelihood and magnitude of each identified impact (both potentially beneficial and harmful) based on expected use, past uses of AI systems in similar contexts, public incident reports, feedback from those external to the team that developed or deployed the AI system, or other data are identified and documented.", "ref": "MAP 5.1", "category": "MAP 5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Likelihood and magnitude of each identified impact (both potentially beneficial and harmful) based on expected use, past uses of AI systems in similar contexts, public incident reports, feedback from those external to the team that developed or deployed the AI system, or other data are identified and documented."},
            {"id": "MAP 5.2", "control_id": "NIST-MAP-5.2", "title": "Practices and personnel for supporting regular engagement with relevant AI actors and integrating feedback about positive, negative, and unanticipated impacts are in place and documented.", "ref": "MAP 5.2", "category": "MAP 5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Practices and personnel for supporting regular engagement with relevant AI actors and integrating feedback about positive, negative, and unanticipated impacts are in place and documented."},
            {"id": "MEASURE 1.1", "control_id": "NIST-MEASURE-1.1", "title": "Approaches and metrics for measurement of AI risks enumerated during the MAP function are selected for implementation starting with the most significant AI risks. The risks or trustworthiness characteristics that will not – or cannot – be measured are properly documented.", "ref": "MEASURE 1.1", "category": "MEASURE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Approaches and metrics for measurement of AI risks enumerated during the MAP function are selected for implementation starting with the most significant AI risks. The risks or trustworthiness characteristics that will not – or cannot – be measured are properly documented."},
            {"id": "MEASURE 1.2", "control_id": "NIST-MEASURE-1.2", "title": "Appropriateness of AI metrics and effectiveness of existing controls are regularly assessed and updated, including reports of errors and potential impacts on affected communities.", "ref": "MEASURE 1.2", "category": "MEASURE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Appropriateness of AI metrics and effectiveness of existing controls are regularly assessed and updated, including reports of errors and potential impacts on affected communities."},
            {"id": "MEASURE 1.3", "control_id": "NIST-MEASURE-1.3", "title": "Internal experts who did not serve as front-line developers for the system and/or independent assessors are involved in regular assessments and updates. Domain experts, users, AI actors external to the team that developed or deployed the AI system, and affected communities are consulted in support of assessments as necessary per organizational risk tolerance.", "ref": "MEASURE 1.3", "category": "MEASURE 1", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Internal experts who did not serve as front-line developers for the system and/or independent assessors are involved in regular assessments and updates. Domain experts, users, AI actors external to the team that developed or deployed the AI system, and affected communities are consulted in support of assessments as necessary per organizational risk tolerance."},
            {"id": "MEASURE 2.1", "control_id": "NIST-MEASURE-2.1", "title": "Test sets, metrics, and details about the tools used during TEVV are documented.", "ref": "MEASURE 2.1", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Test sets, metrics, and details about the tools used during TEVV are documented."},
            {"id": "MEASURE 2.2", "control_id": "NIST-MEASURE-2.2", "title": "Evaluations involving human subjects meet applicable requirements (including human subject protection) and are representative of the relevant population.", "ref": "MEASURE 2.2", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Evaluations involving human subjects meet applicable requirements (including human subject protection) and are representative of the relevant population."},
            {"id": "MEASURE 2.3", "control_id": "NIST-MEASURE-2.3", "title": "AI system performance or assurance criteria are measured qualitatively or quantitatively and demonstrated for conditions similar to deployment setting(s). Measures are documented.", "ref": "MEASURE 2.3", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "AI system performance or assurance criteria are measured qualitatively or quantitatively and demonstrated for conditions similar to deployment setting(s). Measures are documented."},
            {"id": "MEASURE 2.4", "control_id": "NIST-MEASURE-2.4", "title": "The functionality and behavior of the AI system and its components – as identified in the MAP function – are onitored when in production.", "ref": "MEASURE 2.4", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The functionality and behavior of the AI system and its components – as identified in the MAP function – are onitored when in production."},
            {"id": "MEASURE 2.5", "control_id": "NIST-MEASURE-2.5", "title": "The AI system to be deployed is demonstrated to be valid and reliable. Limitations of the generalizability beyond the conditions under which the technology was developed are documented.", "ref": "MEASURE 2.5", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The AI system to be deployed is demonstrated to be valid and reliable. Limitations of the generalizability beyond the conditions under which the technology was developed are documented."},
            {"id": "MEASURE 2.6", "control_id": "NIST-MEASURE-2.6", "title": "The AI system is evaluated regularly for safety risks – as identified in the MAP function. The AI system to be deployed is demonstrated to be safe, its residual negative risk does not exceed the risk tolerance, and it can fail safely, particularly if made to operate beyond its knowledge limits. Safety metrics reflect system reliability and robustness, real-time monitoring, and response times for AI system failures.", "ref": "MEASURE 2.6", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The AI system is evaluated regularly for safety risks – as identified in the MAP function. The AI system to be deployed is demonstrated to be safe, its residual negative risk does not exceed the risk tolerance, and it can fail safely, particularly if made to operate beyond its knowledge limits. Safety metrics reflect system reliability and robustness, real-time monitoring, and response times for AI system failures."},
            {"id": "MEASURE 2.7", "control_id": "NIST-MEASURE-2.7", "title": "AI system security and resilience – as identified in the MAP function – are evaluated and documented.", "ref": "MEASURE 2.7", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "AI system security and resilience – as identified in the MAP function – are evaluated and documented."},
            {"id": "MEASURE 2.8", "control_id": "NIST-MEASURE-2.8", "title": "Risks associated with transparency and accountability – as identified in the MAP function – are examined and documented.", "ref": "MEASURE 2.8", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Risks associated with transparency and accountability – as identified in the MAP function – are examined and documented."},
            {"id": "MEASURE 2.9", "control_id": "NIST-MEASURE-2.9", "title": "The AI model is explained, validated, and documented, and AI system output is interpreted within its context – as identified in the MAP function – to inform responsible use and governance.", "ref": "MEASURE 2.9", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The AI model is explained, validated, and documented, and AI system output is interpreted within its context – as identified in the MAP function – to inform responsible use and governance."},
            {"id": "MEASURE 2.10", "control_id": "NIST-MEASURE-2.10", "title": "Privacy risk of the AI system – as identified in the MAP function – is examined and documented.", "ref": "MEASURE 2.10", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Privacy risk of the AI system – as identified in the MAP function – is examined and documented."},
            {"id": "MEASURE 2.11", "control_id": "NIST-MEASURE-2.11", "title": "Fairness and bias – as identified in the MAP function – are evaluated and results are documented.", "ref": "MEASURE 2.11", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Fairness and bias – as identified in the MAP function – are evaluated and results are documented."},
            {"id": "MEASURE 2.12", "control_id": "NIST-MEASURE-2.12", "title": "Environmental impact and sustainability of AI model training and management activities – as identified in the MAP function – are assessed and documented.", "ref": "MEASURE 2.12", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Environmental impact and sustainability of AI model training and management activities – as identified in the MAP function – are assessed and documented."},
            {"id": "MEASURE 2.13", "control_id": "NIST-MEASURE-2.13", "title": "Effectiveness of the employed TEVV metrics and processes in the MEASURE function are evaluated and documented.", "ref": "MEASURE 2.13", "category": "MEASURE 2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Effectiveness of the employed TEVV metrics and processes in the MEASURE function are evaluated and documented."},
            {"id": "MEASURE 3.1", "control_id": "NIST-MEASURE-3.1", "title": "Approaches, personnel, and documentation are in place to regularly identify and track existing, unanticipated, and emergent AI risks based on factors such as intended and actual performance in deployed contexts.", "ref": "MEASURE 3.1", "category": "MEASURE 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Approaches, personnel, and documentation are in place to regularly identify and track existing, unanticipated, and emergent AI risks based on factors such as intended and actual performance in deployed contexts."},
            {"id": "MEASURE 3.2", "control_id": "NIST-MEASURE-3.2", "title": "Risk tracking approaches are considered for settings where AI risks are difficult to assess using currently available measurement techniques or where metrics are not yet available.", "ref": "MEASURE 3.2", "category": "MEASURE 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Risk tracking approaches are considered for settings where AI risks are difficult to assess using currently available measurement techniques or where metrics are not yet available."},
            {"id": "MEASURE 3.3", "control_id": "NIST-MEASURE-3.3", "title": "Feedback processes for end users and impacted communities to report problems and appeal system outcomes are established and integrated into AI system evaluation metrics.", "ref": "MEASURE 3.3", "category": "MEASURE 3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Feedback processes for end users and impacted communities to report problems and appeal system outcomes are established and integrated into AI system evaluation metrics."},
            {"id": "MEASURE 4.1", "control_id": "NIST-MEASURE-4.1", "title": "Measurement approaches for identifying AI risks are connected to deployment context(s) and informed through consultation with domain experts and other end users. Approaches are documented.", "ref": "MEASURE 4.1", "category": "MEASURE 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Measurement approaches for identifying AI risks are connected to deployment context(s) and informed through consultation with domain experts and other end users. Approaches are documented."},
            {"id": "MEASURE 4.2", "control_id": "NIST-MEASURE-4.2", "title": "Measurement results regarding AI system trustworthiness in deployment context(s) and across the AI lifecycle are informed by input from domain experts and relevant AI actors to validate whether the system is performing consistently as intended. Results are documented.", "ref": "MEASURE 4.2", "category": "MEASURE 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Measurement results regarding AI system trustworthiness in deployment context(s) and across the AI lifecycle are informed by input from domain experts and relevant AI actors to validate whether the system is performing consistently as intended. Results are documented."},
            {"id": "MEASURE 4.3", "control_id": "NIST-MEASURE-4.3", "title": "Measurable performance improvements or declines based on consultations with relevant AI actors, including affected communities, and field data about context-relevant risks and trustworthiness characteristics are identified and documented.", "ref": "MEASURE 4.3", "category": "MEASURE 4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Measurable performance improvements or declines based on consultations with relevant AI actors, including affected communities, and field data about context-relevant risks and trustworthiness characteristics are identified and documented."},
        ],
    },
    "owasp_agentic": {
        "label": "OWASP Agentic AI Top 10 (2026)",
        "articles": [
            # OWASP Top 10 for Agentic Applications 2026 — 10 risks (official document)
            {"id": "ASI01", "control_id": "OWASP-1", "title": "Agent Goal Hijack", "ref": "ASI01", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "AI Agents exhibit autonomous ability to execute a series of tasks to achieve a goal. Due to inherent weaknesses in how natural-language instructions and related content are processed, agents and the underlying model cannot reliably distinguish instructions from related content. As a result, attackers can manipulate an agent’s objectives, task selection, or decision pathways through a variety of techniques - including, but not limited to, prompt-based manipulation, deceptive tool outputs, malicious artefacts, forged agent-to-agent messages, or poisoned external data. Because agents rely on untyped natural-language inputs and loosely governed orchestration logic, they cannot reliably distinguish legitimate instructions from attacker-controlled content. Unlike LLM01:2025, which focuses on altering a single model response, ASI01 captures the broader agentic impact where manipulated inputs redirect goals, planning (when used) and multi-step behavior. Agent Goal Hijack differs from ASI06 (Memory & Context Poisoning) and ASI10 (Rogue Agents) because the attacker directly alters the agent’s goals, instructions, or decision pathways - regardless of whether the manipulation occurs interactively or through pre-positioned inputs such as documents, templates, or external data sources. ASI06 focuses on the persistent corruption of stored context or long-term memory, while ASI10 captures autonomous misalignment that emerges without active attacker control. In the OWASP Agentic AI Threats & Mitigations Guide, ASI01 corresponds to T06 Goal Manipulation (altering the agent’s objectives) and T07 Misaligned & Deceptive Behaviors (bypassing safeguards or deceiving humans). Together, these illustrate how attackers can subvert the agent’s objectives and action-selection logic, redirecting its autonomy toward unintended or harmful outcomes."},
            {"id": "ASI02", "control_id": "OWASP-2", "title": "Tool Misuse and Exploitation", "ref": "ASI02", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Agents can misuse legitimate tools due to prompt injection, misalignment, or unsafe delegation or ambiguous instruction - leading to data exfiltration, tool output manipulation or workflow hijacking. Risks arise from how the agent chooses and applies tools; agent memory, dynamic tool selection, and delegation can contribute to misuse via chaining, privilege escalation, and unintended actions. This relates to LLM06:2025 (Excessive Agency), which addresses excessive autonomy but focuses on the misuse of legitimate tools. This entry covers cases where the agent operates within its authorized privileges but applies a legitimate tool in an unsafe or unintended way - for example deleting valuable data, over-invoking costly APIs, or exfiltrating information. If the misuse involves privilege escalation or credential inheritance, it falls under ASI03 (Identity & Privilege Abuse); if the misuse results in arbitrary or injected code execution, it is classified under ASI05 (Unexpected Code Execution). Finally, tool definitions increasingly come via MCP servers, creating a natural overlap with ASI04 (Agentic Supply Chain Vulnerabilities). The entry maps to T2 Tool Misuse in the Agentic AI Threats and Mitigations Guide whilst T4 Resource Overload and T16 Insecure Inter-Agent Protocol Abuse represent contributing factors that can amplify or enable tool exploitation. The entry aligns with AIVSS Core Risk: Agentic AI Tool Misuse."},
            {"id": "ASI03", "control_id": "OWASP-3", "title": "Identity and Privilege Abuse", "ref": "ASI03", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Identity & Privilege Abuse exploits dynamic trust and delegation in agents to escalate access and bypass controls by manipulating delegation chains, role inheritance, control flows, and agent context; context includes cached credentials or conversation history across interconnected systems. In this context, identity refers both to the agent’s defined persona and to any authentication material that represents it. Agent-to- agent trust or inherited credentials can be exploited to escalate access, hijack privileges, or execute unauthorized actions. This risk arises from the architectural mismatch between user-centric identity systems and agentic design. Without a distinct, governed identity of its own, an agent operates in an attribution gap that makes enforcing true least privilege impossible. Identity in this context includes both the agent’s assigned persona and any authentication material (API keys, OAuth tokens, delegated user sessions) that represent it. This differs from ASI02 (Tools Misuse) which is an unintended or unsafe use of already granted privilege by a principal misusing its own tools. Identity & Privilege Abuse is the agentic evolution of Excessive Agency (LLM06:2025). It often leverages Prompt Injection (LLM01:2025), and because of agent permissions, tool integrations, and multi-agent systems, the impact can amplify and exceed Sensitive Information Disclosure (LLM02:2025) to directly compromise the confidentiality, integrity, and availability of systems and data the agent can reach. In the OWASP ASI Threats and Mitigations, it maps one-to-one to T3: Privilege Compromise, and in OWASP AIVSS it corresponds to Core Risk 2: Agent Access Control Violation."},
            {"id": "ASI04", "control_id": "OWASP-4", "title": "Agentic Supply Chain Vulnerabilities", "ref": "ASI04", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Agentic Supply Chain Vulnerabilities arise when agents, tools, and related artefacts they work with are provided by third parties and may be malicious, compromised, or tampered with in transit. These can be both static and dynamicallyly sourced components, including models and model weights, tools, plug-ins, datasets, other agents, agentic interfaces - MCP (Model Context Protocol), A2A (Agent2Agent) - agentic registries and related artifacts, or update channels. These dependencies may introduce unsafe code, hidden instructions, or deceptive behaviors into the agent’s execution chain. Supply chain is covered in depth in LLM03:2025 Supply Chain Vulnerabilities. However, its focus is on static dependencies. Unlike traditional AI or software supply chains, agentic ecosystems often compose capabilities at runtime - loading external tools and agent personas dynamically – thereby increasing the attack surface. This distributed run-time coordination - combined with agentic autonomy - creates a live supply chain that can cascade vulnerabilities across agents. These shifts focus from manifest to run-time security of a diverse and often opaque component. Tackling this problem requires careful development-time tooling and runtime orchestration, where components are dynamically loaded, shared, and trusted. The entry maps to T17 Supply Chain Compromise in Agentic Threats and Mitigations and across T2 Tool Misuse, T11 Unexpected RCE and Code Attacks, T12 Agent Communication Poisoning, T13 Rogue Agent and T16 Insecure Inter-Agent Protocol Abuse."},
            {"id": "ASI05", "control_id": "OWASP-5", "title": "Unexpected Code Execution (RCE)", "ref": "ASI05", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Agentic systems - including popular vibe coding tools - often generate and execute code. Attackers exploit code-generation features or embedded tool access to escalate actions into remote code execution (RCE), local misuse, or exploitation of internal systems. Because this code is often generated in real-time by the agent it can bypass traditional security controls. Prompt injection, tool misuse, or unsafe serialization can convert text into unintended executable behavior. While code execution can be triggered via the same tool interfaces discussed under ASI02, ASI05 focuses on unexpected or adversarial execution of code (scripts, binaries, JIT/WASM modules, deserialized objects, template engines, in memory evaluations) that leads to host or container compromise, persistence, or sandbox escape - outcomes that require host and runtime-specific mitigations beyond ordinary tool-use controls. This entry builds on LLM01:2025 Prompt Injection and LLM05:2025 Improper Output Handling, reflecting their evolution in agentic systems from a single manipulated output interpreted or executed to orchestrated multi-tool chains that achieve execution through a sequence of otherwise legitimate tool calls. This risk aligns with T11 Unexpected RCE and Code Attacks in Agentic AI – Threats and Mitigations v1.1."},
            {"id": "ASI06", "control_id": "OWASP-6", "title": "Memory & Context Poisoning", "ref": "ASI06", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Agentic systems rely on stored and retrievable information which can be a snapshot of its conversation history, a memory tool or expanded context, which supports continuity across tasks and reasoning cycles. Context includes any information an agent retains, retrieves, or reuses, such as summaries, embeddings, and RAG stores but excludes one-time input prompts covered under LLM01:2025 Prompt Injection. In Memory and Context Poisoning, adversaries corrupt or seed this context with malicious or misleading data, causing future reasoning, planning, or tool use to become biased, unsafe, or aid exfiltration. Ingestion sources such as uploads, API feeds, user input, or peer-agent exchanges may be untrusted or only partially validated. This risk is distinct from ASI01 (Goal Hijack), which captures direct goal manipulation, and ASI08 (Cascading Failures), which describes degradation after poisoning occurs. However, memory poisoning frequently leads to goal hijacking (ASI01), as corrupted context or long-term memory can alter the agent’s goal interpretation, reasoning path, or tool-selection logic. It builds on LLM01:2025 Prompt Injection, LLM04:2025 Data and Model Poisoning, and LLM08:2025 Vector and Embedding Weaknesses, but focuses on persistent corruption of agent memory and retrievable context that propagates across sessions and alters autonomous reasoning. It maps to T1 Memory Poisoning in Agentic Threats and Mitigations, with related impacts in T4 Memory Overload, T6 Broken Goals, and T12 Shared Memory Poisoning. In AIVSS, the AARS fields Memory Use and Contextual Awareness raise the agentic vulnerability score."},
            {"id": "ASI07", "control_id": "OWASP-7", "title": "Insecure Inter-Agent Communication", "ref": "ASI07", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Multi agent systems depend on continuous communication between autonomous agents that coordinate via APIs, message buses, and shared memory, significantly expanding the attack surface. Decentralized architecture, varying autonomy, and uneven trust make perimeter-based security models ineffective. Weak inter-agent controls for authentication, integrity, confidentiality, or authorization let attackers intercept, manipulate, spoof, or block messages. Insecure Inter-Agent Communication occurs when these exchanges lack proper authentication, integrity, or semantic validation, allowing interception, spoofing, or manipulation of agent messages and intents. The threat spans transport, routing, discovery, and semantic layers, including covert or side-channels where agents leak or infer data through timing or behavioral cues. This differs from ASI03 (Identity & Privilege Abuse), which focuses on credential and permissions misuse, and ASI06 (Memory & Context Poisoning), which targets stored knowledge corruption. ASI07 focuses on compromising real-time messages between agents, leading to misinformation, privilege confusion, or coordinated manipulation across distributed agentic systems. The entry is covered by T12 – Agent Communication Poisoning & T16 – Insecure Inter-Agent Protocol Abuse in Agentic Threats and Mitigations"},
            {"id": "ASI08", "control_id": "OWASP-8", "title": "Cascading Failures", "ref": "ASI08", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Agentic cascading failures occur when a single fault (hallucination, malicious input, corrupted tool, or poisoned memory) propagates across autonomous agents, compounding into system-wide harm. Because agents plan, persist, and delegate autonomously, a single error can bypass stepwise human checks and persist in a saved state. As agents form emergent links to new tools or peers, these latent faults chain into privileged operations that compromise confidentiality, integrity, availability, leading to widespread service failures across agent networks, systems, and workflows. Cascading Failures describes the propagation and amplification of an initial fault - not the initial vulnerability itself - across agents, tools, and workflows, turning a single error into system-wide impact. ASI08 focuses on the propagation and amplification of faults rather than their origin. Use the initial defect under ASI04, ASI06, or ASI07 when it represents a direct compromise - such as a tainted dependency, poisoned memory, or spoofed message - and apply ASI08 only when that defect spreads across agents, sessions, or workflows, causing measurable fan-out or systemic impact beyond the original breach. Observable symptoms include rapid fan-out where one faulty decision triggers many downstream agents or tasks in a short time, cross-domain or tenant spread beyond the original context, oscillating retries or feedback loops between agents, and downstream queue storms or repeated identical intents - each providing clear detection hooks that make ASI08 operationally actionable. Cascading failures amplify across interconnected agents, chaining OWASP LLM Top 10 risks. LLM01:2025 Prompt Injection and LLM06:2025 Excessive Agency can trigger autonomous tool runs that spread errors without human checks, while LLM04:2025 Data and Model Poisoning in persistent memory can skew decisions across sessions and workflows. Agentic AI - Threats and Mitigations 1.1 covers this threat in T5 – Cascading Hallucination Attacks while T8 – Repudiation and Untraceability highlights a fundamental defense: the ability to trace, attribute, and audit cascading behaviors through resilient logging and non-repudiation mechanisms that prevent silent propagation. However, these compounding threats illustrate a potential discrepancy in the speed and scale of fault propagation in a multi-agent system and the ability of humans to keep up with them to ensure secure and effective operation of the system. This leaves some unmitigated risks that the enterprise must evaluate carefully to ensure they are within the overall risk budget for the organization."},
            {"id": "ASI09", "control_id": "OWASP-9", "title": "Human-Agent Trust Exploitation", "ref": "ASI09", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Intelligent agents can establish strong trust with human users through their natural language fluency, emotional intelligence, and perceived expertise, known as anthropomorphism. Adversaries or misaligned designs may exploit this trust to influence user decisions, extract sensitive information, or steer outcomes for malicious purposes. In agentic systems, this risk is amplified when humans over-rely on autonomous recommendations or unverifiable rationales, approving actions without independent validation. By leveraging authority bias and persuasive explainability, attackers can bypass oversight, leading to data breaches, financial losses, downstream and reputational harms. The agent acts as an untraceable \"bad influence,\" manipulating the human into performing the final, audited action, making the agent's role in the compromise invisible to forensics. Automation bias, perceived authority, and anthropomorphic cues make abuse look legitimate and hard to spot. Over-reliance on agent recommendations, especially when they appear confident or authoritative, increases the chance of harmful decision-making. This entry is about human misperception or over-reliance whereas ASI10 is agent intent deviation. The entry builds on LLM06:2025 Excessive Agency, and can be caused by LLM01:2025 Prompt Injection, LLM05:2025 Improper Output Handling, or results in LLM09:2025 Misinformation. Aligns with Agentic AI Threats and Mitigations Guide (T7) Misaligned & Deceptive, (T8) Repudiation & Untraceability, (T10) Overwhelming the Human in the Loop."},
            {"id": "ASI10", "control_id": "OWASP-10", "title": "Rogue Agents", "ref": "ASI10", "category": "agentic", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Rogue Agents are malicious or compromised AI Agents that deviate from their intended function or authorized scope, acting harmfully, deceptively, or parasitically within multi-agent or human-agent ecosystems. The agent’s actions may individually appear legitimate, but its emergent behavior becomes harmful, creating a containment gap for traditional rule-based systems. While external compromise, such as Prompt Injection (LLM01:2025), Goal Hijack (AS01) or Supply Chain tampering (AS04) can initiate the divergence, ASI10 focuses on the loss of behavioral integrity and governance once the drift begins, not the initial intrusion itself. Consequences include sensitive information disclosure, misinformation propagation, workflow hijacking, and operational sabotage. Rogue Agents represent a distinct risk of behavioral divergence, unlike Excessive Agency (LLM06:2025), which focuses on over-granted permissions, and can be amplified \"insider threats\" due to the speed and scale of Agentic systems. Consequences include Sensitive Information Disclosure (LLM02;2025), Misinformation (LLM09:2025). In the OWASP Agentic AI Threats and Mitigations guide, ASI10 corresponds to T13 – Rogue Agents in Multi-Agent Systems. The OWASP AIVSS framework maps this risk primarily to Behavioral Integrity (BI), Operational Security (OS), and Compliance Violations (CV), with elevated severity for critical or self-propagating deployments."},
        ],
    },

    "owasp_llm": {
        "label": "OWASP LLM Top 10 (2025)",
        "articles": [
            # OWASP Top 10 for LLM Applications 2025 — 10 risks (official pages)
            {"id": "LLM01:2025", "control_id": "OWASP-LLM-1", "title": "Prompt Injection", "ref": "LLM01:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "A Prompt Injection Vulnerability occurs when user prompts alter the LLM’s behavior or output in unintended ways. These inputs can affect the model even if they are imperceptible to humans, therefore prompt injections do not need to be human-visible/readable, as long as the content is parsed by the model. Prompt Injection vulnerabilities exist in how models process prompts, and how input may force the model to incorrectly pass prompt data to other parts of the model, potentially causing them to violate guidelines, generate harmful content, enable unauthorized access, or influence critical decisions. While techniques like Retrieval Augmented Generation (RAG) and fine-tuning aim to make LLM outputs more relevant and accurate, research shows that they do not fully mitigate prompt injection vulnerabilities. While prompt injection and jailbreaking are related concepts in LLM security, they are often used interchangeably. Prompt injection involves manipulating model responses through specific inputs to alter its behavior, which can include bypassing safety measures. Jailbreaking is a form of prompt injection where the attacker provides inputs that cause the model to disregard its safety protocols entirely. Developers can build safeguards into system prompts and input handling to help mitigate prompt injection attacks, but effective prevention of jailbreaking requires ongoing updates to the model’s training and safety mechanisms."},
            {"id": "LLM02:2025", "control_id": "OWASP-LLM-2", "title": "Sensitive Information Disclosure", "ref": "LLM02:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Sensitive information can affect both the LLM and its application context. This includes personal identifiable information (PII), financial details, health records, confidential business data, security credentials, and legal documents. Proprietary models may also have unique training methods and source code considered sensitive, especially in closed or foundation models. LLMs, especially when embedded in applications, risk exposing sensitive data, proprietary algorithms, or confidential details through their output. This can result in unauthorized data access, privacy violations, and intellectual property breaches. Consumers should be aware of how to interact safely with LLMs. They need to understand the risks of unintentionally providing sensitive data, which may later be disclosed in the model’s output. To reduce this risk, LLM applications should perform adequate data sanitization to prevent user data from entering the training model. Application owners should also provide clear Terms of Use policies, allowing users to opt out of having their data included in the training model. Adding restrictions within the system prompt about data types that the LLM should return can provide mitigation against sensitive information disclosure. However, such restrictions may not always be honored and could be bypassed via prompt injection or other methods."},
            {"id": "LLM03:2025", "control_id": "OWASP-LLM-3", "title": "Supply Chain", "ref": "LLM03:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "LLM supply chains are susceptible to various vulnerabilities, which can affect the integrity of training data, models, and deployment platforms. These risks can result in biased outputs, security breaches, or system failures. While traditional software vulnerabilities focus on issues like code flaws and dependencies, in ML the risks also extend to third-party pre-trained models and data. These external elements can be manipulated through tampering or poisoning attacks. Creating LLMs is a specialized task that often depends on third-party models. The rise of open-access LLMs and new fine-tuning methods like “LoRA” (Low-Rank Adaptation) and “PEFT” (Parameter-Efficient Fine-Tuning), especially on platforms like Hugging Face, introduce new supply-chain risks. Finally, the emergence of on-device LLMs increase the attack surface and supply-chain risks for LLM applications. Some of the risks discussed here are also discussed in “LLM04 Data and Model Poisoning.” This entry focuses on the supply-chain aspect of the risks. A simple threat model can be found here."},
            {"id": "LLM04:2025", "control_id": "OWASP-LLM-4", "title": "Data and Model Poisoning", "ref": "LLM04:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Data poisoning occurs when pre-training, fine-tuning, or embedding data is manipulated to introduce vulnerabilities, backdoors, or biases. This manipulation can compromise model security, performance, or ethical behavior, leading to harmful outputs or impaired capabilities. Common risks include degraded model performance, biased or toxic content, and exploitation of downstream systems. Data poisoning can target different stages of the LLM lifecycle, including pre-training (learning from general data), fine-tuning (adapting models to specific tasks), and embedding (converting text into numerical vectors). Understanding these stages helps identify where vulnerabilities may originate. Data poisoning is considered an integrity attack since tampering with training data impacts the model’s ability to make accurate predictions. The risks are particularly high with external data sources, which may contain unverified or malicious content. Moreover, models distributed through shared repositories or open-source platforms can carry risks beyond data poisoning, such as malware embedded through techniques like malicious pickling, which can execute harmful code when the model is loaded. Also, consider that poisoning may allow for the implementation of a backdoor. Such backdoors may leave the model’s behavior untouched until a certain trigger causes it to change. This may make such changes hard to test for and detect, in effect creating the opportunity for a model to become a sleeper agent."},
            {"id": "LLM05:2025", "control_id": "OWASP-LLM-5", "title": "Improper Output Handling", "ref": "LLM05:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Improper Output Handling refers specifically to insufficient validation, sanitization, and handling of the outputs generated by large language models before they are passed downstream to other components and systems. Since LLM-generated content can be controlled by prompt input, this behavior is similar to providing users indirect access to additional functionality. Improper Output Handling differs from Overreliance in that it deals with LLM-generated outputs before they are passed downstream whereas Overreliance focuses on broader concerns around overdependence on the accuracy and appropriateness of LLM outputs. Successful exploitation of an Improper Output Handling vulnerability can result in XSS and CSRF in web browsers as well as SSRF, privilege escalation, or remote code execution on backend systems. The following conditions can increase the impact of this vulnerability: - The application grants the LLM privileges beyond what is intended for end users, enabling escalation of privileges or remote code execution. - The application is vulnerable to indirect prompt injection attacks, which could allow an attacker to gain privileged access to a target user’s environment. - 3rd party extensions do not adequately validate inputs. - Lack of proper output encoding for different contexts (e.g., HTML, JavaScript, SQL) - Insufficient monitoring and logging of LLM outputs - Absence of rate limiting or anomaly detection for LLM usage"},
            {"id": "LLM06:2025", "control_id": "OWASP-LLM-6", "title": "Excessive Agency", "ref": "LLM06:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "An LLM-based system is often granted a degree of agency by its developer – the ability to call functions or interface with other systems via extensions (sometimes referred to as tools, skills or plugins by different vendors) to undertake actions in response to a prompt. The decision over which extension to invoke may also be delegated to an LLM ‘agent’ to dynamically determine based on input prompt or LLM output. Agent-based systems will typically make repeated calls to an LLM using output from previous invocations to ground and direct subsequent invocations. Excessive Agency is the vulnerability that enables damaging actions to be performed in response to unexpected, ambiguous or manipulated outputs from an LLM, regardless of what is causing the LLM to malfunction. Common triggers include: - hallucination/confabulation caused by poorly-engineered benign prompts, or just a poorly-performing model; - direct/indirect prompt injection from a malicious user, an earlier invocation of a malicious/compromised extension, or (in multi-agent/collaborative systems) a malicious/compromised peer agent. The root cause of Excessive Agency is typically one or more of: - excessive functionality; - excessive permissions; - excessive autonomy. Excessive Agency can lead to a broad range of impacts across the confidentiality, integrity and availability spectrum, and is dependent on which systems an LLM-based app is able to interact with. Note: Excessive Agency differs from Insecure Output Handling which is concerned with insufficient scrutiny of LLM outputs."},
            {"id": "LLM07:2025", "control_id": "OWASP-LLM-7", "title": "System Prompt Leakage", "ref": "LLM07:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The system prompt leakage vulnerability in LLMs refers to the risk that the system prompts or instructions used to steer the behavior of the model can also contain sensitive information that was not intended to be discovered. System prompts are designed to guide the model’s output based on the requirements of the application, but may inadvertently contain secrets. When discovered, this information can be used to facilitate other attacks. It’s important to understand that the system prompt should not be considered a secret, nor should it be used as a security control. Accordingly, sensitive data such as credentials, connection strings, etc. should not be contained within the system prompt language. Similarly, if a system prompt contains information describing different roles and permissions, or sensitive data like connection strings or passwords, while the disclosure of such information may be helpful, the fundamental security risk is not that these have been disclosed, it is that the application allows bypassing strong session management and authorization checks by delegating these to the LLM, and that sensitive data is being stored in a place that it should not be. In short: disclosure of the system prompt itself does not present the real risk — the security risk lies with the underlying elements, whether that be sensitive information disclosure, system guardrails bypass, improper separation of privileges, etc. Even if the exact wording is not disclosed, attackers interacting with the system will almost certainly be able to determine many of the guardrails and formatting restrictions that are present in system prompt language in the course of using the application, sending utterances to the model, and observing the results."},
            {"id": "LLM08:2025", "control_id": "OWASP-LLM-8", "title": "Vector and Embedding Weaknesses", "ref": "LLM08:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Vectors and embeddings vulnerabilities present significant security risks in systems utilizing Retrieval Augmented Generation (RAG) with Large Language Models (LLMs). Weaknesses in how vectors and embeddings are generated, stored, or retrieved can be exploited by malicious actions (intentional or unintentional) to inject harmful content, manipulate model outputs, or access sensitive information. Retrieval Augmented Generation (RAG) is a model adaptation technique that enhances the performance and contextual relevance of responses from LLM Applications, by combining pre-trained language models with external knowledge sources.Retrieval Augmentation uses vector mechanisms and embedding. (Ref #1)"},
            {"id": "LLM09:2025", "control_id": "OWASP-LLM-9", "title": "Misinformation", "ref": "LLM09:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Misinformation from LLMs poses a core vulnerability for applications relying on these models. Misinformation occurs when LLMs produce false or misleading information that appears credible. This vulnerability can lead to security breaches, reputational damage, and legal liability. One of the major causes of misinformation is hallucination—when the LLM generates content that seems accurate but is fabricated. Hallucinations occur when LLMs fill gaps in their training data using statistical patterns, without truly understanding the content. As a result, the model may produce answers that sound correct but are completely unfounded. While hallucinations are a major source of misinformation, they are not the only cause; biases introduced by the training data and incomplete information can also contribute. A related issue is overreliance. Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy. This overreliance exacerbates the impact of misinformation, as users may integrate incorrect data into critical decisions or processes without adequate scrutiny."},
            {"id": "LLM10:2025", "control_id": "OWASP-LLM-10", "title": "Unbounded Consumption", "ref": "LLM10:2025", "category": "llm", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Unbounded Consumption refers to the process where a Large Language Model (LLM) generates outputs based on input queries or prompts. Inference is a critical function of LLMs, involving the application of learned patterns and knowledge to produce relevant responses or predictions. Attacks designed to disrupt service, deplete the target’s financial resources, or even steal intellectual property by cloning a model’s behavior all depend on a common class of security vulnerability in order to succeed. Unbounded Consumption occurs when a Large Language Model (LLM) application allows users to conduct excessive and uncontrolled inferences, leading to risks such as denial of service (DoS), economic losses, model theft, and service degradation. The high computational demands of LLMs, especially in cloud environments, make them vulnerable to resource exploitation and unauthorized usage."},
        ],
    },

    "iso_42001": {
        "label": "ISO 42001",
        "articles": [
            {"id": "4.1", "control_id": "ISO-4.1", "title": "External & Internal Context", "ref": "Clause 4.1", "category": "context", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Determine external and internal issues relevant to the AI management system."},
            {"id": "4.2", "control_id": "ISO-4.2", "title": "Interested Parties", "ref": "Clause 4.2", "category": "context", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Identify interested parties and their requirements relevant to AI management."},
            {"id": "4.3", "control_id": "ISO-4.3", "title": "Scope of AI Management System", "ref": "Clause 4.3", "category": "context", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Define scope and boundaries of the AI management system."},
            {"id": "4.4", "control_id": "ISO-4.4", "title": "AI Management System", "ref": "Clause 4.4", "category": "context", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Establish, implement, maintain and continually improve an AI management system."},
            {"id": "5.1", "control_id": "ISO-5.1", "title": "Leadership & Commitment", "ref": "Clause 5.1", "category": "leadership", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Top management must demonstrate leadership and commitment to the AI management system."},
            {"id": "5.2", "control_id": "ISO-5.2", "title": "AI Policy", "ref": "Clause 5.2", "category": "leadership", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Establish, implement, and maintain an AI policy appropriate to the purpose of the organization."},
            {"id": "5.3", "control_id": "ISO-5.3", "title": "Roles & Responsibilities", "ref": "Clause 5.3", "category": "leadership", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Assign roles, responsibilities, and authorities for AI management system."},
            {"id": "6.1", "control_id": "ISO-6.1", "title": "Risk-Based Planning", "ref": "Clause 6.1", "category": "planning", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Plan actions to address risks and opportunities for the AI management system."},
            {"id": "6.2", "control_id": "ISO-6.2", "title": "AI Objectives", "ref": "Clause 6.2", "category": "planning", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Establish AI objectives at relevant functions and levels, with measures and timelines."},
            {"id": "7.1", "control_id": "ISO-7.1", "title": "Resources", "ref": "Clause 7.1", "category": "support", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Determine and provide resources needed for the AI management system."},
            {"id": "7.2", "control_id": "ISO-7.2", "title": "Competence", "ref": "Clause 7.2", "category": "support", "tiers": ["high", "limited", "gpa"], "summary": "Ensure personnel are competent in AI governance and risk management."},
            {"id": "7.3", "control_id": "ISO-7.3", "title": "Awareness", "ref": "Clause 7.3", "category": "support", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Ensure awareness of AI policy and relevant objectives across the organization."},
            {"id": "7.4", "control_id": "ISO-7.4", "title": "Communication", "ref": "Clause 7.4", "category": "support", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Establish internal and external communications relevant to AI management system."},
            {"id": "7.5", "control_id": "ISO-7.5", "title": "Documented Information", "ref": "Clause 7.5", "category": "support", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Maintain documented information to support the AI management system."},
            {"id": "8.1", "control_id": "ISO-8.1", "title": "Operational Planning & Control", "ref": "Clause 8.1", "category": "operation", "tiers": ["high", "limited", "gpa"], "summary": "Plan, implement, and control AI system processes to meet requirements."},
            {"id": "8.2", "control_id": "ISO-8.2", "title": "AI Risk Assessment", "ref": "Clause 8.2", "category": "operation", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Manage AI systems across design, development, deployment, monitoring, and retirement."},
            {"id": "8.3", "control_id": "ISO-8.3", "title": "AI Risk Treatment", "ref": "Clause 8.3", "category": "operation", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Implement the AI risk treatment plan according to 6.1.3, verify its effectiveness, revalidate ineffective treatment options, and retain documented information of all AI risk treatments."},
            {"id": "8.4", "control_id": "ISO-8.4", "title": "AI System Impact Assessment", "ref": "Clause 8.4", "category": "operation", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Perform AI system impact assessments according to 6.1.4 at planned intervals or when significant changes are proposed, and retain documented information of the results."},
            {"id": "9.1", "control_id": "ISO-9.1", "title": "Monitoring & Measurement", "ref": "Clause 9.1", "category": "evaluation", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Monitor and measure AI system performance and effectiveness of controls."},
            {"id": "9.2", "control_id": "ISO-9.2", "title": "Internal Audit", "ref": "Clause 9.2", "category": "evaluation", "tiers": ["high", "limited", "gpa"], "summary": "Conduct internal audits at planned intervals to assess AI management system compliance."},
            {"id": "9.3", "control_id": "ISO-9.3", "title": "Management Review", "ref": "Clause 9.3", "category": "evaluation", "tiers": ["high", "limited", "gpa"], "summary": "Top management must review the AI management system at planned intervals."},
            {"id": "10.1", "control_id": "ISO-10.1", "title": "Continual Improvement", "ref": "Clause 10.1", "category": "improvement", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Identify nonconformities, determine causes, implement corrective actions, and prevent recurrence."},
            {"id": "10.2", "control_id": "ISO-10.2", "title": "Nonconformity & Corrective Action", "ref": "Clause 10.2", "category": "improvement", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Continually improve the suitability, adequacy, and effectiveness of the AI management system."},
            # A.2 — 
            {"id": "A.2.2", "control_id": "ISO-A.2.2", "title": "AI policy", "ref": "A.2.2", "category": "A.2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall document a policy for the development or use of AI systems."},
            {"id": "A.2.3", "control_id": "ISO-A.2.3", "title": "Alignment with other organizational policies", "ref": "A.2.3", "category": "A.2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine where other policies can be affected by or apply to, the organization's objectives with respect to AI systems."},
            {"id": "A.2.4", "control_id": "ISO-A.2.4", "title": "Review of the AI policy", "ref": "A.2.4", "category": "A.2", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The AI policy shall be reviewed at planned intervals or additionally as needed to ensure its continuing suitability, adequacy and effectiveness."},
            # A.3 — 
            {"id": "A.3.2", "control_id": "ISO-A.3.2", "title": "AI roles and responsibilities", "ref": "A.3.2", "category": "A.3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "Roles and responsibilities for AI shall be defined and allocated according to the needs of the organization."},
            {"id": "A.3.3", "control_id": "ISO-A.3.3", "title": "Reporting of concerns", "ref": "A.3.3", "category": "A.3", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and put in place a process to report concerns about the organization's role with respect to an AI system throughout its life cycle."},
            # A.4 — 
            {"id": "A.4.2", "control_id": "ISO-A.4.2", "title": "Resource documentation", "ref": "A.4.2", "category": "A.4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall identify and document relevant resources required for the activities at given AI system life cycle stages and other AI-related activities relevant for the organization."},
            {"id": "A.4.3", "control_id": "ISO-A.4.3", "title": "Data resources", "ref": "A.4.3", "category": "A.4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "As part of resource identification, the organization shall document information about the data resources utilized for the AI system."},
            {"id": "A.4.4", "control_id": "ISO-A.4.4", "title": "Tooling resources", "ref": "A.4.4", "category": "A.4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "As part of resource identification, the organization shall document information about the tooling resources utilized for the AI system."},
            {"id": "A.4.5", "control_id": "ISO-A.4.5", "title": "System and computing resources", "ref": "A.4.5", "category": "A.4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "As part of resource identification, the organization shall document information about the system and computing resources utilized for the AI system."},
            {"id": "A.4.6", "control_id": "ISO-A.4.6", "title": "Human resources", "ref": "A.4.6", "category": "A.4", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "As part of resource identification, the organization shall document information about the human resources and their competences utilized for the development, deployment, operation, change management, maintenance, transfer and decommissioning, as well as verification and integration of the AI system."},
            # A.5 — 
            {"id": "A.5.2", "control_id": "ISO-A.5.2", "title": "AI system impact assessment process", "ref": "A.5.2", "category": "A.5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall establish a process to assess the potential consequences for individuals or groups of individuals, or both, and societies that can result from the AI system throughout its life cycle."},
            {"id": "A.5.3", "control_id": "ISO-A.5.3", "title": "Documentation of AI system impact assessments", "ref": "A.5.3", "category": "A.5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall document the results of AI system impact assessments and retain results for a defined period."},
            {"id": "A.5.4", "control_id": "ISO-A.5.4", "title": "Assessing AI system impact on individuals or groups of individuals", "ref": "A.5.4", "category": "A.5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall assess and document the potential impacts of AI systems to individuals or groups of individuals throughout the system's life cycle."},
            {"id": "A.5.5", "control_id": "ISO-A.5.5", "title": "Assessing societal impacts of AI systems", "ref": "A.5.5", "category": "A.5", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall assess and document the potential societal impacts of their AI systems throughout their life cycle."},
            # A.6 — 
            {"id": "A.6.1.2", "control_id": "ISO-A.6.1.2", "title": "Objectives for responsible development of AI system", "ref": "A.6.1.2", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall identify and document objectives to guide the responsible development AI systems, and take those objectives into account and integrate measures to achieve them in the development life cycle."},
            {"id": "A.6.1.3", "control_id": "ISO-A.6.1.3", "title": "Processes for responsible AI system design and development", "ref": "A.6.1.3", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document the specific processes for the responsible design and development of the AI system."},
            {"id": "A.6.2.2", "control_id": "ISO-A.6.2.2", "title": "AI system requirements and specification", "ref": "A.6.2.2", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall specify and document requirements for new AI systems or material enhancements to existing systems."},
            {"id": "A.6.2.3", "control_id": "ISO-A.6.2.3", "title": "Documentation of AI system design and development", "ref": "A.6.2.3", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall document the AI system design and development based on organizational objectives, documented requirements and specification criteria."},
            {"id": "A.6.2.4", "control_id": "ISO-A.6.2.4", "title": "AI system verification and validation", "ref": "A.6.2.4", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document verification and validation measures for the AI system and specify criteria for their use."},
            {"id": "A.6.2.5", "control_id": "ISO-A.6.2.5", "title": "AI system deployment", "ref": "A.6.2.5", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall document a deployment plan and ensure that appropriate requirements are met prior to deployment."},
            {"id": "A.6.2.6", "control_id": "ISO-A.6.2.6", "title": "AI system operation and monitoring", "ref": "A.6.2.6", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document the necessary elements for the ongoing operation of the AI system. At the minimum, this should include system and performance monitoring, repairs, updates and support."},
            {"id": "A.6.2.7", "control_id": "ISO-A.6.2.7", "title": "AI system technical documentation", "ref": "A.6.2.7", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine what AI system technical documentation is needed for each relevant category of interested parties, such as users, partners, supervisory authorities, and provide the technical documentation to them in the appropriate form."},
            {"id": "A.6.2.8", "control_id": "ISO-A.6.2.8", "title": "AI system recording of event logs", "ref": "A.6.2.8", "category": "A.6", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine at which phases of the AI system life cycle, record keeping of event logs should be enabled, but at the minimum when the AI system is in use."},
            # A.7 — 
            {"id": "A.7.2", "control_id": "ISO-A.7.2", "title": "Data for development and enhancement of AI system", "ref": "A.7.2", "category": "A.7", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define, document and implement data management processes related to the development of AI systems."},
            {"id": "A.7.3", "control_id": "ISO-A.7.3", "title": "Acquisition of data", "ref": "A.7.3", "category": "A.7", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine and document details about the acquisition and selection of the data used in AI systems."},
            {"id": "A.7.4", "control_id": "ISO-A.7.4", "title": "Quality of data for AI systems", "ref": "A.7.4", "category": "A.7", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document requirements for data quality and ensure that data used to develop and operate the AI system meet those requirements."},
            {"id": "A.7.5", "control_id": "ISO-A.7.5", "title": "Data provenance", "ref": "A.7.5", "category": "A.7", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document a process for recording the provenance of data used in its AI systems over the life cycles of the data and the AI system."},
            {"id": "A.7.6", "control_id": "ISO-A.7.6", "title": "Data preparation", "ref": "A.7.6", "category": "A.7", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document its criteria for selecting data preparations and the data preparation methods to be used."},
            # A.8 — 
            {"id": "A.8.2", "control_id": "ISO-A.8.2", "title": "System documentation and information for users", "ref": "A.8.2", "category": "A.8", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine and provide the necessary information to users of the AI system."},
            {"id": "A.8.3", "control_id": "ISO-A.8.3", "title": "External reporting", "ref": "A.8.3", "category": "A.8", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall provide capabilities for interested parties to report adverse impacts of the AI system."},
            {"id": "A.8.4", "control_id": "ISO-A.8.4", "title": "Communication of incidents", "ref": "A.8.4", "category": "A.8", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine and document a plan for communicating incidents to users of the AI system."},
            {"id": "A.8.5", "control_id": "ISO-A.8.5", "title": "Information for interested parties", "ref": "A.8.5", "category": "A.8", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall determine and document their obligations to reporting information about the AI system to interested parties."},
            # A.9 — 
            {"id": "A.9.2", "control_id": "ISO-A.9.2", "title": "Processes for responsible use of AI systems", "ref": "A.9.2", "category": "A.9", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall define and document the processes for the responsible use of AI systems."},
            {"id": "A.9.3", "control_id": "ISO-A.9.3", "title": "Objectives for responsible use of AI system", "ref": "A.9.3", "category": "A.9", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall identify and document objectives to guide the responsible use of AI systems."},
            {"id": "A.9.4", "control_id": "ISO-A.9.4", "title": "Intended use of the AI system", "ref": "A.9.4", "category": "A.9", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall ensure that the AI system is used according to the intended uses of the AI system and its accompanying documentation."},
            # A.10 — 
            {"id": "A.10.2", "control_id": "ISO-A.10.2", "title": "Allocating responsibilities", "ref": "A.10.2", "category": "A.10", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall ensure that responsibilities within their AI system life cycle are allocated between the organization, its partners, suppliers, customers and third parties."},
            {"id": "A.10.3", "control_id": "ISO-A.10.3", "title": "Suppliers", "ref": "A.10.3", "category": "A.10", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall establish a process to ensure that its usage of services, products or materials provided by suppliers aligns with the organization's approach to the responsible development and use of AI systems."},
            {"id": "A.10.4", "control_id": "ISO-A.10.4", "title": "Customers", "ref": "A.10.4", "category": "A.10", "tiers": ["high", "limited", "minimal", "gpa", "unacceptable"], "summary": "The organization shall ensure that its responsible approach to the development and use of AI systems considers their customer expectations and needs."},
        ],
    },
}


# EU AI Act applicability dates (Regulation (EU) 2024/1689, sts as amended by
# the 2026 "Digital Omnibus"). The Act applies in phases:
#   - Art. 5 prohibitions + AI literacy : 2025-02-02
#   - Arts 51-56 GPAI model rules         : 2025-08-02
#   - Art. 50 transparency (general)      : 2026-08-02 (enforcement powers too)
#   - Art. 57 sandboxes / support         : 2025-08-02
#   - High-risk (Annex III standalone)    : 2027-12-02 (extended by Omnibus)
#   - High-risk embedded (Annex I)        : 2028-08-02 (extended by Omnibus)
# The app models standalone high-risk AI (Annex III), so the default high-risk
# date is 2027-12-02. Annex I (product-embedded) systems would come later.
EU_APPLIES_FROM: dict[str, str] = {
    "5": "2025-02-02",
    "57": "2025-08-02",
    "50": "2026-08-02",
}
EU_GPAI_IDS = {"51", "52", "53", "54", "55", "56"}
EU_DEFAULT_APPLIES_FROM = "2027-12-02"


def eu_applicable_from(article: dict) -> str:
    """ISO-8601 date an EU AI Act article enters into application."""
    aid = str(article.get("id") or "")
    if aid in EU_GPAI_IDS:
        return "2025-08-02"
    return EU_APPLIES_FROM.get(aid, EU_DEFAULT_APPLIES_FROM)


def _eu_article_in_force(article: dict, today: str) -> bool:
    return eu_applicable_from(article) <= today


ALL_PROFILES = ("provider", "deployer", "gpai", "agentic")
EU_CATEGORY_PROFILES = {
    "prohibited": ALL_PROFILES,
    "classification": ALL_PROFILES,
    "requirements": ("provider", "agentic"),
    "provider": ("provider", "agentic"),
    "deployer": ("deployer",),
    "limited": ("provider", "deployer", "agentic"),
    "gpai": ("gpai",),
    "post_market": ("provider", "agentic", "gpai"),
}
NIST_FUNCTIONS_FOR_TIER = {
    "minimal": {"GOVERN"},
    "limited": {"GOVERN", "MAP"},
    "high": {"GOVERN", "MAP", "MEASURE", "MANAGE"},
    "gpa": {"GOVERN", "MAP", "MEASURE", "MANAGE"},
    "unacceptable": {"GOVERN", "MAP", "MEASURE", "MANAGE"},
    "unclassified": {"GOVERN", "MAP", "MEASURE", "MANAGE"},
}
ISO_CATEGORIES_FOR_TIER = {
    "minimal": {"context", "leadership", "A.2", "A.3"},
    "limited": {"context", "leadership", "planning", "support", "A.2", "A.3", "A.4", "A.9", "A.10"},
}


def article_profiles(fw_key: str, article: dict) -> tuple[str, ...]:
    if article.get("profiles"):
        return tuple(article["profiles"])
    if fw_key == "eu_ai_act":
        return EU_CATEGORY_PROFILES.get(article.get("category") or "", ALL_PROFILES)
    if fw_key == "owasp_agentic":
        return ("agentic",)
    if fw_key == "owasp_llm":
        return ("gpai", "provider")
    return ALL_PROFILES


def article_in_queue(fw_key: str, article: dict, tier: str, profile: str) -> bool:
    """Whether this article belongs on the system's work queue."""
    tiers = article.get("tiers") or []
    if tier not in tiers:
        return False
    profiles = article_profiles(fw_key, article)
    if profile and profile not in profiles:
        return False
    if fw_key == "nist_ai_rmf":
        fn = (article.get("category") or "").split()[0]
        allowed = NIST_FUNCTIONS_FOR_TIER.get(tier) or {"GOVERN", "MAP", "MEASURE", "MANAGE"}
        if fn not in allowed:
            return False
    if fw_key == "iso_42001":
        allowed = ISO_CATEGORIES_FOR_TIER.get(tier)
        if allowed and (article.get("category") or "") not in allowed:
            return False
    return True


def applicable_articles(system: dict, framework: str, as_of: str | None = None) -> list[dict]:
    fw = FRAMEWORKS.get(framework) or {}
    tier = system.get("risk_classification") or "unclassified"
    profile = (system.get("ai_profile") or "provider").strip() or "provider"
    today = as_of or datetime.now(timezone.utc).date().isoformat()
    res = []
    for a in fw.get("articles") or []:
        if not article_in_queue(framework, a, tier, profile):
            continue
        if framework == "eu_ai_act" and not _eu_article_in_force(a, today):
            continue
        if framework == "eu_ai_act":
            a = dict(a)
            a["applies_from"] = eu_applicable_from(a)
        res.append(a)
    return res


def gap_analysis_rows(systems: dict, framework: str | None = None) -> list[dict]:
    """Fleet coverage for articles that are in at least one system's classified queue."""
    results = []
    system_list = list(systems.values()) if isinstance(systems, dict) else list(systems or [])
    for fw_key, fw_def in FRAMEWORKS.items():
        if framework and fw_key != framework:
            continue
        today = datetime.now(timezone.utc).date().isoformat()
        for art in fw_def.get("articles") or []:
            if fw_key == "eu_ai_act" and not _eu_article_in_force(art, today):
                continue
            if fw_key == "eu_ai_act":
                art = dict(art)
                art["applies_from"] = eu_applicable_from(art)
            applicable_systems = []
            for sys in system_list:
                tier = sys.get("risk_classification") or "unclassified"
                profile = (sys.get("ai_profile") or "provider").strip() or "provider"
                if article_in_queue(fw_key, art, tier, profile):
                    applicable_systems.append(sys)
            if system_list and not applicable_systems:
                continue
            match_id = art["ref"].replace(" ", "").replace(".", "").lower()
            covered = 0
            for sys in (applicable_systems or system_list):
                tags = [t.lower().replace(".", "").replace(" ", "") for t in sys.get("controls") or []]
                if any(match_id in t for t in tags) or sys.get("classification_status") in ("high", "prohibited"):
                    covered += 1
            denom = len(applicable_systems) if applicable_systems else (len(system_list) or 1)
            pct = round((covered / denom) * 100) if denom else 0
            results.append({
                "framework": fw_key,
                "control_id": art["ref"],
                "control": art.get("title") or "",
                "description": art.get("summary") or "",
                "covered_count": covered,
                "total_systems": len(applicable_systems) if applicable_systems else len(system_list),
                "coverage_pct": pct,
                "status": "covered" if pct >= 80 else "partial" if pct >= 30 else "missing",
            })
    return results


def _load_system(sid: str) -> dict | None:
    p = os.path.join(DATA_DIR, "systems.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        db = json.load(f)
    return db.get(sid)


@router.get("/api/systems/{sid}/conformity/articles")
def list_applicable_articles(sid: str, framework: str = Query("eu_ai_act")):
    system = _load_system(sid)
    if not system:
        raise HTTPException(404, "System not found")
    fw = FRAMEWORKS.get(framework)
    if not fw:
        raise HTTPException(404, f"Framework '{framework}' not found")
    tier = system.get("risk_classification", "unclassified")
    profile = (system.get("ai_profile") or "provider").strip() or "provider"
    applicable = applicable_articles(system, framework)
    today = datetime.now(timezone.utc).date().isoformat()
    eu_in_force = (
        sum(1 for a in fw["articles"] if _eu_article_in_force(a, today))
        if framework == "eu_ai_act"
        else None
    )
    return {
        "articles": applicable,
        "tier": tier,
        "profile": profile,
        "framework": framework,
        "framework_label": fw["label"],
        "catalog_total": len(fw["articles"]),
        "in_force_total": eu_in_force,
        "as_of": today,
        "in_queue": len(applicable),
    }


@router.get("/api/systems/{sid}/conformity")
def get_conformity(sid: str, framework: str = Query("eu_ai_act")):
    db = _load()
    key = f"{sid}:{framework}"
    record = db.get(key)
    return {"conformity": record or None, "framework": framework}


@router.post("/api/systems/{sid}/conformity")
def save_conformity(sid: str, body: dict = {}, framework: str = Query("eu_ai_act")):
    system = _load_system(sid)
    if not system:
        raise HTTPException(404, "System not found")
    fw = FRAMEWORKS.get(framework)
    if not fw:
        raise HTTPException(404, f"Framework '{framework}' not found")
    db = _load()
    key = f"{sid}:{framework}"
    record = db.get(key, {
        "system_id": sid,
        "framework": framework,
        "status": "draft",
        "articles": {},
        "created_at": _now(),
    })
    if "articles" in body:
        record["articles"] = body["articles"]
    if "status" in body:
        record["status"] = body["status"]
    record["updated_at"] = _now()
    db[key] = record
    _save(db)
    return {"conformity": record}


@router.post("/api/systems/{sid}/conformity/export")
def export_conformity(sid: str, framework: str = Query("eu_ai_act")):
    try:
        from fpdf import FPDF
    except ImportError:
        raise HTTPException(501, "PDF generation not available")
    system = _load_system(sid)
    if not system:
        raise HTTPException(404, "System not found")
    fw = FRAMEWORKS.get(framework)
    if not fw:
        raise HTTPException(404, f"Framework '{framework}' not found")
    db = _load()
    key = f"{sid}:{framework}"
    record = db.get(key)
    if not record:
        raise HTTPException(400, "No conformity assessment saved yet")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"{fw['label']} — Assessment Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, f"Generated: {_now()[:10]}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    def sec(t):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, t, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    def fld(l, v):
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(50, 4, l)
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(0, 4, str(v) if v else "-")
        pdf.ln(1)

    sec("1. System Identification")
    fld("Name:", system.get("name"))
    fld("Version:", system.get("version"))
    fld("Description:", system.get("description"))
    fld("Purpose:", system.get("purpose"))
    fld("Risk Classification:", system.get("risk_classification", "unclassified"))

    tier = system.get("risk_classification", "unclassified")
    applicable = applicable_articles(system, framework)

    sec(f"2. Assessment by {fw['label']}")
    articles = record.get("articles", {})
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(30, 5, "Control", border=1)
    pdf.cell(55, 5, "Requirement", border=1)
    pdf.cell(22, 5, "Status", border=1)
    pdf.cell(0, 5, "Notes", border=1, new_x="LMARGIN", new_y="NEXT")
    for art in applicable:
        a = articles.get(art["id"], {})
        status = a.get("status", "missing")
        notes = a.get("notes", "")[:60]
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(30, 5, art["ref"], border=1)
        pdf.cell(55, 5, art["title"][:35], border=1)
        pdf.cell(22, 5, status.upper(), border=1)
        pdf.cell(0, 5, notes, border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    sec("3. Summary")
    overall = "FULLY COMPLIANT" if all(a.get("status") == "compliant" for a in articles.values() if a.get("status")) else "PARTIALLY COMPLIANT"
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, f"Overall Status: {overall}", new_x="LMARGIN", new_y="NEXT")

    buffer = bytes(pdf.output())
    return Response(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=assessment-{framework}-{sid}.pdf"})


@router.post("/api/systems/{sid}/conformity/eu-doc")
def export_eu_declaration(sid: str):
    """EU Declaration of Conformity (Art. 47) — docx."""
    system = _load_system(sid)
    if not system:
        raise HTTPException(404, "System not found")
    from eu_artifacts import export_eu_declaration_of_conformity

    buffer = export_eu_declaration_of_conformity(system)
    return Response(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=eu-declaration-of-conformity-{sid}.docx"},
    )


@router.post("/api/systems/{sid}/conformity/tech-doc")
def export_tech_doc(sid: str):
    """Technical documentation (Art. 11 / Annex IV) — docx."""
    system = _load_system(sid)
    if not system:
        raise HTTPException(404, "System not found")
    from eu_artifacts import export_technical_documentation

    buffer = export_technical_documentation(system)
    return Response(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=technical-documentation-{sid}.docx"},
    )


@router.post("/api/systems/{sid}/conformity/soa-export")
def export_ai_soa_route(sid: str, framework: str = Query("iso_42001")):
    """AI Management System Statement of Applicability (ISO 42001) — docx."""
    system = _load_system(sid)
    if not system:
        raise HTTPException(404, "System not found")
    from eu_artifacts import export_ai_soa

    try:
        buffer = export_ai_soa(system, framework)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return Response(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=ai-statement-of-applicability-{sid}.docx"},
    )
