import { authHeaders } from "@shared/accessToken";
import { fetchJson } from "@shared/fetchJson";
import { apiUrl } from "@shared/apiPrefix";
import type {
  TrainingModule, TrainingModuleCreate, TrainingModuleUpdate,
  TrainingAssignment, AssignmentCreate, AssignmentUpdate,
  BulkAssignBody, BulkCompleteBody, TrainingStats, TrainingAlerts,
  QuizResult,
} from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await authHeaders({
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  });
  return fetchJson<T>(apiUrl(path), { ...init, headers });
}

export const trainingApi = {
  // Modules
  listModules: (params?: { control_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.control_id) qs.set("control_id", params.control_id);
    const q = qs.toString();
    return json<{ modules: TrainingModule[] }>(`/api/training/modules${q ? `?${q}` : ""}`);
  },

  getModule: (id: string) =>
    json<{ module: TrainingModule }>(`/api/training/modules/${encodeURIComponent(id)}`),

  createModule: (body: TrainingModuleCreate) =>
    json<{ module: TrainingModule }>("/api/training/modules", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateModule: (id: string, body: TrainingModuleUpdate) =>
    json<{ module: TrainingModule }>(`/api/training/modules/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteModule: (id: string) =>
    json<{ status: string }>(`/api/training/modules/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  // Assignments
  listAssignments: (params?: { module_id?: string; status?: string; person_id?: string }) => {
    const qs = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => { if (v) qs.set(k, v); });
    }
    const q = qs.toString();
    return json<{ assignments: TrainingAssignment[] }>(`/api/training/assignments${q ? `?${q}` : ""}`);
  },

  getAssignment: (id: string) =>
    json<{ assignment: TrainingAssignment }>(`/api/training/assignments/${encodeURIComponent(id)}`),

  createAssignment: (body: AssignmentCreate) =>
    json<{ assignment: TrainingAssignment }>("/api/training/assignments", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  bulkAssign: (body: BulkAssignBody) =>
    json<{ assignments: TrainingAssignment[]; count: number }>("/api/training/assignments/bulk", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  bulkComplete: (body: BulkCompleteBody) =>
    json<{ updated: number }>("/api/training/assignments/bulk-complete", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateAssignment: (id: string, body: AssignmentUpdate) =>
    json<{ assignment: TrainingAssignment }>(`/api/training/assignments/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteAssignment: (id: string) =>
    json<{ status: string }>(`/api/training/assignments/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),

  // Stats
  stats: () =>
    json<TrainingStats>("/api/training/stats"),

  // Auto-assign & Alerts
  autoAssign: () =>
    json<{ created: number; skipped: number; error?: string }>("/api/training/auto-assign", {
      method: "POST",
    }),

  alerts: () =>
    json<TrainingAlerts>("/api/training/alerts"),
  // Quiz
  quizSubmit: (assignmentId: string, answers: number[]) =>
    json<QuizResult>("/api/training/quiz/submit", {
      method: "POST",
      body: JSON.stringify({ assignment_id: assignmentId, answers }),
    }),
};
