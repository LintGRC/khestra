import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { apiUrl } from "@shared/apiPrefix";
import type {
  RiskItem,
  RiskCreateBody,
  RiskUpdateBody,
  RiskComment,
} from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

const NUM_TO_LEVEL: Record<number, string> = {
  0: "low",
  1: "low",
  2: "medium",
  3: "high",
  4: "critical",
};

function scoreToLevel(score: number): string {
  if (score >= 12) return "critical";
  if (score >= 9) return "high";
  if (score >= 6) return "medium";
  if (score >= 4) return "low";
  return "low";
}

function normalizeRisk(raw: Record<string, unknown>): RiskItem {
  if (raw.inherent_likelihood) return raw as unknown as RiskItem;
  const lh = raw.likelihood as number | undefined;
  const imp = raw.impact as number | undefined;
  const inherentScore = (raw.inherent_score as number) ?? (lh && imp ? lh * imp : 0);
  const resLh = raw.residual_likelihood as number | undefined;
  const resImp = raw.residual_impact as number | undefined;
  const residualScore = (raw.residual_score as number) ?? (resLh != null && resImp != null ? resLh * resImp : 0);
  const controlIds = (raw.control_ids as string[]) ?? [];
  return {
    id: raw.id as string,
    title: (raw.title as string) ?? "",
    description: (raw.description as string) ?? "",
    category: (raw.category as string) ?? "",
    framework: (raw.framework as string) ?? "",
    control_ids: controlIds,
    system_id: (raw.system_id as string) ?? "",
    owner: (raw.owner as string) ?? "",
    status: (raw.status as string) ?? "identified",
    inherent_likelihood: lh != null ? NUM_TO_LEVEL[lh] ?? "low" : "low",
    inherent_impact: imp != null ? NUM_TO_LEVEL[imp] ?? "low" : "low",
    residual_likelihood: resLh != null ? NUM_TO_LEVEL[resLh] ?? "low" : scoreToLevel(residualScore),
    residual_impact: resImp != null ? NUM_TO_LEVEL[resImp] ?? "low" : scoreToLevel(residualScore),
    treatment: (raw.treatment as string) ?? "",
    controls: (raw.controls as string) ?? (raw.treatment_plan as string) ?? "",
    control_id: (raw.control_id as string) ?? controlIds[0] ?? "",
    inherent_score: inherentScore,
    residual_score: residualScore,
    inherent_level: scoreToLevel(inherentScore),
    residual_level: scoreToLevel(residualScore),
    review_date: (raw.review_date as string) ?? "",
    acceptance_expires: (raw.acceptance_expires as string) ?? "",
    control_owner: (raw.control_owner as string) ?? "",
    acceptance_overdue: (raw.acceptance_overdue as boolean) ?? false,
    acceptance_days_left: (raw.acceptance_days_left as number | null) ?? null,
    created_by: (raw.created_by as string) ?? "",
    created_at: (raw.created_at as string) ?? "",
    updated_at: (raw.updated_at as string) ?? "",
    closed_at: (raw.closed_at as string) ?? "",
  };
}

export const riskApi = {
  list: async (params?: {
    framework?: string;
    category?: string;
    status?: string;
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
    const res = await json<{ risks: Record<string, unknown>[] }>(
      `/api/risks${q ? `?${q}` : ""}`,
    );
    return { risks: (res.risks ?? []).map(normalizeRisk) };
  },

  get: async (id: string) => {
    const res = await json<{ risk: Record<string, unknown> }>(
      `/api/risks/${encodeURIComponent(id)}`,
    );
    return { risk: normalizeRisk(res.risk) };
  },

  create: (body: RiskCreateBody) =>
    json<{ risk: RiskItem }>("/api/risks", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: RiskUpdateBody) =>
    json<{ risk: RiskItem }>(`/api/risks/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  reSign: (id: string, changedBy: string) =>
    json<{ risk: RiskItem }>(`/api/risks/${encodeURIComponent(id)}/re-sign`, {
      method: "POST",
      body: JSON.stringify({ changed_by: changedBy }),
    }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/risks/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  stats: () => json<Record<string, unknown>>("/api/risks/stats"),

  addComment: (id: string, author: string, body: string) =>
    json<{ comment: RiskComment }>(
      `/api/risks/${encodeURIComponent(id)}/comments`,
      {
        method: "POST",
        body: JSON.stringify({ author, body }),
      },
    ),

  listControls: (framework?: string) => {
    const qs = framework ? `?framework=${encodeURIComponent(framework)}` : "";
    return json<{ controls: { id: string; title: string; framework: string; clause: string }[] }>(
      `/api/risk-controls${qs}`,
    );
  },

  uncoveredControls: (framework?: string) => {
    const qs = framework ? `?framework=${encodeURIComponent(framework)}` : "";
    return json<{ controls: { id: string; title: string; framework: string; clause: string }[] }>(
      `/api/risk-controls/uncovered${qs}`,
    );
  },

  listFrameworks: () =>
    json<{ frameworks: string[] }>("/api/risk-frameworks"),
};
