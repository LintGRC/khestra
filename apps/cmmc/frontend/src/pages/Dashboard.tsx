import { Link, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { api, ActivityEntry, Analytics, CollectorHealthSummary, Journey, Remediation } from "../api";
import { useLayout } from "../Layout";
import DashboardHealthPanel from "../components/DashboardHealthPanel";
import PageIntro from "../components/PageIntro";
import FamilyProgress from "../components/FamilyProgress";
import { HorizontalBarChart } from "../components/ReadinessCharts";
import SprsTrendChart from "../components/SprsTrendChart";
import { exportTone, gapTone, pctTone, sprsTone } from "../lib/readinessTone";
import { PageSkeleton } from "../components/ui/Skeleton";
import { EvidenceSummaryBadge } from "@shared/evidence-hub/EvidenceSummaryBadge";

type SprsDetail = {
  final_score: number;
  breakdown?: Record<string, number>;
  critical_gaps?: string[];
};

export default function DashboardPage() {
  const { dashboard, apiError, canViewDashboard, settings } = useLayout();
  const [journey, setJourney] = useState<Journey | null>(null);
  const [sprsDetail, setSprsDetail] = useState<SprsDetail | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [remediation, setRemediation] = useState<Remediation | null>(null);
  const [alerts, setAlerts] = useState<Awaited<ReturnType<typeof api.alerts>> | null>(null);
  const [activity, setActivity] = useState<ActivityEntry[] | null>(null);
  const [collectorHealth, setCollectorHealth] = useState<CollectorHealthSummary | null>(null);

  useEffect(() => {
    if (!dashboard) return;
    const fetches: Promise<unknown>[] = [api.journey(), api.alerts(), api.remediation(), api.recentActivity(), api.collectorHealth()];
    if (canViewDashboard) {
      fetches.push(api.sprsDetail(), api.analytics());
    }
    Promise.allSettled(fetches).then((results) => {
      let i = 0;
      const j = results[i++];
      const a = results[i++];
      const rem = results[i++];
      const act = results[i++];
      const ch = results[i++];
      if (j.status === "fulfilled") setJourney(j.value as Journey);
      if (a.status === "fulfilled") setAlerts(a.value as Awaited<ReturnType<typeof api.alerts>>);
      if (rem.status === "fulfilled") setRemediation(rem.value as Remediation);
      if (act.status === "fulfilled") setActivity(act.value as ActivityEntry[]);
      if (ch.status === "fulfilled") setCollectorHealth(ch.value as CollectorHealthSummary);
      if (canViewDashboard) {
        const sd = results[i++];
        const an = results[i++];
        if (sd.status === "fulfilled") setSprsDetail(sd.value as SprsDetail);
        if (an.status === "fulfilled") setAnalytics(an.value as Analytics);
      }
    });
  }, [dashboard?.sprs_score, dashboard?.client_id, canViewDashboard]);

  const gapBars = useMemo(
    () => remediation?.gaps_by_family.slice(0, 8).map((r) => ({ label: r.family, value: r.count })) ?? [],
    [remediation],
  );

  if (apiError && !dashboard) {
    return <p className="muted">Fix the API connection above, then click Retry.</p>;
  }

  if (!dashboard) return <PageSkeleton variant="dashboard" />;

  const progress =
    dashboard.controls_total > 0
      ? Math.round((dashboard.controls_assessed / dashboard.controls_total) * 100)
      : 0;

  const pathProgress = journey?.progress_pct ?? progress;
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  return (
    <>
      <PageIntro view="Dashboard" />
      {journey && !journey.next_step && (
        <div className="banner success" style={{ marginBottom: 16 }}>
          All steps complete. Your assessment is ready for review.
          <Link to={fwBase + "/readiness"} className="btn-link" style={{ marginLeft: 8 }}>Review Readiness →</Link>
        </div>
      )}

      {(dashboard.export_stale || dashboard.blockers.length > 0 || (alerts?.poam_overdue?.length ?? 0) > 0) && (() => {
        const blockCount = dashboard.blockers.length;
        const overdueCount = alerts?.poam_overdue?.length ?? 0;
        const totalItems = blockCount + (dashboard.export_stale ? 1 : 0) + overdueCount;
        const summaryParts: string[] = [];
        if (blockCount > 0) summaryParts.push(`${blockCount} blocker${blockCount > 1 ? "s" : ""}`);
        if (dashboard.export_stale) summaryParts.push("stale export");
        if (overdueCount > 0) summaryParts.push(`${overdueCount} overdue POA&M`);
        const primaryAction = overdueCount > 0
          ? { to: fwBase + `/controls/${encodeURIComponent(alerts!.poam_overdue[0].control_id)}`, label: "Review gaps" }
          : { to: fwBase + "/export", label: "Rebuild SSP" };
        return (
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem",
            padding: "1rem 1.15rem", borderRadius: "var(--radius)", marginBottom: 16,
            background: "linear-gradient(135deg, #234a6e 0%, #1a3a5c 100%)",
            border: "1px solid rgba(255,255,255,0.08)", color: "#fff",
            boxShadow: "0 4px 16px rgba(15, 42, 66, 0.12)",
          }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ margin: "0 0 0.2rem", fontSize: "0.6875rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "rgba(255,255,255,0.75)" }}>Attention needed</p>
              <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600 }}>{totalItems} item{totalItems > 1 ? "s" : ""} require{totalItems === 1 ? "s" : ""} your attention</h3>
              <p style={{ margin: "0.25rem 0 0", fontSize: "0.875rem", color: "rgba(255,255,255,0.8)" }}>{summaryParts.join(" · ")}</p>
            </div>
            <Link to={primaryAction.to} style={{
              flexShrink: 0, alignSelf: "center",
              padding: "0.5rem 1rem", borderRadius: "var(--radius)", fontSize: "0.875rem",
              fontWeight: 600, textDecoration: "none",
              background: "#fff", color: "#1a3a5c",
            }}>{primaryAction.label}</Link>
          </div>
        );
      })()}

      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        <Link to={fwBase + "/controls"} style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          Controls
          <span style={{ fontWeight: 700, color: "var(--primary)" }}>{dashboard.controls_assessed}/{dashboard.controls_total}</span>
          <span style={{ color: "var(--muted)", fontSize: 11 }}>→</span>
        </Link>
        <Link to={fwBase + "/controls"} style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          Open Gaps
          <span style={{ fontWeight: 700, color: dashboard.open_gaps > 0 ? "var(--danger)" : "var(--success)" }}>{dashboard.open_gaps}</span>
          <span style={{ color: "var(--muted)", fontSize: 11 }}>→</span>
        </Link>
        <Link to={fwBase + "/readiness"} style={{ padding: "8px 16px", textDecoration: "none", background: "var(--surface)", borderRadius: 6, border: "1px solid var(--border-subtle)", display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 500, color: "var(--text)" }}>
          SPRS
          <span style={{ fontWeight: 700, color: dashboard.sprs_score >= 80 ? "var(--success)" : dashboard.sprs_score >= 50 ? "var(--warning)" : "var(--danger)" }}>{dashboard.sprs_score}/{dashboard.sprs_max}</span>
          <span style={{ color: "var(--muted)", fontSize: 11 }}>→</span>
        </Link>
        <EvidenceSummaryBadge frameworkId="CMMC" fwBase={fwBase} />
      </div>

      <div className="stats stats-compact">
        <div className={`stat-card stat-${sprsTone(dashboard.sprs_score)}`}>
          <div className="stat-label">SPRS score</div>
          <div className="stat-value">
            {dashboard.sprs_score}
            <span className="muted stat-denom">/{dashboard.sprs_max}</span>
          </div>
        </div>
        <div className={`stat-card stat-${pctTone(pathProgress)}`}>
          <div className="stat-label">Progress</div>
          <div className="stat-value">{pathProgress}%</div>
        </div>
        <div className={`stat-card stat-${gapTone(dashboard.open_gaps)}`}>
          <div className="stat-label">Open gaps</div>
          <div className="stat-value">{dashboard.open_gaps}</div>
        </div>
        <div className={`stat-card stat-${exportTone(dashboard.export_readiness_pct)}`}>
          <div className="stat-label">Export ready</div>
          <div className="stat-value">{dashboard.export_readiness_pct}%</div>
        </div>
        {collectorHealth && collectorHealth.total > 0 && (
          <div
            className={`stat-card stat-${collectorHealth.failing + collectorHealth.error === 0 ? 'ok' : collectorHealth.error > 0 ? 'danger' : 'warning'}`}
            style={{ cursor: "pointer" }}
            onClick={() => window.location.href = `${fwBase}/integrations`}
            title="View collector health"
          >
            <div className="stat-label">Auto checks</div>
            <div className="stat-value">
              {collectorHealth.failing + collectorHealth.error > 0
                ? `${collectorHealth.passing}/${collectorHealth.total} passing`
                : `${collectorHealth.passing} ok`}
            </div>
          </div>
        )}
      </div>

      <DashboardHealthPanel refreshKey={dashboard.client_id} />

      {journey?.next_step && (() => {
        const steps = journey.steps;
        const nextStep = journey.next_step!;
        const VIEW_ROUTES: Record<string, string> = {
          "System Profile": fwBase + "/organization",
          "Assessment": fwBase + "/controls",
          "Report Center": fwBase + "/export",
          "Pre-C3PAO Readiness": fwBase + "/readiness",
        };
        const nextRoute = VIEW_ROUTES[nextStep.view];
        return (
          <section className="panel" style={{ borderLeft: "3px solid var(--primary)", marginBottom: 16 }}>
            <div className="panel-body" style={{ paddingTop: 0 }}>
              <details className="dashboard-details" style={{ background: "transparent", border: "none", borderRadius: 0, marginBottom: 0, boxShadow: "none" }}>
                <summary style={{ display: "flex", alignItems: "center", gap: 10, padding: "0.25rem 2rem 0.25rem 0", fontWeight: 600, fontSize: 12.5, cursor: "pointer" }}>
                  <span>Your path</span>
                  <div style={{ flex: 1, maxWidth: 360, height: 6, background: "var(--border-subtle)", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ width: `${journey.progress_pct}%`, height: "100%", background: "var(--primary)", borderRadius: 4, transition: "width 0.3s" }} />
                  </div>
                  <span style={{ fontSize: 12, color: "var(--text-muted)", flexShrink: 0 }}>{journey.progress_pct}%</span>
                </summary>
                <div style={{ padding: "0.75rem 0 0" }}>
                  <ul className="checklist" style={{ marginBottom: 0 }}>
                    {steps.map((s) => {
                      const route = VIEW_ROUTES[s.view];
                      const isNext = !s.done && s.id === nextStep.id;
                      return (
                        <li key={s.id} className={s.done ? "done" : ""}>
                          {route ? (
                            <Link to={route} className="checklist-link">
                              <span className="checklist-mark">{s.done ? "✓" : isNext ? "→" : "○"}</span>
                              <span style={{ fontWeight: isNext ? 600 : 400 }}>{s.label}</span>
                            </Link>
                          ) : (
                            <>
                              <span className="checklist-mark">{s.done ? "✓" : "○"}</span>
                              <strong>{s.label}</strong>
                            </>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </details>
              <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
                {nextRoute && <Link to={nextRoute} className="btn btn-primary btn-sm">{nextStep.label} →</Link>}
                <Link to={fwBase + "/organization"} style={{ fontSize: 12.5, color: "var(--muted)" }}>Scoping questionnaire →</Link>
              </div>
            </div>
          </section>
        );
      })()}

      {canViewDashboard && (
        <details className="dashboard-details" open>
          <summary>More analytics</summary>
          <div className="dashboard-details-body panel-stack">
            <div className="panel">
              <div className="panel-header"><strong>SPRS trend</strong></div>
              <div className="panel-body">
                <SprsTrendChart history={settings?.sprs_history ?? []} />
              </div>
            </div>

            {gapBars.length > 0 && (
              <div className="panel">
                <div className="panel-header">
                  <strong>Open gaps by family</strong>
                  <span className="muted">{remediation?.open_items ?? 0} POA&amp;M items</span>
                </div>
                <div className="panel-body">
                  <HorizontalBarChart rows={gapBars} />
                </div>
              </div>
            )}

            {analytics && (
              <>
                {(analytics.sprs.critical_gaps.length > 0 ||
                  analytics.sprs.moderate_gaps.length > 0 ||
                  analytics.sprs.low_gaps.length > 0) && (
                  <div className="panel">
                    <div className="panel-header"><strong>Open gaps by weight</strong></div>
                    <div className="panel-body gap-columns">
                      {analytics.sprs.critical_gaps.length > 0 && (
                        <div>
                          <strong>5-point</strong>
                          <div className="priority-chips">
                            {analytics.sprs.critical_gaps.slice(0, 12).map((cid) => (
                              <Link key={cid} className="priority-chip" to={fwBase + `/controls/${encodeURIComponent(cid)}`}>{cid}</Link>
                            ))}
                          </div>
                        </div>
                      )}
                      {analytics.sprs.moderate_gaps.length > 0 && (
                        <div>
                          <strong>3-point</strong>
                          <div className="priority-chips">
                            {analytics.sprs.moderate_gaps.slice(0, 12).map((cid) => (
                              <Link key={cid} className="priority-chip" to={fwBase + `/controls/${encodeURIComponent(cid)}`}>{cid}</Link>
                            ))}
                          </div>
                        </div>
                      )}
                      {analytics.sprs.low_gaps.length > 0 && (
                        <div>
                          <strong>1-point</strong>
                          <div className="priority-chips">
                            {analytics.sprs.low_gaps.slice(0, 12).map((cid) => (
                              <Link key={cid} className="priority-chip" to={fwBase + `/controls/${encodeURIComponent(cid)}`}>{cid}</Link>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                <div className="panel">
                  <div className="panel-header"><strong>Progress by family</strong></div>
                  <div className="panel-body">
                    <FamilyProgress rows={analytics.family_progress} />
                  </div>
                </div>
              </>
            )}

            {sprsDetail?.breakdown && Object.keys(sprsDetail.breakdown).length > 0 && (
              <div className="panel">
                <div className="panel-header"><strong>SPRS breakdown</strong></div>
                <div className="panel-body">
                  <ul>
                    {Object.entries(sprsDetail.breakdown)
                      .filter(([, v]) => v)
                      .map(([label, pts]) => (
                        <li key={label}>
                          {label.replace(/_/g, " ")}: <strong>{pts}</strong>
                        </li>
                      ))}
                  </ul>
                </div>
              </div>
            )}

          </div>
        </details>
      )}

      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="panel-header">
          <strong>Recent activity</strong>
        </div>
        <div className="panel-body" style={{ padding: "8px 0" }}>
          {activity && activity.length > 0 ? (
            activity.map((e, i) => {
              const dotColor = e.type === "evidence_uploaded" ? "var(--primary)" : e.type === "status_change" ? "var(--warning)" : e.type === "comment_added" ? "var(--success)" : e.type === "export_created" ? "var(--muted)" : "var(--muted)";
              return (
                <div key={i} style={{ display: "flex", gap: 10, padding: "6px 16px", alignItems: "flex-start", fontSize: 13 }}>
                  <span style={{ flexShrink: 0, width: 8, height: 8, borderRadius: "50%", background: dotColor, marginTop: 6 }} />
                  <span style={{ flex: 1, minWidth: 0 }}>{e.message}</span>
                  <span className="muted" style={{ flexShrink: 0, fontSize: 11, whiteSpace: "nowrap" }}>{e.timestamp}</span>
                </div>
              );
            })
          ) : (
            <p className="muted" style={{ padding: "6px 16px", fontSize: 13, margin: 0 }}>No recent activity yet.</p>
          )}
        </div>
      </div>

      {!canViewDashboard && settings && (
        <p className="muted">Detailed analytics hidden for {settings.current_role}.</p>
      )}

      <p style={{ marginTop: 20 }}>
        <Link to={fwBase + "/effectiveness"} className="btn-link">
          See program effectiveness →
        </Link>
      </p>
    </>
  );
}
