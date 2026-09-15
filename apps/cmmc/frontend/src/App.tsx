import { Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import DashboardPage from "./pages/Dashboard";
import OrganizationPage from "./pages/Organization";
import ControlsPage from "./pages/Controls";
import ControlDetailPage from "./pages/ControlDetail";
import ReadinessPage from "./pages/Readiness";
import ExportPage from "./pages/Export";
import HelpPage from "./pages/Help";
import TeamPage from "./pages/Team";
import UserManagementPage from "@shared/auth/pages/UserManagementPage";
import IntegrationsPage from "./pages/Integrations";
import AuditLogPage from "./pages/AuditLog";
import AuditList from "@shared/audit-center/pages/AuditList";
import AuditNew from "@shared/audit-center/pages/AuditNew";
import AuditDetail from "@shared/audit-center/pages/AuditDetail";
import TrainingPage from "./pages/Training";
import FindingsPage from "./pages/Findings";
import PoliciesPage from "./pages/Policies";
import PolicyNewPage from "./pages/PolicyNew";
import PolicyDetail from "@shared/policy-manager/pages/PolicyDetail";
import AssetsPage from "./pages/Assets";
import SubcontractorsPage from "./pages/Subcontractors";
import EvidenceHubPage from "./pages/EvidenceHub";
import EvidenceCoveragePage from "./pages/EvidenceCoverage";
import ComplianceCalendarPage from "@shared/compliance-calendar/pages/ComplianceCalendarPage";
import EffectivenessDashboard from "@shared/effectiveness/pages/EffectivenessDashboard";
import ControlTestsPage from "@shared/control-tests/pages/ControlTestsPage";
import IncidentsListPage from "./pages/IncidentsList";
import IncidentsDetailPage from "./pages/IncidentsDetail";
import IncidentsNewPage from "./pages/IncidentsNew";
import IncidentDashboardPage from "./pages/IncidentDashboard";
import IncidentNotificationsPage from "./pages/IncidentNotifications";
import IncidentsEditPage from "./pages/IncidentsEdit";
import PoamList from "./pages/PoamList";
import PoamNew from "./pages/PoamNew";
import PoamDetail from "./pages/PoamDetail";
import { VendorDetail, VendorNew } from "@shared/vendor-manager";
import { RiskDashboard } from "@shared/risk-register";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="organization" element={<OrganizationPage />} />
        <Route path="users" element={<UserManagementPage />} />
        <Route path="controls" element={<ControlsPage />} />
        <Route path="controls/:controlId" element={<ControlDetailPage />} />
        <Route path="readiness" element={<ReadinessPage />} />
        <Route path="export" element={<ExportPage />} />
        <Route path="audits" element={<AuditList frameworkFilter="CMMC" />} />
        <Route path="audits/new" element={<AuditNew frameworkDefault="CMMC" />} />
        <Route path="audits/:id" element={<AuditDetail />} />
        <Route path="audit-log" element={<AuditLogPage />} />
        <Route path="findings" element={<FindingsPage />} />
        <Route path="policies">
          <Route index element={<PoliciesPage />} />
          <Route path="new" element={<PolicyNewPage />} />
          <Route path=":id" element={<PolicyDetail />} />
        </Route>
        <Route path="assets" element={<AssetsPage />} />
        <Route path="subcontractors" element={<SubcontractorsPage />} />
        <Route path="vendors" element={<SubcontractorsPage />} />
        <Route path="vendors/new" element={<VendorNew />} />
        <Route path="vendors/:id" element={<VendorDetail />} />
        <Route path="evidence" element={<EvidenceHubPage />} />
        <Route path="evidence/coverage" element={<EvidenceCoveragePage />} />
        <Route path="compliance-calendar" element={<ComplianceCalendarPage frameworkId="CMMC" />} />
        <Route path="effectiveness" element={<EffectivenessDashboard frameworkId="CMMC Rev 2" />} />
        <Route path="control-tests" element={<ControlTestsPage frameworkId="CMMC Rev 2" />} />
        <Route path="incidents" element={<IncidentsListPage />} />
        <Route path="incidents/new" element={<IncidentsNewPage />} />
        <Route path="incidents/:iid/edit" element={<IncidentsEditPage />} />
        <Route path="incidents/:iid" element={<IncidentsDetailPage />} />
        <Route path="incidents/dashboard" element={<IncidentDashboardPage />} />
        <Route path="incidents/notifications" element={<IncidentNotificationsPage />} />
        <Route path="poam" element={<PoamList />} />
        <Route path="poam/new" element={<PoamNew />} />
        <Route path="poam/:id" element={<PoamDetail />} />
        <Route path="risks" element={<RiskDashboard />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="help" element={<HelpPage />} />
        <Route path="team" element={<TeamPage />} />
        <Route path="training" element={<TrainingPage />} />
      </Route>
    </Routes>
  );
}
