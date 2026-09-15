import { LayoutDashboard, Shield, Scale, Activity, Clock, FileText, BookOpen, Building2, Box, FolderOpen, AlertTriangle, Users, History, ClipboardCheck, Clipboard, Search, GraduationCap, Bell, Calendar } from "lucide-react";import { NavLink, Outlet, useLocation, useOutletContext } from "react-router-dom";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { useScrollRestoration } from "@shared/scroll-restoration/useScrollRestoration";
import { getApiPrefix } from "@shared/apiPrefix";
import { peekLayoutCache } from "@shared/frameworkLayoutCache";
import SidebarShell, { SidebarProvider, SidebarToggle } from "@shared/sidebar/SidebarShell";
import { api, Dashboard, DemoStatus, Settings, NotificationsResponse } from "./api";
import { useAuth } from "@shared/authContext";

import WorkspaceDrawer from "@shared/settings/WorkspaceDrawer";
import { PageSkeleton } from "./components/ui/Skeleton";

export type LayoutContext = {
  dashboard: Dashboard | null;
  settings: Settings | null;
  refreshDashboard: () => Promise<void>;
  canEdit: boolean;
  apiError: string | null;
};

export function useLayout() {
  return useOutletContext<LayoutContext>();
}

type LayoutProps = {
  frameworkSwitcher?: ReactNode;
  active?: boolean;
};

function layoutBootstrap() {
  return peekLayoutCache(getApiPrefix());
}

export default function Layout({ frameworkSwitcher, active = true }: LayoutProps = {}) {
  const { ready: authReady, enabled: authEnabled, authenticated, displayName, email, login, logout } =
    useAuth();
  useScrollRestoration();
  const boot = layoutBootstrap();
  const [dashboard, setDashboard] = useState<Dashboard | null>(
    () => (boot?.dashboard as Dashboard | undefined) ?? null,
  );
  const [settings, setSettings] = useState<Settings | null>(
    () => (boot?.settings as Settings | undefined) ?? null,
  );
  const [demoStatus, setDemoStatus] = useState<DemoStatus | null>(
    () => (boot?.demoStatus as DemoStatus | undefined) ?? null,
  );
  const [demoLoading, setDemoLoading] = useState(false);
  const [clearingDemo, setClearingDemo] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [reviewerName, setReviewerName] = useState("");
  const [initialLoadDone, setInitialLoadDone] = useState(Boolean(boot?.dashboard));
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  const [complianceOpen, setComplianceOpen] = useState(true);
  const [resourcesOpen, setResourcesOpen] = useState(true);
  const [nots, setNots] = useState<NotificationsResponse | null>(null);
  const [showNots, setShowNots] = useState(false);

  const refreshNots = useCallback(async () => {
    try { setNots(await api.getNotifications()); } catch { setNots(null); }
  }, []);

  useEffect(() => {
    refreshNots();
    const interval = setInterval(refreshNots, 60000);
    return () => clearInterval(interval);
  }, [refreshNots]);

  const refreshDashboard = useCallback(async () => {
    setApiError(null);
    const [dashResult, settingsResult, demoResult] = await Promise.allSettled([
      api.dashboard(),
      api.settings(),
      api.demoStatus(),
    ]);
    if (dashResult.status === "fulfilled") setDashboard(dashResult.value);
    else {
      setDashboard(null);
      setApiError(
        "Cannot reach the SOC 2 API. From khestra root run ./run-dev.sh (platform on :5173) " +
          "or apps/soc2/run-dev.sh (standalone on :5175).",
      );
    }
    if (settingsResult.status === "fulfilled") {
      setSettings(settingsResult.value);
      setReviewerName(settingsResult.value.current_user_name || "");
    }
    if (demoResult.status === "fulfilled") setDemoStatus(demoResult.value);
  }, []);

  const saveReviewerName = async () => {
    const name = reviewerName.trim();
    if (name === (settings?.current_user_name || "")) return;
    try {
      await api.patchUserName(name);
      await refreshDashboard();
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (!active || !authReady) return;
    if (authEnabled && !authenticated) return;
    refreshDashboard()
      .catch(console.error)
      .finally(() => setInitialLoadDone(true));
  }, [active, authReady, authEnabled, authenticated, refreshDashboard]);

  const loadDemo = async () => {
    setDemoLoading(true);
    try {
      await api.loadDemo("northwind");
      await refreshDashboard();
    } finally {
      setDemoLoading(false);
    }
  };

  const clearDemo = async () => {
    if (!window.confirm("Exit the sample workspace and start blank for your organization?")) return;
    setClearingDemo(true);
    try {
      await api.clearDemo();
      await refreshDashboard();
    } catch (e) {
      console.error("clearDemo failed", e);
      alert("Failed to exit demo. Check the console for details.");
    } finally {
      setClearingDemo(false);
    }
  };

  const switchClient = async (clientId: string) => {
    await api.activateClient(clientId);
    await refreshDashboard();
  };

  const patchRole = async (role: string) => {
    await api.patchRole(role);
    await refreshDashboard();
  };

  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  const canEdit = (settings?.capabilities?.edit_controls ?? true) && !settings?.workspace_locked;

  const needsAttention =
    (dashboard?.evidence_review_pending ?? 0) > 0 ||
    (dashboard?.open_requests ?? 0) > 0;

  if (!authReady) {
    return (
      <div className="auth-gate">
        <PageSkeleton variant="gate" />
      </div>
    );
  }

  if (authEnabled && !authenticated) {
    return (
      <div className="auth-gate">
        <div className="auth-gate-card panel">
          <h1>Sign in required</h1>
          <p className="muted">Use your organization Microsoft account to access the SOC 2 workspace.</p>
          <button type="button" className="btn btn-primary" onClick={() => login().catch(console.error)}>
            Sign in with Microsoft
          </button>
        </div>
      </div>
    );
  }

  if (!initialLoadDone && !apiError && !dashboard) {
    return (
      <div className="auth-gate">
        <PageSkeleton variant="gate" />
      </div>
    );
  }

  return (
    <div className="app-shell">
      <SidebarProvider active={active}>
      <SidebarShell frameworkSwitcher={frameworkSwitcher} frameworkLabel="SOC 2">
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/dashboard"}>
          <LayoutDashboard size={16} /> Dashboard
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/criteria"}>
          <Shield /> Controls
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/exceptions"}>
          <Activity /> Exceptions
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/audit"}>
          <Clock /> Audit Periods
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/reports"}>
          <FileText /> Reports
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/reviews"}>
          <ClipboardCheck /> Reviews
        </NavLink>

        <button type="button" className="sidebar-section-toggle" onClick={() => setComplianceOpen(!complianceOpen)}>
          <span>Compliance</span>
          <span className={`sidebar-section-chevron${complianceOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${complianceOpen ? " open" : ""}`}>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/risks"}>
          <Scale /> Risk Register
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/policies"}>
          <BookOpen /> Policies
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/findings"}>
          <Search /> Findings
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/incidents"}>
          <AlertTriangle /> Incidents
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/audits"}>
          <Clipboard /> Audits
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/compliance-calendar"}>
          <Calendar /> Compliance calendar
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/effectiveness"}>
          <Activity /> Program effectiveness
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/control-tests"}>
          <Activity /> Control tests
        </NavLink>
        </div>

        <button type="button" className="sidebar-section-toggle" onClick={() => setResourcesOpen(!resourcesOpen)}>
          <span>Resources</span>
          <span className={`sidebar-section-chevron${resourcesOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${resourcesOpen ? " open" : ""}`}>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/assets"}>
          <Box /> Assets
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/vendors"}>
          <Building2 /> Vendors
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/evidence"}>
          <FolderOpen /> Evidence Hub
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/team"}>
          <Users /> Team
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/training"}>
          <GraduationCap /> Training
        </NavLink>
        </div>

        <div className="sidebar-footer">
          <p className="sidebar-utility-label">Settings</p>
          <NavLink
            end
            className={({ isActive }) => `sidebar-utility-link${isActive ? " active" : ""}`}
            to={fwBase + "/integrations"}
          >
            Integrations
          </NavLink>
          <NavLink
            end
            className={({ isActive }) => `sidebar-utility-link${isActive ? " active" : ""}`}
            to={fwBase + "/audit-log"}
          >
            <History /> Audit Log
          </NavLink>
          <button type="button" className="sidebar-utility-btn workspace-btn" onClick={() => setWorkspaceOpen(true)}>
            Workspace
          </button>
          <NavLink
            end
            className={({ isActive }) => `sidebar-utility-link${isActive ? " active" : ""}`}
            to={fwBase + "/scoping"}
          >
            <Activity /> TSC Scope
          </NavLink>
          <NavLink
            end
            className={({ isActive }) => `sidebar-footer-link${isActive ? " active" : ""}`}
            to={fwBase + "/help"}
          >
            Help &amp; FAQ
          </NavLink>
        </div>
      </SidebarShell>
      <div className="main">
        <header className="topbar">
          <div className="topbar-start">
            <SidebarToggle />
            <h1>{dashboard?.org_name ?? (apiError ? "API offline" : "Loading…")}</h1>
            {needsAttention && (
              <span className="topbar-attention">{dashboard!.evidence_review_pending} to review</span>
            )}
          </div>
          <div className="topbar-end">
            <label className="topbar-reviewer-field muted">
              Reviewer
              <input
                type="text"
                className="topbar-reviewer-input"
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                onBlur={() => saveReviewerName().catch(console.error)}
                placeholder={settings?.current_role || "Name"}
                disabled={Boolean(settings?.workspace_locked)}
              />
            </label>
            <div style={{ position: "relative" }}>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                style={{ position: "relative", padding: "4px 8px" }}
                onClick={() => setShowNots(!showNots)}
                title="Notifications"
              >
                <Bell size={16} />
                {(nots?.unread_count ?? 0) > 0 && (
                  <span style={{
                    position: "absolute", top: 0, right: 0,
                    background: "var(--danger)", color: "#fff",
                    borderRadius: "50%", width: 16, height: 16,
                    fontSize: 10, display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    {nots!.unread_count}
                  </span>
                )}
              </button>
              {showNots && (
                <div style={{
                  position: "absolute", right: 0, top: "100%", zIndex: 1000,
                  background: "#fff", border: "1px solid var(--border-color)",
                  borderRadius: 8, boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
                  width: 340, maxHeight: 320, overflowY: "auto",
                }}>
                  <div style={{ padding: "8px 12px", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ fontSize: 13 }}>Notifications</strong>
                    {(nots?.unread_count ?? 0) > 0 && (
                      <button className="btn btn-ghost btn-sm" style={{ fontSize: 11 }} onClick={() => { api.markAllNotificationsRead().then(() => refreshNots()); setShowNots(false); }}>
                        Mark all read
                      </button>
                    )}
                  </div>
                  {(nots?.notifications ?? []).length === 0 && (
                    <p className="muted" style={{ textAlign: "center", padding: "1rem", fontSize: 12 }}>No notifications</p>
                  )}
                  {nots?.notifications.map((n) => (
                    <div key={n.id} style={{
                      padding: "10px 12px", borderBottom: "1px solid var(--border-subtle)",
                      background: n.read ? "transparent" : "var(--info-soft)", cursor: "pointer", fontSize: 12,
                    }}
                      onClick={() => {
                        if (!n.read) api.markNotificationRead(n.id).then(() => refreshNots());
                        setShowNots(false);
                      }}
                    >
                      <div style={{ fontWeight: n.read ? 400 : 600 }}>{n.title}</div>
                      {n.body && <div style={{ color: "var(--text-muted)", marginTop: 2 }}>{n.body}</div>}
                    </div>
                  ))}
                </div>
              )}
            </div>
            {settings?.current_role && (
              <span className="topbar-role-chip">{settings.current_role}</span>
            )}
            {authEnabled && displayName && (
              <span className="topbar-user-chip muted" title={email}>
                {displayName}
              </span>
            )}
            {authEnabled && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => logout().catch(console.error)}>
                Sign out
              </button>
            )}
            {dashboard && (
              <div className="sprs-chip readiness-chip">
                {dashboard.readiness_pct}% ready
              </div>
            )}
          </div>
        </header>
        <main className="content">
          {apiError && (
            <div className="banner error">
              {apiError}{" "}
              <button type="button" className="btn-link" onClick={() => refreshDashboard()}>
                Retry
              </button>
            </div>
          )}
          {settings?.workspace_locked && dashboard?.frozen_audit_period && (
            <div className="banner info">
              Audit period &ldquo;{dashboard.frozen_audit_period.name}&rdquo; is frozen — criteria and evidence
              are read-only.
            </div>
          )}
          {active ? (
            <Outlet
              context={{
                dashboard,
                settings,
                refreshDashboard,
                canEdit,
                apiError,
              }}
            />
          ) : null}
        </main>
      </div>
      <WorkspaceDrawer
        open={workspaceOpen}
        onClose={() => setWorkspaceOpen(false)}
        settings={settings}
        demoStatus={demoStatus}
        demoLoading={demoLoading}
        clearingDemo={clearingDemo}
        canEdit={canEdit}
        showClients={(settings?.clients?.length ?? 0) > 0}
        activeClientName={settings?.clients?.find((c) => c.id === settings?.active_client_id)?.name || settings?.active_client_id || "Default"}
        onRoleChange={(role) => patchRole(role).catch(console.error)}
        onUserNameChange={(name) => api.patchUserName(name).catch(console.error)}
        onClientSwitch={(id) => switchClient(id).catch(console.error)}
        onLoadDemo={() => loadDemo().catch(console.error)}
        onClearDemo={clearDemo}
      />
    </SidebarProvider>
    </div>
  );
}
