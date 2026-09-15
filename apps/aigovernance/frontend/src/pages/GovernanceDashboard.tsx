import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Bell, Clock, AlertTriangle, ChevronDown, ChevronRight, ExternalLink, BarChart3 } from "lucide-react";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { FW_LABELS, AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";
import { EvidenceSummaryBadge } from "@shared/evidence-hub/EvidenceSummaryBadge";
import { apiUrl } from "@shared/apiPrefix";

const API = "/api/ai-governance";

interface ToolStats {
  total: number;
  high_risk?: number;
  production?: number;
  open?: number;
  overdue_regulatory?: number;
  approved?: number;
  draft?: number;
  assessed?: number;
  expired?: number;
}

interface FrameworkInfo {
  covered: number;
  total: number;
  coverage_pct: number;
  status: string;
}

interface CoverageData {
  overall_pct: number;
  overall_status: string;
  frameworks: Record<string, FrameworkInfo>;
}

interface OnboardingStep {
  id: string;
  label: string;
  done: boolean;
}

interface GovernanceData {
  total_systems: number;
  total_incidents: number;
  high_risk: number;
  production_systems: number;
  open_incidents: number;
  overdue_regulatory: number;
  framework_coverage: CoverageData;
  tools: Record<string, ToolStats>;
  onboarding?: {
    steps: OnboardingStep[];
    progress_pct: number;
  };
}

interface GapClause {
  framework: string;
  control_id: string;
  control: string;
  description: string;
  covered_count: number;
  total_systems: number;
  coverage_pct: number;
  status: string;
}

const TOOL_CONFIG: Record<string, { label: string; route: string; metrics: { key: string; label: string; color: string }[]; icon?: string }> = {
  systems: { label: "AI Systems", route: "/aigov/systems", metrics: [{ key: "total", label: "Total", color: "var(--primary)" }, { key: "high_risk", label: "High Risk", color: "var(--danger)" }, { key: "production", label: "In Production", color: "var(--success)" }] },
  incidents: { label: "Incidents", route: "/aigov/incidents", metrics: [{ key: "total", label: "Total", color: "var(--primary)" }, { key: "open", label: "Open", color: "var(--warning)" }, { key: "overdue_regulatory", label: "Overdue", color: "var(--danger)" }] },
  frias: { label: "FRIAs", route: "/aigov/frias", metrics: [{ key: "total", label: "Total", color: "var(--primary)" }, { key: "approved", label: "Approved", color: "var(--success)" }, { key: "draft", label: "Draft", color: "var(--muted)" }] },
  vendors: { label: "Vendors", route: "/aigov/vendors", metrics: [{ key: "total", label: "Total", color: "var(--primary)" }, { key: "assessed", label: "Assessed", color: "var(--success)" }] },
  review_cycles: { label: "Review Cycles", route: "/aigov/review-cycles", metrics: [{ key: "total", label: "Total", color: "var(--primary)" }, { key: "active", label: "Active", color: "var(--success)" }] },
};

export function GovernanceDashboardPage() {
  const { activeFrameworks, toggleFramework } = useActiveFrameworks();
  const [data, setData] = useState<GovernanceData | null>(null);
  const [clauses, setClauses] = useState<GapClause[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [reminders, setReminders] = useState<any>(null);
  const [frameworkTab, setFrameworkTab] = useState(() => activeFrameworks[0] || "eu_ai_act");
  const [expandedClause, setExpandedClause] = useState<string | null>(null);

  useEffect(() => {
    if (!activeFrameworks.includes(frameworkTab as any)) {
      setFrameworkTab(activeFrameworks[0] || "eu_ai_act");
    }
  }, [activeFrameworks]);

  useEffect(() => {
    fetch(`${API}/governance`).then((r) => r.json()).then(setData).catch(() => {});
    fetch(`${API}/gap-analysis`).then((r) => r.json()).then((d) => setClauses(d.results || [])).catch(() => {});
    fetch(apiUrl("/api/notifications")).then((r) => r.json()).then((d) => setNotifications(d.notifications || [])).catch(() => {});
    fetch(`${API}/reminders`).then((r) => r.json()).then(setReminders).catch(() => {});
  }, []);

  const filteredClauses = clauses.filter((c) => c.framework === frameworkTab);

  const activeFwEntries = activeFrameworks
    .map(k => data?.framework_coverage?.frameworks?.[k])
    .filter(Boolean) as FrameworkInfo[];
  const recalculatedOverallPct = activeFwEntries.length > 0
    ? Math.round(activeFwEntries.reduce((s, f) => s + f.covered, 0) / activeFwEntries.reduce((s, f) => s + f.total, 0) * 100)
    : 0;

  const statusColor = (s: string) =>
    s === "covered" ? "var(--success)" : s === "partial" ? "var(--warning)" : "var(--danger)";

  const statusBg = (s: string) =>
    s === "covered" ? "var(--success-soft, rgba(34,197,94,0.1))" : s === "partial" ? "var(--warning-soft, rgba(234,179,8,0.1))" : "var(--danger-soft, rgba(239,68,68,0.1))";
  const onboardingAllDone = data?.onboarding?.steps?.every?.(s => s.done) ?? false;

  return (
    <div className="panel-stack">
      <div className="page-intro">
        <h2 className="page-intro-title">Governance Dashboard</h2>
        <p className="page-intro-summary">Live control map -- aggregated from all tools, mapped to framework clauses.</p>
      </div>

      {onboardingAllDone && (
        <div className="banner success" style={{ marginBottom: 16 }}>
          All setup steps complete. Your AI governance framework is established.
          <Link to="/aigov/systems" className="btn-link" style={{ marginLeft: 8 }}>View Systems →</Link>
        </div>
      )}

      {data && (
        <>

          <div style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "center" }}>
            <span className="muted" style={{ fontSize: 11, fontWeight: 600 }}>Active frameworks:</span>
            {AI_GOV_FRAMEWORKS.map(fw => {
              const active = activeFrameworks.includes(fw.key);
              return (
                <button
                  key={fw.key}
                  className={`btn btn-sm ${active ? "btn-primary" : "btn-ghost"}`}
                  onClick={() => toggleFramework(fw.key)}
                  style={active ? { background: fw.color, borderColor: fw.color, color: "#fff" } : { color: fw.color }}
                >
                  {fw.label}
                </button>
              );
            })}
          </div>

          <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
            {Object.entries(data.tools).map(([key, stats]) => {
              const cfg = TOOL_CONFIG[key];
              if (!cfg) return null;
              const isOnline = stats.total > 0;
              return (
                <NavLink key={key} to={cfg.route} style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--surface)", textDecoration: "none", color: "inherit", fontSize: 12 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: isOnline ? "var(--success)" : "var(--danger)", flexShrink: 0 }} />
                  <span>{cfg.label}</span>
                  {isOnline && <span className="muted">({stats.total})</span>}
                </NavLink>
              );
            })}
            <EvidenceSummaryBadge frameworkId="AIGov" fwBase="/aigov" />
          </div>

          <div className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-header">
              <strong><BarChart3 size={14} style={{ display: "inline", marginRight: 6 }} />Framework Coverage</strong>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="muted" style={{ fontSize: 10 }}>{activeFrameworks.length < 3 ? activeFrameworks.length + "/3 active" : ""}</span>
                <span style={{ fontWeight: 700, fontSize: 18, color: recalculatedOverallPct >= 80 ? "var(--success)" : recalculatedOverallPct >= 30 ? "var(--warning)" : "var(--danger)" }}>
                  {recalculatedOverallPct}%
                </span>
              </div>
            </div>
            <div className="panel-body" style={{ padding: "0.75rem 1rem 1rem" }}>
              <div style={{ width: "100%", background: "var(--info-soft)", borderRadius: 6, height: 10, overflow: "hidden", marginBottom: 12 }}>
                <div style={{ width: `${recalculatedOverallPct}%`, height: "100%", borderRadius: 6, background: recalculatedOverallPct >= 80 ? "var(--success)" : recalculatedOverallPct >= 30 ? "var(--warning)" : "var(--danger)", transition: "width 0.5s" }} />
              </div>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                {Object.entries(data.framework_coverage.frameworks).filter(([key]) => activeFrameworks.includes(key as any)).map(([key, fw]) => (
                  <div key={key} style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                    <span style={{ fontWeight: 500 }}>{FW_LABELS[key] || key}</span>
                    <span style={{ fontWeight: 600, color: statusColor(fw.status) }}>{fw.coverage_pct}%</span>
                    <span className="muted">({fw.covered}/{fw.total})</span>
                  </div>
                ))}
              </div>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10, marginBottom: 16 }}>
            {Object.entries(data.tools).map(([key, stats]) => {
              const cfg = TOOL_CONFIG[key];
              if (!cfg) return null;
              return (
                <NavLink key={key} to={cfg.route} className="panel" style={{ padding: 14, textDecoration: "none", color: "inherit", display: "block" }}>
                  <div style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em", color: "var(--muted)", marginBottom: 6 }}>{cfg.label}</div>
                  <div style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>{stats.total || 0}</div>
                  <div style={{ display: "flex", gap: 8, fontSize: 11, flexWrap: "wrap" }}>
                    {cfg.metrics.map((m) => {
                      const val = (stats as any)[m.key];
                      if (val == null) return null;
                      return (
                        <span key={m.key}>
                          <span style={{ color: m.color, fontWeight: 600 }}>{val}</span>
                          <span className="muted"> {m.label}</span>
                        </span>
                      );
                    })}
                  </div>
                </NavLink>
              );
            })}
          </div>

          {data.onboarding && (() => {
            const steps = data.onboarding!.steps;
            const currentIdx = steps.findIndex(s => !s.done);
            const allDone = currentIdx === -1;
            const currentStep = allDone ? null : steps[currentIdx];
            const stepRoutes: Record<string, string> = {
              system: "/aigov/systems/new",
              classify: "/aigov/systems",
              conformity: "/aigov/systems",
              monitoring: "/aigov/review-cycles",
            };
            return (
              <>
                {!allDone && (
                  <section className="panel" style={{ borderLeft: "3px solid var(--primary)", marginBottom: 16 }}>
                    <div className="panel-body" style={{ paddingTop: 0 }}>
                      <details className="dashboard-details" style={{ background: "transparent", border: "none", borderRadius: 0, marginBottom: 0, boxShadow: "none" }}>
                        <summary style={{ display: "flex", alignItems: "center", gap: 10, padding: "0.25rem 2rem 0.25rem 0", fontWeight: 600, fontSize: 12.5, cursor: "pointer" }}>
                          <span>Your path</span>
                          <div style={{ flex: 1, maxWidth: 360, height: 6, background: "var(--border-subtle)", borderRadius: 4, overflow: "hidden" }}>
                            <div style={{ width: `${data.onboarding!.progress_pct}%`, height: "100%", background: "var(--primary)", borderRadius: 4, transition: "width 0.3s" }} />
                          </div>
                          <span style={{ fontSize: 12, color: "var(--text-muted)", flexShrink: 0 }}>{data.onboarding!.progress_pct}%</span>
                        </summary>
                        <div style={{ padding: "0.75rem 0 0" }}>
                          <ul className="checklist" style={{ marginBottom: 0 }}>
                            {steps.map((s) => {
                              const route = stepRoutes[s.id];
                              const isNext = !s.done && s.id === currentStep!.id;
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
                        {(() => {
                          const route = stepRoutes[currentStep!.id];
                          if (!route) return null;
                          if (currentStep!.id === "system") return <Link to={route} className="btn btn-primary btn-sm">Register a System →</Link>;
                          return <Link to={route} className="btn btn-primary btn-sm">Continue →</Link>;
                        })()}
                        <Link to="/aigov/systems" style={{ fontSize: 12.5, color: "var(--muted)" }}>Classify systems →</Link>
                      </div>
                    </div>
                  </section>
                )}
              </>
            );
          })()}

          <div className="panel">
            <div className="panel-header">
              <strong>Control Coverage</strong>
              <span className="muted">{filteredClauses.filter((c) => c.status === "covered").length}/{filteredClauses.length} covered</span>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              <div className="aigov-tabs" style={{ margin: "0.75rem 1rem" }}>
                {AI_GOV_FRAMEWORKS.filter(f => activeFrameworks.includes(f.key)).map((fw) => (
                  <button key={fw.key} className={`aigov-tab${frameworkTab === fw.key ? " aigov-tab--active" : ""}`} onClick={() => setFrameworkTab(fw.key)}>
                    {fw.label}
                  </button>
                ))}
              </div>
              <div>
                {filteredClauses.map((clause) => {
                  const isExpanded = expandedClause === clause.control_id;
                  return (
                    <div key={clause.control_id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                      <button
                        onClick={() => setExpandedClause(isExpanded ? null : clause.control_id)}
                        style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 16px", width: "100%", background: "none", border: "none", cursor: "pointer", textAlign: "left", color: "inherit", fontSize: 12 }}
                      >
                        <span style={{ width: 8, height: 8, borderRadius: "50%", flexShrink: 0, background: statusColor(clause.status) }} />
                        <span style={{ fontWeight: 500, minWidth: 60, fontFamily: "monospace" }}>{clause.control_id}</span>
                        <span style={{ flex: 1, minWidth: 0 }}>{clause.control}</span>
                        <span style={{ padding: "1px 8px", borderRadius: 4, fontSize: 10, fontWeight: 600, background: statusBg(clause.status), color: statusColor(clause.status) }}>
                          {clause.status === "covered" ? "Covered" : clause.status === "partial" ? "Partial" : "Gap"}
                        </span>
                        <span style={{ fontSize: 11, color: "var(--muted)", flexShrink: 0 }}>
                          {clause.coverage_pct}%
                        </span>
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      </button>
                      {isExpanded && (
                        <div style={{ padding: "0 16px 10px 40px", fontSize: 11, color: "var(--muted)" }}>
                          <p style={{ margin: "0 0 6px" }}>{clause.description}</p>
                          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                            <span>{clause.covered_count} of {clause.total_systems} systems mapped</span>
                            <NavLink to={`/aigov/gap-analysis?control=${clause.control_id}`} style={{ display: "inline-flex", alignItems: "center", gap: 4, color: "var(--primary)", textDecoration: "none" }}>
                              Gap analysis <ExternalLink size={11} />
                            </NavLink>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
                {filteredClauses.length === 0 && (
                  <p className="muted" style={{ padding: "1rem", fontSize: 12 }}>No clauses found for this framework.</p>
                )}
              </div>
            </div>
          </div>

        </>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        {notifications.length > 0 && (
          <div className="panel">
            <div className="panel-header">
              <strong><Bell size={14} style={{ display: "inline", marginRight: 6 }} />Recent Activity</strong>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              {notifications.slice(0, 5).map((n: any, i: number) => (
                <NavLink key={i} to={n.source === "system" ? `/aigov/systems/${n.source_id}` : `/aigov/incidents/${n.source_id}`}
                  style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", borderBottom: i < Math.min(notifications.length, 5) - 1 ? "1px solid var(--border-subtle)" : "none", textDecoration: "none", color: "inherit", fontSize: 12 }}>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: n.action?.includes("approved") ? "var(--success)" : n.action?.includes("rejected") ? "var(--danger)" : "var(--primary)", flexShrink: 0 }} />
                  <span style={{ flex: 1, minWidth: 0 }}>
                    <span style={{ fontWeight: 500 }}>{n.source_title}</span>
                    <span className="muted"> -- {n.detail || n.action?.replace(/_/g, " ") || ""}</span>
                  </span>
                  <span className="muted" style={{ fontSize: 11, flexShrink: 0 }}>{n.timestamp?.slice(0, 10)}</span>
                </NavLink>
              ))}
            </div>
          </div>
        )}

        {reminders && (reminders.overdue?.length > 0 || reminders.upcoming?.length > 0) && (
          <div className="panel">
            <div className="panel-header">
              <strong><Clock size={14} style={{ display: "inline", marginRight: 6 }} />Review Reminders</strong>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              {reminders.overdue?.map((r: any) => (
                <NavLink key={r.id} to={`/aigov/systems/${r.id}`} style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", fontSize: 12, color: "var(--danger)" }}>
                  <AlertTriangle size={14} /> <span style={{ fontWeight: 500 }}>{r.name}</span> -- Overdue by {Math.abs(r.days_overdue || 0)} days
                </NavLink>
              ))}
              {reminders.upcoming?.slice(0, 3).map((r: any) => (
                <NavLink key={r.id} to={`/aigov/systems/${r.id}`} style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", textDecoration: "none", color: "inherit", fontSize: 12 }}>
                  <Clock size={14} style={{ color: "var(--warning)" }} /> <span style={{ fontWeight: 500 }}>{r.name}</span> -- {r.days_until}d until review
                </NavLink>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
