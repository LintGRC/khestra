import PolicyDashboard from "@shared/policy-manager/pages/PolicyDashboard";
import PageIntro from "../components/PageIntro";

export default function CmmcPoliciesPage() {
  return (
    <>
      <PageIntro view="Policies" title="Policies &amp; Attestations" />
      <PolicyDashboard defaultFramework="cmmc" hideHeader />
    </>
  );
}
