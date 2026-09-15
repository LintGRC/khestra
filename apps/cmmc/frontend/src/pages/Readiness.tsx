import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { api, apiUrl, authenticatedDownload, CmmcAssessmentStatus, L1Status, PreC3paoReadiness, Remediation, SprsLedgerRow } from "../api";
import { useLayout } from "../Layout";
import SprsEntryCopy from "../components/SprsEntryCopy";
import SprsTrendChart from "../components/SprsTrendChart";
import { BurndownChart, HorizontalBarChart, SeverityChart } from "../components/ReadinessCharts";
import PageIntro from "../components/PageIntro";
import PackageQualityFindings, { FindingSummary } from "../components/PackageQualityFindings";
import { pctTone } from "../lib/readinessTone";
import { PageSkeleton } from "../components/ui/Skeleton";

type ReviewFinding = { severity: string; title: string; detail: string; control_ids?: string[] };
type ReadinessReview = {
  review_score: number;
  evidence: { met_count: number; with_evidence_count: number; without_evidence_count: number };
  high_count: number;
  medium_count: number;
  findings: ReviewFinding[];
  finding_summary: FindingSummary;
  quality_explanation: string;
  roadmap: { control_id: string; score_impact: number; difficulty: string }[];
};

type EvidenceCoverage = {
  audit_readiness: number;
  assessment_readiness: number;
  documentation_readiness: number;
  evidence_readiness: number;
  export_readiness: number;
};

export default function ReadinessPage() {
  const { canExport, settings } = useLayout();
  const [data, setData] = useState<PreC3paoReadiness | null>(null);
  const [review, setReview] = useState<ReadinessReview | null>(null);
  const [coverage, setCoverage] = useState<EvidenceCoverage | null>(null);
  const [remediation, setRemediation] = useState<Remediation | null>(null);
  const [ledger, setLedger] = useState<SprsLedgerRow[]>([]);
  const [simOpen, setSimOpen] = useState(false);
  const [ledgerOpen, setLedgerOpen] = useState(false);
  const [simControl, setSimControl] = useState("");
  const [simStatus, setSimStatus] = useState("NOT MET");
  const [simResult, setSimResult] = useState<{ current_score: number; projected_score: number; delta: number } | null>(null);
  const [simBusy, setSimBusy] = useState(false);
  const [assessStatus, setAssessStatus] = useState<CmmcAssessmentStatus | null>(null);
  const [closeoutBusy, setCloseoutBusy] = useState(false);
  const [l1, setL1] = useState<L1Status | null>(null);

  useEffect(() => {
    Promise.all([api.preC3pao(), api.readinessReview(), api.evidenceCoverage(), api.remediation(), api.sprsLedger()]).then(([p, r, c, rem, l]) => {
      setData(p);
      setReview(r as ReadinessReview);
      setCoverage(c as EvidenceCoverage);
      setRemediation(rem);
      setLedger(l.rows);
    }).catch(console.error);
    api.assessmentStatus().then(setAssessStatus).catch(() => {});
    api.l1Status().then(setL1).catch(() => {});
  }, []);

  const runCloseout = async () => {
    if (closeoutBusy) return;
    setCloseoutBusy(true);
    try {
      setAssessStatus(await api.assessmentCloseout());
    } catch (err) {
      alert(String(err));
    } finally {
      setCloseoutBusy(false);
    }
  };

  const setL1Status = async (controlId: string, status: string) => {
    try {
      setL1(await api.putL1Status(controlId, status));
    } catch (err) {
      alert(String(err));
    }
  };

  const copyL1Entry = async () => {
    try {
      const { text } = await api.l1EntryText();
      await navigator.clipboard.writeText(text);
      alert("Level 1 SPRS entry summary copied to clipboard.");
    } catch (err) {
      alert(String(err));
    }
  };

  const severityCounts = useMemo(() => {
    if (!remediation) return {};
    const counts: Record<string, number> = {};
    for (const row of remediation.schedule) {
      counts[row.severity] = (counts[row.severity] || 0) + 1;
    }
    return counts;
  }, [remediation]);

  const gapBars = useMemo(
    () =>
      remediation?.gaps_by_family.slice(0, 10).map((r) => ({
        label: r.family,
        value: r.count,
      })) ?? [],
    [remediation],
  );

  const gapRows = useMemo(() => {
    if (!remediation?.schedule.length) return [];
    const roadmapById = new Map((review?.roadmap ?? []).map((r) => [r.control_id, r]));
    const weightById = new Map(remediation.burndown.map((b) => [b.control_id, b.weight]));
    const priorityOrder = new Map(data?.remediation_priority.map((id, i) => [id, i]) ?? []);
    return [...remediation.schedule]
      .sort(
        (a, b) =>
          (priorityOrder.get(a.control_id) ?? 99) - (priorityOrder.get(b.control_id) ?? 99),
      )
      .slice(0, 20)
      .map((row) => ({
        ...row,
        weight: roadmapById.get(row.control_id)?.score_impact ?? weightById.get(row.control_id),
        difficulty: roadmapById.get(row.control_id)?.difficulty,
      }));
  }, [remediation, review, data?.remediation_priority]);

  if (!data) return <PageSkeleton />;

  return (
    <>
      <PageIntro view="Readiness" title="Pre-C3PAO readiness" />
      {assessStatus && (
        <div
          className={`banner ${
            assessStatus.closeout_expired || assessStatus.reassessment_expired || assessStatus.affirmation_expired
              ? "error"
              : assessStatus.status === "conditional"
                ? "warning"
                : assessStatus.status === "final"
                  ? "success"
                  : "info"
          }`}
        >
          <strong>CMMC status ({assessStatus.assessment_type_label || "not declared"}):</strong>{" "}
          {assessStatus.status === "conditional" && (
            <>
              Conditional — POA&amp;M closeout due {assessStatus.closeout_due}
              {assessStatus.closeout_expired
                ? " — EXPIRED (status lapsed; re-assess and re-post to SPRS)"
                : ` (${assessStatus.closeout_days_left} days left)`}
              {assessStatus.gap_count === 0 && (
                <>
                  {" "}
                  — all requirements remediated, ready to close out.{" "}
                  <button className="btn btn-primary" disabled={closeoutBusy} onClick={runCloseout}>
                    {closeoutBusy ? "Closing out…" : "Complete closeout"}
                  </button>
                </>
              )}
            </>
          )}
          {assessStatus.status === "final" && (
            <>
              Final — reassessment due {assessStatus.reassessment_due || "—"}
              {assessStatus.reassessment_expired && " (EXPIRED)"}
              {assessStatus.affirmation_due && ` · annual affirmation due ${assessStatus.affirmation_due}`}
            </>
          )}
          {!assessStatus.status && <>no status recorded — set your assessment type and status on the Organization page.</>}
        </div>
      )}
      {l1 && (
        <div className="panel">
          <div className="panel-header">
            <strong>
              CMMC Level 1 track (FAR 52.204-21 — 15 safeguards, §170.15){" "}
              <span className={`badge ${l1.all_met ? "badge-success" : "badge-warning"}`}>
                {l1.score}/{l1.total} MET
              </span>
            </strong>
          </div>
          <div className="panel-body">
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontSize: 13 }}>
                Status date:{" "}
                <input
                  type="date"
                  value={l1.status_date}
                  onChange={(e) =>
                    api.putL1Assessment({ status_date: e.target.value, affirming_official: l1.affirming_official }).then(setL1).catch(console.error)
                  }
                />
              </label>
              <label style={{ fontSize: 13 }}>
                Affirming Official:{" "}
                <input
                  type="text"
                  value={l1.affirming_official}
                  placeholder="Name / title"
                  style={{ width: 220 }}
                  onChange={(e) =>
                    api.putL1Assessment({ status_date: l1.status_date, affirming_official: e.target.value }).then(setL1).catch(console.error)
                  }
                />
              </label>
              <button type="button" className="btn btn-secondary" onClick={copyL1Entry}>
                Copy SPRS entry summary
              </button>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: 140 }}>Practice</th>
                  <th>Safeguard</th>
                  <th style={{ width: 140 }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {l1.rows.map((r) => (
                  <tr key={r.id}>
                    <td className="muted">{r.id}</td>
                    <td>{r.title}</td>
                    <td>
                      <select value={r.status} onChange={(e) => setL1Status(r.id, e.target.value)}>
                        <option value="NOT MET">NOT MET</option>
                        <option value="MET">MET</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {(data.blockers || []).map((b) => (
        <div key={b} className="banner error">{b}</div>
      ))}

      {!data.self_ready && data.sprs_score >= 80 && data.open_critical_count > 0 && (
        <div className="banner info">
          SPRS meets the ≥80 target, but {data.open_critical_count} five-point control
          {data.open_critical_count === 1 ? "" : "s"} still {data.open_critical_count === 1 ? "is" : "are"} not MET,
          N/A, or inherited. Self-ready requires closing those gaps — a passing score alone does not clear them.
        </div>
      )}

      {!data.self_ready && !(data.sprs_score >= 80 && data.open_critical_count > 0) && (
        <div className="banner warning">
          Not self-ready yet — complete checklist items and fix 5-point gaps on{" "}
          <Link to="/controls">Controls</Link>.
        </div>
      )}
      {data.self_ready && (
        <div className="banner success">Meets self-assessment heuristics for a C3PAO scheduling discussion.</div>
      )}

      {data.poam_eligibility && (
        <div className={`banner ${data.poam_eligibility.eligible ? "success" : "warning"}`}>
          <strong>32 CFR 170.21 conditional status:</strong>{" "}
          {data.poam_eligibility.eligible ? "POA&M-eligible" : "not currently POA&M-eligible"}.{" "}
          {data.poam_eligibility.reason} ({data.poam_eligibility.closeout_days}-day POA&amp;M closeout).
        </div>
      )}
      {typeof data.unanswered_count === "number" && data.unanswered_count > 0 && (
        <div className="banner error">
          {data.unanswered_count} scoped control{data.unanswered_count === 1 ? "" : "s"} unanswered — scored as NOT
          STARTED. Your real SPRS may be higher once they are assessed (honest scoring; nothing is silently skipped).
        </div>
      )}

      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">SPRS score</div>
          <div className="stat-value">{data.sprs_score}/110</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Self-ready</div>
          <div className="stat-value">{data.self_ready ? "Yes" : "No"}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Critical gaps</div>
          <div className="stat-value">{data.open_critical_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">800-171A coverage</div>
          <div className="stat-value">{data.objective_coverage.pct}%</div>
          {data.objective_coverage.missing_sample?.length > 0 && (
            <p className="muted stat-footnote">
              Sample without narrative or E/I/T: {data.objective_coverage.missing_sample.join(", ")}
            </p>
          )}
        </div>
        {typeof data.assessment_ready_count === "number" && (
          <div className="stat-card">
            <div className="stat-label">Assessment-ready (MET + evidence)</div>
            <div className="stat-value">{data.assessment_ready_count}/{data.sprs_detail?.answered_count ?? "—"}</div>
          </div>
        )}
        {review && (
          <div className="stat-card">
            <div className="stat-label">Package quality</div>
            <div className="stat-value">{review.review_score}%</div>
          </div>
        )}
      </div>

      <div className="readiness-sections panel-stack">
        <h3 className="page-section-heading">Readiness status</h3>
        <div className="panel readiness-checklist-panel">
          <div className="panel-header">
            <strong>Checklist</strong>
            <span className="muted">
              {data.checklist.filter((c) => c.done).length}/{data.checklist.length} complete
            </span>
          </div>
          <div className="panel-body">
            <ul className="checklist">
              {data.checklist.map((item) => (
                <li
                  key={item.item}
                  className={[
                    item.done ? "done" : "",
                    !item.done && item.blocks_self_ready ? "blocker" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  <span className="checklist-mark" aria-hidden>{item.done ? "✓" : "—"}</span>
                  <div>
                    <strong>{item.item}</strong>
                    <div className="muted">{item.detail}</div>
                    {item.note && <div className="checklist-note">{item.note}</div>}
                    {item.control_ids && item.control_ids.length > 0 && (
                      <div className="priority-chips checklist-control-links">
                        {item.control_ids.map((cid) => (
                          <Link key={cid} className="priority-chip" to={`/controls/${encodeURIComponent(cid)}`}>
                            {cid}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {(review || coverage) && (
          <div className="panel">
            <div className="panel-header">
              <strong>Package quality</strong>
              <span className="panel-header-meta">
                {review && (
                  <span className="muted">{review.review_score}%</span>
                )}
                {canExport && (
                  <span className="panel-header-links">
                    {review && <button type="button" className="btn-link" onClick={() => authenticatedDownload(apiUrl("/api/export/readiness-review"), "Readiness-Review.txt")}>Review report</button>}
                    {review && coverage && <span className="muted" aria-hidden>·</span>}
                    {coverage && <button type="button" className="btn-link" onClick={() => authenticatedDownload(apiUrl("/api/export/evidence-coverage"), "Evidence-Coverage.txt")}>Coverage report</button>}
                  </span>
                )}
              </span>
            </div>
            <div className="panel-body panel-subsections">
              {review && (
                <div>
                  <p className="muted package-quality-caption">Audit package check — not your SPRS score.</p>
                  <p className="package-quality-metrics">
                    MET with evidence: {review.evidence.with_evidence_count}/{review.evidence.met_count}
                    {review.high_count + review.medium_count > 0 && (
                      <> · {review.high_count + review.medium_count} issue{review.high_count + review.medium_count === 1 ? "" : "s"} to review</>
                    )}
                  </p>
                  {review.finding_summary && (
                    <PackageQualityFindings summary={review.finding_summary} />
                  )}
                </div>
              )}
              {coverage && (
                <div className={review ? "panel-subsection" : undefined}>
                  <div className="readiness-stat-grid">
                    {[
                      ["Audit readiness", coverage.audit_readiness],
                      ["Assessment", coverage.assessment_readiness],
                      ["Documentation", coverage.documentation_readiness],
                      ["Evidence", coverage.evidence_readiness],
                    ].map(([label, pct]) => (
                      <div key={label} className={`stat-card stat-${pctTone(Number(pct))}`}>
                        <div className="stat-label">{label}</div>
                        <div className="stat-value">{pct}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <h3 className="page-section-heading">SPRS &amp; gaps</h3>
        <div className="panel readiness-analytics-panel">
          <div className="panel-body panel-subsections">
            <div className={remediation && remediation.open_items > 0 ? "two-col" : undefined}>
              <div className="panel-subsection">
                <h4 className="panel-subsection-title">SPRS trend</h4>
                <SprsTrendChart history={remediation?.sprs_history ?? settings?.sprs_history ?? []} />
              </div>
              {remediation && remediation.open_items > 0 && (
                <div className="panel-subsection">
                  <h4 className="panel-subsection-title">POA&amp;M by severity</h4>
                  <SeverityChart counts={severityCounts} />
                </div>
              )}
            </div>

            {gapBars.length > 0 && (
              <div className="panel-subsection">
                <h4 className="panel-subsection-title">Open gaps by family</h4>
                <HorizontalBarChart rows={gapBars} />
              </div>
            )}

            {remediation && remediation.burndown.length > 0 && (
              <div className="panel-subsection">
                <h4 className="panel-subsection-title">SPRS burndown projection</h4>
                <BurndownChart
                  points={remediation.burndown}
                  currentScore={remediation.sprs_score}
                  targetScore={remediation.target_score}
                />
              </div>
            )}
          </div>
        </div>

        <h3 className="page-section-heading">SPRS what-if &amp; control ledger</h3>
        <div className="panel">
          <div className="panel-header">
            <strong>What-if simulator</strong>
            <button type="button" className="btn-link" onClick={() => setSimOpen(!simOpen)}>
              {simOpen ? "Collapse" : "Expand"}
            </button>
          </div>
          {simOpen && (
            <div className="panel-body">
              <div className="readiness-sim-row" style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <select value={simControl} onChange={(e) => setSimControl(e.target.value)} style={{ maxWidth: 220 }}>
                  <option value="">— Control —</option>
                  {ledger.map((r) => (
                    <option key={r.control_id} value={r.control_id}>
                      {r.control_id} ({r.weight} PT)
                    </option>
                  ))}
                </select>
                <select value={simStatus} onChange={(e) => setSimStatus(e.target.value)}>
                  {["NOT MET", "PARTIALLY MET", "PLANNED", "IN PROGRESS", "NOT STARTED", "MET"].map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  disabled={simBusy || !simControl}
                  onClick={async () => {
                    setSimBusy(true);
                    try {
                      setSimResult(await api.sprsSimulate([{ control_id: simControl, status: simStatus }]));
                    } finally {
                      setSimBusy(false);
                    }
                  }}
                >
                  {simBusy ? "Simulating…" : "Simulate"}
                </button>
                {simResult && (
                  <span className={simResult.delta < 0 ? "banner danger" : "banner success"} style={{ margin: 0, padding: "4px 10px" }}>
                    {simControl} → {simResult.current_score} → {simResult.projected_score} ({simResult.delta >= 0 ? "+" : ""}{simResult.delta} pts)
                  </span>
                )}
              </div>
              <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
                Toggle a control's status to preview its SPRS impact before changing anything.
              </p>
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-header">
            <strong>Control ledger</strong>
            <span className="muted">{ledger.length} scoped</span>
            <button type="button" className="btn-link" onClick={() => setLedgerOpen(!ledgerOpen)}>
              {ledgerOpen ? "Collapse" : "Expand"}
            </button>
          </div>
          {ledgerOpen && (
            <div className="panel-body">
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Control</th>
                      <th>Weight</th>
                      <th>Status</th>
                      <th>Deduction</th>
                      <th>Evidence</th>
                      <th>Assessment-ready</th>
                      <th>POA&amp;M-eligible</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ledger.map((row) => (
                      <tr key={row.control_id}>
                        <td><Link to={`/controls/${encodeURIComponent(row.control_id)}`}>{row.control_id}</Link></td>
                        <td>{row.weight} PT</td>
                        <td>{row.status}</td>
                        <td>{row.deduction > 0 ? `−${row.deduction}` : "0"}</td>
                        <td>{row.has_evidence ? "✓" : "—"}</td>
                        <td>{row.assessment_ready ? "✓" : "—"}</td>
                        <td>{row.poam_eligible ? "✓" : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {gapRows.length > 0 && remediation && (
          <>
            <h3 className="page-section-heading">Remediation</h3>
            <div className="panel">
              <div className="panel-header">
                <strong>Open gaps</strong>
                <span className="muted">5-point controls first</span>
              </div>
              <div className="panel-body">
                <div className="stats stats-compact remediation-gap-stats">
                  <div className="stat-card">
                    <div className="stat-label">Remediation budget</div>
                    <div className="stat-value">${remediation.total_cost.toLocaleString()}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Unowned gaps</div>
                    <div className="stat-value">{remediation.unowned_gaps}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Open items</div>
                    <div className="stat-value">{remediation.open_items}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Critical risks</div>
                    <div className="stat-value">{remediation.critical_count}</div>
                  </div>
                </div>
                <div className="data-table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Control</th>
                        <th>Weight</th>
                        <th>Difficulty</th>
                        <th>Severity</th>
                        <th>Owner</th>
                        <th>Target</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {gapRows.map((row) => (
                        <tr
                          key={row.control_id}
                          className={row.overdue ? "row-overdue" : row.due_soon ? "row-due-soon" : undefined}
                        >
                          <td>
                            <Link to={`/controls/${encodeURIComponent(row.control_id)}`}>{row.control_id}</Link>
                          </td>
                          <td>{row.weight != null ? `${row.weight} PT` : "—"}</td>
                          <td>{row.difficulty ?? "—"}</td>
                          <td>{row.severity}</td>
                          <td>{row.owner}</td>
                          <td>{row.target_date}</td>
                          <td>{row.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}

        <h3 className="page-section-heading">Export</h3>
        <SprsEntryCopy canDownload={canExport} />

        <div className="panel">
          <div className="panel-header"><strong>Audit package</strong></div>
          <div className="panel-body">
            <p className="muted">
              One zip: SSP, POA&M, SPRS summary, readiness reports, evidence folder, org assets.
            </p>
            {canExport ? (
            <button type="button" className="btn btn-primary" onClick={() => authenticatedDownload(apiUrl("/api/export/audit-package"), "Audit-Package.zip")}>
              Download audit package (.zip)
            </button>
            ) : (
            <p className="muted">Export disabled for your role.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
