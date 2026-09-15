_CONTENT_AUP = """# Acceptable Use Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

The purpose of this Acceptable Use Policy (AUP) is to establish the rules and expectations governing the use of {{ORG_NAME}} information systems, networks, applications, and data.

## 2. Scope

This policy applies to all employees, contractors, consultants, temporary workers, and third-party users.

## 3. Authorized Use

Information systems are provided for business purposes. Incidental personal use is permitted provided it does not interfere with job performance or violate any other policy.

## 4. Prohibited Activities

- Accessing, storing, or transmitting illegal content
- Intentionally introducing malware or malicious code
- Circumventing security controls
- Sharing authentication credentials
- Downloading or installing unapproved software

## 5. Enforcement

Violations may result in disciplinary action up to and including termination. Suspected violations must be reported to the Security Team immediately.

## 6. Review

This policy is reviewed and updated at least annually."""

_CONTENT_ACP = """# Access Control Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Access Control Policy establishes the framework for managing logical and physical access to {{ORG_NAME}} information systems and data.

## 2. Scope

This policy applies to all information systems, applications, databases, networks, and physical facilities that process, store, or transmit company or customer data.

## 3. Identity and Access Management

- Every user must have a unique identifier for accountability
- Shared accounts are prohibited unless technically unavoidable and approved
- Service accounts must be documented and reviewed quarterly
- All access must be authenticated before granting system access

## 4. Least Privilege

Access rights must be limited to the minimum necessary. Privileged access must be:
- Granted only with management approval
- Reviewed quarterly
- Logged and monitored
- Revoked immediately upon role change or termination

## 5. Provisioning and Deprovisioning

- Access requests must be submitted with manager approval
- Standard roles and access profiles are pre-defined
- Access is revoked within 24 hours of termination notification
- Quarterly access reviews are conducted for all systems

## 6. CUI Access Requirements

Access to Controlled Unclassified Information (CUI) must be:
- Limited to personnel with a valid need-to-know
- Granted via formal access request with manager approval
- Reviewed quarterly for all systems within the CUI boundary
- Immediately revoked upon role change or termination
- Monitored and logged for all CUI repositories

All privileged access to CUI systems requires multi-factor authentication and Just-in-Time (JIT) elevation.

## 7. Review

This policy is reviewed and updated at least annually."""

_CONTENT_PAP = """# Identification and Authentication Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Identification and Authentication Policy defines the standards for identifying users, authenticating identities, and managing credentials for all {{ORG_NAME}} information systems in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all users, systems, services, and devices that access {{ORG_NAME}} information resources.

## 3. Identification Requirements

Every user must have a unique identifier for accountability. Shared or group accounts are prohibited unless technically unavoidable and approved by the Security Officer.

## 4. Authentication Requirements

- Minimum password length of 12 characters
- Must contain characters from at least three of: uppercase, lowercase, numbers, special characters
- Must not contain the user's name or common dictionary words
- Must not be reused (minimum of 10 previous passwords remembered)
- Passwords must be changed upon suspected compromise

## 5. Multi-Factor Authentication (MFA)

MFA is required for:
- All remote access to company systems
- All administrative and privileged accounts
- Cloud service provider consoles
- Access to Controlled Unclassified Information (CUI)

Acceptable MFA methods: TOTP authenticator apps, hardware security keys, push notification authentication.

## 6. Account Management

- Accounts locked after 5 consecutive failed login attempts
- Lockout duration is 15 minutes minimum
- Session timeout after 30 minutes of inactivity
- API keys and tokens must be rotated every 90 days
- Inactive accounts disabled after 30 days

## 7. Credential Storage

Passwords must be stored using salted, one-way hashing (bcrypt, argon2, or PBKDF2). Plain-text storage is prohibited. Cryptographic keys must be protected in accordance with NIST SP 800-57.

## 8. CMMC Authentication Requirements

For systems processing Controlled Unclassified Information (CUI):
- MFA is required for all remote access to CUI systems
- MFA is required for all administrative and privileged accounts
- FIPS 140-2 validated MFA methods must be used
- Password policies must align with NIST SP 800-63B guidelines
- Service accounts and non-person entities must use certificate-based authentication

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_CMP = """# Configuration Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Configuration Management Policy establishes a structured process for establishing baseline configurations, managing changes to {{ORG_NAME}} production systems, applications, and infrastructure, and ensuring configuration integrity.

## 2. Scope

This policy applies to all changes affecting production software, cloud infrastructure, database schemas, security controls, and CI/CD pipelines.

## 3. Change Classification

- **Standard:** Pre-approved, low-risk changes following documented procedures
- **Normal:** Changes requiring review and approval before implementation
- **Emergency:** Critical changes to resolve incidents; requires post-implementation review within 24 hours

## 4. Change Request Requirements

All changes must be documented with description, justification, impact assessment, rollback plan, testing performed, and risk assessment.

## 5. Approval

- Peer review required for all code changes
- Manager approval required for normal changes
- Security Team approval required for changes affecting security controls
- Changes must not be self-approved

## 6. Testing

All changes must be tested in a non-production environment before deployment to production.

## 7. Baseline Configurations

Each system type must have a documented baseline configuration that includes:
- Operating system hardening standard
- Approved software inventory
- Security tool requirements (AV/EDR, logging)
- Firewall and network configuration
- User access restrictions

Baselines must be reviewed and updated annually or upon significant system change. Deviations from baseline require documented approval via the change management process.

## 8. Review

This policy is reviewed and updated at least annually."""

_CONTENT_IRP = """# Incident Response Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Incident Response Policy establishes the framework for detecting, responding to, containing, eradicating, and recovering from security incidents affecting {{ORG_NAME}} information systems that process, store, or transmit Controlled Unclassified Information (CUI) in accordance with NIST SP 800-171 and NIST SP 800-61.

## 2. Scope

This policy applies to all security incidents involving {{ORG_NAME}} information systems, networks, applications, and data including CUI. It covers incident detection, response coordination, containment actions, evidence preservation, reporting obligations, and post-incident review for all personnel, contractors, and third-party service providers.

## 3. Incident Response Team

The Incident Response Team (IRT) is responsible for executing this policy. IRT roles include: Incident Commander who leads response coordination, Security Analysts who perform technical investigation and analysis, Communications Lead who manages internal and external notifications, Legal Counsel who advises on regulatory and contractual obligations, and Executive Sponsor who provides organizational authority for response actions. The IRT must be available 24/7 with documented escalation procedures.

## 4. Incident Classification and Response Timelines

Incidents are classified by severity with associated response time requirements:

- **Critical — Response within 15 minutes, containment within 4 hours:** Active data breach involving CUI, ransomware affecting production systems, confirmed system compromise with data exfiltration, or active threat actor in the environment.
- **High — Response within 1 hour, containment within 8 hours:** Unauthorized access to systems containing CUI, successful credential compromise, denial of service affecting CUI availability, or malware on systems within the CUI boundary.
- **Medium — Response within 4 hours, containment within 24 hours:** Malware on non-CUI endpoint, suspicious login activity from external sources, policy violation involving CUI handling, or unauthorized configuration change.
- **Low — Response within 24 hours:** Failed login attempts exceeding threshold, port scans or reconnaissance activity, or minor policy violations without data exposure.

## 5. Incident Detection and Reporting

All personnel must report suspected security incidents immediately to the IRT via designated reporting channels. Detection mechanisms include SIEM alerting with correlation rules, endpoint detection and response monitoring, intrusion detection and prevention system alerts, file integrity monitoring, user and entity behavior analytics, and automated vulnerability scan findings. The IRT must continuously monitor detection systems during business hours and maintain on-call monitoring coverage.

## 6. Response Procedures

The incident response lifecycle follows the NIST SP 800-61 framework:

**Identification:** Verify the incident, determine scope and affected systems, assess initial severity classification, and document the incident in the incident tracking system with a unique incident identifier. Collect initial indicators of compromise including timestamps, affected hosts, user accounts, and network connections.

**Containment:** Implement short-term containment to prevent further damage including network isolation of affected systems, disabling compromised accounts, blocking malicious IP addresses and domains, and revoking compromised credentials. Long-term containment includes applying temporary compensating controls while preparing eradication. Preserve forensic evidence before any destructive containment actions.

**Eradication:** Identify root cause through forensic analysis. Remove malware, backdoors, and attacker tools from all affected systems. Apply security patches to close exploited vulnerabilities. Reset all affected credentials and rotate cryptographic keys. Validate eradication through independent verification scanning.

**Recovery:** Restore affected systems from known-good backups after verifying backup integrity. Reconnect systems to the network only after confirming eradication and applying all required security controls. Monitor restored systems for a minimum of 72 hours for signs of re-infection or persistence. Return systems to normal operations with documented sign-off from the Incident Commander.

## 7. DoD Reporting Requirements

For incidents involving CUI under DoD contracts, the following requirements must be met: submit incident report to the DoD via the DIBNet portal (dibnet.dod.mil) within 72 hours of discovery, notify the Contracting Officer and Contracting Officer Representative immediately upon confirmation of a CUI-related incident, preserve all forensic evidence including system logs, network captures, disk images, and memory dumps with chain of custody documentation, cooperate fully with DoD and C3PAO investigation and remediation efforts, and submit a comprehensive after-action report within 30 days of incident closure.

## 8. Evidence Preservation

Forensic evidence must be collected and preserved with strict chain of custody procedures. Evidence types include system and application logs, network flow data and packet captures, disk and memory images, malware samples, and relevant configuration files. Evidence must be stored on write-once media or immutable storage with access restricted to authorized IRT personnel. Chain of custody must document each transfer, access, and analysis with timestamps and personnel identification. Evidence must be retained for a minimum of one year after incident closure or longer if required by legal or contractual obligations.

## 9. Communications Plan

Internal communications must notify executive management within one hour of confirmed Critical or High severity incidents. Affected system owners and data custodians must be notified within the incident response timeline for their severity level. External communications including customer notifications, regulatory filings, and law enforcement engagement must be coordinated through Legal Counsel. All external communications must be approved by the Communications Lead and Executive Sponsor. Media inquiries must be directed to authorized spokespersons only.

## 10. Incident Response Testing

The Incident Response Plan must be tested at least annually through tabletop exercises simulating realistic incident scenarios including CUI compromise, ransomware, and insider threats. A technical recovery exercise must be conducted annually to validate containment and recovery procedures. Testing results must be documented including identified gaps, remediation actions, and responsible parties. All gaps must be remediated within 90 days of identification.

## 11. After-Action Review and Lessons Learned

Within five business days of incident closure, the IRT must conduct a post-incident review documenting incident timeline, root cause analysis, response effectiveness, control gaps identified, evidence collected, containment and eradication actions taken, recovery validation results, and recommendations for improvement. After-action review findings must be tracked to remediation in the POA&M and risk register. Lessons learned must be incorporated into updated incident response procedures and shared with relevant teams.

## 12. Enforcement

Violations of this policy including failure to report suspected incidents, unauthorized disclosure of incident information, or interference with incident response activities may result in disciplinary action up to and including termination and may be subject to legal action.

## 13. Review

This policy is reviewed and updated at least annually and following any Critical or High severity incident."""

_CONTENT_VMP = """# Vendor Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Vendor Management Policy establishes the framework for assessing, onboarding, monitoring, and offboarding third-party vendors.

## 2. Vendor Risk Classification

- **High Risk:** Access to customer data, PII, production systems
- **Medium Risk:** Access to internal systems, non-sensitive data
- **Low Risk:** No data access

## 3. Due Diligence

Vendors must be assessed on: security (SOC 2, ISO 27001, or questionnaire), privacy practices, compliance certifications, financial stability, and incident history.

## 4. Contractual Requirements

Contracts must include: data protection clauses, security requirements, incident notification (within 24 hours), right to audit, and data deletion upon termination.

## 5. Ongoing Monitoring

High-risk vendors reviewed annually: updated SOC 2 reports, security posture changes, and contract compliance.

## 6. Review

This policy is reviewed and updated at least annually."""

_CONTENT_RAP = """# Risk Assessment Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Risk Assessment Policy establishes the methodology and requirements for identifying, analyzing, evaluating, and treating risks to {{ORG_NAME}} operations, assets, and individuals in accordance with NIST SP 800-171 and NIST SP 800-30.

## 2. Scope

This policy applies to all organizational information systems, applications, network infrastructure, facilities, and third-party services that process, store, or transmit CUI. It covers risk identification, vulnerability scanning, and remediation management.

## 3. Risk Assessment Methodology

Risk assessments must follow the NIST SP 800-30 framework. Each risk is evaluated based on threat identification, vulnerability analysis, likelihood of occurrence, and impact to confidentiality, integrity, and availability. Risk is scored as the product of likelihood and impact using the four-tier scale: Low, Medium, High, and Critical. Both inherent risk and residual risk must be calculated for each identified risk.

## 4. Risk Assessment Frequency and Triggers

Comprehensive risk assessments must be conducted at least annually. Additional assessments must be triggered by significant changes to the information system, deployment of new systems processing CUI, major changes to the threat landscape, significant security incidents, and changes to regulatory requirements. Targeted risk assessments must be conducted for new projects, technologies, or third-party integrations involving CUI.

## 5. Vulnerability Scanning

Vulnerability scans must be conducted monthly on all systems within the CUI boundary using approved scanning tools. Scans must cover operating systems, applications, databases, network devices, and web applications. Authenticated scans must be used wherever feasible for deeper inspection. Scan results must be documented, prioritized by severity, and retained for a minimum of one year. Critical and high-severity findings must trigger immediate remediation actions.

## 6. Vulnerability Remediation

Vulnerabilities must be remediated within the following timeframes based on severity: Critical — within 48 hours, High — within 7 days, Medium — within 30 days, Low — within 90 days. Remediation must be verified through re-scanning. Where immediate remediation is not feasible, compensating controls must be documented and risk must be formally accepted by the risk owner. Vulnerability remediation must be tracked in the risk register with status, responsible party, and target completion date.

## 7. Risk Treatment and Acceptance

Risk treatment options include Mitigate through implementation of security controls, Transfer through insurance or contractual arrangements, Avoid by discontinuing the activity, and Accept when mitigation costs exceed potential impact. Risk acceptance of High or Critical risks requires formal approval from senior management with documented justification. All accepted risks must be reviewed at least quarterly.

## 8. Risk Register and Reporting

The risk register must document risk description, threat source, vulnerability, likelihood and impact scores, risk score, risk owner, treatment strategy, mitigation controls, implementation status, and review dates. The risk register must be reviewed quarterly. High and Critical risks must be reviewed monthly. Summary risk reports must be provided to senior management semi-annually.

## 9. Enforcement

Violations of this policy including failure to conduct required assessments, failure to remediate vulnerabilities within designated timeframes, or unauthorized acceptance of High or Critical risks may result in disciplinary action up to and including termination.

## 10. Review

This policy is reviewed and updated at least annually."""

_CONTENT_DCP = """# Data Classification Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Data Classification Policy establishes the framework for classifying and protecting information assets based on their sensitivity.

## 2. Classification Levels

- **Public:** Approved for public release; no adverse impact
- **Internal:** Internal use only; minor reputational risk
- **Confidential:** Sensitive business information; significant harm if disclosed
- **Restricted:** Highly sensitive, regulated data; severe harm if disclosed

## 3. Handling Requirements

- Restricted data must be encrypted at rest (AES-256) and in transit (TLS 1.2+)
- Confidential data stored on company-managed systems with access controls
- Data disposal follows NIST SP 800-88 guidelines
- Restricted documents labeled "RESTRICTED"

## 4. Data Retention

Data retained per Data Retention Schedule; data no longer needed must be securely disposed.

## 5. Review

This policy is reviewed and updated at least annually."""

_CONTENT_BCDR = """# Business Continuity and Disaster Recovery Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This BCDR Policy defines requirements for maintaining availability and recovering from disruptive events.

## 2. Business Impact Analysis (BIA)

Conducted annually to identify: critical functions, RTO (Recovery Time Objective), RPO (Recovery Point Objective), and resource requirements.

## 3. Backup Requirements

- Daily backups for all production data
- Geographically separate storage
- Restore drills conducted monthly

## 4. Testing

- BCP tabletop exercises conducted annually
- DRP technical recovery tests conducted annually
- Gaps remediated within 90 days

## 5. Review

This policy is reviewed and updated at least annually."""

_CONTENT_COCE = """# Awareness and Training Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Awareness and Training Policy establishes the requirements for security awareness and role-based training for all {{ORG_NAME}} personnel in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all employees, contractors, and third-party users with access to {{ORG_NAME}} information systems and Controlled Unclassified Information (CUI).

## 3. Security Awareness Training

- All personnel must complete security awareness training upon hire and annually thereafter
- Training must cover: insider threat recognition, social engineering and phishing awareness, CUI handling requirements per NIST SP 800-171, data protection and privacy, and incident reporting procedures
- Completion must be documented and tracked in the training management system

## 4. Role-Based Training

Personnel with significant security roles must receive additional role-based training on: secure configuration practices, incident response procedures, risk management fundamentals, and audit log review and monitoring

## 5. Training Records

Records of all training must be maintained for a minimum of 3 years. Records must include: participant name, training date, training topics, and completion status. Management must review training compliance quarterly.

## 6. Review

This policy is reviewed and updated at least annually."""

_CONTENT_AI_ETHICS = """# AI Ethics and Governance Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose and Context

The rapid growth of powerful, user-friendly AI tools has led to widespread use across many tasks. People rely on chatbots (e.g., ChatGPT, Gemini) for questions and summaries, use generative tools (e.g., DALL·E, Midjourney, Veo) for creating content, and coding assistants (e.g., Copilot, Claude) to develop or debug software. While these tools offer significant benefits, they also introduce specific risks. Users must understand these risks and apply AI responsibly. This policy outlines the principles and rules for acceptable use of AI systems at {{ORG_NAME}}.

## 2. Scope

This policy applies to all {{ORG_NAME}} employees and to external contractors working with {{ORG_NAME}} staff.

It covers the use of any public or third-party AI system by all departments and on all {{ORG_NAME}} information assets. It does not apply to formally approved or internally developed AI systems that have their own usage guidelines.

## 3. Acceptable Use Principles

- **Human judgment:** AI tools are not a substitute for human judgment or creativity. Most AI systems generate outputs using statistical patterns from previously ingested data. For example, employment or promotion decisions must never be made solely by AI.
- **Verify output:** Generative systems may produce hallucinations — plausible but incorrect or fabricated information — or rely on outdated, biased, or inaccurate training data. Always verify AI-generated content for correctness, appropriateness, and potential copyright issues.
- **No copying or infringement:** Ensure the output does not copy or infringe existing work. Check that AI-generated content does not closely resemble the work of living artists, copyrighted images, or text from a single identifiable source. Do not ask AI systems to copy, imitate, or modify protected works.
- **No confidential information:** Many AI providers store and reuse input data for model improvement. Do not enter personal data, confidential business information, passwords, configuration files, or any other sensitive details. Assume that anything provided to a public AI service could become publicly accessible.
- **Transparency:** Clearly disclose when AI has contributed to your work. Do not pass off AI-generated content as solely your own. Certain uses, such as public-facing customer support chatbots, may require disclosure under the EU AI Act. If you use AI to generate content, note that AI was used.

## 4. Privacy and the AI Act

Personal data must not be shared with external AI tools or services. Remove all personal data from any document before providing it as input to an AI system. Data protection laws, such as the GDPR, apply fully to any data used with AI systems. Employees must ensure that personal data is used only for the purposes for which it was originally collected.

If you introduce a new AI-powered feature, this may constitute a new use of personal data. In such cases, a Data Protection Impact Assessment (DPIA) may be required. Contact the Information Security team when planning new or innovative uses of personal data so they can determine whether a DPIA is necessary. The team will also evaluate whether the new use is high-risk or restricted under the EU AI Act, and whether additional impact assessments are needed.

If the AI Act applies, the Information Security team will consider, among other things:

- Human oversight of any significant decisions made by AI
- Risks of bias, discrimination, or unfair outcomes
- Logging, monitoring, and auditability requirements
- Transparency obligations, e.g., informing users when they are interacting with a chatbot rather than a human

## 5. AI and Coding

AI tools may be used to support software development tasks, just like other external resources (e.g., search engines or technical websites). However, developers must carefully review all AI-generated code to ensure that it does not introduce security risks such as backdoors or unexpected calls to external services. Developers must also test the code to confirm that it functions as intended. AI-generated code can contain bugs or vulnerabilities, just like any other code.

## 6. Approved AI Services

{{ORG_NAME}} will carefully assess all suppliers, including AI service providers, before their services are used. If you require an AI service, contact the Information Security team and specify which service you need and which supplier you are considering. The team will use the existing supplier review process to determine whether the supplier is suitable and reliable. The review will consider:

- **Supplier reliability**, including relevant certifications. ISO 27001 is preferred for EU-based suppliers, while SOC 2 is acceptable for US-based suppliers.
- **GDPR compliance** if personal data will be shared. This requires either an EU-based supplier or a US-based supplier with a strong privacy policy and a Data Processing Addendum (DPA) that mentions Standard Contractual Clauses (SCCs).
- **Cloud-related risks** if the AI provider is a cloud service, including safe use, maintenance, availability, and exit strategies.

If the planned use of AI represents a major change, {{ORG_NAME}} will create a project plan and assign a project manager.

Employees must not independently introduce AI services into {{ORG_NAME}} operations. Without explicit approval, AI tools may only be used for personal learning or experimentation, and only with non-sensitive data.

## 7. Training and Awareness

{{ORG_NAME}} will regularly conduct surveys to understand which AI tools employees use and for what purposes. These tools and their use cases will be evaluated for security and privacy risks. Approved tools and permitted use cases will be added to a company whitelist, and licenses will be obtained where necessary.

The Security Officer will include AI awareness in the company's information security awareness training and ensure that this policy is accessible to all staff. Additional, role-specific training will be provided to employees who use, oversee, or implement AI systems when relevant.

## 8. Guidelines for Assessing the Use of AI

Product owners should consider the following when deciding whether to use AI, and evaluate these aspects in any AI-related project plan:

- **Transparency / Explainability / Auditability:** make information in and about AI systems understandable to non-experts and useful for audits.
- **Safety / Security:** protect AI systems against external attacks, including safety mechanisms throughout their lifecycle, and ensure they function appropriately even under adverse conditions. This includes regular risk assessments and adherence to data security regulations.
- **Robustness / Reliability:** AI systems must operate reliably, performing consistently according to their intended purposes while minimizing risks, and display technological robustness to misuse or external attacks.
- **Justice / Equity / Fairness / Non-discrimination:** AI systems must be non-discriminatory and ensure bias mitigation; individuals should be subject to the same fair algorithmic treatment regardless of their characteristics.
- **Privacy:** prioritize the individual's right to choose if and to what extent they want to expose themselves, and relate to data protection concepts such as anonymity and informed consent.
- **Accountability / Liability:** define roles and responsibilities for adherence to both company policies and law, and hold actors accountable for impacts caused by the development or use of AI technologies.

## 9. Review

This policy is reviewed and updated at least annually.

## Appendix: References

This policy is inspired by:

- European AI Alliance, "Writing an Organizational AI Policy" (https://futurium.ec.europa.eu/en/european-ai-alliance/document/writingorganizational-ai-policy-first-step-towards-effective-ai-governance)
- Ethics Guidelines for Trustworthy AI (https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-trustworthy-ai)
- GDPR Article 5 — principles relating to processing of personal data (purpose limitation, integrity, confidentiality)
- GDPR Article 6 — lawfulness of processing: a legal basis is required before feeding personal data into any AI or analytics system
- GDPR Articles 12-14 — information to data subjects: be transparent about use of AI with users
- GDPR Article 28 — use of processors: AI services need to be approved by IT and Legal due to potential need for DPAs or data transfer requirements
- EU AI Act Article 50 — transparency obligations: users must be informed when interacting with a chatbot
- EU AI Act Article 6 (Annex III) — when an AI system can be high-risk: requires review by IT or the relevant department

This policy implements parts of the requirements of the following ISO/IEC 27001:2022 Annex A controls: A.5.10 Acceptable use of information and other associated assets, A.5.14 Information transfer, A.5.23 Information security for use of cloud services, A.5.34 Privacy and protection of personally identifiable information (PII), A.8.25 Secure development life cycle, A.8.26 Application security requirements, A.8.28 Secure coding.

Template adapted from the ICT Institute free template kit (https://ictinstitute.nl/free-templates/), used under Creative Commons Attribution 4.0 (CC-BY)."""

_CONTENT_SYSTEM_SEC = """# System Description

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This System Description defines the security posture, controls, and architecture of {{ORG_NAME}} information systems.

## 2. System Description

{{ORG_NAME}} operates information systems that process, store, and transmit business and customer data. Systems are cloud-based with infrastructure-as-code deployment.

## 3. Security Controls

Security controls are implemented across the following domains:
- **Access Control:** Least privilege, MFA, role-based access
- **Awareness and Training:** Annual security awareness training
- **Audit and Accountability:** Centralized logging, audit trail retention
- **Configuration Management:** Baseline configurations, change management
- **Incident Response:** Documented IR plan with annual testing
- **Risk Assessment:** Annual risk assessments with quarterly reviews

## 4. Continuous Monitoring

System security is monitored through:
- Vulnerability scanning
- Security information and event management (SIEM)
- Penetration testing (annual)
- Configuration compliance monitoring

## 5. Review

This SSP is reviewed and updated at least annually or upon significant system change."""

_CONTENT_LMP = """# Audit and Accountability Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Audit and Accountability Policy defines the requirements for logging system events, monitoring security controls, conducting audits, and responding to alerts at {{ORG_NAME}}.

## 2. Scope

This policy applies to all production systems, applications, network devices, cloud infrastructure, and security tools.

## 3. Logging Requirements

The following events must be logged: authentication events, privileged account activity, system errors, data access events, configuration changes, network connections, and service start/stop events. Each log entry must include timestamp, source system, user identifier, event type, and outcome.

## 4. Log Retention

Security logs must be retained for a minimum of 12 months in immutable storage. Archived logs must be available for retrieval within 24 hours.

## 5. Monitoring and Alerting

Continuous monitoring must cover failed login attempts, privileged account anomalies, unauthorized configuration changes, malware detection, data egress, and system resource anomalies. Alert response SLAs: Critical 15 minutes, High 1 hour, Medium 4 hours.

## 6. Log Review

Security logs must be reviewed daily for critical systems. Access logs must be reviewed weekly. A formal review log must be maintained documenting date, reviewer, and findings.

## 7. Enforcement

Failure to enable required logging or respond to alerts within SLA must be reported. Repeated violations may result in disciplinary action.

## 8. Review

This policy is reviewed and updated at least annually."""

_CONTENT_BRP = """# Backup and Recovery Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Backup and Recovery Policy establishes the requirements for creating, storing, and testing backups of {{ORG_NAME}} data and system configurations.

## 2. Scope

This policy applies to all production data, databases, system configurations, and infrastructure-as-code definitions.

## 3. Backup Frequency

Production databases must be backed up at least daily. System configurations must be version-controlled. Application source code must be backed up continuously.

## 4. Retention Requirements

Daily backups retained for 30 days, weekly for 12 weeks, monthly for 12 months, annual for 7 years. Backups containing customer data must meet contractual retention requirements.

## 5. Storage and Encryption

Backups must be stored in a geographically separate location with AES-256 encryption at rest and TLS 1.2+ in transit. Access must be restricted to authorized personnel.

## 6. Backup Testing

Backup integrity must be verified within 24 hours. Full restore drills must be conducted at least quarterly. Results must be documented and reviewed by management.

## 7. Recovery Procedures

Recovery procedures must be documented for each critical system with step-by-step restore instructions.

## 8. Enforcement

Backup failures must be investigated and resolved within 24 hours. Data loss due to failure to follow this policy may result in disciplinary action.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_SIIP = """# System and Information Integrity Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This System and Information Integrity Policy defines requirements for identifying, evaluating, and remediating vulnerabilities across {{ORG_NAME}} information systems in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all servers, workstations, network devices, cloud resources, applications, and databases that process, store, or transmit CUI.

## 3. Vulnerability Scanning

All systems must be scanned for vulnerabilities at least monthly. Critical and high-severity findings must be reported within 24 hours of scan completion. Scans must cover all network-accessible ports and services.

## 4. Patch Management

Critical security patches must be applied within 14 days. High-severity patches within 30 days. Medium within 60 days. Emergency patches may be applied outside the change management window with post-implementation review.

## 5. Malicious Code Protection

Anti-malware software must be deployed on all endpoints and servers. Signature updates must be applied automatically. Periodic scans must be conducted at least weekly.

## 6. System Monitoring

Security-relevant events must be monitored in near real-time. Alerts must be configured for: unauthorized access attempts, malware detection, configuration changes, and anomalous user behavior.

## 7. Exceptions

If a patch cannot be applied within the required timeframe, compensating controls must be documented and approved by the Security Team. Exceptions must be reviewed quarterly.

## 8. Review

This policy is reviewed and updated at least annually."""

_CONTENT_NSP = """# Network Security Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines requirements for securing {{ORG_NAME}} networks, including segmentation, encryption, and boundary protection.

## 2. Scope

This policy applies to all network infrastructure, including firewalls, routers, switches, wireless access points, and cloud networking.

## 3. Network Segmentation

Production networks must be logically or physically separated from non-production networks. Sensitive data must reside on isolated network segments.

## 4. Boundary Protection

All network boundaries must be protected by firewalls or equivalent controls. Inbound and outbound traffic must be restricted to business-necessary ports.

## 5. Encryption

Data in transit across public networks must be encrypted using TLS 1.2+ or equivalent. Wireless networks must use WPA2-Enterprise or stronger.

## 6. CUI Boundary Protection

Network segmentation must separate CUI processing environments from corporate IT and guest networks. All CUI traffic must be encrypted in transit using FIPS 140-2 validated cryptographic modules. Default-deny firewall policies must be applied at all CUI boundary points.

## 7. FIPS 140-2 Cryptography

All cryptographic modules used to protect CUI must be FIPS 140-2 or FIPS 140-3 validated. This includes encryption for data at rest, data in transit, remote access, and wireless communications. Valid NIST certificates must be maintained and available for audit.

## 8. External Connections

All external system interconnections must be formally authorized via an Interconnection Security Agreement (ISA). Third-party connections to CUI systems must route through managed access control points with full audit logging.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_PSP = """# Physical Protection Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Physical Protection Policy establishes requirements for controlling physical access to {{ORG_NAME}} facilities, equipment, and systems that process, store, or transmit Controlled Unclassified Information (CUI) in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all {{ORG_NAME}} facilities housing information systems including offices, data centers, server rooms, wiring closets, and controlled-access areas that contain CUI or critical information system components.

## 3. Physical Access Authorizations

Physical access to facilities containing CUI must be authorized based on job role and business need. A formal access authorization process must validate the individual's identity, role requirements, and security clearance status before granting access. Access authorizations must be reviewed and recertified at least quarterly. Access lists must be maintained and updated promptly upon role changes or personnel departures.

## 4. Physical Access Monitoring

Facilities must have physical access control systems including badge readers, biometric scanners, mantrap entrances, or locked entry points. Physical access events must be logged with timestamps, individual identity, and access point. Access logs must be retained for a minimum of 90 days. Security cameras must monitor entry points and sensitive areas with recording retention of at least 30 days.

## 5. Visitor Access Controls

All visitors must be registered, authenticated, and issued temporary visitor badges before entry. Visitors must be escorted by authorized personnel at all times while in controlled areas. Visitor access must be logged including name, organization, purpose, date, time in/out, and escort identity. Visitor logs must be retained for a minimum of one year. Unauthorized visitors are prohibited and must be reported to security immediately.

## 6. Physical Access Logs

Physical access logs must be maintained for all entry and exit events at controlled access points. Logs must include individual identity, access point location, date, time, and access outcome (granted/denied). Access logs must be reviewed regularly for anomalous activity including unauthorized access attempts, after-hours access, and access pattern deviations. Physical access logs must be retained for a minimum of one year.

## 7. Physical Access Devices

Physical access devices including keycards, badges, fobs, and biometric credentials must be inventoried and tracked. Lost, stolen, or unreturned access devices must be immediately deactivated and reported. Access device inventory must be reconciled quarterly. Access devices must not be shared, loaned, or used by unauthorized individuals.

## 8. Alternative Work Site Security

Personnel working at alternative work sites including home offices and remote locations must implement physical security controls to protect organizational information systems and CUI. Controls must include securing devices when unattended, preventing unauthorized viewing of CUI, and using privacy screens in public areas. CUI printed at alternative work sites must be secured when not in use and disposed of properly.

## 9. Enforcement

Violations of this policy including unauthorized facility access, circumvention of physical controls, or failure to report security incidents may result in disciplinary action up to and including termination and legal prosecution.

## 10. Review

This policy is reviewed and updated at least annually."""

_CONTENT_MPP = """# Media Protection Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Media Protection Policy defines requirements for accessing, marking, handling, storing, transporting, sanitizing, and disposing of digital and physical media containing Controlled Unclassified Information (CUI) in accordance with NIST SP 800-171 and CMMC Level 2 requirements.

## 2. Scope

This policy applies to all digital and physical media including hard drives, solid-state drives, backup tapes, optical discs, USB drives, removable storage devices, and printed materials that contain CUI or organizational sensitive data. This policy covers media throughout its lifecycle from acquisition through disposal.

## 3. Media Access Controls

Access to digital and physical media containing CUI must be restricted to authorized personnel with a valid business need. Media must be stored in secured, access-controlled areas when not in use. Access to media must be logged and reviewed quarterly. Media containing CUI must be physically secured in locked cabinets, safes, or controlled-access rooms.

## 4. Media Marking and Classification

All digital and physical media containing CUI must be externally marked with appropriate CUI designation labels in accordance with DOD/DISA CUI marking requirements. Media containing different classification levels must be labeled at the highest classification level of data stored. System media containing CUI must have the CUI designation visible on the exterior of the media or its storage container.

## 5. Media Storage and Transport

Media containing CUI must be stored in physically secure locations with access controls, environmental monitoring, and fire protection. When transported outside of controlled facilities, media containing CUI must be encrypted using FIPS 140-2 validated modules, transported by authorized personnel using tamper-evident packaging, and logged with chain-of-custody documentation. Unencrypted CUI on media being transported is prohibited.

## 6. Media Sanitization

Media must be sanitized before reuse, release, or disposal using methods appropriate for the classification level of stored data. Sanitization must follow NIST SP 800-88 guidelines: Clear (logical overwrite) for reuse within {{ORG_NAME}}, Purge (cryptographic erasure or secure erase) for removal from controlled areas, and Destroy (shredding, degaussing, incineration) for disposal. Sanitization actions must be documented with date, method, equipment used, and personnel verification.

## 7. Removable Media Controls

The use of portable storage devices including USB drives, external hard drives, and optical media must be controlled and authorized. Removable media must be registered and tracked in the organizational media inventory. The use of personally owned removable media on organizational systems is prohibited. Media lacking an identifiable owner or origin must not be connected to organizational systems.

## 8. Media Downgrading and Reuse

Media containing CUI that will be reused at a lower classification level must be purged or destroyed in accordance with NIST SP 800-88 before reuse. Media downgrading actions must be documented and approved by the data owner. Media that cannot be effectively sanitized must be destroyed.

## 9. Backup Media Protection

Backup media containing CUI must be protected with the same security controls as the source data. Backup media must be encrypted at rest using FIPS 140-2 validated cryptographic modules. Backup media stored offsite must be maintained in secured, access-controlled facilities. Backup media must be included in the organizational media inventory and tracking system.

## 10. Enforcement

Violations of this policy including unauthorized media removal, failure to properly sanitize media, or unencrypted transport of media containing CUI may result in disciplinary action up to and including termination.

## 11. Review

This policy is reviewed and updated at least annually."""

_CONTENT_MAP = """# Maintenance Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Maintenance Policy establishes requirements for performing, authorizing, and documenting maintenance on {{ORG_NAME}} information systems that process, store, or transmit Controlled Unclassified Information (CUI) in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all system maintenance activities including hardware repairs, software updates, firmware updates, configuration changes, and diagnostic activities performed on any information system within the CUI boundary. It covers maintenance performed by {{ORG_NAME}} personnel, contractors, and third-party vendors.

## 3. Maintenance Scheduling and Authorization

All system maintenance must be scheduled during approved maintenance windows. A formal maintenance request must be submitted documenting the scope, expected duration, systems affected, and personnel performing the work. Maintenance must be authorized by the system owner or designated authority before commencement. Emergency maintenance must be approved through the emergency change process and documented within 24 hours of completion.

## 4. Maintenance Personnel Controls

Maintenance personnel must be authorized and authenticated before accessing systems. Non-organizational maintenance personnel must be escorted or supervised during maintenance activities. Maintenance personnel access must be limited to the systems and functions required for the specific maintenance task. Access credentials provided to maintenance personnel must be time-limited and revoked upon maintenance completion.

## 5. Maintenance Tools and Equipment

Maintenance tools and diagnostic equipment must be approved, inventoried, and inspected before use on production systems. Tools capable of accessing or modifying system data must be sanitized before and after use. Unauthorized software, media, or diagnostic tools are prohibited on production systems. Maintenance equipment connecting to production systems must meet organization security configuration standards.

## 6. Non-Local and Remote Maintenance

Remote maintenance sessions must be conducted over encrypted channels using FIPS 140-2 validated cryptography. Multi-factor authentication is required for all remote maintenance access. Remote maintenance sessions must be logged including user identity, connection source, duration, and activities performed. Remote access must be disabled when not actively in use and terminated upon session completion. Remote maintenance must not bypass established security controls.

## 7. Maintenance Records and Documentation

All maintenance activities must be documented including date, description, systems affected, personnel involved, tools used, duration, and outcome. Maintenance records must be retained for a minimum of three years. Verification testing must be performed and documented after maintenance completion to confirm systems are functioning correctly and security controls remain intact.

## 8. Enforcement

Violations of this policy including unauthorized maintenance, use of unapproved tools, or failure to document maintenance activities may result in disciplinary action up to and including termination.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_PERSEC = """# Personnel Security Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Personnel Security Policy establishes requirements for screening, vetting, and managing personnel with access to {{ORG_NAME}} information systems that process, store, or transmit Controlled Unclassified Information (CUI) in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all employees, contractors, temporary workers, interns, and third-party personnel who require access to organizational information systems or CUI.

## 3. Pre-Employment Screening

All individuals must undergo background screening prior to being granted access to organizational systems. Screening must include identity verification, employment history verification, education verification, and criminal background check. Screening level must be commensurate with the sensitivity of the role and the CUI access required. Individuals in roles with elevated privileges or access to large volumes of CUI must undergo enhanced screening. Employment offers must be contingent upon successful completion of background screening.

## 4. Re-Screening and Ongoing Evaluation

Personnel must undergo re-screening upon promotion to roles with increased CUI access, following extended leave exceeding 90 days, or upon reasonable suspicion of security violations. Re-screening must be conducted at a minimum every five years for personnel with access to CUI. Adverse information discovered during re-screening must trigger a security review and may result in access suspension pending resolution.

## 5. Security Agreements and Acknowledgments

All personnel must sign a confidentiality agreement and non-disclosure agreement upon hire and prior to being granted system access. Personnel must annually acknowledge and re-affirm their understanding of security policies, acceptable use requirements, and CUI handling obligations. Signed agreements must be retained in personnel security files for the duration of employment plus three years.

## 6. Personnel Actions and Transfers

Upon transfer, reassignment, or change in role, access privileges must be reviewed and adjusted to match the new role requirements within one business day. Access no longer required must be removed. Upon termination, all system access must be revoked within 24 hours. During adverse personnel actions, access to CUI must be suspended immediately upon notification.

## 7. Termination Procedures

Upon termination, the following actions must be completed within 24 hours: revoke all system and facility access, collect all organizational property including devices, badges, keys, and media, conduct exit interview documenting security obligations and post-employment confidentiality requirements, and notify relevant system owners of access revocation. Personnel security files must be retained in accordance with records retention requirements.

## 8. Enforcement

Violations of this policy including unauthorized disclosure of CUI, failure to report adverse personnel information, or circumvention of screening requirements may result in disciplinary action up to and including termination and may be subject to legal action.

## 9. Review

This policy is reviewed and updated at least annually."""


_CONTENT_SAP = """# Security Assessment Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Security Assessment Policy defines requirements for security assessments, continuous monitoring, and system security planning at {{ORG_NAME}} in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all information systems that process, store, or transmit Controlled Unclassified Information (CUI), and to the security assessment team responsible for evaluating control effectiveness.

## 3. Security Assessment

Security assessments must be conducted at least annually and upon significant system changes. Assessments must evaluate the effectiveness of all implemented security controls against NIST SP 800-171 requirements. Assessment results must be documented in a Security Assessment Report (SAR) and reviewed by management.

## 4. Continuous Monitoring

Continuous monitoring must be implemented for all CUI systems. Monitoring activities must include: vulnerability scanning, configuration compliance checks, access control reviews, and audit log analysis. Monitoring results must be reviewed monthly by the Security Officer.

## 5. System Security Planning

A System Security Plan (SSP) must be developed and maintained for each system that processes CUI. The SSP must document: system boundaries, security control implementations, interconnection agreements, and risk assessment results. The SSP must be reviewed and updated at least annually.

## 6. Plan of Action and Milestones (POA&M)

A POA&M must be maintained for all identified security weaknesses. Each entry must include: deficiency description, severity, remediation actions, responsible party, and scheduled completion date. POA&M must be reviewed quarterly.

## 7. Review

This policy is reviewed and updated at least annually."""

_CONTENT_SCP = """# System and Communications Protection Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This System and Communications Protection Policy defines requirements for boundary protection, network segmentation, encryption, and communications security for {{ORG_NAME}} information systems in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all network infrastructure, communications equipment, cryptographic systems, and information systems that process, store, or transmit Controlled Unclassified Information (CUI).

## 3. Boundary Protection

All external system connections must be protected by managed firewalls at network boundaries. Inbound and outbound traffic must be restricted to explicitly authorized ports, protocols, and services. Default-deny rulesets must be implemented for all network boundaries.

## 4. Network Segmentation

Production environments processing CUI must be logically or physically separated from non-production environments. Internal network segmentation must isolate sensitive systems using VLANs, subnets, or equivalent controls.

## 5. Encryption

All CUI must be encrypted at rest using FIPS 140-2 validated cryptographic modules (AES-256 or equivalent). All CUI in transit across public networks must be encrypted using TLS 1.2 or higher with FIPS 140-2 validated modules. Cryptographic key management must follow NIST SP 800-57 guidelines.

## 6. Denial of Service Protection

Systems must be protected against denial of service attacks through bandwidth management, rate limiting, and traffic filtering. Critical systems must have redundant communication paths.

## 7. Session Controls

Session termination must occur after 30 minutes of inactivity for remote sessions. Concurrent sessions must be limited. Remote access sessions must be monitored and logged.

## 8. Mobile Code

The use of mobile code (JavaScript, ActiveX, Java applets) must be restricted and controlled. Mobile code execution from untrusted sources is prohibited.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_CHANGE_MGMT = """# Change Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Change Management Policy defines the standardized process for requesting, reviewing, approving, implementing, and documenting changes to {{ORG_NAME}} information systems, applications, and infrastructure in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all changes affecting production information systems, including hardware, software, firmware, configuration files, network devices, and cloud infrastructure that process, store, or transmit Controlled Unclassified Information (CUI).

## 3. Change Types and Classification

Changes are classified as Standard (pre-approved, low-risk, routine), Normal (requires review and approval through change advisory process), or Emergency (requires expedited approval to resolve critical incidents or security vulnerabilities). Emergency changes must be documented and reviewed within 24 hours of implementation.

## 4. Change Request and Approval

All changes must be submitted via a formal change request documenting the change description, justification, scope, risk assessment, implementation plan, rollback plan, and test results. Changes must be approved by the Change Advisory Board or designated authority before implementation. Separation of duties must be enforced between requesters, approvers, and implementers.

## 5. Testing and Validation

Changes must be tested in a non-production environment prior to deployment. Testing must validate functionality, security controls, and system integration. Test results must be documented and accompany the change request.

## 6. Implementation and Rollback

Changes must be implemented during approved maintenance windows following the documented implementation plan. A rollback plan must be prepared and tested before each change. Unauthorized changes are prohibited.

## 7. Documentation and Audit

All changes must be logged with timestamps, individuals involved, and outcomes. Change records must be retained for a minimum of three years. Configuration baselines must be updated after approved changes.

## 8. Enforcement

Violations of this policy may result in disciplinary action up to and including termination. Unauthorized changes must be reported to the Security Team immediately.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_DATA_HANDLING = """# Data Handling Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Data Handling Policy defines the requirements for identifying, marking, storing, transmitting, and disposing of Controlled Unclassified Information (CUI) and other sensitive data within {{ORG_NAME}} information systems in accordance with NIST SP 800-171 and CMMC Level 2 requirements.

## 2. Scope

This policy applies to all {{ORG_NAME}} employees, contractors, and third parties who create, access, process, store, transmit, or dispose of CUI or organizational sensitive data on any information system or media.

## 3. Data Classification and Identification

All data must be classified by the data owner according to {{ORG_NAME}} data classification levels. CUI must be explicitly identified and marked with appropriate labeling in accordance with DOD/DISA CUI marking requirements. Data owners are responsible for maintaining an inventory of CUI assets and data flows.

## 4. CUI Storage Requirements

CUI must be stored on authorized systems within the defined CUI boundary. CUI at rest must be encrypted using FIPS 140-2 validated cryptographic modules. CUI must not be stored on personal devices, removable media without authorization, or cloud services not approved for CUI processing. Access to CUI repositories must be restricted by role-based access controls.

## 5. CUI Transmission

CUI transmitted over public networks must be encrypted using TLS 1.2 or higher with FIPS 140-2 validated modules. CUI must not be transmitted via unencrypted email, unsecured file transfer, or unauthorized messaging platforms. Secure file transfer mechanisms must be used for external CUI sharing.

## 6. Media Handling and Sanitization

Digital and physical media containing CUI must be handled, transported, and stored in accordance with Media Protection Policy. Media sanitization must follow NIST SP 800-88 guidelines before reuse or disposal. Sanitization actions must be documented with date, method, and personnel verification.

## 7. Data Retention and Disposal

CUI must be retained in accordance with records retention schedules and contractual obligations. CUI no longer required must be securely disposed of using approved sanitization methods. Certificate of destruction must be maintained for disposed CUI media.

## 8. Enforcement

Violations of this policy may result in disciplinary action up to and including termination. Unauthorized disclosure or mishandling of CUI must be reported to the Security Team immediately.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_MOBILE_DEVICE = """# Mobile Device Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Mobile Device Policy establishes the requirements for connecting mobile devices to {{ORG_NAME}} information systems and governs the use, management, and security of mobile devices that access organizational data in accordance with NIST SP 800-171.

## 2. Scope

This policy applies to all mobile devices including laptops, tablets, smartphones, and portable media that connect to {{ORG_NAME}} networks or access, process, store, or transmit organizational data including CUI. This policy covers both organization-issued and personally owned devices (BYOD) where permitted.

## 3. Device Authorization

All mobile devices must be registered in the organizational asset inventory before connecting to internal networks. Devices must meet minimum security configuration standards including approved operating system versions, encryption, and mobile device management enrollment. Unauthorized devices are prohibited from connecting to internal networks.

## 4. CUI Restrictions

CUI is prohibited from being stored on mobile devices unless explicitly authorized and protected by FIPS 140-2 validated encryption. CUI stored on mobile devices must be within the defined CUI boundary and subject to access controls, audit logging, and remote wipe capability.

## 5. Security Controls

Mobile devices must have screen lock enabled with a minimum six-digit PIN or biometric authentication. Automatic device lock must occur after 5 minutes of inactivity. Devices must run approved anti-malware software with automatic updates. Rooted or jailbroken devices are prohibited.

## 6. Remote Wipe and Lost Reporting

Lost or stolen devices must be reported to the Security Team within 24 hours. Authorized personnel must initiate remote wipe procedures for lost or stolen devices containing organizational data. Remote wipe capability must be verified during device enrollment.

## 7. BYOD Requirements

Where BYOD is permitted, a signed BYOD agreement is required. BYOD devices must meet the same security requirements as organization-issued devices. Organizational data must be containerized and separated from personal data. Organizational data will be remotely wiped upon termination or as needed for security incidents.

## 8. Enforcement

Violations of this policy may result in disciplinary action up to and including termination and remote wipe of organizational data from personal devices.

## 9. Review

This policy is reviewed and updated at least annually."""

_CONTENT_REMOTE_ACCESS = """# Remote Access Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Remote Access Policy establishes the requirements for secure remote access to {{ORG_NAME}} information systems, networks, and data in accordance with NIST SP 800-171 and CMMC Level 2 requirements.

## 2. Scope

This policy applies to all remote access methods including VPN, remote desktop, SSH, web-based access, and third-party remote support tools used to connect to {{ORG_NAME}} internal networks, applications, and systems that process, store, or transmit CUI.

## 3. Authorized Remote Access Methods

Remote access to organizational systems must use {{ORG_NAME}} approved methods: VPN with multi-factor authentication, virtual desktop infrastructure, or secure remote desktop gateway. Unauthorized remote access tools including consumer-grade remote desktop software are prohibited. Remote access must be routed through managed access control points at network boundaries.

## 4. Multi-Factor Authentication

All remote access sessions must be authenticated using multi-factor authentication. MFA must combine something you know with something you have or something you are. Hardware tokens, software authenticators, or biometric factors are acceptable second factors. SMS-based MFA is prohibited for CUI access.

## 5. Endpoint Security Requirements

Devices used for remote access must meet organization security standards including current operating system patches, approved anti-malware software with updated signatures, host-based firewall enabled, and full disk encryption. Remote devices must be scanned for compliance before network access is granted.

## 6. Session Controls

Remote sessions must terminate after 30 minutes of inactivity. Concurrent remote sessions must be limited to one per user unless a business justification is approved. Remote execution of privileged commands must be explicitly authorized and logged.

## 7. Encryption

All remote access connections must be encrypted using FIPS 140-2 validated cryptographic modules. Remote access sessions must use TLS 1.2 or higher or equivalent encrypted tunneling protocols. Unencrypted remote access protocols including Telnet and unencrypted FTP are prohibited.

## 8. Monitoring and Logging

Remote access sessions must be logged including user identity, source IP address, connection timestamp, duration, and commands executed where applicable. Remote access logs must be retained for a minimum of 90 days and reviewed for anomalous activity.

## 9. Enforcement

Violations of this policy may result in suspension of remote access privileges, disciplinary action up to and including termination. Unauthorized remote access attempts must be reported to the Security Team immediately.

## 10. Review

This policy is reviewed and updated at least annually."""


_CONTENT_ISO27001_INFO_SEC = """# Information Security Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Context and Goals

[ORGANIZATION DESCRIPTION]

{{ORG_NAME}} processes confidential and sensitive data in the course of its business. Anyone in {{ORG_NAME}} (or at key positions at suppliers) that is handling confidential or sensitive data should be aware of this policy and act in accordance with it. If anyone observes something in {{ORG_NAME}} that is not in line with this policy, he or she should report this immediately. This can be done either by informing our information security officer, or any member of the security team. The entire management team of {{ORG_NAME}} has been involved in creating this policy and is fully committed to making sure we are compliant.

## 2. Scope

The scope of the {{ORG_NAME}} ISMS is:

- Information security related to ... [e.g. development and delivery of a platform for XYZ]

Within this scope, we provide the following main activities and provide the following services to customers:

- A
- B
- C

The following departments are in scope of this policy:

- A
- B
- C
- D

At this point in time, no departments or business activities have been specifically declared out of scope of this policy. Our company has the following office locations and working locations that are in scope of this policy:

- Main office: [ADDRESS]
- B
- C

{{ORG_NAME}} does/does not directly manage any data centres. [Amazon Web Services / Azure / Google Cloud / IBM] is used as provider of IT infrastructure.

## 3. Stakeholder Analysis

The management team is responsible for maintaining regular contact with stakeholders, understanding the information security requirements and expectations from stakeholders, and making sure that the ISMS is aligned with the stakeholder requirements and expectations. The resulting information is documented in the stakeholder analysis, which will be updated annually. The stakeholder analysis will cover at least:

- Customers
- Users
- Regulatory requirements such as GDPR

The most recent stakeholder analysis can be found in the Register of stakeholders and communication.

## 4. Leadership

The entire management is aware of the information security policy and is committed to support this effort on an ongoing basis. [MGMT_REP] is the management representative that interfaces directly with the security team.

There is an information security team that is responsible for implementing and maintaining information security.

All other staff of the company is regularly updated by the information security team and is responsible for following policies and guidelines.

## 5. Resources, Awareness and Training

Management is responsible for making sure employees executing information security tasks are knowledgeable on the subjects they work on.

They receive security awareness training after onboarding, and after that again at least once a year. Staff involved in product design and development or staff with additional security responsibilities will receive additional training suitable to their role.

## 6. Operations

{{ORG_NAME}} has a register of goals, [LINK DOCUMENT]. These goals are established by top management, and reviewed on an annual basis. When establishing these goals, top management makes sure to include the organizational context and stakeholder requirements.

## 7. Performance Evaluation

The management team will review the effectiveness of the ISMS annually in a management review. If needed, external support will be sought from external partners, such as additional technical advice, independent security testing, or audits by independent parties.

## 8. Continuous Improvement

The management is committed to continuously improving the information security management system.

## 9. Review

This policy is reviewed and updated at least annually.

## Appendix: References

This policy is based on ISO/IEC 27001:2022, covering at least the following Annex A controls:

- A.5.1 Policies for information security
- A.5.2 Information security roles and responsibilities
- A.5.4 Management responsibilities
- A.6.3 Information security awareness, education and training

Template adapted from the ICT Institute free template kit (https://ictinstitute.nl/free-templates/), used under Creative Commons Attribution 4.0 (CC-BY)."""


_CONTENT_ISO27001_RULES = """# Information Security Rules

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. General

Anyone with access to information in {{ORG_NAME}} has an important role in keeping information secure. It does not matter if you work in IT or in other parts of the business: the rules apply to all staff. The IS rules apply to any staff working in or for {{ORG_NAME}}. This includes:

- Permanent staff
- Interns and temporary staff
- [optional] Independent professionals or supplier staff with access to our premises or information

You should receive a copy of this document with your employment contract or on your first day at work.

The scope of this document is the broad use of information and includes hardware, software, and the information itself. You should follow the rules for all locations and devices you use to do your work.

Failure to follow these rules will lead to disciplinary measures such as formal warnings, suspension, or termination of employment. More details can be obtained at HR.

## 2. General Obligation for Information Security

- Anyone working in this organisation is obligated to keep information secure.
- You cannot disclose sensitive information to outsiders or publish information unless this is part of your role and the classification of the information allows it.
- You are obligated to know and respect all information security rules.
- You are obligated to take due care with any data, especially with personal data.
- You are obligated to take due care with company-issued devices.
- You are obligated to mention security incidents immediately to the information security officer. This includes loss of a device, suspicion of a hack, or any unusual situation.

These rules have been created by the management as part of the overall information security policy. Management is fully committed to information security and is available for any questions about these rules. You can ask questions to:

- [CEO / CFO / CIO]
- Email address:
- Phone number (general questions):
- Phone number (for emergencies such as incidents):
- InfoSec team members:

## 3. Classification of Information (A.5.9, A.5.12)

Certain information is considered to be sensitive due to e.g. monetary or legal value, and has to remain confidential, while other information is less crucial. {{ORG_NAME}} has a policy in place on how to handle classified information. The accountability to classify information assets lies with its owner. To distinguish between the importance of different classified assets, the following classification of assets is made:

- Public
- Internal use
- Confidential
- Very confidential

If you are not sure into which category a document or asset falls, ask your manager. We would rather have the same question several times than an internal or confidential document made public.

Please follow these instructions for handling information according to its classification:

- **Very confidential** (passwords, trade secrets) — store on systems explicitly designed for such information; share only when told to do so.
- **Confidential** (source code, contracts, documents with personal data) — store on internal shares/drives; share only with people who need it in their role (ask your manager when in doubt).
- **Internal use** (templates, instructions, procedures) — store on internal shares/drives; share with colleagues.
- **Public** (white papers, information already published online) — store on internal shares/drives or the website; share with colleagues or other people.

You should label documents when created. Documents not labelled should be considered internal-use-only, unless it is clear from context that the information is open (e.g. brochure) or that it is confidential (contains sensitive information).

## 4. Use of Phones, Tablets and Other Mobile Devices (A.8.1)

If you receive a mobile phone, tablet, or other device, please use this device with care to ensure that the information on this device is secure. Specifically, stick to the following rules:

- Do not disable security features on the device.
- Do not share the device with other people.
- Do not open suspicious emails.
- Do not install apps from unknown origin.
- Secure the device with a safe password/PIN.
- Encrypt the storage on devices.
- For laptops: regularly scan for viruses/malware.
- Keep software up to date, in line with recommendations from the manufacturer.
- If a device seems compromised, turn off the device and hand it over to IT staff.
- If a device is lost or stolen, report this immediately to the information security officer.

## 5. Working from Home (A.6.7)

If you work from home or an external location, you must follow the following rules:

- Do not handle personal data from our users and customers on non-company devices. Use only company devices for work.
- If you do have to use a home computer for handling company information, make sure the computer has a firewall and virus/malware scanner installed.

## 6. End of Contract or Employment (A.6.5)

When you leave the company (e.g. end of contract or end of employment), you must do the following:

- Hand in all devices and information carriers from the company.
- Hand in all documents containing confidential data (or dispose of these in a secure way).
- Even after the end of the contract, you are still bound to keep information secure: you may not disclose any sensitive or confidential data to outsiders for at least two years after departure from the company.

## 7. Security Awareness Training (A.6.3)

A security awareness training is organised at least once a year, and you should attend such a training in the first week of working at this organisation and at least once a year. The training is mandatory for all staff handling information. If you have not received any training, contact the information security officer.

## 8. Using and Storing Passwords (A.5.17)

Password and PIN security is an important aspect of all security. For all work-related passwords, you must follow the following rules:

- For each service, you must choose a fresh password not used before or for any other service.
- Passwords should not be easy to guess, so no names, birthdays, or common words, and no passwords of less than 8 characters.
- Passwords must be changed at least once a year.
- Personal passwords and accounts cannot be shared with anyone else.
- We recommend writing down the passwords offline (e.g. in a paper notebook) and keeping this notebook out of sight when you are not present, or using a secure, encrypted password manager on your computer.
- You are not allowed to leave passwords visible in the workplace.
- If devices such as mobile devices have the option of setting a PIN for device access, it is mandatory to set a PIN of at least 6 digits. The same rules that apply to passwords (fresh, not visible) apply to PINs.

## 9. Clean Desk and Clear Screen Policy (A.7.7)

- When leaving the offices, all documents must be removed from desks and stored in a non-visible way. Confidential documents must be stored in locked drawers or filing cabinets.
- Your computers and phones must have a screensaver with a password or similar security measure (e.g. fingerprint reader). You must use the screensaver when leaving the device unattended.

## 10. Reporting Incidents and Vulnerabilities (A.6.8)

- An information security event is a situation where information could be compromised. You can report any event; the security team will determine the next steps.
- An information security vulnerability is a situation where an event could occur, but there is no indication an event has occurred. E.g. a broken window is a good reason to believe an incident has occurred; a window without a lock is a vulnerability.
- If you think an event happened, you should report this immediately to the information security officer. In many cases, the company is obligated to immediately investigate and report incidents to customers or the authorities. The company can only do this if staff is alert.
- A vulnerability should also be reported but is less urgent. Report this on the same day or the next day to the information security officer or to the infosec team via email. They will analyse the vulnerability and resolve it. If you are unsure whether something is a vulnerability, you can still report it as a potential vulnerability, and the infosec team will determine if it is a vulnerability and what action is needed.

## 11. Using Personally Identifiable Information (A.5.34)

Personally identifiable information (PII) should be handled with the utmost care. Examples of PII are social security numbers, email addresses, and names. This leads to the following rules:

- Limit the distribution and storage of PII as much as possible.
- When sending PII, notify the receiver of the intended use. For example, working in HR, when sending a CV of a possible new hire, explicitly mention that the person can use it for the job interview and needs to delete it afterwards. Mention that they cannot forward the CV and should ask you for more information if they need it.
- Only use trusted systems for the distribution and storage of PII.
- Delete the information securely: remove the file from the system and also from the trash folder.
- For functions that handle PII on a daily basis, more specific procedures apply.

## 12. Use of Safe Networks (A.8.21)

Only use known and secure networks. When working in public spaces, explicitly check the network you are connected to. A known network is the company network or your home network. Check wireless networks explicitly on being secure.

## 13. Bring Your Own Device Rules and Use of Private Email Accounts (A.5.10)

Many people have their own personal laptops, tablets, and smartphones and use these for sharing information. It is technically possible to use these devices for work-related matters, but this poses severe security risks. We therefore ask you to:

- Not use personal devices for sharing work-related information, unless the information is public. Our security staff cannot guarantee the security of devices that they did not select or configure.
- Not use your personal email account for work-related emails.
- Make sure any device is from a respectable manufacturer, password-protected, free from malware and viruses, and updated regularly. This is for your own protection and as an extra precaution in case work-related information does leak to a personal device.

## 14. Signature

(Sign here if you have been asked to sign a version of this document as proof that you received and read these rules. You should sign one copy and keep one copy yourself.)

Name: _______________

Place, Date: _______________

## Appendix: References

This policy is based on ISO/IEC 27001:2022, covering at least the following Annex A controls:

- A.5.9 Inventory of information and other associated assets
- A.5.10 Acceptable use of information and other associated assets
- A.5.12 Classification of information
- A.5.17 Authentication information
- A.5.34 Protection of privacy and PII
- A.6.3 Information security awareness, education and training
- A.6.5 Responsibilities after termination or change of employment
- A.6.7 Working from home (teleworking)
- A.6.8 Reporting information security events
- A.7.7 Clear desk and clear screen
- A.8.1 User endpoint devices
- A.8.21 Security of network services

Template adapted from the ICT Institute free template kit (https://ictinstitute.nl/free-templates/), used under Creative Commons Attribution 4.0 (CC-BY)."""


BUILTIN_TEMPLATES = [
    {
        "key": "acceptable_use_policy",
        "name": "Acceptable Use Policy",
        "short_name": "AUP",
        "description": "Defines acceptable use of company information systems and data",
        "mapped_controls_soc2": ["CC6.1", "CC6.2", "CC6.7", "CC6.8"],
        "mapped_controls_cmmc": [],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_AUP,
    },
    {
        "key": "access_control_policy",
        "name": "Access Control Policy",
        "short_name": "ACP",
        "description": "Establishes requirements for logical and physical access controls",
        "mapped_controls_soc2": ["CC6.1", "CC6.3", "CC6.6"],
        "mapped_controls_cmmc": ["AC.L2-3.1.1", "AC.L2-3.1.2", "AC.L2-3.1.3", "AC.L2-3.1.4", "AC.L2-3.1.5", "AC.L2-3.1.6", "AC.L2-3.1.7", "AC.L2-3.1.8", "AC.L2-3.1.9", "AC.L2-3.1.10", "AC.L2-3.1.11", "AC.L2-3.1.12", "AC.L2-3.1.13", "AC.L2-3.1.14", "AC.L2-3.1.15", "AC.L2-3.1.16", "AC.L2-3.1.17", "AC.L2-3.1.18", "AC.L2-3.1.19", "AC.L2-3.1.20", "AC.L2-3.1.21", "AC.L2-3.1.22"],
        "mapped_controls_eu_ai_act": ["EU-15", "EU-26"],
        "mapped_controls_nist_ai_rmf": ["NIST-GOVERN-1.1", "NIST-GOVERN-4.1", "NIST-MANAGE-1.3"],
        "mapped_controls_iso_42001": ["ISO-8.1", "ISO-9.1", "ISO-A.9"],
        "framework_tags": ["SOC2", "CMMC", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_ACP,
    },
    {
        "key": "identification_authentication_policy",
        "name": "Identification and Authentication Policy",
        "short_name": "IAP",
        "description": "Defines identification, authentication, MFA, and credential management standards per NIST SP 800-171",
        "mapped_controls_soc2": ["CC6.1", "CC6.5", "CC6.6"],
        "mapped_controls_cmmc": ["IA.L2-3.5.1", "IA.L2-3.5.2", "IA.L2-3.5.3", "IA.L2-3.5.4", "IA.L2-3.5.5", "IA.L2-3.5.6", "IA.L2-3.5.7", "IA.L2-3.5.8", "IA.L2-3.5.9", "IA.L2-3.5.10", "IA.L2-3.5.11"],
        "mapped_controls_eu_ai_act": ["EU-15", "EU-26"],
        "mapped_controls_nist_ai_rmf": ["NIST-GOVERN-1.1", "NIST-GOVERN-4.1", "NIST-MAP-2.1"],
        "mapped_controls_iso_42001": ["ISO-7.1", "ISO-8.1", "ISO-A.9"],
        "framework_tags": ["SOC2", "CMMC", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_PAP,
    },
    {
        "key": "configuration_management_policy",
        "name": "Configuration Management Policy",
        "short_name": "CMP",
        "description": "Defines the process for establishing baseline configurations and managing changes to production systems",
        "mapped_controls_soc2": ["CC8.1"],
        "mapped_controls_cmmc": ["CM.L2-3.4.1", "CM.L2-3.4.2", "CM.L2-3.4.3", "CM.L2-3.4.4", "CM.L2-3.4.5", "CM.L2-3.4.6", "CM.L2-3.4.7", "CM.L2-3.4.8", "CM.L2-3.4.9"],
        "mapped_controls_eu_ai_act": ["EU-15", "EU-17", "EU-53"],
        "mapped_controls_nist_ai_rmf": ["NIST-GOVERN-4.1", "NIST-MANAGE-4.1"],
        "mapped_controls_iso_42001": ["ISO-8.1", "ISO-10.1", "ISO-A.9"],
        "framework_tags": ["SOC2", "CMMC", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_CMP,
    },
    {
        "key": "incident_response_policy",
        "name": "Incident Response Policy",
        "short_name": "IRP",
        "description": "Defines procedures for detecting, responding to, and recovering from security incidents",
        "mapped_controls_soc2": ["CC7.2", "CC7.3", "CC7.4", "CC7.5"],
        "mapped_controls_cmmc": ["IR.L2-3.6.1", "IR.L2-3.6.2", "IR.L2-3.6.3"],
        "mapped_controls_eu_ai_act": ["EU-20", "EU-72", "EU-73"],
        "mapped_controls_nist_ai_rmf": ["NIST-MEASURE-3.1", "NIST-MANAGE-1.3", "NIST-MANAGE-4.1"],
        "mapped_controls_iso_42001": ["ISO-9.1", "ISO-10.1", "ISO-A.10", "ISO-10.2"],
        "framework_tags": ["SOC2", "CMMC", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_IRP,
    },
    {
        "key": "information_security_policy",
        "name": "Information Security Policy",
        "short_name": "ISP",
        "description": "High-level ISMS policy describing context, scope, stakeholder analysis, leadership, and commitment per ISO/IEC 27001",
        "mapped_controls_soc2": [],
        "mapped_controls_cmmc": [],
        "mapped_controls_iso27001": ["ISO27K-A.5.1", "ISO27K-A.5.2", "ISO27K-A.5.4", "ISO27K-A.6.3"],
        "framework_tags": ["iso27001"],
        "content": _CONTENT_ISO27001_INFO_SEC,
    },
    {
        "key": "information_security_rules",
        "name": "Information Security Rules",
        "short_name": "ISR",
        "description": "Employee-facing information security rules covering classification, passwords, mobile devices, teleworking, PII, and incident reporting per ISO/IEC 27001",
        "mapped_controls_soc2": [],
        "mapped_controls_cmmc": [],
        "mapped_controls_iso27001": ["ISO27K-A.5.9", "ISO27K-A.5.10", "ISO27K-A.5.12", "ISO27K-A.5.17", "ISO27K-A.5.34", "ISO27K-A.6.3", "ISO27K-A.6.5", "ISO27K-A.6.7", "ISO27K-A.6.8", "ISO27K-A.7.7", "ISO27K-A.8.1", "ISO27K-A.8.21"],
        "framework_tags": ["iso27001"],
        "content": _CONTENT_ISO27001_RULES,
    },
    {
        "key": "vendor_management_policy",
        "name": "Vendor Management Policy",
        "short_name": "VMP",
        "description": "Defines third-party risk assessment and vendor oversight requirements",
        "mapped_controls_soc2": ["CC5.1", "CC5.2", "CC9.2"],
        "mapped_controls_cmmc": [],
        "mapped_controls_eu_ai_act": ["EU-22", "EU-23", "EU-24", "EU-25"],
        "mapped_controls_nist_ai_rmf": ["NIST-MAP-4.1", "NIST-MANAGE-3.1"],
        "mapped_controls_iso_42001": ["ISO-4.2", "ISO-8.1", "ISO-A.8"],
        "framework_tags": ["SOC2", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_VMP,
    },
    {
        "key": "risk_assessment_policy",
        "name": "Risk Assessment Policy",
        "short_name": "RAP",
        "description": "Defines the risk management framework and assessment methodology",
        "mapped_controls_soc2": ["CC3.1", "CC3.2"],
        "mapped_controls_cmmc": ["RA.L2-3.11.1", "RA.L2-3.11.2", "RA.L2-3.11.3"],
        "mapped_controls_eu_ai_act": ["EU-9", "EU-27"],
        "mapped_controls_nist_ai_rmf": ["NIST-GOVERN-3.1", "NIST-MAP-4.1", "NIST-MAP-5.1", "NIST-MEASURE-1.1", "NIST-MANAGE-1.3"],
        "mapped_controls_iso_42001": ["ISO-6.1", "ISO-9.1", "ISO-A.7"],
        "framework_tags": ["SOC2", "CMMC", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_RAP,
    },
    {
        "key": "data_classification_policy",
        "name": "Data Classification Policy",
        "short_name": "DCP",
        "description": "Defines data classification levels and handling requirements",
        "mapped_controls_soc2": ["CC6.1", "CC6.7"],
        "mapped_controls_cmmc": [],
        "mapped_controls_eu_ai_act": ["EU-10"],
        "mapped_controls_nist_ai_rmf": ["NIST-MAP-4.1", "NIST-MEASURE-2.10"],
        "mapped_controls_iso_42001": ["ISO-7.5", "ISO-A.8"],
        "framework_tags": ["SOC2", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_DCP,
    },
    {
        "key": "business_continuity_policy",
        "name": "Business Continuity and Disaster Recovery Policy",
        "short_name": "BCDR",
        "description": "Defines requirements for business continuity and disaster recovery planning",
        "mapped_controls_soc2": ["CC7.5"],
        "mapped_controls_cmmc": [],
        "mapped_controls_iso27001": ["ISO27K-A.5.29", "ISO27K-A.5.30", "ISO27K-A.8.13", "ISO27K-A.8.14"],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_BCDR,
    },
    {
        "key": "awareness_training_policy",
        "name": "Awareness and Training Policy",
        "short_name": "ATP",
        "description": "Defines security awareness and role-based training requirements per NIST SP 800-171",
        "mapped_controls_soc2": ["CC1.1", "CC1.2"],
        "mapped_controls_cmmc": ["AT.L2-3.2.1", "AT.L2-3.2.2", "AT.L2-3.2.3"],
        "framework_tags": ["SOC2", "CMMC"],
        "content": _CONTENT_COCE,
    },
    {
        "key": "ai_ethics_governance_policy",
        "name": "AI Ethics and Governance Policy",
        "short_name": "AEGP",
        "description": "Defines ethical principles and governance for AI systems",
        "mapped_controls_soc2": [],
        "mapped_controls_cmmc": [],
        "mapped_controls_eu_ai_act": ["EU-5", "EU-6", "EU-13", "EU-14", "EU-26", "EU-50"],
        "mapped_controls_nist_ai_rmf": ["NIST-GOVERN-1.1", "NIST-GOVERN-2.1", "NIST-GOVERN-3.1", "NIST-GOVERN-4.1", "NIST-GOVERN-5.1", "NIST-GOVERN-6.1", "NIST-MANAGE-3.1"],
        "mapped_controls_iso_42001": ["ISO-4.4", "ISO-5.1", "ISO-5.2", "ISO-5.3", "ISO-7.3", "ISO-A.5", "ISO-A.6", "ISO-A.10"],
        "mapped_controls_iso27001": ["ISO27K-A.5.10", "ISO27K-A.5.14", "ISO27K-A.5.23", "ISO27K-A.5.34", "ISO27K-A.8.25", "ISO27K-A.8.26", "ISO27K-A.8.28"],
        "framework_tags": ["aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_AI_ETHICS,
    },
    {
        "key": "system_security_plan",
        "name": "System Description",
        "short_name": "SD",
        "description": "Master document describing the system, boundaries, controls, and how they satisfy SOC 2 Trust Services Criteria",
        "mapped_controls_soc2": ["CC1.1", "CC1.2", "CC1.3", "CC1.4"],
        "mapped_controls_cmmc": [],
        "mapped_controls_eu_ai_act": ["EU-11", "EU-43", "EU-48"],
        "mapped_controls_nist_ai_rmf": ["NIST-MAP-1.1", "NIST-MAP-2.1", "NIST-MAP-3.1", "NIST-GOVERN-4.1"],
        "mapped_controls_iso_42001": ["ISO-4.3", "ISO-4.4", "ISO-7.5", "ISO-A.9"],
        "framework_tags": ["SOC2", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_SYSTEM_SEC,
    },
    {
        "key": "audit_accountability_policy",
        "name": "Audit and Accountability Policy",
        "short_name": "AAP",
        "description": "Defines requirements for system logging, auditing, monitoring, and alerting",
        "mapped_controls_soc2": ["CC7.1", "CC4.1", "CC6.1", "CC7.2"],
        "mapped_controls_cmmc": ["AU.L2-3.3.1", "AU.L2-3.3.2", "AU.L2-3.3.3", "AU.L2-3.3.4", "AU.L2-3.3.5", "AU.L2-3.3.6", "AU.L2-3.3.7", "AU.L2-3.3.8", "AU.L2-3.3.9"],
        "mapped_controls_eu_ai_act": ["EU-12", "EU-18", "EU-19"],
        "mapped_controls_nist_ai_rmf": ["NIST-MEASURE-3.1", "NIST-MANAGE-4.1"],
        "mapped_controls_iso_42001": ["ISO-9.1", "ISO-9.2", "ISO-A.10", "ISO-8.1"],
        "framework_tags": ["SOC2", "CMMC", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_LMP,
    },
    {
        "key": "backup_policy",
        "name": "Backup and Recovery Policy",
        "short_name": "BRP",
        "description": "Defines backup frequency, retention, and recovery requirements for data and systems",
        "mapped_controls_soc2": ["CC6.4", "CC7.5", "CC6.6"],
        "mapped_controls_cmmc": [],
        "mapped_controls_eu_ai_act": ["EU-15", "EU-18"],
        "mapped_controls_nist_ai_rmf": ["NIST-MEASURE-3.1", "NIST-MANAGE-2.2"],
        "mapped_controls_iso_42001": ["ISO-8.1", "ISO-9.1", "ISO-A.10"],
        "framework_tags": ["SOC2", "aigovernance", "eu_ai_act", "nist_ai_rmf", "iso42001"],
        "content": _CONTENT_BRP,
    },
    {
        "key": "system_information_integrity_policy",
        "name": "System and Information Integrity Policy",
        "short_name": "SIIP",
        "description": "Defines requirements for vulnerability scanning, patch management, malicious code protection, and system monitoring",
        "mapped_controls_soc2": ["CC7.1"],
        "mapped_controls_cmmc": ["SI.L2-3.14.1", "SI.L2-3.14.2", "SI.L2-3.14.3", "SI.L2-3.14.4", "SI.L2-3.14.5", "SI.L2-3.14.6", "SI.L2-3.14.7"],
        "framework_tags": ["SOC2", "CMMC"],
        "content": _CONTENT_SIIP,
    },
    {
        "key": "network_security_policy",
        "name": "Network Security Policy",
        "short_name": "NSP",
        "description": "Defines requirements for network segmentation, boundary protection, and encryption",
        "mapped_controls_soc2": ["CC6.1", "CC6.6"],
        "mapped_controls_cmmc": [],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_NSP,
    },
    {
        "key": "physical_security_policy",
        "name": "Physical Protection Policy",
        "short_name": "PESP",
        "description": "Defines requirements for physical access controls and environmental protections",
        "mapped_controls_soc2": ["CC6.6"],
        "mapped_controls_cmmc": ["PE.L2-3.10.1", "PE.L2-3.10.2", "PE.L2-3.10.3", "PE.L2-3.10.4", "PE.L2-3.10.5", "PE.L2-3.10.6"],
        "framework_tags": ["SOC2", "CMMC"],
        "content": _CONTENT_PSP,
    },
    {
        "key": "media_protection_policy",
        "name": "Media Protection Policy",
        "short_name": "MPP",
        "description": "Defines requirements for protecting information on digital and physical media",
        "mapped_controls_soc2": ["CC6.6"],
        "mapped_controls_cmmc": ["MP.L2-3.8.1", "MP.L2-3.8.2", "MP.L2-3.8.3", "MP.L2-3.8.4", "MP.L2-3.8.5", "MP.L2-3.8.6", "MP.L2-3.8.7", "MP.L2-3.8.8", "MP.L2-3.8.9"],
        "framework_tags": ["SOC2", "CMMC"],
        "content": _CONTENT_MPP,
    },
    {
        "key": "maintenance_policy",
        "name": "Maintenance Policy",
        "short_name": "MAP",
        "description": "Defines requirements for scheduled and emergency maintenance of information systems",
        "mapped_controls_soc2": [],
        "mapped_controls_cmmc": ["MA.L2-3.7.1", "MA.L2-3.7.2", "MA.L2-3.7.3", "MA.L2-3.7.4", "MA.L2-3.7.5", "MA.L2-3.7.6"],
        "framework_tags": ["CMMC"],
        "content": _CONTENT_MAP,
    },
    {
        "key": "personnel_security_policy",
        "name": "Personnel Security Policy",
        "short_name": "PSP",
        "description": "Defines requirements for personnel screening, security agreements, and termination",
        "mapped_controls_soc2": [],
        "mapped_controls_cmmc": ["PS.L2-3.9.1", "PS.L2-3.9.2"],
        "framework_tags": ["CMMC"],
        "content": _CONTENT_PERSEC,
    },
    {
        "key": "security_assessment_policy",
        "name": "Security Assessment Policy",
        "short_name": "SAP",
        "description": "Defines requirements for security assessments, continuous monitoring, and system security planning",
        "mapped_controls_cmmc": ["CA.L2-3.12.1", "CA.L2-3.12.2", "CA.L2-3.12.3", "CA.L2-3.12.4"],
        "mapped_controls_soc2": ["CC4.1", "CC7.1", "CC7.2"],
        "framework_tags": ["SOC2", "CMMC"],
        "content": _CONTENT_SAP,
    },
    {
        "key": "system_communications_protection_policy",
        "name": "System and Communications Protection Policy",
        "short_name": "SCPP",
        "description": "Defines requirements for boundary protection, network segmentation, encryption, and communications security",
        "mapped_controls_cmmc": ["SC.L2-3.13.1", "SC.L2-3.13.2", "SC.L2-3.13.3", "SC.L2-3.13.4", "SC.L2-3.13.5", "SC.L2-3.13.6", "SC.L2-3.13.7", "SC.L2-3.13.8", "SC.L2-3.13.9", "SC.L2-3.13.10", "SC.L2-3.13.11", "SC.L2-3.13.12", "SC.L2-3.13.13", "SC.L2-3.13.14", "SC.L2-3.13.15", "SC.L2-3.13.16"],
        "mapped_controls_soc2": ["CC6.1", "CC6.6"],
        "framework_tags": ["SOC2", "CMMC"],
        "content": _CONTENT_SCP,
    },
    {
        "key": "change_management_policy",
        "name": "Change Management Policy",
        "short_name": "CMGP",
        "description": "Defines the standardized process for requesting, reviewing, approving, and implementing changes to information systems",
        "mapped_controls_cmmc": [],
        "mapped_controls_soc2": ["CC8.1"],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_CHANGE_MGMT,
    },
    {
        "key": "data_handling_policy",
        "name": "Data Handling Policy",
        "short_name": "DHP",
        "description": "Defines requirements for identifying, marking, storing, transmitting, and disposing of CUI and sensitive data",
        "mapped_controls_cmmc": [],
        "mapped_controls_soc2": ["CC6.1", "CC6.7"],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_DATA_HANDLING,
    },
    {
        "key": "mobile_device_policy",
        "name": "Mobile Device Policy",
        "short_name": "MDP",
        "description": "Establishes requirements for connecting mobile devices to organizational information systems and managing mobile device security",
        "mapped_controls_cmmc": [],
        "mapped_controls_soc2": ["CC6.1", "CC6.6"],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_MOBILE_DEVICE,
    },
    {
        "key": "remote_access_policy",
        "name": "Remote Access Policy",
        "short_name": "RACP",
        "description": "Establishes requirements for secure remote access to organizational information systems, networks, and data",
        "mapped_controls_cmmc": [],
        "mapped_controls_soc2": ["CC6.1", "CC6.3", "CC6.6"],
        "framework_tags": ["SOC2"],
        "content": _CONTENT_REMOTE_ACCESS,
    },
]
