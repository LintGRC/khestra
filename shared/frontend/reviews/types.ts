export type ReviewItem = {
  id: string;
  type: string;
  title: string;
  description: string;
  frequency: string;
  owner_id: string;
  owner_name: string;
  scheduled_date: string;
  completed_date: string;
  status: string;
  evidence_ids: string[];
  findings: Record<string, any>[];
  control_ids: string[];
  framework_id: string;
  workspace_id: string;
  org_id: string;
  created_at: string;
  updated_at: string;
};

export const REVIEW_TYPE_LABELS: Record<string, string> = {
  access_review: "Access Review",
  policy_review: "Policy Review",
  vendor_review: "Vendor Review",
  bcp_dr_test: "BCP / DR Test",
  risk_review: "Risk Review",
  firewall_review: "Firewall Review",
};
