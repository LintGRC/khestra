import { useEffect, useState } from "react";
import { api, ReadinessScores } from "../api";
import { pctTone } from "../lib/readinessTone";

export default function AssessmentReadinessStrip() {
  const [scores, setScores] = useState<ReadinessScores | null>(null);
  const [familyOpen, setFamilyOpen] = useState(false);

  useEffect(() => {
    api.evidenceCoverage().then((s) => {
      setScores(s as ReadinessScores);
      if ((s as ReadinessScores).evidence_readiness < 100) {
        setFamilyOpen(true);
      }
    }).catch(console.error);
  }, []);

  if (!scores) return null;

  const rows = [
    ["Assessment", scores.assessment_readiness],
    ["Documentation", scores.documentation_readiness],
    ["Evidence", scores.evidence_readiness],
    ["Audit readiness", scores.audit_readiness],
  ] as const;

  const ev = scores.evidence_detail;
  const families = ev?.families ?? [];
  const weakFamilies = ev?.weak_families ?? [];

  return (
    <div className="panel assessment-readiness-strip">
      <div className="panel-header">
        <strong>Readiness</strong>
        <span className="muted">Audit prep — not SPRS score</span>
      </div>
      <div className="panel-body">
        <div className="readiness-stat-grid">
          {rows.map(([label, pct]) => (
            <div key={label} className={`stat-card stat-${pctTone(pct)}`}>
              <div className="stat-label">{label}</div>
              <div className="stat-value">{pct}%</div>
            </div>
          ))}
        </div>
        {ev?.met_count ? (
          <p className="muted readiness-caption">
            <strong>{ev.met_count}</strong> controls marked MET — evidence or examine ref on{" "}
            <strong>{ev.with_evidence_count}</strong> ({ev.evidence_pct}%).
            {ev.evidence_files_count != null && ev.evidence_files_count > 0 && (
              <> · <strong>{ev.evidence_files_count}</strong> file(s) attached.</>
            )}
          </p>
        ) : (
          <p className="muted readiness-caption">Mark implementation status to track evidence coverage.</p>
        )}

        {weakFamilies.length > 0 && (
          <div className="banner warning evidence-weak-banner">
            Weakest families:{" "}
            {weakFamilies
              .slice(0, 5)
              .map((r) => `${r.family} (${r.evidence_pct}%)`)
              .join(", ")}
          </div>
        )}

        {families.length > 0 && (
          <div className="evidence-family-section">
            <button
              type="button"
              className="btn-link evidence-family-toggle"
              onClick={() => setFamilyOpen(!familyOpen)}
            >
              {familyOpen ? "Hide" : "Show"} evidence coverage by family
            </button>
            {familyOpen && (
              <table className="evidence-family-table">
                <thead>
                  <tr>
                    <th>Family</th>
                    <th>Controls</th>
                    <th>MET w/ evidence</th>
                    <th>Coverage</th>
                  </tr>
                </thead>
                <tbody>
                  {families.map((row) => (
                    <tr key={row.code}>
                      <td>
                        <span className="family-name-cell">{row.family}</span>
                        <span className="muted family-code-cell"> ({row.code})</span>
                      </td>
                      <td>{row.controls_label}</td>
                      <td>
                        {row.met ? `${row.with_evidence}/${row.met}` : "—"}
                      </td>
                      <td>{row.evidence_pct != null ? `${row.evidence_pct}%` : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
