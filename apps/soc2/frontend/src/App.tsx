import { Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import { api } from "./api";
import DashboardPage from "./pages/Dashboard";
import WelcomePage from "./pages/Welcome";
import OrganizationPage from "./pages/Organization";
import ScopingPage from "./pages/Scoping";
import ReadinessPage from "./pages/Readiness";
import MyWorkPage from "./pages/MyWork";
import PriorityQueuePage from "./pages/PriorityQueue";
import CriteriaPage from "./pages/Criteria";
import CriterionDetailPage from "./pages/CriterionDetail";
import EvidenceHubPage from "./pages/EvidenceHub";
import EvidenceRequestsPage from "./pages/EvidenceRequests";
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
import ExceptionsPage from "./pages/Exceptions";
import NewExceptionPage from "./pages/NewException";
import ExceptionDetailPage from "./pages/ExceptionDetail";
import RisksPage from "./pages/Risks";
import PoliciesPage from "./pages/Policies";
import FindingsPage from "./pages/Findings";
import VendorsPage from "./pages/Vendors";
import NewVendorPage from "./pages/NewVendor";
import VendorDetailPage from "./pages/VendorDetailPage";
import AuditPage from "./pages/Audit";
import AuditLogPage from "./pages/AuditLog";
import AuditList from "@shared/audit-center/pages/AuditList";
import AuditNew from "@shared/audit-center/pages/AuditNew";
import AuditDetail from "@shared/audit-center/pages/AuditDetail";
import TrainingPage from "./pages/Training";
import ReportsPage from "./pages/Reports";
import IntegrationsPage from "./pages/Integrations";
import GovernanceDashboardPage from "./pages/GovernanceDashboard";
import TestingPage from "./pages/TestingPage";
import TeamPage from "./pages/Team";
import AssetsPage from "./pages/Assets";
import PolicyCreatePage from "@shared/policy-manager/pages/PolicyCreate";
import PolicyDetailPage from "@shared/policy-manager/pages/PolicyDetail";
import ReviewsList from "@shared/reviews/pages/ReviewsList";
import HelpPage from "@shared/settings/HelpPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="governance" element={<GovernanceDashboardPage />} />
        <Route path="welcome" element={<WelcomePage />} />
        <Route path="organization" element={<OrganizationPage />} />
        <Route path="scoping" element={<ScopingPage />} />
        <Route path="readiness" element={<ReadinessPage />} />
        <Route path="my-work" element={<MyWorkPage />} />
        <Route path="priority-queue" element={<PriorityQueuePage />} />
        <Route path="criteria" element={<CriteriaPage />} />
        <Route path="criteria/:controlId" element={<CriterionDetailPage />} />
        <Route path="evidence" element={<EvidenceHubPage />} />
        <Route path="evidence/requests" element={<EvidenceRequestsPage />} />
        <Route path="evidence/coverage" element={<EvidenceCoveragePage />} />
        <Route path="compliance-calendar" element={<ComplianceCalendarPage frameworkId="SOC2" />} />
        <Route path="effectiveness" element={<EffectivenessDashboard frameworkId="SOC 2" />} />
        <Route path="control-tests" element={<ControlTestsPage frameworkId="SOC 2" />} />
        <Route path="incidents" element={<IncidentsListPage />} />
        <Route path="incidents/new" element={<IncidentsNewPage />} />
        <Route path="incidents/:iid/edit" element={<IncidentsEditPage />} />
        <Route path="incidents/:iid" element={<IncidentsDetailPage />} />
        <Route path="incidents/dashboard" element={<IncidentDashboardPage />} />
        <Route path="incidents/notifications" element={<IncidentNotificationsPage />} />
        <Route path="exceptions">
          <Route index element={<ExceptionsPage />} />
          <Route path="new" element={<NewExceptionPage />} />
          <Route path=":id" element={<ExceptionDetailPage />} />
        </Route>
        <Route path="risks" element={<RisksPage />} />
        <Route path="policies">
          <Route index element={<PoliciesPage />} />
          <Route path="new" element={<PolicyCreatePage />} />
          <Route path=":id" element={<PolicyDetailPage />} />
        </Route>
        <Route path="assets" element={<AssetsPage />} />
        <Route path="findings" element={<FindingsPage />} />
        <Route path="vendors">
          <Route index element={<VendorsPage />} />
          <Route path="new" element={<NewVendorPage />} />
          <Route path=":id" element={<VendorDetailPage />} />
        </Route>
        <Route path="tests" element={<TestingPage />} />
        <Route path="audits" element={<AuditList frameworkFilter="SOC2" />} />
        <Route path="audits/new" element={<AuditNew frameworkDefault="SOC2" />} />
        <Route path="audits/:id" element={<AuditDetail />} />
        <Route path="audit" element={<AuditPage />} />
        <Route path="audit-log" element={<AuditLogPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="reviews" element={<ReviewsList />} />
        <Route path="help" element={<HelpPage getHelp={api.help} />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="team" element={<TeamPage />} />
        <Route path="training" element={<TrainingPage />} />
      </Route>
    </Routes>
  );
}
