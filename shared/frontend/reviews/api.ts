import { apiUrl } from "@shared/apiPrefix";
import type { ReviewItem } from "./types";

function json<T>(url: string, init?: RequestInit): Promise<T> {
  return fetch(apiUrl(url), { headers: { "Content-Type": "application/json" }, ...init }).then((r) => {
    if (!r.ok) throw new Error(r.statusText);
    return r.json();
  });
}

export const reviewsApi = {
  list: (params?: { type?: string; status?: string; workspace_id?: string; framework_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.type) qs.set("type", params.type);
    if (params?.status) qs.set("status", params.status);
    if (params?.workspace_id) qs.set("workspace_id", params.workspace_id);
    if (params?.framework_id) qs.set("framework_id", params.framework_id || "");
    return json<{ reviews: ReviewItem[]; total: number }>(`/api/reviews${qs.toString() ? `?${qs}` : ""}`);
  },

  get: (id: string) => json<{ review: ReviewItem }>(`/api/reviews/${encodeURIComponent(id)}`),

  create: (body: Partial<ReviewItem> & { title: string }) =>
    json<{ review: ReviewItem }>("/api/reviews", { method: "POST", body: JSON.stringify(body) }),

  update: (id: string, body: Partial<ReviewItem>) =>
    json<{ review: ReviewItem }>(`/api/reviews/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(body) }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/reviews/${encodeURIComponent(id)}`, { method: "DELETE" }),

  types: () => json<{ types: string[]; frequencies: string[]; statuses: string[] }>("/api/reviews/types"),
};
