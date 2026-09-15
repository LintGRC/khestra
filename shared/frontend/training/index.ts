export { trainingApi } from "./api";
export type {
  TrainingModule, TrainingModuleCreate, TrainingModuleUpdate,
  TrainingAssignment, AssignmentCreate, AssignmentUpdate,
  BulkAssignBody, BulkCompleteBody, TrainingStats, TrainingStatus,
  TrainingAlerts, TrainingAlertItem,
} from "./types";
export { TRAINING_STATUSES } from "./types";
export { default as TrainingPage } from "./pages/TrainingPage";
