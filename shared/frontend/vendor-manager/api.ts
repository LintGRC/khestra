import { apiUrl, getApiPrefix } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import type {
  VendorItem,
  VendorAssessment,
  VendorRemediation,
  VendorActivity,
} from "./types";

const FRAMEWORK_MAP: Record<string, string> = {
  "/api/soc2": "SOC2",
  "/api/ai-governance": "AIGov",
  "/api/cmmc": "CMMC",
  "/api/iso27001": "ISO27001",
};

export function detectFrameworkId(): string | undefined {
  const prefix = getApiPrefix();
  return FRAMEWORK_MAP[prefix];
}

const TERMS: Record<string, { singular: string; plural: string; title: string }> = {
  SOC2: { singular: "Vendor", plural: "Vendors", title: "Vendor Management" },
  AIGov: { singular: "Vendor", plural: "Vendors", title: "Vendor Management" },
  CMMC: { singular: "Subcontractor", plural: "Subcontractors", title: "Subcontractor Management" },
  ISO27001: { singular: "Vendor", plural: "Vendors", title: "Vendor Management" },
};

function currentTerms() {
  const fw = detectFrameworkId();
  return TERMS[fw || ""] || TERMS.SOC2;
}

export function vendorTerm(count?: number): string {
  const t = currentTerms();
  return count !== undefined && count !== 1 ? t.plural : t.singular;
}

export function vendorTitle(): string {
  return currentTerms().title;
}

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const vendorApi = {
  list: (params?: { org_id?: string; framework_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.org_id) qs.set("org_id", params.org_id);
    if (params?.framework_id) qs.set("framework_id", params.framework_id);
    const q = qs.toString();
    return json<{ vendors: VendorItem[] }>(
      `/api/vendors${q ? `?${q}` : ""}`,
    );
  },

  get: (id: string) =>
    json<{ vendor: VendorItem }>(
      `/api/vendors/${encodeURIComponent(id)}`,
    ),

  create: (body: Partial<VendorItem>) =>
    json<{ vendor: VendorItem }>("/api/vendors", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  update: (id: string, body: Partial<VendorItem>) =>
    json<{ vendor: VendorItem }>(
      `/api/vendors/${encodeURIComponent(id)}`,
      {
        method: "PATCH",
        body: JSON.stringify(body),
      },
    ),

  delete: (id: string) =>
    json<{ status: string }>(
      `/api/vendors/${encodeURIComponent(id)}`,
      { method: "DELETE" },
    ),

  seed: () =>
    json<{ ok: boolean; count: number }>("/api/vendors/seed", {
      method: "POST",
    }),

  exportCsvUrl: () => apiUrl("/api/vendors/export/csv"),

  linkFramework: (id: string, frameworkId: string) =>
    json<{ vendor: VendorItem }>(
      `/api/vendors/${encodeURIComponent(id)}/frameworks`,
      { method: "POST", body: JSON.stringify({ framework_id: frameworkId }) },
    ),

  unlinkFramework: (id: string, frameworkId: string) =>
    json<{ vendor: VendorItem }>(
      `/api/vendors/${encodeURIComponent(id)}/frameworks/${encodeURIComponent(frameworkId)}`,
      { method: "DELETE" },
    ),

  assessment: (id: string) =>
    json<{ assessment: VendorAssessment | null }>(
      `/api/vendors/${encodeURIComponent(id)}/assessment`,
    ),

  runAssessment: (id: string) =>
    json<{ assessment: VendorAssessment }>(
      `/api/vendors/${encodeURIComponent(id)}/assess`,
      { method: "POST" },
    ),

  remediations: (id: string) =>
    json<{ remediations: VendorRemediation[] }>(
      `/api/vendors/${encodeURIComponent(id)}/remediations`,
    ),

  updateRemediation: (
    vendorId: string,
    remediationId: string,
    body: Partial<VendorRemediation>,
  ) =>
    json<{ remediation: VendorRemediation }>(
      `/api/vendors/${encodeURIComponent(vendorId)}/remediations/${encodeURIComponent(remediationId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(body),
      },
    ),

  activity: (id: string) =>
    json<{ activities: VendorActivity[] }>(
      `/api/vendors/${encodeURIComponent(id)}/activity`,
    ),

  sendQuestionnaire: (id: string) =>
    json<{ status: string; link?: string }>(
      `/api/vendors/${encodeURIComponent(id)}/send-questionnaire`,
      { method: "POST" },
    ),

  remind: (id: string) =>
    json<{ ok: boolean; level: string; count: number }>(
      `/api/vendors/${encodeURIComponent(id)}/remind`,
      { method: "POST" },
    ),

  saveDraft: (vendorId: string, answers: { questionId: string; value: any }[]) =>
    json<{ status: string }>("/api/vendors/response/draft", {
      method: "POST",
      body: JSON.stringify({ vendor_id: vendorId, answers }),
    }),

  createRemediation: (vendorId: string, body: { description: string; owner: string; due_date: string; assessment_id: string }) =>
    json<{ remediation: VendorRemediation }>(
      `/api/vendors/${encodeURIComponent(vendorId)}/remediations`,
      { method: "POST", body: JSON.stringify(body) },
    ),

  uploadCert: async (vendorId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const headers = await authHeaders({});
    delete (headers as any)["Content-Type"];
    return fetchJson<{ vendor: VendorItem }>(
      apiUrl(`/api/vendors/${encodeURIComponent(vendorId)}/cert`),
      { method: "POST", headers, body: formData },
    );
  },
};
