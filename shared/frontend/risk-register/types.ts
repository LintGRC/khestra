export type RiskCategory =
  | "security"
  | "privacy"
  | "operational"
  | "compliance"
  | "reputational"
  | "strategic"
  | "financial"
  | "third_party";

export type RiskStatus =
  | "identified"
  | "assessed"
  | "in_treatment"
  | "mitigated"
  | "accepted"
  | "monitoring"
  | "closed";

export type RiskTreatment = "mitigate" | "accept" | "transfer" | "avoid";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export type RiskItem = {
  id: string;
  title: string;
  description: string;
  category: string;
  framework: string;
  control_ids: string[];
  system_id: string;
  owner: string;
  status: string;
  inherent_likelihood: string;
  inherent_impact: string;
  residual_likelihood: string;
  residual_impact: string;
  treatment: string;
  controls: string;
  control_id: string;
  inherent_score: number;
  residual_score: number;
  inherent_level: string;
  residual_level: string;
  review_date: string;
  acceptance_expires: string;
  control_owner: string;
  acceptance_overdue?: boolean;
  acceptance_days_left?: number | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  closed_at: string;
  comments?: RiskComment[];
  framework_metadata?: Record<string, unknown>;
};

export type RiskComment = {
  id: string;
  author: string;
  body: string;
  created_at: string;
};

export type RiskCreateBody = {
  title: string;
  description?: string;
  category?: string;
  framework?: string;
  control_ids?: string[];
  system_id?: string;
  owner?: string;
  inherent_likelihood?: string;
  inherent_impact?: string;
  residual_likelihood?: string;
  residual_impact?: string;
  treatment?: string;
  controls?: string;
  control_id?: string;
  status?: string;
  review_date?: string;
  acceptance_expires?: string;
  control_owner?: string;
  framework_metadata?: Record<string, unknown>;
};

export type RiskUpdateBody = Partial<RiskCreateBody>;

export const LEVELS: readonly RiskLevel[] = ["low", "medium", "high", "critical"] as const;

export const CATEGORIES: readonly RiskCategory[] = [
  "operational",
  "strategic",
  "financial",
  "compliance",
  "reputational",
  "security",
  "privacy",
  "third_party",
] as const;

export const STATUSES: readonly RiskStatus[] = [
  "identified",
  "assessed",
  "in_treatment",
  "mitigated",
  "accepted",
  "monitoring",
  "closed",
] as const;

export const TREATMENTS: readonly RiskTreatment[] = [
  "mitigate",
  "accept",
  "transfer",
  "avoid",
] as const;
