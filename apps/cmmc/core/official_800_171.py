"""
Official NIST SP 800-171 Rev 2 and SP 800-171A data extracted from the authoritative NIST PDFs.

Source files:
  - docs/NIST.SP.800-171r2.pdf (110 CUI security requirements)
  - docs/NIST.SP.800-171A.pdf (assessment objectives with [a][b][c] determination statements)

Regenerated from docs/NIST.SP.800-171A.pdf via pdftotext so determination
statements are complete (not truncated mid-sentence).
"""

from __future__ import annotations

from typing import Any, Dict, List


FAMILY_NAMES = {
    "AC": "Access Control",
    "AT": "Awareness and Training",
    "AU": "Audit and Accountability",
    "CA": "Security Assessment",
    "CM": "Configuration Management",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PE": "Physical Protection",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
}

# Official assessment objectives from NIST SP 800-171A
# 110 controls / 320 assessment objectives
OFFICIAL_OBJECTIVES: Dict[str, List[tuple[str, str]]] = {
    "AC.L2-3.1.1": [
        ("a", "authorized users are identified."),
        ("b", "processes acting on behalf of authorized users are identified."),
        ("c", "devices (and other systems) authorized to connect to the system are identified."),
        ("d", "system access is limited to authorized users."),
        ("e", "system access is limited to processes acting on behalf of authorized users."),
        ("f", "system access is limited to authorized devices (including other systems)."),
    ],
    "AC.L2-3.1.2": [
        ("a", "the types of transactions and functions that authorized users are permitted to execute are defined."),
        ("b", "system access is limited to the defined types of transactions and functions for authorized users."),
    ],
    "AC.L2-3.1.3": [
        ("a", "information flow control policies are defined."),
        ("b", "methods and enforcement mechanisms for controlling the flow of CUI are defined."),
        ("c", "designated sources and destinations (e.g., networks, individuals, and devices) for CUI within the system and between interconnected systems are identified."),
        ("d", "authorizations for controlling the flow of CUI are defined."),
        ("e", "approved authorizations for controlling the flow of CUI are enforced."),
    ],
    "AC.L2-3.1.4": [
        ("a", "the duties of individuals requiring separation are defined."),
        ("b", "responsibilities for duties that require separation are assigned to separate individuals."),
        ("c", "access privileges that enable individuals to exercise the duties that require separation are granted to separate individuals."),
    ],
    "AC.L2-3.1.5": [
        ("a", "privileged accounts are identified."),
        ("b", "access to privileged accounts is authorized in accordance with the principle of least privilege."),
        ("c", "security functions are identified."),
        ("d", "access to security functions is authorized in accordance with the principle of."),
    ],
    "AC.L2-3.1.6": [
        ("a", "nonsecurity functions are identified."),
        ("b", "users are required to use non-privileged accounts or roles when accessing nonsecurity functions."),
    ],
    "AC.L2-3.1.7": [
        ("a", "privileged functions are defined."),
        ("b", "non-privileged users are defined."),
        ("c", "non-privileged users are prevented from executing privileged functions."),
        ("d", "the execution of privileged functions is captured in audit logs."),
    ],
    "AC.L2-3.1.8": [
        ("a", "the means of limiting unsuccessful logon attempts is defined."),
        ("b", "the defined means of limiting unsuccessful logon attempts is implemented."),
    ],
    "AC.L2-3.1.9": [
        ("a", "privacy and security notices required by CUI-specified rules are identified, consistent, and associated with the specific CUI category."),
        ("b", "privacy and security notices are displayed."),
    ],
    "AC.L2-3.1.10": [
        ("a", "the period of inactivity after which the system initiates a session lock is defined."),
        ("b", "access to the system and viewing of data is prevented by initiating a session lock after the defined period of inactivity."),
        ("c", "previously visible information is concealed via a pattern-hiding display after the defined period of inactivity."),
    ],
    "AC.L2-3.1.11": [
        ("a", "conditions requiring a user session to terminate are defined."),
        ("b", "a user session is automatically terminated after any of the defined conditions occur."),
    ],
    "AC.L2-3.1.12": [
        ("a", "remote access sessions are permitted."),
        ("b", "the types of permitted remote access are identified."),
        ("c", "remote access sessions are controlled."),
        ("d", "remote access sessions are monitored."),
    ],
    "AC.L2-3.1.13": [
        ("a", "sessions are identified. cryptographic mechanisms to protect the confidentiality of remote access."),
        ("b", "sessions are implemented."),
    ],
    "AC.L2-3.1.14": [
        ("a", "managed access control points are identified and implemented."),
        ("b", "remote access is routed through managed network access control points."),
    ],
    "AC.L2-3.1.15": [
        ("a", "privileged commands authorized for remote execution are identified."),
        ("b", "security-relevant information authorized to be accessed remotely is identified."),
        ("c", "the execution of the identified privileged commands via remote access is authorized."),
        ("d", "access to the identified security-relevant information via remote access is authorized."),
    ],
    "AC.L2-3.1.16": [
        ("a", "wireless access points are identified."),
        ("b", "wireless access is authorized prior to allowing such connections."),
    ],
    "AC.L2-3.1.17": [
        ("a", "wireless access to the system is protected using authentication."),
        ("b", "wireless access to the system is protected using encryption."),
    ],
    "AC.L2-3.1.18": [
        ("a", "mobile devices that process, store, or transmit CUI are identified."),
        ("b", "mobile device connections are authorized."),
        ("c", "mobile device connections are monitored and logged."),
    ],
    "AC.L2-3.1.19": [
        ("a", "mobile devices and mobile computing platforms that process, store, or transmit CUI are identified."),
        ("b", "encryption is employed to protect CUI on identified mobile devices and mobile computing platforms."),
    ],
    "AC.L2-3.1.20": [
        ("a", "connections to external systems are identified."),
        ("b", "the use of external systems is identified."),
        ("c", "connections to external systems are verified."),
        ("d", "the use of external systems is verified."),
        ("e", "connections to external systems are controlled/limited."),
        ("f", "the use of external systems is controlled/limited."),
    ],
    "AC.L2-3.1.21": [
        ("a", "the use of portable storage devices containing CUI on external systems is identified and documented."),
        ("b", "limits on the use of portable storage devices containing CUI on external systems are defined."),
        ("c", "the use of portable storage devices containing CUI on external systems is limited as defined."),
    ],
    "AC.L2-3.1.22": [
        ("a", "individuals authorized to post or process information on publicly accessible systems are identified."),
        ("b", "procedures to ensure CUI is not posted or processed on publicly accessible systems are identified."),
        ("c", "a review process is in place prior to posting of any content to publicly accessible systems."),
        ("d", "content on publicly accessible systems is reviewed to ensure that it does not include CUI."),
        ("e", "mechanisms are in place to remove and address improper posting of CUI."),
    ],
    "AT.L2-3.2.1": [
        ("a", "security risks associated with organizational activities involving CUI are identified."),
        ("b", "policies, standards, and procedures related to the security of the system are identified."),
        ("c", "managers, systems administrators, and users of the system are made aware of the security risks associated with their activities."),
        ("d", "managers, systems administrators, and users of the system are made aware of the applicable policies, standards, and procedures related to the security of the system."),
    ],
    "AT.L2-3.2.2": [
        ("a", "information security-related duties, roles, and responsibilities are defined."),
        ("b", "information security-related duties, roles, and responsibilities are assigned to designated personnel."),
        ("c", "personnel are adequately trained to carry out their assigned information security-related duties, roles, and responsibilities."),
    ],
    "AT.L2-3.2.3": [
        ("a", "potential indicators associated with insider threats are identified."),
        ("b", "security awareness training on recognizing and reporting potential indicators of insider threat is provided to managers and employees."),
    ],
    "AU.L2-3.3.1": [
        ("a", "audit logs needed (i.e., event types to be logged) to enable the monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity are specified."),
        ("b", "the content of audit records needed to support monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity is defined."),
        ("c", "audit records are created (generated)."),
        ("d", "audit records, once created, contain the defined content."),
        ("e", "retention requirements for audit records are defined."),
        ("f", "audit records are retained as defined."),
    ],
    "AU.L2-3.3.2": [
        ("a", "the content of the audit records needed to support the ability to uniquely trace users to their actions is defined."),
        ("b", "audit records, once created, contain the defined content."),
    ],
    "AU.L2-3.3.3": [
        ("a", "a process for determining when to review logged events is defined."),
        ("b", "event types being logged are reviewed in accordance with the defined review process."),
        ("c", "event types being logged are updated based on the review."),
    ],
    "AU.L2-3.3.4": [
        ("a", "personnel or roles to be alerted in the event of an audit logging process failure are identified."),
        ("b", "types of audit logging process failures for which alert will be generated are defined."),
        ("c", "identified personnel or roles are alerted in the event of an audit logging process failure."),
    ],
    "AU.L2-3.3.5": [
        ("a", "audit record review, analysis, and reporting processes for investigation and response to indications of unlawful, unauthorized, suspicious, or unusual activity are defined."),
        ("b", "defined audit record review, analysis, and reporting processes are correlated."),
    ],
    "AU.L2-3.3.6": [
        ("a", "an audit record reduction capability that supports on-demand analysis is provided."),
        ("b", "a report generation capability that supports on-demand reporting is provided."),
    ],
    "AU.L2-3.3.7": [
        ("a", "internal system clocks are used to generate time stamps for audit records."),
        ("b", "an authoritative source with which to compare and synchronize internal system clocks is specified."),
        ("c", "internal system clocks used to generate time stamps for audit records are compared to and synchronized with the specified authoritative time source."),
    ],
    "AU.L2-3.3.8": [
        ("a", "audit information is protected from unauthorized access."),
        ("b", "audit information is protected from unauthorized modification."),
        ("c", "audit information is protected from unauthorized deletion."),
        ("d", "audit logging tools are protected from unauthorized access."),
        ("e", "audit logging tools are protected from unauthorized modification."),
        ("f", "audit logging tools are protected from unauthorized deletion."),
    ],
    "AU.L2-3.3.9": [
        ("a", "a subset of privileged users granted access to manage audit logging functionality is defined."),
        ("b", "management of audit logging functionality is limited to the defined subset of privileged users."),
    ],
    "CM.L2-3.4.1": [
        ("a", "a baseline configuration is established."),
        ("b", "the baseline configuration includes hardware, software, firmware, and."),
        ("c", "the baseline configuration is maintained (reviewed and updated) throughout the system development life cycle."),
        ("d", "a system inventory is established."),
        ("e", "the system inventory includes hardware, software, firmware, and documentation."),
        ("f", "the inventory is maintained (reviewed and updated) throughout the system development life cycle."),
    ],
    "CM.L2-3.4.2": [
        ("a", "security configuration settings for information technology products employed in the system are established and included in the baseline configuration."),
        ("b", "security configuration settings for information technology products employed in the system are enforced."),
    ],
    "CM.L2-3.4.3": [
        ("a", "changes to the system are tracked."),
        ("b", "changes to the system are reviewed."),
        ("c", "changes to the system are approved or disapproved."),
        ("d", "changes to the system are logged."),
    ],
    "CM.L2-3.4.4": [
        ("a", "Determine if the security impact of changes to the system is analyzed prior to implementation."),
    ],
    "CM.L2-3.4.5": [
        ("a", "physical access restrictions associated with changes to the system are defined."),
        ("b", "physical access restrictions associated with changes to the system are documented."),
        ("c", "physical access restrictions associated with changes to the system are approved."),
        ("d", "physical access restrictions associated with changes to the system are enforced."),
        ("e", "logical access restrictions associated with changes to the system are defined."),
        ("f", "logical access restrictions associated with changes to the system are documented."),
        ("g", "logical access restrictions associated with changes to the system are approved."),
        ("h", "logical access restrictions associated with changes to the system are enforced."),
    ],
    "CM.L2-3.4.6": [
        ("a", "essential system capabilities are defined based on the principle of least functionality."),
        ("b", "the system is configured to provide only the defined essential capabilities."),
    ],
    "CM.L2-3.4.7": [
        ("a", "essential programs are defined."),
        ("b", "the use of nonessential programs is defined."),
        ("c", "the use of nonessential programs is restricted, disabled, or prevented as defined."),
        ("d", "essential functions are defined."),
        ("e", "the use of nonessential functions is defined."),
        ("f", "the use of nonessential functions is restricted, disabled, or prevented as defined."),
        ("g", "essential ports are defined."),
        ("h", "the use of nonessential ports is defined."),
        ("i", "the use of nonessential ports is restricted, disabled, or prevented as defined."),
        ("j", "essential protocols are defined."),
        ("k", "the use of nonessential protocols is defined."),
        ("l", "the use of nonessential protocols is restricted, disabled, or prevented as defined."),
        ("m", "essential services are defined."),
        ("n", "the use of nonessential services is defined."),
        ("o", "the use of nonessential services is restricted, disabled, or prevented as defined."),
    ],
    "CM.L2-3.4.8": [
        ("a", "a policy specifying whether whitelisting or blacklisting is to be implemented is specified."),
        ("b", "the software allowed to execute under whitelisting or denied use under blacklisting is specified."),
        ("c", "whitelisting to allow the execution of authorized software or blacklisting to prevent the use of unauthorized software is implemented as specified."),
    ],
    "CM.L2-3.4.9": [
        ("a", "a policy for controlling the installation of software by users is established."),
        ("b", "installation of software by users is controlled based on the established policy."),
        ("c", "installation of software by users is monitored."),
    ],
    "IA.L2-3.5.1": [
        ("a", "system users are identified."),
        ("b", "processes acting on behalf of users are identified."),
        ("c", "devices accessing the system are identified."),
    ],
    "IA.L2-3.5.2": [
        ("a", "the identity of each user is authenticated or verified as a prerequisite to system access."),
        ("b", "the identity of each process acting on behalf of a user is authenticated or verified as a prerequisite to system access."),
        ("c", "the identity of each device accessing or connecting to the system is authenticated or verified as a prerequisite to system access."),
    ],
    "IA.L2-3.5.3": [
        ("a", "privileged accounts are identified."),
        ("b", "multifactor authentication is implemented for local access to privileged accounts."),
        ("c", "multifactor authentication is implemented for network access to privileged accounts."),
        ("d", "multifactor authentication is implemented for network access to non-privileged accounts."),
    ],
    "IA.L2-3.5.4": [
        ("a", "Determine if replay-resistant authentication mechanisms are implemented for network account access to privileged and non-privileged accounts."),
    ],
    "IA.L2-3.5.5": [
        ("a", "a period within which identifiers cannot be reused is defined."),
        ("b", "reuse of identifiers is prevented within the defined period."),
    ],
    "IA.L2-3.5.6": [
        ("a", "a period of inactivity after which an identifier is disabled is defined."),
        ("b", "identifiers are disabled after the defined period of inactivity."),
    ],
    "IA.L2-3.5.7": [
        ("a", "password complexity requirements are defined."),
        ("b", "password change of character requirements are defined."),
        ("c", "minimum password complexity requirements as defined are enforced when new passwords are created."),
        ("d", "minimum password change of character requirements as defined are enforced when new passwords are created."),
    ],
    "IA.L2-3.5.8": [
        ("a", "the number of generations during which a password cannot be reused is specified."),
        ("b", "reuse of passwords is prohibited during the specified number of generations."),
    ],
    "IA.L2-3.5.9": [
        ("a", "Determine if an immediate change to a permanent password is required when a temporary password is used for system logon."),
    ],
    "IA.L2-3.5.10": [
        ("a", "passwords are cryptographically protected in storage."),
        ("b", "passwords are cryptographically protected in transit."),
    ],
    "IA.L2-3.5.11": [
        ("a", "Determine if authentication information is obscured during the authentication process."),
    ],
    "IR.L2-3.6.1": [
        ("a", "an operational incident-handling capability is established."),
        ("b", "the operational incident-handling capability includes preparation."),
        ("c", "the operational incident-handling capability includes detection."),
        ("d", "the operational incident-handling capability includes analysis."),
        ("e", "the operational incident-handling capability includes containment."),
        ("f", "the operational incident-handling capability includes recovery."),
        ("g", "the operational incident-handling capability includes user response activities."),
    ],
    "IR.L2-3.6.2": [
        ("a", "incidents are tracked."),
        ("b", "incidents are documented."),
        ("c", "authorities to whom incidents are to be reported are identified."),
        ("d", "organizational officials to whom incidents are to be reported are identified."),
        ("e", "identified authorities are notified of incidents."),
        ("f", "identified organizational officials are notified of incidents."),
    ],
    "IR.L2-3.6.3": [
        ("a", "Determine if the incident response capability is tested."),
    ],
    "MA.L2-3.7.1": [
        ("a", "Determine if system maintenance is performed."),
    ],
    "MA.L2-3.7.2": [
        ("a", "tools used to conduct system maintenance are controlled."),
        ("b", "techniques used to conduct system maintenance are controlled."),
        ("c", "mechanisms used to conduct system maintenance are controlled."),
        ("d", "personnel used to conduct system maintenance are controlled."),
    ],
    "MA.L2-3.7.3": [
        ("a", "Determine if equipment to be removed from organizational spaces for off-site maintenance is sanitized of any CUI."),
    ],
    "MA.L2-3.7.4": [
        ("a", "Determine if media containing diagnostic and test programs are checked for malicious code before being used in organizational systems that process, store, or transmit CUI."),
    ],
    "MA.L2-3.7.5": [
        ("a", "multifactor authentication is used to establish nonlocal maintenance sessions via external network connections."),
        ("b", "nonlocal maintenance sessions established via external network connections are terminated when nonlocal maintenance is complete."),
    ],
    "MA.L2-3.7.6": [
        ("a", "Determine if maintenance personnel without required access authorization are supervised during maintenance activities."),
    ],
    "MP.L2-3.8.1": [
        ("a", "paper media containing CUI is physically controlled."),
        ("b", "digital media containing CUI is physically controlled."),
        ("c", "paper media containing CUI is securely stored."),
        ("d", "digital media containing CUI is securely stored."),
    ],
    "MP.L2-3.8.2": [
        ("a", "Determine if access to CUI on system media is limited to authorized users."),
    ],
    "MP.L2-3.8.3": [
        ("a", "system media containing CUI is sanitized or destroyed before disposal."),
        ("b", "system media containing CUI is sanitized before it is released for reuse."),
    ],
    "MP.L2-3.8.4": [
        ("a", "media containing CUI is marked with applicable CUI markings."),
        ("b", "media containing CUI is marked with distribution limitations."),
    ],
    "MP.L2-3.8.5": [
        ("a", "access to media containing CUI is controlled."),
        ("b", "accountability for media containing CUI is maintained during transport outside of controlled areas."),
    ],
    "MP.L2-3.8.6": [
        ("a", "Determine if the confidentiality of CUI stored on digital media is protected during transport using cryptographic mechanisms or alternative physical safeguards."),
    ],
    "MP.L2-3.8.7": [
        ("a", "Determine if the use of removable media on system components is controlled."),
    ],
    "MP.L2-3.8.8": [
        ("a", "Determine if the use of portable storage devices is prohibited when such devices have no identifiable owner."),
    ],
    "MP.L2-3.8.9": [
        ("a", "Determine if the confidentiality of backup CUI is protected at storage locations."),
    ],
    "PS.L2-3.9.1": [
        ("a", "Determine if individuals are screened prior to authorizing access to organizational systems containing CUI."),
    ],
    "PS.L2-3.9.2": [
        ("a", "a policy and/or process for terminating system access and any credentials coincident with personnel actions is established."),
        ("b", "system access and credentials are terminated consistent with personnel actions such as termination or transfer."),
        ("c", "the system is protected during and after personnel transfer actions."),
    ],
    "PE.L2-3.10.1": [
        ("a", "authorized individuals allowed physical access are identified."),
        ("b", "physical access to organizational systems is limited to authorized individuals."),
        ("c", "physical access to equipment is limited to authorized individuals."),
        ("d", "physical access to operating environments is limited to authorized individuals."),
    ],
    "PE.L2-3.10.2": [
        ("a", "the physical facility where organizational systems reside is protected."),
        ("b", "the support infrastructure for organizational systems is protected."),
        ("c", "the physical facility where organizational systems reside is monitored."),
        ("d", "the support infrastructure for organizational systems is monitored."),
    ],
    "PE.L2-3.10.3": [
        ("a", "visitors are escorted."),
        ("b", "visitor activity is monitored."),
    ],
    "PE.L2-3.10.4": [
        ("a", "Determine if audit logs of physical access are maintained."),
    ],
    "PE.L2-3.10.5": [
        ("a", "physical access devices are identified."),
        ("b", "physical access devices are controlled."),
        ("c", "physical access devices are managed."),
    ],
    "PE.L2-3.10.6": [
        ("a", "safeguarding measures for CUI are defined for alternate work sites."),
        ("b", "safeguarding measures for CUI are enforced for alternate work sites."),
    ],
    "RA.L2-3.11.1": [
        ("a", "the frequency to assess risk to organizational operations, organizational assets, and individuals is defined."),
        ("b", "risk to organizational operations, organizational assets, and individuals resulting from the operation of an organizational system that processes, stores, or transmits CUI is assessed with the defined frequency."),
    ],
    "RA.L2-3.11.2": [
        ("a", "the frequency to scan for vulnerabilities in organizational systems and applications is defined."),
        ("b", "vulnerability scans are performed on organizational systems with the defined frequency."),
        ("c", "vulnerability scans are performed on applications with the defined frequency."),
        ("d", "vulnerability scans are performed on organizational systems when new vulnerabilities are identified."),
        ("e", "vulnerability scans are performed on applications when new vulnerabilities are identified."),
    ],
    "RA.L2-3.11.3": [
        ("a", "vulnerabilities are identified."),
        ("b", "vulnerabilities are remediated in accordance with risk assessments."),
    ],
    "CA.L2-3.12.1": [
        ("a", "the frequency of security control assessments is defined."),
        ("b", "security controls are assessed with the defined frequency to determine if the controls are effective in their application."),
    ],
    "CA.L2-3.12.2": [
        ("a", "deficiencies and vulnerabilities to be addressed by the plan of action are identified."),
        ("b", "a plan of action is developed to correct identified deficiencies and reduce or eliminate identified vulnerabilities."),
        ("c", "the plan of action is implemented to correct identified deficiencies and reduce or eliminate identified vulnerabilities."),
    ],
    "CA.L2-3.12.3": [
        ("a", "Determine if security controls are monitored on an ongoing basis to ensure the continued effectiveness of those controls."),
    ],
    "CA.L2-3.12.4": [
        ("a", "a system security plan is developed."),
        ("b", "the system boundary is described and documented in the system security plan."),
        ("c", "the system environment of operation is described and documented in the system security plan."),
        ("d", "the security requirements identified and approved by the designated authority as non-applicable are identified."),
        ("e", "the method of security requirement implementation is described and documented in the system security plan."),
        ("f", "the relationship with or connection to other systems is described and documented in the system security plan."),
        ("g", "the frequency to update the system security plan is defined."),
        ("h", "system security plan is updated with the defined frequency."),
    ],
    "SC.L2-3.13.1": [
        ("a", "the external system boundary is defined."),
        ("b", "key internal system boundaries are defined."),
        ("c", "communications are monitored at the external system boundary."),
        ("d", "communications are monitored at key internal boundaries."),
        ("e", "communications are controlled at the external system boundary."),
        ("f", "communications are controlled at key internal boundaries."),
        ("g", "communications are protected at the external system boundary."),
        ("h", "communications are protected at key internal boundaries."),
    ],
    "SC.L2-3.13.2": [
        ("a", "architectural designs that promote effective information security are identified."),
        ("b", "software development techniques that promote effective information security are identified."),
        ("c", "systems engineering principles that promote effective information security are identified."),
        ("d", "identified architectural designs that promote effective information security are employed."),
        ("e", "identified software development techniques that promote effective information security are employed."),
        ("f", "identified systems engineering principles that promote effective information security are employed."),
    ],
    "SC.L2-3.13.3": [
        ("a", "user functionality is identified."),
        ("b", "system management functionality is identified."),
        ("c", "user functionality is separated from system management functionality."),
    ],
    "SC.L2-3.13.4": [
        ("a", "Determine if unauthorized and unintended information transfer via shared system resources is prevented."),
    ],
    "SC.L2-3.13.5": [
        ("a", "publicly accessible system components are identified."),
        ("b", "subnetworks for publicly accessible system components are physically or logically separated from internal networks."),
    ],
    "SC.L2-3.13.6": [
        ("a", "network communications traffic is denied by default."),
        ("b", "network communications traffic is allowed by exception."),
    ],
    "SC.L2-3.13.7": [
        ("a", "Determine if remote devices are prevented from simultaneously establishing non-remote connections with the system and communicating via some other connection to resources in external networks (i.e., split tunneling)."),
    ],
    "SC.L2-3.13.8": [
        ("a", "cryptographic mechanisms intended to prevent unauthorized disclosure of CUI are identified."),
        ("b", "alternative physical safeguards intended to prevent unauthorized disclosure of CUI are identified."),
        ("c", "either cryptographic mechanisms or alternative physical safeguards are implemented to prevent unauthorized disclosure of CUI during transmission."),
    ],
    "SC.L2-3.13.9": [
        ("a", "a period of inactivity to terminate network connections associated with communications sessions is defined."),
        ("b", "network connections associated with communications sessions are terminated at the end of the sessions."),
        ("c", "network connections associated with communications sessions are terminated."),
    ],
    "SC.L2-3.13.10": [
        ("a", "cryptographic keys are established whenever cryptography is employed."),
        ("b", "cryptographic keys are managed whenever cryptography is employed."),
    ],
    "SC.L2-3.13.11": [
        ("a", "Determine if FIPS-validated cryptography is employed to protect the confidentiality of CUI."),
    ],
    "SC.L2-3.13.12": [
        ("a", "collaborative computing devices are identified."),
        ("b", "collaborative computing devices provide indication to users of devices in use."),
        ("c", "remote activation of collaborative computing devices is prohibited."),
    ],
    "SC.L2-3.13.13": [
        ("a", "use of mobile code is controlled."),
        ("b", "use of mobile code is monitored."),
    ],
    "SC.L2-3.13.14": [
        ("a", "use of Voice over Internet Protocol (VoIP) technologies is controlled."),
        ("b", "use of Voice over Internet Protocol (VoIP) technologies is monitored."),
    ],
    "SC.L2-3.13.15": [
        ("a", "Determine if the authenticity of communications sessions is protected."),
    ],
    "SC.L2-3.13.16": [
        ("a", "Determine if the confidentiality of CUI at rest is protected."),
    ],
    "SI.L2-3.14.1": [
        ("a", "the time within which to identify system flaws is specified."),
        ("b", "system flaws are identified within the specified time frame."),
        ("c", "the time within which to report system flaws is specified."),
        ("d", "system flaws are reported within the specified time frame."),
        ("e", "the time within which to correct system flaws is specified."),
        ("f", "system flaws are corrected within the specified time frame."),
    ],
    "SI.L2-3.14.2": [
        ("a", "designated locations for malicious code protection are identified."),
        ("b", "protection from malicious code at designated locations is provided."),
    ],
    "SI.L2-3.14.3": [
        ("a", "response actions to system security alerts and advisories are identified."),
        ("b", "system security alerts and advisories are monitored."),
        ("c", "actions in response to system security alerts and advisories are taken."),
    ],
    "SI.L2-3.14.4": [
        ("a", "Determine if malicious code protection mechanisms are updated when new releases are available."),
    ],
    "SI.L2-3.14.5": [
        ("a", "the frequency for malicious code scans is defined."),
        ("b", "malicious code scans are performed with the defined frequency."),
        ("c", "real-time malicious code scans of files from external sources as files are downloaded, opened, or executed are performed."),
    ],
    "SI.L2-3.14.6": [
        ("a", "the system is monitored to detect attacks and indicators of potential attacks."),
        ("b", "inbound communications traffic is monitored to detect attacks and indicators of potential attacks."),
        ("c", "outbound communications traffic is monitored to detect attacks and indicators of potential attacks."),
    ],
    "SI.L2-3.14.7": [
        ("a", "authorized use of the system is defined."),
        ("b", "unauthorized use of the system is identified."),
    ],
}


# Note: get_effective_status() is for future objective-driven assessment.
# Do NOT auto-inject empty NOT_STARTED objectives onto answers or force
# status through this helper on demo load — that broke MET counts.


def build_control_objectives(control_id: str, answer: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Merge official 171A letters/text with any saved objective statuses from the answer."""
    catalog = OFFICIAL_OBJECTIVES.get(control_id) or []
    if not catalog:
        return []
    saved = {(o.get("letter") or ""): o for o in (answer or {}).get("objectives") or [] if isinstance(o, dict)}
    from guidance.objective_guidance import OBJECTIVE_DELIVERABLE_GUIDANCE
    guidance_map = OBJECTIVE_DELIVERABLE_GUIDANCE.get(control_id, {})
    out: List[Dict[str, Any]] = []
    for letter, text in catalog:
        prev = saved.get(letter) or {}
        g = guidance_map.get(letter, {})
        out.append({
            "letter": letter,
            "text": text,
            "status": prev.get("status") or "NOT_STARTED",
            "evidence_refs": list(prev.get("evidence_refs") or []),
            "notes": prev.get("notes") or "",
            "deliverable": g.get("deliverable", ""),
            "how": g.get("how", ""),
            "kind": g.get("kind", ""),
        })
    return out


def get_effective_status(answer: Dict[str, Any]) -> str:
    """Derive advisory status from assessment objectives when present.

    If objectives are missing/empty, returns the stored answer status unchanged.
    """
    if answer.get("override_active") and answer.get("override_justification"):
        raw = answer.get("status", "NOT STARTED")
        return raw.upper().strip() if isinstance(raw, str) else "NOT STARTED"

    objectives = answer.get("objectives") or []
    if not objectives:
        raw = answer.get("status", "NOT STARTED")
        return raw.upper().strip() if isinstance(raw, str) else "NOT STARTED"

    statuses = set()
    for o in objectives:
        s = (o.get("status") or "NOT_STARTED").upper().strip()
        if s in ("NOT_STARTED", "NOT STARTED"):
            statuses.add("NOT_STARTED")
        elif s in ("NA", "NOT APPLICABLE", "N/A"):
            statuses.add("NA")
        elif s == "MET":
            statuses.add("MET")
        elif s in ("NOT_MET", "NOT MET"):
            statuses.add("NOT MET")
        else:
            statuses.add("NOT_STARTED")

    # Incomplete set → keep stored status (do not demote MET demos)
    if "NOT_STARTED" in statuses:
        raw = answer.get("status", "NOT STARTED")
        return raw.upper().strip() if isinstance(raw, str) else "NOT STARTED"
    if statuses == {"NOT MET"} or "NOT MET" in statuses:
        return "NOT MET" if "MET" not in statuses else "IN PROGRESS"
    if statuses == {"MET"}:
        return "MET"
    if statuses == {"NA"}:
        return "NOT APPLICABLE"
    if "MET" in statuses:
        return "IN PROGRESS"
    raw = answer.get("status", "NOT STARTED")
    return raw.upper().strip() if isinstance(raw, str) else "NOT STARTED"

