PLAN_TYPES = {
    "eu_ai_act": [
        "ai_risk_management",
        "conformity_assessment",
        "incident_response",
        "post_market_monitoring",
        "ai_literacy",
        "training_competence",
        "systemic_risk_mitigation",
    ],
    "nist_ai_rmf": [
        "ai_risk_management",
        "incident_response",
        "continuous_improvement",
        "change_management",
        "stakeholder_communication",
        "third_party_risk_management",
    ],
    "iso_42001": [
        "ams_implementation",
        "risk_assessment_treatment",
        "internal_audit",
        "management_review",
        "competence_development",
        "continual_improvement",
    ],
}

PLAN_TEMPLATES = {
    "eu_ai_act": {

        "ai_risk_management": {
            "name": "AI Risk Management Plan",
            "description": "Risk management process for high-risk AI systems per Art. 9, covering risk identification, analysis, evaluation, and mitigation across the system lifecycle.",
            "content": """## 1. Purpose & Scope
This AI Risk Management Plan establishes the process for identifying, analyzing, evaluating, and mitigating risks associated with AI systems classified as high-risk under EU AI Act Art. 9. It applies to all high-risk AI systems operated within the organization.

## 2. Risk Management Process
### 2.1 Risk Identification
- Systematic identification of known and foreseeable risks to health, safety, and fundamental rights
- Review at each significant system change
- Sources: testing results, incident reports, user feedback, external threat intelligence

### 2.2 Risk Analysis & Evaluation
- Each identified risk shall be evaluated for severity and probability
- Risk scoring matrix: Severity (1-5) × Probability (1-5) = Risk Score
- Thresholds: Score ≥ 12 = unacceptable, 6-11 = high, 3-5 = medium, 1-2 = low

### 2.3 Risk Mitigation
- Eliminate or reduce risks through design and development choices
- Implement appropriate technical and organizational measures
- Provide information to deployers on residual risks
- Validation: each mitigation measure shall be tested and documented

## 3. Roles & Responsibilities
- Risk Owner: [Enter name] — accountable for risk management of [system name]
- Risk Manager: [Enter name] — responsible for risk assessment execution
- Review Board: [Enter names] — quarterly risk review committee

## 4. Monitoring & Review
- Continuous monitoring throughout system lifecycle
- Formal risk review triggered by: significant system changes, new incident patterns, regulatory updates
- Annual comprehensive risk management review

## 5. Documentation
- Risk management documentation shall be maintained and updated
- Includes: risk register, risk assessment reports, mitigation validation records
- Retention: throughout system lifetime plus 5 years

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "conformity_assessment": {
            "name": "Conformity Assessment Plan",
            "description": "Plan for conducting EU AI Act conformity assessment per Art. 43 and Annex VI/VII, including internal controls, technical documentation review, and notified body engagement.",
            "content": """## 1. Purpose & Scope
This Conformity Assessment Plan defines the procedure for demonstrating compliance of high-risk AI systems with EU AI Act requirements per Art. 43 and Annex VI/VII.

## 2. Applicable Systems
[List high-risk AI systems subject to conformity assessment]

## 3. Conformity Assessment Procedure
### 3.1 Internal Control (Annex VI)
For systems classified as high-risk under Art. 6(2):
- Verify risk management system (Art. 9)
- Verify data governance (Art. 10)
- Verify technical documentation (Art. 11 + Annex IV)
- Verify record-keeping (Art. 12)
- Verify transparency (Art. 13)
- Verify human oversight (Art. 14)
- Verify accuracy, robustness, cybersecurity (Art. 15)

### 3.2 Notified Body Assessment (Annex VII)
For systems classified as high-risk under Art. 6(1):
- Submit technical documentation to notified body
- Notified body reviews documentation
- Notified body issues certificate of conformity
- Annual surveillance audits

## 4. Timeline & Milestones
- Technical documentation complete: [date]
- Internal conformity assessment: [date]
- Notified body submission: [date]
- EU Database registration: [date]

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "incident_response": {
            "name": "Incident Response Plan (AI)",
            "description": "Incident response and serious incident reporting for AI systems per Art. 73, including detection, triage, containment, remediation, and mandatory reporting to national authorities.",
            "content": """## 1. Purpose & Scope
This AI Incident Response Plan establishes procedures for detecting, responding to, and reporting serious incidents involving AI systems per EU AI Act Art. 73.

## 2. Definitions
- Serious Incident: incident directly causing death, serious harm to health/property, or serious disruption of critical infrastructure
- Near Miss: incident with potential to become serious but was prevented
- Reportable Incident: any serious incident involving a high-risk AI system

## 3. Incident Response Process
### 3.1 Detection & Triage (0-2 hours)
- Monitoring systems detect anomaly or alert
- Initial triage by on-call AI incident responder
- Severity classification: Critical / High / Medium / Low

### 3.2 Containment & Analysis (2-24 hours)
- Isolate affected AI system or model version
- Collect logs, evidence, and system state
- Conduct root cause analysis
- Determine if incident meets reporting threshold

### 3.3 Remediation & Recovery (24-72 hours)
- Implement fix or rollback to safe version
- Verify fix through testing
- Resume operations after approval

### 3.4 Reporting (per Art. 73)
- Report to national supervisory authority within 15 days of becoming aware
- Report includes: nature of incident, circumstances, effects, corrective actions
- For GPAI systems with systemic risk: report to AI Office within 7 days

## 4. Contact & Escalation
- AI Incident Response Lead: [name], [phone]
- Legal / Regulatory Liaison: [name], [phone]
- National Authority Contact: [AI Office / national regulator]

## 5. Post-Incident Review
- Root cause analysis report
- Lessons learned documentation
- Incident response plan update

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "post_market_monitoring": {
            "name": "Post-Market Monitoring Plan",
            "description": "Systematic post-market monitoring for AI systems per Art. 61, defining data collection, analysis, and reporting to detect emerging risks throughout the system lifecycle.",
            "content": """## 1. Purpose & Scope
This Post-Market Monitoring Plan defines the systematic process for collecting, analyzing, and reporting data on the performance and safety of AI systems throughout their lifetime, per EU AI Act Art. 61.

## 2. Monitoring Strategy
### 2.1 Data Sources
- Automated performance metrics collection
- User feedback and complaint analysis
- Incident and near-miss reports
- Drift detection (data drift, concept drift, model drift)
- External: regulatory updates, scientific literature, industry incidents

### 2.2 Metrics & Thresholds
- Accuracy degradation: alert if >5% drop from baseline
- Bias metrics: monitor for drift in fairness metrics
- User satisfaction: quarterly survey score target > 4.0/5.0
- Incident rate: >3 incidents/quarter triggers review

## 3. Collection & Analysis Cadence
- Automated metrics: continuous, daily review
- User feedback: weekly aggregation
- Drift analysis: monthly
- Comprehensive review: quarterly

## 4. Reporting
- Quarterly Post-Market Monitoring Report to AI governance board
- Annual summary report
- Immediate notification of any serious incident or emerging risk

## 5. Triggered Review
Post-market monitoring data shall trigger an unscheduled review when:
- Metric exceeds threshold for 7 consecutive days
- Any serious incident occurs
- Regulatory guidance changes materially

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "ai_literacy": {
            "name": "AI Literacy Plan",
            "description": "AI literacy program per Art. 4, ensuring staff who deploy and operate AI systems have sufficient AI literacy including technical knowledge, risk awareness, and ethical principles.",
            "content": """## 1. Purpose & Scope
This AI Literacy Plan establishes training and awareness programs to ensure all personnel involved in the deployment and operation of AI systems possess sufficient AI literacy per EU AI Act Art. 4.

## 2. Target Audiences
- AI Developers & Engineers: deep technical literacy
- AI System Operators: operational literacy
- Managers & Decision-Makers: governance and risk literacy
- General Staff: basic awareness

## 3. Literacy Levels by Role
### 3.1 Developers & Engineers
- Understanding of AI/ML fundamentals
- Bias detection and mitigation techniques
- Robustness testing methodologies
- EU AI Act compliance requirements

### 3.2 Operators
- System capabilities and limitations
- Human oversight procedures
- Incident reporting process
- Data handling and privacy requirements

### 3.3 Managers
- AI risk management principles
- Regulatory compliance framework
- Ethical AI principles
- Third-party AI governance

## 4. Training Program
- Initial training: upon assignment to AI-related role
- Refresher training: annual
- Awareness communications: quarterly
- Training methods: workshops, e-learning modules, tabletop exercises

## 5. Tracking & Records
- Training completion tracked in [LMS/HR system]
- Records maintained for minimum 3 years
- Annual literacy assessment

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "training_competence": {
            "name": "Training & Competence Plan (AI)",
            "description": "Training and competence program for AI personnel covering technical skills, regulatory knowledge, ethical awareness, and role-specific qualifications.",
            "content": """## 1. Purpose & Scope
This Training & Competence Plan defines the qualification requirements and training programs for personnel involved in developing, deploying, and overseeing AI systems.

## 2. Competence Framework
### 2.1 Technical Competence
- ML engineering and model development
- Data engineering and governance
- Model evaluation and testing
- System security and robustness

### 2.2 Regulatory Competence
- EU AI Act requirements by role
- Data protection and privacy
- Sector-specific regulations
- Standards (ISO 42001, ISO 27001)

### 2.3 Ethical Competence
- Ethical AI principles and frameworks
- Fairness, accountability, transparency
- Human rights impact assessment

## 3. Qualification Requirements by Role
| Role | Required Competencies | Minimum Training Hours/Year |
|------|----------------------|---------------------------|
| AI Developer | Technical + Ethical | 40 hours |
| AI Operator | Technical + Regulatory | 24 hours |
| AI Risk Manager | Regulatory + Ethical | 32 hours |
| AI Governance Lead | All | 48 hours |
| General Staff | Awareness | 4 hours |

## 4. Assessment & Certification
- Annual competence assessment
- Role-based certification renewal every 2 years
- Performance evaluation includes AI competence metrics

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "systemic_risk_mitigation": {
            "name": "Systemic Risk Mitigation Plan (GPAI)",
            "description": "Systemic risk mitigation plan for general-purpose AI (GPAI) models with systemic risk per Art. 51-55, covering risk assessment, model evaluation, incident tracking, and mitigation measures.",
            "content": """## 1. Purpose & Scope
This Systemic Risk Mitigation Plan addresses requirements for general-purpose AI models classified as presenting systemic risk per EU AI Act Art. 51-55.

## 2. Risk Assessment (Art. 51-52)
- Conduct systematic risk assessment of GPAI model capabilities
- Evaluate: autonomous replication, manipulation, cybersecurity risks, health/safety impacts
- Update assessment when model is significantly modified

## 3. Model Evaluation (Art. 55)
- Standardized model evaluations including:
  - Adversarial testing for harmful outputs
  - Bias and fairness across diverse inputs
  - Accuracy and reliability benchmarks
  - Capability assessment (emergent capabilities)
- Independent external evaluation: annual

## 4. Incident Tracking & Reporting
- Track all model-related incidents
- Report serious incidents to AI Office within 7 days
- Maintain incident registry with root cause analysis

## 5. Mitigation Measures
- Implement state-of-the-art safety measures
- Deploy content filtering and guardrails
- Establish usage monitoring
- Implement model access controls
- Maintain fallback/degraded mode procedures

## 6. Documentation & Transparency
- Maintain technical documentation per Annex XI
- Publish detailed summaries of training data per Art. 53
- Report to AI Office on compliance annually

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },
    },

    "nist_ai_rmf": {

        "ai_risk_management": {
            "name": "AI Risk Management Plan",
            "description": "Risk management plan aligned with NIST AI RMF GOVERN and MAP functions, addressing risk identification, assessment, response, and monitoring for AI systems.",
            "content": """## 1. Purpose & Scope
This AI Risk Management Plan establishes risk management processes aligned with the NIST AI Risk Management Framework (AI RMF), covering the GOVERN, MAP, MEASURE, and MANAGE functions.

## 2. Risk Management Framework Mapping
### NIST AI RMF Functions
- **GOVERN**: Establish AI risk management policies, processes, and accountability
- **MAP**: Understand the AI system context and identify risks
- **MEASURE**: Assess and measure AI risks
- **MANAGE**: Treat and respond to AI risks

## 3. Risk Categories
- **Technical Risks**: model accuracy, robustness, reliability, cybersecurity
- **Operational Risks**: deployment failures, integration issues, scalability
- **Ethical Risks**: bias, fairness, transparency, accountability
- **Legal/Regulatory Risks**: compliance gaps, liability, IP infringement
- **Reputational Risks**: public perception, stakeholder trust

## 4. Risk Assessment Process
1. Context establishment (MAP-1): document AI system purpose, deployment context, stakeholders
2. Risk identification (MAP-2): identify credible risks across all categories
3. Risk analysis (MEASURE-1): evaluate likelihood and impact
4. Risk evaluation (MEASURE-2): prioritize risks against risk tolerance
5. Risk treatment (MANAGE-1): select and implement mitigation measures

## 5. Risk Tolerance & Criteria
| Severity | Score | Response |
|----------|-------|----------|
| Critical | 15-25 | Immediate remediation required, escalate to governance board |
| High | 10-14 | Remediation within 30 days |
| Medium | 5-9 | Remediation within 90 days |
| Low | 1-4 | Document and monitor |

## 6. Monitoring & Review
- Continuous monitoring of risk indicators
- Quarterly risk review
- Annual comprehensive risk assessment

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "incident_response": {
            "name": "AI Incident Response Plan",
            "description": "Incident response aligned to NIST AI RMF MANAGE function, covering AI-specific incident types including model degradation, adversarial attacks, bias emergence, and safety failures.",
            "content": """## 1. Purpose & Scope
This AI Incident Response Plan provides procedures for detecting, analyzing, containing, and recovering from AI-specific incidents, aligned with NIST AI RMF MANAGE function and the NIST Incident Response framework.

## 2. AI-Specific Incident Types
- Model degradation or drift
- Adversarial attacks (poisoning, evasion, extraction)
- Bias or fairness emergence
- Safety failure (harmful outputs)
- Data breach via AI system
- Unauthorized model access or extraction
- Systemic failure at scale

## 3. Response Tiers
### Tier 1: Automated Response
- Threshold-based automated containment
- Model rollback to last known good version
- Automatic alerting to AI operations team

### Tier 2: Operational Response
- AI incident response team activation
- Detailed investigation and root cause analysis
- Remediation and verification

### Tier 3: Strategic Response
- Governance board notification
- External stakeholder communication
- Regulatory reporting if required
- Post-incident review and lessons learned

## 4. Team Structure
- AI Incident Commander: [name]
- Technical Lead: [name]
- Communications Lead: [name]
- Legal Counsel: [name]

## 5. Post-Incident Activities
- Root cause analysis report within 5 business days
- Remediation plan with timeline
- Incident response plan update
- Training and awareness if gaps identified

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "continuous_improvement": {
            "name": "AI Continuous Improvement Plan",
            "description": "Continuous improvement process for AI systems per NIST AI RMF, incorporating lessons learned, performance monitoring feedback, and iterative refinement of AI risk management practices.",
            "content": """## 1. Purpose & Scope
This AI Continuous Improvement Plan defines the process for systematically improving AI systems and AI risk management practices over time, aligned with NIST AI RMF's emphasis on iterative risk management.

## 2. Improvement Sources
- Post-incident lessons learned
- Performance monitoring data
- Audit findings and recommendations
- User and stakeholder feedback
- Regulatory and standards updates
- Industry best practice evolution

## 3. Improvement Process
1. **Identify**: Collect improvement opportunities from all sources
2. **Evaluate**: Assess impact, effort, and priority of each opportunity
3. **Plan**: Define improvement actions, owners, and timelines
4. **Implement**: Execute improvements with change management
5. **Verify**: Confirm improvement effectiveness through testing
6. **Standardize**: Update procedures, training, and documentation

## 4. Cadence
- Ongoing: low-effort improvement capture
- Monthly: improvement backlog review
- Quarterly: improvement prioritization
- Annually: comprehensive continuous improvement review

## 5. Metrics
- Number of improvements implemented per quarter
- Mean time to implement improvements
- Improvement effectiveness rating (post-implementation review)

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "change_management": {
            "name": "AI Change Management Plan",
            "description": "Change management process for AI systems covering model updates, retraining, deployment changes, and configuration management with risk assessment at each change.",
            "content": """## 1. Purpose & Scope
This AI Change Management Plan defines the process for managing changes to AI systems, including model updates, retraining, deployment changes, and configuration modifications.

## 2. Change Types
- **Minor**: Model parameter tuning, threshold adjustment, UI changes
- **Moderate**: Model retraining with new data, feature changes, minor architecture updates
- **Major**: Architecture changes, new model family, deployment environment changes
- **Emergency**: Security patch, critical bug fix, incident-driven change

## 3. Change Process
### 3.1 Request
- Submit change request with description, rationale, and risk assessment
- Classify change type (minor/moderate/major/emergency)

### 3.2 Review & Approval
- Minor: AI system owner review and approve
- Moderate: AI governance board review and approve
- Major: Full risk assessment + governance board + stakeholder notification
- Emergency: Fast-track approval with post-implementation review

### 3.3 Testing & Validation
- All changes must pass relevant evaluations before deployment
- Regression testing for accuracy, bias, robustness
- Performance impact assessment

### 3.4 Deployment & Monitoring
- Staged rollout for major changes
- Monitoring period of [N] days post-deployment
- Rollback plan documented

## 4. Documentation
- Change request records
- Test results and evaluation reports
- Approval documentation
- Deployment records

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "stakeholder_communication": {
            "name": "Stakeholder Communication Plan",
            "description": "Communication plan for AI system stakeholders including users, affected persons, regulators, and the public, aligned with NIST AI RMF transparency and communication practices.",
            "content": """## 1. Purpose & Scope
This Stakeholder Communication Plan defines how the organization communicates with stakeholders about AI systems, their capabilities, limitations, and risks.

## 2. Stakeholder Groups
- **Internal**: AI developers, operators, management, affected employees
- **External Users**: system users, customers, partners
- **Affected Persons**: individuals whose rights or safety may be impacted
- **Regulators**: sector regulators, AI Office, data protection authorities
- **Public**: general public, media, civil society organizations

## 3. Communication Types
### 3.1 Transparency Notices
- Clear description of AI system purpose and capabilities
- Known limitations and risks
- Human oversight available
- Contact for questions or complaints

### 3.2 Incident Communications
- Internal notification within 1 hour of serious incident
- Regulatory notification per applicable requirements
- Affected persons notification if harm occurred

### 3.3 Regular Updates
- Quarterly AI governance newsletter
- Annual AI transparency report
- System-specific release notes

## 4. Channels
- Internal: email, intranet, team meetings
- External: website, service documentation, regulatory portals
- Incident: dedicated notification system

## 5. Review & Update
- Communication templates reviewed annually
- Stakeholder feedback collected and incorporated

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "third_party_risk_management": {
            "name": "Third-Party AI Risk Management Plan",
            "description": "Risk management for third-party AI components, vendor AI systems, and external AI services including due diligence, monitoring, and oversight per NIST AI RMF.",
            "content": """## 1. Purpose & Scope
This Third-Party AI Risk Management Plan establishes procedures for identifying, assessing, and managing risks associated with third-party AI components, services, and vendor-provided AI systems.

## 2. Scope of Third-Party AI
- Pre-trained models and foundation models
- AI/ML components in procured software
- Cloud-based AI services and APIs
- AI systems developed by vendors/partners
- Open-source AI components

## 3. Due Diligence Process
### 3.1 Vendor Assessment
- AI vendor questionnaire covering: development practices, testing, bias mitigation, data governance, security
- Review of vendor AI risk management practices
- Independent evaluation of critical third-party AI components

### 3.2 Risk Classification
- Critical: third-party AI directly affecting safety or fundamental rights
- High: third-party AI in core business processes
- Medium: third-party AI in supporting processes
- Low: non-critical third-party AI with limited impact

## 4. Ongoing Monitoring
- Vendor AI system performance monitoring
- Periodic reassessment (annual for critical/high)
- Incident notification requirements in contracts
- Audit rights for critical third-party AI

## 5. Contractual Requirements
- All third-party AI contracts shall include:
  - AI transparency and documentation requirements
  - Performance and accuracy SLAs
  - Incident notification obligations
  - Audit and inspection rights
  - Data protection and privacy requirements

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },
    },

    "iso_42001": {

        "ams_implementation": {
            "name": "AI Management System Implementation Plan",
            "description": "Implementation plan for an AI Management System (AIMS) per ISO 42001 Clause 4-10, covering scope definition, leadership, planning, operation, evaluation, and continual improvement.",
            "content": """## 1. Purpose & Scope
This AI Management System (AIMS) Implementation Plan defines the roadmap for establishing, implementing, maintaining, and continually improving an AI Management System conforming to ISO/IEC 42001.

## 2. Scope Definition (Clause 4)
- Define organizational context
- Identify interested parties and their requirements
- Determine AIMS scope: [list AI systems and processes covered]

## 3. Leadership & Commitment (Clause 5)
- Establish AI governance policy
- Define roles, responsibilities, and authorities
- Establish AI governance board or committee
- Allocate resources for AIMS

## 4. Planning (Clause 6)
- Identify AI-related risks and opportunities
- Establish AI objectives and targets
- Plan changes to the AIMS

## 5. Support (Clause 7)
- Allocate resources for AI system development and operation
- Establish competence requirements and training programs
- Define communication processes internal and external
- Documented information management

## 6. Operation (Clause 8)
- AI system development lifecycle controls
- Risk assessment and treatment processes
- Operational planning and control
- Third-party AI management

## 7. Performance Evaluation (Clause 9)
- Monitoring, measurement, analysis, and evaluation
- Internal audit program
- Management review

## 8. Improvement (Clause 10)
- Nonconformity and corrective action process
- Continual improvement process

## Implementation Timeline
| Phase | Activities | Target Date |
|-------|-----------|-------------|
| 1. Initiation | Scope, policy, team | [date] |
| 2. Planning | Risk assessment, objectives | [date] |
| 3. Implementation | Operational controls, documentation | [date] |
| 4. Evaluation | Internal audit, management review | [date] |
| 5. Certification | External audit, certification | [date] |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "risk_assessment_treatment": {
            "name": "AI Risk Assessment & Treatment Plan",
            "description": "Risk assessment and treatment process per ISO 42001 Clause 6.1 and Annex A, covering AI-specific risk identification, analysis, evaluation, and treatment with a defined risk acceptance criteria.",
            "content": """## 1. Purpose & Scope
This AI Risk Assessment & Treatment Plan defines the process for systematic risk assessment and risk treatment for AI systems within the AI Management System, per ISO 42001 Clause 6.1 and Annex A.

## 2. Risk Assessment Process
### 2.1 Risk Identification
- Identify risks related to AI system development, deployment, and operation
- Consider: AI-specific risks, organizational context, interested party requirements
- Sources: system documentation, incident history, stakeholder input, external intelligence

### 2.2 Risk Analysis
- Assess likelihood and consequence for each risk
- Use defined risk criteria and scales
- Document assumptions and methodology

### 2.3 Risk Evaluation
- Compare risk levels against risk acceptance criteria
- Prioritize risks for treatment
- Identify unacceptable risks requiring immediate action

## 3. Risk Acceptance Criteria
| Risk Level | Score Range | Action Required |
|------------|-------------|-----------------|
| Unacceptable | 15-25 | Immediate treatment, escalation to governance board |
| High | 10-14 | Treatment plan within 30 days |
| Medium | 5-9 | Treatment plan within 90 days |
| Acceptable | 1-4 | Monitor, treat if cost-effective |
| Negligible | 0 | Accept, document rationale |

## 4. Risk Treatment Options
- Avoid: discontinue AI system or use case
- Reduce: implement controls to lower risk
- Transfer: share risk through contracts, insurance
- Accept: formal acceptance with documented rationale

## 5. Treatment Plan
For each risk requiring treatment:
- Treatment option selected
- Control measures to be implemented
- Owner responsible for implementation
- Target completion date
- Verification method

## 6. Residual Risk Acceptance
- All residual risks shall be formally accepted at appropriate authority level
- Document acceptance rationale

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "internal_audit": {
            "name": "AI Internal Audit Plan",
            "description": "Internal audit program for the AI Management System per ISO 42001 Clause 9.2, defining audit criteria, scope, frequency, methods, and auditor competence requirements.",
            "content": """## 1. Purpose & Scope
This AI Internal Audit Plan defines the internal audit program for evaluating the effectiveness of the AI Management System (AIMS) per ISO 42001 Clause 9.2.

## 2. Audit Objectives
- Verify AIMS conforms to ISO 42001 requirements
- Verify AIMS is effectively implemented and maintained
- Identify opportunities for improvement
- Prepare for external certification audits

## 3. Audit Scope
The internal audit shall cover:
- All clauses of ISO 42001 (Clause 4-10)
- Annex A controls applicable to the AI systems in scope
- AI system operational processes and controls
- Documentation and record management

## 4. Audit Frequency & Schedule
- Full AIMS audit: annual
- Targeted audits: quarterly (specific clauses or systems)
- Triggered audits: following significant incidents, major changes, or compliance findings

## 5. Auditor Requirements
- Independence from the area being audited
- Knowledge of ISO 42001 and AI governance
- Understanding of AI system development and operations
- Internal audit training and certification preferred

## 6. Audit Process
1. **Planning**: Define audit objectives, scope, criteria, and team
2. **Execution**: Collect evidence through interviews, document review, observation
3. **Reporting**: Document findings, nonconformities, observations
4. **Follow-up**: Verify corrective actions within defined timelines

## 7. Reporting
- Audit report within 2 weeks of audit completion
- Nonconformities tracked to closure
- Trend analysis across audit cycles

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "management_review": {
            "name": "AI Management Review Plan",
            "description": "Management review process for the AI Management System per ISO 42001 Clause 9.3, defining inputs, agenda, participants, and outputs for periodic top management reviews.",
            "content": """## 1. Purpose & Scope
This AI Management Review Plan defines the process for top management's periodic review of the AI Management System (AIMS) to ensure its continuing suitability, adequacy, effectiveness, and alignment with strategic direction, per ISO 42001 Clause 9.3.

## 2. Review Frequency
- Scheduled: quarterly (minimum annual)
- Triggered: following significant incidents, major organizational changes, or external changes affecting AIMS

## 3. Participants
- Top management / AI governance board
- AIMS management representative
- AI system owners (as relevant)
- Risk management lead
- Internal audit lead
- Legal/compliance representative

## 4. Review Inputs
- Status of actions from previous management reviews
- Changes in external and internal context
- AIMS performance: AI risk assessment status, incident trends, evaluation results
- Audit results: internal and external audit findings
- Feedback from interested parties: user feedback, regulator communications
- Resource adequacy assessment
- Effectiveness of risk treatment measures
- Opportunities for improvement

## 5. Review Outputs
- Decisions and actions related to improvement opportunities
- Decisions on resource needs
- Changes to AIMS policy and objectives
- Decisions on risk acceptance
- Records of the review (minutes, decisions, action items)

## 6. Documentation
- Meeting agenda distributed 1 week prior
- Management review minutes within 5 business days
- Action items tracked in [system name]

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "competence_development": {
            "name": "AI Competence Development Plan",
            "description": "Competence management for AI personnel per ISO 42001 Clause 7.2, including competence identification, training programs, qualifications tracking, and periodic competence evaluation.",
            "content": """## 1. Purpose & Scope
This AI Competence Development Plan defines the competence requirements and development programs for personnel performing work affecting the AI Management System, per ISO 42001 Clause 7.2.

## 2. Competence Identification
For each role affecting AIMS performance, identify:
- Required education, training, and experience
- AI-specific knowledge and skills
- Regulatory and standards knowledge
- Ethical and responsible AI principles

## 3. Role Competence Matrix
| Role | AI Technical | Regulatory | Risk Management | Ethics | ISO 42001 |
|------|:---:|:---:|:---:|:---:|:---:|
| AI Developer | Expert | Working | Working | Working | Aware |
| AI Operator | Working | Aware | Aware | Aware | Aware |
| AI Risk Manager | Working | Expert | Expert | Working | Working |
| AI Governance Lead | Working | Expert | Expert | Expert | Expert |
| Internal Auditor | Aware | Working | Working | Aware | Expert |

## 4. Development Activities
- Formal training courses and certifications
- On-the-job training and mentoring
- Conference and workshop attendance
- Self-study and online learning
- Cross-functional project participation

## 5. Competence Evaluation
- Annual competence assessment against role requirements
- Evaluation methods: tests, practical assessments, performance reviews
- Gap analysis and individual development plans

## 6. Records
- Competence records maintained for all AI personnel
- Training completion records
- Certifications and qualifications
- Review period: annual update

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },

        "continual_improvement": {
            "name": "AI Continual Improvement Plan",
            "description": "Continual improvement process for the AI Management System per ISO 42001 Clause 10.1, addressing nonconformities, corrective actions, and systematic improvement of AI processes and controls.",
            "content": """## 1. Purpose & Scope
This AI Continual Improvement Plan defines the process for identifying and implementing improvements to the AI Management System (AIMS) and associated AI systems, per ISO 42001 Clause 10.1.

## 2. Improvement Sources
- Nonconformities and corrective actions (Clause 10.1)
- Internal and external audit findings
- Management review decisions
- Performance monitoring and measurement data
- Incident and near-miss analysis
- Stakeholder feedback
- Changes in regulatory requirements
- Industry best practice evolution

## 3. Nonconformity & Corrective Action Process
1. **Identification**: Detect and document nonconformity
2. **Evaluation**: Assess severity and impact
3. **Root Cause Analysis**: Determine underlying cause
4. **Corrective Action**: Define action to eliminate root cause
5. **Implementation**: Execute corrective action
6. **Verification**: Confirm effectiveness of corrective action
7. **Closure**: Document and close

## 4. Improvement Categories
- **Immediate**: Corrective actions for identified nonconformities
- **Preventive**: Actions to prevent potential nonconformities
- **Enhancement**: Improvements to effectiveness and efficiency
- **Innovation**: Adoption of new methods, tools, or practices

## 5. Metrics & Targets
- Time to close nonconformities: target < 30 days
- Recurrence rate: target < 5%
- Improvement suggestions implemented per quarter: target > 3
- AIMS maturity score improvement: target > 10% annually

## 6. Improvement Register
All improvement opportunities tracked in [system name] with:
- Description
- Source
- Priority (low/medium/high/critical)
- Assigned owner
- Target date
- Status

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | [date] | [author] | Initial plan""",
        },
    },
}
