export type VendorStatus =
  | "pending"
  | "sent"
  | "responded"
  | "assessed"
  | "approved"
  | "rejected"
  | "under_review";

export type VendorItem = {
  id: string;
  name: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  website: string;
  product_service: string;
  category: string;
  ai_service_type: string;
  tier: string;
  tags: string[];
  status: string;
  risk_score: number | null;
  risk_level: string;
  frameworks: string[];
  data_residency: string[];
  transfer_mechanism: string;
  dpa_in_place: boolean;
  certificates: VendorCertificate[];
  reminder_count: number;
  org_id: string;
  workspace_id: string;
  created_at: string;
  updated_at: string;
  handles_cui: boolean;
  cmmc_level: string;
  sprs_score: number | null;
  flow_down_clause_signed: string;
  cui_categories: string[];
  last_assessment_date: string;
  soc_report_date: string;
  review_date: string;
  data_types: string[];
  soc_report_type: string;
  soc_report_opinion: string;
  soc_report_coverage_start: string;
  soc_report_coverage_end: string;
  next_review_due: string;
};

export type VendorCertificate = {
  id: string;
  type: string;
  filename: string;
  uploaded_at: string;
};

export type VendorAssessment = {
  id: string;
  vendor_id: string;
  response_id: string;
  overall_score: number;
  overall_level: string;
  category_scores: { category: string; score: number; level: string }[];
  findings: string[];
  created_at: string;
};

export type VendorRemediation = {
  id: string;
  vendor_id: string;
  assessment_id: string;
  description: string;
  priority: string;
  status: string;
  owner: string;
  due_date: string;
  created_at: string;
  updated_at: string;
};

export type VendorActivity = {
  id: string;
  vendor_id: string;
  action: string;
  detail: string;
  timestamp: string;
};

export const VENDOR_STATUSES: readonly VendorStatus[] = [
  "pending",
  "sent",
  "responded",
  "assessed",
  "approved",
  "rejected",
  "under_review",
] as const;

export const VENDOR_CATEGORIES = [
  "ai_platform",
  "cloud_provider",
  "data_processor",
  "consulting",
  "saas",
  "infrastructure",
  "other",
] as const;
