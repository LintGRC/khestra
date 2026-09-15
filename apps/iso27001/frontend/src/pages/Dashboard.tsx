import { useLayout } from "../Layout";
import { authenticatedDownload } from "../api";

export default function Dashboard() {
  const { dashboard, apiError, refreshDashboard } = useLayout();
  const counts = dashboard?.rollup?.counts ?? {};

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <h2>ISO 27001 Dashboard</h2>
          <p className="muted">Statement of Applicability and certification readiness overview.</p>
        </div>
        {dashboard && (
          <div className="sprs-chip readiness-chip">
            {dashboard.readiness_pct}% implemented
          </div>
        )}
      </section>
      {apiError && (
        <div className="banner error">
          {apiError}{" "}
          <button type="button" className="btn-link" onClick={() => refreshDashboard()}>
            Retry
          </button>
        </div>
      )}
      {dashboard && (
        <>
          <div className="metric-grid">
            <div className="metric-card">
              <div className="metric-value">{dashboard.rollup.total}</div>
              <div className="metric-label">Controls in SoA</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{counts.implemented ?? 0}</div>
              <div className="metric-label">Implemented</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{counts["partially implemented"] ?? 0}</div>
              <div className="metric-label">Partially implemented</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{counts["not implemented"] ?? 0}</div>
              <div className="metric-label">Not implemented</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{counts.excluded ?? 0}</div>
              <div className="metric-label">Excluded</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{dashboard.tests_total}</div>
              <div className="metric-label">Control tests</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{dashboard.evidence_total}</div>
              <div className="metric-label">Evidence items</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{dashboard.evidence_linked}</div>
              <div className="metric-label">Evidence linked to controls</div>
            </div>
          </div>
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Auditor pack (clauses 9.2 / 9.3)</h3>
            <p className="muted" style={{ fontSize: 13 }}>
              Internal audit report, management-review minutes, and the nonconformity / corrective-action register.
            </p>
            <div className="button-row">
              <button type="button" className="btn btn-secondary" onClick={() => authenticatedDownload("/api/iso/auditor-pack.zip", "iso27001_auditor_pack.zip")}>
                Download auditor pack
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => authenticatedDownload("/api/iso/audit-report.docx", "iso27001_internal_audit_report.docx")}>
                Internal audit (9.2)
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => authenticatedDownload("/api/iso/management-review.docx", "iso27001_management_review_minutes.docx")}>
                Management review (9.3)
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => authenticatedDownload("/api/iso/nc-capa.xlsx", "iso27001_nc_capa_register.xlsx")}>
                NC / CAPA register
              </button>
            </div>
          </div>
          <div className="card">
            <h3 style={{ marginTop: 0 }}>By section</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Section</th>
                  <th>Controls</th>
                  <th>Implemented</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(dashboard.rollup.by_section).map(([section, info]) => (
                  <tr key={section}>
                    <td>{section}</td>
                    <td>{info.total}</td>
                    <td>{info.implemented}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}