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
    throw new Error("Session expired");
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

export type SoaRow = {
  control_id: string;
  section: string;
  title: string;
  summary: string;
  status: string;
  applicable: boolean;
  justification: string;
  doc_link: string;
  updated_at: string;
  attributes?: Record<string, string[]>;
  linked_risks?: Array<{
    id: string;
    title: string;
    status: string;
    treatment: string;
    inherent_score: number;
  }>;
};

export type SoaRollup = {
  counts: Record<string, number>;
  total: number;
  applicable_total: number;
  excluded: number;
  by_section: Record<string, { total: number; implemented: number }>;
};

export type SoaResponse = {
  rows: SoaRow[];
  rollup: SoaRollup;
};

export type DashboardData = {
  org_name: string;
  readiness_pct: number;
  implementation_pct: number;
  rollup: SoaRollup;
  tests_total: number;
  evidence_total: number;
  evidence_linked: number;
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
};

export type EvidenceGuidance = {
  evidence_type: string;
  items: string[];
  collectors: string[];
  tests: string[];
  modules: string[];
};

export type ControlEvidenceItem = {
  id: string;
  name: string;
  filename: string;
  review_status: string;
  auto_status?: string;
  uploaded_by: string;
  uploaded_at: string;
  period_covered?: string;
  display_title?: string;
};

export type Sufficiency = {
  score: number;
  level: string;
  count: number;
  breakdown: Record<string, unknown>;
};

export type ConnectorInfo = {
  id: string;
  name: string;
  description: string;
  required_fields: string[];
  optional_fields: string[];
  permissions_hint: string;
  beta?: boolean;
  configured: boolean;
  configured_fields: string[];
  missing_fields: string[];
  monitor: {
    connector_id: string;
    enabled: boolean;
    interval: string;
    last_run_at: string | null;
    last_status: string;
    last_error: string | null;
    check_count: number;
    pass_count: number;
    fail_count: number;
    warn_count: number;
    error_count: number;
    attach_on_run: boolean;
  } | null;
};

export type CollectorDashboard = {
  connectors: ConnectorInfo[];
  monitoring: {
    connectors: ConnectorInfo["monitor"][];
    due_connectors: string[];
    recent_runs: { connector_id: string; started_at: string; completed_at: string; status: string; summary: string; fixture: boolean }[];
  };
  drift_events: { connector_id: string; check_id: string; event_type: string; summary: string; timestamp: string }[];
  recent_runs: CollectorDashboard["monitoring"]["recent_runs"];
};

export type CollectorRunResult = {
  run: { monitor_run_id: string; summary: string };
  attached: { control_id: string; filename: string }[];
  monitor_run_id?: string;
  drift_events: { connector_id: string; check_id: string; event_type: string; summary: string; timestamp: string }[];
};

export const api = {
  async soa(): Promise<SoaResponse> {
    const res = await authFetch("/api/soa");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async getSoa(control_id: string): Promise<SoaRow> {
    const res = await authFetch(`/api/soa/${encodeURIComponent(control_id)}`);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return data.control;
  },
  async updateSoa(control_id: string, fields: Record<string, unknown>): Promise<SoaRow> {
    const res = await authFetch(`/api/soa/${encodeURIComponent(control_id)}`, {
      method: "PATCH",
      body: JSON.stringify(fields),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return data.control;
  },
  async evidenceGuidance(control_id: string): Promise<EvidenceGuidance> {
    const res = await authFetch(`/api/soa/evidence-guidance/${encodeURIComponent(control_id)}`);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return data.guidance;
  },
  async controlEvidence(control_id: string): Promise<ControlEvidenceItem[]> {
    const res = await authFetch(
      `/api/evidence-hub?framework_id=${encodeURIComponent("ISO 27001")}&control_id=${encodeURIComponent(control_id)}`,
    );
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return data.evidence ?? [];
  },
  async controlSufficiency(control_id: string): Promise<Sufficiency | null> {
    const res = await authFetch(
      `/api/evidence-hub/sufficiency?framework_id=${encodeURIComponent("ISO 27001")}&control_id=${encodeURIComponent(control_id)}`,
    );
    if (!res.ok) return null;
    return res.json();
  },
  async findingsForControl(control_id: string): Promise<Array<{ id: string; title: string; severity: string; status: string }>> {
    const res = await authFetch(`/api/findings?control_id=${encodeURIComponent(control_id)}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.findings ?? data.items ?? [];
  },
  async collectors(): Promise<CollectorDashboard> {
    const res = await authFetch("/api/collectors");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async saveCollectorCredentials(connectorId: string, credentials: Record<string, string>) {
    const res = await authFetch(`/api/collectors/${encodeURIComponent(connectorId)}/credentials`, {
      method: "PUT",
      body: JSON.stringify({ credentials }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async deleteCollectorCredentials(connectorId: string) {
    const res = await authFetch(`/api/collectors/${encodeURIComponent(connectorId)}/credentials`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async patchCollectorSchedule(
    connectorId: string,
    patch: { enabled?: boolean; interval?: string; attach_on_run?: boolean },
  ) {
    const res = await authFetch(`/api/collectors/${encodeURIComponent(connectorId)}/schedule`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async runCollector(connectorId: string, body: { use_fixture: boolean; attach: boolean }): Promise<CollectorRunResult> {
    const res = await authFetch(`/api/collectors/${encodeURIComponent(connectorId)}/run`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async runDueCollectors(useFixtureIfUnconfigured: boolean) {
    const res = await authFetch("/api/collectors/monitoring/run-due", {
      method: "POST",
      body: JSON.stringify({ use_fixture_if_unconfigured: useFixtureIfUnconfigured }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async dashboard(): Promise<DashboardData> {
    const res = await authFetch("/api/dashboard");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async getNotifications(): Promise<NotificationsResponse> {
    const res = await authFetch("/api/notifications");
    if (!res.ok) return { notifications: [], unread_count: 0 };
    return res.json();
  },
  async markNotificationRead(id: string) {
    await authFetch(`/api/notifications/${encodeURIComponent(id)}/read`, { method: "PATCH" });
  },
  async markAllNotificationsRead() {
    await authFetch("/api/notifications/read-all", { method: "PATCH" });
  },
  async settings(): Promise<Settings> {
    const res = await authFetch("/api/settings");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
};