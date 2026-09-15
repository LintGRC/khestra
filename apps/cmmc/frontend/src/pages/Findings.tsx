import { useNavigate, useLocation } from "react-router-dom";
import FindingDashboard from "@shared/audit-findings/pages/FindingDashboard";
import type { FindingItem } from "@shared/audit-findings/types";

export default function FindingsPage() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  const handleCreatePoam = (finding: FindingItem) => {
    const params = new URLSearchParams({
      finding_title: finding.title,
      finding_description: finding.description,
      finding_control_id: (finding.control_ids || [])[0] || "",
      finding_framework: finding.framework || "CMMC",
      finding_owner: finding.owner,
      finding_severity: finding.severity,
    });
    navigate(`${fwBase}/poam/new?${params.toString()}`);
  };

  return (
    <FindingDashboard
      frameworkFilter="cmmc"
      onControlClick={(controlId) => navigate(`${fwBase}/controls/${encodeURIComponent(controlId)}`)}
      onCreatePoam={handleCreatePoam}
    />
  );
}
