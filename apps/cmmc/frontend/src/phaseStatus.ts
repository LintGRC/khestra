import { Journey } from "./api";

export type PhaseId = "org" | "controls" | "readiness" | "export";

const PHASE_META: Record<PhaseId, { stepIds: string[]; readinessDone?: boolean }> = {
  org: { stepIds: ["profile", "scope"] },
  controls: { stepIds: ["assess", "narratives"] },
  readiness: { readinessDone: true, stepIds: [] },
  export: { stepIds: ["export"] },
};

export function phaseDone(phaseId: PhaseId, steps: Journey["steps"]): boolean {
  const meta = PHASE_META[phaseId];
  if (meta.readinessDone) {
    const assess = steps.find((s) => s.id === "assess");
    const narratives = steps.find((s) => s.id === "narratives");
    return Boolean(assess?.done && narratives?.done);
  }
  return meta.stepIds.every((id) => steps.find((s) => s.id === id)?.done);
}

export function navPhaseState(
  phaseId: PhaseId,
  pathname: string,
  path: string,
  journey: Journey | null,
): "done" | "current" | "upcoming" {
  const steps = journey?.steps ?? [];
  // If path is relative (no leading /), derive full path from current pathname
  const fullPath = path.startsWith("/") ? path : pathname.replace(/^(\/[^/]*).*$/, "$1") + "/" + path;
  const onPage = fullPath === "/" ? pathname === "/" : pathname === fullPath || pathname.startsWith(`${fullPath}/`);
  if (onPage) return "current";
  if (journey && phaseDone(phaseId, steps)) return "done";
  return "upcoming";
}
