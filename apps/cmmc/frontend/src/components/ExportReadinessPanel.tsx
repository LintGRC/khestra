import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, ExportReadinessReport } from "../api";

type Props = {
  dashboardScore?: number;
  sprsScore?: number;
};

export default function ExportReadinessPanel({ dashboardScore, sprsScore }: Props) {
  const [report, setReport] = useState<ExportReadinessReport | null>(null);
  const [warningsOpen, setWarningsOpen] = useState(false);

  useEffect(() => {
    api.exportReadinessReport().then(setReport).catch(console.error);
  }, []);

  if (!report) return null;

  const score = report.score ?? dashboardScore ?? 0;
  const sprs = report.sprs_score ?? sprsScore ?? 0;
  const narratives = report.ssp_narratives;
  const showWarnings = warningsOpen || score < 70;

  return (
    <div className="export-readiness-panel">
      <div className="stats">
        <div className={`stat-card stat-${score >= 70 ? "good" : score >= 50 ? "warn" : "bad"}`}>
          <div className="stat-label">Export readiness</div>
          <div className="stat-value">{score}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">SPRS score</div>
          <div className="stat-value">{sprs}/110</div>
        </div>
        <div className={`stat-card stat-${report.open_gap_count ? "bad" : "good"}`}>
          <div className="stat-label">Open gaps</div>
          <div className="stat-value">{report.open_gap_count}</div>
        </div>
        {narratives && (
          <div className={`stat-card stat-${narratives.documented_pct >= 70 ? "good" : narratives.documented_pct >= 40 ? "warn" : "bad"}`}>
            <div className="stat-label">SSP descriptions</div>
            <div className="stat-value">{narratives.documented_count}/{narratives.scoped_count}</div>
          </div>
        )}
      </div>

      {narratives && narratives.empty_count > 0 && (
        <div className="banner info">
          {narratives.empty_count} control{narratives.empty_count === 1 ? "" : "s"} still need an SSP description.{" "}
          <Link to="/controls">Review on Controls</Link> — use the progress bar to filter missing.
        </div>
      )}

      {narratives && narratives.missing_met_narrative_count > 0 && (
        <div className="banner info">
          {narratives.missing_met_narrative_count} MET/N/A/Inherited control{narratives.missing_met_narrative_count === 1 ? "" : "s"} still lack a narrative.
          Use <Link to="/controls">Controls → Draft SSP narratives</Link> or enable starters on SSP export.
        </div>
      )}

      {report.blockers.map((b) => (
        <div key={b} className="banner error">
          {b}
        </div>
      ))}

      {report.warning_items.length > 0 && (
        <div className="panel">
          <button
            type="button"
            className="panel-header export-warnings-toggle"
            aria-expanded={showWarnings}
            onClick={() => setWarningsOpen(!warningsOpen)}
          >
            <strong>{report.warning_items.length} recommendations before export</strong>
          </button>
          {showWarnings && (
            <div className="panel-body">
              <p className="muted">
                Fill these in under Organization → System Profile when you can. Exports still work; SSP uses placeholders where needed.
              </p>
              <ul className="export-warning-list">
                {report.warning_items.map((w) => (
                  <li key={w.title}>
                    <strong>{w.title}</strong>
                    {w.detail && <div className="muted">{w.detail}</div>}
                  </li>
                ))}
              </ul>
              {report.missing_narrative_controls.length > 0 && (
                <>
                  <p className="muted"><strong>Controls missing narratives (sample):</strong></p>
                  <div className="priority-chips">
                    {report.missing_narrative_controls.map((c) => (
                      <Link
                        key={c.id}
                        className="priority-chip"
                        to={`/controls/${encodeURIComponent(c.id)}`}
                        title={c.name}
                      >
                        {c.id} · {c.status}
                      </Link>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
