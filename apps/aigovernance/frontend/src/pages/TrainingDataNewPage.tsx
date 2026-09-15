import { useEffect, useState } from "react";
import { useNavigate, NavLink } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

const API = "/api/ai-governance";

const CONSENT_STATUSES = ["not_applicable", "explicit", "implicit", "opt_out", "legitimate_interest", "contractual_necessity"];

export function TrainingDataNewPage() {
  const navigate = useNavigate();
  const [systems, setSystems] = useState<any[]>([]);
  const [form, setForm] = useState({
    name: "", system_id: "", system_name: "", description: "",
    data_sources: "", volume: "", data_types: "",
    contains_pii: false, pii_handling: "",
    consent_status: "not_applicable", consent_mechanism: "",
    quality_measures: "", bias_mitigation: "", copyright_compliance: "",
    governance_status: "draft", notes: "",
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
      const r = await fetch(`${API}/training-datasets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const d = await r.json();
      navigate(`/aigov/training-data/${d.id}`);
    } catch { /* */ } finally { setSaving(false); }
  }

  const togglePii = () => setForm({ ...form, contains_pii: !form.contains_pii });

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "1.25rem" }}>
        <NavLink to="/aigov/training-data" className="btn btn-ghost btn-sm"><ArrowLeft size={14} /></NavLink>
        <h1 style={{ margin: 0 }}>New Training Dataset</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="panel" style={{ padding: 16 }}>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Name *</label><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g., Customer Support Corpus v2" required /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>AI System</label>
              <select value={form.system_id} onChange={e => {
                const sys = systems.find(s => s.id === e.target.value);
                setForm({ ...form, system_id: e.target.value, system_name: sys?.name || "" });
              }}>
                <option value="">No system</option>
                {systems.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div><label className="muted" style={{ fontSize: 11 }}>Governance status</label>
              <select value={form.governance_status} onChange={e => setForm({ ...form, governance_status: e.target.value })}>
                <option value="draft">Draft</option>
                <option value="under_review">Under Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="needs_update">Needs Update</option>
              </select>
            </div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Describe the dataset and its intended use..." /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Data sources</label><input value={form.data_sources} onChange={e => setForm({ ...form, data_sources: e.target.value })} placeholder="Internal CRM, Zendesk tickets" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Volume</label><input value={form.volume} onChange={e => setForm({ ...form, volume: e.target.value })} placeholder="500K records, 10GB" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Data types</label><input value={form.data_types} onChange={e => setForm({ ...form, data_types: e.target.value })} placeholder="text, structured, image" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Contains PII</label>
              <label style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 0" }}>
                <input type="checkbox" checked={form.contains_pii} onChange={togglePii} />
                <span style={{ fontSize: 13 }}>{form.contains_pii ? "Yes — describe handling below" : "No"}</span>
              </label>
            </div>
            {form.contains_pii && <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>PII handling</label><textarea rows={2} value={form.pii_handling} onChange={e => setForm({ ...form, pii_handling: e.target.value })} placeholder="Anonymized, pseudonymized, consent obtained..." /></div>}
            <div><label className="muted" style={{ fontSize: 11 }}>Consent status</label>
              <select value={form.consent_status} onChange={e => setForm({ ...form, consent_status: e.target.value })}>
                {CONSENT_STATUSES.map(s => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            <div><label className="muted" style={{ fontSize: 11 }}>Consent mechanism</label><input value={form.consent_mechanism} onChange={e => setForm({ ...form, consent_mechanism: e.target.value })} placeholder="Opt-in during signup, DPA, etc." /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Quality measures</label><textarea rows={2} value={form.quality_measures} onChange={e => setForm({ ...form, quality_measures: e.target.value })} placeholder="Deduplication, validation, outlier removal..." /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Bias mitigation</label><textarea rows={2} value={form.bias_mitigation} onChange={e => setForm({ ...form, bias_mitigation: e.target.value })} placeholder="Balanced sampling, fairness auditing..." /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Copyright compliance</label><textarea rows={2} value={form.copyright_compliance} onChange={e => setForm({ ...form, copyright_compliance: e.target.value })} placeholder="Verified internal data, licensed datasets, no copyrighted material..." /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Notes</label><textarea rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Additional context..." /></div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <button type="submit" className="btn btn-primary" disabled={saving || !form.name.trim()}>{saving ? "Creating..." : "Create Dataset"}</button>
          <NavLink to="/aigov/training-data" className="btn btn-secondary">Cancel</NavLink>
        </div>
      </form>
    </div>
  );
}
