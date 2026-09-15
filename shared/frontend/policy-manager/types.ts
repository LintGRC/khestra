export type PolicyItem = {
  id: string;
  name: string;
  version: string;
  description: string;
  content: string;
  filename: string;
  file_uploaded: boolean;
  status?: string;
  mapped_controls: string[];
  created_at: string;
  updated_at: string;
};

export type AttestationItem = {
  id: string;
  policy_id: string;
  user_name: string;
  date: string;
  acknowledged: boolean;
};

export type TemplateItem = {
  key: string;
  name: string;
  short_name: string;
  description: string;
  mapped_controls: string[];
  framework_tags: string[];
};

export type PolicyCoverage = {
  policies_total: number;
  controls_with_policy: number;
  controls_total: number;
  coverage_pct: number;
  by_control: Record<string, number>;
};

export type PolicyMapping = {
  id: string;
  policy_id: string;
  framework: string;
  control_id: string;
  control_label: string;
  mapped_at: string;
};

export type FrameworkMeta = {
  id: string;
  label: string;
  shortLabel: string;
  live?: boolean;
};

export const KNOWN_FRAMEWORKS: FrameworkMeta[] = [
  { id: "soc2", label: "SOC 2", shortLabel: "SOC 2", live: true },
  { id: "cmmc", label: "CMMC Level 2", shortLabel: "CMMC", live: true },
  { id: "aigovernance", label: "AI Governance", shortLabel: "AI Gov", live: true },
  { id: "iso42001", label: "ISO 42001", shortLabel: "ISO 42001", live: true },
  { id: "iso27001", label: "ISO 27001", shortLabel: "ISO 27001", live: false },
  { id: "eu_ai_act", label: "EU AI Act", shortLabel: "EU AI Act", live: true },
  { id: "nist_ai_rmf", label: "NIST AI RMF", shortLabel: "AI RMF", live: true },
];

export const LIVE_FRAMEWORKS: FrameworkMeta[] = KNOWN_FRAMEWORKS.filter((f) => f.live);
export const FUTURE_FRAMEWORKS: FrameworkMeta[] = KNOWN_FRAMEWORKS.filter((f) => !f.live);
