import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { apiUrl } from "@shared/apiPrefix";
import type { ManagementReview, ReviewCreateBody } from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const managementReviewApi = {
  list: (status?: string) => {
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";
    return json<{ records: ManagementReview[] }>(`/api/management-reviews${qs}`);
  },

  get: (id: string) =>
    json<{ record: ManagementReview }>(`/api/management-reviews/${encodeURIComponent(id)}`),

  stats: () =>
    json<{
      total: number;
      by_status: Record<string, number>;
      open_actions_latest: number;
    }>("/api/management-reviews/stats"),

  inputs: () =>
    json<{ inputs: { key: string; label: string }[]; output_categories: string[] }>(
      "/api/management-reviews/inputs",
    ),

  create: (body: ReviewCreateBody) =>
    json<{ record: ManagementReview }>("/api/management-reviews", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: ReviewCreateBody) =>
    json<{ record: ManagementReview }>(`/api/management-reviews/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  remove: (id: string) =>
    json<{ ok: boolean }>(`/api/management-reviews/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),
};
