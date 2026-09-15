export type FrameworkId = "cmmc" | "soc2" | "aigovernance" | "iso27001";

export type FrameworkMeta = {
  id: FrameworkId;
  label: string;
  shortLabel: string;
  apiPrefix: string;
  shellClass: string;
  homePath: string;
};

export const FRAMEWORKS: Record<FrameworkId, FrameworkMeta> = {
  cmmc: {
    id: "cmmc",
    label: "CMMC Level 2",
    shortLabel: "CMMC",
    apiPrefix: "/api/cmmc",
    shellClass: "",
    homePath: "/",
  },
  soc2: {
    id: "soc2",
    label: "SOC 2 Type II",
    shortLabel: "SOC 2",
    apiPrefix: "/api/soc2",
    shellClass: "app-shell--soc2",
    homePath: "/",
  },
  aigovernance: {
    id: "aigovernance",
    label: "AI Governance",
    shortLabel: "AI Gov",
    apiPrefix: "/api/ai-governance",
    shellClass: "",
    homePath: "/",
  },
  iso27001: {
    id: "iso27001",
    label: "ISO 27001",
    shortLabel: "ISO 27001",
    apiPrefix: "/api/iso27001",
    shellClass: "",
    homePath: "/",
  },
};

export const FRAMEWORK_ORDER: FrameworkId[] = ["cmmc", "soc2", "aigovernance", "iso27001"];

export function parseFrameworkList(raw: string | undefined): FrameworkId[] {
  if (!raw) return ["cmmc"];
  const ids = raw
    .split(",")
    .map((s) => s.trim())
    .filter(
      (s): s is FrameworkId =>
        s === "cmmc" || s === "soc2" || s === "aigovernance" || s === "iso27001",
    );
  return ids.length ? ids : ["cmmc"];
}
