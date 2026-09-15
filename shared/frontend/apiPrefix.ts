const FRAMEWORK_PREFIXES: Record<string, string> = {
  cmmc: "/api/cmmc",
  soc2: "/api/soc2",
  aigovernance: "/api/ai-governance",
  iso27001: "/api/iso27001",
};

function frameworkFromPath(): string | null {
  if (typeof window === "undefined") return null;
  const match = location.pathname.match(/^\/(cmmc|soc2|aigov|iso27001)(?:\/|$)/);
  if (!match) return null;
  const raw = match[1];
  return raw === "aigov" ? "aigovernance" : raw;
}

export function getApiPrefix(): string {
  if (typeof window === "undefined") return "";
  const fw = frameworkFromPath();
  return fw ? (FRAMEWORK_PREFIXES[fw] ?? "") : "";
}

/** Shared-entity API prefixes owned by the Global (core) service — every
 *  framework shell routes these to `/api/core/*` so each shared router is
 *  mounted exactly once (see apps/core/server/main.py). */
const SHARED_PREFIXES = [
  "/api/policies",
  "/api/risks",
  "/api/assets",
  "/api/vendors",
  "/api/incidents",
  "/api/personnel",
  "/api/evidence-hub",
  "/api/collectors",
  "/api/trust-center",
  "/api/compliance-calendar",
  "/api/control-tests",
  "/api/effectiveness",
  "/api/remediation",
  "/api/ccf",
  "/api/findings",
  "/api/audit-center",
  "/api/training",
  "/api/notifications",
  "/api/org-context",
  "/api/management-reviews",
  "/api/exceptions",
  "/api/orgs",
  "/api/raci",
  "/api/reviews",
];

export function apiUrl(path: string): string {
  if (!path.startsWith("/api")) return path;
  if (SHARED_PREFIXES.some((prefix) => path.startsWith(prefix))) {
    return `/api/core${path.slice(4)}`;
  }
  const prefix = getApiPrefix();
  if (!prefix) {
    // Global pages (no framework in the URL) hit the Global service — the
    // neutral home of shared entities (policies, risks, assets, ...).
    return `/api/core${path.slice(4)}`;
  }
  const rest = path.slice(4);
  return `${prefix}${rest}`;
}

export type FrameworkId = "cmmc" | "soc2" | "aigovernance" | "iso27001";

const FRAMEWORK_IDS: FrameworkId[] = ["cmmc", "soc2", "aigovernance", "iso27001"];

const FRAMEWORK_BASES: Record<FrameworkId, string> = {
  cmmc: "/cmmc",
  soc2: "/soc2",
  aigovernance: "/aigov",
  iso27001: "/iso27001",
};

const LAST_FRAMEWORK_KEY = "khestra.lastFramework";

/** Shared entities surfaced as global overview cards with detail/create
 *  views living inside framework shells. iso27001 only has bare list routes
 *  for some of them, so it is excluded for detail/new. */
export type DetailFeature =
  | "assets"
  | "evidence"
  | "vendors"
  | "vendor-new"
  | "incidents"
  | "incident-new";

const FEATURE_ROUTES: Record<DetailFeature, FrameworkId[]> = {
  assets: FRAMEWORK_IDS,
  evidence: FRAMEWORK_IDS,
  vendors: ["cmmc", "soc2", "aigovernance"],
  "vendor-new": ["cmmc", "soc2", "aigovernance"],
  incidents: ["cmmc", "soc2", "aigovernance"],
  "incident-new": ["cmmc", "soc2", "aigovernance"],
};

export function rememberFramework(id: FrameworkId | null): void {
  if (typeof window === "undefined") return;
  if (id === null) localStorage.removeItem(LAST_FRAMEWORK_KEY);
  else localStorage.setItem(LAST_FRAMEWORK_KEY, id);
}

export function lastFramework(): FrameworkId {
  if (typeof window === "undefined") return "cmmc";
  const raw = localStorage.getItem(LAST_FRAMEWORK_KEY);
  return (FRAMEWORK_IDS as string[]).includes(raw ?? "") ? (raw as FrameworkId) : "cmmc";
}

/** Base path of the framework hosting a shared entity's detail/create views:
 *  current shell, else last selected framework, else CMMC. */
export function frameworkDetailBase(feature: DetailFeature): string {
  const current = frameworkFromPath() as FrameworkId | null;
  const fw = current ?? lastFramework();
  const capable = FEATURE_ROUTES[feature];
  return FRAMEWORK_BASES[capable.includes(fw) ? fw : "cmmc"];
}
