export const AI_GOV_FRAMEWORKS = [
  { key: "eu_ai_act", label: "EU AI Act", color: "var(--primary)" },
  { key: "nist_ai_rmf", label: "NIST AI RMF", color: "#2563eb" },
  { key: "iso_42001", label: "ISO 42001", color: "#7c3aed" },
  { key: "owasp_agentic", label: "OWASP Agentic", color: "#ea580c" },
  { key: "owasp_llm", label: "OWASP LLM", color: "#0891b2" },
] as const;

export type AiGovFrameworkKey = (typeof AI_GOV_FRAMEWORKS)[number]["key"];

export const FW_LABELS: Record<string, string> = {
  eu_ai_act: "EU AI Act",
  nist_ai_rmf: "NIST AI RMF",
  iso_42001: "ISO 42001",
  owasp_agentic: "OWASP Agentic",
  owasp_llm: "OWASP LLM",
};

export const FW_COLORS: Record<string, string> = {
  eu_ai_act: "var(--primary)",
  nist_ai_rmf: "#2563eb",
  iso_42001: "#7c3aed",
  owasp_agentic: "#ea580c",
  owasp_llm: "#0891b2",
};
