import { Link, useLocation } from "react-router-dom";
import { useLayout } from "../Layout";
import PageIntro from "../components/PageIntro";
import { EmptyState, PageSkeleton } from "../components/ui/Skeleton";
import { EvidenceSummaryBadge } from "@shared/evidence-hub/EvidenceSummaryBadge";
import { useEffect, useState } from "react";
import { api, ReadinessTrendsResponse } from "../api";

export default function DashboardPage() {
  const { dashboard, apiError } = useLayout();
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  const steps = [
    { key: "welcome", label: "Welcome", href: "/welcome", actionLabel: "Learn more", details: "This guide walks you through 6 steps to prepare for a SOC 2 Type II audit.", done: true },
    { key: "org", label: "Organization Profile", href: "/organization", actionLabel: "Set up organization", details: "Define your organization name, system description, architecture, boundary, and team roles.", done: (dashboard?.org_name?.length ?? 0) > 0 },
    { key: "scoping", label: "TSC Scoping", href: "/scoping", actionLabel: "Select categories", details: "Choose which Trust Services Criteria categories apply — Security is always required.", done: dashboard?.scoping_completed ?? false },
    { key: "controls", label: "Assess Controls", href: "/criteria", actionLabel: "Assess controls", details: "Review each control, set status, add implementation narratives, and assign owners.", done: (dashboard?.controls_assessed ?? 0) > 0 },
    { key: "policies", label: "Create Policies", href: "/policies", actionLabel: "Create policies", details: "Create or upload policies covering Acceptable Use, Access Control, Incident Response, and more.", done: (dashboard?.policy_coverage?.policies_total ?? 0) > 0 },
    { key: "evidence", label: "Collect Evidence", href: "/evidence", actionLabel: "Upload evidence", details: "Upload screenshots, configs, and logs that demonstrate your controls in action.", done: (dashboard?.evidence_coverage_pct ?? 0) > 0 },
    { key: "readiness", label: "Review Readiness", href: "/readiness", actionLabel: "View readiness", details: "Check your readiness score, address open gaps, and prepare your audit package.", done: (dashboard?.readiness_pct ?? 0) > 0 },
  ];
  const doneCount = steps.filter(s => s.done).length;
  const stepsTotal = steps.length;
  const currentIdx = steps.findIndex(s => !s.done);
  const progress = Math.round((doneCount / stepsTotal) * 100);
  const allDone = currentIdx === -1;
  const currentStep = allDone ? null : steps[currentIdx];
  const [trends, setTrends] = useState<ReadinessTrendsResponse | null>(null);

  useEffect(() => {
    api.getReadinessTrends().then(setTrends).catch(() => {});
  }, []);

  if (apiError && !dashboard) {
    return <p className="muted">Fix the API connection above, then click Retry.</p>;
  }

  if (!dashboard) return <PageSkeleton variant="dashboard" />;

  const daysLeft = dashboard.active_audit_period
    ? Math.max(0, Math.ceil(
        (new Date(dashboard.active_audit_period.end_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      ))
    : null;

  const coveredCount = dashboard.coverage.filter((c) => c.has_evidence).length;
  const autoCount = dashboard.coverage.filter((c) => c.has_auto_evidence).length;

  return (
    <div className="page-stack">
      <PageIntro title="SOC 2 Readiness" />

      {allDone && (
        <div className="banner success" style={{ marginBottom: 16 }}>
          All setup steps complete. You're ready for your SOC 2 audit.
          <Link to={fwBase + "/readiness"} className="btn-link" style={{ marginLeft: 8 }}>Review Readiness →</Link>
        </div>
      )}

      <div className="dash-nav" style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        <Link to={fwBase + "/my-work"} className="dash-nav-item" style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          My Work
          <span style={{ fontWeight: 700, color: "var(--primary)" }}>{dashboard.open_gaps + dashboard.evidence_review_pending + dashboard.open_requests}</span>
          <span style={{ color: "var(--text-muted)", fontSize: 11 }}>→</span>
        </Link>
        <Link to={fwBase + "/priority-queue"} className="dash-nav-item" style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          Priority Queue
          <span style={{ fontWeight: 700, color: "var(--danger)" }}>{dashboard.open_gaps}</span>
          <span style={{ color: "var(--text-muted)", fontSize: 11 }}>→</span>
        </Link>
        <Link to={fwBase + "/readiness"} className="dash-nav-item" style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          Readiness
          <span style={{ fontWeight: 700, color: "var(--success)" }}>{dashboard.readiness_pct}%</span>
          <span style={{ color: "var(--text-muted)", fontSize: 11 }}>→</span>
        </Link>
        <Link to={fwBase + "/organization"} className="dash-nav-item" style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          Organization
          <span style={{ fontWeight: 700, color: "var(--warning)" }}>{dashboard.org_name ? "✓" : "—"}</span>
          <span style={{ color: "var(--text-muted)", fontSize: 11 }}>→</span>
        </Link>
        <EvidenceSummaryBadge frameworkId="SOC2" fwBase={fwBase} />
      </div>

      {dashboard.frozen_audit_period && (
        <div className="banner success">
          Evidence frozen for "{dashboard.frozen_audit_period.name}" — audit package ready.
        </div>
      )}

      <div className="stats stats-compact">
        <div className="stat-card">
          <div className="stat-label">Overall</div>
          <div className="stat-value">{dashboard.readiness_pct}%</div>
          <p className="muted">{dashboard.controls_met}/{dashboard.controls_total} criteria met</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">Open gaps</div>
          <div className="stat-value">{dashboard.open_gaps}</div>
          <p className="muted">Not met or not started</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">Open exceptions</div>
          <div className="stat-value">{dashboard.open_exceptions ?? 0}</div>
          <p className="muted">POA&M items</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active risks</div>
          <div className="stat-value">{dashboard.active_risks ?? 0}</div>
          <p className="muted">{(dashboard.critical_risks ?? 0) > 0 ? `${dashboard.critical_risks} critical` : "Risk register"}</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">Policy coverage</div>
          <div className="stat-value">{dashboard.policy_coverage?.coverage_pct ?? 0}%</div>
          <p className="muted">{dashboard.policy_coverage?.policies_total ?? 0} policies</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">PoF coverage</div>
          <div className="stat-value" style={{ color: (dashboard.pof_coverage_pct ?? 0) >= 80 ? "var(--success)" : (dashboard.pof_coverage_pct ?? 0) >= 50 ? "var(--warning)" : "var(--danger)" }}>{dashboard.pof_coverage_pct ?? 0}%</div>
          <p className="muted">{dashboard.pof_addressed ?? 0}/{dashboard.pof_applicable ?? 0} PoFs addressed</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">Test pass rate</div>
          <div className="stat-value">{dashboard.test_pass_rate ?? "—"}%</div>
          <p className="muted">{dashboard.test_pass ?? 0} passed, {dashboard.test_fail ?? 0} failed</p>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overdue tests</div>
          <div className="stat-value" style={{ color: (dashboard.overdue_tests ?? 0) > 0 ? "var(--danger)" : "var(--success)" }}>{dashboard.overdue_tests ?? 0}</div>
          <p className="muted">{dashboard.test_total ?? 0} total tests</p>
        </div>
      </div>

      {((dashboard?.critical_risks ?? 0) > 0) && (
        <div className="banner danger">
          {dashboard.critical_risks} risk(s) at critical level require immediate attention.
          <Link to={fwBase + "/risks"} className="btn-link">View Risks</Link>
        </div>
      )}

      {((dashboard?.material_findings ?? 0) > 0) && (
        <div className="banner danger">
          {dashboard.material_findings} material/major audit finding(s) require remediation.
          <Link to={fwBase + "/findings"} className="btn-link">View Findings</Link>
        </div>
      )}

      {((dashboard?.open_findings ?? 0) > 0) && !(dashboard?.material_findings ?? 0) && (
        <div className="banner warning">
          {dashboard.open_findings} open audit finding(s) pending remediation.
          <Link to={fwBase + "/findings"} className="btn-link">View Findings</Link>
        </div>
      )}

      {(dashboard.overdue_tests ?? 0) > 0 && (
        <div className="banner warning">
          {dashboard.overdue_tests} test(s) are past their due date.
          <Link to={fwBase + "/tests"} className="btn-link">View Tests</Link>
        </div>
      )}

      {dashboard.expired_exceptions > 0 && (
        <div className="banner danger">
          {dashboard.expired_exceptions} exception(s) have passed their review date.
          <Link to={fwBase + "/exceptions"} className="btn-link">Review</Link>
        </div>
      )}

      {daysLeft !== null && (
        <div className={`banner ${daysLeft <= 30 ? "warning" : "info"}`}>
          Audit period "{dashboard.active_audit_period!.name}" ends in <strong>{daysLeft} days</strong>{" "}
          ({dashboard.active_audit_period!.end_date}).
          <Link to={fwBase + "/audit"} className="btn-link">View</Link>
        </div>
      )}

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <strong>Readiness by trust service category</strong>
          </div>
          <div className="panel-body">
            {dashboard.category_readiness?.length ? (
              <div className="category-readiness-list">
                {dashboard.category_readiness.map((row) => (
                  <div key={row.category} className="category-readiness-row">
                    <div className="category-readiness-head">
                      <Link to={`${fwBase}/criteria?category=${encodeURIComponent(row.category)}`}>{row.category}</Link>
                      <span className="muted">{row.met}/{row.total} met · {row.readiness_pct}%</span>
                    </div>
                    <div className="freshness-bar-track">
                      <div
                        className="freshness-bar-fill"
                        style={{
                          width: `${row.readiness_pct}%`,
                          backgroundColor: row.readiness_pct >= 80 ? "var(--success)" : row.readiness_pct >= 50 ? "var(--warning)" : "var(--danger)",
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No criteria in catalog yet.</p>
            )}
          </div>
        </section>

        {trends && trends.trends.length >= 2 && (
          <section className="panel" style={{ gridColumn: "1 / -1" }}>
            <div className="panel-header">
              <strong>Readiness trend</strong>
              <span className="muted" style={{ fontSize: 12, marginLeft: 8 }}>
                {trends.count} snapshot{trends.count !== 1 ? "s" : ""} · {trends.improvement >= 0 ? "+" : ""}{trends.improvement}% change
              </span>
            </div>
            <div className="panel-body" style={{ paddingTop: 12 }}>
              <svg viewBox="0 0 600 120" style={{ width: "100%", height: 120 }}>
                {(() => {
                  const pts = trends.trends.map(t => t.readiness_pct);
                  const max = Math.max(...pts, 100);
                  const min = Math.min(...pts, 0);
                  const range = max - min || 1;
                  const w = 600 / (pts.length - 1);
                  const y = (v: number) => 100 - ((v - min) / range) * 80 - 10;
                  const line = pts.map((v, i) => `${i * w},${y(v)}`).join(" ");
                  return (
                    <>
                      <polyline fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinejoin="round" points={line} />
                      {pts.map((v, i) => (
                        <circle key={i} cx={i * w} cy={y(v)} r="3" fill="var(--primary)" />
                      ))}
                      <text x="0" y="16" fontSize="9" fill="var(--text-muted)">{Math.round(max)}%</text>
                      <text x="0" y="112" fontSize="9" fill="var(--text-muted)">{Math.round(min)}%</text>
                    </>
                  );
                })()}
              </svg>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
                {trends.trends.map((t, i) => (
                  <span key={i}>{t.timestamp.slice(5, 10)}</span>
                ))}
              </div>
            </div>
          </section>
        )}

        <section className="panel">
          <div className="panel-header">
            <strong>Evidence</strong>
            <Link to={`${fwBase}/evidence`} style={{ fontSize: 12, color: "var(--muted)", textDecoration: "none" }}>
              View details →
            </Link>
          </div>
          <div className="panel-body" style={{ display: "flex", flexDirection: "column", gap: 16, paddingTop: 12 }}>
            <div>
              <strong style={{ color: dashboard.evidence_coverage_pct >= 80 ? "var(--success)" : dashboard.evidence_coverage_pct >= 50 ? "var(--warning)" : "var(--danger)" }}>
                {dashboard.evidence_coverage_pct}%
              </strong>
              <span className="muted"> coverage · {coveredCount} criteria</span>
            </div>
            <div>
              <strong>{dashboard.auto_coverage_pct}%</strong>
              <span className="muted"> auto-collected ({autoCount} criteria)</span>
            </div>
            {Object.entries(dashboard.freshness || {}).length > 0 && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 24px", marginTop: 8 }}>
                {["fresh", "stale", "expired", "never"].map((key) => {
                  const val = (dashboard.freshness || {})[key] || 0;
                  const cap = key.charAt(0).toUpperCase() + key.slice(1);
                  return (
                    <div key={key} style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ color: key === "fresh" ? "var(--success)" : key === "stale" ? "var(--warning)" : key === "expired" ? "var(--danger)" : "var(--muted)" }}>{cap}</span>
                      <span style={{ color: val === 0 ? "var(--muted)" : undefined }}>{val}</span>
                    </div>
                  );
                })}
              </div>
            )}
            {dashboard.period_coverage && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                  <span><span className="muted">Period coverage — </span>{dashboard.period_coverage.period_name}</span>
                  <strong style={{ color: dashboard.period_coverage.coverage_pct >= 80 ? "var(--success)" : dashboard.period_coverage.coverage_pct >= 50 ? "var(--warning)" : "var(--danger)" }}>{dashboard.period_coverage.coverage_pct}%</strong>
                </div>
                <div className="freshness-bar-track" style={{ height: 8 }}>
                  <div
                    className="freshness-bar-fill"
                    style={{
                      width: `${dashboard.period_coverage.coverage_pct}%`,
                      height: "100%",
                      backgroundColor: dashboard.period_coverage.coverage_pct >= 80 ? "var(--success)" : dashboard.period_coverage.coverage_pct >= 50 ? "var(--warning)" : "var(--danger)",
                    }}
                  />
                </div>
                <p className="muted" style={{ marginTop: 4 }}>
                  {dashboard.period_coverage.controls_covered}/{dashboard.period_coverage.total_controls} criteria · {dashboard.period_coverage.start_date} → {dashboard.period_coverage.end_date}
                </p>
              </div>
            )}
          </div>
        </section>

      </div>

      {!allDone && (
        <section className="panel" style={{ borderLeft: "3px solid var(--primary)", marginBottom: 16 }}>
          <div className="panel-body" style={{ paddingTop: 0 }}>
            <details className="dashboard-details" style={{ background: "transparent", border: "none", borderRadius: 0, marginBottom: 0, boxShadow: "none" }}>
              <summary style={{ display: "flex", alignItems: "center", gap: 10, padding: "0.25rem 2rem 0.25rem 0", fontWeight: 600, fontSize: 12.5, cursor: "pointer" }}>
                <span>Your path</span>
                <div style={{ flex: 1, maxWidth: 360, height: 6, background: "var(--border-subtle)", borderRadius: 4, overflow: "hidden" }}>
                  <div style={{ width: `${progress}%`, height: "100%", background: "var(--primary)", borderRadius: 4, transition: "width 0.3s" }} />
                </div>
                <span style={{ fontSize: 12, color: "var(--text-muted)", flexShrink: 0 }}>{progress}%</span>
              </summary>
              <div style={{ padding: "0.75rem 0 0" }}>
                <ul className="checklist" style={{ marginBottom: 0 }}>
                  {steps.map((step) => {
                    const isNext = !step.done && step.key === currentStep!.key;
                    return (
                      <li key={step.key} className={step.done ? "done" : ""}>
                        <Link to={fwBase + step.href} className="checklist-link">
                          <span className="checklist-mark">{step.done ? "✓" : isNext ? "→" : "○"}</span>
                          <span style={{ fontWeight: isNext ? 600 : 400 }}>{step.label}</span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </details>
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
              <Link to={fwBase + currentStep!.href} className="btn btn-primary btn-sm">{currentStep!.actionLabel} →</Link>
              <Link to={fwBase + "/organization"} style={{ fontSize: 12.5, color: "var(--muted)" }}>Scoping questionnaire →</Link>
            </div>
          </div>
        </section>
      )}

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <strong>Recent activity</strong>
          </div>
          <div className="panel-body">
            {dashboard.recent_activity.length === 0 ? (
              <EmptyState compact title="No recent activity" />
            ) : (
              <ul className="activity-list">
                {dashboard.recent_activity.map((a, i) => (
                  <li key={i} className="activity-item">
                    <span className="activity-type">
                      {a.type === "evidence_uploaded" ? (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                      ) : a.type === "request_created" ? (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                      ) : (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                      )}
                    </span>
                    <span className="activity-text">
                      {a.type === "evidence_uploaded" && (
                        <>Evidence uploaded to <Link to={`${fwBase}/criteria/${encodeURIComponent(a.control_id!)}`}>{a.control_id}</Link></>
                      )}
                      {a.type === "status_change" && (
                        <>{a.control_id} → {a.status}</>
                      )}
                      {a.type === "request_created" && (
                        <>Request: {a.title}</>
                      )}
                    </span>
                    <span className="muted activity-time">{a.timestamp}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>

    </div>
  );
}
