import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import type { AssetItem } from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const assetsApi = {
  list: () => json<{ assets: AssetItem[] }>("/api/assets"),

  get: (id: string) => json<{ asset: AssetItem }>(`/api/assets/${encodeURIComponent(id)}`),

  create: (body: Partial<AssetItem>) =>
    json<{ asset: AssetItem }>("/api/assets", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: Partial<AssetItem>) =>
    json<{ asset: AssetItem }>(`/api/assets/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/assets/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  importCsv: async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const headers = await authHeaders({});
    delete (headers as any)["Content-Type"];
    const res = await fetch(apiUrl("/api/assets/import/csv"), { method: "POST", headers, body: fd });
    return res.json() as Promise<{ imported: number }>;
  },

  exportCsvUrl: () => apiUrl("/api/assets/export/csv"),
};
