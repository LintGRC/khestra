import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import FrameworkSwitcher from "./FrameworkSwitcher";
import SidebarShell, { SidebarProvider, SidebarToggle } from "@shared/sidebar/SidebarShell";
import WorkspaceDrawer from "@shared/settings/WorkspaceDrawer";

export default function RootLayout() {
  const { pathname } = useLocation();
  const fwMatch = pathname.match(/^\/(cmmc|soc2|aigov)/);
  const fwBase = fwMatch ? fwMatch[0] : "/soc2";
  const [complianceOpen, setComplianceOpen] = useState(true);
  const [resourcesOpen, setResourcesOpen] = useState(true);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);

  return (
    <div className="app-shell">
      <SidebarProvider active={true}>
        <SidebarShell frameworkSwitcher={<FrameworkSwitcher placeholder="Framework" />} frameworkLabel="Platform">
          <button type="button" className="sidebar-section-toggle" onClick={() => setComplianceOpen(!complianceOpen)}>
            <span>Compliance</span>
            <span className={`sidebar-section-chevron${complianceOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
          </button>
          <div className={`sidebar-section-content${complianceOpen ? " open" : ""}`}>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/posture">
            Unified Control Posture
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/remediation">
            Remediation Queue
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/collectors">
            Collectors
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/risks">
            Risk Register
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/policies">
            Policy Hub
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/incidents">
            Incidents
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/audits">
            Audits
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/compliance-calendar">
            Compliance calendar
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/effectiveness">
            Program effectiveness
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/control-tests">
            Control tests
          </NavLink>
          </div>

          <button type="button" className="sidebar-section-toggle" onClick={() => setResourcesOpen(!resourcesOpen)}>
            <span>Resources</span>
            <span className={`sidebar-section-chevron${resourcesOpen ? "" : " collapsed"}`} aria-hidden>▾</span>
          </button>
          <div className={`sidebar-section-content${resourcesOpen ? " open" : ""}`}>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/assets">
            Assets
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/vendors">
            Vendors
          </NavLink>
          <NavLink end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} to="/evidence">
            Evidence Hub
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
            <NavLink end className={({ isActive }) => `sidebar-utility-link${isActive ? " active" : ""}`} to="/audit-log">
            Audit Log
          </NavLink>
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
            <NavLink
              end
              className={({ isActive }) => `sidebar-footer-link${isActive ? " active" : ""}`}
              to="/trust"
            >
              Trust Center
            </NavLink>
          </div>
        </SidebarShell>
        <div className="main">
          <header className="topbar">
            <div className="topbar-start">
              <SidebarToggle />
              <h1>{pathname === "/" ? "GRC Platform Overview" : ({"/policies": "Policy Hub", "/posture": "Unified Control Posture", "/remediation": "Remediation Queue", "/collectors": "Collectors", "/assets": "Assets", "/vendors": "Vendors", "/evidence": "Evidence Hub", "/incidents": "Incidents", "/audits": "Audits", "/audit-log": "Audit Log", "/risks": "Risk Register", "/trust": "Trust Center"} as Record<string, string>)[pathname] || "Global"}</h1>
            </div>
          </header>
          <main className="content">
            <Outlet />
          </main>
        </div>
      </SidebarProvider>
      <WorkspaceDrawer open={workspaceOpen} onClose={() => setWorkspaceOpen(false)} />
    </div>
  );
}
