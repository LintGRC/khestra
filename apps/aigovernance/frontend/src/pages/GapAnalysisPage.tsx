import { useState, useEffect } from "react";
import { ArrowLeft, ArrowRight, CheckCircle, XCircle, Download, RotateCcw, BarChart3 } from "lucide-react";
import { SCOPING, CATEGORIES, type Question, type Result } from "@shared/gap-analysis/types";
import { computeGaps, overallScore, getActiveCategories, getQuestionsByCategory, exportAssessmentCSV } from "@shared/gap-analysis/lib";

const STORAGE_KEY = "khestra_gap_analysis";

function loadProgress(): { phase: number; scopeAnswers: Record<string, boolean>; answers: Record<string, boolean> } | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return null;
}

function saveProgress(phase: number, scopeAnswers: Record<string, boolean>, answers: Record<string, boolean>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ phase, scopeAnswers, answers }));
  } catch { /* ignore */ }
}

function clearProgress() {
  try { localStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ }
}

export function GapAnalysisPage() {
  const [phase, setPhase] = useState(0);
  const [scopeAnswers, setScopeAnswers] = useState<Record<string, boolean>>({});
  const [answers, setAnswers] = useState<Record<string, boolean>>({});
  const [categoryIndex, setCategoryIndex] = useState(0);
  const [results, setResults] = useState<Result[]>([]);
  const [expandedGap, setExpandedGap] = useState<string | null>(null);

  useEffect(() => {
    const saved = loadProgress();
    if (saved) {
      setPhase(saved.phase);
      setScopeAnswers(saved.scopeAnswers);
      setAnswers(saved.answers);
    }
  }, []);

  useEffect(() => {
    if (phase > 0) saveProgress(phase, scopeAnswers, answers);
  }, [phase, scopeAnswers, answers]);

  function startAssessment() {
    clearProgress();
    setPhase(1);
    setScopeAnswers({});
    setAnswers({});
    setCategoryIndex(0);
    setResults([]);
  }

  function handleScopeAnswer(id: string, value: boolean) {
    const updated = { ...scopeAnswers, [id]: value };
    setScopeAnswers(updated);
    if (value) {
      const q = SCOPING.find((s) => s.id === id);
      if (q?.ifNo) {
        for (const cid of q.ifNo.skipCategories || []) {
          const cat = CATEGORIES.find((c) => c.id === cid);
          if (cat?.gate === id) {
            const catQs = getQuestionsByCategory(updated)[cid] || [];
            for (const qq of catQs) {
              delete updated[qq.id];
            }
          }
        }
        for (const skipId of q.ifNo.skipIds || []) {
          delete updated[skipId];
        }
        setAnswers((prev) => {
          const next = { ...prev };
          for (const cid of q.ifNo?.skipCategories || []) {
            const catQs = getQuestionsByCategory(updated)[cid] || [];
            for (const qq of catQs) {
              delete next[qq.id];
            }
          }
          for (const skipId of q.ifNo?.skipIds || []) {
            delete next[skipId];
          }
          return next;
        });
      }
    }
  }

  function goToQuestions() {
    setPhase(2);
    setCategoryIndex(0);
  }

  function goToCategory(index: number) {
    const cats = getActiveCategories(scopeAnswers);
    if (index >= cats.length) {
      const r = computeGaps(answers, scopeAnswers);
      setResults(r);
      setPhase(3);
      clearProgress();
      return;
    }
    setCategoryIndex(index);
  }

  function handleAnswer(qid: string) {
    setAnswers((prev) => ({ ...prev, [qid]: !prev[qid] }));
  }

  function handleRestart() {
    clearProgress();
    setPhase(0);
    setScopeAnswers({});
    setAnswers({});
    setResults([]);
  }

  function copyResults() {
    const csv = exportAssessmentCSV(answers, scopeAnswers);
    navigator.clipboard.writeText(csv);
  }

  const activeCats = getActiveCategories(scopeAnswers);
  const groupedQs = getQuestionsByCategory(scopeAnswers);

  // Phase 0: Landing
  if (phase === 0) {
    return (
      <div className="page-stack">
        <div className="page-header">
          <h2>Gap Analysis</h2>
          <p className="muted">Self-assessment against NIST AI RMF and ISO 42001 frameworks</p>
        </div>
        <div className="panel" style={{ padding: 24, textAlign: "center" }}>
          <BarChart3 size={48} style={{ color: "var(--primary)", margin: "0 auto 16px", display: "block", opacity: 0.5 }} />
          <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 8px" }}>AI Governance Gap Analysis</h2>
          <p className="muted" style={{ fontSize: 13, maxWidth: 400, margin: "0 auto 20px" }}>
            Assess your organization&apos;s AI governance maturity across 7 categories mapped to NIST AI RMF and ISO 42001.
            The assessment takes 5-10 minutes.
          </p>
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
            {CATEGORIES.map((c) => (
              <span key={c.id} style={{ fontSize: 11, padding: "3px 10px", borderRadius: 20, border: "1px solid var(--border)", background: "var(--surface)" }}>{c.label}</span>
            ))}
          </div>
          <button className="btn btn-primary" onClick={startAssessment}>Start Assessment</button>
          {loadProgress() && (
            <button className="btn btn-secondary" style={{ marginLeft: 8 }} onClick={() => setPhase(loadProgress()!.phase)}>Resume Previous</button>
          )}
        </div>
      </div>
    );
  }

  // Phase 1: Scoping
  if (phase === 1) {
    return (
      <div className="page-stack">
        <div className="page-header">
          <h2>Gap Analysis</h2>
          <p className="muted">Step 1 of 3: Scope your assessment</p>
        </div>
        <div className="panel" style={{ padding: 20, width: "100%" }}>
          <div style={{ width: "100%", height: 4, background: "var(--info-soft)", borderRadius: 2, marginBottom: 20, overflow: "hidden" }}>
            <div style={{ width: "33%", height: "100%", background: "var(--primary)", borderRadius: 2 }} />
          </div>
          {SCOPING.map((q) => (
            <div key={q.id} style={{ marginBottom: 16, paddingBottom: 16, borderBottom: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>{q.text}</div>
              {q.hint && <div className="muted" style={{ fontSize: 11, marginBottom: 8 }}>{q.hint}</div>}
              <div style={{ display: "flex", gap: 8 }}>
                <button
                  className={`btn btn-sm ${scopeAnswers[q.id] === true ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => handleScopeAnswer(q.id, true)}
                >Yes</button>
                <button
                  className={`btn btn-sm ${scopeAnswers[q.id] === false ? "btn-primary" : "btn-secondary"}`}
                  style={scopeAnswers[q.id] === false ? { background: "var(--muted)", borderColor: "var(--muted)", color: "white" } : {}}
                  onClick={() => handleScopeAnswer(q.id, false)}
                >No</button>
              </div>
            </div>
          ))}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
            <button className="btn btn-primary" onClick={goToQuestions} disabled={Object.keys(scopeAnswers).length < SCOPING.length}>
              Next <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Phase 2: Questions
  if (phase === 2) {
    const cat = activeCats[categoryIndex];
    const questions = groupedQs[cat?.id] || [];
    const answered = questions.filter((q) => answers[q.id]).length;

    return (
      <div className="page-stack">
        <div className="page-header">
          <h2>Gap Analysis</h2>
          <p className="muted">Step 2 of 3: {cat?.label} ({categoryIndex + 1} of {activeCats.length})</p>
        </div>
        <div className="panel" style={{ padding: 20, width: "100%" }}>
          <div style={{ width: "100%", height: 4, background: "var(--info-soft)", borderRadius: 2, marginBottom: 20, overflow: "hidden" }}>
            <div style={{ width: `${((categoryIndex + 1) / activeCats.length) * 100}%`, height: "100%", background: "var(--primary)", borderRadius: 2 }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: 0 }}>{cat?.label}</h3>
              <span className="muted" style={{ fontSize: 11 }}>{cat?.framework} &middot; {cat?.description}</span>
            </div>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>{answered}/{questions.length}</span>
          </div>
          {questions.map((q: Question) => (
            <div key={q.id} onClick={() => handleAnswer(q.id)} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 0", borderBottom: "1px solid var(--border-subtle)", cursor: "pointer" }}>
              <input type="checkbox" readOnly checked={answers[q.id] || false} style={{ marginTop: 2, flexShrink: 0, pointerEvents: "none", width: "auto" }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 2 }}>{q.text}</div>
                <div className="muted" style={{ fontSize: 11 }}>{q.framework} &middot; {q.clause}{q.hint ? ` &middot; ${q.hint}` : ""}</div>
              </div>
            </div>
          ))}
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
            <button className="btn btn-secondary btn-sm" disabled={categoryIndex === 0} onClick={() => goToCategory(categoryIndex - 1)}>
              <ArrowLeft size={14} /> Previous
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => goToCategory(categoryIndex + 1)}>
              {categoryIndex < activeCats.length - 1 ? <>Next <ArrowRight size={14} /></> : "See Results"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Phase 3: Results
  const overall = overallScore(results);

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Gap Analysis Results</h2>
        <p className="muted">Step 3 of 3: Assessment complete</p>
      </div>

      <div className="panel" style={{ padding: 20, textAlign: "center", marginBottom: 16 }}>
        <div style={{ fontSize: 48, fontWeight: 700, color: overall >= 80 ? "var(--success)" : overall >= 50 ? "var(--warning)" : "var(--danger)" }}>
          {overall}%
        </div>
        <div className="muted" style={{ fontSize: 13, marginTop: 4 }}>Overall AI Governance Maturity</div>
        <div style={{ width: "100%", maxWidth: 300, margin: "12px auto", background: "var(--info-soft)", borderRadius: 6, height: 12, overflow: "hidden" }}>
          <div style={{ width: `${overall}%`, height: "100%", borderRadius: 6, background: overall >= 80 ? "var(--success)" : overall >= 50 ? "var(--warning)" : "var(--danger)", transition: "width 0.5s" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
          <button className="btn btn-secondary btn-sm" onClick={copyResults}><Download size={14} /> Copy CSV</button>
          <button className="btn btn-secondary btn-sm" onClick={() => {
            const csv = exportAssessmentCSV(answers, scopeAnswers);
            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a"); a.href = url; a.download = "gap-analysis.csv"; a.click();
            URL.revokeObjectURL(url);
          }}><Download size={14} /> Export CSV</button>
          <button className="btn btn-secondary btn-sm" onClick={handleRestart}><RotateCcw size={14} /> New Assessment</button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 12, marginBottom: 16 }}>
        {results.map((r) => (
          <div key={r.category} className="panel" style={{ padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
              <div>
                <div style={{ fontSize: 12, fontWeight: 600 }}>{r.label}</div>
                <div className="muted" style={{ fontSize: 10 }}>{r.framework}</div>
              </div>
              <span style={{ fontSize: 20, fontWeight: 700, color: r.percent >= 80 ? "var(--success)" : r.percent >= 50 ? "var(--warning)" : "var(--danger)" }}>
                {r.percent}%
              </span>
            </div>
            <div style={{ width: "100%", background: "var(--info-soft)", borderRadius: 4, height: 6, overflow: "hidden", marginBottom: 8 }}>
              <div style={{ width: `${r.percent}%`, height: "100%", borderRadius: 4, background: r.percent >= 80 ? "var(--success)" : r.percent >= 50 ? "var(--warning)" : "var(--danger)" }} />
            </div>
            <div style={{ fontSize: 11, color: "var(--muted)" }}>{r.score}/{r.max} controls met</div>
            {r.gaps.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <div
                  style={{ fontSize: 11, fontWeight: 600, color: "var(--danger)", cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}
                  onClick={() => setExpandedGap(expandedGap === r.category ? null : r.category)}
                >
                  {r.gaps.length} gap{r.gaps.length > 1 ? "s" : ""}
                </div>
                {expandedGap === r.category && (
                  <div style={{ marginTop: 4, fontSize: 11 }}>
                    {r.gaps.map((g) => (
                      <div key={g.id} style={{ padding: "4px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                        <div style={{ fontWeight: 500 }}>{g.text}</div>
                        <div className="muted">{g.clause}{g.hint ? ` - ${g.hint}` : ""}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            {r.gaps.length === 0 && (
              <div style={{ marginTop: 8, fontSize: 11, color: "var(--success)", display: "flex", alignItems: "center", gap: 4 }}>
                <CheckCircle size={12} /> All controls met
              </div>
            )}
          </div>
        ))}
      </div>

      {results.some((r) => r.gaps.length > 0) && (
        <div className="panel" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, margin: "0 0 12px" }}>Priority Action Items</h3>
          {results
            .flatMap((r) => r.gaps.map((g) => ({ ...g, category: r.label, percent: r.percent })))
            .sort((a, b) => a.percent - b.percent)
            .slice(0, 10)
            .map((item, i) => (
              <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 12 }}>
                <XCircle size={14} style={{ color: "var(--danger)", flexShrink: 0, marginTop: 1 }} />
                <div>
                  <div style={{ fontWeight: 500, marginBottom: 2 }}>{item.text}</div>
                  <div className="muted">{item.category} &middot; {item.clause}</div>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
