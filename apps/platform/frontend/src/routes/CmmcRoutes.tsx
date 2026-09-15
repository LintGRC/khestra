import { Route } from "react-router-dom";
import RiskDashboard from "@shared/risk-register/pages/RiskDashboard";
import AuditList from "@shared/audit-center/pages/AuditList";
import AuditNew from "@shared/audit-center/pages/AuditNew";
import AuditDetail from "@shared/audit-center/pages/AuditDetail";
import CmmcFindingsPage from "@cmmc/pages/Findings";
import CmmcDashboardPage from "@cmmc/pages/Dashboard";
import OrganizationPage from "@cmmc/pages/Organization";
import ControlsPage from "@cmmc/pages/Controls";
import ControlDetailPage from "@cmmc/pages/ControlDetail";
import ReadinessPage from "@cmmc/pages/Readiness";
import ExportPage from "@cmmc/pages/Export";
import { api } from "@cmmc/api";
import HelpPage from "@shared/settings/HelpPage";
import CmmcIntegrationsPage from "@cmmc/pages/Integrations";
import CmmcAuditLogPage from "@cmmc/pages/AuditLog";
import CmmcPoliciesPage from "@cmmc/pages/Policies";
import CmmcPolicyCreate from "@shared/policy-manager/pages/PolicyCreate";
import CmmcPolicyDetail from "@shared/policy-manager/pages/PolicyDetail";
import CmmcAssetsPage from "@cmmc/pages/Assets";
import CmmcSubcontractorsPage from "@cmmc/pages/Subcontractors";
import CmmcEvidenceHubPage from "@cmmc/pages/EvidenceHub";
import TeamPage from "@shared/personnel/pages/PersonnelDashboard";
import UserManagementPage from "@shared/auth/pages/UserManagementPage";
import TrainingPage from "@shared/training/pages/TrainingPage";
import CmmcPoamList from "@cmmc/pages/PoamList";
import CmmcPoamNew from "@cmmc/pages/PoamNew";
import CmmcPoamDetail from "@cmmc/pages/PoamDetail";
import IncidentsListPage from "@cmmc/pages/IncidentsList";
import IncidentsDetailPage from "@cmmc/pages/IncidentsDetail";
import IncidentsNewPage from "@cmmc/pages/IncidentsNew";
import IncidentDashboardPage from "@cmmc/pages/IncidentDashboard";
import IncidentNotificationsPage from "@cmmc/pages/IncidentNotifications";
import IncidentsEditPage from "@cmmc/pages/IncidentsEdit";
import VendorListPage from "@shared/vendor-manager/pages/VendorDashboard";
import VendorDetailPage from "@shared/vendor-manager/pages/VendorDetail";
import VendorNewPage from "@shared/vendor-manager/pages/VendorNew";
import VendorComparePage from "@shared/vendor-manager/pages/VendorCompare";

/** Route elements for CMMC — must be a fragment, not a wrapper component (RR v7). */
export const cmmcRouteElements = (
  <>
    <Route index element={<CmmcDashboardPage />} />
    <Route path="dashboard" element={<CmmcDashboardPage />} />
    <Route path="risks" element={<RiskDashboard />} />
    <Route path="organization" element={<OrganizationPage />} />
    <Route path="users" element={<UserManagementPage />} />
    <Route path="controls" element={<ControlsPage />} />
    <Route path="controls/:controlId" element={<ControlDetailPage />} />
    <Route path="readiness" element={<ReadinessPage />} />
    <Route path="export" element={<ExportPage />} />
    <Route path="help" element={<HelpPage getHelp={() => api.help()} />} />
    <Route path="audits" element={<AuditList frameworkFilter="CMMC" />} />
    <Route path="audits/new" element={<AuditNew frameworkDefault="CMMC" />} />
    <Route path="audits/:id" element={<AuditDetail />} />
    <Route path="audit-log" element={<CmmcAuditLogPage />} />
    <Route path="policies">
      <Route index element={<CmmcPoliciesPage />} />
      <Route path="new" element={<CmmcPolicyCreate frameworkFilter="cmmc" />} />
      <Route path=":id" element={<CmmcPolicyDetail />} />
    </Route>
    <Route path="assets" element={<CmmcAssetsPage />} />
    <Route path="subcontractors" element={<CmmcSubcontractorsPage />} />
    <Route path="evidence" element={<CmmcEvidenceHubPage />} />
    <Route path="team" element={<TeamPage />} />
    <Route path="training" element={<TrainingPage />} />
    <Route path="poam">
      <Route index element={<CmmcPoamList />} />
      <Route path="new" element={<CmmcPoamNew />} />
      <Route path=":id" element={<CmmcPoamDetail />} />
    </Route>
    <Route path="findings" element={<CmmcFindingsPage />} />
    <Route path="integrations" element={<CmmcIntegrationsPage />} />
    <Route path="incidents" element={<IncidentsListPage />} />
    <Route path="incidents/new" element={<IncidentsNewPage />} />
    <Route path="incidents/:iid/edit" element={<IncidentsEditPage />} />
    <Route path="incidents/:iid" element={<IncidentsDetailPage />} />
    <Route path="incidents/dashboard" element={<IncidentDashboardPage />} />
    <Route path="incidents/notifications" element={<IncidentNotificationsPage />} />
    <Route path="vendors" element={<VendorListPage />} />
    <Route path="vendors/compare" element={<VendorComparePage />} />
    <Route path="vendors/new" element={<VendorNewPage />} />
    <Route path="vendors/:id" element={<VendorDetailPage />} />
  </>
);
