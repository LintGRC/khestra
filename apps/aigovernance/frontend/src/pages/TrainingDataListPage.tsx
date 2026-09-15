import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { Plus, Trash2, Database } from "lucide-react";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";

const API = "/api/ai-governance";

const STATUS_COLORS: Record<string, string> = {
  approved: "var(--success-soft, #dcfce7),var(--success, #166534)",
  rejected: "var(--danger-soft, #fee2e2),var(--danger, #991b1b)",
  under_review: "var(--info-soft, #dbeafe),var(--info, #1e40af)",
  draft: "var(--surface, #f3f4f6),var(--muted, #6b7280)",
  needs_update: "var(--warning-soft, #fef3c7),var(--warning, #92400e)",
};

export function TrainingDataListPage() {
  const [allDatasets, setAllDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", system_name: "", data_sources: "", volume: "", governance_status: "draft" });
  const [saving, setSaving] = useState(false);

  function load() {
    setLoading(true);
    fetch(`${API}/training-datasets`).then(r => r.json()).then(d => setAllDatasets(d.datasets || [])).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this dataset?")) return;
    await fetch(`${API}/training-datasets/${id}`, { method: "DELETE" });
    load();
  }

  async function handleCreate() {
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API}/training-datasets`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setShowForm(false);
      setForm({ name: "", system_name: "", data_sources: "", volume: "", governance_status: "draft" });
      load();
    } catch { /* */ } finally { setSaving(false); }
  }

  const filtered = allDatasets.filter(d => {
    if (filterStatus && d.governance_status !== filterStatus) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!d.name?.toLowerCase().includes(q) && !d.system_name?.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div className="aigov-page-header" style={{ marginBottom: 0 }}>
          <h1>Training Data</h1>
          <p>{filtered.length} of {allDatasets.length} datasets</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}><Plus size={14} /> New Dataset</button>
        </div>
      </div>

      {showForm && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <strong>New Training Dataset</strong>
            <button className="btn btn-sm btn-ghost" onClick={() => setShowForm(false)}>✕</button>
          </div>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Name</label><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g., Customer Support Corpus v2" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>System</label><input value={form.system_name} onChange={e => setForm({ ...form, system_name: e.target.value })} placeholder="System name" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Volume</label><input value={form.volume} onChange={e => setForm({ ...form, volume: e.target.value })} placeholder="e.g., 500K records" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Status</label><select value={form.governance_status} onChange={e => setForm({ ...form, governance_status: e.target.value })}><option value="draft">Draft</option><option value="under_review">Under Review</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="needs_update">Needs Update</option></select></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Data sources</label><input value={form.data_sources} onChange={e => setForm({ ...form, data_sources: e.target.value })} placeholder="e.g., Internal CRM, Zendesk tickets" /></div>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleCreate} disabled={saving || !form.name.trim()}>{saving ? "Creating..." : "Create Dataset"}</button>
        </div>
      )}

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search by name or system..." />
        <FilterSelect value={filterStatus} onChange={setFilterStatus} options={[
          { value: "draft", label: "Draft" },
          { value: "under_review", label: "Under Review" },
          { value: "approved", label: "Approved" },
          { value: "rejected", label: "Rejected" },
          { value: "needs_update", label: "Needs Update" },
        ]} placeholder="All status" />
      </FilterBar>

      {loading ? (
        <p className="muted">Loading...</p>
      ) : filtered.length === 0 ? (
        <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No training datasets yet. Document your training data provenance.</p>
      ) : (
        <div className="panel-stack" style={{ gap: 8 }}>
          {filtered.map(d => {
            const sc = STATUS_COLORS[d.governance_status] || STATUS_COLORS.draft;
            return (
              <div key={d.id} className="panel" style={{ padding: 12, borderLeft: `3px solid ${sc.split(",")[1] || "var(--muted)"}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, flex: 1 }}>
                    <Database size={16} style={{ color: "var(--primary)" }} />
                    <div style={{ flex: 1 }}>
                      <NavLink to={`/aigov/training-data/${d.id}`} style={{ fontWeight: 600, textDecoration: "none", color: "inherit" }}>{d.name}</NavLink>
                      {d.system_name && <span className="muted" style={{ marginLeft: 8, fontSize: 12 }}>{d.system_name}</span>}
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: sc.split(",")[0], color: sc.split(",")[1] }}>{d.governance_status?.replace(/_/g, " ")}</span>
                    {d.volume && <span className="muted" style={{ fontSize: 12 }}>{d.volume}</span>}
                    {d.contains_pii && <span className="badge badge-warning" style={{ fontSize: 10 }}>PII</span>}
                    <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(d.id)}><Trash2 size={12} /></button>
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
