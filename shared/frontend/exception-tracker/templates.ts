export type ExceptionTemplate = {
  id: string;
  label: string;
  title: string;
  description: string;
  framework: string;
  control_reference: string;
  likelihood: number;
  impact: number;
  expiry_days: number;
  compensating_controls: string;
};

export const EXCEPTION_TEMPLATES: ExceptionTemplate[] = [
  {
    id: "mfa-legacy",
    label: "MFA on Legacy System",
    title: "MFA not supported on legacy payroll server",
    description:
      "The legacy SunOS server hosting the payroll application does not support SAML, OIDC, or any modern MFA protocol. Migration to a supported OS is planned for Q4.",
    framework: "SOC2",
    control_reference: "CC6.1",
    likelihood: 3,
    impact: 5,
    expiry_days: 90,
    compensating_controls:
      "IP allowlisting to authorized corporate ranges, SIEM logging of all authentication attempts, monthly access review by IT operations, VPN required for all administrative access.",
  },
  {
    id: "vendor-no-sso",
    label: "Vendor Without SSO",
    title: "No SSO for LMS platform",
    description:
      "The learning management system vendor only supports username/password authentication. SSO/SAML integration is on the vendor's roadmap but not yet available.",
    framework: "SOC2",
    control_reference: "CC6.1",
    likelihood: 2,
    impact: 3,
    expiry_days: 180,
    compensating_controls:
      "MFA enforced at the application level, quarterly access review, 90-day password rotation enforced, account lockout after 5 failed attempts.",
  },
  {
    id: "unpatched-cve",
    label: "Deferred Security Patch",
    title: "Critical patch deferred on file server",
    description:
      "The critical security patch CVE-2025-1234 could not be applied during the current change window due to dependency conflicts with the legacy accounting interface. Patching scheduled for next maintenance window.",
    framework: "SOC2",
    control_reference: "CC7.1",
    likelihood: 3,
    impact: 4,
    expiry_days: 60,
    compensating_controls:
      "Host isolated on a segmented VLAN, egress restricted to approved IPs only, WAF rules deployed at perimeter, enhanced monitoring and alerting enabled.",
  },
  {
    id: "service-account",
    label: "Shared Service Account",
    title: "Non-rotating service account for batch processing",
    description:
      "The batch processing service account SVC_BATCH is shared across 12 scheduled jobs. Individual service principals cannot be used until the job scheduler is upgraded.",
    framework: "SOC2",
    control_reference: "CC6.3",
    likelihood: 2,
    impact: 4,
    expiry_days: 120,
    compensating_controls:
      "Service account password is 32+ characters and stored in the enterprise secrets vault, rotated every 60 days, usage logged to SIEM, approval required for any credential retrieval.",
  },
  {
    id: "encryption-gap",
    label: "Legacy Encryption Algorithm",
    title: "TLS 1.0 enabled for legacy payment terminal",
    description:
      "One payment terminal model in the warehouse still requires TLS 1.0. The hardware replacement is approved but backordered. TLS 1.2+ is enforced for all other traffic.",
    framework: "SOC2",
    control_reference: "CC6.7",
    likelihood: 2,
    impact: 5,
    expiry_days: 90,
    compensating_controls:
      "Terminal is on a dedicated PCI VLAN with strict ACLs, only connects to the payment processor FQDN, network-level IPS monitors for protocol downgrade attacks.",
  },
  {
    id: "access-review",
    label: "Quarterly Access Review Override",
    title: "Emergency break-glass account for network admins",
    description:
      "Two break-glass administrative accounts exist for emergency network access during incident response. These accounts are excluded from automated de-provisioning.",
    framework: "SOC2",
    control_reference: "CC6.2",
    likelihood: 1,
    impact: 3,
    expiry_days: 365,
    compensating_controls:
      "Break-glass accounts require two-person activation, usage triggers immediate alert to CISO, credentials are stored in a sealed envelope in the safe, reviewed quarterly.",
  },
];
