import { apiUrl } from "@shared/apiPrefix";
import { authHeaders, setAccessTokenGetter } from "@shared/accessToken";

export { apiUrl };
export { setAccessTokenGetter };

export async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  const headers = await authHeaders(init?.headers);
  if (!headers.has("Content-Type") && init?.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiUrl(url), { ...init, headers });
  if (res.status === 401) {
    localStorage.removeItem("khestra_auth_token");
    window.location.href = window.location.pathname.substring(0, window.location.pathname.indexOf("/app")) || "/";
    throw new Error("Session expired — redirecting to login");
  }
  return res;
}

export async function authenticatedDownload(url: string, filename: string) {
  const res = await authFetch(url);
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const objUrl = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = objUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(objUrl);
}

export type DemoStatus = {
  is_demo: boolean;
  demo_id?: string;
  org_name?: string;
  label?: string;
};

export type CmmcScope = {
  esp: string;
  esp_name: string;
  esp_facilities: string;
  facilities: string;
  scope_statement: string;
  assets_in_scope: string;
};

export type ContractRecord = {
  id?: string;
  name: string;
  contract_number: string;
  clause: string;
  required_status: string;
  flowdown_required: boolean;
  notes: string;
  held_status?: string;
  mismatch?: boolean;
};

export type L1Status = {
  score: number;
  total: number;
  met: number;
  rows: Array<{ id: string; title: string; status: string }>;
  status_date: string;
  affirming_official: string;
  affirmed_at: string;
  all_met: boolean;
};

export type Dashboard = {
  client_id: string;
  org_name: string;
  sprs_score: number;
  sprs_max: number;
  open_gaps: number;
  export_readiness_pct: number;
  controls_assessed: number;
  controls_total: number;
  last_export_at: string | null;
  export_stale: boolean;
  blockers: string[];
  cmmc_status?: CmmcAssessmentStatus;
};

export type CmmcAssessmentStatus = {
  assessment_type: string;
  assessment_type_label: string;
  status: string;
  status_date: string;
  affirming_official: string;
  affirmed_at: string;
  sprs_score: number;
  sprs_max: number;
  gap_count: number;
  poam_eligible: boolean;
  poam_blocking: string[];
  closeout_due: string;
  closeout_days_left: number | null;
  closeout_expired: boolean;
  reassessment_due: string;
  reassessment_days_left: number | null;
  reassessment_expired: boolean;
  affirmation_due: string;
  affirmation_days_left: number | null;
  affirmation_expired: boolean;
};

export type CollectorHealthSummary = {
  passing: number;
  failing: number;
  error: number;
  uncollected: number;
  total: number;
};

export type ControlSummary = {
  id: string;
  family: string;
  name: string;
  weight: number;
  weight_tier?: string;
  weight_badge?: string;
  weight_hint?: string;
  status: string;
  has_narrative: boolean;
  evidence_count: number;
  owner?: string;
  target_date?: string;
  overdue?: boolean;
  comment_count?: number;
  collector_status?: string | null;
};

export type ControlComment = {
  id: string;
  author: string;
  text: string;
  created_at: string;
};

export type ControlObjective = {
  letter: string;
  text: string;
  status: string;
  evidence_refs: string[];
  notes: string;
  deliverable?: string;
  how?: string;
  kind?: string;
};

export type EvidenceProvenance = {
  connector_id?: string;
  connector_name?: string;
  check_id?: string;
  check_name?: string;
  status?: string;
  collected_at?: string;
  method?: string;
  period_covered?: string;
  review_status?: string;
  valid_until?: string;
};

export type EvidenceItem = {
  filename: string;
  upload_date: string;
  sha256: string;
  is_hub_evidence?: boolean;
  hub_id?: string;
  evidence_type?: string;
  display_title?: string;
  evidence_version?: string;
  auto_status?: string;
  review_status?: string;
  period_covered?: string;
  provenance?: EvidenceProvenance;
};

export type EvidenceHistoryPeriod = {
  period_covered: string;
  hub_id?: string;
  upload_date?: string;
  status?: string;
  sha256?: string;
  display_title?: string;
};

export type EvidenceHistorySummary = {
  filename: string;
  count: number;
  oldest: string;
  newest: string;
  periods: EvidenceHistoryPeriod[];
};

export type AutomationCoverage = {
  level: "automated" | "partial" | "manual";
  collectors: { check_id: string; connector_id: string; connector_name: string }[];
  gaps: string[];
  summary: string;
  check_count: number;
  connector_count: number;
};

export type ControlDetail = ControlSummary & {
  description: string;
  implementation_narrative: string;
  ai_generated?: boolean;
  ai_generated_at?: string | null;
  ai_draft?: string | null;
  ai_draft_created_at?: string | null;
  ai_draft_method?: string | null;
  assessor_notes: string;
  examine: string;
  interview: string;
  test: string;
  owner: string;
  target_date: string;
  remediation_plan: string;
  estimated_cost: string;
  likelihood: string;
  impact: string;
  maturity: string;
  evidence: EvidenceItem[];
  evidence_history_summary?: EvidenceHistorySummary[];
  status_options: string[];
  maturity_options?: string[];
  likelihood_options?: string[];
  impact_options?: string[];
  comments?: ControlComment[];
  team_members?: string[];
  scope_context?: {
    kind: string;
    title: string;
    detail: string;
    org_responsibility?: string;
    provider_responsibility?: string;
    citation?: string;
    inheritance_level?: string;
    provider?: string;
  } | null;
  linked_policies?: { id: string; title: string; version?: number }[];
  linked_assets?: { id: string; name?: string; asset_name?: string; type?: string; asset_type?: string; cui?: string }[];
  linked_team?: string[];
  linked_subcontractors?: { id: string; name: string }[];
  linking_profile?: {
    policies: string[];
    assets: { suggested: string[] } | null;
    team: string[];
    subcontractors?: string[];
    evidence_types?: string[];
    risk_types?: string[];
    enriched_policies?: string[];
    enriched_teams?: string[];
    enriched_assets?: string[];
    mandatory?: string[];
    recommended?: string[];
  };
  readiness?: ControlReadiness;
  auto_badge?: AutoBadge | null;
  automation_coverage?: AutomationCoverage | null;
  objectives?: ControlObjective[];
  computed_status?: string;
  override_active?: boolean;
  override_justification?: string;
  fips_certificate_number?: string;
  cloud_authorization_status?: string;
  dfars_72hr_reporting_enabled?: boolean;
};

export type AutoBadge = {
  status: "pass" | "fail" | "error" | "partial" | "uncollected" | "stale";
  last_run_at: string | null;
  check_count: number;
  passing: number;
  failing: number;
  error: number;
  checks: { check_id: string; status: string; collected_at?: string }[];
  error_message: string | null;
};

export type ReadinessItem = {
  id: string;
  label: string;
  done: boolean;
  required: boolean;
  hint: string;
};

export type ControlReadiness = {
  items: ReadinessItem[];
  readiness_pct: number;
  readiness_label: string;
  required_count: number;
  done_count: number;
};

export const INVENTORY_COLUMNS = [
  "asset_name",
  "asset_type",
  "in_scope",
  "cui",
  "owner",
  "location",
  "notes",
] as const;

export type ControlGuidance = {
  control_id: string;
  name: string;
  family: string;
  weight: number;
  plain_summary: string;
  catalog_description: string;
  objectives: string[];
  evidence_hints: string[];
  minimum_proof?: {
    control_id: string;
    evidence_types: { type: string; label: string; connectors: string[]; checks: string[] }[];
    mapped_collector_checks: string[];
  };
  family_prompts: string[];
  starter_narrative: string;
  org_context_used?: boolean;
  stack_pattern?: string | null;
};

export type WizardStep = {
  id: string;
  title: string;
  caption: string;
  fields: string[];
};

export type OrgAssets = {
  topology_filename: string;
  appendix_files: { filename: string; label: string }[];
};

export type SystemScope = {
  system_name: string;
  description: string;
  cui_types: string;
  boundary_diagram: string;
  external_connections: string;
  owner: string;
  last_review: string;
  has_cui: boolean;
  cui_asset_pct: number;
};

export type ExceptionItem = {
  id: string;
  title?: string;
  control_id: string;
  framework?: string;
  status: string;
  risk_level: string;
  description: string;
  compensating_controls: string;
  risk_acceptance: string;
  created_by: string;
  approved_by: string;
  expiry_date: string;
  created_at: string;
  updated_at: string;
  milestones?: MilestoneItem[];
  owner?: string;
  risk_assessment?: { likelihood?: number; impact?: number; score?: number; residual?: string; rationale?: string };
};

export type ExceptionBody = {
  control_id: string;
  title?: string;
  description?: string;
  framework?: string;
  status?: string;
  risk_level?: string;
  compensating_controls?: string;
  risk_acceptance?: string;
  created_by?: string;
  approved_by?: string;
  expiry_date?: string;
};

export type MilestoneItem = {
  id: string;
  description: string;
  target_date: string;
  completion_date: string;
  status: "not_started" | "in_progress" | "completed";
  owner: string;
  created_at: string;
  updated_at: string;
};

export type MilestoneBody = {
  description: string;
  target_date?: string;
  owner?: string;
  status?: string;
  completion_date?: string;
};

export type ScopeCoverageException = {
  type: "undeclared" | "unmanaged" | "non_compliant" | "stale_sync";
  title: string;
  detail: string;
  device_name?: string;
  inventory_name?: string;
  asset_type?: string;
  compliance_state?: string;
  control_ids?: string[];
};

export type ScopeCoverageRecord = {
  kind: "live" | "declared" | "both";
  asset_name: string;
  asset_type: string;
  in_scope: string;
  cui: string;
  status: string;
  compliance_state: string;
  source: string;
};

export type ScopeCoverage = {
  synced_at: string;
  has_inventory: boolean;
  has_sync: boolean;
  reconciled: boolean;
  summary: {
    declared_in_scope: number;
    live_devices: number;
    matched: number;
    exception_count: number;
    exception_counts: Record<string, number>;
  };
  records: ScopeCoverageRecord[];
  exceptions: ScopeCoverageException[];
  control_ids: string[];
};

export type Organization = {
  org_profile: Record<string, string>;
  asset_scope: Record<string, number>;
  asset_types: Record<string, string>;
  env_scope: Record<string, string>;
  env_scope_labels?: { yes_no: Record<string, string>; cloud: Record<string, string> };
  env_scope_fields?: { key: string; label: string; type: "yes_no" | "cloud" }[];
  env_scope_complete?: boolean;
  env_scope_summary?: string;
  inheritance_hints?: InheritanceHint[];
  inheritance_map?: InheritanceMapRow[];
  scoping_suggestions?: ScopingSuggestion[];
  org_inventory: { assets: Record<string, string>[]; updated_at: string };
  org_assets: OrgAssets;
  scoped_controls_count: number;
  scope_confirmed: boolean;
  scope_coverage?: ScopeCoverage;
  audit_log: { timestamp: string; control_id: string; field: string; old_value: string; new_value: string }[];
  needs_wizard: boolean;
  wizard_steps: WizardStep[];
  field_labels: Record<string, string>;
  field_placeholders: Record<string, string>;
  team_members?: string[];
  system_scope?: Record<string, string>;
};

export type InheritanceHint = {
  control_id: string;
  provider: string;
  note: string;
  control_name: string;
  status?: string;
};

export type InheritanceMapRow = {
  control_id: string;
  control_name: string;
  provider: string;
  org_responsibility: string;
  provider_responsibility: string;
  citation: string;
  inheritance_level: string;
};

export type ScopingSuggestion = {
  control_id: string;
  suggestion: string;
  reason: string;
  status?: string;
};

export type Analytics = {
  sprs: {
    final_score: number;
    met: number;
    assessed: number;
    total: number;
    open_gaps: number;
    penalties: Record<string, number>;
    breakdown: Record<string, number>;
    critical_gaps: string[];
    moderate_gaps: string[];
    low_gaps: string[];
  };
  family_progress: { family: string; total: number; met: number; reviewed: number; open_gaps: number; pct: number }[];
  family_readiness_pct: Record<string, number>;
  poam_by_severity: Record<string, number>;
};

export type Remediation = {
  total_cost: number;
  unowned_gaps: number;
  open_items: number;
  critical_count: number;
  readiness_pct: number;
  sprs_score: number;
  gaps_by_family: { family: string; count: number }[];
  schedule: {
    control_id: string;
    severity: string;
    owner: string;
    target_date: string;
    remediation_steps: string;
    status: string;
    overdue: boolean;
    due_soon: boolean;
  }[];
  burndown: { control_id: string; weight: number; target_date: string; cumulative_score: number }[];
  sprs_history: { timestamp: string; score: number }[];
  target_score: number;
};

export type ControlMeta = {
  dependencies: string[];
  dependencies_at_risk: string[];
  sprs_weight_label: string;
  at_risk_points: string | null;
  validation_rules: { type: string; rules: { description: string }[]; file_types: string[] } | null;
  risk_level: string;
};

export type RoleCapabilities = {
  edit_controls: boolean;
  edit_org: boolean;
  export_data: boolean;
  validate_config: boolean;
  view_dashboard: boolean;
  manage_users: boolean;
};

export type FamilyFilterOption = {
  code: string;
  family: string;
  count: number;
  label: string;
};

export type Settings = {
  current_role: string;
  current_user_name: string;
  team_members: string[];
  user_roles: string[];
  permissions: Record<string, boolean>;
  capabilities: RoleCapabilities;
  clients: { id: string; name: string }[];
  active_client_id: string;
  msp_mode: boolean;
  sprs_history: { timestamp: string; score: number; readiness?: number }[];
  app_version?: string;
  auth_enabled?: boolean;
  auth_role_locked?: boolean;
  auth_user_email?: string;
  sandbox_mode?: boolean;
  needs_organization?: boolean;
};

export type MyWorkReport = {
  current_user_name: string;
  team_members: string[];
  assigned_count: number;
  overdue_count: number;
  needs_user_name: boolean;
  controls: {
    id: string;
    family: string;
    name: string;
    status: string;
    owner: string;
    target_date: string;
    overdue: boolean;
    has_narrative: boolean;
    comment_count: number;
  }[];
};

export type Journey = {
  progress_pct: number;
  sprs_score: number;
  open_critical: number;
  next_step: { id: string; label: string; hint: string; view: string } | null;
  steps: { id: string; label: string; hint: string; view: string; done: boolean; optional?: boolean }[];
  metrics: {
    profile_pct: number;
    assessed_pct: number;
    narrative_pct: number;
    report_pct: number;
    evidence_pct: number;
  };
};

export type ActivityEntry = {
  type: "status_change" | "evidence_uploaded" | "comment_added" | "export_created" | "narrative" | "owner" | "field_change";
  control_id: string;
  message: string;
  timestamp: string;
};

export type PriorityControl = {
  id: string;
  name: string;
  family: string;
  status: string;
  weight_tier: string;
  weight_badge: string;
};

export type NextAssessment = {
  next_control_id: string | null;
  next_control_name: string;
  next_control_status?: string;
  priority_controls: string[];
  priority_details?: PriorityControl[];
};

export type EvidenceFamilyRow = {
  family: string;
  code: string;
  scoped: number;
  met: number;
  with_evidence: number;
  without_evidence: number;
  evidence_pct: number | null;
  controls_label: string;
};

export type ReadinessScores = {
  assessment_readiness: number;
  documentation_readiness: number;
  evidence_readiness: number;
  audit_readiness: number;
  export_readiness: number;
  evidence_detail?: {
    met_count: number;
    with_evidence_count: number;
    without_evidence_count?: number;
    evidence_pct: number;
    evidence_files_count?: number;
    families?: EvidenceFamilyRow[];
    weak_families?: Pick<EvidenceFamilyRow, "family" | "code" | "evidence_pct" | "with_evidence" | "met">[];
  };
};

export type ReadinessReviewSummary = {
  review_score: number;
  quality_explanation: string;
  evidence: {
    met_count: number;
    with_evidence_count: number;
    without_evidence_count: number;
  };
  finding_summary: {
    met_no_proof_count: number;
  };
};

export type ExportReadinessReport = {
  score: number;
  profile_score: number;
  narrative_score: number;
  assessment_score: number;
  blockers: string[];
  warnings: string[];
  warning_items: { title: string; detail: string }[];
  missing_narrative_count: number;
  missing_narrative_controls: { id: string; status: string; name: string }[];
  open_gap_count: number;
  export_allowed: boolean;
  sprs_score: number;
  ssp_narratives?: {
    documented_count: number;
    empty_count: number;
    missing_met_narrative_count: number;
    scoped_count: number;
    documented_pct: number;
  };
};

export type SspProgress = {
  documented_count: number;
  scoped_count: number;
  documented_pct: number;
  empty_count: number;
  families: {
    family: string;
    scoped_count: number;
    documented_count: number;
    documented_pct: number;
  }[];
};

export type PreC3paoReadiness = {
  self_ready: boolean;
  sprs_score: number;
  open_critical_count: number;
  evidence_coverage_pct: number;
  assessment_ready_count?: number;
  unanswered_count?: number;
  conditional_sprs?: number;
  sprs_detail?: {
    final_score: number;
    answered_count: number;
    unanswered_count: number;
  };
  poam_eligibility?: {
    eligible: boolean;
    score: number;
    threshold: number;
    eligible_ids: string[];
    blocking_ids: string[];
    unmet_count: number;
    closeout_days: number;
    reason: string;
  };
  checklist: {
    item: string;
    done: boolean;
    detail: string;
    control_ids?: string[];
    blocks_self_ready?: boolean;
    note?: string | null;
  }[];
  remediation_priority: string[];
  blockers: string[];
  objective_coverage: {
    covered_count: number;
    total: number;
    pct: number;
    missing_sample: string[];
  };
};

export type SprsLedgerRow = {
  control_id: string;
  family: string;
  name: string;
  weight: number;
  status: string;
  answered: boolean;
  deduction: number;
  has_evidence: boolean;
  assessment_ready: boolean;
  poam_eligible: boolean;
};

export type ConnectorMonitorState = {
  connector_id: string;
  enabled: boolean;
  interval: "manual" | "daily" | "weekly";
  last_run_at: string | null;
  last_status: "healthy" | "degraded" | "broken" | "never" | "pass" | "fail" | "warn" | "error" | string;
  last_error: string | null;
  attach_on_run: boolean;
  pass_count: number;
  fail_count: number;
  warn_count: number;
  error_count: number;
};

export type WebhookCollectorInfo = {
  id: string;
  name: string;
  source_system: string;
  webhook_token?: string;
  token_hint?: string;
  created_at: string;
  last_ingest_at?: string | null;
  ingest_count: number;
  enabled: boolean;
  ingest_url: string;
};

export type WebhookCollectorsResponse = {
  collectors: WebhookCollectorInfo[];
  env_token_configured: boolean;
  ingest_url: string;
};

export type CollectorInfo = {
  id: string;
  name: string;
  description: string;
  required_fields: string[];
  optional_fields: string[];
  permissions_hint?: string;
  beta?: boolean;
  configured: boolean;
  configured_fields: string[];
  missing_fields: string[];
  monitor?: ConnectorMonitorState | null;
};

export type DriftEvent = {
  id: string;
  connector_id: string;
  check_id: string;
  event_type: string;
  summary: string;
  details: string;
  timestamp: string;
  previous_status?: string | null;
  current_status: string;
};

export type EvidenceFreshness = {
  max_age_days: number;
  stale_check_count: number;
  stale_control_count: number;
  stale_checks: { connector_id: string; check_id: string; collected_at?: string }[];
  stale_controls: { control_id: string; latest_upload?: string }[];
};

export type CollectorsDashboard = {
  connectors: CollectorInfo[];
  monitoring: {
    connectors: ConnectorMonitorState[];
    due_connectors: string[];
    recent_runs: CollectorRunResult[];
  };
  drift_events: DriftEvent[];
  freshness: EvidenceFreshness;
  recent_runs: CollectorRunResult[];
};

export type CollectorCheck = {
  check_id: string;
  check_name: string;
  status: string;
  evidence: string;
  detail: string;
  collected_at: string;
};

export type CollectorRunResult = {
  connector_id: string;
  started_at: string;
  completed_at: string;
  summary: string;
  fixture: boolean;
  checks: CollectorCheck[];
  drift_events?: Record<string, unknown>[];
};

export type CollectorAttachResult = {
  control_id: string;
  filename: string;
  sha256: string;
  check_id: string;
};

export type RunResultInfo = {
  summary: string;
  checks: { check_name: string; status: string; evidence: string; detail: string }[];
  attached: number;
  drift: number;
};

export type SchedulerStatus = {
  alive: boolean;
  last_check_at: string | null;
  last_error: string | null;
  ran_count: number;
  error_count: number;
};

const json = async <T>(url: string, init?: RequestInit): Promise<T> => {
  const headers = await authHeaders(init?.headers);
  if (!headers.has("Content-Type") && init?.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiUrl(url), { ...init, headers });
  if (res.status === 401) {
    localStorage.removeItem("khestra_auth_token");
    window.location.href = window.location.pathname.substring(0, window.location.pathname.indexOf("/app")) || "/";
    throw new Error("Session expired — redirecting to login");
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
};

export const api = {
  dashboard: () => json<Dashboard>("/api/dashboard"),
  settings: () => json<Settings>("/api/settings"),
  createOrganization: (name: string, loadDemo = true, demoId = "apex") =>
    json<{ client_id: string; name: string; active_client_id: string }>("/api/organizations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, load_demo: loadDemo, demo_id: demoId }),
    }),
  patchRole: (role: string) =>
    json<{ current_role: string }>("/api/settings/role", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    }),
  patchUserName: (name: string) =>
    json<{ current_user_name: string }>("/api/settings/user-name", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    }),
  patchMspMode: (msp_mode: boolean) =>
    json<{ msp_mode: boolean }>("/api/settings/msp-mode", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ msp_mode }),
    }),
  createClient: (display_name: string) =>
    json<{ client_id: string }>("/api/clients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name }),
    }),
  activateClient: (clientId: string) =>
    json<{ active_client_id: string }>(`/api/clients/${clientId}/activate`, { method: "POST" }),
  journey: () => json<Journey>("/api/journey"),
  nextControl: () => json<NextAssessment>("/api/assessment/next"),
  assessmentStatus: () => json<CmmcAssessmentStatus>("/api/assessment/status"),
  putAssessmentStatus: (body: {
    assessment_type: string;
    status: string;
    status_date: string;
    affirming_official?: string;
  }) =>
    json<CmmcAssessmentStatus>("/api/assessment/status", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  assessmentCloseout: () =>
    json<CmmcAssessmentStatus>("/api/assessment/closeout", { method: "POST" }),
  assessmentScope: () => json<{ scope: CmmcScope }>("/api/assessment/scope"),
  putAssessmentScope: (body: CmmcScope) =>
    json<{ scope: CmmcScope }>("/api/assessment/scope", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  contracts: () => json<{ contracts: ContractRecord[] }>("/api/contracts"),
  createContract: (body: ContractRecord) =>
    json<{ contract: ContractRecord }>("/api/contracts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  deleteContract: (id: string) =>
    json<{ status: string }>(`/api/contracts/${encodeURIComponent(id)}`, { method: "DELETE" }),
  l1Status: () => json<L1Status>("/api/assessment/l1"),
  putL1Status: (controlId: string, status: string) =>
    json<L1Status>(`/api/assessment/l1/${encodeURIComponent(controlId)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    }),
  putL1Assessment: (body: { status_date: string; affirming_official: string }) =>
    json<L1Status>("/api/assessment/l1", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  l1EntryText: () => json<{ text: string }>("/api/assessment/l1/entry-text"),
  loadDemo: (demoId: string) =>
    json<{ org_name: string; sprs_score: number } & DemoStatus>(`/api/demo/load?demo_id=${demoId}`, { method: "POST" }),
  demoStatus: () => json<DemoStatus>("/api/demo/status"),
  clearDemo: () => json<{ status: string }>("/api/demo/clear", { method: "POST" }),
  renameClient: (clientId: string, name: string) =>
    json<{ client_id: string; name: string }>(`/api/clients/${encodeURIComponent(clientId)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    }),
  deleteClient: (clientId: string) =>
    json<{ deleted: string; active_client_id: string }>(`/api/clients/${encodeURIComponent(clientId)}`, {
      method: "DELETE",
    }),
  controls: (family?: string, q?: string, assignedTo?: "me") => {
    const p = new URLSearchParams();
    if (family) p.set("family", family);
    if (q) p.set("q", q);
    if (assignedTo) p.set("assigned_to", assignedTo);
    const qs = p.toString();
    return json<{
      controls: ControlSummary[];
      families: string[];
      family_options: FamilyFilterOption[];
      status_options: string[];
    }>(`/api/controls${qs ? `?${qs}` : ""}`);
  },
  myWork: () => json<MyWorkReport>("/api/controls/my-work"),
  analytics: () => json<Analytics>("/api/analytics"),
  remediation: () => json<Remediation>("/api/remediation"),
  controlMeta: (id: string) => json<ControlMeta>(`/api/controls/${encodeURIComponent(id)}/meta`),
  validateConfig: async (controlId: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(apiUrl(`/api/controls/${encodeURIComponent(controlId)}/validate-config`), {
      method: "POST",
      body: fd,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ passed: boolean; details: { rule: string; passed: boolean }[] }>;
  },
  control: (id: string) => json<ControlDetail>(`/api/controls/${encodeURIComponent(id)}`),
  proofPackage: async (id: string) => {
    const res = await authFetch(`/api/controls/${encodeURIComponent(id)}/proof-package`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  downloadProofPackage: async (id: string) => {
    const res = await authFetch(`/api/controls/${encodeURIComponent(id)}/proof-package`);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `proof-package-${id.replace(/[^A-Za-z0-9._-]+/g, "_")}.json`;
    a.click();
    URL.revokeObjectURL(url);
    return data;
  },
  postControlComment: (id: string, text: string) =>
    json<{ comments: ControlComment[] }>(`/api/controls/${encodeURIComponent(id)}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    }),
  controlGuidance: (id: string) => json<ControlGuidance>(`/api/controls/${encodeURIComponent(id)}/guidance`),
  generateNarrative: (id: string, useAi = false, force = false, includeCurrentNarrative = false) =>
    json<{ narrative: string; sources: string[]; method: string; collector_count: number; ai_available: boolean; ai_error: string | null; ingested?: string[]; draft_created?: boolean }>(
      `/api/controls/${encodeURIComponent(id)}/generate-narrative`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          use_ai: useAi,
          force,
          include_current_narrative: includeCurrentNarrative,
        }),
      },
    ),
  approveAiDraft: (id: string) =>
    json<{ status: string; ai_generated: boolean }>(
      `/api/controls/${encodeURIComponent(id)}/ai-draft/approve`,
      { method: "POST" },
    ),
  rejectAiDraft: (id: string) =>
    json<{ status: string }>(
      `/api/controls/${encodeURIComponent(id)}/ai-draft/reject`,
      { method: "POST" },
    ),
  generateAllNarratives: (scope: string, useAi = false, force = false) =>
    json<{ scope: string; candidate_count: number; generated: number; skipped: number }>(
      "/api/narratives/generate-all",
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scope, use_ai: useAi, force }) },
    ),
  evidenceSummary: (id: string) =>
    json<{ collector_count: number; examine: string; test: string }>(
      `/api/controls/${encodeURIComponent(id)}/evidence-summary`,
    ),
  applyEvidenceSummary: (id: string, mode: "append" | "replace" = "append") =>
    json<{ examine: string; test: string; collector_count: number; mode: string }>(
      `/api/controls/${encodeURIComponent(id)}/apply-evidence-summary`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      },
    ),
  remediationSummary: (id: string) =>
    json<{ gap_count: number; collector_count: number; remediation_plan: string }>(
      `/api/controls/${encodeURIComponent(id)}/remediation-summary`,
    ),
  applyRemediationSummary: (id: string, mode: "append" | "replace" = "append") =>
    json<{ remediation_plan: string; gap_count: number; collector_count: number; mode: string }>(
      `/api/controls/${encodeURIComponent(id)}/apply-remediation-summary`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      },
    ),
  patchControl: (id: string, body: Partial<ControlDetail>) =>
    json<{ control: ControlSummary; sprs_score: number; export_stale: boolean }>(
      `/api/controls/${encodeURIComponent(id)}`,
      { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
    ),
  uploadEvidence: async (id: string, files: File | File[]) => {
    const list = Array.isArray(files) ? files : [files];
    const fd = new FormData();
    for (const file of list) {
      fd.append("files", file);
    }
    const res = await fetch(apiUrl(`/api/controls/${encodeURIComponent(id)}/evidence`), { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ uploaded: { filename: string; sha256: string }[]; count: number }>;
  },
  verifyEvidence: (controlId: string, filename: string) =>
    json<{ verified: boolean; expected_sha256: string; filename: string }>(
      `/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(filename)}/verify`,
    ),
  deleteEvidence: (controlId: string, filename: string) =>
    json<{ status: string; filename: string }>(
      `/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(filename)}`,
      { method: "DELETE" },
    ),
  evidenceDownloadUrl: (controlId: string, filename: string) =>
    `/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(filename)}`,
  organization: () => json<Organization>("/api/organization"),
  systemScope: () => json<SystemScope>("/api/system-scope"),
  patchSystemScope: (body: Partial<SystemScope>) =>
    json<{ system_scope: Record<string, string> }>("/api/system-scope", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  patchOrgProfile: (org_profile: Record<string, string>) =>
    json<{ org_profile: Record<string, string> }>("/api/org-profile", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ org_profile }),
    }),
  patchInventory: (assets: Record<string, string>[]) =>
    json<{ org_inventory: Organization["org_inventory"] }>("/api/inventory", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assets }),
    }),
  importInventory: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(apiUrl("/api/inventory/import"), { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ imported: number; warnings: string[] }>;
  },
  patchAssetScope: (asset_scope: Record<string, number>) =>
    json<{ scoped_controls_count: number }>("/api/asset-scope", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset_scope }),
    }),
  patchEnvScope: (env_scope: Record<string, string>) =>
    json<{ env_scope: Record<string, string> }>("/api/env-scope", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ env_scope }),
    }),
  uploadTopology: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(apiUrl("/api/org-assets/topology"), { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ topology_filename: string }>;
  },
  deleteTopology: () => json<{ topology_filename: string }>("/api/org-assets/topology", { method: "DELETE" }),
  uploadAppendix: async (file: File, label: string) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(apiUrl(`/api/org-assets/appendix?label=${encodeURIComponent(label)}`), {
      method: "POST",
      body: fd,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  deleteAppendix: (filename: string) =>
    json<{ org_assets: OrgAssets }>(`/api/org-assets/appendix/${encodeURIComponent(filename)}`, {
      method: "DELETE",
    }),
  preC3pao: () => json<PreC3paoReadiness>("/api/readiness/pre-c3pao"),
  sprsLedger: () => json<{ rows: SprsLedgerRow[]; count: number }>("/api/sprs/ledger"),
  sprsSimulate: (changes: { control_id: string; status: string }[]) =>
    json<{ current_score: number; projected_score: number; delta: number; applied_changes: string[] }>(
      "/api/sprs/simulate",
      { method: "POST", body: JSON.stringify({ changes }) },
    ),
  exportReadinessReport: () => json<ExportReadinessReport>("/api/readiness/export-report"),
  sspProgress: () => json<SspProgress>("/api/ssp/progress"),
  sprsEntryText: () => json<{ text: string }>("/api/readiness/sprs-entry-text"),
  help: () => json<{ views: Record<string, { title: string; summary: string; tips: string[] }>; faq: { q: string; a: string }[] }>("/api/help"),
  alerts: () =>
    json<{
      poam_overdue: { control_id: string; message: string }[];
      env_suggestions: { control_id: string; suggestion: string; reason: string }[];
    }>("/api/alerts"),
  recentActivity: () => json<ActivityEntry[]>("/api/recent-activity"),
  sprsDetail: () => json<{ final_score: number; breakdown: Record<string, unknown>; critical_gaps: string[] }>("/api/sprs-detail"),
  readinessReview: () => json<Record<string, unknown>>("/api/readiness/review"),
  evidenceCoverage: () => json<ReadinessScores>("/api/readiness/evidence-coverage"),
  familyObjectives: (family: string) => json<{ prompts: string[] }>(`/api/objectives/family/${encodeURIComponent(family)}`),
  sprsValidation: () => json<{ scenarios: unknown; report: string }>("/api/validation/sprs"),
  sprsPreview: (controlId: string, status: string) =>
    json<{ current_score: number; projected_score: number; delta: string }>(
      `/api/controls/${encodeURIComponent(controlId)}/sprs-preview?status=${encodeURIComponent(status)}`,
    ),
  importPoam: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(apiUrl("/api/import/poam"), { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ applied: string[]; warnings: string[]; count: number }>;
  },
  importWorkspace: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(apiUrl("/api/import/workspace"), { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  resetWorkspace: () => json<{ status: string }>("/api/workspace/reset", { method: "POST" }),
  resetControls: () => json<{ status: string }>("/api/workspace/reset-controls", { method: "POST" }),
  collectors: () => json<CollectorsDashboard>("/api/collectors"),
  collectorHealth: () => json<CollectorHealthSummary>("/api/collectors/health"),
  saveCollectorCredentials: (connectorId: string, credentials: Record<string, string>) =>
    json<CollectorInfo>(`/api/collectors/${encodeURIComponent(connectorId)}/credentials`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ credentials }),
    }),
  aiKeyStatus: () => json<{ has_ai_key: boolean; source: string }>("/api/settings/ai-key"),
  saveAiKey: (apiKey: string) =>
    json<{ has_ai_key: boolean; source: string }>("/api/settings/ai-key", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey }),
    }),
  deleteAiKey: () =>
    json<{ has_ai_key: boolean; source: string }>("/api/settings/ai-key", { method: "DELETE" }),
  patchCollectorSchedule: (
    connectorId: string,
    body: { enabled?: boolean; interval?: string; attach_on_run?: boolean },
  ) =>
    json<ConnectorMonitorState>(`/api/collectors/${encodeURIComponent(connectorId)}/schedule`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  runDueCollectors: (use_fixture_if_unconfigured = false) =>
    json<{ due_count: number; ran_count: number; results: unknown[]; errors: unknown[] }>(
      "/api/collectors/monitoring/run-due",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_fixture_if_unconfigured }),
      },
    ),
  runCollector: (
    connectorId: string,
    body: { use_fixture?: boolean; attach?: boolean; control_ids?: string[] },
  ) =>
    json<{
      run: CollectorRunResult;
      attached: CollectorAttachResult[];
      monitor_run_id?: string;
      drift_events?: DriftEvent[];
    }>(
      `/api/collectors/${encodeURIComponent(connectorId)}/run`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
    ),
  schedulerStatus: () => json<SchedulerStatus>("/api/collectors/monitoring/scheduler-status"),
  webhooks: () => json<WebhookCollectorsResponse>("/api/webhooks"),
  createWebhook: (name: string, source_system: string) =>
    json<{ collector: WebhookCollectorInfo; usage: string }>("/api/webhooks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, source_system }),
    }),
  deleteWebhook: (collectorId: string) =>
    json<{ status: string }>(`/api/webhooks/${encodeURIComponent(collectorId)}`, {
      method: "DELETE",
    }),
  // Exceptions
  listExceptions: () => json<{ exceptions: ExceptionItem[] }>("/api/exceptions"),
  createException: (body: ExceptionBody) =>
    json<{ exception: ExceptionItem }>("/api/exceptions", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateException: (id: string, body: Partial<ExceptionBody>) =>
    json<{ exception: ExceptionItem }>(`/api/exceptions/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deleteException: (id: string) =>
    json<{ status: string }>(`/api/exceptions/${encodeURIComponent(id)}`, { method: "DELETE" }),
  // Milestones
  addMilestone: (eid: string, body: MilestoneBody) =>
    json<{ milestone: MilestoneItem }>(`/api/exceptions/${encodeURIComponent(eid)}/milestones`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateMilestone: (eid: string, mid: string, body: Partial<MilestoneBody>) =>
    json<{ milestone: MilestoneItem }>(
      `/api/exceptions/${encodeURIComponent(eid)}/milestones/${encodeURIComponent(mid)}`,
      { method: "PATCH", body: JSON.stringify(body) },
    ),
  deleteMilestone: (eid: string, mid: string) =>
    json<{ status: string }>(
      `/api/exceptions/${encodeURIComponent(eid)}/milestones/${encodeURIComponent(mid)}`,
      { method: "DELETE" },
    ),
};
