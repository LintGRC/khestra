import { useEffect, useState } from "react";
import { api, apiUrl, authenticatedDownload } from "../api";
import { useLayout } from "../Layout";
import ExportReadinessPanel from "../components/ExportReadinessPanel";
import ExportQualityNote from "../components/ExportQualityNote";
import PageIntro from "../components/PageIntro";
import { CONTROL_FAMILIES, familyLabel } from "../constants/controlFamilies";

function sspUrl(fillStartersOnExport: boolean, sspVersion: string, preparedBy: string, approvedBy: string): string {
  const p = new URLSearchParams();
  if (fillStartersOnExport) p.set("fill_starters", "true");
  if (sspVersion) p.set("version", sspVersion);
  if (preparedBy) p.set("prepared_by", preparedBy);
  if (approvedBy) p.set("approved_by", approvedBy);
  const qs = p.toString();
  return `/api/export/ssp${qs ? `?${qs}` : ""}`;
}

export default function ExportPage() {
  const { dashboard, refreshDashboard, canExport, settings } = useLayout();
  const [acknowledged, setAcknowledged] = useState(false);
  const [fillStartersOnExport, setFillStartersOnExport] = useState(false);
  const [sspVersion, setSspVersion] = useState("");
  const [preparedBy, setPreparedBy] = useState("");
  const [approvedBy, setApprovedBy] = useState("");
  const [family, setFamily] = useState("AC");
  const [importMsg, setImportMsg] = useState("");
  const [validation, setValidation] = useState<string | null>(null);
  const [resourceAsk, setResourceAsk] = useState<string>("");
  const [orgProfile, setOrgProfile] = useState<Record<string, string>>({});
  const profile = orgProfile;
  const missingFields = [
    !profile.cage_code && "CAGE Code",
    !profile.uei && "UEI",
    !profile.poc_name && "POC Name",
    !profile.poc_email && "POC Email",
    !profile.poc_phone && "POC Phone",
    !profile.assessment_methodology && "Assessment Methodology",
  ].filter(Boolean);

  useEffect(() => {
    api.sprsValidation().then((v) => setValidation(v.report)).catch(console.error);
    api.organization().then((data) => {
      setOrgProfile(data.org_profile);
      setResourceAsk(data.org_profile.board_resource_ask || "");
    }).catch(() => {});
  }, []);

  const afterDownload = () => {
    setTimeout(() => refreshDashboard(), 500);
  };

  const onSspDownload = async () => {
    if (!acknowledged) return;
    const url = sspUrl(fillStartersOnExport, sspVersion, preparedBy, approvedBy);
    await authenticatedDownload(apiUrl(url), "SSP.docx");
    afterDownload();
  };

  const onSimpleDownload = (path: string, filename: string) => async () => {
    await authenticatedDownload(apiUrl(path), filename);
    afterDownload();
  };

  const onPoamImport = async (file: File) => {
    setImportMsg("");
    try {
      const r = await api.importPoam(file);
      setImportMsg(`Applied ${r.count} row(s).${r.warnings.length ? ` Warnings: ${r.warnings.join("; ")}` : ""}`);
      await refreshDashboard();
    } catch (err) {
      setImportMsg(String(err));
    }
  };

  const saveResourceAsk = async () => {
    try {
      await api.patchOrgProfile({ board_resource_ask: resourceAsk.trim() });
      refreshDashboard();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <PageIntro view="Export" title="Report center" />
      {!canExport && (
        <div className="banner warning">
          Export is disabled for {settings?.current_role ?? "this role"}. Switch to Assessor, Compliance Manager, or Executive to download reports.
        </div>
      )}

      <ExportReadinessPanel
        dashboardScore={dashboard?.export_readiness_pct}
        sprsScore={dashboard?.sprs_score}
      />

      {canExport && <ExportQualityNote />}

      {dashboard?.export_stale && canExport && (
        <div className="banner warning">
          Your assessment has changed since the last export. Download fresh files below.
        </div>
      )}

      {canExport && missingFields.length > 0 && (
        <div className="banner warning">
          Your SPRS entry summary will be incomplete. Missing: {missingFields.join(", ")}. Add these in the Organization Profile section.
        </div>
      )}

      {canExport && (
      <div className="export-sections panel-stack">
        <h3 className="page-section-heading">Downloads</h3>
        <div className="panel">
          <div className="panel-header">
            <strong>Primary exports</strong>
          </div>
          <div className="panel-body">
            <p className="muted">
              Official DoW Word template and POA&M — assembled from your assessment data.
              The SSP lists attached evidence by filename; download the audit package for the actual files.
            </p>
            <label className="ack-row export-ack-toggle">
              <input
                type="checkbox"
                checked={acknowledged}
                onChange={(e) => setAcknowledged(e.target.checked)}
              />
              I understand exports are drafts for review — not submitted to SPRS automatically. I have reviewed control statuses and narratives.
            </label>
            <label className="ack-row export-starter-toggle">
              <input
                type="checkbox"
                checked={fillStartersOnExport}
                onChange={(e) => setFillStartersOnExport(e.target.checked)}
              />
              Insert org-aware starter text where implementation narrative is empty (export only — does not change saved controls)
            </label>
            <div className="form-grid" style={{ marginTop: "0.75rem" }}>
              <div>
                <label htmlFor="ssp-version">Document version</label>
                <input
                  id="ssp-version"
                  value={sspVersion}
                  onChange={(e) => setSspVersion(e.target.value)}
                  placeholder="e.g. 1.0"
                />
              </div>
              <div>
                <label htmlFor="ssp-prepared-by">Prepared by</label>
                <input
                  id="ssp-prepared-by"
                  value={preparedBy}
                  onChange={(e) => setPreparedBy(e.target.value)}
                  placeholder="Name"
                />
              </div>
              <div>
                <label htmlFor="ssp-approved-by">Approved by</label>
                <input
                  id="ssp-approved-by"
                  value={approvedBy}
                  onChange={(e) => setApprovedBy(e.target.value)}
                  placeholder="Name"
                />
              </div>
            </div>
            <div className="btn-row">
              <button
                type="button"
                className={`btn btn-primary${acknowledged ? "" : " disabled"}`}
                onClick={onSspDownload}
                disabled={!acknowledged}
              >
                SSP (.docx)
              </button>
              <button
                type="button"
                className={`btn btn-outline${acknowledged ? "" : " disabled"}`}
                onClick={onSimpleDownload("/api/export/pdf/ssp-summary", "SSP-Summary.pdf")}
                disabled={!acknowledged}
              >
                SSP Summary (.pdf)
              </button>
              <button
                type="button"
                className={`btn btn-secondary${acknowledged ? "" : " disabled"}`}
                onClick={onSimpleDownload("/api/export/poam", "POAM.xlsx")}
                disabled={!acknowledged}
              >
                POA&M (.xlsx)
              </button>
              <button
                type="button"
                className={`btn btn-outline${acknowledged ? "" : " disabled"}`}
                onClick={onSimpleDownload("/api/export/pdf/poam", "POAM.pdf")}
                disabled={!acknowledged}
              >
                POA&M (.pdf)
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={onSimpleDownload("/api/export/audit-package", "Audit-Package.zip")}
              >
                Audit package (.zip)
              </button>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Executive Board Report</strong></div>
          <div className="panel-body">
            <p className="muted">
              One-page board-ready summary: SPRS posture over time, top risks, POA&amp;M health and your
              resource ask. Exported as PDF.
            </p>
            <div className="form-grid">
              <label>
                Resource ask (shown in the report)
                <input
                  type="text"
                  value={resourceAsk}
                  onChange={(e) => setResourceAsk(e.target.value)}
                  onBlur={saveResourceAsk}
                  placeholder="e.g. Need $15k for an MDM solution to close 3 high-priority gaps"
                />
              </label>
            </div>
            <div className="btn-row">
              <button
                type="button"
                className="btn btn-primary"
                onClick={onSimpleDownload("/api/export/pdf/executive-report", "Executive-Board-Report.pdf")}
              >
                Executive Board Report (.pdf)
              </button>
            </div>
          </div>
        </div>

        <details className="dashboard-details">
          <summary>More exports &amp; imports</summary>
          <div className="dashboard-details-body panel-stack">
            <div className="panel">
              <div className="panel-header"><strong>POA&amp;M CSV, Exception Register &amp; family SSP</strong></div>
              <div className="panel-body">
                <div className="btn-row">
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/poam-csv", "POAM.csv")}>
                    POA&amp;M (.csv)
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/poam-exceptions", "Exception-Register.csv")}>
                    Exception Register (.csv)
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/poam-oscal", "POAM-OSCAL.json")}>
                    OSCAL POA&amp;M (.json)
                  </button>
                </div>
                <div style={{ marginTop: "1rem" }}>
                  <label>Import POA&amp;M CSV (updates control fields)</label>
                  <input type="file" accept=".csv" onChange={(e) => e.target.files?.[0] && onPoamImport(e.target.files[0])} />
                  {importMsg && <p className="muted">{importMsg}</p>}
                </div>
                <div className="filters" style={{ marginTop: "1rem" }}>
                  <select value={family} onChange={(e) => setFamily(e.target.value)}>
                    {CONTROL_FAMILIES.map((f) => (
                      <option key={f.code} value={f.code}>{familyLabel(f.code, f.name)}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={onSimpleDownload(`/api/export/ssp-family?family=${family}`, `SSP-${family}.docx`)}
                  >
                    Download section
                  </button>
                </div>
              </div>
            </div>

            <div className="panel">
              <div className="panel-header"><strong>SPRS &amp; supporting files</strong></div>
              <div className="panel-body">
                <div className="btn-row">
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/sprs-summary", "SPRS-Summary.txt")}>SPRS summary (.txt)</button>
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/sprs-one-pager", "SPRS-One-Pager.txt")}>SPRS one-pager (.txt)</button>
                  <button type="button" className="btn btn-outline" onClick={onSimpleDownload("/api/export/pdf/sprs", "SPRS.pdf")}>SPRS (.pdf)</button>
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/appendix-pack", "Appendix-Pack.zip")}>Appendix pack (.zip)</button>
                </div>
              </div>
            </div>

            <div className="panel">
              <div className="panel-header"><strong>Readiness reports</strong></div>
              <div className="panel-body">
                <div className="btn-row">
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/readiness-review", "Readiness-Review.txt")}>Readiness review (.txt)</button>
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/evidence-coverage", "Evidence-Coverage.txt")}>Evidence coverage (.txt)</button>
                  <button type="button" className="btn btn-secondary" onClick={onSimpleDownload("/api/export/validation-report", "SPRS-Validation.txt")}>SPRS validation (.txt)</button>
                </div>
                {validation && (
                  <pre className="code-block" style={{ marginTop: "1rem", maxHeight: 160, overflow: "auto" }}>
                    {validation.split("\n").slice(0, 8).join("\n")}
                  </pre>
                )}
              </div>
            </div>
          </div>
        </details>

        {dashboard?.last_export_at && !dashboard.export_stale && (
          <p className="muted">Last export matches current assessment ({dashboard.last_export_at}).</p>
        )}
      </div>
      )}
    </>
  );
}
