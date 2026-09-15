import { useEffect, useState } from "react";
import { useNavigate, NavLink } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

const API = "/api/ai-governance";

const EVAL_TYPES = ["accuracy", "robustness", "bias", "cybersecurity", "fairness", "performance", "red_team", "hallucination", "human_review", "conformity", "internal_audit"];

export function EvaluationsNewPage() {
  const navigate = useNavigate();
  const [systems, setSystems] = useState<any[]>([]);
  const [form, setForm] = useState({
    name: "", system_id: "", system_name: "", evaluation_type: "accuracy", status: "planned",
    methodology: "", criteria: "", results: "", score: 0,
    tester: "", test_date: "", reviewer: "", review_date: "", notes: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch(`${API}/systems`).then(r => r.json()).then(d => setSystems(d.systems || [])).catch(() => {});
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      const r = await fetch(`${API}/evaluations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const d = await r.json();
      navigate(`/aigov/evaluations/${d.id}`);
    } catch { /* */ } finally { setSaving(false); }
  }

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "1.25rem" }}>
        <NavLink to="/aigov/evaluations" className="btn btn-ghost btn-sm"><ArrowLeft size={14} /></NavLink>
        <h1 style={{ margin: 0 }}>New Evaluation</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="panel" style={{ padding: 16 }}>
          <div className="form-grid">
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Name *</label>
              <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g., GPT-4 Accuracy Test Q3 2025" required />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Evaluation type</label>
              <select value={form.evaluation_type} onChange={e => setForm({ ...form, evaluation_type: e.target.value })}>
                {EVAL_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Status</label>
              <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="passed">Passed</option>
                <option value="failed">Failed</option>
                <option value="needs_review">Needs Review</option>
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>AI System</label>
              <select value={form.system_id} onChange={e => {
                const sys = systems.find(s => s.id === e.target.value);
                setForm({ ...form, system_id: e.target.value, system_name: sys?.name || "" });
              }}>
                <option value="">No system</option>
                {systems.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Tester</label>
              <input value={form.tester} onChange={e => setForm({ ...form, tester: e.target.value })} placeholder="Who ran it?" />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Test date</label>
              <input type="date" value={form.test_date} onChange={e => setForm({ ...form, test_date: e.target.value })} />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Reviewer</label>
              <input value={form.reviewer} onChange={e => setForm({ ...form, reviewer: e.target.value })} placeholder="Who reviewed?" />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Review date</label>
              <input type="date" value={form.review_date} onChange={e => setForm({ ...form, review_date: e.target.value })} />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Score (%)</label>
              <input type="number" min={0} max={100} value={form.score} onChange={e => setForm({ ...form, score: parseFloat(e.target.value) || 0 })} />
            </div>
          </div>
          <div className="form-grid" style={{ marginTop: 12 }}>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Methodology</label>
              <textarea rows={3} value={form.methodology} onChange={e => setForm({ ...form, methodology: e.target.value })} placeholder="Describe the testing approach..." />
            </div>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Criteria / Thresholds</label>
              <textarea rows={2} value={form.criteria} onChange={e => setForm({ ...form, criteria: e.target.value })} placeholder="e.g., Accuracy > 95%, F1 > 0.90" />
            </div>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Results (JSON)</label>
              <textarea rows={4} value={form.results} onChange={e => setForm({ ...form, results: e.target.value })} placeholder='{"accuracy": 96.2, "f1": 0.93}' style={{ fontFamily: "monospace", fontSize: 12 }} />
            </div>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Notes</label>
              <textarea rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Any additional context..." />
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <button type="submit" className="btn btn-primary" disabled={saving || !form.name.trim()}>{saving ? "Creating..." : "Create Evaluation"}</button>
          <NavLink to="/aigov/evaluations" className="btn btn-secondary">Cancel</NavLink>
        </div>
      </form>
    </div>
  );
}
