import { Route, Routes, Navigate } from "react-router-dom";
import UnifiedDashboard from "./pages/UnifiedDashboard";
import UnifiedPosturePage from "./pages/UnifiedPosture";
import FrameworkSwitcher from "./framework/FrameworkSwitcher";
import RootLayout from "./framework/RootLayout";
import CmmcLayout from "@cmmc/Layout";
import Soc2Layout from "@soc2/Layout";
import AiGovernanceLayout from "@aigov/Layout";
import Iso27001Layout from "@iso27001/Layout";
import { aigovernanceRouteElements } from "@aigov/routeElements";
import { cmmcRouteElements } from "./routes/CmmcRoutes";
import { soc2RouteElements } from "./routes/Soc2Routes";
import { iso27001RouteElements } from "./routes/Iso27001Routes";
import PolicyDashboard from "@shared/policy-manager/pages/PolicyDashboard";
import PolicyCreate from "@shared/policy-manager/pages/PolicyCreate";
import PolicyDetail from "@shared/policy-manager/pages/PolicyDetail";
import GlobalAssetsPage from "./pages/global/GlobalAssetsPage";
import GlobalVendorsPage from "./pages/global/GlobalVendorsPage";
import GlobalEvidencePage from "./pages/global/GlobalEvidencePage";
import GlobalIncidentsPage from "./pages/global/GlobalIncidentsPage";
import GlobalAuditLogPage from "./pages/global/GlobalAuditLogPage";
import GlobalAuditTrackerPage from "./pages/global/GlobalAuditTrackerPage";
import GlobalRisksPage from "./pages/global/GlobalRisksPage";
import CollectorsPage from "./pages/global/CollectorsPage";
import RemediationQueuePage from "./pages/global/RemediationQueuePage";
import ComplianceCalendarPage from "@shared/compliance-calendar/pages/ComplianceCalendarPage";
import EffectivenessDashboard from "@shared/effectiveness/pages/EffectivenessDashboard";
import ControlTestsPage from "@shared/control-tests/pages/ControlTestsPage";
import TrustCenterPage from "@shared/trust-center/TrustCenterPage";

const frameworkSwitcher = <FrameworkSwitcher />;

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<UnifiedDashboard />} />
        <Route path="posture" element={<UnifiedPosturePage />} />
        <Route path="collectors" element={<CollectorsPage />} />
        <Route path="remediation" element={<RemediationQueuePage />} />
        <Route path="policies">
          <Route index element={<PolicyDashboard />} />
          <Route path="new" element={<PolicyCreate />} />
          <Route path=":id" element={<PolicyDetail />} />
        </Route>
        <Route path="assets" element={<GlobalAssetsPage />} />
        <Route path="vendors" element={<GlobalVendorsPage />} />
        <Route path="vendors/compare" element={<GlobalVendorsPage />} />
        <Route path="evidence" element={<GlobalEvidencePage />} />
        <Route path="incidents" element={<GlobalIncidentsPage />} />
        <Route path="incidents/dashboard" element={<GlobalIncidentsPage />} />
        <Route path="audits" element={<GlobalAuditTrackerPage />} />
        <Route path="audit-log" element={<GlobalAuditLogPage />} />
        <Route path="risks" element={<GlobalRisksPage />} />
        <Route path="compliance-calendar" element={<ComplianceCalendarPage />} />
        <Route path="effectiveness" element={<EffectivenessDashboard />} />
        <Route path="control-tests" element={<ControlTestsPage />} />
        <Route path="trust" element={<TrustCenterPage />} />
      </Route>
      <Route path="/cmmc/*" element={<CmmcLayout frameworkSwitcher={frameworkSwitcher} />}>
        {cmmcRouteElements}
      </Route>
      <Route path="/soc2/*" element={<Soc2Layout frameworkSwitcher={frameworkSwitcher} />}>
        {soc2RouteElements}
      </Route>
      <Route path="/aigov/*" element={<AiGovernanceLayout frameworkSwitcher={frameworkSwitcher} />}>
        {aigovernanceRouteElements}
      </Route>
      <Route path="/iso27001/*" element={<Iso27001Layout frameworkSwitcher={frameworkSwitcher} />}>
        {iso27001RouteElements}
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
