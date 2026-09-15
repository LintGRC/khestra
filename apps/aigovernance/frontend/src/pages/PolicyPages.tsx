import PolicyDashboard from "@shared/policy-manager/pages/PolicyDashboard";
import PolicyCreate from "@shared/policy-manager/pages/PolicyCreate";
import PolicyDetail from "@shared/policy-manager/pages/PolicyDetail";

export function PoliciesListPage() {
  return <PolicyDashboard defaultFramework="aigovernance" />;
}

export function PolicyCreatePage() {
  return <PolicyCreate frameworkFilter="ai" />;
}

export function PolicyDetailPage() {
  return <PolicyDetail />;
}
