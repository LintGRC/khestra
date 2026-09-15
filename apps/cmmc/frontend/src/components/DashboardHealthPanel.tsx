import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, ReadinessScores, Remediation, SspProgress } from "../api";
import ReadinessMetricBars from "./ReadinessMetricBars";
import { PanelSkeleton } from "./ui/Skeleton";

const DIMENSIONS = [
  ["Assessment", "assessment_readiness"],
  ["Documentation", "documentation_readiness"],
  ["Evidence", "evidence_readiness"],
  ["Audit readiness", "audit_readiness"],
] as const;

type Props = {
  refreshKey?: string;
};

export default function DashboardHealthPanel({ refreshKey }: Props) {
  const [scores, setScores] = useState<ReadinessScores | null>(null);
  const [remediation, setRemediation] = useState<Remediation | null>(null);
  const [ssp, setSsp] = useState<SspProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.allSettled([api.evidenceCoverage(), api.remediation(), api.sspProgress()]).then(
      (results) => {
        if (cancelled) return;
        const [coverageResult, remediationResult, sspResult] = results;

        if (coverageResult.status === "fulfilled") {
          setScores(coverageResult.value);
        } else {
          setScores(null);
          setError("Could not load readiness scores.");
        }

        if (remediationResult.status === "fulfilled") {
          setRemediation(remediationResult.value);
        } else {
          setRemediation(null);
        }

        if (sspResult.status === "fulfilled") {
          setSsp(sspResult.value);
        } else {
          setSsp(null);
        }

        setLoading(false);
      },
    );

    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const insight = useMemo(() => {
    if (!scores) return null;
    const dims = DIMENSIONS.map(([label, key]) => ({
      label,
      pct: scores[key],
    }));
    const weakest = dims.reduce((a, b) => (b.pct < a.pct ? b : a));
    const parts: string[] = [];
    if (weakest.pct < 80) {
      parts.push(`Weakest area: ${weakest.label} (${weakest.pct}%)`);
    }
    if (ssp && ssp.empty_count > 0) {
      parts.push(
        `${ssp.empty_count} control${ssp.empty_count === 1 ? "" : "s"} need SSP descriptions`,
      );
    }
    if (remediation && remediation.open_items > 0) {
      const high = remediation.critical_count;
      if (high > 0 && high < remediation.open_items) {
        parts.push(
          `${remediation.open_items} open gap${remediation.open_items === 1 ? "" : "s"} (${high} high-severity)`,
        );
      } else {
        parts.push(
          `${remediation.open_items} open gap${remediation.open_items === 1 ? "" : "s"}`,
        );
      }
    }
    if (!parts.length) {
      return scores.audit_readiness >= 80
        ? "Readiness looks solid across assessment, documentation, and evidence."
        : "Complete organization profile and control assessments to build readiness.";
    }
    return parts.join(" · ");
  }, [scores, ssp, remediation]);

  return (
    <div className="panel dashboard-health-panel">
      <div className="panel-header">
        <strong>Overall readiness</strong>
        <Link className="btn-link" to="/readiness">
          Full report
        </Link>
      </div>
      <div className="panel-body">
        {loading && <PanelSkeleton rows={4} />}
        {!loading && error && <p className="muted">{error}</p>}
        {!loading && scores && (
          <>
            <ReadinessMetricBars scores={scores} className="readiness-metric-bars" />
            <p className="muted readiness-caption">
              Audit prep scores (documentation &amp; evidence) — not the same as SPRS gap count.
            </p>
            <p className="dashboard-health-insight muted">
              {insight}
              {insight && !insight.startsWith("Readiness looks solid") && (
                <>
                  {" "}
                  — <Link to="/controls">Review controls</Link>
                </>
              )}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
