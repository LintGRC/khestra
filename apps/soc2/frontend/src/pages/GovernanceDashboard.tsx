import { Link } from "react-router-dom";
import { useLayout } from "../Layout";
import { PageSkeleton } from "../components/ui/Skeleton";
function ChartIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>; }
function ShieldIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>; }
function AlertIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>; }
function FileIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>; }
function BuildingIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><line x1="9" y1="6" x2="9" y2="6.01"/><line x1="15" y1="6" x2="15" y2="6.01"/><line x1="9" y1="10" x2="9" y2="10.01"/><line x1="15" y1="10" x2="15" y2="10.01"/><line x1="9" y1="14" x2="9" y2="14.01"/><line x1="15" y1="14" x2="15" y2="14.01"/></svg>; }
function ActivityIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>; }

const TSC_LABELS: Record<string, string> = {
  Security: "Security",
  Availability: "Availability",
  "Processing Integrity": "Processing Integrity",
  Confidentiality: "Confidentiality",
  Privacy: "Privacy",
};

export default function GovernanceDashboardPage() {
  const { dashboard, apiError } = useLayout();

  if (apiError && !dashboard) {
    return <p className="muted">Fix the API connection above, then click Retry.</p>;
  }

  if (!dashboard) return <PageSkeleton variant="dashboard" />;

  const coveredCount = dashboard.coverage.filter((c) => c.has_evidence).length;
  const metCount = dashboard.coverage.filter((c) => c.status === "MET" || c.status === "NOT APPLICABLE" || c.status === "INHERITED").length;
  const notMetCount = dashboard.coverage.filter((c) => c.status === "NOT MET" || c.status === "NOT STARTED").length;
  const inProgressCount = dashboard.controls_total - metCount - notMetCount;
  const staleCount = (dashboard.freshness?.stale ?? 0) + (dashboard.freshness?.expired ?? 0);

  const overallScore = dashboard.readiness_pct;

  const statusColor = (s: string) =>
    s === "MET" || s === "NOT APPLICABLE" || s === "INHERITED" ? "var(--success)" : s === "NOT MET" || s === "NOT STARTED" ? "var(--danger)" : "var(--warning)";

  const statusBg = (s: string) =>
    s === "MET" || s === "NOT APPLICABLE" || s === "INHERITED" ? "var(--success-soft, rgba(34,197,94,0.1))" : s === "NOT MET" || s === "NOT STARTED" ? "var(--danger-soft, rgba(239,68,68,0.1))" : "var(--warning-soft, rgba(234,179,8,0.1))";

  const statusLabel = (s: string) =>
    s === "MET" || s === "NOT APPLICABLE" || s === "INHERITED" ? "Met" : s === "NOT MET" || s === "NOT STARTED" ? "Gap" : "In Progress";

  const controlsByCategory = dashboard.coverage.reduce<Record<string, { total: number; met: number }>>((acc, c) => {
    const cat = c.category || "Other";
    if (!acc[cat]) acc[cat] = { total: 0, met: 0 };
    acc[cat].total++;
    if (c.status === "MET" || c.status === "NOT APPLICABLE" || c.status === "INHERITED") acc[cat].met++;
    return acc;
  }, {});

  const toolCards = [
    { label: "Criteria", route: "/criteria", total: dashboard.controls_total, sub: `${coveredCount} with evidence`, subColor: "var(--primary)", icon: ShieldIcon },
    { label: "Risks", route: "/risks", total: dashboard.active_risks || 0, sub: `${dashboard.critical_risks || 0} critical`, subColor: dashboard.critical_risks ? "var(--danger)" : "var(--muted)", icon: AlertIcon },
    { label: "Exceptions", route: "/exceptions", total: dashboard.open_exceptions || 0, sub: `${dashboard.expired_exceptions || 0} expired`, subColor: dashboard.expired_exceptions ? "var(--danger)" : "var(--muted)", icon: ActivityIcon },
    { label: "Policies", route: "/policies", total: dashboard.policy_coverage?.policies_total || 0, sub: `${dashboard.policy_coverage?.coverage_pct || 0}% coverage`, subColor: "var(--success)", icon: FileIcon },
    { label: "Findings", route: "/findings", total: dashboard.open_findings || 0, sub: `${dashboard.material_findings || 0} material`, subColor: dashboard.material_findings ? "var(--danger)" : "var(--muted)", icon: BuildingIcon },
    { label: "Evidence", route: "/evidence", total: dashboard.evidence_total || 0, sub: `${dashboard.evidence_review_pending || 0} pending review`, subColor: dashboard.evidence_review_pending ? "var(--warning)" : "var(--muted)", icon: ChartIcon },
  ];

  return (
    <div className="page-stack">
      <div className="page-intro">
        <h1>Governance Dashboard</h1>
        <p>SOC 2 readiness mapped to framework clauses -- aggregated from all modules.</p>
      </div>

      {/* Tool connection badges */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {toolCards.map((t) => {
          const isOnline = t.total > 0;
          return (
            <Link key={t.label} to={t.route} style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--surface)", textDecoration: "none", color: "inherit", fontSize: 12 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: isOnline ? "var(--success)" : "var(--danger)", flexShrink: 0 }} />
              <span>{t.label}</span>
              {isOnline && <span className="muted">({t.total})</span>}
            </Link>
          );
        })}
      </div>

      {/* Overall Score */}
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="panel-header">
          <strong>Overall Readiness</strong>
          <span style={{ fontWeight: 700, fontSize: 18, color: overallScore >= 80 ? "var(--success)" : overallScore >= 50 ? "var(--warning)" : "var(--danger)" }}>
            {overallScore}%
          </span>
        </div>
        <div className="panel-body" style={{ padding: "0.75rem 1rem 1rem" }}>
          <div style={{ width: "100%", background: "var(--info-soft)", borderRadius: 6, height: 10, overflow: "hidden", marginBottom: 12 }}>
            <div style={{ width: `${overallScore}%`, height: "100%", borderRadius: 6, background: overallScore >= 80 ? "var(--success)" : overallScore >= 50 ? "var(--warning)" : "var(--danger)", transition: "width 0.5s" }} />
          </div>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap", fontSize: 12 }}>
            <span><strong>{metCount}</strong> met</span>
            <span><strong>{inProgressCount}</strong> in progress</span>
            <span><strong>{notMetCount}</strong> gaps</span>
            <span><strong>{dashboard.controls_total}</strong> total controls</span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10, marginBottom: 16 }}>
        {toolCards.map((t) => {
          const Icon = t.icon;
          return (
            <Link key={t.label} to={t.route} className="panel" style={{ padding: 14, textDecoration: "none", color: "inherit", display: "block" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <span style={{ color: "var(--primary)", display: "flex" }}><Icon /></span>
                <div style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em", color: "var(--muted)" }}>{t.label}</div>
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 2 }}>{t.total}</div>
              <div style={{ fontSize: 11, color: t.subColor }}>{t.sub}</div>
            </Link>
          );
        })}
      </div>

      {/* Control Status Distribution */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div className="panel">
          <div className="panel-header">
            <strong>Control Status by Category</strong>
          </div>
          <div className="panel-body" style={{ padding: "0.75rem 1rem" }}>
            {Object.entries(controlsByCategory).length === 0 ? (
              <p className="muted" style={{ fontSize: 12 }}>No controls loaded.</p>
            ) : (
              Object.entries(controlsByCategory).map(([cat, data]) => {
                const pct = data.total > 0 ? Math.round((data.met / data.total) * 100) : 0;
                return (
                  <div key={cat} style={{ marginBottom: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
                      <Link to={`/criteria?category=${encodeURIComponent(cat)}`} style={{ fontWeight: 500, color: "inherit", textDecoration: "none" }}>{cat}</Link>
                      <span className="muted">{data.met}/{data.total} ({pct}%)</span>
                    </div>
                    <div style={{ width: "100%", background: "var(--info-soft)", borderRadius: 4, height: 6, overflow: "hidden" }}>
                      <div style={{ width: `${pct}%`, height: "100%", borderRadius: 4, background: pct >= 80 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)" }} />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <strong>Status Breakdown</strong>
          </div>
          <div className="panel-body" style={{ padding: "0.75rem 1rem" }}>
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
              <span style={{ padding: "2px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600, background: "var(--success-soft, rgba(34,197,94,0.1))", color: "var(--success)" }}>{metCount} Met</span>
              <span style={{ padding: "2px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600, background: "var(--warning-soft, rgba(234,179,8,0.1))", color: "var(--warning)" }}>{inProgressCount} In Progress</span>
              <span style={{ padding: "2px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600, background: "var(--danger-soft, rgba(239,68,68,0.1))", color: "var(--danger)" }}>{notMetCount} Gaps</span>
            </div>
            {dashboard.coverage.slice(0, 20).map((c) => (
              <Link key={c.id} to={`/criteria/${encodeURIComponent(c.id)}`} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 0", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", color: "inherit", fontSize: 12 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", flexShrink: 0, background: statusColor(c.status) }} />
                <span style={{ fontFamily: "monospace", fontSize: 10, minWidth: 50, flexShrink: 0 }}>{c.id}</span>
                <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.category || ""}</span>
                <span style={{ padding: "1px 6px", borderRadius: 3, fontSize: 9, fontWeight: 600, background: statusBg(c.status), color: statusColor(c.status), flexShrink: 0 }}>{statusLabel(c.status)}</span>
              </Link>
            ))}
            {dashboard.coverage.length > 20 && (
              <Link to="/criteria" style={{ display: "block", textAlign: "center", fontSize: 11, color: "var(--primary)", marginTop: 8, textDecoration: "none" }}>
                View all {dashboard.coverage.length} controls
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Readiness by Category & Freshness */}
      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <strong>Readiness by Trust Service Category</strong>
          </div>
          <div className="panel-body">
            {dashboard.category_readiness?.length ? (
              <div className="category-readiness-list">
                {dashboard.category_readiness.map((row) => (
                  <div key={row.category} className="category-readiness-row">
                    <div className="category-readiness-head">
                      <Link to={`/criteria?category=${encodeURIComponent(row.category)}`}>{TSC_LABELS[row.category] || row.category}</Link>
                      <span className="muted">{row.met}/{row.total} met &middot; {row.readiness_pct}%</span>
                    </div>
                    <div className="freshness-bar-track">
                      <div className="freshness-bar-fill" style={{
                        width: `${row.readiness_pct}%`,
                        backgroundColor: row.readiness_pct >= 80 ? "var(--success)" : row.readiness_pct >= 50 ? "var(--warning)" : "var(--danger)",
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No criteria in catalog yet.</p>
            )}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <strong>Evidence Freshness</strong>
          </div>
          <div className="panel-body">
            {Object.entries(dashboard.freshness || {}).length === 0 ? (
              <p className="muted">No evidence collected yet.</p>
            ) : (
              <div className="freshness-bars">
                {["fresh", "stale", "expired", "never"].map((key) => {
                  const val = (dashboard.freshness || {})[key] || 0;
                  if (val === 0) return null;
                  const pct = Math.round((val / dashboard.controls_total) * 100);
                  const fColor = key === "fresh" ? "var(--success)" : key === "stale" ? "var(--warning)" : key === "expired" ? "var(--danger)" : "var(--muted)";
                  return (
                    <div key={key} className="freshness-row">
                      <span className="freshness-label">{key}</span>
                      <div className="freshness-bar-track">
                        <div className="freshness-bar-fill" style={{ width: `${pct}%`, backgroundColor: fColor }} />
                      </div>
                      <span className="freshness-count">{val}</span>
                    </div>
                  );
                })}
              </div>
            )}
            <div style={{ marginTop: 10, fontSize: 12, display: "flex", gap: 12 }}>
              <Link to="/evidence" style={{ color: "var(--primary)", textDecoration: "none" }}>Browse evidence</Link>
              {staleCount > 0 && <Link to="/criteria" style={{ color: "var(--danger)", textDecoration: "none" }}>{staleCount} need refresh</Link>}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
