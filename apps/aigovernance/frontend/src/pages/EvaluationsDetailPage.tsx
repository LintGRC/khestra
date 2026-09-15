import { useEffect, useState } from "react";
import { useParams, useNavigate, NavLink } from "react-router-dom";
import { Trash2, Edit3, ArrowLeft, ExternalLink } from "lucide-react";

const API = "/api/ai-governance";

const EVAL_TYPES = ["accuracy", "robustness", "bias", "cybersecurity", "fairness", "performance", "red_team", "hallucination", "human_review", "conformity", "internal_audit"];

const STATUS_OPTIONS = ["planned", "in_progress", "passed", "failed", "needs_review"];

export function EvaluationsDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState<any>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({});
  const [saving, setSaving] = useState(false);
  const [tabs, setTabs] = useState<"details" | "results" | "controls">("details");

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/evaluations/${id}`).then(r => r.json()).then(d => {
      setEvaluation(d.evaluation);
      setForm(d.evaluation);
    }).catch(() => navigate("/aigov/evaluations"));
  }, [id, navigate]);

  async function handleDelete() {
    if (!confirm("Delete this evaluation?")) return;
    await fetch(`${API}/evaluations/${id}`, { method: "DELETE" });
    navigate("/aigov/evaluations");
  }

  async function handleSave() {
    setSaving(true);
    try {
      await fetch(`${API}/evaluations/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      const r = await fetch(`${API}/evaluations/${id}`).then(r => r.json());
      setEvaluation(r.evaluation);
      setForm(r.evaluation);
      setEditing(false);
    } catch { /* */ } finally { setSaving(false); }
  }

  async function handleStatus(status: string) {
    await fetch(`${API}/evaluations/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
    const r = await fetch(`${API}/evaluations/${id}`).then(r => r.json());
    setEvaluation(r.evaluation);
    setForm(r.evaluation);
  }

  if (!evaluation) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  const f = editing ? form : evaluation;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <NavLink to="/aigov/evaluations" className="btn btn-ghost btn-sm"><ArrowLeft size={14} /></NavLink>
          <div>
            <h1 style={{ margin: 0 }}>{evaluation.name}</h1>
            <p className="muted" style={{ margin: 0, fontSize: 12 }}>{evaluation.evaluation_type?.replace(/_/g, " ")} — {evaluation.system_name || "No system"}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {evaluation.system_id && (
            <NavLink to={`/aigov/systems/${evaluation.system_id}`} className="btn btn-secondary btn-sm">
              <ExternalLink size={14} /> System
            </NavLink>
          )}
          {!editing ? (
            <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}><Edit3 size={14} /> Edit</button>
          ) : (
            <>
              <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save"}</button>
              <button className="btn btn-secondary btn-sm" onClick={() => { setEditing(false); setForm(evaluation); }}>Cancel</button>
            </>
          )}
          <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={handleDelete}><Trash2 size={14} /></button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {STATUS_OPTIONS.map(s => (
          <button key={s} className={`btn btn-sm ${evaluation.status === s ? "btn-primary" : "btn-secondary"}`} onClick={() => handleStatus(s)} disabled={s === evaluation.status}>
            {s.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      <div className="panel" style={{ padding: 0 }}>
        <div style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--border-subtle)" }}>
          {(["details", "results", "controls"] as const).map(tab => (
            <button key={tab} className={`btn btn-ghost btn-sm`} style={{ padding: "10px 16px", borderBottom: tabs === tab ? "2px solid var(--primary)" : "2px solid transparent", borderRadius: 0 }} onClick={() => setTabs(tab)}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {tabs === "details" && (
          <div style={{ padding: 16 }}>
            <div className="form-grid">
              <div><label className="muted" style={{ fontSize: 11 }}>Name</label>{editing ? <input value={f.name} onChange={e => setForm({ ...form, name: e.target.value })} /> : <p>{evaluation.name}</p>}</div>
              <div><label className="muted" style={{ fontSize: 11 }}>Type</label>{editing ? <select value={f.evaluation_type} onChange={e => setForm({ ...form, evaluation_type: e.target.value })}>{EVAL_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}</select> : <p>{evaluation.evaluation_type?.replace(/_/g, " ")}</p>}</div>
              <div><label className="muted" style={{ fontSize: 11 }}>Status</label><p>{evaluation.status?.replace(/_/g, " ")}</p></div>
              <div><label className="muted" style={{ fontSize: 11 }}>System</label>{editing ? <input value={f.system_name} onChange={e => setForm({ ...form, system_name: e.target.value })} /> : <p>{evaluation.system_name || "—"}</p>}</div>
              <div><label className="muted" style={{ fontSize: 11 }}>Tester</label>{editing ? <input value={f.tester} onChange={e => setForm({ ...form, tester: e.target.value })} /> : <p>{evaluation.tester || "—"}</p>}</div>
              <div><label className="muted" style={{ fontSize: 11 }}>Test date</label>{editing ? <input type="date" value={f.test_date} onChange={e => setForm({ ...form, test_date: e.target.value })} /> : <p>{evaluation.test_date || "—"}</p>}</div>
              <div><label className="muted" style={{ fontSize: 11 }}>Reviewer</label>{editing ? <input value={f.reviewer} onChange={e => setForm({ ...form, reviewer: e.target.value })} /> : <p>{evaluation.reviewer || "—"}</p>}</div>
              <div><label className="muted" style={{ fontSize: 11 }}>Review date</label>{editing ? <input type="date" value={f.review_date} onChange={e => setForm({ ...form, review_date: e.target.value })} /> : <p>{evaluation.review_date || "—"}</p>}</div>
            </div>
            <div className="form-grid" style={{ marginTop: 12 }}>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Methodology</label>{editing ? <textarea rows={3} value={f.methodology} onChange={e => setForm({ ...form, methodology: e.target.value })} placeholder="Describe the testing methodology..." /> : <p style={{ whiteSpace: "pre-wrap" }}>{evaluation.methodology || "—"}</p>}</div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Criteria</label>{editing ? <textarea rows={2} value={f.criteria} onChange={e => setForm({ ...form, criteria: e.target.value })} placeholder="What thresholds were used?" /> : <p style={{ whiteSpace: "pre-wrap" }}>{evaluation.criteria || "—"}</p>}</div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Notes</label>{editing ? <textarea rows={3} value={f.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Additional notes..." /> : <p style={{ whiteSpace: "pre-wrap" }}>{evaluation.notes || "—"}</p>}</div>
            </div>
          </div>
        )}

        {tabs === "results" && (
          <div style={{ padding: 16 }}>
            <div className="form-grid">
              <div><label className="muted" style={{ fontSize: 11 }}>Score</label>{editing ? <input type="number" min={0} max={100} value={f.score} onChange={e => setForm({ ...form, score: parseFloat(e.target.value) || 0 })} /> : <p>{evaluation.score > 0 ? `${evaluation.score}%` : "—"}</p>}</div>
            </div>
            <div className="span-2" style={{ marginTop: 12 }}>
              <label className="muted" style={{ fontSize: 11 }}>Detailed results (JSON)</label>
              {editing ? (
                <textarea rows={6} value={f.results} onChange={e => setForm({ ...form, results: e.target.value })} placeholder='{"accuracy": 96.2, "f1": 0.93}' style={{ fontFamily: "monospace", fontSize: 12 }} />
              ) : (
                <pre style={{ fontSize: 12, background: "var(--surface)", padding: 12, borderRadius: "var(--radius)", overflow: "auto" }}>{evaluation.results || "—"}</pre>
              )}
            </div>
          </div>
        )}

        {tabs === "controls" && (
          <div style={{ padding: 16 }}>
            <label className="muted" style={{ fontSize: 11 }}>Mapped control IDs</label>
            {editing ? (
              <input value={(f.control_ids || []).join(", ")} onChange={e => setForm({ ...form, control_ids: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean) })} placeholder="EU-15, NIST-MEASURE-4, ISO-9.1" />
            ) : (
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
                {(evaluation.control_ids || []).length > 0 ? (evaluation.control_ids as string[]).map((c: string) => (
                  <span key={c} style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: "var(--info-soft, #dbeafe)", color: "var(--info, #1d4ed8)" }}>{c}</span>
                )) : <span className="muted">None mapped</span>}
              </div>
            )}
            {evaluation.evidence_ids && evaluation.evidence_ids.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <label className="muted" style={{ fontSize: 11 }}>Evidence links</label>
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
                  {(evaluation.evidence_ids as string[]).map((eid: string) => (
                    <NavLink key={eid} to={`/aigov/evidence`} style={{ fontSize: 11, padding: "2px 8px", borderRadius: "var(--radius)", background: "var(--surface)", textDecoration: "none" }}>{eid}</NavLink>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
        <p className="muted" style={{ fontSize: 11 }}>Created: {evaluation.created_at?.slice(0, 10)}</p>
        <p className="muted" style={{ fontSize: 11 }}>Updated: {evaluation.updated_at?.slice(0, 10)}</p>
      </div>
    </div>
  );
}
