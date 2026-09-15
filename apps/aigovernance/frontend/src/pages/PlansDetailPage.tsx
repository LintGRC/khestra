import { useEffect, useState } from "react";
import { useParams, useNavigate, NavLink } from "react-router-dom";
import { Trash2, Edit3, ArrowLeft, CheckCircle } from "lucide-react";
import { FW_LABELS } from "./aiGovFrameworks";

const API = "/api/ai-governance";

const STATUS_OPTIONS = ["draft", "under_review", "approved", "archived"];

export function PlansDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plan, setPlan] = useState<any>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    if (id === "seed") {
      fetch(`${API}/plans/seed`, { method: "POST" })
        .then(() => { navigate("/aigov/plans"); })
        .catch(() => navigate("/aigov/plans"));
      return;
    }
    fetch(`${API}/plans/${id}`).then(r => r.json()).then(d => {
      setPlan(d.plan);
      setForm(d.plan);
    }).catch(() => navigate("/aigov/plans"));
  }, [id, navigate]);

  async function handleDelete() {
    if (!confirm("Delete this plan?")) return;
    await fetch(`${API}/plans/${id}`, { method: "DELETE" });
    navigate("/aigov/plans");
  }

  async function handleSave() {
    setSaving(true);
    try {
      await fetch(`${API}/plans/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      const r = await fetch(`${API}/plans/${id}`).then(r => r.json());
      setPlan(r.plan);
      setForm(r.plan);
      setEditing(false);
    } catch { /* */ } finally { setSaving(false); }
  }

  async function handleStatus(status: string) {
    await fetch(`${API}/plans/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
    const r = await fetch(`${API}/plans/${id}`).then(r => r.json());
    setPlan(r.plan);
    setForm(r.plan);
  }

  if (!plan || id === "seed") return <p className="muted" style={{ padding: 24 }}>Loading...</p>;
  const f = editing ? form : plan;
  const fwColor = plan.framework === "eu_ai_act" ? "var(--primary)" : plan.framework === "nist_ai_rmf" ? "var(--info)" : "var(--success)";

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <NavLink to="/aigov/plans" className="btn btn-ghost btn-sm"><ArrowLeft size={14} /></NavLink>
          <div>
            <h1 style={{ margin: 0 }}>{plan.name}</h1>
            <p className="muted" style={{ margin: 0, fontSize: 12 }}>{FW_LABELS[plan.framework] || plan.framework} — {plan.status?.replace(/_/g, " ")}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <div style={{ display: "flex", gap: 4 }}>
            {STATUS_OPTIONS.map(s => (
              <button key={s} className={`btn btn-sm ${s === plan.status ? "btn-primary" : "btn-ghost"}`}
                onClick={() => handleStatus(s)}
                style={s === plan.status ? {} : { fontSize: 11 }}>
                {s === "approved" && <CheckCircle size={12} />}
                {s.replace(/_/g, " ")}
              </button>
            ))}
          </div>
          {!editing ? (
            <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}><Edit3 size={14} /> Edit</button>
          ) : (
            <>
              <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save"}</button>
              <button className="btn btn-secondary btn-sm" onClick={() => { setEditing(false); setForm(plan); }}>Cancel</button>
            </>
          )}
          <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={handleDelete}><Trash2 size={14} /></button>
        </div>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <div style={{ display: "flex", gap: 24, marginBottom: 16 }}>
          <div><span className="muted" style={{ fontSize: 11, display: "block" }}>Owner</span><span>{plan.owner || "—"}</span></div>
          <div><span className="muted" style={{ fontSize: 11, display: "block" }}>Due Date</span><span>{plan.due_date || "—"}</span></div>
          <div><span className="muted" style={{ fontSize: 11, display: "block" }}>Framework</span><span style={{ color: fwColor, fontWeight: 600 }}>{FW_LABELS[plan.framework] || plan.framework}</span></div>
          <div><span className="muted" style={{ fontSize: 11, display: "block" }}>Plan Type</span><span>{plan.plan_type?.replace(/_/g, " ")}</span></div>
          <div><span className="muted" style={{ fontSize: 11, display: "block" }}>Systems</span><span>{(plan.systems?.length || 0) > 0 ? plan.systems.length + " linked" : "None"}</span></div>
        </div>

        {editing ? (
          <div>
            <div className="form-grid">
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Name</label>
                <input value={f.name} onChange={e => setForm({ ...form, name: e.target.value })} />
              </div>
              <div>
                <label className="muted" style={{ fontSize: 11 }}>Owner</label>
                <input value={f.owner || ""} onChange={e => setForm({ ...form, owner: e.target.value })} placeholder="Who owns this plan?" />
              </div>
              <div>
                <label className="muted" style={{ fontSize: 11 }}>Due date</label>
                <input type="date" value={f.due_date || ""} onChange={e => setForm({ ...form, due_date: e.target.value })} />
              </div>
            </div>
            <div className="form-grid" style={{ marginTop: 12 }}>
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Description</label>
                <textarea rows={3} value={f.description || ""} onChange={e => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Content</label>
                <textarea rows={20} value={f.content || ""} onChange={e => setForm({ ...form, content: e.target.value })} style={{ fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap" }} />
              </div>
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Notes</label>
                <textarea rows={3} value={f.notes || ""} onChange={e => setForm({ ...form, notes: e.target.value })} />
              </div>
            </div>
          </div>
        ) : (
          <div>
            {plan.description && <p style={{ marginBottom: 12 }}>{plan.description}</p>}
            {plan.content && (
              <div style={{ background: "var(--surface)", padding: 16, borderRadius: "var(--radius)", fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
                {plan.content}
              </div>
            )}
            {plan.notes && <p className="muted" style={{ marginTop: 12, fontStyle: "italic" }}>{plan.notes}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
