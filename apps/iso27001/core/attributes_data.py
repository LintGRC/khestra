"""ISO/IEC 27002:2022 control attributes (Annex A attribute table).

Extracted from the official 27002:2022 PDF attribute tables (control type,
information security properties, cybersecurity concepts, operational
capabilities, security domains) for all 93 Annex A controls.
"""

CONTROL_ATTRIBUTES = {
    "A.5.1": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Governance"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Resilience"
      ]
    },
    "A.5.2": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Governance"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection",
        "Resilience"
      ]
    },
    "A.5.3": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Governance",
        "Identity_and_access_management"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.5.4": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Governance"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.5.5": {
      "control_type": [
        "Preventive",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect",
        "Respond",
        "Recover"
      ],
      "capabilities": [
        "Governance"
      ],
      "domains": [
        "Defence",
        "Resilience"
      ]
    },
    "A.5.6": {
      "control_type": [
        "Preventive",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Respond",
        "Recover"
      ],
      "capabilities": [
        "Governance"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.7": {
      "control_type": [
        "Preventive",
        "Detective",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Respond",
        "Detect"
      ],
      "capabilities": [
        "Threat_and_vulnerability_management"
      ],
      "domains": [
        "Defence",
        "Resilience"
      ]
    },
    "A.5.8": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Governance"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.9": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Asset_management"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.10": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Asset_management",
        "Information_protection"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.11": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Asset_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.12": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Information_protection"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.5.13": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Information_protection"
      ],
      "domains": [
        "Defence",
        "Protection"
      ]
    },
    "A.5.14": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Asset_management",
        "Information_protection"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.15": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.16": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.17": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.18": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.19": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Supplier_relationships_security"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.20": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Supplier_relationships_security"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.21": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Supplier_relationships_security"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.22": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Supplier_relationships_security",
        "Information_security_assurance"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection",
        "Defence"
      ]
    },
    "A.5.23": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Supplier_relationships_security"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.24": {
      "control_type": [
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Respond",
        "Recover"
      ],
      "capabilities": [
        "Governance",
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.25": {
      "control_type": [
        "Detective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Detect",
        "Respond"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.26": {
      "control_type": [
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Respond",
        "Recover"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.27": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.28": {
      "control_type": [
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Detect",
        "Respond"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.29": {
      "control_type": [
        "Preventive",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Respond"
      ],
      "capabilities": [
        "Continuity"
      ],
      "domains": [
        "Protection",
        "Resilience"
      ]
    },
    "A.5.30": {
      "control_type": [
        "Corrective"
      ],
      "properties": [
        "Availability"
      ],
      "concepts": [
        "Respond"
      ],
      "capabilities": [
        "Continuity"
      ],
      "domains": [
        "Resilience"
      ]
    },
    "A.5.31": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Legal_and_compliance"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.5.32": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Legal_and_compliance"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.5.33": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Legal_and_compliance",
        "Asset_management",
        "Information_protection"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.5.34": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Information_protection",
        "Legal_and_compliance"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.5.35": {
      "control_type": [
        "Preventive",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Information_security_assurance"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.5.36": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Legal_and_compliance",
        "Information_security_assurance"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.5.37": {
      "control_type": [
        "Preventive",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Recover"
      ],
      "capabilities": [
        "Asset_management",
        "Physical_security",
        "System_and_network_security",
        "Application_security",
        "Secure_configuration",
        "Identity_and_access_management",
        "Threat_and_vulnerability_management",
        "Continuity",
        "Information_security_event_management"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection",
        "Defence"
      ]
    },
    "A.6.1": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Human_resource_security"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.6.2": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Human_resource_security"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.6.3": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Human_resource_security"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.6.4": {
      "control_type": [
        "Preventive",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Respond"
      ],
      "capabilities": [
        "Human_resource_security"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.6.5": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Human_resource_security",
        "Asset_management"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.6.6": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Human_resource_security",
        "Information_protection",
        "Supplier_relationships_security"
      ],
      "domains": [
        "Governance_and_Ecosystem"
      ]
    },
    "A.6.7": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Asset_management",
        "Information_protection",
        "Physical_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.6.8": {
      "control_type": [
        "Detective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Detect"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.7.1": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.2": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.3": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Asset_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.4": {
      "control_type": [
        "Preventive",
        "Detective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.7.5": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.6": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.7": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.8": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Asset_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.9": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Asset_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.10": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Asset_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.11": {
      "control_type": [
        "Preventive",
        "Detective"
      ],
      "properties": [
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.12": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.7.13": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Asset_management"
      ],
      "domains": [
        "Protection",
        "Resilience"
      ]
    },
    "A.7.14": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Physical_security",
        "Asset_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.1": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Asset_management",
        "Information_protection"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.2": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.3": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.4": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management",
        "Application_security",
        "Secure_configuration"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.5": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Identity_and_access_management"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.6": {
      "control_type": [
        "Preventive",
        "Detective"
      ],
      "properties": [
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "Continuity"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.8.7": {
      "control_type": [
        "Preventive",
        "Detective",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "System_and_network_security",
        "Information_protection"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.8.8": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Protect"
      ],
      "capabilities": [
        "Threat_and_vulnerability_management"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection",
        "Defence"
      ]
    },
    "A.8.9": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Secure_configuration"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.10": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Information_protection",
        "Legal_and_compliance"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.11": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Information_protection"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.12": {
      "control_type": [
        "Preventive",
        "Detective"
      ],
      "properties": [
        "Confidentiality"
      ],
      "concepts": [
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "Information_protection"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.8.13": {
      "control_type": [
        "Corrective"
      ],
      "properties": [
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Recover"
      ],
      "capabilities": [
        "Continuity"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.14": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Continuity",
        "Asset_management"
      ],
      "domains": [
        "Protection",
        "Resilience"
      ]
    },
    "A.8.15": {
      "control_type": [
        "Detective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Detect"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.8.16": {
      "control_type": [
        "Detective",
        "Corrective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Detect",
        "Respond"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Defence"
      ]
    },
    "A.8.17": {
      "control_type": [
        "Detective"
      ],
      "properties": [
        "Integrity"
      ],
      "concepts": [
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "Information_security_event_management"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.8.18": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "System_and_network_security",
        "Secure_configuration",
        "Application_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.19": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Secure_configuration",
        "Application_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.20": {
      "control_type": [
        "Preventive",
        "Detective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect",
        "Detect"
      ],
      "capabilities": [
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.21": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.22": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.23": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.24": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Secure_configuration"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.25": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Application_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.26": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Application_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection",
        "Defence"
      ]
    },
    "A.8.27": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Application_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.28": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Application_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.29": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify"
      ],
      "capabilities": [
        "Application_security",
        "Information_security_assurance",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.30": {
      "control_type": [
        "Preventive",
        "Detective"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Identify",
        "Detect",
        "Protect"
      ],
      "capabilities": [
        "System_and_network_security",
        "Application_security",
        "Supplier_relationships_security"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
    "A.8.31": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Application_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.32": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Application_security",
        "System_and_network_security"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.33": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "Information_protection"
      ],
      "domains": [
        "Protection"
      ]
    },
    "A.8.34": {
      "control_type": [
        "Preventive"
      ],
      "properties": [
        "Confidentiality",
        "Integrity",
        "Availability"
      ],
      "concepts": [
        "Protect"
      ],
      "capabilities": [
        "System_and_network_security",
        "Information_protection"
      ],
      "domains": [
        "Governance_and_Ecosystem",
        "Protection"
      ]
    },
}
