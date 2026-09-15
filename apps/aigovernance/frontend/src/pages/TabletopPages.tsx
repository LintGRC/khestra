import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";

const API = "/api/ai-governance";

type ScenarioStep = {
  step: number; title: string; prompt: string; context: string;
  questions: string[]; expertGuidance: string;
  scoringCriteria: string[]; frameworkRefs: string[];
  timeAllocation: number;
};
type Scenario = {
  id: string; type: string; title: string; description: string;
  difficulty: string; estimatedTime: string; triggers: string[];
  steps: ScenarioStep[];
};
type Exercise = {
  id: string; scenarioId: string; scenarioTitle: string;
  scenarioType: string; status: string; participants: string[];
  responses: { step: number; answer: string }[];
  scores: { step: number; title: string; score: number; maxScore: number;
    percentage: number; strengths: string[]; gaps: string[];
    frameworkRequirements: string[] }[];
  overallScore: number; overallPercentage: number;
  recommendations: string[]; completedAt: string;
};

function difficultyColor(d: string) {
  const m: Record<string, string> = { beginner: "badge-muted", intermediate: "badge-warning", advanced: "badge-danger" };
  return m[d] || "badge-muted";
}

export function TabletopLandingPage() {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/tabletop/scenarios`).then(r => r.json()),
      fetch(`${API}/tabletop/exercises`).then(r => r.json()),
    ]).then(([s, e]) => {
      setScenarios(s.scenarios || []);
      setExercises(e.exercises || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>AI Tabletop Exercises</h2>
        <p className="muted">Scenario-based incident response drills for AI governance and security teams.</p>
      </div>

      {exercises.length > 0 && (
        <div className="panel">
          <div className="panel-header"><strong>Recent Exercises</strong></div>
          <div className="panel-body">
            {exercises.slice(-5).reverse().map((e) => (
              <Link key={e.id} to={`/aigov/tabletop/exercises/${e.id}`}
                style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none" }}>
                <span>{e.scenarioTitle}</span>
                <span className="muted">{e.overallPercentage}% · {(e.completedAt || "").slice(0, 10)}</span>
              </Link>
            ))}
            <Link to="/aigov/tabletop/exercises" className="btn btn-secondary btn-sm" style={{ marginTop: "0.5rem" }}>View all</Link>
          </div>
        </div>
      )}

      <h3 style={{ margin: "1rem 0 0.5rem" }}>Scenarios</h3>
      <div className="panel-stack">
        {scenarios.map((s) => (
          <div key={s.id} className="panel" style={{ cursor: "pointer" }} onClick={() => navigate(`/aigov/tabletop/play/${s.id}`)}>
            <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{s.title}</strong>
              <span className={`badge ${difficultyColor(s.difficulty)}`}>{s.difficulty}</span>
            </div>
            <div className="panel-body">
              <p className="muted" style={{ fontSize: "0.85rem", marginBottom: "0.5rem" }}>{s.description}</p>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <span className="muted" style={{ fontSize: "0.8rem" }}>{s.estimatedTime}</span>
                <span className="muted" style={{ fontSize: "0.8rem" }}>{s.steps.length} steps</span>
              </div>
              {s.triggers.length > 0 && (
                <div style={{ marginTop: "0.35rem", display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                  {s.triggers.map((t) => (
                    <span key={t} className="badge badge-muted" style={{ fontSize: "0.7rem" }}>{t}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function TabletopPlayPage() {
  const { scenarioId } = useParams();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [stepIdx, setStepIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Exercise | null>(null);

  useEffect(() => {
    if (!scenarioId) return;
    fetch(`${API}/tabletop/scenarios/${scenarioId}`)
      .then(r => r.json())
      .then(d => setScenario(d.scenario))
      .catch(() => navigate("/aigov/tabletop"));
  }, [scenarioId, navigate]);

  if (!scenario) return <div className="page-stack"><p className="muted">Loading scenario...</p></div>;

  const step = scenario.steps[stepIdx];
  const isLast = stepIdx >= scenario.steps.length - 1;

  function next() {
    if (isLast) return handleSubmit();
    setStepIdx(i => i + 1);
  }

  function prev() {
    if (stepIdx === 0) return;
    setStepIdx(i => i - 1);
  }

  async function handleSubmit() {
    if (!scenario) return;
    setSubmitting(true);
    try {
      const responses = Object.entries(answers).map(([stepStr, answer]) => ({
        step: parseInt(stepStr), answer, timeSpent: 0, selfRated: 0,
      }));
      const r = await fetch(`${API}/tabletop/exercise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenarioId: scenario.id, responses }),
      });
      const d = await r.json();
      setResult(d.exercise);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  if (result) {
    return (
      <div className="page-stack">
        <div className="page-header">
          <h2>{scenario.title}</h2>
          <p className="muted">Exercise complete</p>
        </div>
        <div className="panel" style={{ textAlign: "center", padding: "2rem" }}>
          <h1 style={{ fontSize: "3rem", margin: 0 }}>{result.overallPercentage}%</h1>
          <p className="muted">Overall score</p>
        </div>
        {result.scores.map((s) => (
          <div key={s.step} className="panel">
            <div className="panel-header" style={{ display: "flex", justifyContent: "space-between" }}>
              <strong>Step {s.step}: {s.title}</strong>
              <span>{s.score}/{s.maxScore} ({s.percentage}%)</span>
            </div>
            <div className="panel-body">
              <p style={{ whiteSpace: "pre-wrap", fontSize: "0.85rem" }}>{answers[s.step] || ""}</p>
              {s.strengths.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <span style={{ fontSize: "0.8rem", color: "var(--success)" }}>Strengths:</span>
                  {s.strengths.map((st) => <p key={st} style={{ fontSize: "0.8rem", margin: "0.15rem 0", color: "var(--success)" }}>✓ {st}</p>)}
                </div>
              )}
              {s.gaps.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <span style={{ fontSize: "0.8rem", color: "var(--danger)" }}>Gaps:</span>
                  {s.gaps.map((g) => <p key={g} style={{ fontSize: "0.8rem", margin: "0.15rem 0", color: "var(--danger)" }}>△ {g}</p>)}
                </div>
              )}
            </div>
          </div>
        ))}
        <div className="panel">
          <div className="panel-header"><strong>Recommendations</strong></div>
          <div className="panel-body">
            {result.recommendations.map((r, i) => (
              <p key={i} style={{ fontSize: "0.85rem", margin: "0.25rem 0" }}>• {r}</p>
            ))}
          </div>
        </div>
        <div className="btn-row">
          <Link to={`/aigov/tabletop/exercises/${result.id}`} className="btn btn-primary">View Report</Link>
          <button className="btn btn-secondary" onClick={() => navigate("/aigov/tabletop")}>Back to Scenarios</button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>{scenario.title}</h2>
        <p className="muted">Step {stepIdx + 1} of {scenario.steps.length}</p>
      </div>

      <div className="panel">
        <div className="panel-header"><strong>Step {step.step}: {step.title}</strong></div>
        <div className="panel-body">
          <div style={{ background: "var(--bg-soft)", padding: "0.75rem", borderRadius: "6px", marginBottom: "1rem" }}>
            <p style={{ fontSize: "0.85rem", marginBottom: "0.5rem" }}><strong>Situation:</strong> {step.prompt}</p>
            <p className="muted" style={{ fontSize: "0.8rem" }}><strong>Context:</strong> {step.context}</p>
          </div>
          <div style={{ marginBottom: "1rem" }}>
            {step.questions.map((q, i) => (
              <p key={i} style={{ fontSize: "0.85rem", fontWeight: 500, marginBottom: "0.25rem" }}>{i + 1}. {q}</p>
            ))}
          </div>
          <label>Your response</label>
          <textarea
            rows={6}
            value={answers[step.step] || ""}
            onChange={(e) => setAnswers((a) => ({ ...a, [step.step]: e.target.value }))}
            placeholder="Describe your actions, decisions, and reasoning..."
            style={{ width: "100%" }}
          />
        </div>
        <div className="panel-footer" style={{ display: "flex", justifyContent: "space-between", padding: "0.75rem" }}>
          <button className="btn btn-secondary" onClick={prev} disabled={stepIdx === 0}>Previous</button>
          <button className="btn btn-primary" onClick={next} disabled={submitting || !(answers[step.step] || "").trim()}>
            {submitting ? "Submitting..." : isLast ? "Submit & Score" : "Next Step"}
          </button>
        </div>
      </div>
    </div>
  );
}

export function TabletopExercisesPage() {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/tabletop/exercises`)
      .then(r => r.json())
      .then(d => setExercises(d.exercises || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;

  const sorted = [...exercises].reverse();

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Tabletop Exercises</h2>
        <p className="muted">{exercises.length} total</p>
      </div>
      {sorted.length === 0 ? (
        <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No exercises yet. Run one from the scenarios page.</p></div></div>
      ) : (
        <div className="panel"><div className="panel-body">
          {sorted.map((e) => (
            <Link key={e.id} to={`/aigov/tabletop/exercises/${e.id}`} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none" }}>
              <div>
                <strong>{e.scenarioTitle}</strong>
                <div className="muted" style={{ fontSize: "0.8rem" }}>
                  {(e.completedAt || "").slice(0, 10)} · {e.participants?.length || 0} participants
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: "1.2rem", fontWeight: 600 }}>{e.overallPercentage}%</span>
              </div>
            </Link>
          ))}
        </div></div>
      )}
      <Link to="/aigov/tabletop" className="btn btn-secondary" style={{ alignSelf: "flex-start" }}>Back to Scenarios</Link>
    </div>
  );
}

export function TabletopDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/tabletop/exercises/${id}`)
      .then(r => r.json())
      .then(d => setExercise(d.exercise))
      .catch(() => navigate("/aigov/tabletop/exercises"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;
  if (!exercise) return <div className="page-stack"><p className="muted">Exercise not found.</p></div>;

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>{exercise.scenarioTitle}</h2>
          <p className="muted">Completed {(exercise.completedAt || "").slice(0, 10)}</p>
        </div>
        <a href={`${API}/tabletop/exercises/${exercise.id}?format=docx`} className="btn btn-secondary" download>Download Report (.docx)</a>
      </div>

      <div className="panel" style={{ textAlign: "center", padding: "2rem" }}>
        <h1 style={{ fontSize: "3rem", margin: 0 }}>{exercise.overallPercentage}%</h1>
        <p className="muted">Overall score · Score: {exercise.overallScore}</p>
      </div>

      {exercise.scores.map((s) => (
        <div key={s.step} className="panel">
          <div className="panel-header" style={{ display: "flex", justifyContent: "space-between" }}>
            <strong>Step {s.step}: {s.title}</strong>
            <span>{s.score}/{s.maxScore} ({s.percentage}%)</span>
          </div>
          <div className="panel-body">
            {s.strengths.length > 0 && (
              <div style={{ marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--success)", fontWeight: 500 }}>Strengths</span>
                {s.strengths.map((st) => <p key={st} style={{ fontSize: "0.8rem", margin: "0.15rem 0", color: "var(--success)" }}>✓ {st}</p>)}
              </div>
            )}
            {s.gaps.length > 0 && (
              <div style={{ marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--danger)", fontWeight: 500 }}>Gaps</span>
                {s.gaps.map((g) => <p key={g} style={{ fontSize: "0.8rem", margin: "0.15rem 0", color: "var(--danger)" }}>△ {g}</p>)}
              </div>
            )}
            {s.frameworkRequirements.length > 0 && (
              <div>
                <span className="muted" style={{ fontSize: "0.75rem" }}>Framework references: {s.frameworkRequirements.join(", ")}</span>
              </div>
            )}
          </div>
        </div>
      ))}

      <div className="panel">
        <div className="panel-header"><strong>Recommendations</strong></div>
        <div className="panel-body">
          {exercise.recommendations.map((r, i) => (
            <p key={i} style={{ fontSize: "0.85rem", margin: "0.25rem 0" }}>• {r}</p>
          ))}
        </div>
      </div>

      <div className="btn-row">
        <button className="btn btn-secondary" onClick={() => navigate("/aigov/tabletop/exercises")}>Back to Exercises</button>
      </div>
    </div>
  );
}
