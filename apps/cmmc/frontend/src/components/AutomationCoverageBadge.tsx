import { AutomationCoverage } from "../api";

type Props = {
  coverage: AutomationCoverage | null | undefined;
};

const LEVEL_CLS: Record<string, string> = {
  automated: "auto-badge--pass",
  partial: "auto-badge--warn",
  manual: "auto-badge--idle",
};

const LEVEL_LABEL: Record<string, string> = {
  automated: "Coverage: Automated",
  partial: "Coverage: Partial",
  manual: "Coverage: Manual",
};

export default function AutomationCoverageBadge({ coverage }: Props) {
  if (!coverage) return null;

  const cls = LEVEL_CLS[coverage.level] || LEVEL_CLS.manual;
  const label = LEVEL_LABEL[coverage.level] || "Coverage";
  const gapsPreview = (coverage.gaps || []).slice(0, 3).join(" · ");
  const tooltip = [
    coverage.summary,
    coverage.connector_count ? `${coverage.connector_count} connector(s), ${coverage.check_count} check(s)` : "",
    gapsPreview ? `Still needs: ${gapsPreview}` : "No detected human gaps",
  ]
    .filter(Boolean)
    .join("\n");

  const short =
    coverage.level === "partial" && coverage.connector_count
      ? `${label} · ${coverage.connector_count} collector${coverage.connector_count === 1 ? "" : "s"}`
      : label;

  return (
    <span className={`auto-badge ${cls}`} title={tooltip}>
      {short}
    </span>
  );
}
