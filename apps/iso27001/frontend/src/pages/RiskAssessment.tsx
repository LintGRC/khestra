import { Link, useLocation } from "react-router-dom";
import { authenticatedDownload } from "../api";

const SCALES: Array<[number, string, string]> = [
  [0, "Negligible", "Rare"],
  [1, "Low", "Unlikely"],
  [2, "Moderate", "Possible"],
  [3, "High", "Likely"],
  [4, "Very high", "Almost certain"],
  [5, "Extreme", "Certain"],
];

export default function RiskAssessmentPage() {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(iso27001)/)?.[0] ?? "";

  return (
    <>
      <section className="page-header">
        <div>
          <h2>Risk assessment</h2>
          <p className="muted">
            ISO/IEC 27001:2022 clause 6.1 — ISO 31000-aligned ISMS risk assessment and reporting.
          </p>
        </div>
      </section>
      <div className="panel-stack">
        <div className="panel">
          <div className="panel-header">
            <strong>Process (ISO 31000 / ISO 27001 clause 6.1)</strong>
          </div>
          <div className="panel-body">
            <ol>
              <li>
                <strong>Context (clauses 4.1 / 4.2):</strong> record internal and external issues,
                interested parties, and their requirements in{" "}
                <Link to={`${fwBase}/context`}>Context &amp; Scope</Link>.
              </li>
              <li>
                <strong>Risk criteria (clause 6.1.2):</strong> use the consequence and likelihood
                scales below to define acceptable risk.
              </li>
              <li>
                <strong>Risk assessment (clause 6.1.3):</strong> record risks in the{" "}
                <Link to={`${fwBase}/risks`}>Risk Register</Link> with a{" "}
                <code>framework = iso27001</code> tag so they feed this report, the compliance
                calendar, and evidence-hub mappings.
              </li>
              <li>
                <strong>Risk treatment (clause 6.2):</strong> select treatment (avoid / mitigate /
                transfer / accept) and link controls in the register.
              </li>
              <li>
                <strong>Report:</strong> export the Risk Assessment Report and Risk Register below —
                both are required ISMS documents.
              </li>
            </ol>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <strong>Risk criteria — consequence &amp; likelihood scales (clause 6.1.2)</strong>
          </div>
          <div className="panel-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Score</th>
                  <th>Consequence</th>
                  <th>Likelihood</th>
                </tr>
              </thead>
              <tbody>
                {SCALES.map(([score, consequence, likelihood]) => (
                  <tr key={score}>
                    <td>{score}</td>
                    <td>{consequence}</td>
                    <td>{likelihood}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="muted" style={{ marginTop: "0.75rem" }}>
              Inherent score = consequence × likelihood (0–25). Levels: 12+ Critical, 9+ High,
              6+ Medium, 4+ Low. Record residual risk after treatment.
            </p>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <strong>Deliverables</strong>
          </div>
          <div className="panel-body">
            <div className="button-row">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => authenticatedDownload("/api/iso/risk-report.docx", "iso27001_risk_assessment_report.docx")}
              >
                Export Risk Assessment Report (DOCX)
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => authenticatedDownload("/api/iso/risk-report.xlsx", "iso27001_risk_register.xlsx")}
              >
                Export Risk Register (XLSX)
              </button>
            </div>
            <p className="muted" style={{ marginTop: "0.75rem" }}>
              Reports include ISO-scoped risks only (<code>framework = iso27001</code> in the Risk
              Register). Empty until risks are recorded.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
