export type WeightTier = "critical" | "standard" | "low" | "variable";

function statusTone(status: string): string {
  if (status === "MET" || status === "NOT APPLICABLE" || status === "INHERITED") return "status-met";
  if (status === "NOT MET" || status === "NOT STARTED") return "status-gap";
  return "status-neutral";
}

type Props = {
  label: string;
  tier: WeightTier | string;
  status?: string;
  title?: string;
};

export default function SprsWeightBadge({ label, tier, status, title }: Props) {
  const classes = [
    "sprs-weight-badge",
    `sprs-weight-${tier}`,
    status ? "sprs-weight-badge-status" : "",
    status ? statusTone(status) : "",
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <span className={classes} title={title}>
      {label}
    </span>
  );
}

export function focusAnchorId(controlId: string): string {
  return `cmmc-focus-${controlId.replace(/\./g, "-")}`;
}
