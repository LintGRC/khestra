import { Route } from "react-router-dom";
import AuditList from "@shared/audit-center/pages/AuditList";
import AuditNew from "@shared/audit-center/pages/AuditNew";
import AuditDetail from "@shared/audit-center/pages/AuditDetail";
import Soc2DashboardPage from "@soc2/pages/Dashboard";
import Soc2GovernanceDashboard from "@soc2/pages/GovernanceDashboard";
import WelcomePage from "@soc2/pages/Welcome";
import OrganizationPage from "@soc2/pages/Organization";
import ReadinessPage from "@soc2/pages/Readiness";
import MyWorkPage from "@soc2/pages/MyWork";
import PriorityQueuePage from "@soc2/pages/PriorityQueue";
import ExceptionsPage from "@soc2/pages/Exceptions";
import NewExceptionPage from "@soc2/pages/NewException";
import ExceptionDetailPage from "@soc2/pages/ExceptionDetail";
import RisksPage from "@soc2/pages/Risks";
import PoliciesPage from "@soc2/pages/Policies";
import PolicyCreate from "@shared/policy-manager/pages/PolicyCreate";
import PolicyDetail from "@shared/policy-manager/pages/PolicyDetail";
import FindingsPage from "@soc2/pages/Findings";
import VendorsPage from "@soc2/pages/Vendors";
import CriteriaPage from "@soc2/pages/Criteria";
import CriterionDetailPage from "@soc2/pages/CriterionDetail";
import EvidenceHubPage from "@soc2/pages/EvidenceHub";
import EvidenceRequestsPage from "@soc2/pages/EvidenceRequests";
import AuditPage from "@soc2/pages/Audit";
import AuditLogPage from "@soc2/pages/AuditLog";
import Soc2AssetsPage from "@soc2/pages/Assets";
import ReportsPage from "@soc2/pages/Reports";
import CmmcIntegrationsPage from "@cmmc/pages/Integrations";
import TeamPage from "@shared/personnel/pages/PersonnelDashboard";
import TrainingPage from "@shared/training/pages/TrainingPage";
import VendorDetailPage from "@shared/vendor-manager/pages/VendorDetail";
import VendorNewPage from "@shared/vendor-manager/pages/VendorNew";
import VendorComparePage from "@shared/vendor-manager/pages/VendorCompare";
import IncidentsListPage from "@soc2/pages/IncidentsList";
import IncidentsDetailPage from "@soc2/pages/IncidentsDetail";
import IncidentsNewPage from "@soc2/pages/IncidentsNew";
import IncidentDashboardPage from "@soc2/pages/IncidentDashboard";
import IncidentNotificationsPage from "@soc2/pages/IncidentNotifications";
import IncidentsEditPage from "@soc2/pages/IncidentsEdit";
import ReviewsList from "@shared/reviews/pages/ReviewsList";
import { api } from "@cmmc/api";
import ScopingPage from "@soc2/pages/Scoping";
import EvidenceCoveragePage from "@soc2/pages/EvidenceCoverage";
import ComplianceCalendarPage from "@shared/compliance-calendar/pages/ComplianceCalendarPage";
import EffectivenessDashboard from "@shared/effectiveness/pages/EffectivenessDashboard";
import ControlTestsPage from "@shared/control-tests/pages/ControlTestsPage";
import TestingPage from "@soc2/pages/TestingPage";
import HelpPage from "@shared/settings/HelpPage";

/** Route elements for SOC 2 — must be a fragment, not a wrapper component (RR v7). */
export const soc2RouteElements = (
  <>
    <Route index element={<Soc2DashboardPage />} />
    <Route path="welcome" element={<WelcomePage />} />
    <Route path="organization" element={<OrganizationPage />} />
    <Route path="readiness" element={<ReadinessPage />} />
    <Route path="my-work" element={<MyWorkPage />} />
    <Route path="priority-queue" element={<PriorityQueuePage />} />
    <Route path="dashboard" element={<Soc2DashboardPage />} />
    <Route path="governance" element={<Soc2GovernanceDashboard />} />
    <Route path="exceptions">
      <Route index element={<ExceptionsPage />} />
      <Route path="new" element={<NewExceptionPage />} />
      <Route path=":id" element={<ExceptionDetailPage />} />
    </Route>
    <Route path="risks" element={<RisksPage />} />
    <Route path="policies">
      <Route index element={<PoliciesPage />} />
      <Route path="new" element={<PolicyCreate frameworkFilter="soc2" />} />
      <Route path=":id" element={<PolicyDetail />} />
    </Route>
    <Route path="findings" element={<FindingsPage />} />
    <Route path="vendors" element={<VendorsPage />} />
    <Route path="vendors/compare" element={<VendorComparePage />} />
    <Route path="vendors/new" element={<VendorNewPage />} />
    <Route path="vendors/:id" element={<VendorDetailPage />} />
    <Route path="criteria" element={<CriteriaPage />} />
    <Route path="criteria/:controlId" element={<CriterionDetailPage />} />
    <Route path="scoping" element={<ScopingPage />} />
    <Route path="evidence" element={<EvidenceHubPage />} />
    <Route path="evidence/requests" element={<EvidenceRequestsPage />} />
    <Route path="evidence/coverage" element={<EvidenceCoveragePage />} />
    <Route path="compliance-calendar" element={<ComplianceCalendarPage frameworkId="SOC2" />} />
    <Route path="effectiveness" element={<EffectivenessDashboard frameworkId="SOC 2" />} />
    <Route path="control-tests" element={<ControlTestsPage frameworkId="SOC 2" />} />
    <Route path="tests" element={<TestingPage />} />
    <Route path="audit" element={<AuditPage />} />
    <Route path="audits" element={<AuditList frameworkFilter="SOC2" />} />
    <Route path="audits/new" element={<AuditNew frameworkDefault="SOC2" />} />
    <Route path="audits/:id" element={<AuditDetail />} />
    <Route path="audit-log" element={<AuditLogPage />} />
    <Route path="reviews" element={<ReviewsList />} />
    <Route path="assets" element={<Soc2AssetsPage />} />
    <Route path="reports" element={<ReportsPage />} />
    <Route path="integrations" element={<CmmcIntegrationsPage />} />
    <Route path="help" element={<HelpPage getHelp={() => api.help()} />} />
    <Route path="team" element={<TeamPage />} />
    <Route path="training" element={<TrainingPage />} />
    <Route path="incidents" element={<IncidentsListPage />} />
    <Route path="incidents/new" element={<IncidentsNewPage />} />
    <Route path="incidents/:iid/edit" element={<IncidentsEditPage />} />
    <Route path="incidents/:iid" element={<IncidentsDetailPage />} />
    <Route path="incidents/dashboard" element={<IncidentDashboardPage />} />
    <Route path="incidents/notifications" element={<IncidentNotificationsPage />} />
  </>
);
