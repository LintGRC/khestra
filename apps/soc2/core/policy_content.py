"""SOC 2 policy templates with TSC mapping.

Each template uses {{ORG_NAME}} and {{DATE}} placeholders filled at generation time.
"""

from typing import Dict, List

TEMPLATES: Dict[str, Dict] = {
    "acceptable_use_policy": {
        "name": "Acceptable Use Policy",
        "short_name": "AUP",
        "description": "Defines acceptable use of company information systems and data",
        "mapped_controls": ["CC6.1", "CC6.2", "CC6.7", "CC6.8"],
        "content": """# Acceptable Use Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

The purpose of this Acceptable Use Policy (AUP) is to establish the rules and expectations governing the use of {{ORG_NAME}} information systems, networks, applications, and data. This policy ensures the confidentiality, integrity, and availability of company and customer information.

## 2. Scope

This policy applies to all employees, contractors, consultants, temporary workers, and third-party users of {{ORG_NAME}} information systems, regardless of location or device used.

## 3. Policy Statements

### 3.1 Authorized Use
Information systems are provided for business purposes. Incidental personal use is permitted provided it does not interfere with job performance, consume significant resources, or violate any other policy.

### 3.2 Prohibited Activities
The following activities are strictly prohibited:
- Accessing, storing, or transmitting illegal content
- Intentionally introducing malware, viruses, or malicious code
- Circumventing security controls or accessing systems without authorization
- Using company systems for harassment, discrimination, or offensive communications
- Sharing authentication credentials with others
- Downloading or installing unapproved software
- Storing company data on personal devices without authorization

### 3.3 Access Control
Users must:
- Use unique user accounts and strong passwords
- Lock workstations when away from their desk
- Report lost or compromised credentials immediately
- Only access data and systems necessary for their role (principle of least privilege)

### 3.4 Data Handling
Users must follow the Data Classification Policy when handling sensitive information. Personally Identifiable Information (PII), customer data, and proprietary business information must be protected according to their classification level.

### 3.5 Remote Access
Remote access to company systems must use approved VPN or zero-trust access solutions with multi-factor authentication enabled.

## 4. Monitoring and Privacy

{{ORG_NAME}} reserves the right to monitor network activity, system usage, and communications on company-owned systems to ensure compliance with this policy and protect the security of our information assets. Users should have no expectation of privacy when using company systems.

## 5. Enforcement

Violations of this policy may result in disciplinary action, up to and including termination of employment, termination of contracts, and/or legal action. Suspected violations must be reported to the Security Team immediately.

## 6. Review

This policy is reviewed and updated at least annually. All employees must acknowledge this policy upon hire and annually thereafter.

**Satisfies SOC 2: CC6.1, CC6.2, CC6.7, CC6.8**""",
    },
    "access_control_policy": {
        "name": "Access Control Policy",
        "short_name": "ACP",
        "description": "Establishes requirements for logical and physical access controls",
        "mapped_controls": ["CC6.1", "CC6.3", "CC6.6"],
        "content": """# Access Control Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Access Control Policy establishes the framework for managing logical access to {{ORG_NAME}} information systems and data. The objective is to ensure that access is granted based on business need, least privilege, and separation of duties.

## 2. Scope

This policy applies to all information systems, applications, databases, networks, and physical facilities used to process, store, or transmit company or customer data.

## 3. Policy Statements

### 3.1 Identity and Access Management

- Every user must have a unique identifier (username) for accountability
- Shared accounts are prohibited except where technically unavoidable and approved by the Security Team
- Service accounts must be documented, reviewed quarterly, and use managed credentials
- All access must be authenticated before granting system access

### 3.2 Least Privilege

Access rights must be limited to the minimum necessary for the user to perform their job function. Privileged access (administrator, root, superuser) must be:
- Granted only with management approval
- Reviewed quarterly
- Logged and monitored
- Revoked immediately upon role change or termination

### 3.3 Provisioning and Deprovisioning

- Access requests must be submitted via the designated ticket system with manager approval
- Standard roles and access profiles are pre-defined for each job function
- Access is revoked within 24 hours of termination notification
- Quarterly access reviews are conducted for all systems and applications

### 3.4 Password and Authentication

All systems must enforce authentication requirements defined in the Password and Authentication Policy, including:
- Minimum password length and complexity
- Multi-factor authentication for remote and privileged access
- Account lockout after repeated failed attempts
- Password rotation requirements

### 3.5 Physical Access

Physical access to offices, data centers, and server rooms must be controlled via:
- Badge-based access control systems
- Visitor logs and escort requirements
- Quarterly review of physical access records
- Video surveillance where applicable

## 4. Segregation of Duties

Conflicting duties must be separated to prevent fraud and error. No single individual may perform both:
- Development and production deployment
- Request and approval of their own access
- Security administration and audit log review

## 5. Enforcement

Unauthorized access attempts or violations of this policy must be reported immediately to the Security Team. Violations may result in disciplinary action, up to and including termination.

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.1, CC6.3, CC6.6**""",
    },
    "password_authentication_policy": {
        "name": "Password and Authentication Policy",
        "short_name": "PAP",
        "description": "Defines password, MFA, and authentication standards",
        "mapped_controls": ["CC6.1", "CC6.5", "CC6.6"],
        "content": """# Password and Authentication Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines the authentication standards for all {{ORG_NAME}} information systems. Strong authentication is the first line of defense against unauthorized access and is required for SOC 2 compliance.

## 2. Scope

This policy applies to all user accounts, service accounts, and system accounts across all company-operated and third-party systems that store, process, or transmit company data.

## 3. Policy Statements

### 3.1 Password Requirements

All user passwords must meet the following minimum standards:
- Minimum length of 12 characters
- Must contain characters from at least three of the following categories: uppercase letters, lowercase letters, numbers, special characters
- Must not contain the user's name, username, or common dictionary words
- Must not be reused (minimum of 10 previous passwords remembered)
- Default/temporary passwords must be changed upon first login

### 3.2 Multi-Factor Authentication (MFA)

MFA is required for:
- All remote access to company systems
- All administrative and privileged accounts
- Cloud service provider consoles
- Email and collaboration platforms

Acceptable MFA methods include:
- Time-based one-time passwords (TOTP) via authenticator apps
- Hardware security keys (FIDO2/WebAuthn)
- Push notification-based authentication
- SMS-based authentication (discouraged, but permitted where no alternative exists)

### 3.3 Account Management

- Accounts are locked after 5 consecutive failed login attempts
- Lockout duration is 15 minutes minimum
- Session timeout after 30 minutes of inactivity for web applications
- Service accounts must use key-based or certificate-based authentication where possible
- API keys and tokens must be rotated every 90 days

### 3.4 Credential Storage

Passwords must be stored using salted, one-way hashing algorithms (bcrypt, argon2, or PBKDF2). Plain-text password storage is prohibited. Credentials must never be hardcoded in source code, configuration files, or scripts.

### 3.5 Secrets Management

All application secrets, API keys, certificates, and credentials must be stored in an approved secrets management system (e.g., vault, cloud key management service). Access to secrets must be audited.

## 4. Enforcement

Compromised credentials must be reported immediately. Password sharing is prohibited. Violations may result in disciplinary action.

## 5. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.1, CC6.5, CC6.6**""",
    },
    "change_management_policy": {
        "name": "Change Management Policy",
        "short_name": "CMP",
        "description": "Defines the process for managing changes to production systems",
        "mapped_controls": ["CC8.1"],
        "content": """# Change Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Change Management Policy establishes a structured process for planning, approving, implementing, and reviewing changes to {{ORG_NAME}} production systems, applications, and infrastructure. The goal is to minimize disruption and prevent unauthorized modifications.

## 2. Scope

This policy applies to all changes affecting:
- Production software applications and services
- Cloud infrastructure (compute, networking, storage)
- Database schemas and configurations
- Security controls (firewall rules, IAM policies, encryption settings)
- CI/CD pipelines and deployment automation

## 3. Policy Statements

### 3.1 Change Classification

Changes are classified as:

- **Standard:** Pre-approved, low-risk changes following documented procedures (e.g., routine patching, certificate renewal)
- **Normal:** Changes requiring review and approval before implementation (e.g., feature deployment, configuration changes)
- **Emergency:** Critical changes required to resolve a production incident. May bypass normal approval but requires post-implementation review within 24 hours.

### 3.2 Change Request Requirements

All normal and emergency changes must be documented with:
- Description of the change and business justification
- Impact assessment (systems, users, data affected)
- Rollback plan
- Testing performed
- Risk assessment
- Approver designation

### 3.3 Change Approval

- Peer review is required for all code changes
- Manager or technical lead approval is required for normal changes
- Security Team approval is required for changes affecting security controls
- Changes must not be self-approved (separation of duties)

### 3.4 Testing

All changes must be tested in a non-production environment before deployment to production. Testing must validate:
- Functional correctness
- Performance impact
- Security implications
- Integration with dependent systems

### 3.5 Deployment

- Changes must be deployed during approved maintenance windows
- Emergency changes may be deployed immediately with post-implementation review
- Deployment must be automated where possible using CI/CD pipelines
- Changes are deployed using infrastructure-as-code where applicable

## 4. Post-Implementation Review

After implementation, the change owner must:
- Verify the change operates as expected
- Monitor for unexpected behavior for at least 24 hours
- Update documentation and runbooks

## 5. Audit and Compliance

All change records must be retained for a minimum of 12 months. Change logs must include: requestor, approver, implementer, timestamp, description, and outcome.

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC8.1**""",
    },
    "incident_response_policy": {
        "name": "Incident Response Policy",
        "short_name": "IRP",
        "description": "Defines procedures for detecting, responding to, and recovering from security incidents",
        "mapped_controls": ["CC7.2", "CC7.3", "CC7.4", "CC7.5"],
        "content": """# Incident Response Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Incident Response Policy defines the framework for detecting, responding to, containing, and recovering from security incidents affecting {{ORG_NAME}} information systems and data.

## 2. Scope

This policy covers all types of security incidents including but not limited to: unauthorized access, data breaches, malware infections, denial of service attacks, system compromises, and physical security incidents.

## 3. Policy Statements

### 3.1 Incident Classification

Incidents are classified by severity:

- **Critical:** Active data breach, system compromise affecting customer data, ransomware deployment
- **High:** Unauthorized access to sensitive systems, successful phishing leading to credential theft, DDoS disrupting service
- **Medium:** Malware detected on endpoint, suspicious login activity, policy violation with security implications
- **Low:** Failed login attempts, port scans, informational security alerts

### 3.2 Incident Response Team

The Security Team is responsible for incident response. Key roles include:
- **Incident Commander:** Leads the response effort
- **Technical Lead:** Conducts forensic analysis and remediation
- **Communications Lead:** Manages internal and external communications
- **Legal/Compliance:** Advises on regulatory obligations and notifications

### 3.3 Detection and Reporting

All employees must report suspected security incidents immediately to the Security Team via:
- Emergency: Phone call to on-call security engineer
- Non-emergency: Ticket system or security@ email alias

Automated detection mechanisms include:
- SIEM alerting for suspicious activity
- Endpoint detection and response (EDR) alerts
- Cloud security posture monitoring
- Vulnerability scanning results

### 3.4 Response Procedures

1. **Identification:** Verify and classify the incident
2. **Containment:** Isolate affected systems to prevent further damage
3. **Eradication:** Remove the threat (malware, unauthorized access) from affected systems
4. **Recovery:** Restore systems to normal operation from known-good backups
5. **Lessons Learned:** Conduct post-incident review within 5 business days

### 3.5 Communication

- Critical incidents must be escalated to executive leadership within 1 hour of detection
- Customer notification must follow contractual obligations and applicable regulations
- External communications must be approved by Legal

### 3.6 Evidence Preservation

Forensic evidence must be preserved including: system logs, network captures, disk images, and relevant documentation. Chain of custody must be maintained.

## 4. Breach Notification

In the event of a confirmed data breach involving PII or customer data, {{ORG_NAME}} will comply with all applicable breach notification laws and contractual obligations.

## 5. Training and Testing

- All employees receive annual security awareness training
- The Incident Response Plan is tested at least annually via tabletop exercises
- Lessons learned are incorporated into policy updates

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC7.2, CC7.3, CC7.4, CC7.5**""",
    },
    "vendor_management_policy": {
        "name": "Vendor Management Policy",
        "short_name": "VMP",
        "description": "Defines third-party risk assessment and vendor oversight requirements",
        "mapped_controls": ["CC5.1", "CC5.2", "CC9.2"],
        "content": """# Vendor Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Vendor Management Policy establishes the framework for assessing, onboarding, monitoring, and offboarding third-party vendors that access, process, or store company or customer data.

## 2. Scope

This policy applies to all third-party relationships including:
- Software-as-a-Service (SaaS) providers
- Cloud infrastructure providers
- Professional services firms with data access
- Subcontractors and consultants
- API and data integration partners

## 3. Policy Statements

### 3.1 Vendor Risk Classification

Vendors are classified based on their access to data and systems:
- **High Risk:** Access to customer data, PII, production systems, or critical infrastructure
- **Medium Risk:** Access to internal systems, non-sensitive data
- **Low Risk:** No data access (e.g., office supplies, facilities)

### 3.2 Due Diligence

Before engaging a vendor, the following must be assessed:
- **Security:** SOC 2 report, ISO 27001 certification, or security questionnaire
- **Privacy:** Data processing practices, subprocessor relationships
- **Compliance:** Relevant regulatory certifications (GDPR, HIPAA, PCI-DSS)
- **Financial Stability:** Business continuity risk
- **Incident History:** Past breaches or security incidents

### 3.3 Contractual Requirements

Vendor contracts must include:
- Data protection and confidentiality clauses
- Security requirements aligned with {{ORG_NAME}} policies
- Incident notification requirements (within 24 hours for breaches)
- Right to audit security practices
- Data deletion and return upon contract termination
- Subprocessor approval requirements

### 3.4 Ongoing Monitoring

High-risk vendors must be reviewed annually. Monitoring includes:
- Review of updated SOC 2 reports or certifications
- Security posture changes
- Any reported incidents or breaches
- Contract and SLA compliance

### 3.5 Vendor Offboarding

Upon termination of a vendor relationship:
- Access to all {{ORG_NAME}} systems must be revoked
- Vendor must confirm deletion of all company and customer data
- Return of any company-owned assets or equipment
- Final compliance review

## 4. Vendor Inventory

A current inventory of all vendors with their risk classification and data access levels must be maintained and reviewed quarterly.

## 5. Enforcement

Engaging vendors without proper assessment and approval is prohibited and may result in disciplinary action.

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC5.1, CC5.2, CC9.2**""",
    },
    "risk_assessment_policy": {
        "name": "Risk Assessment Policy",
        "short_name": "RAP",
        "description": "Defines the risk management framework and assessment methodology",
        "mapped_controls": ["CC3.1", "CC3.2"],
        "content": """# Risk Assessment Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Risk Assessment Policy defines the methodology for identifying, analyzing, evaluating, and treating information security risks at {{ORG_NAME}}.

## 2. Scope

This policy applies to all information assets, systems, processes, and third-party relationships that could impact the confidentiality, integrity, or availability of company or customer data.

## 3. Policy Statements

### 3.1 Risk Management Framework

{{ORG_NAME}} adopts a risk management framework aligned with NIST SP 800-30 and ISO 27005, consisting of:
1. Risk Identification
2. Risk Analysis (Likelihood × Impact)
3. Risk Evaluation
4. Risk Treatment
5. Risk Monitoring and Review

### 3.2 Risk Identification

Risks are identified through:
- Annual enterprise risk assessments
- Vulnerability scanning and penetration testing
- Vendor risk assessments
- Threat intelligence monitoring
- Incident post-mortem analysis
- Internal audit findings
- Employee-reported concerns

### 3.3 Risk Analysis

Each risk is assessed on two dimensions:
- **Likelihood:** Low / Medium / High / Critical
- **Impact:** Low / Medium / High / Critical

The inherent risk score (before controls) and residual risk score (after controls) are both calculated.

### 3.4 Risk Treatment

For each identified risk, the organization selects one of four treatment strategies:
- **Mitigate:** Implement controls to reduce risk to an acceptable level
- **Transfer:** Share risk through insurance or contractual arrangements
- **Avoid:** Discontinue the activity creating the risk
- **Accept:** Acknowledge the risk when cost of mitigation exceeds potential impact

All "Accept" decisions for High or Critical risks must be approved by executive leadership.

### 3.5 Risk Register

A risk register is maintained documenting:
- Risk description and category
- Inherent and residual likelihood/impact scores
- Assigned risk owner
- Treatment strategy and status
- Control activities in place
- Review date and next scheduled review

### 3.6 Risk Monitoring

- The risk register is reviewed quarterly by the Security Team
- High and Critical risks are reviewed monthly
- Changes to the threat landscape trigger ad-hoc risk assessments
- Risk metrics are reported to leadership quarterly

## 4. Roles and Responsibilities

- **Executive Leadership:** Approves risk acceptance for High/Critical risks
- **Security Team:** Facilitates risk assessments, maintains the risk register
- **Risk Owners:** Monitor and manage assigned risks, implement treatment plans
- **All Employees:** Report identified risks and control failures

## 5. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC3.1, CC3.2**""",
    },
    "data_classification_policy": {
        "name": "Data Classification Policy",
        "short_name": "DCP",
        "description": "Defines data classification levels and handling requirements",
        "mapped_controls": ["CC6.1", "CC6.7"],
        "content": """# Data Classification Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Data Classification Policy establishes the framework for classifying, labeling, handling, and protecting information assets at {{ORG_NAME}} based on their sensitivity and criticality.

## 2. Scope

This policy applies to all information created, collected, processed, stored, or transmitted by {{ORG_NAME}}, regardless of format (digital, physical, or verbal).

## 3. Classification Levels

### 3.1 Public
Information approved for public release. Disclosure has no adverse impact.

Examples: Marketing materials, public website content, job postings.

### 3.2 Internal
Information intended for internal use only. Unauthorized disclosure may cause minor reputational or operational impact.

Examples: Internal policies, employee directories, project plans, meeting notes.

### 3.3 Confidential
Sensitive business information. Unauthorized disclosure may cause significant financial, legal, or competitive harm.

Examples: Customer contracts, financial reports, source code, business strategy, employee records.

### 3.4 Restricted
Highly sensitive information subject to regulatory protection or contractual obligation. Unauthorized disclosure may cause severe harm.

Examples: Customer PII, authentication credentials, encryption keys, payment card data, health information, trade secrets.

## 4. Handling Requirements

### 4.1 Storage
- Restricted data must be encrypted at rest using AES-256 or equivalent
- Confidential data must be stored on company-managed systems with access controls
- Internal data must not be stored on personal devices or unapproved cloud services

### 4.2 Transmission
- Restricted data must be encrypted in transit using TLS 1.2 or higher
- Restricted data must not be transmitted via unencrypted email
- Use of company-approved file sharing platforms for external sharing

### 4.3 Disposal
- Restricted and Confidential data must be securely deleted when no longer needed
- Physical documents containing Restricted data must be shredded
- Digital media must be sanitized per NIST SP 800-88 guidelines

### 4.4 Labeling
- Restricted documents must be clearly labeled as "RESTRICTED"
- Confidential documents should be labeled as "CONFIDENTIAL" where practical
- Automated data classification tools should be used where available

## 5. Data Retention

Data must be retained according to the Data Retention Schedule and applicable legal requirements. Data no longer required must be securely disposed.

## 6. Data Owner Responsibilities

Each data asset must have an assigned Data Owner responsible for:
- Classifying the data according to this policy
- Approving access requests
- Reviewing classification annually
- Ensuring proper handling and disposal

## 7. Enforcement

Unauthorized disclosure of Restricted or Confidential data must be reported immediately to the Security Team. Violations may result in disciplinary action.

## 8. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.1, CC6.7**""",
    },
    "business_continuity_policy": {
        "name": "Business Continuity and Disaster Recovery Policy",
        "short_name": "BCDR",
        "description": "Defines requirements for business continuity and disaster recovery planning",
        "mapped_controls": ["CC7.5"],
        "content": """# Business Continuity and Disaster Recovery Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Business Continuity and Disaster Recovery (BCDR) Policy defines the requirements for maintaining the availability of critical services and recovering from disruptive events at {{ORG_NAME}}.

## 2. Scope

This policy applies to all critical business processes, information systems, and supporting infrastructure required to deliver services to customers.

## 3. Policy Statements

### 3.1 Business Impact Analysis (BIA)

A BIA must be conducted annually to identify:
- Critical business functions and their dependencies
- Recovery Time Objectives (RTO) — maximum acceptable downtime
- Recovery Point Objectives (RPO) — maximum acceptable data loss
- Resource requirements for recovery

### 3.2 Business Continuity Plan (BCP)

The BCP must document:
- Critical function recovery procedures
- Roles and responsibilities of the recovery team
- Communication plan for internal and external stakeholders
- Alternate work arrangements (remote work, alternate sites)
- Priority order for restoring business functions

### 3.3 Disaster Recovery Plan (DRP)

The DRP must document:
- Technical recovery procedures for critical systems
- Backup and restore procedures
- Infrastructure provisioning (Infrastructure as Code)
- Database and data recovery procedures
- Application recovery sequences and dependencies

### 3.4 Backup Requirements

- Backups must be performed daily for all production data
- Backups must be stored in a geographically separate location
- Backup integrity must be tested monthly via restore drills
- Retention: 30 days of daily backups, 12 monthly backups, 7 annual backups

### 3.5 High Availability

Critical production systems must be designed for high availability:
- Redundant infrastructure across availability zones or regions
- Auto-scaling to handle load spikes
- Database replication with automatic failover
- Load balancing across multiple instances

### 3.6 Testing

- BCP tabletop exercises must be conducted annually
- DRP technical recovery tests must be conducted annually
- Test results must be documented and reviewed
- Gaps identified during testing must be remediated within 90 days

## 4. Roles and Responsibilities

- **BCDR Coordinator:** Maintains plans, schedules tests, coordinates response
- **IT Operations:** Executes technical recovery procedures
- **Department Heads:** Maintain department-level continuity procedures
- **Executive Leadership:** Declares disaster, approves plan activation

## 5. Plan Maintenance

BCP and DRP documents must be updated:
- After any significant system or organizational change
- After any test that reveals gaps
- At least annually

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC7.5**""",
    },
    "code_of_conduct_policy": {
        "name": "Code of Conduct and Ethics Policy",
        "short_name": "COCE",
        "description": "Defines ethical standards and expected behavior for all personnel",
        "mapped_controls": ["CC1.1", "CC1.2"],
        "content": """# Code of Conduct and Ethics Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Code of Conduct and Ethics Policy establishes the principles and standards of behavior expected of all {{ORG_NAME}} personnel. A strong ethical culture is foundational to trust, security, and SOC 2 compliance.

## 2. Scope

This policy applies to all employees, contractors, consultants, board members, and temporary workers of {{ORG_NAME}}.

## 3. Core Values and Principles

### 3.1 Integrity
We act with honesty and transparency in all business dealings. We do not misrepresent facts, conceal information, or engage in deceptive practices.

### 3.2 Respect
We treat all individuals with dignity and respect. Discrimination, harassment, and retaliation have no place at {{ORG_NAME}}.

### 3.3 Accountability
We take responsibility for our actions and decisions. When mistakes occur, we acknowledge them, learn from them, and take corrective action.

### 3.4 Confidentiality
We protect the confidentiality of company, customer, and employee information. Confidential information is never shared inappropriately, even after employment ends.

### 3.5 Compliance
We comply with all applicable laws, regulations, and contractual obligations. We follow company policies and procedures designed to ensure security and compliance.

## 4. Policy Statements

### 4.1 Conflicts of Interest

Employees must avoid situations where personal interests conflict with company interests. Potential conflicts must be disclosed to management immediately. This includes:
- Outside employment or business activities
- Financial interests in competitors, vendors, or customers
- Personal relationships influencing business decisions
- Gifts or entertainment from vendors exceeding nominal value

### 4.2 Anti-Bribery and Anti-Corruption

Bribery, kickbacks, and corruption in any form are strictly prohibited. This includes:
- Offering or accepting payments to influence business decisions
- Facilitating payments to government officials
- Gifts intended to secure improper advantage

### 4.3 Protection of Company Assets

Employees must protect company assets from theft, misuse, and damage. This includes:
- Physical assets (equipment, facilities)
- Information assets (data, intellectual property, trade secrets)
- Financial assets (funds, credit cards)
- Reputational assets (brand, customer trust)

### 4.4 Reporting Violations

Employees have a duty to report suspected violations of this Code of Conduct or any company policy. Reports may be made to:
- Direct manager
- Human Resources
- Security Team
- Anonymous reporting channel (if available)

{{ORG_NAME}} prohibits retaliation against anyone who reports concerns in good faith.

### 4.5 Social Responsibility

{{ORG_NAME}} is committed to:
- Environmental sustainability in our operations
- Diversity, equity, and inclusion in our workforce
- Ethical treatment of workers in our supply chain
- Data privacy and security for our customers

## 5. Investigation and Enforcement

All reported violations will be investigated promptly and confidentially to the extent possible. Violations may result in disciplinary action, up to and including termination of employment and legal action.

## 6. Acknowledgment

All personnel must acknowledge this Code of Conduct and Ethics Policy upon hire and annually thereafter.

## 7. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC1.1, CC1.2**""",
    },
    "logging_monitoring_policy": {
        "name": "Logging and Monitoring Policy",
        "short_name": "LMP",
        "description": "Defines requirements for system logging, monitoring, and alerting",
        "mapped_controls": ["CC7.1", "CC4.1", "CC6.1", "CC7.2"],
        "content": """# Logging and Monitoring Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Logging and Monitoring Policy defines the requirements for logging system events, monitoring security controls, and responding to alerts at {{ORG_NAME}}. Continuous monitoring is essential for detecting anomalies, supporting incident response, and demonstrating effective control operation for SOC 2.

## 2. Scope

This policy applies to all production systems, applications, network devices, cloud infrastructure, and security tools that process, store, or transmit company or customer data.

## 3. Policy Statements

### 3.1 Logging Requirements

The following events must be logged for all in-scope systems:
- Authentication events (successful and failed logins, logouts)
- Privileged account activity (administrator actions, role changes)
- System and application errors
- Data access events (reads, modifications, deletions of sensitive data)
- Configuration changes (firewall rules, IAM policies, system settings)
- Network connections (inbound and outbound, especially to external hosts)
- Service start, stop, and restart events

### 3.2 Log Content

Each log entry must include, at minimum:
- Timestamp with timezone (NTP-synchronized)
- Source system identifier (hostname, IP address, cloud resource ID)
- User or process identifier
- Event type and severity
- Description of the event
- Outcome (success or failure)

### 3.3 Log Retention

- Security logs must be retained for a minimum of 12 months
- Audit-relevant logs must be retained for minimum 12 months (or per contractual requirements)
- Logs must be stored in immutable storage to prevent tampering
- Archived logs must be available for retrieval within 24 hours

### 3.4 Monitoring and Alerting

The Security Team must implement monitoring coverage for:
- Failed login attempts exceeding a threshold (account lockout, brute force detection)
- Privileged account usage outside of normal patterns
- Unauthorized configuration changes
- Malware or intrusion detection alerts
- Data egress to unauthorized destinations
- System resource anomalies (CPU, memory, disk, network)

### 3.5 Alert Response

- Critical alerts must be acknowledged within 15 minutes
- High alerts must be acknowledged within 1 hour
- Medium alerts must be reviewed within 4 hours
- All alerts must be documented and tracked to resolution

### 3.6 Log Review

- Security logs must be reviewed daily for critical systems
- Access logs must be reviewed weekly
- A formal log review log must be maintained documenting review date, reviewer, and findings

### 3.7 Clock Synchronization

All systems must synchronize their clocks using NTP to a centralized time source. Time deviation must not exceed 5 seconds.

## 4. Roles and Responsibilities

- **Security Team:** Configures monitoring tools, responds to alerts, performs log reviews
- **IT Operations:** Ensures logging is enabled on all systems, maintains log storage
- **System Owners:** Ensure their systems generate required log events
- **Internal Audit:** Reviews log review records and monitoring coverage quarterly

## 5. Enforcement

Failure to enable required logging or respond to alerts within SLA must be reported. Repeated violations may result in disciplinary action.

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC7.1, CC4.1, CC6.1, CC7.2**""",
    },
    "backup_policy": {
        "name": "Backup and Recovery Policy",
        "short_name": "BRP",
        "description": "Defines backup frequency, retention, and recovery requirements for data and systems",
        "mapped_controls": ["CC6.4", "CC7.5", "CC6.6"],
        "content": """# Backup and Recovery Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Backup and Recovery Policy establishes the requirements for creating, storing, and testing backups of {{ORG_NAME}} data and system configurations. Adequate backup and recovery capabilities are essential for ensuring data availability and meeting SOC 2 commitments.

## 2. Scope

This policy applies to all production data, databases, system configurations, application code, and infrastructure-as-code definitions required to operate {{ORG_NAME}} services.

## 3. Policy Statements

### 3.1 Backup Frequency

- Production databases must be backed up at least daily
- File shares and document repositories must be backed up at least daily
- System configurations and infrastructure-as-code must be version-controlled and backed up with each change
- Application source code must be version-controlled and backed up continuously

### 3.2 Backup Types

- **Full backups:** Complete data set — weekly minimum
- **Incremental backups:** Changes since last full/differential — daily
- **Transaction log backups:** Continuous or hourly for databases requiring point-in-time recovery

### 3.3 Retention Requirements

- Daily backups: retained for minimum 30 days
- Weekly backups: retained for minimum 12 weeks
- Monthly backups: retained for minimum 12 months
- Annual backups: retained for minimum 7 years
- Backups containing customer data must meet contractual retention requirements

### 3.4 Storage and Encryption

- Backups must be stored in a geographically separate location from primary data
- At-rest encryption (AES-256 or equivalent) is required for all backups
- In-transit encryption (TLS 1.2+) is required during backup transfer
- Access to backup storage must be restricted to authorized personnel only

### 3.5 Backup Testing

- Backup integrity must be verified within 24 hours of each backup
- Full restore drills must be conducted at least quarterly
- Restore time objectives (RTO) must be measured and documented during each drill
- Test results must be documented and reviewed by management

### 3.6 Recovery Procedures

- Recovery procedures must be documented for each critical system
- Runbooks must include step-by-step restore instructions
- Contact information for recovery team members must be maintained and tested quarterly

## 4. Roles and Responsibilities

- **IT Operations:** Executes backups, monitors backup success/failure, conducts restore drills
- **System Owners:** Defines RTO/RPO for their systems, approves recovery procedures
- **Security Team:** Reviews backup encryption and access controls
- **Management:** Reviews backup test results and approves recovery plan changes

## 5. Enforcement

Backup failures must be investigated and resolved within 24 hours. Repeated backup failures must be escalated to management. Data loss due to failure to follow this policy may result in disciplinary action.

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.4, CC7.5, CC6.6**""",
    },
    "system_description": {
        "name": "System Description",
        "short_name": "SD",
        "description": "Master document describing the system, boundaries, controls, and how they satisfy SOC 2 Trust Services Criteria",
        "mapped_controls": ["CC1.1", "CC1.2", "CC1.3", "CC1.4", "CC2.1", "CC2.2", "CC2.3"],
        "content": """# System Description

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This System Description serves as the master document describing {{ORG_NAME}} information system, its boundaries, the security controls implemented, and how these controls satisfy the SOC 2 Trust Services Criteria. This document provides a comprehensive overview of the security posture for auditors, customers, and stakeholders.

## 2. System Description

### 2.1 System Overview

{{ORG_NAME}} operates a cloud-based information system that processes, stores, and transmits business and customer data. The system includes applications, databases, cloud infrastructure, networks, and supporting services necessary to deliver {{ORG_NAME}} services.

### 2.2 System Boundaries

The system boundary encompasses:
- Cloud infrastructure (compute, storage, networking, databases)
- Software applications and APIs
- Identity and access management systems
- Monitoring and logging infrastructure
- Backup and disaster recovery systems
- Third-party services integrated into the system

### 2.3 Data Flow

Data flows through the system via:
- User interactions through web and mobile interfaces
- API integrations with customer systems
- Automated data processing pipelines
- Third-party service integrations
- Backup and replication processes

## 3. Trust Services Criteria Mapping

### 3.1 Security (CC1 — CC9)

The Common Criteria (Security) are addressed through the following control categories:

**CC1 — Control Environment:** Code of Conduct, organizational structure, board oversight
**CC2 — Communication:** Internal and external communication of responsibilities, incident reporting channels
**CC3 — Risk Assessment:** Annual risk assessments, vendor risk management
**CC4 — Monitoring:** Continuous monitoring, log review, alert response
**CC5 — Vendor Management:** Vendor risk assessments, contract review, vendor monitoring
**CC6 — Logical and Physical Access:** Access control, authentication, encryption, data classification
**CC7 — Incident Response and Monitoring:** Incident response plan, logging, monitoring, BCDR
**CC8 — Change Management:** Change approval process, testing, deployment procedures
**CC9 — Risk Mitigation:** Business continuity, vendor oversight

### 3.2 Availability (A1)

Availability commitments are addressed through:
- Redundant infrastructure across availability zones
- Automated failover and disaster recovery
- Backup and restore procedures
- Capacity planning and auto-scaling
- Incident response and escalation procedures

### 3.3 Confidentiality (C1)

Confidentiality commitments are addressed through:
- Data classification and handling procedures
- Encryption at rest and in transit
- Access controls based on least privilege
- Data loss prevention monitoring
- Confidentiality agreements with personnel and vendors

### 3.4 Processing Integrity (PI1)

Processing integrity commitments are addressed through:
- Change management and testing procedures
- Input validation and error handling
- Automated monitoring of processing jobs
- Batch processing reconciliation
- Incident detection and correction procedures

### 3.5 Privacy (P1)

Privacy commitments are addressed through:
- Privacy notice and data handling policies
- Consent management procedures
- Data subject rights processes
- Data retention and disposal procedures
- Breach notification procedures

## 4. Roles and Responsibilities

- **Executive Leadership:** Overall accountability for security and compliance
- **Security Team:** Design, implement, and monitor security controls
- **System Owners:** Maintain system security and document changes
- **Internal Audit:** Independent evaluation of control effectiveness
- **Compliance Officer:** Oversee SOC 2 compliance and evidence collection
- **All Personnel:** Adhere to policies and report security concerns

## 5. Continuous Monitoring

{{ORG_NAME}} maintains continuous monitoring through:
- Security information and event management (SIEM)
- Vulnerability scanning and penetration testing
- Configuration compliance monitoring
- User activity monitoring
- Third-party monitoring and assessment

## 6. Review and Maintenance

This System Description is reviewed and updated at least annually or upon significant system change. All updates are tracked through change management.

**Satisfies SOC 2: CC1.1, CC1.2, CC1.3, CC1.4, CC2.1, CC2.2, CC2.3**""",
    },
    "vulnerability_patch_policy": {
        "name": "Vulnerability and Patch Management Policy",
        "short_name": "VPMP",
        "description": "Defines requirements for vulnerability scanning, assessment, and patch remediation",
        "mapped_controls": ["CC7.1"],
        "content": """# Vulnerability and Patch Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines requirements for identifying, evaluating, and remediating vulnerabilities across {{ORG_NAME}} information systems.

## 2. Scope

This policy applies to all servers, workstations, network devices, cloud resources, applications, and databases.

## 3. Vulnerability Scanning

All systems must be scanned for vulnerabilities at least monthly. Critical and high-severity findings must be reported within 24 hours.

## 4. Patch Management

Critical security patches must be applied within 14 days. High-severity within 30 days. Medium within 60 days. Emergency patches may be applied outside the change management window.

## 5. Exceptions

If a patch cannot be applied within the required timeframe, compensating controls must be documented and approved by the Security Team.

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC7.1**""",
    },
    "network_security_policy": {
        "name": "Network Security Policy",
        "short_name": "NSP",
        "description": "Defines requirements for network segmentation, boundary protection, and encryption",
        "mapped_controls": ["CC6.1", "CC6.6"],
        "content": """# Network Security Policy

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

## 6. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.1, CC6.6**""",
    },
    "physical_security_policy": {
        "name": "Physical and Environmental Security Policy",
        "short_name": "PESP",
        "description": "Defines requirements for physical access controls and environmental protections",
        "mapped_controls": ["CC6.6"],
        "content": """# Physical and Environmental Security Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines requirements for physical access controls and environmental protections for {{ORG_NAME}} facilities and equipment.

## 2. Scope

This policy applies to all facilities housing information systems, including offices, data centers, and server rooms.

## 3. Physical Access

Physical access to sensitive areas must be controlled via badge systems or equivalent. Access must be granted based on business need and reviewed quarterly. Visitors must be escorted and logged.

## 4. Environmental Protection

Facilities must have fire detection/suppression, climate control, and power backup (UPS/generator). Environmental monitoring must be in place for server rooms.

## 5. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.6**""",
    },
    "media_protection_policy": {
        "name": "Media Protection Policy",
        "short_name": "MPP",
        "description": "Defines requirements for protecting information on digital and physical media",
        "mapped_controls": ["CC6.6"],
        "content": """# Media Protection Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines requirements for protecting information stored on digital and physical media throughout its lifecycle.

## 2. Scope

This policy applies to all removable media, backup tapes, optical discs, USB drives, and hard drives containing company or customer data.

## 3. Media Handling

Media containing sensitive data must be encrypted. Removable media must be tracked and inventoried. Portable devices must use full-disk encryption.

## 4. Media Disposal

Media must be securely destroyed when no longer needed using approved methods. A certificate of destruction must be maintained.

## 5. Review

This policy is reviewed and updated at least annually.

**Satisfies SOC 2: CC6.6**""",
    },
    "maintenance_policy": {
        "name": "Maintenance Policy",
        "short_name": "MAP",
        "description": "Defines requirements for scheduled and emergency maintenance of information systems",
        "mapped_controls": ["CC6.6", "CC8.1"],
        "content": """# Maintenance Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines requirements for scheduled and emergency maintenance of {{ORG_NAME}} information systems and equipment.

## 2. Scope

This policy applies to all hardware, software, and infrastructure requiring periodic maintenance.

## 3. Scheduled Maintenance

System maintenance must be scheduled during approved maintenance windows. Maintenance must be documented including scope, duration, and outcome.

## 4. Remote Maintenance

Remote maintenance must use encrypted connections with MFA. Sessions must be logged and monitored. Remote access must be terminated upon completion.

## 5. Review

This policy is reviewed and updated at least annually.""",
    },
    "personnel_security_policy": {
        "name": "Personnel Security Policy",
        "short_name": "PSP",
        "description": "Defines requirements for personnel screening, security agreements, and termination",
        "mapped_controls": ["CC1.1", "CC1.4", "CC6.1"],
        "content": """# Personnel Security Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This policy defines requirements for personnel screening, security agreements, and termination procedures at {{ORG_NAME}}.

## 2. Scope

This policy applies to all employees, contractors, and temporary workers with access to company information systems.

## 3. Screening

Personnel must undergo background screening prior to being granted access to sensitive systems. Screening level must be commensurate with role sensitivity.

## 4. Security Agreements

All personnel must sign confidentiality agreements and acknowledge security policies upon hire and annually.

## 5. Termination

Access must be revoked within 24 hours of termination. Exit interviews must review security obligations. Return of all company property must be verified.

## 6. Review

This policy is reviewed and updated at least annually.""",
    },
    "information_security_policy": {
        "name": "Information Security Policy",
        "short_name": "ISP",
        "description": "Overarching policy that defines the information security program framework",
        "mapped_controls": ["CC1.1", "CC1.2"],
        "content": """# Information Security Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Information Security Policy establishes the overarching framework for protecting the confidentiality, integrity, and availability of {{ORG_NAME}} information assets. All other security policies derive from this document.

## 2. Scope

This policy applies to all information systems, networks, applications, data, personnel, and third-party services that process, store, or transmit {{ORG_NAME}} or customer information.

## 3. Information Security Objectives

- Protect the confidentiality of sensitive and regulated data
- Maintain the integrity of information and processing systems
- Ensure the availability of critical systems and data
- Comply with applicable legal, regulatory, and contractual requirements

## 4. Security Governance

The Security Team is responsible for maintaining the information security program. Management is responsible for ensuring policy adherence within their teams. All personnel are responsible for understanding and following security policies.

## 5. Risk Management

Information security risks are identified, assessed, and treated through a formal risk management process per the Risk Assessment Policy. Residual risks are accepted by management.

## 6. Continuous Improvement

The information security program is reviewed at least annually. Controls are tested and improved based on risk assessment results, incident findings, and audit observations.

## 7. Review

This policy is reviewed and updated at least annually.""",
    },
    "asset_management_policy": {
        "name": "Asset Management Policy",
        "short_name": "AMP",
        "description": "Defines requirements for tracking, classifying, and protecting information assets",
        "mapped_controls": ["CC6.1"],
        "content": """# Asset Management Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Asset Management Policy defines the requirements for identifying, classifying, tracking, and protecting information assets throughout their lifecycle.

## 2. Scope

This policy applies to all hardware, software, data, cloud resources, and information systems owned or operated by {{ORG_NAME}}.

## 3. Asset Inventory

An asset inventory must be maintained covering: servers, endpoints, cloud assets, applications, databases, and SaaS services. Each asset must record: owner, type, location, data classification, criticality, and status.

## 4. Asset Classification

Assets are classified based on the data they process, store, or transmit. Classification levels follow the Data Classification Policy. Assets handling regulated data are flagged for enhanced controls.

## 5. Asset Lifecycle

- **Procurement:** Security requirements assessed before acquisition
- **Onboarding:** Asset added to inventory, baseline security controls applied
- **Operation:** Continuous monitoring, vulnerability management, and patching
- **Decommissioning:** Data securely wiped, certificates revoked, inventory updated

## 6. Criticality

Assets are assigned a criticality level (Low, Medium, High, Critical) based on impact to business operations and data sensitivity. Critical and High assets receive priority monitoring and recovery planning.

## 7. Review

Asset inventory is reviewed quarterly. This policy is reviewed and updated at least annually.""",
    },
    "mobile_device_policy": {
        "name": "Mobile Device and BYOD Policy",
        "short_name": "MDP",
        "description": "Defines security requirements for mobile devices and bring your own device (BYOD)",
        "mapped_controls": ["CC6.1", "CC6.6"],
        "content": """# Mobile Device and BYOD Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Mobile Device and BYOD Policy establishes security requirements for mobile devices that access {{ORG_NAME}} information systems.

## 2. Scope

This policy applies to all company-issued mobile devices and personal devices used to access company data, email, or applications (BYOD).

## 3. Device Requirements

- Devices must be protected by a passcode or biometric lock
- Full-disk encryption must be enabled
- Operating system and applications must be kept current with security patches
- Jailbroken or rooted devices are prohibited from accessing company systems
- Remote wipe capability must be enabled

## 4. BYOD Provisions

Personal devices used for work must enroll in mobile device management (MDM). Company data may be selectively wiped upon termination without affecting personal data.

## 5. Prohibited Actions

- Storing company credentials in unencrypted notes or files
- Connecting to unsecured public Wi-Fi without VPN
- Installing applications from untrusted sources
- Disabling security controls or device management profiles

## 6. Loss or Theft

Lost or stolen devices must be reported immediately. The company will initiate remote lock and wipe procedures upon notification.

## 7. Review

This policy is reviewed and updated at least annually.""",
    },
    "secure_development_policy": {
        "name": "Secure Software Development Policy",
        "short_name": "SSDP",
        "description": "Defines security requirements throughout the software development lifecycle",
        "mapped_controls": ["CC8.1"],
        "content": """# Secure Software Development Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Secure Software Development Policy defines security requirements for the design, development, testing, and deployment of software at {{ORG_NAME}}.

## 2. Scope

This policy applies to all software developed by or for {{ORG_NAME}}, including internal tools, customer-facing applications, APIs, infrastructure-as-code, and CI/CD pipelines.

## 3. Secure Development Lifecycle

Security is integrated into each phase of development:
- **Design:** Threat modeling, security requirements definition
- **Development:** Secure coding standards, dependency scanning, pre-commit hooks
- **Testing:** Static analysis (SAST), software composition analysis (SCA), unit and integration testing
- **Review:** Peer code review required for all changes
- **Deployment:** Automated deployment with security gates

## 4. Code Review

All code changes require peer review before merging. At least one reviewer must not be the author. Security-sensitive changes require Security Team review.

## 5. Dependency Management

Third-party dependencies are scanned for known vulnerabilities before inclusion. Critical and High severity vulnerabilities must be remediated before production deployment.

## 6. Secrets Management

Credentials, API keys, and tokens must not be committed to source code. Secrets must be stored in an approved secrets management solution.

## 7. Deployment Security

Deployments follow the Change Management Policy. Production access requires MFA and is logged. Immutable deployment patterns are preferred.

## 8. Review

This policy is reviewed and updated at least annually.""",
    },
    "privacy_policy": {
        "name": "Privacy Policy",
        "short_name": "PP",
        "description": "Defines personal data handling and privacy protection requirements",
        "mapped_controls": [f"P{i}.1" for i in range(1, 9)],
        "content": """# Privacy Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Privacy Policy establishes the principles and requirements for the collection, use, storage, processing, and disclosure of personal data by {{ORG_NAME}}.

## 2. Scope

This policy applies to all systems, processes, and personnel that collect, process, or store personal data of customers, employees, or other individuals.

## 3. Privacy Principles

- **Notice:** Individuals are informed of data collection purposes and practices
- **Choice:** Individuals are given choices regarding data use and sharing
- **Consent:** Consent is obtained prior to data collection where required
- **Purpose Limitation:** Data is collected and used only for specified purposes
- **Data Minimization:** Only necessary data is collected
- **Accuracy:** Personal data is kept accurate and up to date
- **Retention:** Data is retained only as long as necessary per the Data Retention Schedule
- **Security:** Personal data is protected with appropriate technical and organizational measures
- **Access:** Individuals may access and request correction of their personal data

## 4. Data Subject Rights

Requests for access, correction, deletion, or portability of personal data are processed within applicable legal timeframes.

## 5. Cross-Border Transfers

Personal data transferred across borders is protected through appropriate safeguards including Standard Contractual Clauses or equivalent mechanisms.

## 6. Breach Notification

Personal data breaches are assessed for notification requirements per applicable regulations. Affected individuals and regulators are notified within required timeframes.

## 7. Review

This policy is reviewed and updated at least annually.""",
    },
    "availability_policy": {
        "name": "Availability Policy",
        "short_name": "AP",
        "description": "Defines system availability targets and continuity requirements",
        "mapped_controls": ["A1.1", "A1.2"],
        "content": """# Availability Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Availability Policy defines the requirements for maintaining the availability of {{ORG_NAME}} systems and services in accordance with contractual commitments and business needs.

## 2. Scope

This policy applies to all production systems, applications, and infrastructure components that support customer-facing services and internal business operations.

## 3. Availability Targets

Service availability targets are defined in customer agreements and SLAs. Internal targets for critical systems are documented in the Business Continuity Plan. Performance against targets is measured and reported monthly.

## 4. Monitoring and Measurement

System availability is monitored continuously using automated tools. Outages, degradation events, and maintenance windows are tracked. Availability percentage is calculated monthly excluding planned maintenance.

## 5. Capacity Management

System capacity is monitored and reviewed to ensure sufficient resources to meet demand. Capacity planning includes peak load analysis, growth projections, and proactive scaling.

## 6. Maintenance Windows

Planned maintenance is scheduled during defined maintenance windows. Customer notice is provided per SLA requirements. Emergency maintenance is approved by management and communicated as soon as practical.

## 7. Incident Response

Availability incidents follow the Incident Response Policy. Critical outages escalate to the Incident Response Team within 15 minutes.

## 8. Review

This policy is reviewed and updated at least annually.""",
    },
    "processing_integrity_policy": {
        "name": "Processing Integrity Policy",
        "short_name": "PIP",
        "description": "Defines requirements for accurate, complete, timely, and authorized data processing",
        "mapped_controls": [f"PI1.{i}" for i in range(1, 6)],
        "content": """# Processing Integrity Policy

**Organization:** {{ORG_NAME}}
**Version:** 1.0
**Effective Date:** {{DATE}}

## 1. Purpose

This Processing Integrity Policy defines the requirements for ensuring that data processing is complete, accurate, timely, and properly authorized.

## 2. Scope

This policy applies to all systems and processes that collect, process, transmit, or report data used for customer services, financial reporting, and operational decisions.

## 3. Processing Principles

- **Completeness:** All valid transactions are processed without omission
- **Accuracy:** Data is processed correctly and errors are detected and corrected
- **Timeliness:** Processing occurs within defined time windows
- **Authorization:** Processing is performed only by authorized parties

## 4. Input Validation

Data inputs are validated at system boundaries to ensure accuracy and completeness. Validation includes format checks, range validation, and duplicate detection.

## 5. Processing Controls

Automated controls verify processing completeness including record counts, hash totals, sequence checks, and exception reporting. Processing failures are logged and alerted.

## 6. Error Handling

Processing errors are logged with sufficient detail for investigation. Correction procedures are documented. Material errors are reviewed by management.

## 7. Output Verification

System outputs are verified against inputs periodically. Reports include control totals and reconciliation information.

## 8. Review

This policy is reviewed and updated at least annually.""",
    },
}

TEMPLATE_LIST: List[Dict] = [
    {
        "key": k,
        "name": v["name"],
        "short_name": v["short_name"],
        "description": v["description"],
        "mapped_controls": v["mapped_controls"],
    }
    for k, v in TEMPLATES.items()
]
