import { useEffect, useState } from "react";
import { useNavigate, NavLink } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";

const API = "/api/ai-governance";

export function PlansNewPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const navigate = useNavigate();
  const [planTypes, setPlanTypes] = useState<Record<string, any[]>>({});
  const [form, setForm] = useState({
    name: "", plan_type: "", framework: "", description: "",
    owner: "", status: "draft", due_date: "", content: "", notes: "",
    systems: [] as string[],
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch(`${API}/plans/types`).then(r => r.json()).then(d => {
      setPlanTypes(d.plan_types || {});
    }).catch(() => {});
  }, []);

  function handleFrameworkChange(fw: string) {
    const tmpl = planTypes[fw]?.[0];
    setForm({ ...form, framework: fw, plan_type: tmpl || "", name: "", description: "", content: "" });
  }

  function handlePlanTypeChange(pt: string) {
    setForm({ ...form, plan_type: pt });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      const r = await fetch(`${API}/plans`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const d = await r.json();
      navigate(`/aigov/plans/${d.id}`);
    } catch { /* */ } finally { setSaving(false); }
  }

  const fwPlans = form.framework ? (planTypes[form.framework] || []) : [];

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "1.25rem" }}>
        <NavLink to="/aigov/plans" className="btn btn-ghost btn-sm"><ArrowLeft size={14} /></NavLink>
        <h1 style={{ margin: 0 }}>New Plan</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="panel" style={{ padding: 16 }}>
          <div className="form-grid">
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Name *</label>
              <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g., AI Risk Management Plan 2026" required />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Framework</label>
              <select value={form.framework} onChange={e => handleFrameworkChange(e.target.value)}>
                <option value="">Select framework...</option>
                {AI_GOV_FRAMEWORKS.filter(fw => activeFrameworks.includes(fw.key)).map(fw => (
                  <option key={fw.key} value={fw.key}>{fw.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Plan type</label>
              <select value={form.plan_type} onChange={e => handlePlanTypeChange(e.target.value)} disabled={!form.framework}>
                <option value="">Select type...</option>
                {fwPlans.map(t => {
                  const key = typeof t === "string" ? t : t.plan_type || "";
                  const name = typeof t === "string" ? t.replace(/_/g, " ") : t.name || key;
                  return <option key={key} value={key}>{name}</option>;
                })}
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Owner</label>
              <input value={form.owner} onChange={e => setForm({ ...form, owner: e.target.value })} placeholder="Plan owner" />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Status</label>
              <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                <option value="draft">Draft</option>
                <option value="under_review">Under Review</option>
                <option value="approved">Approved</option>
                <option value="archived">Archived</option>
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Due date</label>
              <input type="date" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} />
            </div>
          </div>
          <div className="form-grid" style={{ marginTop: 12 }}>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Description</label>
              <textarea rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Brief description of this plan's purpose..." />
            </div>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Content</label>
              <textarea rows={15} value={form.content} onChange={e => setForm({ ...form, content: e.target.value })} placeholder="Plan content / body text..." style={{ fontFamily: "monospace", fontSize: 12 }} />
            </div>
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Notes</label>
              <textarea rows={2} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Internal notes..." />
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <button type="submit" className="btn btn-primary" disabled={saving || !form.name.trim()}>{saving ? "Creating..." : "Create Plan"}</button>
          <NavLink to="/aigov/plans" className="btn btn-secondary">Cancel</NavLink>
        </div>
      </form>
    </div>
  );
}
