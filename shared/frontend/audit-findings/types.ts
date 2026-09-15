export type FindingSeverity = "critical" | "high" | "medium" | "low" | "info";

export type FindingStatus =
  | "open"
  | "in_progress"
  | "in_remediation"
  | "resolved"
  | "verified"
  | "closed"
  | "dismissed";

export type FindingItem = {
  id: string;
  title: string;
  description: string;
  remediation: string;
  source: string;
  source_id: string;
  severity: string;
  status: string;
  owner: string;
  framework: string;
  control_ids: string[];
  evidence_ids: string[];
  tags: string[];
  created_by: string;
  created_at: string;
  updated_at: string;
};

export type FindingCreateBody = {
  title: string;
  description?: string;
  remediation?: string;
  source?: string;
  source_id?: string;
  severity?: string;
  status?: string;
  owner?: string;
  framework?: string;
  control_ids?: string[];
  evidence_ids?: string[];
  tags?: string[];
};

export type FindingUpdateBody = Partial<FindingCreateBody>;

export type CorrectiveAction = {
  id: string;
  finding_id: string;
  title: string;
  description: string;
  owner: string;
  target_date: string;
  status: string;
  completed_at: string;
  evidence_id: string;
  notes: string;
  created_by: string;
  created_at: string;
  updated_at: string;
};

export const SEVERITIES: readonly FindingSeverity[] = [
  "critical",
  "high",
  "medium",
  "low",
  "info",
] as const;

export const STATUSES: readonly FindingStatus[] = [
  "open",
  "in_progress",
  "in_remediation",
  "resolved",
  "verified",
  "closed",
  "dismissed",
] as const;
