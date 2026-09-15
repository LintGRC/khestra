import { NavLink, Outlet, useLocation, useOutletContext } from "react-router-dom";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { useScrollRestoration } from "@shared/scroll-restoration/useScrollRestoration";
import { getApiPrefix } from "@shared/apiPrefix";
import { peekLayoutCache } from "@shared/frameworkLayoutCache";
import SidebarShell, { SidebarProvider, SidebarToggle } from "@shared/sidebar/SidebarShell";
import { api, Dashboard, DemoStatus, Journey, Settings } from "./api";
import { useAuth } from "./auth/AuthProvider";

import OrganizationOnboarding from "./components/OrganizationOnboarding";
import WorkspaceDrawer from "@shared/settings/WorkspaceDrawer";
import { PageSkeleton } from "./components/ui/Skeleton";
import { navPhaseState, PhaseId } from "./phaseStatus";

export type LayoutContext = {
  dashboard: Dashboard | null;
  settings: Settings | null;
  refreshDashboard: () => Promise<void>;
  openWorkspace: () => void;
  canEdit: boolean;
  canEditOrg: boolean;
  canExport: boolean;
  canValidate: boolean;
  canViewDashboard: boolean;
  canManageUsers: boolean;
  apiError: string | null;
};

export function useLayout() {
  return useOutletContext<LayoutContext>();
}

function layoutBootstrap() {
  return peekLayoutCache(getApiPrefix());
}

type LayoutProps = {
  frameworkSwitcher?: ReactNode;
};

export default function Layout({ frameworkSwitcher }: LayoutProps = {}) {
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
  const [newClientName, setNewClientName] = useState("");
  const [showNewClient, setShowNewClient] = useState(false);
  const [showManageClient, setShowManageClient] = useState(false);
  const [renameClientName, setRenameClientName] = useState("");
  const [apiError, setApiError] = useState<string | null>(null);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  const [complianceOpen, setComplianceOpen] = useState(true);
  const [resourcesOpen, setResourcesOpen] = useState(true);
  const [journey, setJourney] = useState<Journey | null>(
    () => (boot?.journey as Journey | undefined) ?? null,
  );
  const [initialLoadDone, setInitialLoadDone] = useState(Boolean(boot?.dashboard));

  const refreshDashboard = useCallback(async () => {
    setApiError(null);
    const [dashResult, settingsResult, demoResult, journeyResult] = await Promise.allSettled([
      api.dashboard(),
      api.settings(),
      api.demoStatus(),
      api.journey(),
    ]);
    if (dashResult.status === "fulfilled") {
      setDashboard(dashResult.value);
    } else {
      setDashboard(null);
      setApiError(
        "Cannot reach the API. From platform/, run ./run-dev.sh (not just the Vite UI). " +
          "If port 8080 was in use, the script now frees it automatically.",
      );
    }
    if (settingsResult.status === "fulfilled") {
      setSettings(settingsResult.value);
    } else {
      setSettings(null);
      if (dashResult.status !== "fulfilled") {
        setApiError(
          (prev) =>
            prev ||
            "API running but missing routes — restart ./run-dev.sh to pick up the latest server.",
        );
      }
    }
    if (demoResult.status === "fulfilled") {
      setDemoStatus(demoResult.value);
    } else {
      setDemoStatus(null);
    }
    if (journeyResult.status === "fulfilled") {
      setJourney(journeyResult.value);
    } else {
      setJourney(null);
    }
  }, []);

  useEffect(() => {
    if (!authReady) return;
    if (authEnabled && !authenticated) return;
    refreshDashboard()
      .catch(console.error)
      .finally(() => setInitialLoadDone(true));
  }, [authReady, authEnabled, authenticated, refreshDashboard]);

  useEffect(() => {
    if (!settings || !showManageClient) return;
    const current = settings.clients.find((c) => c.id === settings.active_client_id);
    setRenameClientName(current?.name || "");
  }, [settings?.active_client_id, showManageClient, settings?.clients]);

  const loadDemo = async (demoId: string) => {
    setDemoLoading(true);
    try {
      await api.loadDemo(demoId);
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

  const onRoleChange = async (role: string) => {
    await api.patchRole(role);
    await refreshDashboard();
  };

  const onUserNameChange = async (name: string) => {
    await api.patchUserName(name);
    await refreshDashboard();
  };

  const onMspToggle = async () => {
    if (!settings) return;
    await api.patchMspMode(!settings.msp_mode);
    await refreshDashboard();
  };

  const onClientSwitch = async (clientId: string) => {
    await api.activateClient(clientId);
    await refreshDashboard();
    window.location.reload();
  };

  const createClient = async () => {
    if (!newClientName.trim()) return;
    const { client_id } = await api.createClient(newClientName.trim());
    setNewClientName("");
    setShowNewClient(false);
    await onClientSwitch(client_id);
  };

  const renameClient = async () => {
    if (!settings || !renameClientName.trim()) return;
    await api.renameClient(settings.active_client_id, renameClientName.trim());
    await refreshDashboard();
  };

  const deleteClient = async () => {
    if (!settings || settings.active_client_id === "default") return;
    const current = settings.clients.find((c) => c.id === settings.active_client_id);
    if (!window.confirm(`Delete client workspace "${current?.name || settings.active_client_id}"? This cannot be undone.`)) {
      return;
    }
    const result = await api.deleteClient(settings.active_client_id);
    await api.activateClient(result.active_client_id);
    window.location.reload();
  };

  const caps = settings?.capabilities;
  const canEdit = caps?.edit_controls ?? false;
  const canEditOrg = caps?.edit_org ?? false;
  const canExport = caps?.export_data ?? false;
  const canValidate = caps?.validate_config ?? false;
  const canViewDashboard = caps?.view_dashboard ?? true;
  const canManageUsers = caps?.manage_users ?? false;
  const showClients = settings?.msp_mode || (settings?.clients?.length ?? 0) > 1;
  const activeClient = settings?.clients.find((c) => c.id === settings.active_client_id);
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  const phaseNav = (phaseId: PhaseId, path: string, label: string) => {
    const state = navPhaseState(phaseId, pathname, path, journey);
    return (
      <NavLink className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/" + path}>
        <span className="nav-link-text">{label}</span>
        <span className={`nav-phase-dot nav-phase-dot--${state}`} aria-hidden />
      </NavLink>
    );
  };

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
          <p className="muted">
            Use your organization Microsoft account. Your role (Assessor, Engineer, etc.) is assigned
            per organization in this sandbox.
          </p>
          <button type="button" className="btn btn-primary" onClick={() => login().catch(console.error)}>
            Sign in with Microsoft
          </button>
        </div>
      </div>
    );
  }

  if (authEnabled && authenticated && !initialLoadDone && !apiError) {
    return (
      <div className="auth-gate">
        <PageSkeleton variant="gate" />
      </div>
    );
  }

  if (settings?.needs_organization) {
    return <OrganizationOnboarding onCreated={refreshDashboard} />;
  }

  return (
    <div className="app-shell">
      <SidebarProvider active={true}>
      <SidebarShell frameworkSwitcher={frameworkSwitcher} frameworkLabel="CMMC">
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/dashboard"}>
          Dashboard
        </NavLink>
        {phaseNav("org", "organization", "Organization")}
{phaseNav("controls", "controls", "Controls")}
{phaseNav("readiness", "readiness", "Readiness")}
{phaseNav("export", "export", "Export")}

        <button type="button" className="sidebar-section-toggle" onClick={() => setComplianceOpen(!complianceOpen)}>
          <span>Compliance</span>
          <span className={`sidebar-section-chevron${complianceOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${complianceOpen ? " open" : ""}`}>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/risks"}>
          Risk Register
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/policies"}>
          Policies
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/findings"}>
          Findings
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/poam"}>
          POA&Ms
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/incidents"}>
          Incidents
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/audits"}>
          Audits
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/compliance-calendar"}>
          Compliance calendar
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/effectiveness"}>
          Program effectiveness
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/control-tests"}>
          Control tests
        </NavLink>
        </div>

        <button type="button" className="sidebar-section-toggle" onClick={() => setResourcesOpen(!resourcesOpen)}>
          <span>Resources</span>
          <span className={`sidebar-section-chevron${resourcesOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${resourcesOpen ? " open" : ""}`}>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/assets"}>
          Assets
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/vendors"}>
          Subcontractors
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/evidence"}>
          Evidence Hub
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/team"}>
          Team
        </NavLink>
        <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to={fwBase + "/training"}>
          Training
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
            Audit Log
          </NavLink>
          {canManageUsers && <NavLink end className={({ isActive }) => `sidebar-utility-link${isActive ? " active" : ""}`} to={fwBase + "/users"}>Users</NavLink>}
          <button type="button" className="sidebar-utility-btn workspace-btn" onClick={() => setWorkspaceOpen(true)}>
            Workspace
          </button>
          <NavLink
            end
            className={({ isActive }) => `sidebar-footer-link${isActive ? " active" : ""}`}
            to={fwBase + "/help"}
          >
            Help &amp; FAQ
          </NavLink>
        </div>
      </SidebarShell>
      <WorkspaceDrawer
        open={workspaceOpen}
        onClose={() => setWorkspaceOpen(false)}
        settings={settings}
        demoStatus={demoStatus}
        demoLoading={demoLoading}
        canExport={canExport}
        canEdit={canEdit}
        canEditOrg={canEditOrg}
        showClients={showClients}
        activeClientName={activeClient?.name || settings?.active_client_id || "Default"}
        showManageClient={showManageClient}
        showNewClient={showNewClient}
        newClientName={newClientName}
        renameClientName={renameClientName}
        onRoleChange={onRoleChange}
        onUserNameChange={onUserNameChange}
        onMspToggle={onMspToggle}
        onClientSwitch={onClientSwitch}
        onCreateClient={createClient}
        onRenameClient={renameClient}
        onDeleteClient={deleteClient}
        onLoadDemo={loadDemo}
        onClearDemo={clearDemo}
        clearingDemo={clearingDemo}
        setShowManageClient={setShowManageClient}
        setShowNewClient={setShowNewClient}
        setNewClientName={setNewClientName}
        setRenameClientName={setRenameClientName}
        onImportWorkspace={(f) => api.importWorkspace(f)}
        onResetControls={() => api.resetControls()}
        onResetWorkspace={() => api.resetWorkspace()}
      />
      <div className="main">
        <header className="topbar">
          <div className="topbar-start">
            <SidebarToggle />
            <h1>{dashboard?.org_name ?? (apiError ? "API offline" : "Loading…")}</h1>
            {showClients && settings && (
              <button
                type="button"
                className="topbar-client-chip"
                onClick={() => setWorkspaceOpen(true)}
                title="Switch client workspace"
              >
                {activeClient?.name || settings.active_client_id}
              </button>
            )}
          </div>
          <div className="topbar-end">
            {authEnabled && (
              <span className="topbar-user-chip muted" title={email}>
                {displayName || email}
              </span>
            )}
            {settings?.current_role && (
              <span className="topbar-role-chip">{settings.current_role}</span>
            )}
            {authEnabled && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => logout().catch(console.error)}>
                Sign out
              </button>
            )}
            {dashboard && (
              <div className="sprs-chip">
                SPRS {dashboard.sprs_score}/{dashboard.sprs_max}
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
          {settings?.msp_mode && !showClients && (
            <div className="banner info msp-banner">
              <strong>MSP / consultant mode</strong>
              <span className="muted">Enable multiple clients in Workspace settings.</span>
            </div>
          )}
            <Outlet
              context={{
                dashboard,
                settings,
                refreshDashboard,
                openWorkspace: () => setWorkspaceOpen(true),
                canEdit,
                canEditOrg,
                canExport,
                canValidate,
                canViewDashboard,
                canManageUsers,
                apiError,
              }}
            />
        </main>
      </div>
    </SidebarProvider>
    </div>
  );
}
