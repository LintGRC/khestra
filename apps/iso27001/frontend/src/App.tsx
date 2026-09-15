import { Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import Dashboard from "./pages/Dashboard";
import SoaList from "./pages/SoaList";
import SoaDetail from "./pages/SoaDetail";
import RiskAssessmentPage from "./pages/RiskAssessment";
import { EvidenceHubPage } from "@shared/evidence-hub";
import ControlTestsPage from "@shared/control-tests/pages/ControlTestsPage";
import ComplianceCalendarPage from "@shared/compliance-calendar/pages/ComplianceCalendarPage";
import EffectivenessDashboard from "@shared/effectiveness/pages/EffectivenessDashboard";
import { RiskDashboard } from "@shared/risk-register";
import { PolicyDashboard } from "@shared/policy-manager";
import { FindingDashboard } from "@shared/audit-findings";
import { IncidentsListPage, IncidentsNewPage, IncidentsDetailPage, IncidentsEditPage, IncidentDashboardPage, IncidentNotificationsPage } from "@shared/incidents";
import { AuditList, AuditNew, AuditDetail } from "@shared/audit-center";
import { PolicyCreate, PolicyDetail } from "@shared/policy-manager";
import { VendorNew, VendorDetail, VendorCompare } from "@shared/vendor-manager";
import ReviewsList from "@shared/reviews/pages/ReviewsList";
import { ContextScopePage } from "@shared/org-context";
import { ManagementReviewPage } from "@shared/management-review";
import { AssetsPage } from "@shared/assets";
import { VendorDashboard } from "@shared/vendor-manager";
import { PersonnelDashboard } from "@shared/personnel";
import { TrainingPage } from "@shared/training";
import { AuditLogPage } from "@shared/audit-log";
import IntegrationsPage from "./pages/Integrations";

const ISO = "ISO 27001";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="soa" element={<SoaList />} />
        <Route path="soa/:id" element={<SoaDetail />} />
        <Route path="risk-assessment" element={<RiskAssessmentPage />} />
        <Route path="evidence" element={<EvidenceHubPage />} />
        <Route path="control-tests" element={<ControlTestsPage frameworkId={ISO} />} />
        <Route path="compliance-calendar" element={<ComplianceCalendarPage frameworkId={ISO} />} />
        <Route path="effectiveness" element={<EffectivenessDashboard frameworkId={ISO} />} />
        <Route path="risks" element={<RiskDashboard />} />
        <Route path="policies" element={<PolicyDashboard />} />
        <Route path="policies/new" element={<PolicyCreate />} />
        <Route path="policies/:id" element={<PolicyDetail />} />
        <Route path="findings" element={<FindingDashboard />} />
        <Route path="incidents" element={<IncidentsListPage />} />
        <Route path="incidents/new" element={<IncidentsNewPage />} />
        <Route path="incidents/:iid/edit" element={<IncidentsEditPage />} />
        <Route path="incidents/:iid" element={<IncidentsDetailPage />} />
        <Route path="incidents/dashboard" element={<IncidentDashboardPage />} />
        <Route path="incidents/notifications" element={<IncidentNotificationsPage />} />
        <Route path="audits" element={<AuditList frameworkFilter={ISO} />} />
        <Route path="audits/new" element={<AuditNew frameworkDefault={ISO} />} />
        <Route path="audits/:id" element={<AuditDetail />} />
        <Route path="reviews" element={<ReviewsList />} />
        <Route path="context" element={<ContextScopePage />} />
        <Route path="management-review" element={<ManagementReviewPage />} />
        <Route path="assets" element={<AssetsPage />} />
        <Route path="vendors" element={<VendorDashboard />} />
        <Route path="vendors/new" element={<VendorNew />} />
        <Route path="vendors/:id" element={<VendorDetail />} />
        <Route path="vendors/compare" element={<VendorCompare />} />
        <Route path="team" element={<PersonnelDashboard />} />
        <Route path="training" element={<TrainingPage />} />
        <Route path="audit-log" element={<AuditLogPage />} />
        <Route path="integrations" element={<IntegrationsPage />} />
      </Route>
    </Routes>
  );
}