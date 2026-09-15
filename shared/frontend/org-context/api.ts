import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { apiUrl } from "@shared/apiPrefix";
import type { ContextCreateBody, ContextRecord } from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const orgContextApi = {
  list: () =>
    json<{ records: ContextRecord[]; latest: ContextRecord | null }>("/api/org-context"),

  get: (id: string) =>
    json<{ record: ContextRecord }>(`/api/org-context/${encodeURIComponent(id)}`),

  stats: () =>
    json<{
      total: number;
      climate_relevant: number;
      interested_parties_latest: number;
      latest: ContextRecord | null;
    }>("/api/org-context/stats"),

  create: (body: ContextCreateBody) =>
    json<{ record: ContextRecord }>("/api/org-context", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: ContextCreateBody) =>
    json<{ record: ContextRecord }>(`/api/org-context/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  remove: (id: string) =>
    json<{ ok: boolean }>(`/api/org-context/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),
};
