import { useEffect, useState } from "react";
import { api, apiUrl, EvidenceManifest } from "../api";
import PageIntro from "../components/PageIntro";
import { PageSkeleton } from "../components/ui/Skeleton";

export default function ReportsPage() {
  const [manifest, setManifest] = useState<EvidenceManifest | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.manifest()
      .then(setManifest)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageSkeleton variant="default" />;

  return (
    <div className="page-stack">
      <PageIntro title="Reports & Exports" />

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header"><strong>System Description (DOCX)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Full system description with control environment, assessment details, evidence summary, and appendices.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/system-description-docx")}>
              Download DOCX
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Exceptions (CSV)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Control exceptions with compensating controls, risk levels, and remediation plans.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/exceptions")}>
              Download CSV
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Exceptions (DOCX)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Exceptions report in document format — ready to share with auditors and management.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/exceptions-docx")}>
              Download DOCX
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Evidence index (CSV)</strong></div>
          <div className="panel-body">
            <p className="muted">
              All evidence items across all criteria with SHA-256 hashes.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/evidence-index")}>
              Download CSV
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Readiness summary (CSV)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Readiness %, evidence coverage, and gap counts — snapshot for auditor handoff.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/readiness-summary")}>
              Download CSV
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Control Matrix (Excel)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Criteria × evidence grid with status, PoF coverage, narratives, and owner — side-by-side view for audit planning.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/control-matrix")}>
              Download XLSX
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>System description (Markdown)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Auditor-facing narrative from control statuses and implementation narratives.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/system-description")}>
              Download Markdown
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Executive Summary (PDF)</strong></div>
          <div className="panel-body">
            <p className="muted">
              One-page board/management report: readiness, category breakdown, risks, exceptions, tests, and PoF coverage.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/executive-summary")}>
              Download PDF
            </a>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header"><strong>Gap Analysis (DOCX)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Per-criterion remediation plan: open gaps with recommended actions, evidence hints, and owner assignments.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/gap-analysis")}>
              Download DOCX
            </a>
          </div>
        </section>

        <section className="panel" style={{ gridColumn: "1 / -1" }}>
          <div className="panel-header"><strong>Full Audit Package (ZIP)</strong></div>
          <div className="panel-body">
            <p className="muted">
              Complete package: System Description (DOCX), Exceptions (CSV), evidence index, readiness summary, and all evidence files.
            </p>
            <a className="btn btn-primary btn-sm" href={apiUrl("/api/reports/audit-package-enhanced")}>
              Download Audit Package
            </a>
          </div>
        </section>
      </div>

      {manifest && (
        <section className="panel">
          <div className="panel-header"><strong>Evidence summary</strong></div>
          <div className="panel-body">
            <div className="stats stats-compact">
              <div className="stat-card">
                <div className="stat-label">Total evidence</div>
                <div className="stat-value">{manifest.total_evidence}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Controls covered</div>
                <div className="stat-value">{manifest.controls_covered}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Manifest hash</div>
                <div className="stat-value stat-value--compact" style={{ wordBreak: "break-all" }}>{manifest.manifest_hash.slice(0, 16)}…</div>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
