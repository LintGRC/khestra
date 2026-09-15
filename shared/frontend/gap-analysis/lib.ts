import { CATEGORIES, QUESTIONS, type Question, type Result } from "./types";

export function getQuestions(scopeAnswers: Record<string, boolean>): Question[] {
  return QUESTIONS.filter((q) => {
    if (!q.scopeGate) return true;
    return scopeAnswers[q.scopeGate] !== false;
  });
}

export function getActiveCategories(scopeAnswers: Record<string, boolean>): typeof CATEGORIES {
  return CATEGORIES.filter((c) => {
    if (!c.gate) return true;
    return scopeAnswers[c.gate] !== false;
  });
}

export function getQuestionsByCategory(scopeAnswers: Record<string, boolean>): Record<string, Question[]> {
  const active = getActiveCategories(scopeAnswers);
  const all = getQuestions(scopeAnswers);
  const grouped: Record<string, Question[]> = {};
  for (const cat of active) {
    grouped[cat.id] = all.filter((q) => q.category === cat.id);
  }
  return grouped;
}

export function countTotalQuestions(scopeAnswers: Record<string, boolean>): number {
  return getQuestions(scopeAnswers).length;
}

export function computeGaps(answers: Record<string, boolean>, scopeAnswers: Record<string, boolean>): Result[] {
  const activeCats = getActiveCategories(scopeAnswers);
  const results: Result[] = [];
  for (const cat of activeCats) {
    const catQuestions = getQuestions(scopeAnswers).filter((q) => q.category === cat.id);
    if (catQuestions.length === 0) continue;
    const answered = catQuestions.filter((q) => answers[q.id] === true);
    const gaps = catQuestions.filter((q) => !answers[q.id]);
    results.push({
      category: cat.id,
      label: cat.label,
      framework: cat.framework,
      score: answered.length,
      max: catQuestions.length,
      percent: Math.round((answered.length / catQuestions.length) * 100),
      gaps: gaps.map((q) => ({ id: q.id, text: q.text, clause: q.clause, hint: q.hint })),
    });
  }
  return results;
}

export function overallScore(results: Result[]): number {
  const total = results.reduce((s, r) => s + r.score, 0);
  const max = results.reduce((s, r) => s + r.max, 0);
  return max > 0 ? Math.round((total / max) * 100) : 0;
}

export function exportAssessmentCSV(answers: Record<string, boolean>, scopeAnswers: Record<string, boolean>): string {
  const all = getQuestions(scopeAnswers);
  const headers = ["ID", "Clause", "Framework", "Category", "Question", "Status", "Notes"];
  const rows = all.map((q) => [
    q.id, q.clause, q.framework, q.category, q.text,
    answers[q.id] ? "Met" : "Gap",
    answers[q.id] ? "" : (q.hint || ""),
  ]);
  return [headers.join(","), ...rows.map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(","))].join("\n");
}
