import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";

export { apiUrl } from "@shared/apiPrefix";

export type Dashboard = {
  client_id: string;
  org_name: string;
  readiness_pct: number;
  evidence_coverage_pct: number;
  auto_coverage_pct: number;
  controls_met: number;
  controls_total: number;
  controls_assessed: number;
  open_gaps: number;
  open_exceptions: number;
  expired_exceptions: number;
  active_risks: number;
  critical_risks: number;
  high_risks: number;
  open_findings: number;
  material_findings: number;
  policy_coverage: PolicyCoverage;
  coverage: CoverageItem[];
  category_readiness: CategoryReadiness[];
  freshness: Record<string, number>;
  evidence_total: number;
  evidence_review_pending: number;
  open_requests: number;
  active_audit_period: AuditPeriod | null;
  frozen_audit_period: AuditPeriod | null;
  recent_activity: ActivityEvent[];
  is_demo?: boolean;
  demo_id?: string;
  test_pass_rate?: number;
  test_total?: number;
  test_pass?: number;
  test_fail?: number;
  test_not_tested?: number;
  test_needs_review?: number;
  overdue_tests?: number;
  period_coverage?: PeriodCoverage;
  pof_total?: number;
  pof_addressed?: number;
  pof_not_applicable?: number;
  pof_applicable?: number;
  pof_coverage_pct?: number;
  scoping_completed?: boolean;
};

export type CoverageItem = {
  id: string;
  category?: string;
  status: string;
  has_evidence: boolean;
  has_auto_evidence: boolean;
  evidence_count: number;
  freshness: string;
  last_evidence_date: string | null;
};

export type CategoryReadiness = {
  category: string;
  total: number;
  met: number;
  readiness_pct: number;
};

export type ActivityEvent = {
  type: string;
  control_id?: string;
  filename?: string;
  status?: string;
  title?: string;
  timestamp: string;
  is_auto?: boolean;
};

export type ControlTest = {
  id: string;
  control_id: string;
  framework: string;
  test_procedure: string;
  frequency: string;
  sample_size: number;
  sampling_methodology?: string;
  population_size?: number;
  confidence_level?: number;
  margin_of_error?: number;
  last_tested: string | null;
  next_test_due: string | null;
  status: string;
  tested_by: string;
  evidence_id: string;
  notes: string;
  created_by: string;
  created_at: string;
  updated_at: string;
};

export type TestResultItem = {
  id: string;
  test_id: string;
  result: string;
  tested_by: string;
  tested_at: string;
  evidence_id: string;
  notes: string;
  created_at: string;
};

export type TestStats = {
  total: number;
  by_status: Record<string, number>;
  by_framework: Record<string, number>;
  pass_rate: number;
  not_tested: number;
  pass: number;
  fail: number;
  needs_review: number;
};

export type PointOfFocus = {
  id: string;
  text: string;
  theme: string;
  evidence_hints?: string[];
};

export type PofStatus = {
  status: "addressed" | "not_applicable";
  justification?: string;
};

export type ControlSummary = {
  id: string;
  code: string;
  category: string;
  name: string;
  description: string;
  status: string;
  has_narrative: boolean;
  evidence_count: number;
  auto_evidence_count: number;
  last_evidence_date: string | null;
  has_auto_evidence: boolean;
  owner?: string;
  target_date?: string;
  operating_status?: string;
  pof_total?: number;
  pof_addressed?: number;
  pof_not_applicable?: number;
  pof_coverage_pct?: number;
};

export type EvidenceGuidance = {
  text: string;
  maps_to_pofs: string[];
  collectors: string[];
};

export type TscCategoryInfo = {
  label: string;
  description: string;
  mandatory: boolean;
  guidance_question: string;
  example_commitment: string;
  criteria_count: number;
};

export type TscScopeResponse = {
  scope: Record<string, boolean>;
  categories: Record<string, TscCategoryInfo>;
  summary: {
    selected_categories: number;
    total_categories: number;
    in_scope_criteria: number;
    total_criteria: number;
    by_category: Record<string, { selected: boolean; mandatory: boolean; criteria_count: number }>;
  };
  scoping_completed: boolean;
};

export type ReadinessTrendsResponse = {
  trends: {
    timestamp: string;
    event: string;
    readiness_pct: number;
    composite_score: number;
    evidence_coverage_pct: number;
    quality_evidence_pct: number;
    gap_count: number;
    controls_total: number;
    controls_met: number;
  }[];
  latest: {
    timestamp: string;
    readiness_pct: number;
    composite_score: number;
  } | null;
  count: number;
  improvement: number;
};

export type NotificationItem = {
  id: string;
  recipient: string;
  type: string;
  title: string;
  body: string;
  link: string;
  read: boolean;
  created_at: string;
};

export type NotificationsResponse = {
  notifications: NotificationItem[];
  unread_count: number;
};

export type ControlDetail = ControlSummary & {
  implementation_narrative: string;
  assessor_notes: string;
  remediation_plan: string;
  frequency: string;
  frequency_options: string[];
  last_review_date: string;
  next_review_date: string;
  evidence: EvidenceItem[];
  status_options: string[];
  operating_status_options?: string[];
  evidence_guidance?: EvidenceGuidance;
  reviews: ReviewItem[];
  linked_policies?: { id: string; title: string; version?: number }[];
  linked_assets?: { id: string; name?: string; asset_name?: string; type?: string; asset_type?: string; cui?: string }[];
  linked_team?: string[];
  linking_profile?: {
    policies: string[];
    assets: string[] | null;
    team: string[];
  };
  points_of_focus: PointOfFocus[];
  pof_statuses: Record<string, PofStatus>;
  comments: CommentItem[];
};

export type EvidenceItem = {
  id?: string;
  control_id: string;
  filename: string;
  upload_date: string;
  sha256: string;
  is_auto?: boolean;
  source?: string;
  review_status?: string;
  reviewer?: string;
  reviewed_at?: string;
  review_comment?: string;
  valid_from?: string;
  valid_to?: string | null;
};

export type PeriodCoverage = {
  period_id: string | null;
  period_name: string;
  start_date: string | null;
  end_date: string | null;
  total_controls: number;
  controls_covered: number;
  coverage_pct: number;
  per_control: Record<string, { evidence_count: number; has_evidence: boolean; valid_from_range: string | null; valid_to_range: string | null }>;
};

export type ReviewItem = {
  filename: string;
  reviewer: string;
  status: string;
  comment: string;
  reviewed_at: string;
};

export type Settings = {
  org_name: string;
  current_role: string;
  current_user_name: string;
  capabilities: { edit_controls?: boolean; view_dashboard?: boolean };
  status_options: string[];
  operating_status_options?: string[];
  user_roles: string[];
  is_demo?: boolean;
  demo_id?: string;
  workspace_locked?: boolean;
  auth_enabled?: boolean;
  auth_role_locked?: boolean;
  auth_user_email?: string;
  clients?: { id: string; name: string; created?: string }[];
  active_client_id?: string;
};

export type DemoStatus = {
  is_demo: boolean;
  demo_id?: string;
  org_name?: string;
  label?: string;
};

export type AuditPeriod = {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  frozen: boolean;
  frozen_at: string | null;
  created_at: string;
};

export type Soc2Engagement = {
  type: string;
  firm: string;
  cpa_contact: string;
  engagement_start: string;
  engagement_end: string;
  status: string;
};

export type AuditLogEntry = {
  timestamp: string;
  event: string;
  user: string;
  [key: string]: unknown;
};

export type EvidenceManifest = {
  generated_at: string;
  total_evidence: number;
  controls_covered: number;
  manifest_hash: string;
  items: { control_id: string; filename: string; sha256: string; upload_date: string; review_status: string }[];
};

export type EvidenceRequest = {
  id: string;
  control_id: string;
  title: string;
  description: string;
  assigned_to: string;
  due_date: string;
  status: string;
  created_at: string;
};

export type ConnectorMonitorState = {
  connector_id: string;
  enabled: boolean;
  interval: "manual" | "daily" | "weekly";
  last_run_at: string | null;
  last_status: string;
  attach_on_run: boolean;
};

export type CollectorInfo = {
  id: string;
  name: string;
  description: string;
  required_fields: string[];
  optional_fields: string[];
  permissions_hint?: string;
  configured: boolean;
  configured_fields?: string[];
  missing_fields?: string[];
  monitor?: ConnectorMonitorState | null;
};

export type DriftEvent = {
  id: string;
  connector_id: string;
  check_id: string;
  event_type: string;
  summary: string;
  details?: string;
  timestamp: string;
  message?: string;
};

export type EvidenceFreshness = {
  max_age_days: number;
  stale_check_count: number;
  stale_control_count: number;
  stale_checks?: { connector_id: string; check_id: string; collected_at?: string }[];
  stale_controls?: { control_id: string; latest_upload?: string }[];
  controls?: unknown[];
};

export type WebhookCollectorInfo = {
  id: string;
  name: string;
  source_system: string;
  webhook_token?: string;
  token_hint?: string;
  created_at?: string;
  last_ingest_at?: string | null;
  ingest_count?: number;
  enabled?: boolean;
  ingest_url?: string;
};

export type CollectorsDashboard = {
  connectors: CollectorInfo[];
  monitoring: { due_connectors: string[] };
  drift_events: DriftEvent[];
  freshness: EvidenceFreshness;
};

// --- Exceptions / POA&M ---

export type ExceptionItem = {
  id: string;
  title?: string;
  control_id: string;
  framework?: string;
  status: "open" | "pending_approval" | "approved" | "rejected" | "expired" | "closed";
  risk_level: "low" | "medium" | "high" | "critical";
  description: string;
  compensating_controls: string;
  risk_acceptance: string;
  created_by: string;
  approved_by: string;
  expiry_date: string;
  created_at: string;
  updated_at: string;
};

export type ExceptionBody = {
  control_id: string;
  title?: string;
  status?: string;
  risk_level?: string;
  description?: string;
  compensating_controls?: string;
  risk_acceptance?: string;
  created_by?: string;
  approved_by?: string;
  expiry_date?: string;
};

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({ "Content-Type": "application/json", ...(init?.headers || {}) });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

// --- Risk Register ---

export type RiskItem = {
  id: string;
  control_id: string;
  title: string;
  description: string;
  category: string;
  inherent_likelihood: string;
  inherent_impact: string;
  residual_likelihood: string;
  residual_impact: string;
  treatment: string;
  controls: string;
  owner: string;
  status: string;
  inherent_score: number;
  residual_score: number;
  inherent_level: string;
  residual_level: string;
  review_date: string;
  created_at: string;
  updated_at: string;
  closed_at: string;
};

export type RiskBody = {
  control_id?: string;
  title?: string;
  description?: string;
  category?: string;
  inherent_likelihood?: string;
  inherent_impact?: string;
  residual_likelihood?: string;
  residual_impact?: string;
  treatment?: string;
  controls?: string;
  owner?: string;
  status?: string;
  review_date?: string;
};

// --- Policy Management ---

export type PolicyItem = {
  id: string;
  name: string;
  version: string;
  description: string;
  content: string;
  filename: string;
  file_uploaded: boolean;
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
};

export type PolicyCoverage = {
  policies_total: number;
  controls_with_policy: number;
  controls_total: number;
  coverage_pct: number;
  by_control: Record<string, number>;
};

// --- Organization Profile ---

export type OrgProfile = Record<string, string>;

export type EnvScope = Record<string, string>;

export type InventoryAsset = Record<string, string>;

export type Organization = {
  org_profile: OrgProfile;
  env_scope: EnvScope;
  env_scope_labels?: { yes_no: Record<string, string>; cloud: Record<string, string> };
  env_scope_complete?: boolean;
  env_scope_summary?: string;
  scoping_suggestions?: { control_id: string; suggestion: string; reason: string }[];
  org_inventory: { assets: InventoryAsset[]; updated_at: string };
  inventory_columns?: string[];
  audit_log: { timestamp: string; event: string; [key: string]: unknown }[];
  needs_wizard: boolean;
  wizard_steps: { key: string; label: string; fields: string[] }[];
  field_labels: Record<string, string>;
  field_placeholders: Record<string, string>;
  org_name: string;
  scoping_completed?: boolean;
};

// --- Readiness Assessment ---

export type ReadinessChecklistItem = {
  key: string;
  label: string;
  done: boolean;
  detail: string;
  required: boolean;
};

export type ReadinessCategory = {
  category: string;
  total: number;
  met: number;
  gap: number;
  readiness_pct: number;
  pof_total?: number;
  pof_addressed?: number;
  pof_not_applicable?: number;
  pof_coverage_pct?: number;
};

export type ReadinessGap = {
  control_id: string;
  category: string;
  name: string;
  status: string;
  has_narrative: boolean;
  has_evidence: boolean;
  owner: string;
  target_date: string;
};

export type ReadinessAssessment = {
  readiness_pct: number;
  composite_score: number;
  controls_total: number;
  controls_met: number;
  controls_assessed: number;
  open_gaps: ReadinessGap[];
  gap_count: number;
  missing_evidence: { control_id: string; category: string; name: string; status: string }[];
  missing_evidence_count: number;
  missing_narrative: { control_id: string; category: string; name: string; status: string }[];
  missing_narrative_count: number;
  category_readiness: ReadinessCategory[];
  profile_score: number;
  evidence_coverage_pct: number;
  quality_evidence_pct?: number;
  controls_with_quality_evidence?: number;
  narrative_coverage_pct: number;
  assessment_pct: number;
  policy_coverage_pct: number;
  policy_mapped_count: number;
  open_exceptions_count: number;
  pof: {
    pof_total: number;
    pof_addressed: number;
    pof_not_applicable: number;
    pof_applicable: number;
    pof_coverage_pct: number;
  };
  checklist: ReadinessChecklistItem[];
  checklist_done: number;
  checklist_total: number;
  blockers: string[];
  effort: string;
  audit_ready: boolean;
};

// --- My Work ---

export type WorkControlItem = {
  control_id: string;
  category: string;
  name: string;
  status: string;
  target_date: string;
  evidence_count: number;
  days_left?: number;
  days_overdue?: number;
};

export type WorkReviewItem = {
  control_id: string;
  filename: string;
  upload_date: string;
  source: string;
};

export type WorkRequestItem = {
  request_id: string;
  control_id: string;
  title: string;
  due_date: string;
  created_at: string;
};

export type MyWork = {
  assigned_controls: WorkControlItem[];
  assigned_count: number;
  due_soon: WorkControlItem[];
  due_soon_count: number;
  overdue: WorkControlItem[];
  overdue_count: number;
  missing_evidence: { control_id: string; category: string; name: string; status: string; owner: string }[];
  missing_evidence_count: number;
  needs_review: WorkReviewItem[];
  needs_review_count: number;
  pending_requests: WorkRequestItem[];
  pending_requests_count: number;
  pending_approval: { id: string; control_id: string; description: string; risk_level: string }[];
  pending_approval_count: number;
};

// --- Comments ---

export type CommentItem = {
  id: string;
  text: string;
  author: string;
  created_at: string;
  parent_id?: string;
  mentions?: string[];
};

export type PriorityQueueItem = {
  control_id: string;
  category: string;
  name: string;
  status: string;
  owner: string;
  target_date: string;
  evidence_count: number;
  narrative: boolean;
  score: number;
  tier: "risk" | "urgent" | "fast" | "blocked" | "normal";
  reasons: string[];
};

export type PriorityQueueResult = {
  items: PriorityQueueItem[];
  total: number;
  tiers: {
    risk: PriorityQueueItem[];
    urgent: PriorityQueueItem[];
    fast: PriorityQueueItem[];
    blocked: PriorityQueueItem[];
  };
  tier_counts: {
    risk: number;
    urgent: number;
    fast: number;
    blocked: number;
    normal: number;
  };
};

export const api = {
  dashboard: () => json<Dashboard>("/api/dashboard"),
  settings: () => json<Settings>("/api/settings"),
  patchRole: (role: string) =>
    json<{ current_role: string }>("/api/settings/role", { method: "PATCH", body: JSON.stringify({ role }) }),
  patchUserName: (name: string) =>
    json<{ current_user_name: string }>("/api/settings/user-name", {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),
  demoStatus: () => json<DemoStatus>("/api/demo/status"),
  loadDemo: (demoId = "northwind") =>
    json<{ org_name: string; readiness_pct: number }>(`/api/demo/load?demo_id=${encodeURIComponent(demoId)}`, {
      method: "POST",
    }),
  clearDemo: () => json<{ status: string }>("/api/demo/clear", { method: "POST" }),
  clients: () => json<{ id: string; name: string; created?: string }[]>("/api/clients"),
  createClient: (name: string) =>
    json<{ client_id: string; name: string; active_client_id: string }>("/api/clients", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  activateClient: (clientId: string) =>
    json<{ active_client_id: string }>(`/api/clients/${encodeURIComponent(clientId)}/activate`, { method: "POST" }),
  renameClient: (clientId: string, name: string) =>
    json<{ client_id: string; name: string }>(`/api/clients/${encodeURIComponent(clientId)}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),
  deleteClient: (clientId: string) =>
    json<{ active_client_id: string }>(`/api/clients/${encodeURIComponent(clientId)}`, { method: "DELETE" }),
  controls: (category?: string, q?: string) => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (q) params.set("q", q);
    const qs = params.toString();
    return json<{
      controls: ControlSummary[];
      status_options: string[];
      category_options: { id: string; label: string }[];
    }>(`/api/controls${qs ? `?${qs}` : ""}`);
  },
  control: (id: string) => json<ControlDetail>(`/api/controls/${encodeURIComponent(id)}`),
  patchControl: (id: string, body: Partial<ControlDetail>) =>
    json<ControlDetail>(`/api/controls/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  uploadEvidence: async (controlId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    const headers = await authHeaders();
    const res = await fetch(apiUrl(`/api/controls/${encodeURIComponent(controlId)}/evidence`), {
      method: "POST",
      headers,
      body: form,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<ControlDetail>;
  },
  reviewEvidence: (controlId: string, filename: string, body: { reviewer: string; status: string; comment?: string }) =>
    json(`/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(filename)}/review`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  evidence: () => json<{ evidence: EvidenceItem[] }>("/api/evidence"),
  evidenceCoverage: (periodId?: string) => {
    const qs = periodId ? `?period_id=${encodeURIComponent(periodId)}` : "";
    return json<PeriodCoverage>(`/api/evidence/coverage${qs}`);
  },
  auditLog: () => json<{ entries: AuditLogEntry[] }>("/api/audit-log"),
  auditPeriods: () => json<{ periods: AuditPeriod[] }>("/api/audit/periods"),
  auditEngagement: () => json<{ engagement: Soc2Engagement }>("/api/audit/engagement"),
  putAuditEngagement: (body: Soc2Engagement) =>
    json<{ engagement: Soc2Engagement }>("/api/audit/engagement", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  createAuditPeriod: (body: { name: string; start_date: string; end_date: string }) =>
    json<{ period: AuditPeriod }>("/api/audit/periods", { method: "POST", body: JSON.stringify(body) }),
  freezeAuditPeriod: (periodId: string) =>
    json<{ period: AuditPeriod }>(`/api/audit/periods/${encodeURIComponent(periodId)}/freeze`, { method: "POST" }),
  manifest: () => json<EvidenceManifest>("/api/audit/manifest"),
  evidenceRequests: () => json<{ requests: EvidenceRequest[] }>("/api/evidence/requests"),
  createEvidenceRequest: (body: { control_id: string; title: string; description?: string; assigned_to?: string; due_date?: string }) =>
    json<{ request: EvidenceRequest }>("/api/evidence/requests", { method: "POST", body: JSON.stringify(body) }),
  patchEvidenceRequest: (id: string, body: { status?: string; assigned_to?: string; due_date?: string }) =>
    json<{ request: EvidenceRequest }>(`/api/evidence/requests/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  activity: () => json<{ activity: ActivityEvent[] }>("/api/evidence/activity"),

  collectors: () => json<CollectorsDashboard>("/api/collectors"),
  saveCollectorCredentials: (connectorId: string, credentials: Record<string, string>) =>
    json(`/api/collectors/${encodeURIComponent(connectorId)}/credentials`, {
      method: "PUT",
      body: JSON.stringify({ credentials }),
    }),
  patchCollectorSchedule: (connectorId: string, patch: { enabled?: boolean; interval?: string; attach_on_run?: boolean }) =>
    json(`/api/collectors/${encodeURIComponent(connectorId)}/schedule`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),
  runCollector: (connectorId: string, opts: { use_fixture?: boolean; attach?: boolean } = {}) =>
    json<{ run: { summary: string }; attached?: unknown[]; drift_events?: unknown[] }>(
      `/api/collectors/${encodeURIComponent(connectorId)}/run`,
      { method: "POST", body: JSON.stringify({ use_fixture: opts.use_fixture, attach: opts.attach ?? true }) },
    ),
  runDue: (useFixtureIfUnconfigured = false) =>
    json<{ ran_count: number; results: unknown[] }>("/api/collectors/monitoring/run-due", {
      method: "POST",
      body: JSON.stringify({ use_fixture_if_unconfigured: useFixtureIfUnconfigured }),
    }),
  webhooks: () =>
    json<{ collectors: { id: string; name: string; source_system: string }[]; env_token_configured: boolean }>("/api/webhooks"),
  createWebhook: (name: string, source_system: string) =>
    json<{ collector: { id: string; name: string }; webhook_token: string; usage: string }>("/api/webhooks", {
      method: "POST",
      body: JSON.stringify({ name, source_system }),
    }),
  deleteWebhook: (collectorId: string) =>
    json(`/api/webhooks/${encodeURIComponent(collectorId)}`, { method: "DELETE" }),
  evidenceDownloadUrl: (controlId: string, filename: string) =>
    apiUrl(`/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(filename)}`),
  deleteEvidence: (controlId: string, filename: string) =>
    json(`/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(filename)}`, {
      method: "DELETE",
    }),
  readinessSummaryUrl: () => apiUrl("/api/reports/readiness-summary"),
  systemDescriptionUrl: () => apiUrl("/api/reports/system-description"),

  // Exceptions / POA&M
  listExceptions: (control_id?: string) =>
    json<{ exceptions: ExceptionItem[] }>("/api/exceptions" + (control_id ? `?control_id=${encodeURIComponent(control_id)}` : "")),
  createException: (body: ExceptionBody) =>
    json<{ exception: ExceptionItem }>("/api/exceptions", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getException: (id: string) =>
    json<{ exception: ExceptionItem }>(`/api/exceptions/${encodeURIComponent(id)}`),
  updateException: (id: string, body: Partial<ExceptionBody>) =>
    json<{ exception: ExceptionItem }>(`/api/exceptions/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deleteException: (id: string) =>
    json(`/api/exceptions/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Risk Register
  listRisks: () => json<{ risks: RiskItem[] }>("/api/risks"),
  createRisk: (body: RiskBody) =>
    json<{ risk: RiskItem }>("/api/risks", { method: "POST", body: JSON.stringify(body) }),
  updateRisk: (id: string, body: Partial<RiskBody>) =>
    json<{ risk: RiskItem }>(`/api/risks/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteRisk: (id: string) =>
    json(`/api/risks/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Policy Management
  listPolicies: () => json<{ policies: PolicyItem[] }>("/api/policies"),
  listTemplates: () => json<{ templates: TemplateItem[] }>("/api/policies/templates"),
  createPolicy: (body: { name: string; version?: string; description?: string; content?: string; filename?: string; mapped_controls?: string[] }) =>
    json<{ policy: PolicyItem }>("/api/policies", { method: "POST", body: JSON.stringify(body) }),
  updatePolicy: (id: string, body: { name?: string; version?: string; description?: string; content?: string; filename?: string; file_uploaded?: boolean; mapped_controls?: string[] }) =>
    json<{ policy: PolicyItem }>(`/api/policies/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(body) }),
  generatePolicy: (id: string, template: string) =>
    json<{ policy: PolicyItem }>(`/api/policies/${encodeURIComponent(id)}/generate`, { method: "POST", body: JSON.stringify({ template }) }),
  exportPolicyUrl: (id: string) => apiUrl(`/api/policies/${encodeURIComponent(id)}/export`),
  deletePolicy: (id: string) =>
    json(`/api/policies/${encodeURIComponent(id)}`, { method: "DELETE" }),
  listAttestations: (policyId?: string) => {
    const qs = policyId ? `?policy_id=${encodeURIComponent(policyId)}` : "";
    return json<{ attestations: AttestationItem[] }>(`/api/policies/attestations${qs}`);
  },
  createAttestation: (body: { policy_id: string; user_name: string }) =>
    json<{ attestation: AttestationItem }>("/api/policies/attestations", { method: "POST", body: JSON.stringify(body) }),

  // Organization Profile
  organization: () => json<Organization>("/api/organization"),
  patchOrgProfile: (body: Partial<OrgProfile>) =>
    json<{ org_profile: OrgProfile; org_name: string }>("/api/org-profile", { method: "PATCH", body: JSON.stringify(body) }),
  patchEnvScope: (body: Partial<EnvScope>) =>
    json<{ env_scope: EnvScope; env_scope_complete: boolean; env_scope_summary: string }>("/api/env-scope", { method: "PATCH", body: JSON.stringify(body) }),
  patchInventory: (assets: InventoryAsset[]) =>
    json<{ org_inventory: { assets: InventoryAsset[]; updated_at: string } }>("/api/inventory", { method: "PATCH", body: JSON.stringify({ assets }) }),

  // Readiness Assessment
  readinessAssessment: () => json<ReadinessAssessment>("/api/readiness/assessment"),

  // My Work
  myWork: () => json<MyWork>("/api/my-work"),

  // Comments
  addComment: (controlId: string, text: string, parent_id?: string) =>
    json<{ comment: CommentItem }>(`/api/controls/${encodeURIComponent(controlId)}/comments`, {
      method: "POST",
      body: JSON.stringify({ text, parent_id }),
    }),
  deleteComment: (controlId: string, commentId: string) =>
    json(`/api/controls/${encodeURIComponent(controlId)}/comments/${encodeURIComponent(commentId)}`, {
      method: "DELETE",
    }),

  // Priority Queue
  priorityQueue: (limit = 30) =>
    json<PriorityQueueResult>(`/api/priority-queue?limit=${limit}`),

  // Tests of Controls (Type 2)
  listTests: (controlId?: string) => {
    const qs = controlId ? `?control_id=${encodeURIComponent(controlId)}` : "";
    return json<{ tests: ControlTest[] }>(`/api/testing/tests${qs}`);
  },
  createTest: (body: { control_id: string; framework?: string; test_procedure: string; frequency?: string; sample_size?: number; notes?: string }) =>
    json<{ test: ControlTest }>("/api/testing/tests", { method: "POST", body: JSON.stringify(body) }),
  getTest: (testId: string) => json<{ test: ControlTest }>(`/api/testing/tests/${encodeURIComponent(testId)}`),
  updateTest: (testId: string, body: Partial<ControlTest>) =>
    json<{ test: ControlTest }>(`/api/testing/tests/${encodeURIComponent(testId)}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteTest: (testId: string) =>
    json(`/api/testing/tests/${encodeURIComponent(testId)}`, { method: "DELETE" }),
  getTestResults: (testId: string) =>
    json<{ results: TestResultItem[] }>(`/api/testing/tests/${encodeURIComponent(testId)}/results`),
  addTestResult: (testId: string, body: { result: string; tested_by?: string; evidence_id?: string; notes?: string }) =>
    json<{ result: TestResultItem }>(`/api/testing/tests/${encodeURIComponent(testId)}/results`, { method: "POST", body: JSON.stringify(body) }),
  testStats: () => json<TestStats>("/api/testing/stats"),

  // Asset & Personnel Inventory
  listAssets: () => json<{ assets: Record<string, unknown>[] }>("/api/assets"),
  listPersonnel: () => json<{ personnel: Record<string, unknown>[] }>("/api/personnel"),

  // Points of Focus
  patchPof: (controlId: string, pofId: string, status: "addressed" | "not_applicable", justification: string = "") =>
    json<ControlDetail>(`/api/controls/${encodeURIComponent(controlId)}/pofs/${encodeURIComponent(pofId)}`, {
      method: "PATCH",
      body: JSON.stringify({ status, justification }),
    }),
  bulkPatchPofs: (controlId: string, updates: Record<string, { status: string; justification?: string }>) =>
    json<ControlDetail>(`/api/controls/${encodeURIComponent(controlId)}/pofs`, {
      method: "PATCH",
      body: JSON.stringify({ updates }),
    }),

  // TSC Scoping
  getScope: () => json<TscScopeResponse>("/api/scoping/tsc"),
  patchScope: (scope: Record<string, boolean>) =>
    json<TscScopeResponse>("/api/scoping/tsc", {
      method: "PATCH",
      body: JSON.stringify({ scope, scoping_completed: true }),
    }),

  // Readiness Trends
  getReadinessTrends: () => json<ReadinessTrendsResponse>("/api/readiness/trends"),

  // Notifications
  getNotifications: (unreadOnly?: boolean) => json<NotificationsResponse>("/api/notifications" + (unreadOnly ? "?unread_only=true" : "")),
  markNotificationRead: (id: string) => json<{ status: string }>(`/api/notifications/${encodeURIComponent(id)}/read`, { method: "PATCH" }),
  markAllNotificationsRead: () => json<{ status: string; marked_read: number }>("/api/notifications/read-all", { method: "PATCH" }),
  help: () => json<{ views: Record<string, { title: string; summary: string; tips: string[] }>; faq: { q: string; a: string }[] }>("/api/help"),
};
