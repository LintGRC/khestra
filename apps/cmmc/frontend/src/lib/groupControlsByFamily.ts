import { ControlSummary } from "../api";

export type ControlFamilyGroup = {
  family: string;
  controls: ControlSummary[];
};

export function groupControlsByFamily(controls: ControlSummary[]): ControlFamilyGroup[] {
  const groups: ControlFamilyGroup[] = [];
  for (const control of controls) {
    const fam = control.family || "Other";
    const last = groups[groups.length - 1];
    if (last?.family === fam) {
      last.controls.push(control);
    } else {
      groups.push({ family: fam, controls: [control] });
    }
  }
  return groups;
}

export function familyScrollLabel(
  controls: ControlSummary[],
  family?: string,
  code?: string,
): { prefix: string; name: string } {
  const id = controls[0]?.id || "";
  const fromId = id.match(/^([A-Z]{2})\.L2/);
  const prefix = fromId ? `${fromId[1]}.L2` : code ? `${code}.L2` : "";
  const name = family || controls[0]?.family || "";
  return { prefix, name };
}
