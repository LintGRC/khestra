export type Severity = "critical" | "high" | "medium" | "low";
export type Status = "triage" | "investigation" | "containment" | "root_cause_analysis" | "remediation" | "closed";
export type FailureMode =
  | "prompt_injection" | "model_poisoning" | "model_drift"
  | "data_exfiltration" | "systemic_bias" | "security_breach"
  | "agent_failure" | "other";

export type Impact = {
  description?: string;
  affected_inference_pct?: number;
  total_users_exposed?: number;
  downstream_applications?: string[];
};

export type Timeline = {
  reported_at?: string;
  triaged_at?: string | null;
  investigation_at?: string | null;
  contained_at?: string | null;
  rca_at?: string | null;
  remediation_at?: string | null;
  closed_at?: string | null;
};

export type RegulatoryClock = {
  type?: string;
  days?: number;
  label?: string;
  deadline?: string;
  notified?: boolean;
  notified_at?: string | null;
};

export type Telemetry = {
  prompt?: string;
  response?: string;
  model_parameters?: Record<string, unknown>;
  anonymized_logs?: string;
  snapshot_taken_at?: string | null;
};

export type Rca = {
  root_cause?: string;
  contributing_factors?: string[];
  lessons_learned?: string;
  blast_radius?: string;
};

export type EvidenceItem = {
  id: string;
  filename: string;
  label: string;
  size: number;
  uploaded_at: string;
};

export type CorrectiveAction = {
  id: string;
  description: string;
  assigned_to?: string;
  due_date?: string;
  status: "pending" | "in_progress" | "completed";
  completed_at?: string | null;
};

export type RegulatoryReport = {
  id: string;
  report_type: "initial" | "supplemental" | "final";
  submitted_to?: string;
  content?: string;
  created_at: string;
  submitted_at?: string | null;
};

export type HistoryEntry = {
  timestamp: string;
  action: string;
  detail?: string;
};

export type Incident = {
  id: string;
  title: string;
  description?: string;
  failure_mode?: FailureMode;
  severity: Severity;
  status: Status;
  model_id?: string;
  model_name?: string;
  system_id?: string;
  reporter_name?: string;
  source?: string;
  external_id?: string;
  control_id?: string;
  impact?: Impact;
  timeline?: Timeline;
  regulatory_clock?: RegulatoryClock;
  telemetry?: Telemetry;
  rca?: Rca;
  evidence?: EvidenceItem[];
  corrective_actions?: CorrectiveAction[];
  regulatory_reports?: RegulatoryReport[];
  history?: HistoryEntry[];
  created_at: string;
  updated_at: string;
};

export type Playbook = {
  title: string;
  sections: Record<string, string[]>;
};

export const SEVERITY_LABELS: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

export const STATUS_LABELS: Record<string, string> = {
  triage: "Triage",
  investigation: "Investigation",
  containment: "Containment",
  root_cause_analysis: "Root Cause Analysis",
  remediation: "Remediation",
  closed: "Closed",
};

export const FAILURE_MODE_LABELS: Record<string, string> = {
  prompt_injection: "Prompt Injection",
  model_poisoning: "Model Poisoning",
  model_drift: "Model Drift",
  data_exfiltration: "Data Exfiltration",
  systemic_bias: "Systemic Bias",
  security_breach: "Security Breach",
  agent_failure: "Agent Failure",
  other: "Other",
};
