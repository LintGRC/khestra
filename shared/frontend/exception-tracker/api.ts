import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import type {
  ExceptionItem,
  ExceptionCreateBody,
  ExceptionUpdateBody,
  Stats,
  Reminder,
  Comment,
  Milestone,
} from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({ "Content-Type": "application/json", ...(init?.headers || {}) });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

async function jsonNoContentType<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({ ...(init?.headers || {}) });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const exceptionApi = {
  list: (params?: {
    org_id?: string;
    workspace_id?: string;
    framework?: string;
    control_id?: string;
    status?: string;
    owner?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v) qs.set(k, v);
      });
    }
    const q = qs.toString();
    return json<{ exceptions: ExceptionItem[] }>(`/api/exceptions${q ? `?${q}` : ""}`);
  },

  get: (id: string) => json<{ exception: ExceptionItem }>(`/api/exceptions/${encodeURIComponent(id)}`),

  create: (body: ExceptionCreateBody) =>
    json<{ exception: ExceptionItem }>("/api/exceptions", { method: "POST", body: JSON.stringify(body) }),

  update: (id: string, body: ExceptionUpdateBody) =>
    json<{ exception: ExceptionItem }>(`/api/exceptions/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/exceptions/${encodeURIComponent(id)}`, { method: "DELETE" }),

  stats: () => json<Stats>("/api/exceptions/stats"),

  reminders: () => json<{ expired: Reminder[]; urgent: Reminder[]; upcoming: Reminder[] }>("/api/exceptions/reminders"),

  getReminder: (id: string) =>
    json<{ message: string; days_left: number; is_expired: boolean }>(
      `/api/exceptions/${encodeURIComponent(id)}/reminder`,
    ),

  addComment: (id: string, author: string, body: string) =>
    json<{ comment: Comment }>(`/api/exceptions/${encodeURIComponent(id)}/comments`, {
      method: "POST",
      body: JSON.stringify({ author, body }),
    }),

  addMilestone: (id: string, description: string, target_date: string, owner: string) =>
    json<{ milestone: Milestone }>(`/api/exceptions/${encodeURIComponent(id)}/milestones`, {
      method: "POST",
      body: JSON.stringify({ description, target_date, owner }),
    }),

  updateMilestone: (
    excId: string,
    milestoneId: string,
    body: { description?: string; target_date?: string; status?: string; owner?: string; evidence?: string },
  ) =>
    json<{ milestone: Milestone }>(
      `/api/exceptions/${encodeURIComponent(excId)}/milestones/${encodeURIComponent(milestoneId)}`,
      { method: "PATCH", body: JSON.stringify(body) },
    ),

  deleteMilestone: (excId: string, milestoneId: string) =>
    json<{ status: string }>(
      `/api/exceptions/${encodeURIComponent(excId)}/milestones/${encodeURIComponent(milestoneId)}`,
      { method: "DELETE" },
    ),

  extend: (id: string, expiry_days: number, approval_notes: string, changed_by: string) =>
    json<ExceptionItem>(`/api/exceptions/${encodeURIComponent(id)}/extend`, {
      method: "POST",
      body: JSON.stringify({ expiry_days, approval_notes, changed_by }),
    }),

  review: (id: string, outcome: string, notes: string, changed_by: string) =>
    json<{ exception: ExceptionItem; outcome: string }>(`/api/exceptions/${encodeURIComponent(id)}/review`, {
      method: "POST",
      body: JSON.stringify({ outcome, notes, changed_by }),
    }),

  approve: (id: string, notes: string) =>
    json<{ exception: ExceptionItem; outcome: string }>(`/api/exceptions/${encodeURIComponent(id)}/approve`, {
      method: "POST",
      body: JSON.stringify({ notes, changed_by: "" }),
    }),

  reject: (id: string, notes: string) =>
    json<{ exception: ExceptionItem; outcome: string }>(`/api/exceptions/${encodeURIComponent(id)}/reject`, {
      method: "POST",
      body: JSON.stringify({ notes, changed_by: "" }),
    }),

  uploadAttachment: async (id: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    const headers = await authHeaders();
    const res = await fetch(apiUrl(`/api/exceptions/${encodeURIComponent(id)}/attachments`), {
      method: "POST",
      headers,
      body: form,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<{ attachment: { id: string; filename: string } }>;
  },

  getAttachmentUrl: (excId: string, fileId: string) =>
    apiUrl(`/api/exceptions/${encodeURIComponent(excId)}/attachments/${encodeURIComponent(fileId)}`),

  deleteAttachment: (excId: string, fileId: string) =>
    jsonNoContentType<{ status: string }>(
      `/api/exceptions/${encodeURIComponent(excId)}/attachments/${encodeURIComponent(fileId)}`,
      { method: "DELETE" },
    ),

  downloadCsv: () => {
    window.open(apiUrl("/api/exceptions/export.csv"), "_blank");
  },

  downloadPortfolioPdf: () => {
    window.open(apiUrl("/api/exceptions/portfolio.pdf"), "_blank");
  },

  downloadApprovalMemo: (id: string) => {
    window.open(apiUrl(`/api/exceptions/${encodeURIComponent(id)}/approval-memo`), "_blank");
  },

  downloadAuditorReport: (id: string) => {
    window.open(apiUrl(`/api/exceptions/${encodeURIComponent(id)}/auditor-report`), "_blank");
  },

  getLifecycle: (id: string) =>
    json<{ extension_log: unknown[]; history: unknown[] }>(
      `/api/exceptions/${encodeURIComponent(id)}/lifecycle`,
    ),

  getTransitions: (id: string) =>
    json<{ transitions: string[] }>(`/api/exceptions/${encodeURIComponent(id)}/transitions`),

  seed: () => json<{ ok: boolean; count: number }>("/api/exceptions/seed", { method: "POST" }),

  frameworks: () => json<{ frameworks: string[] }>("/api/frameworks"),
};
