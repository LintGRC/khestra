"""Per-objective deliverable guidance for NIST SP 800-171A assessment objectives.

Each entry maps a control ID + objective letter to what the assessor needs.
The `kind` field drives the label shown in the ControlDetail UI.
"""

OBJECTIVE_DELIVERABLE_GUIDANCE: dict[str, dict[str, dict[str, str]]] = {
    "AC.L2-3.1.1": {
        "a": {
            "deliverable": 'Authorized user list',
            "how": 'Examine: Access control policy; procedures addressing account management; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Authorized process list',
            "how": 'Examine: Access control policy; procedures addressing account management; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Authorized device list',
            "how": 'Examine: Access control policy; procedures addressing account management; system security plan',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'User access restriction rules',
            "how": 'Test: Organizational processes for managing system accounts; mechanisms for implementing account management',
            "kind": 'config',
        },
        "e": {
            "deliverable": 'Process access restriction rules',
            "how": 'Test: Organizational processes for managing system accounts; mechanisms for implementing account management',
            "kind": 'config',
        },
        "f": {
            "deliverable": 'Device access restriction rules',
            "how": 'Test: Organizational processes for managing system accounts; mechanisms for implementing account management',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.10": {
        "a": {
            "deliverable": 'Inactivity timeout policy',
            "how": 'Examine: Access control policy; procedures addressing session lock; procedures addressing identification and authentication',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Inactivity session lock configuration',
            "how": 'Test: Mechanisms implementing access control policy for session lock',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Session lock mechanism proof',
            "how": 'Examine: Access control policy; procedures addressing session lock Test: Mechanisms implementing access control policy for session lock',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.11": {
        "a": {
            "deliverable": 'Session termination policy',
            "how": 'Examine: Access control policy; procedures addressing session termination; system design documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Session termination configuration',
            "how": 'Examine: Access control policy; procedures addressing session termination Test: Mechanisms implementing user session termination',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.12": {
        "a": {
            "deliverable": 'Remote access policy',
            "how": 'Examine: Access control policy; procedures addressing remote access implementation and usage (including restrictions) Test: Remote access management capability for the system',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Permitted remote access type inventory',
            "how": 'Examine: Access control policy; procedures addressing remote access implementation and usage (including restrictions); configuration management plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Remote access control/enforcement configuration',
            "how": 'Test: Remote access management capability for the system',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Remote access session records',
            "how": 'Examine: Access control policy; procedures addressing remote access implementation and usage (including restrictions) Test: Remote access management capability for the system',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.13": {
        "a": {
            "deliverable": 'Remote access encryption mechanism policy',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Remote access session encryption configuration',
            "how": 'Test: Cryptographic mechanisms protecting confidentiality of remote access sessions',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.14": {
        "a": {
            "deliverable": 'Managed network access control point list',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Remote access routing configuration',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system Test: Mechanisms routing all remote accesses through managed network access control points',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.15": {
        "a": {
            "deliverable": 'Privileged remote command list',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system; system configuration settings and associated documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Remote-accessible information list',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system; system configuration settings and associated documentation',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Remote privileged command authorization records',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system Test: Mechanisms implementing remote access management',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Remote information access authorization records',
            "how": 'Examine: Access control policy; procedures addressing remote access to the system Test: Mechanisms implementing remote access management',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.16": {
        "a": {
            "deliverable": 'Wireless access point inventory',
            "how": 'Examine: Access control policy; configuration management plan; procedures addressing wireless access implementation and usage (including restrictions)',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Wireless access authorization records',
            "how": 'Examine: Access control policy; configuration management plan Test: Wireless access management capability for the system',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.17": {
        "a": {
            "deliverable": 'Wireless authentication configuration',
            "how": 'Test: Mechanisms implementing wireless access protections to the system',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Wireless encryption configuration',
            "how": 'Test: Mechanisms implementing wireless access protections to the system',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.18": {
        "a": {
            "deliverable": 'Mobile device inventory (CUI)',
            "how": 'Examine: Access control policy; authorizations for mobile device connections to organizational systems; procedures addressing access control for mobile device usage (including restrictions)',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Mobile device connection authorization records',
            "how": 'Examine: Access control policy; authorizations for mobile device connections to organizational systems Test: Access control capability authorizing mobile device connections to organizational systems',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Mobile device connection monitoring log records',
            "how": 'Examine: Access control policy; authorizations for mobile device connections to organizational systems Test: Access control capability authorizing mobile device connections to organizational systems',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.19": {
        "a": {
            "deliverable": 'Mobile computing platform inventory (CUI)',
            "how": 'Examine: Access control policy; procedures addressing access control for mobile devices; system design documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Mobile device CUI encryption configuration',
            "how": 'Test: Encryption mechanisms protecting confidentiality of information on mobile devices',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.2": {
        "a": {
            "deliverable": 'Authorized transaction and function list',
            "how": 'Examine: Access control policy; procedures addressing access enforcement Test: Mechanisms implementing access control policy',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Transaction access control rules',
            "how": 'Test: Mechanisms implementing access control policy',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.20": {
        "a": {
            "deliverable": 'External connection list',
            "how": 'Examine: Access control policy; procedures addressing the use of external systems; terms and conditions for external systems',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'External system usage policy',
            "how": 'Examine: Access control policy; procedures addressing the use of external systems; terms and conditions for external systems',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'External connection verification records',
            "how": 'Examine: Access control policy; procedures addressing the use of external systems Test: Mechanisms implementing terms and conditions on use of external systems',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'External system verification records',
            "how": 'Examine: Access control policy; procedures addressing the use of external systems Test: Mechanisms implementing terms and conditions on use of external systems',
            "kind": 'evidence',
        },
        "e": {
            "deliverable": 'External connection restriction rules',
            "how": 'Test: Mechanisms implementing terms and conditions on use of external systems',
            "kind": 'config',
        },
        "f": {
            "deliverable": 'External system usage restriction rules',
            "how": 'Test: Mechanisms implementing terms and conditions on use of external systems',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.21": {
        "a": {
            "deliverable": 'Portable storage device usage documentation (external systems)',
            "how": 'Examine: Access control policy; procedures addressing the use of external systems; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Portable storage device usage limit policy',
            "how": 'Examine: Access control policy; procedures addressing the use of external systems; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Portable storage device restriction configuration',
            "how": 'Test: Mechanisms implementing restrictions on use of portable storage devices',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.22": {
        "a": {
            "deliverable": 'Public system authorization list',
            "how": 'Examine: Access control policy; procedures addressing publicly accessible content; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'CUI public posting prohibition policy',
            "how": 'Examine: Access control policy; procedures addressing publicly accessible content Test: Mechanisms implementing management of publicly accessible content',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Public content pre-review policy',
            "how": 'Examine: Access control policy; procedures addressing publicly accessible content Test: Mechanisms implementing management of publicly accessible content',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Public content CUI review records',
            "how": 'Examine: Access control policy; procedures addressing publicly accessible content Test: Mechanisms implementing management of publicly accessible content',
            "kind": 'evidence',
        },
        "e": {
            "deliverable": 'CUI removal mechanism configuration',
            "how": 'Examine: Access control policy; procedures addressing publicly accessible content Test: Mechanisms implementing management of publicly accessible content',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.3": {
        "a": {
            "deliverable": 'Information flow control policy',
            "how": 'Examine: Access control policy; information flow control policies; procedures addressing information flow enforcement',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Information flow enforcement methods',
            "how": 'Examine: Access control policy; information flow control policies; procedures addressing information flow enforcement',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'CUI source/destination list',
            "how": 'Examine: Access control policy; information flow control policies; procedures addressing information flow enforcement',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'CUI flow authorization policy',
            "how": 'Examine: Access control policy; information flow control policies; procedures addressing information flow enforcement',
            "kind": 'policy',
        },
        "e": {
            "deliverable": 'CUI flow enforcement rules',
            "how": 'Test: Mechanisms implementing information flow enforcement policy',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.4": {
        "a": {
            "deliverable": 'Separation-of-duties list',
            "how": 'Examine: Access control policy; procedures addressing divisions of responsibility and separation of duties; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Separation-of-duties assignment records',
            "how": 'Examine: Access control policy; procedures addressing divisions of responsibility and separation of duties Test: Mechanisms implementing separation of duties policy',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Separation-of-duties access privilege records',
            "how": 'Examine: Access control policy; procedures addressing divisions of responsibility and separation of duties Test: Mechanisms implementing separation of duties policy',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.5": {
        "a": {
            "deliverable": 'Privileged account list',
            "how": 'Examine: Access control policy; procedures addressing account management; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Least privilege authorization policy',
            "how": 'Examine: Access control policy; procedures addressing account management Test: Organizational processes for managing system accounts; mechanisms for implementing account management',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Security function list',
            "how": 'Examine: Access control policy; procedures addressing account management; system security plan',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'Security function authorization policy',
            "how": 'Examine: Access control policy; procedures addressing account management Test: Organizational processes for managing system accounts; mechanisms for implementing account management',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.6": {
        "a": {
            "deliverable": 'Nonsecurity function list',
            "how": 'Examine: Access control policy; procedures addressing least privilege; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Non-privileged account usage enforcement records',
            "how": 'Examine: Access control policy; procedures addressing least privilege Test: Mechanisms implementing least privilege functions',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.7": {
        "a": {
            "deliverable": 'Privileged function list',
            "how": 'Examine: Access control policy; procedures addressing least privilege; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Non-privileged user list',
            "how": 'Examine: Access control policy; procedures addressing least privilege; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Privileged function restriction configuration',
            "how": 'Test: Mechanisms implementing least privilege functions for non-privileged users; mechanisms auditing the execution of privileged functions',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Privileged function execution audit log records',
            "how": 'Examine: Access control policy; procedures addressing least privilege Test: Mechanisms implementing least privilege functions for non-privileged users; mechanisms auditing the execution of privileged functions',
            "kind": 'evidence',
        },
    },
    "AC.L2-3.1.8": {
        "a": {
            "deliverable": 'Unsuccessful login attempt limit policy',
            "how": 'Examine: Access control policy; procedures addressing unsuccessful logon attempts; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Unsuccessful login attempt limit configuration',
            "how": 'Test: Mechanisms implementing access control policy for unsuccessful logon attempts',
            "kind": 'config',
        },
    },
    "AC.L2-3.1.9": {
        "a": {
            "deliverable": 'System use notification content policy',
            "how": 'Examine: Privacy and security policies, procedures addressing system use notification; documented approval of system use notification messages or banners; system audit logs and records',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'System use notification banner proof',
            "how": 'Examine: Privacy and security policies, procedures addressing system use notification; documented approval of system use notification messages or banners Test: Mechanisms implementing system use notification',
            "kind": 'evidence',
        },
    },
    "AT.L2-3.2.1": {
        "a": {
            "deliverable": 'Security risk documentation',
            "how": 'Examine: Security awareness and training policy; procedures addressing security awareness training implementation; relevant codes of federal regulations',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Applicable policy listing',
            "how": 'Examine: Security awareness and training policy; procedures addressing security awareness training implementation; relevant codes of federal regulations',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Security awareness training records',
            "how": 'Examine: Security awareness and training policy; procedures addressing security awareness training implementation Test: Mechanisms managing security awareness training; mechanisms managing role-based security training',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Policy awareness training records',
            "how": 'Examine: Security awareness and training policy; procedures addressing security awareness training implementation Test: Mechanisms managing security awareness training; mechanisms managing role-based security training',
            "kind": 'evidence',
        },
    },
    "AT.L2-3.2.2": {
        "a": {
            "deliverable": 'Information security role definitions',
            "how": 'Examine: Security awareness and training policy; procedures addressing security training implementation; codes of federal regulations',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Security role assignment records',
            "how": 'Examine: Security awareness and training policy; procedures addressing security training implementation Test: Mechanisms managing role-based security training; mechanisms managing security awareness training',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Personnel training completion records',
            "how": 'Examine: Security awareness and training policy; procedures addressing security training implementation Test: Mechanisms managing role-based security training; mechanisms managing security awareness training',
            "kind": 'evidence',
        },
    },
    "AT.L2-3.2.3": {
        "a": {
            "deliverable": 'Insider threat indicator documentation',
            "how": 'Examine: Security awareness and training policy; procedures addressing security awareness training implementation; security awareness training curriculum',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Insider threat training records',
            "how": 'Examine: Security awareness and training policy; procedures addressing security awareness training implementation Test: Mechanisms managing insider threat training',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.1": {
        "a": {
            "deliverable": 'Written audit logging policy',
            "how": 'Examine: Audit and accountability policy; procedures addressing auditable events; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Log field specification',
            "how": 'Examine: Audit and accountability policy; procedures addressing auditable events; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Audit logging configuration proof',
            "how": 'Test: Mechanisms implementing system audit logging',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Log sample with field verification',
            "how": 'Examine: Audit and accountability policy; procedures addressing auditable events Test: Mechanisms implementing system audit logging',
            "kind": 'evidence',
        },
        "e": {
            "deliverable": 'Retention policy statement',
            "how": 'Examine: Audit and accountability policy; procedures addressing auditable events; system security plan',
            "kind": 'policy',
        },
        "f": {
            "deliverable": 'Retention configuration proof',
            "how": 'Test: Mechanisms implementing system audit logging',
            "kind": 'config',
        },
    },
    "AU.L2-3.3.2": {
        "a": {
            "deliverable": 'User action traceability policy',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit records and event types; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'User action traceability configuration',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit records and event types Test: Mechanisms implementing system audit logging',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.3": {
        "a": {
            "deliverable": 'Logged event type list',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit records and event types; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Event content specification',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit records and event types Test: Mechanisms supporting review and update of logged event types',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Logged event review frequency policy',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit records and event types Test: Mechanisms supporting review and update of logged event types',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.4": {
        "a": {
            "deliverable": 'Audit failure alert personnel list',
            "how": 'Examine: Audit and accountability policy; procedures addressing response to audit logging processing failures; system design documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Audit failure types definition',
            "how": 'Examine: Audit and accountability policy; procedures addressing response to audit logging processing failures; system design documentation',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Audit failure notification records',
            "how": 'Examine: Audit and accountability policy; procedures addressing response to audit logging processing failures Test: Mechanisms implementing system response to audit logging processing failures',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.5": {
        "a": {
            "deliverable": 'Audit log reduction process policy',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit record review, analysis, and reporting; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Audit log correlation capability proof',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit record review, analysis, and reporting Test: Mechanisms supporting analysis and correlation of audit records; mechanisms integrating audit review, analysis and reporting',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.6": {
        "a": {
            "deliverable": 'Audit record review frequency policy',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit record reduction and report generation Test: Audit record reduction and report generation capability',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Audit record review, analysis, reporting records',
            "how": 'Examine: Audit and accountability policy; procedures addressing audit record reduction and report generation Test: Audit record reduction and report generation capability',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.7": {
        "a": {
            "deliverable": 'Time stamp source configuration',
            "how": 'Examine: Audit and accountability policy; procedures addressing time stamp generation Test: Mechanisms implementing time stamp generation; mechanisms implementing internal information system clock synchronization',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Authoritative time source specification',
            "how": 'Examine: Audit and accountability policy; procedures addressing time stamp generation; system design documentation',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Clock synchronization records',
            "how": 'Examine: Audit and accountability policy; procedures addressing time stamp generation Test: Mechanisms implementing time stamp generation; mechanisms implementing internal information system clock synchronization',
            "kind": 'evidence',
        },
    },
    "AU.L2-3.3.8": {
        "a": {
            "deliverable": 'Audit information access-protection configuration',
            "how": 'Test: Mechanisms implementing audit information protection',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Audit information modification-protection configuration',
            "how": 'Test: Mechanisms implementing audit information protection',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Audit information deletion-protection configuration',
            "how": 'Test: Mechanisms implementing audit information protection',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Audit logging tool access-protection configuration',
            "how": 'Test: Mechanisms implementing audit information protection',
            "kind": 'config',
        },
        "e": {
            "deliverable": 'Audit logging tool modification-protection configuration',
            "how": 'Test: Mechanisms implementing audit information protection',
            "kind": 'config',
        },
        "f": {
            "deliverable": 'Audit logging tool deletion-protection configuration',
            "how": 'Test: Mechanisms implementing audit information protection',
            "kind": 'config',
        },
    },
    "AU.L2-3.3.9": {
        "a": {
            "deliverable": 'Privileged audit-management user list',
            "how": 'Examine: Audit and accountability policy; access control policy and procedures; procedures addressing protection of audit information',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Audit-management access restriction configuration',
            "how": 'Test: Mechanisms managing access to audit logging functionality',
            "kind": 'config',
        },
    },
    "CA.L2-3.12.1": {
        "a": {
            "deliverable": 'Security control assessment schedule',
            "how": 'Examine: Security assessment and authorization policy; procedures addressing security assessment planning; procedures addressing security assessments',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Security control assessment results',
            "how": 'Examine: Security assessment and authorization policy; procedures addressing security assessment planning Test: Mechanisms supporting security assessment, security assessment plan development, and security assessment reporting',
            "kind": 'evidence',
        },
    },
    "CA.L2-3.12.2": {
        "a": {
            "deliverable": 'Deficiency and vulnerability list',
            "how": 'Examine: Security assessment and authorization policy; procedures addressing plan of action; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Plan of action and milestones (POA&M)',
            "how": 'Examine: Security assessment and authorization policy; procedures addressing plan of action; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'POA&M implementation records',
            "how": 'Test: Mechanisms for developing, implementing, and maintaining plan of action',
            "kind": 'config',
        },
    },
    "CA.L2-3.12.3": {
        "a": {
            "deliverable": 'Security control monitoring records',
            "how": 'Examine: Security planning policy; organizational procedures addressing system security plan development and implementation Test: Organizational processes for system security plan development, review, update, and approval; mechanisms supporting the system security plan',
            "kind": 'evidence',
        },
    },
    "CA.L2-3.12.4": {
        "a": {
            "deliverable": 'System security plan',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'System boundary documentation',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'System environment description',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'Excluded requirement documentation',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "e": {
            "deliverable": 'Security implementation description',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "f": {
            "deliverable": 'System interconnection documentation',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "g": {
            "deliverable": 'SSP update schedule',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "h": {
            "deliverable": 'SSP update records',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation Test: Organizational processes for system security plan development, review, update, and approval; mechanisms supporting the system security plan',
            "kind": 'evidence',
        },
    },
    "CM.L2-3.4.1": {
        "a": {
            "deliverable": 'Baseline configuration policy',
            "how": 'Examine: Configuration management policy; procedures addressing the baseline configuration of the system; procedures addressing system inventory',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Baseline configuration inclusion list',
            "how": 'Examine: Configuration management policy; procedures addressing the baseline configuration of the system Test: Organizational processes for managing baseline configurations; mechanisms supporting configuration control of the baseline configuration',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Baseline configuration records',
            "how": 'Examine: Configuration management policy; procedures addressing the baseline configuration of the system Test: Organizational processes for managing baseline configurations; mechanisms supporting configuration control of the baseline configuration',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'System inventory policy',
            "how": 'Examine: Configuration management policy; procedures addressing the baseline configuration of the system; procedures addressing system inventory',
            "kind": 'policy',
        },
        "e": {
            "deliverable": 'System inventory requirements',
            "how": 'Examine: Configuration management policy; procedures addressing the baseline configuration of the system Test: Organizational processes for managing baseline configurations; mechanisms supporting configuration control of the baseline configuration',
            "kind": 'evidence',
        },
        "f": {
            "deliverable": 'Inventory records',
            "how": 'Examine: Configuration management policy; procedures addressing the baseline configuration of the system Test: Organizational processes for managing baseline configurations; mechanisms supporting configuration control of the baseline configuration',
            "kind": 'evidence',
        },
    },
    "CM.L2-3.4.2": {
        "a": {
            "deliverable": 'Baseline configuration management policy',
            "how": 'Examine: Configuration management policy; baseline configuration; procedures addressing configuration settings for the system',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Baseline configuration update records',
            "how": 'Test: Organizational processes for managing configuration settings; mechanisms that implement, monitor, and/or control system configuration settings',
            "kind": 'config',
        },
    },
    "CM.L2-3.4.3": {
        "a": {
            "deliverable": 'Change tracking policy',
            "how": 'Examine: Configuration management policy; procedures addressing system configuration change control Test: Organizational processes for configuration change control; mechanisms that implement configuration change control',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Change review records',
            "how": 'Examine: Configuration management policy; procedures addressing system configuration change control Test: Organizational processes for configuration change control; mechanisms that implement configuration change control',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Change approval/denial records',
            "how": 'Examine: Configuration management policy; procedures addressing system configuration change control Test: Organizational processes for configuration change control; mechanisms that implement configuration change control',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Change logging records',
            "how": 'Examine: Configuration management policy; procedures addressing system configuration change control Test: Organizational processes for configuration change control; mechanisms that implement configuration change control',
            "kind": 'evidence',
        },
    },
    "CM.L2-3.4.4": {
        "a": {
            "deliverable": 'Security impact analysis policy',
            "how": 'Examine: Configuration management policy; procedures addressing security impact analysis for system changes Test: Organizational processes for security impact analysis',
            "kind": 'evidence',
        },
    },
    "CM.L2-3.4.5": {
        "a": {
            "deliverable": 'Physical change restriction definition',
            "how": 'Examine: Configuration management policy; procedures addressing access restrictions for changes to the system; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Physical change restriction documentation',
            "how": 'Examine: Configuration management policy; procedures addressing access restrictions for changes to the system; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Physical change restriction approval records',
            "how": 'Examine: Configuration management policy; procedures addressing access restrictions for changes to the system Test: Organizational processes for managing access restrictions associated with changes to the system; mechanisms supporting, implementing, and enforcing access restrictions associated with changes to the system',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Physical change restriction enforcement config',
            "how": 'Test: Organizational processes for managing access restrictions associated with changes to the system; mechanisms supporting, implementing, and enforcing access restrictions associated with changes to the system',
            "kind": 'config',
        },
        "e": {
            "deliverable": 'Logical change restriction definition',
            "how": 'Examine: Configuration management policy; procedures addressing access restrictions for changes to the system; system security plan',
            "kind": 'policy',
        },
        "f": {
            "deliverable": 'Logical change restriction documentation',
            "how": 'Examine: Configuration management policy; procedures addressing access restrictions for changes to the system; system security plan',
            "kind": 'policy',
        },
        "g": {
            "deliverable": 'Logical change restriction approval records',
            "how": 'Examine: Configuration management policy; procedures addressing access restrictions for changes to the system Test: Organizational processes for managing access restrictions associated with changes to the system; mechanisms supporting, implementing, and enforcing access restrictions associated with changes to the system',
            "kind": 'evidence',
        },
        "h": {
            "deliverable": 'Logical change restriction enforcement config',
            "how": 'Test: Organizational processes for managing access restrictions associated with changes to the system; mechanisms supporting, implementing, and enforcing access restrictions associated with changes to the system',
            "kind": 'config',
        },
    },
    "CM.L2-3.4.6": {
        "a": {
            "deliverable": 'Least functionality policy',
            "how": 'Examine: Configuration management policy; configuration management plan; procedures addressing least functionality in the system',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Unnecessary function/program/port list',
            "how": 'Examine: Configuration management policy; configuration management plan Test: Organizational processes prohibiting or restricting functions, ports, protocols, or services; mechanisms implementing restrictions or prohibition of functions, ports, protocols, or services',
            "kind": 'evidence',
        },
    },
    "CM.L2-3.4.7": {
        "a": {
            "deliverable": 'Essential program list',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Nonessential program usage policy',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Program restriction rules',
            "how": 'Test: Organizational processes for reviewing and disabling nonessential programs, functions, ports, protocols, or services; mechanisms implementing review and handling of nonessential programs, functions, ports, protocols, or services',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Essential function list',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "e": {
            "deliverable": 'Nonessential function usage policy',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "f": {
            "deliverable": 'Function restriction rules',
            "how": 'Test: Organizational processes for reviewing and disabling nonessential programs, functions, ports, protocols, or services; mechanisms implementing review and handling of nonessential programs, functions, ports, protocols, or services',
            "kind": 'config',
        },
        "g": {
            "deliverable": 'Essential port list',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "h": {
            "deliverable": 'Nonessential port usage policy',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "i": {
            "deliverable": 'Port restriction rules',
            "how": 'Test: Organizational processes for reviewing and disabling nonessential programs, functions, ports, protocols, or services; mechanisms implementing review and handling of nonessential programs, functions, ports, protocols, or services',
            "kind": 'config',
        },
        "j": {
            "deliverable": 'Essential protocol list',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "k": {
            "deliverable": 'Nonessential protocol usage policy',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "l": {
            "deliverable": 'Protocol restriction rules',
            "how": 'Test: Organizational processes for reviewing and disabling nonessential programs, functions, ports, protocols, or services; mechanisms implementing review and handling of nonessential programs, functions, ports, protocols, or services',
            "kind": 'config',
        },
        "m": {
            "deliverable": 'Essential service list',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "n": {
            "deliverable": 'Nonessential service usage policy',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; configuration management plan',
            "kind": 'policy',
        },
        "o": {
            "deliverable": 'Service restriction rules',
            "how": 'Test: Organizational processes for reviewing and disabling nonessential programs, functions, ports, protocols, or services; mechanisms implementing review and handling of nonessential programs, functions, ports, protocols, or services',
            "kind": 'config',
        },
    },
    "CM.L2-3.4.8": {
        "a": {
            "deliverable": 'Whitelist/blacklist approach policy',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system Test: Organizational process for identifying, reviewing, and updating programs authorized or not authorized to execute on the system; process for implementing blacklisting or whitelisting',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Whitelisted/blacklisted software list',
            "how": 'Examine: Configuration management policy; procedures addressing least functionality in the system; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Whitelist/blacklist enforcement configuration',
            "how": 'Test: Organizational process for identifying, reviewing, and updating programs authorized or not authorized to execute on the system; process for implementing blacklisting or whitelisting',
            "kind": 'config',
        },
    },
    "CM.L2-3.4.9": {
        "a": {
            "deliverable": 'User-installed software policy',
            "how": 'Examine: Configuration management policy; procedures addressing user installed software; configuration management plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'User-installed software enforcement configuration',
            "how": 'Test: Organizational processes governing user-installed software on the system; mechanisms enforcing rules or methods for governing the installation of software by users',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'User-installed software monitoring records',
            "how": 'Examine: Configuration management policy; procedures addressing user installed software Test: Organizational processes governing user-installed software on the system; mechanisms enforcing rules or methods for governing the installation of software by users',
            "kind": 'evidence',
        },
    },
    "IA.L2-3.5.1": {
        "a": {
            "deliverable": 'User identification policy',
            "how": 'Examine: Identification and authentication policy; procedures addressing user identification and authentication; system security plan, system design documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Process identification policy',
            "how": 'Examine: Identification and authentication policy; procedures addressing user identification and authentication; system security plan, system design documentation',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Device identification policy',
            "how": 'Examine: Identification and authentication policy; procedures addressing user identification and authentication; system security plan, system design documentation',
            "kind": 'policy',
        },
    },
    "IA.L2-3.5.10": {
        "a": {
            "deliverable": 'Password storage encryption configuration',
            "how": 'Examine: Identification and authentication policy; password policy Test: Mechanisms supporting or implementing password-based authenticator management capability',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Password transmission encryption configuration',
            "how": 'Examine: Identification and authentication policy; password policy Test: Mechanisms supporting or implementing password-based authenticator management capability',
            "kind": 'config',
        },
    },
    "IA.L2-3.5.11": {
        "a": {
            "deliverable": 'Authentication feedback obscurity configuration',
            "how": 'Examine: Identification and authentication policy; procedures addressing authenticator feedback Test: Mechanisms supporting or implementing the obscuring of feedback of authentication information during authentication',
            "kind": 'evidence',
        },
    },
    "IA.L2-3.5.2": {
        "a": {
            "deliverable": 'User authentication configuration',
            "how": 'Examine: Identification and authentication policy; system security plan Test: Mechanisms supporting or implementing authenticator management capability',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Process authentication configuration',
            "how": 'Examine: Identification and authentication policy; system security plan Test: Mechanisms supporting or implementing authenticator management capability',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Device authentication configuration',
            "how": 'Examine: Identification and authentication policy; system security plan Test: Mechanisms supporting or implementing authenticator management capability',
            "kind": 'evidence',
        },
    },
    "IA.L2-3.5.3": {
        "a": {
            "deliverable": 'Privileged account identification policy',
            "how": 'Examine: Identification and authentication policy; procedures addressing user identification and authentication; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'MFA local access configuration',
            "how": 'Test: Mechanisms supporting or implementing multifactor authentication capability',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'MFA network privileged access configuration',
            "how": 'Test: Mechanisms supporting or implementing multifactor authentication capability',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'MFA network non-privileged access configuration',
            "how": 'Test: Mechanisms supporting or implementing multifactor authentication capability',
            "kind": 'config',
        },
    },
    "IA.L2-3.5.4": {
        "a": {
            "deliverable": 'Replay-resistant authentication implementation proof',
            "how": 'Test: Mechanisms supporting or implementing identification and authentication capability or replay resistant authentication mechanisms',
            "kind": 'config',
        },
    },
    "IA.L2-3.5.5": {
        "a": {
            "deliverable": 'Identifier reuse period policy',
            "how": 'Examine: Identification and authentication policy; procedures addressing identifier management; procedures addressing account management',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Identifier reuse prevention configuration',
            "how": 'Test: Mechanisms supporting or implementing identifier management',
            "kind": 'config',
        },
    },
    "IA.L2-3.5.6": {
        "a": {
            "deliverable": 'Identifier inactivity disable period policy',
            "how": 'Test: Mechanisms supporting or implementing identifier management',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Identifier inactivity disable configuration',
            "how": 'Test: Mechanisms supporting or implementing identifier management',
            "kind": 'config',
        },
    },
    "IA.L2-3.5.7": {
        "a": {
            "deliverable": 'Password complexity policy',
            "how": 'Examine: Identification and authentication policy; password policy; procedures addressing authenticator management',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Password change character policy',
            "how": 'Examine: Identification and authentication policy; password policy; procedures addressing authenticator management',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Password complexity enforcement configuration',
            "how": 'Test: Mechanisms supporting or implementing password-based authenticator management capability',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Password change character enforcement configuration',
            "how": 'Test: Mechanisms supporting or implementing password-based authenticator management capability',
            "kind": 'config',
        },
    },
    "IA.L2-3.5.8": {
        "a": {
            "deliverable": 'Single-use authentication mechanism policy',
            "how": 'Examine: Identification and authentication policy; password policy; procedures addressing authenticator management',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Single-use authentication block configuration',
            "how": 'Examine: Identification and authentication policy; password policy Test: Mechanisms supporting or implementing password-based authenticator management capability',
            "kind": 'evidence',
        },
    },
    "IA.L2-3.5.9": {
        "a": {
            "deliverable": 'Temporary password change policy',
            "how": 'Examine: Identification and authentication policy; password policy Test: Mechanisms supporting or implementing password-based authenticator management capability',
            "kind": 'evidence',
        },
    },
    "IR.L2-3.6.1": {
        "a": {
            "deliverable": 'Incident response plan and procedures',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'IR capability — preparation phase',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'IR capability — detection phase',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'IR capability — analysis phase',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
        "e": {
            "deliverable": 'IR capability — containment phase',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
        "f": {
            "deliverable": 'IR capability — recovery phase',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
        "g": {
            "deliverable": 'IR capability — user response phase',
            "how": 'Examine: Incident response policy; contingency planning policy; procedures addressing incident handling',
            "kind": 'policy',
        },
    },
    "IR.L2-3.6.2": {
        "a": {
            "deliverable": 'Incident tracking records',
            "how": 'Examine: Incident response policy; procedures addressing incident monitoring Test: Incident monitoring capability for the organization; mechanisms supporting or implementing tracking and documenting of system security incidents',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Incident documentation records',
            "how": 'Examine: Incident response policy; procedures addressing incident monitoring Test: Incident monitoring capability for the organization; mechanisms supporting or implementing tracking and documenting of system security incidents',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'External notification authority listing',
            "how": 'Examine: Incident response policy; procedures addressing incident monitoring; incident response records and documentation',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'Internal official notification listing',
            "how": 'Examine: Incident response policy; procedures addressing incident monitoring; incident response records and documentation',
            "kind": 'policy',
        },
        "e": {
            "deliverable": 'External authority notification records',
            "how": 'Examine: Incident response policy; procedures addressing incident monitoring Test: Incident monitoring capability for the organization; mechanisms supporting or implementing tracking and documenting of system security incidents',
            "kind": 'evidence',
        },
        "f": {
            "deliverable": 'Internal official notification records',
            "how": 'Examine: Incident response policy; procedures addressing incident monitoring Test: Incident monitoring capability for the organization; mechanisms supporting or implementing tracking and documenting of system security incidents',
            "kind": 'evidence',
        },
    },
    "IR.L2-3.6.3": {
        "a": {
            "deliverable": 'Incident response test results',
            "how": 'Examine: Incident response policy; contingency planning policy Test: Mechanisms and processes for incident response',
            "kind": 'evidence',
        },
    },
    "MA.L2-3.7.1": {
        "a": {
            "deliverable": 'System maintenance schedule and records',
            "how": 'Examine: System maintenance policy; procedures addressing controlled system maintenance Test: Organizational processes for scheduling, performing, documenting, reviewing, approving, and monitoring maintenance and repairs for systems; organizational processes for sanitizing system components',
            "kind": 'evidence',
        },
    },
    "MA.L2-3.7.2": {
        "a": {
            "deliverable": 'Maintenance tool control policy',
            "how": 'Test: Organizational processes for approving, controlling, and monitoring maintenance tools; mechanisms supporting or implementing approval, control, and monitoring of maintenance tools',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Maintenance technique control policy',
            "how": 'Test: Organizational processes for approving, controlling, and monitoring maintenance tools; mechanisms supporting or implementing approval, control, and monitoring of maintenance tools',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Maintenance mechanism control policy',
            "how": 'Test: Organizational processes for approving, controlling, and monitoring maintenance tools; mechanisms supporting or implementing approval, control, and monitoring of maintenance tools',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Maintenance personnel control policy',
            "how": 'Test: Organizational processes for approving, controlling, and monitoring maintenance tools; mechanisms supporting or implementing approval, control, and monitoring of maintenance tools',
            "kind": 'config',
        },
    },
    "MA.L2-3.7.3": {
        "a": {
            "deliverable": 'Off-site maintenance removal policy',
            "how": 'Examine: System maintenance policy; procedures addressing controlled system maintenance Test: Organizational processes for scheduling, performing, documenting, reviewing, approving, and monitoring maintenance and repairs for systems; organizational processes for sanitizing system components',
            "kind": 'evidence',
        },
    },
    "MA.L2-3.7.4": {
        "a": {
            "deliverable": 'Diagnostic media malware check policy',
            "how": 'Examine: System maintenance policy; procedures addressing system maintenance tools Test: Organizational process for inspecting media for malicious code; mechanisms supporting or implementing inspection of media used for maintenance',
            "kind": 'evidence',
        },
    },
    "MA.L2-3.7.5": {
        "a": {
            "deliverable": 'Nonlocal maintenance MFA configuration',
            "how": 'Examine: System maintenance policy; procedures addressing nonlocal system maintenance Test: Organizational processes for managing nonlocal maintenance; mechanisms implementing, supporting, and managing nonlocal maintenance',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Remote maintenance session termination records',
            "how": 'Examine: System maintenance policy; procedures addressing nonlocal system maintenance Test: Organizational processes for managing nonlocal maintenance; mechanisms implementing, supporting, and managing nonlocal maintenance',
            "kind": 'evidence',
        },
    },
    "MA.L2-3.7.6": {
        "a": {
            "deliverable": 'Maintenance personnel supervision policy',
            "how": 'Examine: System maintenance policy; procedures addressing maintenance personnel Test: Organizational processes for authorizing and managing maintenance personnel; mechanisms supporting or implementing authorization of maintenance personnel',
            "kind": 'evidence',
        },
    },
    "MP.L2-3.8.1": {
        "a": {
            "deliverable": 'Paper media storage records (CUI)',
            "how": 'Examine: System media protection policy; procedures addressing media storage Test: Organizational processes for restricting information media; mechanisms supporting or implementing media access restrictions',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Digital media storage records (CUI)',
            "how": 'Examine: System media protection policy; procedures addressing media storage Test: Organizational processes for restricting information media; mechanisms supporting or implementing media access restrictions',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Paper media secure storage configuration',
            "how": 'Test: Organizational processes for restricting information media; mechanisms supporting or implementing media access restrictions',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Digital media secure storage configuration',
            "how": 'Test: Organizational processes for restricting information media; mechanisms supporting or implementing media access restrictions',
            "kind": 'config',
        },
    },
    "MP.L2-3.8.2": {
        "a": {
            "deliverable": 'CUI media access restriction configuration',
            "how": 'Test: Organizational processes for storing media; mechanisms supporting or implementing secure media storage and media protection',
            "kind": 'config',
        },
    },
    "MP.L2-3.8.3": {
        "a": {
            "deliverable": 'Media sanitization policy',
            "how": 'Examine: System media protection policy; procedures addressing media sanitization and disposal Test: Organizational processes for media sanitization; mechanisms supporting or implementing media sanitization',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Media sanitization records',
            "how": 'Examine: System media protection policy; procedures addressing media sanitization and disposal Test: Organizational processes for media sanitization; mechanisms supporting or implementing media sanitization',
            "kind": 'evidence',
        },
    },
    "MP.L2-3.8.4": {
        "a": {
            "deliverable": 'CUI media classification marking records',
            "how": 'Examine: System media protection policy; procedures addressing media marking Test: Organizational processes for marking information media; mechanisms supporting or implementing media marking',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Media distribution limitation marking records',
            "how": 'Examine: System media protection policy; procedures addressing media marking Test: Organizational processes for marking information media; mechanisms supporting or implementing media marking',
            "kind": 'evidence',
        },
    },
    "MP.L2-3.8.5": {
        "a": {
            "deliverable": 'Media transport protection policy',
            "how": 'Test: Organizational processes for storing media; mechanisms supporting or implementing media storage and media protection',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Media transport protection records',
            "how": 'Examine: System media protection policy; procedures addressing media storage Test: Organizational processes for storing media; mechanisms supporting or implementing media storage and media protection',
            "kind": 'evidence',
        },
    },
    "MP.L2-3.8.6": {
        "a": {
            "deliverable": 'Digital media confidentiality protection policy',
            "how": 'Test: Cryptographic mechanisms protecting information on digital media during transportation outside controlled areas',
            "kind": 'config',
        },
    },
    "MP.L2-3.8.7": {
        "a": {
            "deliverable": 'Removable media use policy',
            "how": 'Test: Organizational processes for media use; mechanisms restricting or prohibiting use of system media on systems or system components',
            "kind": 'config',
        },
    },
    "MP.L2-3.8.8": {
        "a": {
            "deliverable": 'Portable storage device ownership policy',
            "how": 'Examine: System media protection policy; system use policy Test: Organizational processes for media use; mechanisms prohibiting use of media on systems or system components',
            "kind": 'evidence',
        },
    },
    "MP.L2-3.8.9": {
        "a": {
            "deliverable": 'Backup CUI confidentiality protection policy',
            "how": 'Test: Organizational processes for conducting system backups; mechanisms supporting or implementing system backups',
            "kind": 'config',
        },
    },
    "PE.L2-3.10.1": {
        "a": {
            "deliverable": 'Physical access authorization list',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access authorizations; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Physical access enforcement configuration',
            "how": 'Test: Organizational processes for physical access authorizations; mechanisms supporting or implementing physical access authorizations',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Equipment physical access restriction configuration',
            "how": 'Test: Organizational processes for physical access authorizations; mechanisms supporting or implementing physical access authorizations',
            "kind": 'config',
        },
        "d": {
            "deliverable": 'Operating environment physical access restriction configuration',
            "how": 'Test: Organizational processes for physical access authorizations; mechanisms supporting or implementing physical access authorizations',
            "kind": 'config',
        },
    },
    "PE.L2-3.10.2": {
        "a": {
            "deliverable": 'Facility protection policy',
            "how": 'Test: Organizational processes for monitoring physical access; mechanisms supporting or implementing physical access monitoring',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Infrastructure protection policy',
            "how": 'Test: Organizational processes for monitoring physical access; mechanisms supporting or implementing physical access monitoring',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Facility monitoring records',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access monitoring Test: Organizational processes for monitoring physical access; mechanisms supporting or implementing physical access monitoring',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Infrastructure monitoring records',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access monitoring Test: Organizational processes for monitoring physical access; mechanisms supporting or implementing physical access monitoring',
            "kind": 'evidence',
        },
    },
    "PE.L2-3.10.3": {
        "a": {
            "deliverable": 'Visitor escort policy',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access control Test: Organizational processes for physical access control; mechanisms supporting or implementing physical access control',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Visitor activity monitoring records',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access control Test: Organizational processes for physical access control; mechanisms supporting or implementing physical access control',
            "kind": 'evidence',
        },
    },
    "PE.L2-3.10.4": {
        "a": {
            "deliverable": 'Physical access audit log configuration',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access control Test: Organizational processes for physical access control; mechanisms supporting or implementing physical access control',
            "kind": 'evidence',
        },
    },
    "PE.L2-3.10.5": {
        "a": {
            "deliverable": 'Physical access device list',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access control; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Physical access device control records',
            "how": 'Test: Organizational processes for physical access control; mechanisms supporting or implementing physical access control',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Physical access device management records',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing physical access control Test: Organizational processes for physical access control; mechanisms supporting or implementing physical access control',
            "kind": 'evidence',
        },
    },
    "PE.L2-3.10.6": {
        "a": {
            "deliverable": 'Physical facility protection policy',
            "how": 'Examine: Physical and environmental protection policy; procedures addressing alternate work sites for personnel; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Physical facility monitoring policy',
            "how": 'Test: Organizational processes for security at alternate work sites; mechanisms supporting alternate work sites',
            "kind": 'config',
        },
    },
    "PS.L2-3.9.1": {
        "a": {
            "deliverable": 'Personnel screening records',
            "how": 'Examine: Personnel security policy; procedures addressing personnel screening Test: Organizational processes for personnel screening',
            "kind": 'evidence',
        },
    },
    "PS.L2-3.9.2": {
        "a": {
            "deliverable": 'Personnel termination/transfer policy',
            "how": 'Examine: Personnel security policy; procedures addressing personnel transfer and termination; records of personnel transfer and termination actions',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Account termination records',
            "how": 'Examine: Personnel security policy; procedures addressing personnel transfer and termination Test: Organizational processes for personnel transfer and termination; mechanisms supporting or implementing personnel transfer and termination notifications',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Transfer access protection proof',
            "how": 'Test: Organizational processes for personnel transfer and termination; mechanisms supporting or implementing personnel transfer and termination notifications',
            "kind": 'config',
        },
    },
    "RA.L2-3.11.1": {
        "a": {
            "deliverable": 'Risk assessment schedule and policy',
            "how": 'Examine: Risk assessment policy; security planning policy and procedures; procedures addressing organizational risk assessments',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Risk assessment records',
            "how": 'Examine: Risk assessment policy; security planning policy and procedures Test: Organizational processes for risk assessment; mechanisms supporting or for conducting, documenting, reviewing, disseminating, and updating the risk assessment',
            "kind": 'evidence',
        },
    },
    "RA.L2-3.11.2": {
        "a": {
            "deliverable": 'Vulnerability scanning schedule and policy',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning; risk assessment',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'System vulnerability scan results (scheduled)',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning Test: Organizational processes for vulnerability scanning, analysis, remediation, and information sharing; mechanisms supporting or implementing vulnerability scanning, analysis, remediation, and information sharing',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Application vulnerability scan results (scheduled)',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning Test: Organizational processes for vulnerability scanning, analysis, remediation, and information sharing; mechanisms supporting or implementing vulnerability scanning, analysis, remediation, and information sharing',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'System vulnerability scan results (event-driven)',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning Test: Organizational processes for vulnerability scanning, analysis, remediation, and information sharing; mechanisms supporting or implementing vulnerability scanning, analysis, remediation, and information sharing',
            "kind": 'evidence',
        },
        "e": {
            "deliverable": 'Application vulnerability scan results (event-driven)',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning Test: Organizational processes for vulnerability scanning, analysis, remediation, and information sharing; mechanisms supporting or implementing vulnerability scanning, analysis, remediation, and information sharing',
            "kind": 'evidence',
        },
    },
    "RA.L2-3.11.3": {
        "a": {
            "deliverable": 'Vulnerability identification records',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning Test: Organizational processes for vulnerability scanning, analysis, remediation, and information sharing; mechanisms supporting or implementing vulnerability scanning, analysis, remediation, and information sharing',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Vulnerability remediation records',
            "how": 'Examine: Risk assessment policy; procedures addressing vulnerability scanning Test: Organizational processes for vulnerability scanning, analysis, remediation, and information sharing; mechanisms supporting or implementing vulnerability scanning, analysis, remediation, and information sharing',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.1": {
        "a": {
            "deliverable": 'External boundary policy',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Internal boundary policy',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'External boundary monitoring configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection Test: Mechanisms implementing boundary protection capability',
            "kind": 'evidence',
        },
        "d": {
            "deliverable": 'Internal boundary monitoring configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection Test: Mechanisms implementing boundary protection capability',
            "kind": 'evidence',
        },
        "e": {
            "deliverable": 'External boundary control configuration',
            "how": 'Test: Mechanisms implementing boundary protection capability',
            "kind": 'config',
        },
        "f": {
            "deliverable": 'Internal boundary control configuration',
            "how": 'Test: Mechanisms implementing boundary protection capability',
            "kind": 'config',
        },
        "g": {
            "deliverable": 'External boundary protection configuration',
            "how": 'Test: Mechanisms implementing boundary protection capability',
            "kind": 'config',
        },
        "h": {
            "deliverable": 'Internal boundary protection configuration',
            "how": 'Test: Mechanisms implementing boundary protection capability',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.10": {
        "a": {
            "deliverable": 'Cryptographic key generation/management policy',
            "how": 'Examine: System and communications protection policy; procedures addressing cryptographic key establishment and management; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Cryptographic key management configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing cryptographic key establishment and management Test: Mechanisms supporting or implementing cryptographic key establishment and management',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.11": {
        "a": {
            "deliverable": 'FIPS-validated cryptography implementation proof',
            "how": 'Test: Mechanisms supporting or implementing cryptographic protection',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.12": {
        "a": {
            "deliverable": 'Collaborative computing device identification policy',
            "how": 'Examine: System and communications protection policy; procedures addressing collaborative computing; access control policy and procedures',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Collaborative computing device indication policy',
            "how": 'Examine: System and communications protection policy; procedures addressing collaborative computing Test: Mechanisms supporting or implementing management of remote activation of collaborative computing devices; mechanisms providing an indication of use of collaborative computing devices',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Collaborative device disabling configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing collaborative computing Test: Mechanisms supporting or implementing management of remote activation of collaborative computing devices; mechanisms providing an indication of use of collaborative computing devices',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.13": {
        "a": {
            "deliverable": 'Mobile code usage policy',
            "how": 'Test: Organizational process for controlling, authorizing, monitoring, and restricting mobile code; mechanisms supporting or implementing the management of mobile code',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'Mobile code enforcement configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing mobile code Test: Organizational process for controlling, authorizing, monitoring, and restricting mobile code; mechanisms supporting or implementing the management of mobile code',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.14": {
        "a": {
            "deliverable": 'Voice-over-IP policy',
            "how": 'Test: Organizational process for authorizing, monitoring, and controlling VoIP; mechanisms supporting or implementing authorizing, monitoring, and controlling VoIP',
            "kind": 'config',
        },
        "b": {
            "deliverable": 'VoIP usage restriction configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing VoIP Test: Organizational process for authorizing, monitoring, and controlling VoIP; mechanisms supporting or implementing authorizing, monitoring, and controlling VoIP',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.15": {
        "a": {
            "deliverable": 'Communication session authenticity protection proof',
            "how": 'Test: Mechanisms supporting or implementing session authenticity',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.16": {
        "a": {
            "deliverable": 'CUI at-rest confidentiality protection proof',
            "how": 'Test: Mechanisms supporting or implementing confidentiality protections for information at rest',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.2": {
        "a": {
            "deliverable": 'Architecture description',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Software development technique list',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Systems engineering principle list',
            "how": 'Examine: Security planning policy; procedures addressing system security plan development and implementation; procedures addressing system security plan reviews and updates',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'Architectural design implementation configuration',
            "how": 'Test: Organizational processes for system security plan development, review, update, and approval; mechanisms supporting the system security plan',
            "kind": 'config',
        },
        "e": {
            "deliverable": 'Software development technique implementation configuration',
            "how": 'Test: Organizational processes for system security plan development, review, update, and approval; mechanisms supporting the system security plan',
            "kind": 'config',
        },
        "f": {
            "deliverable": 'Systems engineering principle implementation configuration',
            "how": 'Test: Organizational processes for system security plan development, review, update, and approval; mechanisms supporting the system security plan',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.3": {
        "a": {
            "deliverable": 'User functionality inventory',
            "how": 'Examine: System and communications protection policy; procedures addressing application partitioning; system design documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'System management functionality inventory',
            "how": 'Examine: System and communications protection policy; procedures addressing application partitioning; system design documentation',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Application partitioning configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing application partitioning Test: Separation of user functionality from system management functionality',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.4": {
        "a": {
            "deliverable": 'Shared-resource information leakage prevention configuration',
            "how": 'Test: Mechanisms preventing unauthorized or unintended information transfer via shared system resources',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.5": {
        "a": {
            "deliverable": 'Publicly accessible system component inventory',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Public subnetwork separation configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection Test: Mechanisms implementing boundary protection capability',
            "kind": 'evidence',
        },
    },
    "SC.L2-3.13.6": {
        "a": {
            "deliverable": 'Default-deny network traffic policy',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection Test: Mechanisms implementing traffic management at managed interfaces',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Default-deny traffic exception configuration',
            "how": 'Examine: System and communications protection policy; procedures addressing boundary protection Test: Mechanisms implementing traffic management at managed interfaces',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.7": {
        "a": {
            "deliverable": 'Remote device simultaneous connection policy',
            "how": 'Test: Mechanisms implementing boundary protection capability; mechanisms supporting or restricting non-remote connections',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.8": {
        "a": {
            "deliverable": 'Transmission cryptographic mechanism policy',
            "how": 'Examine: System and communications protection policy; procedures addressing transmission confidentiality and integrity; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Alternative physical safeguard policy',
            "how": 'Examine: System and communications protection policy; procedures addressing transmission confidentiality and integrity; system security plan',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Transmission confidentiality protection configuration',
            "how": 'Test: Cryptographic mechanisms or mechanisms supporting or implementing transmission confidentiality; organizational processes for defining and implementing alternative physical safeguards',
            "kind": 'config',
        },
    },
    "SC.L2-3.13.9": {
        "a": {
            "deliverable": 'Network connection inactivity timeout policy',
            "how": 'Examine: System and communications protection policy; procedures addressing network disconnect; system design documentation',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Network connection termination-at-end-of-session records',
            "how": 'Examine: System and communications protection policy; procedures addressing network disconnect Test: Mechanisms supporting or implementing network disconnect capability',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Network connection inactivity-termination records',
            "how": 'Examine: System and communications protection policy; procedures addressing network disconnect Test: Mechanisms supporting or implementing network disconnect capability',
            "kind": 'evidence',
        },
    },
    "SI.L2-3.14.1": {
        "a": {
            "deliverable": 'Flaw identification timeframe policy',
            "how": 'Examine: System and information integrity policy; procedures addressing flaw remediation; procedures addressing configuration management',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Flaw identification records',
            "how": 'Examine: System and information integrity policy; procedures addressing flaw remediation; procedures addressing configuration management',
            "kind": 'policy',
        },
        "c": {
            "deliverable": 'Flaw reporting timeframe policy',
            "how": 'Examine: System and information integrity policy; procedures addressing flaw remediation; procedures addressing configuration management',
            "kind": 'policy',
        },
        "d": {
            "deliverable": 'Flaw reporting records',
            "how": 'Examine: System and information integrity policy; procedures addressing flaw remediation Test: Organizational processes for identifying, reporting, and correcting system flaws; organizational process for installing software and firmware updates',
            "kind": 'evidence',
        },
        "e": {
            "deliverable": 'Flaw correction timeframe policy',
            "how": 'Examine: System and information integrity policy; procedures addressing flaw remediation; procedures addressing configuration management',
            "kind": 'policy',
        },
        "f": {
            "deliverable": 'Flaw correction records',
            "how": 'Examine: System and information integrity policy; procedures addressing flaw remediation Test: Organizational processes for identifying, reporting, and correcting system flaws; organizational process for installing software and firmware updates',
            "kind": 'evidence',
        },
    },
    "SI.L2-3.14.2": {
        "a": {
            "deliverable": 'Malicious code protection location list',
            "how": 'Examine: System and information integrity policy; configuration management policy and procedures; procedures addressing malicious code protection',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Malicious code protection configuration',
            "how": 'Examine: System and information integrity policy; configuration management policy and procedures Test: Organizational processes for employing, updating, and configuring malicious code protection mechanisms; organizational process for addressing false positives and resulting potential impact',
            "kind": 'config',
        },
    },
    "SI.L2-3.14.3": {
        "a": {
            "deliverable": 'Security alert response action policy',
            "how": 'Examine: System and information integrity policy; procedures addressing security alerts, advisories, and directives; system security plan',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Security alert monitoring configuration',
            "how": 'Examine: System and information integrity policy; procedures addressing security alerts, advisories, and directives Test: Organizational processes for defining, receiving, generating, disseminating, and complying with security alerts, advisories, and directives; mechanisms supporting or implementing definition, receipt, generation, and dissemination of security alerts, advisories, and directives',
            "kind": 'config',
        },
        "c": {
            "deliverable": 'Security alert response action records',
            "how": 'Examine: System and information integrity policy; procedures addressing security alerts, advisories, and directives Test: Organizational processes for defining, receiving, generating, disseminating, and complying with security alerts, advisories, and directives; mechanisms supporting or implementing definition, receipt, generation, and dissemination of security alerts, advisories, and directives',
            "kind": 'evidence',
        },
    },
    "SI.L2-3.14.4": {
        "a": {
            "deliverable": 'Malicious code signature update policy',
            "how": 'Examine: System and information integrity policy; configuration management policy and procedures Test: Organizational processes for employing, updating, and configuring malicious code protection mechanisms; organizational process for addressing false positives and resulting potential impact',
            "kind": 'evidence',
        },
    },
    "SI.L2-3.14.5": {
        "a": {
            "deliverable": 'Malicious code scan frequency policy',
            "how": 'Examine: System and information integrity policy; configuration management policy and procedures; procedures addressing malicious code protection',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Malicious code scan records',
            "how": 'Examine: System and information integrity policy; configuration management policy and procedures Test: Organizational processes for employing, updating, and configuring malicious code protection mechanisms; organizational process for addressing false positives and resulting potential impact',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Real-time external file malicious code scan configuration',
            "how": 'Examine: System and information integrity policy; configuration management policy and procedures Test: Organizational processes for employing, updating, and configuring malicious code protection mechanisms; organizational process for addressing false positives and resulting potential impact',
            "kind": 'config',
        },
    },
    "SI.L2-3.14.6": {
        "a": {
            "deliverable": 'System attack monitoring configuration',
            "how": 'Examine: System and information integrity policy; procedures addressing system monitoring tools and techniques Test: Organizational processes for system monitoring; mechanisms supporting or implementing intrusion detection capability and system monitoring',
            "kind": 'evidence',
        },
        "b": {
            "deliverable": 'Inbound attack monitoring configuration',
            "how": 'Examine: System and information integrity policy; procedures addressing system monitoring tools and techniques Test: Organizational processes for system monitoring; mechanisms supporting or implementing intrusion detection capability and system monitoring',
            "kind": 'evidence',
        },
        "c": {
            "deliverable": 'Outbound attack monitoring configuration',
            "how": 'Examine: System and information integrity policy; procedures addressing system monitoring tools and techniques Test: Organizational processes for system monitoring; mechanisms supporting or implementing intrusion detection capability and system monitoring',
            "kind": 'evidence',
        },
    },
    "SI.L2-3.14.7": {
        "a": {
            "deliverable": 'Authorized system use definition',
            "how": 'Examine: Continuous monitoring strategy; system and information integrity policy; procedures addressing system monitoring tools and techniques',
            "kind": 'policy',
        },
        "b": {
            "deliverable": 'Unauthorized system use detection configuration',
            "how": 'Examine: Continuous monitoring strategy; system and information integrity policy; procedures addressing system monitoring tools and techniques',
            "kind": 'config',
        },
    },
}
