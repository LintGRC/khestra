import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { LIVE_FRAMEWORKS } from "./types";
import type {
  PolicyItem,
  AttestationItem,
  TemplateItem,
  PolicyMapping,
} from "./types";

const DISPLAYABLE_MAPPING_KEYS = new Set<string>([
  ...LIVE_FRAMEWORKS.map((f) => f.id),
  "aigov",
  "aigovernance",
  "ai_governance",
]);

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

function normalizePolicy(raw: Record<string, unknown>): PolicyItem {
  if (raw.name) return raw as unknown as PolicyItem;
  const mc = raw.mapped_controls as Record<string, string[]> | undefined;
  const flatControls: string[] = [];
  if (mc) {
    for (const [key, val] of Object.entries(mc)) {
      if (DISPLAYABLE_MAPPING_KEYS.has(key) && Array.isArray(val)) flatControls.push(...val);
    }
  }
  return {
    id: raw.id as string,
    name: (raw.title as string) ?? "",
    version: String((raw.version as number | string) ?? "1.0"),
    description: (raw.description as string) ?? "",
    content: (raw.content as string) ?? "",
    status: (raw.status as string) ?? undefined,
    filename: (raw.filename as string) ?? "",
    file_uploaded: !!(raw.file_uploaded as boolean),
    mapped_controls: Array.isArray(raw.mapped_controls)
      ? (raw.mapped_controls as string[])
      : flatControls,
    created_at: (raw.created_at as string) ?? "",
    updated_at: (raw.updated_at as string) ?? "",
  };
}

export const policyApi = {
  list: async (frameworkTag?: string) => {
    const qs = frameworkTag ? `?framework_tag=${encodeURIComponent(frameworkTag)}` : "";
    const res = await json<{ policies: Record<string, unknown>[] }>(
      `/api/policies${qs}`,
    );
    return { policies: (res.policies ?? []).map(normalizePolicy) };
  },

  get: async (id: string) => {
    const res = await json<{ policy: Record<string, unknown> }>(
      `/api/policies/${encodeURIComponent(id)}`,
    );
    return { policy: normalizePolicy(res.policy) };
  },

  create: (body: {
    name: string;
    version?: string;
    description?: string;
    content?: string;
    filename?: string;
    mapped_controls?: string[];
    framework_tags?: string[];
  }) =>
    json<{ policy: PolicyItem }>("/api/policies", {
      method: "POST",
      body: JSON.stringify({
        name: body.name,
        description: body.description,
        content: body.content || "",
        mapped_controls_list: body.mapped_controls ?? [],
        framework_tags: body.framework_tags ?? [],
      }),
    }),

  update: (
    id: string,
    body: {
      name?: string;
      version?: string;
      description?: string;
      content?: string;
      filename?: string;
      file_uploaded?: boolean;
      mapped_controls?: string[];
    },
  ) =>
    json<{ policy: PolicyItem }>(`/api/policies/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify({
        ...(body.name ? { name: body.name } : {}),
        ...(body.description ? { description: body.description } : {}),
        ...(body.content !== undefined ? { content: body.content } : {}),
        ...(body.mapped_controls
          ? { mapped_controls_list: body.mapped_controls }
          : {}),
      }),
    }),

  delete: (id: string) =>
    json<{ status: string }>(`/api/policies/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  generate: (id: string, template: string) =>
    json<{ policy: PolicyItem; tiptap_json?: Record<string, unknown> }>(
      `/api/policies/${encodeURIComponent(id)}/generate`,
      {
        method: "POST",
        body: JSON.stringify({ template }),
      },
    ),

  exportUrl: (id: string) =>
    apiUrl(`/api/policies/${encodeURIComponent(id)}/export`),

  templates: () =>
    json<{ templates: TemplateItem[] }>("/api/policies/templates"),

  attestations: (policyId?: string) => {
    const qs = policyId
      ? `?policy_id=${encodeURIComponent(policyId)}`
      : "";
    return json<{ attestations: AttestationItem[] }>(
      `/api/policies/attestations${qs}`,
    );
  },

  attest: (body: { policy_id: string; user_name: string }) =>
    json<{ attestation: AttestationItem }>(
      `/api/policies/${encodeURIComponent(body.policy_id)}/attest`,
      {
        method: "POST",
        body: JSON.stringify({ user_name: body.user_name }),
      },
    ),

  // ─── Cross-Framework Mappings ────────────────────────

  listMappings: (policyId: string) =>
    json<{ mappings: PolicyMapping[] }>(
      `/api/policies/${encodeURIComponent(policyId)}/mappings`,
    ),

  createMapping: (
    policyId: string,
    body: { framework: string; control_id: string; control_label?: string },
  ) =>
    json<{ mapping: PolicyMapping }>(
      `/api/policies/${encodeURIComponent(policyId)}/mappings`,
      {
        method: "POST",
        body: JSON.stringify({
          framework: body.framework,
          control_id: body.control_id,
          control_label: body.control_label ?? "",
        }),
      },
    ),

  deleteMapping: (policyId: string, mappingId: string) =>
    json<{ status: string }>(
      `/api/policies/${encodeURIComponent(policyId)}/mappings/${encodeURIComponent(mappingId)}`,
      { method: "DELETE" },
    ),
};
