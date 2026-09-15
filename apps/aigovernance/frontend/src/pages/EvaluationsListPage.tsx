import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { Plus, Trash2, ClipboardCheck } from "lucide-react";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";

const API = "/api/ai-governance";

const EVAL_TYPES = ["accuracy", "robustness", "bias", "cybersecurity", "fairness", "performance", "red_team", "hallucination", "human_review", "conformity", "internal_audit"];

const STATUS_COLORS: Record<string, string> = {
  passed: "var(--success-soft, #dcfce7),var(--success, #166534)",
  failed: "var(--danger-soft, #fee2e2),var(--danger, #991b1b)",
  in_progress: "var(--info-soft, #dbeafe),var(--info, #1e40af)",
  planned: "var(--surface, #f3f4f6),var(--muted, #6b7280)",
  needs_review: "var(--warning-soft, #fef3c7),var(--warning, #92400e)",
};

export function EvaluationsListPage() {
  const [allEvals, setAllEvals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", system_id: "", system_name: "", evaluation_type: "accuracy", test_date: "", tester: "" });
  const [saving, setSaving] = useState(false);

  function load() {
    setLoading(true);
    fetch(`${API}/evaluations`).then(r => r.json()).then(d => setAllEvals(d.evaluations || [])).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this evaluation?")) return;
    await fetch(`${API}/evaluations/${id}`, { method: "DELETE" });
    load();
  }

  async function handleCreate() {
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API}/evaluations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setShowForm(false);
      setForm({ name: "", system_id: "", system_name: "", evaluation_type: "accuracy", test_date: "", tester: "" });
      load();
    } catch { /* */ } finally { setSaving(false); }
  }

  const filtered = allEvals.filter(e => {
    if (filterType && e.evaluation_type !== filterType) return false;
    if (filterStatus && e.status !== filterStatus) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!e.name?.toLowerCase().includes(q) && !e.system_name?.toLowerCase().includes(q) && !e.tester?.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div className="aigov-page-header" style={{ marginBottom: 0 }}>
          <h1>Evaluations</h1>
          <p>{filtered.length} of {allEvals.length} evaluations</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}><Plus size={14} /> New Evaluation</button>
        </div>
      </div>

      {showForm && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <strong>New Evaluation</strong>
            <button className="btn btn-sm btn-ghost" onClick={() => setShowForm(false)}>✕</button>
          </div>
          <div className="form-grid">
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Name</label>
              <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g., GPT-4 Accuracy Test Q3" />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Type</label>
              <select value={form.evaluation_type} onChange={e => setForm({ ...form, evaluation_type: e.target.value })}>
                {EVAL_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>System</label>
              <input value={form.system_name} onChange={e => setForm({ ...form, system_name: e.target.value })} placeholder="System name" />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Test date</label>
              <input type="date" value={form.test_date} onChange={e => setForm({ ...form, test_date: e.target.value })} />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Tester</label>
              <input value={form.tester} onChange={e => setForm({ ...form, tester: e.target.value })} placeholder="Who ran it?" />
            </div>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleCreate} disabled={saving || !form.name.trim()}>{saving ? "Creating..." : "Create Evaluation"}</button>
        </div>
      )}

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search by name, system, tester..." />
        <FilterSelect value={filterType} onChange={setFilterType} options={EVAL_TYPES.map(t => ({ value: t, label: t.replace(/_/g, " ") }))} placeholder="All types" />
        <FilterSelect value={filterStatus} onChange={setFilterStatus} options={[
          { value: "planned", label: "Planned" },
          { value: "in_progress", label: "In Progress" },
          { value: "passed", label: "Passed" },
          { value: "failed", label: "Failed" },
          { value: "needs_review", label: "Needs Review" },
        ]} placeholder="All status" />
      </FilterBar>

      {loading ? (
        <p className="muted">Loading...</p>
      ) : filtered.length === 0 ? (
        <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No evaluations yet. Create one to track AI system testing.</p>
      ) : (
        <div className="panel-stack" style={{ gap: 8 }}>
          {filtered.map(e => {
            const sc = STATUS_COLORS[e.status] || STATUS_COLORS.planned;
            return (
              <div key={e.id} className="panel" style={{ padding: 12, borderLeft: `3px solid ${sc.split(",")[1] || "var(--muted)"}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, flex: 1 }}>
                    <ClipboardCheck size={16} style={{ color: "var(--primary)" }} />
                    <div style={{ flex: 1 }}>
                      <NavLink to={`/aigov/evaluations/${e.id}`} style={{ fontWeight: 600, textDecoration: "none", color: "inherit" }}>{e.name}</NavLink>
                      {e.system_name && <span className="muted" style={{ marginLeft: 8, fontSize: 12 }}>{e.system_name}</span>}
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: sc.split(",")[0], color: sc.split(",")[1] }}>{e.evaluation_type?.replace(/_/g, " ")}</span>
                    <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: sc.split(",")[0], color: sc.split(",")[1] }}>{e.status?.replace(/_/g, " ")}</span>
                    {e.score > 0 && <span className="muted" style={{ fontSize: 12 }}>Score: {e.score}%</span>}
                    {e.test_date && <span className="muted" style={{ fontSize: 12 }}>{e.test_date}</span>}
                    <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(e.id)}><Trash2 size={12} /></button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
