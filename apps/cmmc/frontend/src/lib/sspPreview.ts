import { ControlDetail } from "../api";
import { CONTROL_FAMILIES } from "../constants/controlFamilies";

export type SspPreviewPayload = {
  control_id: string;
  heading: string;
  family: string;
  family_section: string;
  attributes: { label: string; value: string }[];
  description: string;
  description_missing: boolean;
  assessment_methods: string[];
  evidence_files: { filename: string; upload_date: string }[];
  placeholders: string[];
  export_note: string;
};

function riskSeverity(weight: number): string {
  if (weight >= 5) return "Critical";
  if (weight === 3) return "High";
  if (weight === 1) return "Moderate";
  return "Low";
}

function familySectionLabel(familyName: string): string {
  const idx = CONTROL_FAMILIES.findIndex((f) => f.name === familyName);
  return idx >= 0 ? `5.${idx + 1} ${familyName}` : familyName;
}

const PLACEHOLDER_RE = /\[[^\]]+\]/g;

export function buildControlSspPreview(
  control: ControlDetail,
  form: Partial<ControlDetail>,
): SspPreviewPayload {
  const status = form.status || control.status || "NOT STARTED";
  const narrative = (form.implementation_narrative ?? control.implementation_narrative ?? "").trim();
  const examine = (form.examine ?? control.examine ?? "").trim();
  const interview = (form.interview ?? control.interview ?? "").trim();
  const test = (form.test ?? control.test ?? "").trim();
  const evidence = control.evidence || [];

  let description: string;
  let description_missing: boolean;
  if (narrative) {
    description = narrative;
    description_missing = false;
  } else if (status === "MET") {
    description =
      "Control implementation narrative not provided. Describe how this control is implemented.";
    description_missing = true;
  } else {
    description = "Control not yet implemented.";
    description_missing = true;
  }

  const assessment_methods: string[] = [];
  if (examine) assessment_methods.push(`Examine: ${examine}`);
  if (interview) assessment_methods.push(`Interview: ${interview}`);
  if (test) assessment_methods.push(`Test: ${test}`);

  const placeholders = [...new Set(description.match(PLACEHOLDER_RE) ?? [])];

  return {
    control_id: control.id,
    heading: `${control.id} - ${control.name}`,
    family: control.family,
    family_section: familySectionLabel(control.family),
    attributes: [
      { label: "Status", value: status },
      { label: "Impact Level", value: riskSeverity(control.weight) },
      { label: "Weight", value: String(control.weight) },
    ],
    description,
    description_missing,
    assessment_methods,
    evidence_files: evidence.map((ev) => ({
      filename: ev.filename,
      upload_date: ev.upload_date,
    })),
    placeholders,
    export_note: "Read-only preview — updates as you edit. Filenames export in the SSP; actual files are in the audit package zip.",
  };
}
