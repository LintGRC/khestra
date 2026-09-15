import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { apiUrl } from "@shared/apiPrefix";
import type { Audit, AuditCreate, AuditUpdate, EvidenceRequest, RequestCreate, RequestUpdate, AuditStats } from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const auditApi = {
  list: (params?: { framework?: string; audit_type?: string; status?: string; auditor_name?: string; control_id?: string }) => {
    const qs = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => { if (v) qs.set(k, v); });
    }
    const q = qs.toString();
    return json<{ audits: Audit[] }>(`/api/audit-center/audits${q ? `?${q}` : ""}`);
  },

  get: (id: string) =>
    json<{ audit: Audit }>(`/api/audit-center/audits/${encodeURIComponent(id)}`),

  create: (body: AuditCreate) =>
    json<{ audit: Audit }>("/api/audit-center/audits", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: AuditUpdate) =>
    json<{ audit: Audit }>(`/api/audit-center/audits/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/audit-center/audits/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  freeze: (id: string) =>
    json<{ audit: Audit }>(`/api/audit-center/audits/${encodeURIComponent(id)}/freeze`, {
      method: "POST",
    }),

  stats: () =>
    json<AuditStats>("/api/audit-center/stats"),

  listRequests: (auditId: string) =>
    json<{ requests: EvidenceRequest[] }>(`/api/audit-center/audits/${encodeURIComponent(auditId)}/requests`),

  createRequest: (auditId: string, body: RequestCreate) =>
    json<{ request: EvidenceRequest }>(`/api/audit-center/audits/${encodeURIComponent(auditId)}/requests`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateRequest: (auditId: string, requestId: string, body: RequestUpdate) =>
    json<{ request: EvidenceRequest }>(
      `/api/audit-center/audits/${encodeURIComponent(auditId)}/requests/${encodeURIComponent(requestId)}`,
      { method: "PATCH", body: JSON.stringify(body) },
    ),

  deleteRequest: (auditId: string, requestId: string) =>
    json<{ status: string }>(
      `/api/audit-center/audits/${encodeURIComponent(auditId)}/requests/${encodeURIComponent(requestId)}`,
      { method: "DELETE" },
    ),
};
