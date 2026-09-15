/** CMMC / 800-171 control families — code is official prefix in control IDs (e.g. AC.L2-3.1.1). */
export const CONTROL_FAMILIES = [
  { code: "AC", name: "Access Control" },
  { code: "AT", name: "Awareness and Training" },
  { code: "AU", name: "Audit and Accountability" },
  { code: "CM", name: "Configuration Management" },
  { code: "IA", name: "Identification and Authentication" },
  { code: "IR", name: "Incident Response" },
  { code: "MA", name: "Maintenance" },
  { code: "MP", name: "Media Protection" },
  { code: "PE", name: "Physical Protection" },
  { code: "PS", name: "Personnel Security" },
  { code: "RA", name: "Risk Assessment" },
  { code: "CA", name: "Security Assessment" },
  { code: "SC", name: "System and Communications Protection" },
  { code: "SI", name: "System and Information Integrity" },
] as const;

export function familyLabel(code: string, name: string) {
  return `${name} (${code})`;
}
