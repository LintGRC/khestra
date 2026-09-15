import { Route } from "react-router-dom";
import Dashboard from "@iso27001/pages/Dashboard";
import SoaList from "@iso27001/pages/SoaList";
import SoaDetail from "@iso27001/pages/SoaDetail";
import { EvidenceHubPage } from "@shared/evidence-hub";
import ControlTestsPage from "@shared/control-tests/pages/ControlTestsPage";
import ComplianceCalendarPage from "@shared/compliance-calendar/pages/ComplianceCalendarPage";
import EffectivenessDashboard from "@shared/effectiveness/pages/EffectivenessDashboard";
import { RiskDashboard } from "@shared/risk-register";
import { PolicyDashboard } from "@shared/policy-manager";
import { FindingDashboard } from "@shared/audit-findings";
import { IncidentsListPage } from "@shared/incidents";
import { AuditList } from "@shared/audit-center";
import ReviewsList from "@shared/reviews/pages/ReviewsList";
import { AssetsPage } from "@shared/assets";
import { VendorDashboard } from "@shared/vendor-manager";
import { PersonnelDashboard } from "@shared/personnel";
import { TrainingPage } from "@shared/training";
import { AuditLogPage } from "@shared/audit-log";

const ISO = "ISO 27001";

/** Route elements for ISO 27001 — must be a fragment, not a wrapper component (RR v7). */
export const iso27001RouteElements = (
  <>
    <Route index element={<Dashboard />} />
    <Route path="soa" element={<SoaList />} />
    <Route path="soa/:id" element={<SoaDetail />} />
    <Route path="evidence" element={<EvidenceHubPage />} />
    <Route path="control-tests" element={<ControlTestsPage frameworkId={ISO} />} />
    <Route path="compliance-calendar" element={<ComplianceCalendarPage frameworkId={ISO} />} />
    <Route path="effectiveness" element={<EffectivenessDashboard frameworkId={ISO} />} />
    <Route path="risks" element={<RiskDashboard />} />
    <Route path="policies" element={<PolicyDashboard />} />
    <Route path="findings" element={<FindingDashboard />} />
    <Route path="incidents" element={<IncidentsListPage />} />
    <Route path="audits" element={<AuditList />} />
    <Route path="reviews" element={<ReviewsList />} />
    <Route path="assets" element={<AssetsPage />} />
    <Route path="vendors" element={<VendorDashboard />} />
    <Route path="team" element={<PersonnelDashboard />} />
    <Route path="training" element={<TrainingPage />} />
    <Route path="audit-log" element={<AuditLogPage />} />
  </>
);
