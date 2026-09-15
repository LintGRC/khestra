import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { Incident, Playbook } from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({ "Content-Type": "application/json", ...(init?.headers || {}) });
  const res = await fetch(apiUrl(path), { ...init, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const api = {
  list: (params?: { status?: string; severity?: string; failure_mode?: string; control_id?: string; q?: string; limit?: number; offset?: number; overdue?: boolean; sort_by?: string; sort_order?: string }) => {
    const p = new URLSearchParams();
    if (params?.status) p.set("status", params.status);
    if (params?.severity) p.set("severity", params.severity);
    if (params?.failure_mode) p.set("failure_mode", params.failure_mode);
    if (params?.control_id) p.set("control_id", params.control_id);
    if (params?.q) p.set("q", params.q);
    if (params?.limit) p.set("limit", String(params.limit));
    if (params?.offset) p.set("offset", String(params.offset));
    if (params?.overdue) p.set("overdue", "true");
    if (params?.sort_by) p.set("sort_by", params.sort_by);
    if (params?.sort_order) p.set("sort_order", params.sort_order);
    const qs = p.toString();
    return json<{ incidents: Incident[]; total: number }>(`/api/incidents${qs ? `?${qs}` : ""}`);
  },

  get: (iid: string) => json<{ incident: Incident }>(`/api/incidents/${encodeURIComponent(iid)}`),

  create: (data: Partial<Incident> & { title: string }) =>
    json<{ incident: Incident }>("/api/incidents", { method: "POST", body: JSON.stringify(data) }),

  update: (iid: string, data: Partial<Incident>) =>
    json<{ incident: Incident }>(`/api/incidents/${encodeURIComponent(iid)}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (iid: string) =>
    json<{ ok: boolean }>(`/api/incidents/${encodeURIComponent(iid)}`, { method: "DELETE" }),

  bulk: (ids: string[], action: string, value?: string) =>
    json<{ incidents: Incident[]; count: number }>("/api/incidents/bulk", {
      method: "POST",
      body: JSON.stringify({ ids, action, value }),
    }),

  transition: (iid: string, status: string, detail?: string, rca?: Record<string, unknown>) =>
    json<{ incident: Incident }>(`/api/incidents/${encodeURIComponent(iid)}/transition`, {
      method: "POST",
      body: JSON.stringify({ status, detail, rca }),
    }),

  notifyRegulator: (iid: string) =>
    json<{ incident: Incident }>(`/api/incidents/${encodeURIComponent(iid)}/notify-regulator`, { method: "POST" }),

  autoClassify: (iid: string) =>
    json<{ incident: Incident }>(`/api/incidents/${encodeURIComponent(iid)}/auto-classify`, { method: "POST" }),

  uploadEvidence: async (iid: string, file: File, label?: string) => {
    const fd = new FormData();
    fd.append("file", file);
    if (label) fd.append("label", label);
    const headers = await authHeaders();
    const res = await fetch(apiUrl(`/api/incidents/${encodeURIComponent(iid)}/evidence`), { method: "POST", headers, body: fd });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ evidence: import("./types").EvidenceItem }>;
  },

  deleteEvidence: (iid: string, eid: string) =>
    json<{ ok: boolean }>(`/api/incidents/${encodeURIComponent(iid)}/evidence/${encodeURIComponent(eid)}`, { method: "DELETE" }),

  addCorrectiveAction: (iid: string, data: { description: string; assigned_to?: string; due_date?: string }) =>
    json<{ corrective_action: import("./types").CorrectiveAction }>(
      `/api/incidents/${encodeURIComponent(iid)}/corrective-actions`,
      { method: "POST", body: JSON.stringify(data) },
    ),

  updateCorrectiveAction: (iid: string, caid: string, data: { status?: string; description?: string; assigned_to?: string }) =>
    json<{ corrective_action: import("./types").CorrectiveAction }>(
      `/api/incidents/${encodeURIComponent(iid)}/corrective-actions/${encodeURIComponent(caid)}`,
      { method: "PATCH", body: JSON.stringify(data) },
    ),

  saveTelemetry: (iid: string, telemetry: Record<string, unknown>) =>
    json<{ incident: Incident }>(`/api/incidents/${encodeURIComponent(iid)}/telemetry`, {
      method: "POST",
      body: JSON.stringify(telemetry),
    }),

  createRegulatoryReport: (iid: string, data: { report_type: string; submitted_to?: string; content?: string }) =>
    json<{ report: import("./types").RegulatoryReport }>(
      `/api/incidents/${encodeURIComponent(iid)}/regulatory-reports`,
      { method: "POST", body: JSON.stringify(data) },
    ),

  playbooks: () => json<{ playbooks: Record<string, Playbook> }>("/api/playbooks"),
  playbook: (mode: string) => json<{ playbook: Playbook }>(`/api/playbooks/${encodeURIComponent(mode)}`),
  stats: () => json<{ total: number; open: number; overdue_regulatory: number; by_status: Record<string, number>; by_severity: Record<string, number>; by_failure_mode: Record<string, number> }>("/api/incidents/stats"),
  seed: () => json<{ incidents: Incident[]; count: number }>("/api/incidents/seed", { method: "POST" }),

  exportUrl: (iid: string) => apiUrl(`/api/incidents/${encodeURIComponent(iid)}/export`),
  exportCsvUrl: () => apiUrl("/api/incidents/export/csv"),
  regulatorPackUrl: (iid: string) => apiUrl(`/api/incidents/${encodeURIComponent(iid)}/export/regulator-pack`),
};
