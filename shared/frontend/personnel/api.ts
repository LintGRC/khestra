import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { apiUrl } from "@shared/apiPrefix";
import type { PersonItem } from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const personnelApi = {
  list: (params?: { org_id?: string; framework_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.org_id) qs.set("org_id", params.org_id);
    if (params?.framework_id) qs.set("framework_id", params.framework_id);
    const q = qs.toString();
    return json<{ personnel: PersonItem[] }>(`/api/personnel${q ? `?${q}` : ""}`);
  },

  get: (id: string) =>
    json<{ person: PersonItem }>(`/api/personnel/${encodeURIComponent(id)}`),

  create: (body: Partial<PersonItem>) =>
    json<{ person: PersonItem }>("/api/personnel", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: Partial<PersonItem>) =>
    json<{ person: PersonItem }>(`/api/personnel/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/personnel/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  importFrom: (provider: string) =>
    json<{ ok: boolean; count: number; updated: number; deactivated?: number; error?: string; errors?: string[] }>(
      `/api/personnel/import/${encodeURIComponent(provider)}`,
      { method: "POST" },
    ),

  getProviderConfig: (provider: string) =>
    json<{ ok: boolean; config: Record<string, string | boolean>; schema: { label: string; fields: { key: string; label: string; is_secret: boolean; placeholder?: string }[] } }>(
      `/api/settings/${encodeURIComponent(provider)}`,
    ),

  saveProviderConfig: (provider: string, body: Record<string, string>) =>
    json<{ ok: boolean }>(`/api/settings/${encodeURIComponent(provider)}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  testProviderConfig: (provider: string) =>
    json<{ ok: boolean; error: string | null }>(`/api/settings/${encodeURIComponent(provider)}/test`, {
      method: "POST",
    }),
};
