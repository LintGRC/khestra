import { ReactNode, useEffect, useState } from "react";
import { NavLink, Outlet, useOutletContext, useLocation } from "react-router-dom";
import { Database, Shield, Building2, Activity, Scale, BookOpen, FileSearch, Users, RefreshCw, Box, FolderOpen, UserPlus, Play, ClipboardCheck, Table, FileText, CheckCircle, FileSpreadsheet, Award, GraduationCap, Calendar } from "lucide-react";
import SidebarShell, { SidebarProvider, SidebarToggle } from "@shared/sidebar/SidebarShell";
import { authHeaders } from "@shared/accessToken";
import { useAuth } from "./auth/AuthProvider";
import WorkspaceDrawer from "@shared/settings/WorkspaceDrawer";
import { AiGovFrameworkProvider } from "./pages/AiGovFrameworkContext";
import "./aigov.css";

type GovernanceData = {
  org_name: string;
  total_systems: number;
  total_incidents: number;
  high_risk: number;
  production_systems: number;
  open_incidents: number;
  overdue_regulatory: number;
};

export type AiGovContext = {
  data: GovernanceData | null;
  systems: any[];
  apiPrefix: string;
};

export function useAiGov() {
  return useOutletContext<AiGovContext>();
}

function AiGovernanceLayoutInner({ frameworkSwitcher }: LayoutProps = {}) {
  const { pathname } = useLocation();
  const { ready: authReady, enabled: authEnabled, authenticated, displayName, email, login, logout } = useAuth();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const [data, setData] = useState<GovernanceData | null>(null);
  const [systems, setSystems] = useState<any[]>([]);
  const [govOpen, setGovOpen] = useState(true);
  const [assessOpen, setAssessOpen] = useState(true);
  const [opsOpen, setOpsOpen] = useState(true);
  const [complianceOpen, setComplianceOpen] = useState(true);
  const [resourcesOpen, setResourcesOpen] = useState(true);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  const apiPrefix = "/api/ai-governance";

  useEffect(() => {
    const load = async () => {
      const headers = await authHeaders();
      const [gov, sys] = await Promise.all([
        fetch(`${apiPrefix}/governance`, { headers }).then((r) => r.json()),
        fetch(`${apiPrefix}/systems`, { headers }).then((r) => r.json()),
      ]);
      setData(gov);
      setSystems(sys.systems || []);
    };
    load().catch(() => {});
  }, []);

  if (!authReady) {
    return (
      <div className="auth-gate">
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (authEnabled && !authenticated) {
    return (
      <div className="auth-gate">
        <div className="auth-gate-card panel">
          <h1>Sign in required</h1>
          <p className="muted">Sign in to access AI Governance.</p>
          <button type="button" className="btn btn-primary" onClick={() => login().catch(console.error)}>
            Sign in with Microsoft
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <SidebarProvider active={true}>
      <SidebarShell frameworkSwitcher={frameworkSwitcher} frameworkLabel="AI Governance" sidebarClassName="aigov-sidebar">
        <NavLink to={fwBase + "/dashboard"} end className="nav-link">
          <Activity /> Dashboard
        </NavLink>

        <button type="button" className="sidebar-section-toggle" onClick={() => setGovOpen(!govOpen)}>
          <span>Governance</span>
          <span className={`sidebar-section-chevron${govOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${govOpen ? " open" : ""}`}>
        <NavLink to={fwBase + "/systems"} end className="nav-link">
          <Database /> Systems
        </NavLink>
        <NavLink to={fwBase + "/evaluations"} end className="nav-link">
          <ClipboardCheck /> Evaluations
        </NavLink>
        <NavLink to={fwBase + "/training-data"} end className="nav-link">
          <Table /> Training Data
        </NavLink>
        <NavLink to={fwBase + "/plans"} end className="nav-link">
          <FileText /> Plans
        </NavLink>
        <NavLink to={fwBase + "/contracts"} end className="nav-link">
          <FileText /> Contracts
        </NavLink>
        </div>

        <button type="button" className="sidebar-section-toggle" onClick={() => setAssessOpen(!assessOpen)}>
          <span>Assessments</span>
          <span className={`sidebar-section-chevron${assessOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${assessOpen ? " open" : ""}`}>
        <NavLink to={fwBase + "/readiness"} end className="nav-link">
          <CheckCircle /> Readiness
        </NavLink>
        <NavLink to={fwBase + "/competence"} end className="nav-link">
          <Award /> Competence
        </NavLink>
        <NavLink to={fwBase + "/gap-analysis"} end className="nav-link">
          <FileSearch /> Gap Analysis
        </NavLink>
        <NavLink to={fwBase + "/audit-report"} end className="nav-link">
          <FileSpreadsheet /> Audit Report
        </NavLink>
        <NavLink to={fwBase + "/frias"} end className="nav-link">
          <Users /> FRIAs
        </NavLink>
        </div>

        <button type="button" className="sidebar-section-toggle" onClick={() => setOpsOpen(!opsOpen)}>
          <span>Operations</span>
          <span className={`sidebar-section-chevron${opsOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${opsOpen ? " open" : ""}`}>
        <NavLink to={fwBase + "/review-cycles"} end className="nav-link">
          <RefreshCw /> Review Cycles
        </NavLink>
        <NavLink to={fwBase + "/tabletop"} end className="nav-link">
          <Play /> Tabletop
        </NavLink>
        </div>

        <button type="button" className="sidebar-section-toggle" onClick={() => setComplianceOpen(!complianceOpen)}>
          <span>Compliance</span>
          <span className={`sidebar-section-chevron${complianceOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${complianceOpen ? " open" : ""}`}>
        <NavLink to={fwBase + "/risks"} end className="nav-link">
          <Scale /> Risk Register
        </NavLink>
        <NavLink to={fwBase + "/compliance-calendar"} end className="nav-link">
          <Calendar /> Compliance calendar
        </NavLink>
        <NavLink to={fwBase + "/effectiveness"} end className="nav-link">
          <Activity /> Program effectiveness
        </NavLink>
        <NavLink to={fwBase + "/control-tests"} end className="nav-link">
          <Activity /> Control tests
        </NavLink>
        <NavLink to={fwBase + "/policies"} end className="nav-link">
          <BookOpen /> Policies
        </NavLink>
        <NavLink to={fwBase + "/incidents"} end className="nav-link">
          <Shield /> Incidents
        </NavLink>
        <NavLink to={fwBase + "/audits"} end className="nav-link">
          <ClipboardCheck /> Audits
        </NavLink>
        </div>

        <button type="button" className="sidebar-section-toggle" onClick={() => setResourcesOpen(!resourcesOpen)}>
          <span>Resources</span>
          <span className={`sidebar-section-chevron${resourcesOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
        </button>
        <div className={`sidebar-section-content${resourcesOpen ? " open" : ""}`}>
        <NavLink to={fwBase + "/assets"} end className="nav-link">
          <Box /> Assets
        </NavLink>
        <NavLink to={fwBase + "/vendors"} end className="nav-link">
          <Building2 /> Vendors
        </NavLink>
        <NavLink to={fwBase + "/team"} end className="nav-link">
          <UserPlus /> Team
        </NavLink>
        <NavLink to={fwBase + "/evidence"} end className="nav-link">
          <FolderOpen /> Evidence Hub
        </NavLink>
        <NavLink to={fwBase + "/training"} end className="nav-link">
          <GraduationCap /> Training
        </NavLink>
        </div>

        <div className="sidebar-footer">
          <p className="sidebar-utility-label">Settings</p>
          <NavLink to={fwBase + "/integrations"} end className="sidebar-utility-link">
            Integrations
          </NavLink>
          <NavLink to={fwBase + "/audit"} end className="sidebar-utility-link">
            Audit Log
          </NavLink>
          <button type="button" className="sidebar-utility-btn workspace-btn" onClick={() => setWorkspaceOpen(true)}>
            Workspace
          </button>
          <NavLink to={fwBase + "/help"} end className="sidebar-footer-link">
            Help &amp; FAQ
          </NavLink>
        </div>
      </SidebarShell>

      <div className="main">
        <header className="topbar">
          <div className="topbar-start">
            <SidebarToggle />
            <h1>{data?.org_name ?? "AI Governance"}</h1>
          </div>
          <div className="topbar-end">
            {authEnabled && (
              <span className="topbar-user-chip muted" title={email}>
                {displayName || email}
              </span>
            )}
            {authEnabled && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => logout().catch(console.error)}>
                Sign out
              </button>
            )}
          </div>
        </header>
        <main className="content">
          <Outlet context={{ data, systems, apiPrefix }} />
        </main>
      </div>
    </SidebarProvider>
      <WorkspaceDrawer open={workspaceOpen} onClose={() => setWorkspaceOpen(false)} />
    </div>
  );
}

type LayoutProps = {
  frameworkSwitcher?: ReactNode;
};

export default function Layout({ frameworkSwitcher }: LayoutProps = {}) {
  return (
    <AiGovFrameworkProvider>
      <AiGovernanceLayoutInner frameworkSwitcher={frameworkSwitcher} />
    </AiGovFrameworkProvider>
  );
}
