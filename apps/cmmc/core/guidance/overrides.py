"""Hand-edited guidance overrides — edit this file to tune plain summaries and 800-171A objectives."""

# Plain-language one-liners (override auto-generated summaries)
PLAIN_SUMMARY_OVERRIDES = {
    "IA.L2-3.5.3": "Require MFA for admin accounts and for remote access by regular users.",
    "IA.L2-3.5.8": "Block users from reusing recent passwords.",
    "IA.L2-3.5.9": "Temporary passwords must be changed on first login.",
    "IA.L2-3.5.10": "Never store or send passwords in clear text — use hashing and encryption.",
    "IA.L2-3.5.11": "Hide passwords as users type; don't leak hints in error messages.",
    "SC.L2-3.13.11": "Use FIPS-validated encryption wherever CUI is protected.",
    "AC.L2-3.1.8": "Lock accounts after too many failed login attempts.",
    "AC.L2-3.1.15": "Control who can run admin commands remotely — require approval and logging (PAM, jump server, or similar).",
    "SC.L2-3.13.8": "Encrypt CUI when it moves across networks.",
}

# Per-control 800-171A-style examine/interview/test prompts (override generated text)
CONTROL_OBJECTIVE_OVERRIDES = {
    "AC.L2-3.1.8": [
        "Examine: account lockout policy for domain and cloud IdP.",
        "Test: trigger failed logons on sample account; verify lockout and reset timing.",
    ],
    "AC.L2-3.1.15": [
        "Examine: remote access / privileged access policy; PAM or jump-host configuration.",
        "Interview: admins on approval workflow for remote privileged sessions.",
        "Test: verify remote privileged commands require authorization and appear in SIEM/PAM logs.",
    ],
    "IA.L2-3.5.3": [
        "Examine: MFA policy and Conditional Access / IdP configuration.",
        "Test: privileged and remote non-privileged logons require MFA.",
        "Interview: admins on break-glass and MFA enrollment process.",
    ],
    "IA.L2-3.5.8": [
        "Examine: password history policy in AD/Entra ID.",
        "Test: verify password reuse is blocked for configured generations.",
    ],
    "IA.L2-3.5.10": [
        "Examine: authentication protocol and storage standards (no plaintext passwords).",
        "Test: confirm LDAPS/TLS for auth traffic; hashed storage only.",
    ],
    "SC.L2-3.13.11": [
        "Examine: crypto standard referencing FIPS 140-validated modules.",
        "Test: endpoints/servers processing CUI run FIPS-approved algorithms.",
    ],
    "SC.L2-3.13.8": [
        "Examine: encryption in transit standard (TLS/IPsec).",
        "Test: sample CUI transmission uses approved cipher suites.",
    ],
    "AU.L2-3.3.4": [
        "Examine: alerting runbook when log ingestion fails.",
        "Test: simulate logging failure; verify alert within SLA.",
    ],
    "AU.L2-3.3.5": [
        "Examine: SIEM correlation rules and IR escalation paths.",
        "Interview: SOC on suspicious activity triage workflow.",
    ],
    "CM.L2-3.4.7": [
        "Examine: hardening baseline restricting ports/services.",
        "Test: scan sample host for nonessential open services.",
    ],
    "IR.L2-3.6.2": [
        "Examine: IR plan reporting chain (internal + DoW breach).",
        "Interview: IR lead on last tabletop or real incident.",
    ],
    "MP.L2-3.8.6": [
        "Examine: removable media encryption procedure.",
        "Test: sample external drive requires encryption before CUI export.",
    ],
}

# Family-level assessment prompts (800-171A style)
FAMILY_PROMPTS = {
    "Access Control": [
        "Examine: access control policy, account listings, remote access config.",
        "Interview: system admins on provisioning and review process.",
        "Test: sample user accounts for least privilege and lockout settings.",
    ],
    "Awareness and Training": [
        "Examine: security awareness policy, training records, CUI handling materials.",
        "Interview: personnel on reporting incidents and handling CUI.",
    ],
    "Audit and Accountability": [
        "Examine: audit policy, log retention settings, SIEM/export samples.",
        "Test: generate sample audit records for privileged actions.",
    ],
    "Configuration Management": [
        "Examine: baseline configuration docs, change control tickets.",
        "Test: sample system for unauthorized software or open ports.",
    ],
    "Identification and Authentication": [
        "Examine: password/MFA policy, IdP configuration exports.",
        "Test: verify MFA enforced for privileged and remote access.",
    ],
    "Incident Response": [
        "Examine: IR plan, recent tabletop or ticket examples.",
        "Interview: IR lead on escalation and reporting timelines.",
    ],
    "Maintenance": [
        "Examine: maintenance policy, remote maintenance procedures.",
        "Test: remote maintenance session requires MFA and logging.",
    ],
    "Media Protection": [
        "Examine: media sanitization procedures, portable media restrictions.",
    ],
    "Personnel Security": [
        "Examine: screening policy, termination checklists.",
        "Interview: HR/security on personnel screening workflow.",
    ],
    "Physical Protection": [
        "Examine: facility access logs, visitor procedures, CUI storage areas.",
    ],
    "Risk Assessment": [
        "Examine: risk assessment policy, latest risk register.",
    ],
    "Security Assessment": [
        "Examine: security assessment plan, POA&M, prior assessment results.",
    ],
    "System and Communications Protection": [
        "Examine: boundary protection architecture, encryption standards.",
        "Test: FIPS-validated crypto where CUI is protected in transit/at rest.",
    ],
    "System and Information Integrity": [
        "Examine: malware protection policy, patch management records.",
        "Test: malicious code protection active on sample endpoints.",
    ],
}

# Default evidence hints when no per-control objectives exist
DEFAULT_EVIDENCE_HINTS = [
    "Examine: policy or standard that covers this control.",
    "Interview: person responsible for this control in your org.",
    "Test: sample showing the control works as described.",
]
