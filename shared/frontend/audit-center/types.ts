export type AuditStatus = "planned" | "in_progress" | "frozen" | "completed" | "cancelled";
export type AuditType = "internal" | "external" | "readiness" | "certification" | "surveillance";
export type RequestStatus = "open" | "submitted" | "approved" | "rejected" | "waived";

export const AUDIT_STATUSES = ["planned", "in_progress", "frozen", "completed", "cancelled"] as const;
export const AUDIT_TYPES = ["internal", "external", "readiness", "certification", "surveillance"] as const;
export const REQUEST_STATUSES = ["open", "submitted", "approved", "rejected", "waived"] as const;

export type Audit = {
  id: string;
  title: string;
  framework: string;
  audit_type: string;
  start_date: string;
  end_date: string;
  status: string;
  auditor_name: string;
  auditor_email: string;
  scope_notes: string;
  preparation_notes: string;
  control_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
};

export type AuditCreate = {
  title: string;
  framework?: string;
  audit_type?: string;
  start_date?: string;
  end_date?: string;
  auditor_name?: string;
  auditor_email?: string;
  scope_notes?: string;
  preparation_notes?: string;
  control_id?: string;
  created_by?: string;
};

export type AuditUpdate = Partial<AuditCreate> & { status?: string };

export type EvidenceRequest = {
  id: string;
  audit_id: string;
  title: string;
  control_id: string;
  description: string;
  requested_by: string;
  assigned_to: string;
  status: string;
  evidence_id: string;
  evidence_notes: string;
  due_date: string;
  created_at: string;
  updated_at: string;
};

export type RequestCreate = {
  title: string;
  control_id?: string;
  description?: string;
  requested_by?: string;
  assigned_to?: string;
  evidence_notes?: string;
  due_date?: string;
};

export type RequestUpdate = Partial<RequestCreate> & { status?: string; evidence_id?: string };

export type AuditStats = {
  total_audits: number;
  total_evidence_requests: number;
  by_status: Record<string, number>;
  by_framework: Record<string, number>;
  by_audit_type: Record<string, number>;
  request_statuses: Record<string, number>;
};
