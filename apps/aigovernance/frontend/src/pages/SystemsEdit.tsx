import { Fragment, useEffect, useState } from "react";
import { useNavigate, NavLink, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

const API = "/api/ai-governance";
const DATA_TYPES = ["Customer PII", "Employee PII", "Financial Data", "Source Code", "PHI / Health Data", "Secrets / Credentials", "Public Data", "Intellectual Property", "Biometric Data", "Location Data", "Behavioral Data", "Synthetic Data"];

export function SystemsEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: "", version: "1.0.0", description: "", purpose: "", owner: "", business_owner: "",
    technical_owner: "", risk_owner: "", vendor: "", source: "internal", foundation_model: "",
    is_fine_tuned: false, framework: "", deployment_status: "development", environment: "development",
    is_public_facing: false, transparency_notice_url: "",
    input_data_sources: "", processing_location: "", output_destinations: "",
    performance_metrics: "", known_limitations: "", out_of_scope_uses: "",
    human_oversight: "", bias_fairness_notes: "", training_data: "",
  });
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const [dataInputs, setDataInputs] = useState<string[]>([]);
  const [dataOutputs, setDataOutputs] = useState<string[]>([]);

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/systems/${id}`).then((r) => r.json()).then((d) => {
      const s = d.system;
      setForm({ name: s.name, version: s.version || "1.0.0", description: s.description || "", purpose: s.purpose || "", owner: s.owner || "", business_owner: s.business_owner || "", technical_owner: s.technical_owner || "", risk_owner: s.risk_owner || "", vendor: s.vendor || "", source: s.source || "internal", foundation_model: s.foundation_model || "", is_fine_tuned: s.is_fine_tuned || false, framework: s.framework || "", deployment_status: s.deployment_status || "development", environment: s.environment || "development", is_public_facing: s.is_public_facing || false, transparency_notice_url: s.transparency_notice_url || "", input_data_sources: s.input_data_sources || "", processing_location: s.processing_location || "", output_destinations: s.output_destinations || "", performance_metrics: s.performance_metrics || "", known_limitations: s.known_limitations || "", out_of_scope_uses: s.out_of_scope_uses || "", human_oversight: s.human_oversight || "", bias_fairness_notes: s.bias_fairness_notes || "", training_data: s.training_data || "" });
      setTags(s.tags || []);
      setDataInputs(s.data_inputs || []);
      setDataOutputs(s.data_outputs || []);
    }).finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    await fetch(`${API}/systems/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, tags, data_inputs: dataInputs, data_outputs: dataOutputs }) });
    navigate(`/aigov/systems/${id}`);
  }

  if (loading) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  return (
    <div style={{ maxWidth: 640 }}>
      <NavLink to={`/aigov/systems/${id}`} style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--muted)", textDecoration: "none", marginBottom: 12 }}>
        <ArrowLeft size={12} /> Back to System
      </NavLink>
      <div className="aigov-page-header">
        <h1>Edit System</h1>
      </div>
      <form onSubmit={handleSubmit} className="panel-stack">
        <div className="panel">
          <div className="panel-header"><strong>Basic Information</strong></div>
          <div className="panel-body">
            <div className="form-grid">
              <div><label className="muted" style={{ fontSize: 11 }}>Name *</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Version</label><input value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Source</label><select value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}><option value="internal">Internal</option><option value="external">External</option><option value="open_source">Open Source</option></select></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Purpose</label><textarea value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} rows={2} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Foundation Model</label><input value={form.foundation_model} onChange={(e) => setForm({ ...form, foundation_model: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Framework</label><input value={form.framework} onChange={(e) => setForm({ ...form, framework: e.target.value })} /></div>
            </div>
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, marginTop: 8 }}>
              <input type="checkbox" checked={form.is_fine_tuned} onChange={(e) => setForm({ ...form, is_fine_tuned: e.target.checked })} />
              Fine-tuned model
            </label>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Ownership</strong></div>
          <div className="panel-body">
            <div className="form-grid">
              <div><label className="muted" style={{ fontSize: 11 }}>Owner</label><input value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Vendor</label><input value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Business Owner</label><input value={form.business_owner} onChange={(e) => setForm({ ...form, business_owner: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Technical Owner</label><input value={form.technical_owner} onChange={(e) => setForm({ ...form, technical_owner: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Risk Owner</label><input value={form.risk_owner} onChange={(e) => setForm({ ...form, risk_owner: e.target.value })} /></div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Deployment</strong></div>
          <div className="panel-body">
            <div className="form-grid">
              <div><label className="muted" style={{ fontSize: 11 }}>Status</label><select value={form.deployment_status} onChange={(e) => setForm({ ...form, deployment_status: e.target.value })}><option>development</option><option>staging</option><option>production</option><option>deprecated</option></select></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Environment</label><select value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}><option>development</option><option>staging</option><option>production</option></select></div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Transparency &amp; Data Lineage</strong></div>
          <div className="panel-body">
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, marginBottom: 8 }}>
              <input type="checkbox" checked={form.is_public_facing} onChange={(e) => setForm({ ...form, is_public_facing: e.target.checked })} />
              Public-facing system (Article 50)
            </label>
            {form.is_public_facing && <div style={{ marginBottom: 8 }}><label className="muted" style={{ fontSize: 11 }}>Transparency Notice URL</label><input value={form.transparency_notice_url} onChange={(e) => setForm({ ...form, transparency_notice_url: e.target.value })} /></div>}
            <div className="form-grid">
              <div><label className="muted" style={{ fontSize: 11 }}>Input Data Sources</label><input value={form.input_data_sources} onChange={(e) => setForm({ ...form, input_data_sources: e.target.value })} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Processing Location</label><input value={form.processing_location} onChange={(e) => setForm({ ...form, processing_location: e.target.value })} /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Output Destinations</label><input value={form.output_destinations} onChange={(e) => setForm({ ...form, output_destinations: e.target.value })} /></div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Data Mapping</strong></div>
          <div className="panel-body" style={{ padding: "0.5rem 1rem 1rem" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 80px 80px", gap: 4, fontSize: 11 }}>
              <div className="muted" style={{ fontWeight: 600, padding: "4px 0" }}>Data Type</div>
              <div className="muted" style={{ fontWeight: 600, padding: "4px 0", textAlign: "center" }}>Input</div>
              <div className="muted" style={{ fontWeight: 600, padding: "4px 0", textAlign: "center" }}>Output</div>
              {DATA_TYPES.map(t => (
                <Fragment key={t}>
                  <div style={{ padding: "4px 0" }}>{t}</div>
                  <div style={{ textAlign: "center" }}>
                    <input type="checkbox" checked={dataInputs.includes(t)} onChange={() => setDataInputs(dataInputs.includes(t) ? dataInputs.filter(x => x !== t) : [...dataInputs, t])} />
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <input type="checkbox" checked={dataOutputs.includes(t)} onChange={() => setDataOutputs(dataOutputs.includes(t) ? dataOutputs.filter(x => x !== t) : [...dataOutputs, t])} />
                  </div>
                </Fragment>
              ))}
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Model Card</strong></div>
          <div className="panel-body">
            <div className="form-grid">
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Performance Metrics</label><textarea value={form.performance_metrics} onChange={(e) => setForm({ ...form, performance_metrics: e.target.value })} rows={2} placeholder="Accuracy, precision, recall, robustness, stress test results..." /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Known Limitations &amp; Edge Cases</label><textarea value={form.known_limitations} onChange={(e) => setForm({ ...form, known_limitations: e.target.value })} rows={2} placeholder="Failure modes, edge cases, conditions where performance degrades..." /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Out-of-Scope Uses</label><textarea value={form.out_of_scope_uses} onChange={(e) => setForm({ ...form, out_of_scope_uses: e.target.value })} rows={2} placeholder="Prohibited or inappropriate use cases..." /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Human Oversight</label><textarea value={form.human_oversight} onChange={(e) => setForm({ ...form, human_oversight: e.target.value })} rows={2} placeholder="Human-in-the-loop measures, override capabilities, escalation procedures..." /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Bias &amp; Fairness</label><textarea value={form.bias_fairness_notes} onChange={(e) => setForm({ ...form, bias_fairness_notes: e.target.value })} rows={2} placeholder="Bias testing results, fairness metrics, demographic parity..." /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Training Data</label><textarea value={form.training_data} onChange={(e) => setForm({ ...form, training_data: e.target.value })} rows={2} placeholder="Dataset description, data provenance, preprocessing, labeling methodology..." /></div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Tags</strong></div>
          <div className="panel-body">
            <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginBottom: 8 }}>
              {tags.map((t) => (
                <span key={t} className="badge" style={{ background: "var(--primary-soft)", color: "var(--primary)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                  {t}
                  <button type="button" onClick={() => setTags(tags.filter((x) => x !== t))} style={{ border: "none", background: "none", cursor: "pointer", color: "var(--primary)", fontSize: 14, padding: 0 }}>&times;</button>
                </span>
              ))}
            </div>
            <div style={{ display: "flex", gap: 4 }}>
              <input placeholder="Add tag" value={tagInput} onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); if (tagInput.trim() && !tags.includes(tagInput.trim())) { setTags([...tags, tagInput.trim()]); setTagInput(""); } }}}
                style={{ flex: 1 }} />
              <button type="button" className="btn btn-secondary" onClick={() => { if (tagInput.trim() && !tags.includes(tagInput.trim())) { setTags([...tags, tagInput.trim()]); setTagInput(""); } }}>Add</button>
            </div>
          </div>
        </div>

        <div className="btn-row">
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Saving..." : "Save Changes"}</button>
        </div>
      </form>
    </div>
  );
}
