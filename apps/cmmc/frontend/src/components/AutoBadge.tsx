import { AutoBadge as AutoBadgeType } from "../api";

type Props = {
  badge: AutoBadgeType | null | undefined;
};

const STATUS_STYLE: Record<string, { cls: string; label: string }> = {
  pass: { cls: "auto-badge--pass", label: "Auto: \u2713 Passing" },
  fail: { cls: "auto-badge--fail", label: "Auto: \u2717 Failing" },
  error: { cls: "auto-badge--error", label: "Auto: \u26A0 Error" },
  partial: { cls: "auto-badge--warn", label: "Auto: \u26A0 Partial" },
  uncollected: { cls: "auto-badge--idle", label: "Auto: No data" },
  stale: { cls: "auto-badge--idle", label: "Auto: Stale" },
};

export default function AutoBadge({ badge }: Props) {
  if (!badge) return null;

  const style = STATUS_STYLE[badge.status] ?? STATUS_STYLE.uncollected;

  const tooltip = badge.status === "error" && badge.error_message
    ? badge.error_message
    : badge.last_run_at
    ? `Last run: ${badge.last_run_at}`
    : "No collector data available";

  return (
    <span
      className={`auto-badge ${style.cls}`}
      title={tooltip}
    >
      {style.label}
    </span>
  );
}
