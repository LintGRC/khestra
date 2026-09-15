export type TrainingStatus = "assigned" | "in_progress" | "completed" | "overdue" | "exempt";

export const TRAINING_STATUSES = ["assigned", "in_progress", "completed", "overdue", "exempt"] as const;

export type TrainingModule = {
  id: string;
  title: string;
  description: string;
  category: string;
  is_required: boolean;
  renewal_period_days: number;
  control_ids: string[];
  content_md?: string;
  quiz_questions?: QuizQuestion[];
  created_by: string;
  created_at: string;
  updated_at: string;
};

export type TrainingModuleCreate = {
  title: string;
  description?: string;
  category?: string;
  is_required?: boolean;
  renewal_period_days?: number;
  control_ids?: string[];
  created_by?: string;
};

export type TrainingModuleUpdate = Partial<TrainingModuleCreate>;

export type TrainingAssignment = {
  id: string;
  module_id: string;
  person_id: string;
  person_name: string;
  person_email: string;
  status: string;
  assigned_date: string;
  completion_date: string;
  expiry_date: string;
  evidence_id: string;
  notes: string;
  exemption_reason: string;
  exempted_by: string;
  exempted_date: string;
  created_at: string;
  updated_at: string;
};

export type AssignmentCreate = {
  module_id: string;
  person_id: string;
  assigned_date?: string;
};

export type AssignmentUpdate = {
  status?: string;
  completion_date?: string;
  expiry_date?: string;
  evidence_id?: string;
  notes?: string;
  exemption_reason?: string;
  exempted_by?: string;
  exempted_date?: string;
};

export type BulkAssignBody = {
  module_id: string;
  person_ids: string[];
  assigned_date?: string;
};

export type BulkCompleteBody = {
  assignment_ids: string[];
  completion_date: string;
};

export type TrainingStats = {
  total_modules: number;
  total_assignments: number;
  completed: number;
  overdue: number;
  exempt: number;
  completion_rate: number;
  per_module: {
    module_id: string;
    total: number;
    completed: number;
    overdue: number;
    exempt: number;
    rate: number;
  }[];
  per_person: {
    person_id: string;
    person_name: string;
    person_email: string;
    total: number;
    completed: number;
    overdue: number;
    rate: number;
  }[];
};

export type TrainingAlertItem = {
  id: string;
  person_id: string;
  person_name: string;
  person_email: string;
  module_id: string;
  module_title: string;
  status: string;
  expiry_date: string;
};

export type TrainingAlerts = {
  overdue_count: number;
  overdue: TrainingAlertItem[];
  expiring_soon_count: number;
  expiring_soon: TrainingAlertItem[];
};

export type QuizQuestion = {
  q: string;
  options: string[];
  correct: number;
};

export type QuizResult = {
  score: number;
  correct: number;
  total: number;
  passed: boolean;
};
