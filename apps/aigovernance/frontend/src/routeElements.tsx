import { Route } from "react-router-dom";
import AuditList from "@shared/audit-center/pages/AuditList";
import AuditNew from "@shared/audit-center/pages/AuditNew";
import AuditDetail from "@shared/audit-center/pages/AuditDetail";
import { GovernanceDashboardPage } from "./pages/GovernanceDashboard";
import { SystemsListPage } from "./pages/SystemsList";
import { SystemsDetailPage } from "./pages/SystemsDetail";
import { SystemsNewPage } from "./pages/SystemsNew";
import { SystemsEditPage } from "./pages/SystemsEdit";
import { SystemsClassifyPage } from "./pages/SystemsClassify";
import { EvaluationsListPage } from "./pages/EvaluationsListPage";
import { EvaluationsDetailPage } from "./pages/EvaluationsDetailPage";
import { EvaluationsNewPage } from "./pages/EvaluationsNewPage";
import { TrainingDataListPage } from "./pages/TrainingDataListPage";
import { TrainingDataDetailPage } from "./pages/TrainingDataDetailPage";
import { TrainingDataNewPage } from "./pages/TrainingDataNewPage";
import IncidentsListPage from "./pages/IncidentsList";
import IncidentsDetailPage from "./pages/IncidentsDetail";
import IncidentsNewPage from "./pages/IncidentsNew";
import IncidentDashboardPage from "./pages/IncidentDashboard";
import IncidentNotificationsPage from "./pages/IncidentNotifications";
import IncidentsEditPage from "./pages/IncidentsEdit";
import { FriaListPage, FriaDetailPage, FriaNewPage } from "./pages/FriaPages";
import { FriaLandingPage } from "./pages/FriaLanding";
import RisksPage from "./pages/RiskPages";
import { PoliciesListPage, PolicyCreatePage, PolicyDetailPage } from "./pages/PolicyPages";
import { FindingsListPage } from "./pages/FindingPages";
import { VendorListPage, VendorDetailPage, VendorNewPage, VendorComparePage } from "./pages/VendorPages";
import { VendorQuestionnairePortal } from "./pages/VendorQuestionnairePortal";
import { PlansListPage } from "./pages/PlansListPage";
import { PlansDetailPage } from "./pages/PlansDetailPage";
import { PlansNewPage } from "./pages/PlansNewPage";
import { ContractsListPage } from "./pages/ContractsListPage";
import { ContractsDetailPage } from "./pages/ContractsDetailPage";
import { ReadinessChecklistPage } from "./pages/ReadinessChecklistPage";
import { AuditReportPage } from "./pages/AuditReportPage";
import { CompetencePage } from "./pages/CompetencePage";
import { GapAnalysisPage } from "./pages/GapAnalysisPage";
import IntegrationsPage from "./pages/Integrations";
import { AuditLogPage } from "./pages/AuditLogPage";
import { ConformityAssessmentPage } from "./pages/ConformityAssessmentPage";
import { DossierPage } from "./pages/DossierPage";
import { TabletopLandingPage, TabletopPlayPage, TabletopExercisesPage, TabletopDetailPage } from "./pages/TabletopPages";
import ReviewCyclesPage from "./pages/ReviewCyclesPage";
import AssetsPage from "./pages/AssetsPage";
import EvidenceHubPage from "./pages/EvidenceHubPage";
import EvidenceCoveragePage from "./pages/EvidenceCoveragePage";
import ComplianceCalendarPage from "@shared/compliance-calendar/pages/ComplianceCalendarPage";
import EffectivenessDashboard from "@shared/effectiveness/pages/EffectivenessDashboard";
import ControlTestsPage from "@shared/control-tests/pages/ControlTestsPage";
import TeamPage from "@shared/personnel/pages/PersonnelDashboard";
import TrainingPage from "@shared/training/pages/TrainingPage";
import HelpPage from "@shared/settings/HelpPage";
import { api } from "./api";

export const aigovernanceRouteElements = (
  <>
    <Route index element={<GovernanceDashboardPage />} />
    <Route path="dashboard" element={<GovernanceDashboardPage />} />
    <Route path="systems" element={<SystemsListPage />} />
    <Route path="systems/new" element={<SystemsNewPage />} />
    <Route path="systems/:id" element={<SystemsDetailPage />} />
    <Route path="systems/:id/edit" element={<SystemsEditPage />} />
    <Route path="systems/:id/classify" element={<SystemsClassifyPage />} />
    <Route path="incidents" element={<IncidentsListPage />} />
    <Route path="incidents/new" element={<IncidentsNewPage />} />
    <Route path="incidents/:iid/edit" element={<IncidentsEditPage />} />
    <Route path="incidents/:iid" element={<IncidentsDetailPage />} />
    <Route path="incidents/dashboard" element={<IncidentDashboardPage />} />
    <Route path="incidents/notifications" element={<IncidentNotificationsPage />} />
    <Route path="frias" element={<FriaLandingPage />} />
    <Route path="frias/list" element={<FriaListPage />} />
    <Route path="frias/new" element={<FriaNewPage />} />
    <Route path="frias/:id" element={<FriaDetailPage />} />
    <Route path="risks" element={<RisksPage />} />
    <Route path="compliance-calendar" element={<ComplianceCalendarPage frameworkId="AIGov" />} />
    <Route path="effectiveness" element={<EffectivenessDashboard frameworkId="AI Gov" />} />
    <Route path="control-tests" element={<ControlTestsPage frameworkId="AI Gov" />} />
    <Route path="policies">
      <Route index element={<PoliciesListPage />} />
      <Route path="new" element={<PolicyCreatePage />} />
      <Route path=":id" element={<PolicyDetailPage />} />
    </Route>
    <Route path="findings" element={<FindingsListPage />} />
    <Route path="vendors" element={<VendorListPage />} />
    <Route path="vendors/compare" element={<VendorComparePage />} />
    <Route path="vendors/new" element={<VendorNewPage />} />
    <Route path="vendors/:id" element={<VendorDetailPage />} />
    <Route path="questionnaire/:vid" element={<VendorQuestionnairePortal />} />
    <Route path="plans" element={<PlansListPage />} />
    <Route path="plans/new" element={<PlansNewPage />} />
    <Route path="plans/:id" element={<PlansDetailPage />} />
    <Route path="contracts" element={<ContractsListPage />} />
    <Route path="contracts/new" element={<ContractsListPage />} />
    <Route path="contracts/:id" element={<ContractsDetailPage />} />
    <Route path="readiness" element={<ReadinessChecklistPage />} />
    <Route path="readiness/:id" element={<ReadinessChecklistPage />} />
    <Route path="controls" element={<ReadinessChecklistPage />} />
    <Route path="controls/:id" element={<ReadinessChecklistPage />} />
    <Route path="audit-report" element={<AuditReportPage />} />
    <Route path="competence" element={<CompetencePage />} />
    <Route path="gap-analysis" element={<GapAnalysisPage />} />
    <Route path="audits" element={<AuditList frameworkFilter="AIGov" />} />
    <Route path="audits/new" element={<AuditNew frameworkDefault="AIGov" />} />
    <Route path="audits/:id" element={<AuditDetail />} />
    <Route path="audit" element={<AuditLogPage />} />
    <Route path="evidence" element={<EvidenceHubPage />} />
    <Route path="evidence/coverage" element={<EvidenceCoveragePage />} />
    <Route path="evaluations" element={<EvaluationsListPage />} />
    <Route path="evaluations/new" element={<EvaluationsNewPage />} />
    <Route path="evaluations/:id" element={<EvaluationsDetailPage />} />
    <Route path="training-data" element={<TrainingDataListPage />} />
    <Route path="training-data/new" element={<TrainingDataNewPage />} />
    <Route path="training-data/:id" element={<TrainingDataDetailPage />} />
    <Route path="systems/:id/conformity" element={<ConformityAssessmentPage />} />
    <Route path="systems/:id/dossier" element={<DossierPage />} />
    <Route path="tabletop" element={<TabletopLandingPage />} />
    <Route path="tabletop/play/:scenarioId" element={<TabletopPlayPage />} />
    <Route path="tabletop/exercises" element={<TabletopExercisesPage />} />
    <Route path="tabletop/exercises/:id" element={<TabletopDetailPage />} />
    <Route path="review-cycles" element={<ReviewCyclesPage />} />
    <Route path="assets" element={<AssetsPage />} />
    <Route path="team" element={<TeamPage />} />
    <Route path="training" element={<TrainingPage />} />
    <Route path="integrations" element={<IntegrationsPage />} />
    <Route path="help" element={<HelpPage getHelp={() => api.help()} />} />
  </>
);
