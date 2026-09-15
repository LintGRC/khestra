import { Link, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { api, ReadinessScores } from "../api";
import SprsWeightBadge from "./SprsWeightBadge";
import CollectorDotLegend from "./CollectorDotLegend";
import SprsWeightLegend from "./SprsWeightLegend";

type PriorityRow = {
  id: string;
  name?: string;
  family?: string;
  status?: string;
  weight_tier?: string;
  weight_badge?: string;
};

type Props = {
  priorityRows: PriorityRow[];
  onGoToControl: (controlId: string) => void;
};

export default function AssessmentInsightsPanel({ priorityRows, onGoToControl }: Props) {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const focusLink = (controlId: string) => `${fwBase}/controls?focus=${encodeURIComponent(controlId)}`;
  const [scores, setScores] = useState<ReadinessScores | null>(null);
  const [poamOverdue, setPoamOverdue] = useState<{ control_id: string; message: string }[]>([]);
  const [envSuggestions, setEnvSuggestions] = useState<{ control_id: string; reason: string }[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    Promise.all([api.evidenceCoverage(), api.alerts()])
      .then(([s, alerts]) => {
        setScores(s as ReadinessScores);
        setPoamOverdue(alerts.poam_overdue || []);
        setEnvSuggestions(alerts.env_suggestions || []);
        setLoaded(true);
      })
      .catch(console.error);
  }, []);

  const alertCount = useMemo(() => {
    const weak = scores?.evidence_detail?.weak_families?.length ?? 0;
    return poamOverdue.length + envSuggestions.length + (weak > 0 ? 1 : 0);
  }, [poamOverdue, envSuggestions, scores]);

  if (!loaded) return null;

  const ev = scores?.evidence_detail;
  const topPriority = priorityRows.slice(0, 5);

  return (
    <details className="insights-panel">
      <summary className="insights-panel-summary">
        <span>
          Assessment insights
          {alertCount > 0 && <span className="insights-badge">{alertCount} to review</span>}
        </span>
        <span className="muted">Readiness, scoping &amp; priorities</span>
      </summary>
      <div className="insights-panel-body">
        {scores && (
          <div className="insights-readiness-row">
            <div className="insights-stat">
              <span className="insights-stat-label">Evidence</span>
              <span className="insights-stat-value">{scores.evidence_readiness}%</span>
            </div>
            <div className="insights-stat">
              <span className="insights-stat-label">Documentation</span>
              <span className="insights-stat-value">{scores.documentation_readiness}%</span>
            </div>
            <div className="insights-stat">
              <span className="insights-stat-label">Audit prep</span>
              <span className="insights-stat-value">{scores.audit_readiness}%</span>
            </div>
            {ev?.met_count ? (
              <p className="muted insights-caption">
                {ev.with_evidence_count}/{ev.met_count} MET controls have evidence or examine refs
              </p>
            ) : null}
          </div>
        )}

        {poamOverdue.length > 0 && (
          <div className="banner warning insights-alert">
            <strong>{poamOverdue.length} overdue POA&amp;M:</strong>{" "}
            {poamOverdue.slice(0, 4).map((a, i) => (
              <span key={a.control_id}>
                {i > 0 && ", "}
                <Link to={focusLink(a.control_id)}>{a.control_id}</Link>
              </span>
            ))}
          </div>
        )}

        {envSuggestions.length > 0 ? (
          <div className="insights-section">
            <p className="insights-section-label">Scoping suggestions</p>
            <div className="priority-list compact">
              {envSuggestions.slice(0, 6).map((item) => (
                <Link key={item.control_id} className="priority-control-link" to={focusLink(item.control_id)}>
                  <strong>{item.control_id}</strong>
                  <span className="muted"> — {item.reason}</span>
                </Link>
              ))}
            </div>
          </div>
        ) : (
          <p className="muted insights-hint">
            Complete <Link to={`${fwBase}/organization`}>environment scope</Link> for N/A suggestions.
          </p>
        )}

        {topPriority.length > 0 && (
          <div className="insights-section">
            <p className="insights-section-label">Priority controls (5-point first)</p>
            <div className="priority-list">
              {topPriority.map((row) => (
                <button
                  key={row.id}
                  type="button"
                  className="priority-control-link"
                  onClick={() => onGoToControl(row.id)}
                >
                  <div className="priority-control-row">
                    <div className="priority-control-badge">
                      <SprsWeightBadge label={row.weight_badge || "—"} tier={row.weight_tier || "standard"} />
                    </div>
                    <div className="priority-control-body">
                      <div className="priority-control-id">{row.id}</div>
                      <div className="priority-control-meta muted">
                        {[row.family, row.status].filter(Boolean).join(" · ")}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        <SprsWeightLegend />
        <CollectorDotLegend />
      </div>
    </details>
  );
}
