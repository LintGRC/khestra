export interface Attendee {
  name: string;
  role: string;
}

export interface ReviewInput {
  key: string;
  label: string;
  reviewed: boolean;
  note?: string;
}

export interface ReviewOutput {
  decision: string;
  category: string;
  owner: string;
  target_date: string;
}

export interface ActionItem {
  description: string;
  owner: string;
  target_date: string;
  status: string;
}

export interface ManagementReview {
  id: string;
  title: string;
  date: string;
  status: string;
  attendees: Attendee[];
  inputs: ReviewInput[];
  outputs: ReviewOutput[];
  action_items: ActionItem[];
  minutes: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewCreateBody {
  title?: string;
  date?: string;
  status?: string;
  attendees?: Attendee[];
  inputs?: ReviewInput[];
  outputs?: ReviewOutput[];
  action_items?: ActionItem[];
  minutes?: string;
}

export const REVIEW_STATUSES = ["scheduled", "in_progress", "completed"] as const;

export const OUTPUT_CATEGORY_LABELS: Record<string, string> = {
  improvement: "Improvement opportunity",
  resource: "Resource needs",
  policy: "Policy / objective change",
  risk_acceptance: "Risk acceptance",
  other: "Other decision",
};
