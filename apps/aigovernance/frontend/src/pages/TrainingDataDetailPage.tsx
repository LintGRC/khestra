import { useEffect, useState } from "react";
import { useParams, useNavigate, NavLink } from "react-router-dom";
import { Trash2, Edit3, ArrowLeft, ExternalLink } from "lucide-react";

const API = "/api/ai-governance";

const CONSENT_STATUSES = ["not_applicable", "explicit", "implicit", "opt_out", "legitimate_interest", "contractual_necessity"];
const GOVERNANCE_STATUSES = ["draft", "under_review", "approved", "rejected", "needs_update"];

export function TrainingDataDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState<any>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/training-datasets/${id}`).then(r => r.json()).then(d => {
      setDataset(d.dataset);
      setForm(d.dataset);
    }).catch(() => navigate("/aigov/training-data"));
  }, [id, navigate]);

  async function handleDelete() {
    if (!confirm("Delete this training dataset?")) return;
    await fetch(`${API}/training-datasets/${id}`, { method: "DELETE" });
    navigate("/aigov/training-data");
  }

  async function handleSave() {
    setSaving(true);
    try {
      await fetch(`${API}/training-datasets/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      const r = await fetch(`${API}/training-datasets/${id}`).then(r => r.json());
      setDataset(r.dataset);
      setForm(r.dataset);
      setEditing(false);
    } catch { /* */ } finally { setSaving(false); }
  }

  async function handleStatus(status: string) {
    await fetch(`${API}/training-datasets/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ governance_status: status }) });
    const r = await fetch(`${API}/training-datasets/${id}`).then(r => r.json());
    setDataset(r.dataset);
    setForm(r.dataset);
  }

  if (!dataset) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  const f = editing ? form : dataset;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <NavLink to="/aigov/training-data" className="btn btn-ghost btn-sm"><ArrowLeft size={14} /></NavLink>
          <div>
            <h1 style={{ margin: 0 }}>{dataset.name}</h1>
            <p className="muted" style={{ margin: 0, fontSize: 12 }}>{dataset.system_name || "No system"}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {dataset.system_id && (
            <NavLink to={`/aigov/systems/${dataset.system_id}`} className="btn btn-secondary btn-sm">
              <ExternalLink size={14} /> System
            </NavLink>
          )}
          {!editing ? (
            <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}><Edit3 size={14} /> Edit</button>
          ) : (
            <>
              <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save"}</button>
              <button className="btn btn-secondary btn-sm" onClick={() => { setEditing(false); setForm(dataset); }}>Cancel</button>
            </>
          )}
          <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={handleDelete}><Trash2 size={14} /></button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {GOVERNANCE_STATUSES.map(s => (
          <button key={s} className={`btn btn-sm ${dataset.governance_status === s ? "btn-primary" : "btn-secondary"}`} onClick={() => handleStatus(s)} disabled={s === dataset.governance_status}>
            {s.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <div className="form-grid">
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Name</label>{editing ? <input value={f.name} onChange={e => setForm({ ...form, name: e.target.value })} /> : <p>{dataset.name}</p>}</div>
          <div><label className="muted" style={{ fontSize: 11 }}>System</label>{editing ? <input value={f.system_name} onChange={e => setForm({ ...form, system_name: e.target.value })} /> : <p>{dataset.system_name || "—"}</p>}</div>
          <div><label className="muted" style={{ fontSize: 11 }}>Volume</label>{editing ? <input value={f.volume} onChange={e => setForm({ ...form, volume: e.target.value })} /> : <p>{dataset.volume || "—"}</p>}</div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label>{editing ? <textarea rows={3} value={f.description} onChange={e => setForm({ ...form, description: e.target.value })} /> : <p style={{ whiteSpace: "pre-wrap" }}>{dataset.description || "—"}</p>}</div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Data sources</label>{editing ? <input value={f.data_sources} onChange={e => setForm({ ...form, data_sources: e.target.value })} /> : <p>{dataset.data_sources || "—"}</p>}</div>
          <div><label className="muted" style={{ fontSize: 11 }}>Data types</label>{editing ? <input value={f.data_types} onChange={e => setForm({ ...form, data_types: e.target.value })} /> : <p>{dataset.data_types || "—"}</p>}</div>
          <div><label className="muted" style={{ fontSize: 11 }}>Contains PII</label><p>{dataset.contains_pii ? "Yes" : "No"}</p></div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>PII handling</label>{editing ? <textarea rows={2} value={f.pii_handling} onChange={e => setForm({ ...form, pii_handling: e.target.value })} /> : <p>{dataset.pii_handling || "—"}</p>}</div>
          <div><label className="muted" style={{ fontSize: 11 }}>Consent status</label>{editing ? <select value={f.consent_status} onChange={e => setForm({ ...form, consent_status: e.target.value })}>{CONSENT_STATUSES.map(s => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}</select> : <p>{dataset.consent_status?.replace(/_/g, " ")}</p>}</div>
          <div><label className="muted" style={{ fontSize: 11 }}>Consent mechanism</label>{editing ? <input value={f.consent_mechanism} onChange={e => setForm({ ...form, consent_mechanism: e.target.value })} /> : <p>{dataset.consent_mechanism || "—"}</p>}</div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Quality measures</label>{editing ? <textarea rows={2} value={f.quality_measures} onChange={e => setForm({ ...form, quality_measures: e.target.value })} /> : <p>{dataset.quality_measures || "—"}</p>}</div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Bias mitigation</label>{editing ? <textarea rows={2} value={f.bias_mitigation} onChange={e => setForm({ ...form, bias_mitigation: e.target.value })} /> : <p>{dataset.bias_mitigation || "—"}</p>}</div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Copyright compliance</label>{editing ? <textarea rows={2} value={f.copyright_compliance} onChange={e => setForm({ ...form, copyright_compliance: e.target.value })} /> : <p>{dataset.copyright_compliance || "—"}</p>}</div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Notes</label>{editing ? <textarea rows={3} value={f.notes} onChange={e => setForm({ ...form, notes: e.target.value })} /> : <p style={{ whiteSpace: "pre-wrap" }}>{dataset.notes || "—"}</p>}</div>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
        <p className="muted" style={{ fontSize: 11 }}>Created: {dataset.created_at?.slice(0, 10)}</p>
        <p className="muted" style={{ fontSize: 11 }}>Updated: {dataset.updated_at?.slice(0, 10)}</p>
      </div>
    </div>
  );
}
