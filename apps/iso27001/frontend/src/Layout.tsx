import {
  LayoutDashboard, ShieldCheck, Scale, Activity, FileText, Building2, Box, FolderOpen, Users, GraduationCap, Bell, Calendar, CheckSquare, AlertTriangle, Clipboard, ClipboardCheck, Globe, RefreshCw,
} from "lucide-react";
import { NavLink, Outlet, useLocation, useOutletContext } from "react-router-dom";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { useScrollRestoration } from "@shared/scroll-restoration/useScrollRestoration";
import { getApiPrefix } from "@shared/apiPrefix";
import { peekLayoutCache } from "@shared/frameworkLayoutCache";
import SidebarShell, { SidebarProvider, SidebarToggle } from "@shared/sidebar/SidebarShell";
import { api, DashboardData, NotificationsResponse, Settings } from "./api";
import { useAuth } from "@shared/authContext";

export type LayoutContext = {
  dashboard: DashboardData | null;
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

function PageGate() {
  return (
    <div className="auth-gate">
      <div className="panel" style={{ width: 420, padding: "2rem" }}>
        <p className="muted">Loading&hellip;</p>
      </div>
    </div>
  );
}

export default function Layout({ frameworkSwitcher, active = true }: LayoutProps = {}) {
  const { ready: authReady, enabled: authEnabled, authenticated, displayName, email, login, logout } = useAuth();
  useScrollRestoration();
  const boot = peekLayoutCache(getApiPrefix());
  const [dashboard, setDashboard] = useState<DashboardData | null>(
    () => (boot?.dashboard as DashboardData | undefined) ?? null,
  );
  const [settings, setSettings] = useState<Settings | null>(
    () => (boot?.settings as Settings | undefined) ?? null,
  );
  const [apiError, setApiError] = useState<string | null>(null);
  const [initialLoadDone, setInitialLoadDone] = useState(Boolean(boot?.dashboard));
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
    const [dashResult, settingsResult] = await Promise.allSettled([
      api.dashboard(),
      api.settings(),
    ]);
    if (dashResult.status === "fulfilled") setDashboard(dashResult.value);
    else {
      setDashboard(null);
      setApiError(
        "Cannot reach the ISO 27001 API. From khestra root run `apps/iso27001/run-dev.sh` " +
          "(standalone on :5177).",
      );
    }
    if (settingsResult.status === "fulfilled") setSettings(settingsResult.value);
  }, []);

  useEffect(() => {
    if (!active || !authReady) return;
    if (authEnabled && !authenticated) return;
    refreshDashboard()
      .catch(console.error)
      .finally(() => setInitialLoadDone(true));
  }, [active, authReady, authEnabled, authenticated, refreshDashboard]);

  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(iso27001)/)?.[0] ?? "";

  const canEdit = settings?.capabilities?.edit_controls ?? true;

  if (!authReady) return <div className="auth-gate"><PageGate/></div>;
  if (authEnabled && !authenticated) {
    return (
      <div className="auth-gate">
        <div className="auth-gate-card panel">
          <h1>Sign in required</h1>
          <p className="muted">Use your organization Microsoft account to access the ISO 27001 workspace.</p>
          <button type="button" className="btn btn-primary" onClick={() => login().catch(console.error)}>
            Sign in with Microsoft
          </button>
        </div>
      </div>
    );
  }
  if (!initialLoadDone && !apiError && !dashboard) return <div className="auth-gate"><PageGate/></div>;

  return (
    <div className="app-shell">
      <SidebarProvider active={active}>
        <SidebarShell frameworkSwitcher={frameworkSwitcher} frameworkLabel="ISO 27001">
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/"}>
            <LayoutDashboard size={16} /> Dashboard
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/soa"}>
            <ShieldCheck/> SoA
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/context"}>
            <Globe /> Context & Scope
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/management-review"}>
            <RefreshCw /> Management Review
          </NavLink>

          <button type="button" className="sidebar-section-toggle" onClick={() => setComplianceOpen(!complianceOpen)}>
            <span>Compliance</span>
            <span className={`sidebar-section-chevron${complianceOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
          </button>
          <div className={`sidebar-section-content${complianceOpen ? " open" : ""}`}>
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/risks"}>
              <Scale /> Risk Register
            </NavLink>
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/risk-assessment"}>
              <Activity /> Risk Assessment
            </NavLink>
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/policies"}>
              <FileText /> Policies
            </NavLink>
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/findings"}>
              <CheckSquare /> Findings
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
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/reviews"}>
              <ClipboardCheck /> Reviews
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
              <Users /> Personnel
            </NavLink>
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/training"}>
              <GraduationCap /> Training
            </NavLink>
            <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/integrations"}>
              <FolderOpen /> Integrations
            </NavLink>
          </div>
        </SidebarShell>
        <div className="main">
          <header className="topbar">
            <div className="topbar-start">
              <SidebarToggle />
              <h1>{dashboard?.org_name ?? (apiError ? "API offline" : "Loading…")}</h1>
            </div>
            <div className="topbar-end">
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
                <span className="topbar-user-chip muted" title={email}>{displayName}</span>
              )}
              {authEnabled && (
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => logout().catch(console.error)}>
                  Sign out
                </button>
              )}
              {dashboard && (
                <div className="sprs-chip readiness-chip">
                  {dashboard.readiness_pct}% implemented
                </div>
              )}
            </div>
          </header>
          <main className="content">
            {apiError && (
              <div className="banner error">
                {apiError}{" "}
                <button type="button" className="btn-link" onClick={() => refreshDashboard()}>Retry</button>
              </div>
            )}
            {active ? <Outlet context={{ dashboard, settings, refreshDashboard, canEdit, apiError }} /> : null}
          </main>
        </div>
      </SidebarProvider>
    </div>
  );
}