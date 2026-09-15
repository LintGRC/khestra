export const DEMO_CHOICES = {
  apex: {
    label: "Apex Defense",
    description: "Mature self-assessment — most controls MET, examine refs only (no files).",
  },
  bridgeport: {
    label: "Bridgeport Systems",
    description: "Mid-assessment — open gaps, wireless N/A, ~27 controls with evidence files.",
  },
} as const;

export type DemoId = keyof typeof DEMO_CHOICES;

export const DEMO_LIST: { id: DemoId; label: string; description: string }[] = (
  Object.entries(DEMO_CHOICES) as [DemoId, (typeof DEMO_CHOICES)[DemoId]][]
).map(([id, { label, description }]) => ({ id, label, description }));
