import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type ReadinessAssessment } from "../api";
import PageIntro from "../components/PageIntro";

export default function ReadinessPage() {
  const [data, setData] = useState<ReadinessAssessment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.readinessAssessment()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-stack"><p className="muted">Loading readiness assessment…</p></div>;
  if (!data) return <div className="page-stack"><p className="muted">Could not load readiness assessment.</p></div>;

  const pctColor = (pct: number) => pct >= 80 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)";

  return (
    <div className="page-stack">
      <PageIntro title="Readiness Assessment" summary="How close are you to being audit-ready? This assessment evaluates your controls, evidence, policies, and documentation." />

      {data.audit_ready && (
        <div className="banner success">
          Your workspace appears audit-ready! All required checklist items are complete.
        </div>
      )}
      {data.blockers.length > 0 && (
        <div className="banner error">
          <strong>{data.blockers.length} blocker(s) remain:</strong> {data.blockers[0]}
          {data.blockers.length > 1 && ` (+${data.blockers.length - 1} more)`}
        </div>
      )}

      {/* Stats Grid */}
      <div className="dashboard-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
        <div className="stat-card">
          <span className="stat-label">Readiness</span>
          <span className="stat-value" style={{ color: pctColor(data.readiness_pct) }}>{data.readiness_pct}%</span>
          <span className="stat-sub">{data.controls_met}/{data.controls_total} controls met</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Composite Score</span>
          <span className="stat-value" style={{ color: pctColor(data.composite_score) }}>{data.composite_score}</span>
          <span className="stat-sub">weighted readiness</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Open Gaps</span>
          <span className="stat-value" style={{ color: data.gap_count === 0 ? "var(--success)" : "var(--danger)" }}>{data.gap_count}</span>
          <span className="stat-sub">controls need work</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">PoF Coverage</span>
          <span className="stat-value" style={{ color: pctColor(data.pof?.pof_coverage_pct || 0) }}>{(data.pof?.pof_coverage_pct || 0)}%</span>
          <span className="stat-sub">{data.pof?.pof_addressed}/{data.pof?.pof_applicable} PoFs addressed</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Evidence</span>
          <span className="stat-value" style={{ color: pctColor(data.evidence_coverage_pct) }}>{data.evidence_coverage_pct}%</span>
          <span className="stat-sub">coverage</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Effort</span>
          <span className="stat-value" style={{ fontSize: 14, lineHeight: 1.3 }}>{data.effort}</span>
          <span className="stat-sub">estimated</span>
        </div>
      </div>

      {/* Checklist */}
      <section className="panel">
        <div className="panel-header">
          <h3>Audit Readiness Checklist</h3>
          <span className="badge badge-muted">{data.checklist_done}/{data.checklist_total}</span>
        </div>
        <div className="panel-body">
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {data.checklist.map((item) => (
              <li key={item.key} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                <span style={{ fontSize: 18, width: 24, textAlign: "center" }}>
                  {item.done ? "✅" : item.required ? "⬜" : "◽"}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500 }}>{item.label}</div>
                  <div className="muted" style={{ fontSize: 13 }}>{item.detail}</div>
                </div>
                {item.required && !item.done && (
                  <span className="badge badge-danger">Required</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Category Breakdown */}
      <section className="panel">
        <div className="panel-header"><h3>Readiness by Trust Service Category</h3></div>
        <div className="panel-body">
          {data.category_readiness.map((cat) => (
            <div key={cat.category} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <Link to={`/criteria?category=${encodeURIComponent(cat.category)}`} className="btn-link" style={{ fontWeight: 500, textDecoration: "none" }}>
                  {cat.category}
                </Link>
                <span className="muted" style={{ fontSize: 13 }}>{cat.met}/{cat.total} ({cat.readiness_pct}%)</span>
              </div>
              <div style={{ background: "var(--border-subtle)", borderRadius: 4, height: 8, overflow: "hidden" }}>
                <div style={{
                  width: `${cat.readiness_pct}%`,
                  height: "100%",
                  background: pctColor(cat.readiness_pct),
                  borderRadius: 4,
                  transition: "width 0.3s",
                }} />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Open Gaps */}
      {data.open_gaps.length > 0 && (
        <section className="panel">
          <div className="panel-header">
            <h3>Open Gaps</h3>
            <span className="badge badge-danger">{data.gap_count}</span>
          </div>
          <div className="panel-body">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Control</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Narrative</th>
                  <th>Evidence</th>
                  <th>Owner</th>
                  <th>Target</th>
                </tr>
              </thead>
              <tbody>
                {data.open_gaps.map((gap) => (
                  <tr key={gap.control_id}>
                    <td>
                      <Link to={`/criteria/${gap.control_id}`} className="btn-link">{gap.control_id}</Link>
                    </td>
                    <td>{gap.category}</td>
                    <td><span className={`badge ${gap.status === "NOT MET" ? "badge-danger" : "badge-warning"}`}>{gap.status}</span></td>
                    <td>{gap.has_narrative ? "✅" : "—"}</td>
                    <td>{gap.has_evidence ? "✅" : "—"}</td>
                    <td>{gap.owner || "—"}</td>
                    <td>{gap.target_date || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Missing Evidence */}
      {data.missing_evidence_count > 0 && (
        <section className="panel">
          <div className="panel-header">
            <h3>Met Controls Without Evidence</h3>
            <span className="badge badge-warning">{data.missing_evidence_count}</span>
          </div>
          <div className="panel-body">
            <p className="muted" style={{ marginBottom: 8 }}>
              These controls are marked MET but have no uploaded evidence. Auditors will ask for proof.
            </p>
            <table className="data-table">
              <thead>
                <tr><th>Control</th><th>Category</th><th>Name</th></tr>
              </thead>
              <tbody>
                {data.missing_evidence.map((item) => (
                  <tr key={item.control_id}>
                    <td><Link to={`/criteria/${item.control_id}`} className="btn-link">{item.control_id}</Link></td>
                    <td>{item.category}</td>
                    <td>{item.name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Missing Narratives */}
      {data.missing_narrative_count > 0 && (
        <section className="panel">
          <div className="panel-header">
            <h3>Met Controls Without Narratives</h3>
            <span className="badge badge-warning">{data.missing_narrative_count}</span>
          </div>
          <div className="panel-body">
            <p className="muted" style={{ marginBottom: 8 }}>
              These controls are marked MET but have no implementation narrative documented.
            </p>
            <table className="data-table">
              <thead>
                <tr><th>Control</th><th>Category</th><th>Name</th></tr>
              </thead>
              <tbody>
                {data.missing_narrative.map((item) => (
                  <tr key={item.control_id}>
                    <td><Link to={`/criteria/${item.control_id}`} className="btn-link">{item.control_id}</Link></td>
                    <td>{item.category}</td>
                    <td>{item.name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
