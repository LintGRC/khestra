import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import type {
  FindingItem,
  FindingCreateBody,
  FindingUpdateBody,
  CorrectiveAction,
} from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const findingApi = {
  list: (params?: {
    source?: string;
    severity?: string;
    status?: string;
    framework?: string;
    owner?: string;
    control_id?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v) qs.set(k, v);
      });
    }
    const q = qs.toString();
    return json<{ findings: FindingItem[] }>(
      `/api/findings${q ? `?${q}` : ""}`,
    );
  },

  get: (id: string) =>
    json<{ finding: FindingItem }>(
      `/api/findings/${encodeURIComponent(id)}`,
    ),

  create: (body: FindingCreateBody) =>
    json<{ finding: FindingItem }>("/api/findings", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: FindingUpdateBody) =>
    json<{ finding: FindingItem }>(
      `/api/findings/${encodeURIComponent(id)}`,
      {
        method: "PATCH",
        body: JSON.stringify(body),
      },
    ),

  delete: (id: string) =>
    json<{ status: string }>(
      `/api/findings/${encodeURIComponent(id)}`,
      { method: "DELETE" },
    ),

  stats: () =>
    json<{
      by_severity: Record<string, number>;
      by_status: Record<string, number>;
      by_framework: Record<string, number>;
      by_source: Record<string, number>;
    }>("/api/findings/stats"),

  listActions: (findingId: string) =>
    json<{ actions: CorrectiveAction[] }>(
      `/api/findings/${encodeURIComponent(findingId)}/actions`,
    ),

  createAction: (findingId: string, body: Partial<CorrectiveAction>) =>
    json<{ action: CorrectiveAction }>(
      `/api/findings/${encodeURIComponent(findingId)}/actions`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),

  updateAction: (
    findingId: string,
    actionId: string,
    body: Partial<CorrectiveAction>,
  ) =>
    json<{ action: CorrectiveAction }>(
      `/api/findings/${encodeURIComponent(findingId)}/actions/${encodeURIComponent(actionId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(body),
      },
    ),

  deleteAction: (findingId: string, actionId: string) =>
    json<{ status: string }>(
      `/api/findings/${encodeURIComponent(findingId)}/actions/${encodeURIComponent(actionId)}`,
      { method: "DELETE" },
    ),
};
