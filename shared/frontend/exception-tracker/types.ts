export type RiskLevel = "low" | "medium" | "high" | "critical";

export type ExceptionStatus =
  | "open"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "expired"
  | "closed";

export type HistoryEntry = {
  id: string;
  timestamp: string;
  action: string;
  notes: string;
  detail?: string;
  performed_by?: string;
};

export type Attachment = {
  id: string;
  filename: string;
  stored_as: string;
  uploaded_at: string;
};

export type Comment = {
  id: string;
  author: string;
  body: string;
  created_at: string;
};

export type Milestone = {
  id: string;
  description: string;
  target_date: string;
  completion_date: string;
  status: "not_started" | "in_progress" | "completed";
  owner: string;
  evidence: string;
  created_at: string;
  updated_at: string;
};

export type ExceptionItem = {
  id: string;
  title: string;
  description: string;
  org_id: string;
  workspace_id: string;
  framework: string;
  control_id: string;
  control_reference: string;
  status: ExceptionStatus;
  risk_level: RiskLevel;
  likelihood: number;
  impact: number;
  compensating_controls: string;
  risk_acceptance: string;
  owner: string;
  created_by: string;
  approved_by: string;
  expiry_date: string;
  expiry_days: number;
  approval_notes: string;
  notes: string;
  model_id: string;
  risk_assessment: Record<string, unknown> | null;
  milestones: Milestone[];
  comments: Comment[];
  attachments: Attachment[];
  history: HistoryEntry[];
  extension_log: ExtensionLogEntry[];
  created_at: string;
  updated_at: string;
  risk_score: number;
  risk_color: string;
  expires_at: string | null;
  days_left: number;
  is_expired: boolean;
};

export type ExtensionLogEntry = {
  old_expiry_days: number;
  new_expiry_days: number;
  old_expiry_date: string;
  reason: string;
  changed_by: string;
  timestamp: string;
};

export type Stats = {
  total: number;
  open: number;
  pending_approval: number;
  approved: number;
  rejected: number;
  expired: number;
  expiring_soon: number;
  closed: number;
  by_status: Record<string, number>;
  by_risk: Record<string, number>;
};

export type Reminder = {
  id: string;
  message: string;
  days_left: number;
  is_expired: boolean;
  risk_level: string;
  title: string;
};

export type ExceptionCreateBody = {
  title: string;
  description: string;
  framework: string;
  control_id: string;
  control_reference: string;
  likelihood: number;
  impact: number;
  compensating_controls: string;
  owner: string;
  expiry_days: number;
  model_id?: string;
};

export type ExceptionUpdateBody = Partial<ExceptionCreateBody> & {
  status?: ExceptionStatus;
  approved_by?: string;
  notes?: string;
};
