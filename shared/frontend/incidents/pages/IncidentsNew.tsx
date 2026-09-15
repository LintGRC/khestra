import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type { FailureMode } from "../types";
import { FAILURE_MODE_LABELS } from "../types";

const TEMPLATES: { label: string; values: Partial<Record<string, string>> }[] = [
  { label: "Prompt Injection", values: { title: "Prompt Injection / Jailbreaking Detected", failure_mode: "prompt_injection", severity: "high", description: "User bypassed model guardrails using a crafted prompt, exposing internal system instructions.", impact_description: "Potential unauthorized access to system prompts and training data boundaries." } },
  { label: "Hallucination / Drift", values: { title: "Severe Model Hallucination / Drift", failure_mode: "model_drift", severity: "medium", description: "Model producing factually incorrect outputs with high confidence across multiple queries.", impact_description: "Misinformation risk for end users relying on model outputs for decision-making." } },
  { label: "Data Exfiltration", values: { title: "Unintended PII / Data Exfiltration", failure_mode: "data_exfiltration", severity: "high", description: "Model output contained personally identifiable information (PII) not present in the input.", impact_description: "Potential GDPR/CCPA data breach requiring regulatory notification." } },
  { label: "Bias Complaint", values: { title: "Systemic Bias / Discriminatory Output", failure_mode: "systemic_bias", severity: "medium", description: "Model consistently producing biased outputs against a protected demographic group.", impact_description: "Fairness and discrimination risk requiring ethics committee review." } },
];

export default function IncidentsNew({ basePath = "/incidents" }: { basePath?: string }) {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const prefillControlId = params.get("control_id") || "";
  const [form, setForm] = useState({ title: "", description: "", failure_mode: "", severity: "medium", reporter_name: "", model_name: "", control_id: prefillControlId, impact_description: "", affected_inference_pct: 0, total_users_exposed: 0, downstream_applications: "" });
  const [saving, setSaving] = useState(false);

  const applyTemplate = (tpl: typeof TEMPLATES[0]) => {
    setForm((f) => ({ ...f, ...tpl.values, affected_inference_pct: f.affected_inference_pct, total_users_exposed: f.total_users_exposed, downstream_applications: f.downstream_applications }));
  };

  const handleSubmit = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const d = await api.create({ ...(form as unknown as Parameters<typeof api.create>[0]), title: form.title.trim() });
      navigate(`${basePath}/${d.incident.id}`);
    } catch (e) {
      alert(String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Report Incident</h2>
        <p className="muted">Quick templates to pre-fill common AI incident types</p>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {TEMPLATES.map((t) => (
          <button key={t.label} className="btn btn-sm btn-secondary" onClick={() => applyTemplate(t)}>{t.label}</button>
        ))}
      </div>

      <div className="panel">
        <div className="panel-header"><strong>Incident Details</strong></div>
        <div className="panel-body">
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Title *</label><input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Brief incident title" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Failure Mode</label><select value={form.failure_mode} onChange={(e) => setForm({ ...form, failure_mode: e.target.value })}><option value="">Select...</option>{(Object.entries(FAILURE_MODE_LABELS) as [FailureMode, string][]).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Severity</label><select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Detailed description of the incident" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Reporter Name</label><input value={form.reporter_name} onChange={(e) => setForm({ ...form, reporter_name: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Model Name</label><input value={form.model_name} onChange={(e) => setForm({ ...form, model_name: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Control ID</label><input value={form.control_id} onChange={(e) => setForm({ ...form, control_id: e.target.value })} placeholder="SC.L2-3.13.1" /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Impact Description</label><textarea rows={2} value={form.impact_description} onChange={(e) => setForm({ ...form, impact_description: e.target.value })} placeholder="Business/user impact" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>% Calls Affected</label><input type="number" min={0} max={100} value={form.affected_inference_pct} onChange={(e) => setForm({ ...form, affected_inference_pct: Number(e.target.value) })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Users Exposed</label><input type="number" min={0} value={form.total_users_exposed} onChange={(e) => setForm({ ...form, total_users_exposed: Number(e.target.value) })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Downstream Applications (comma-separated)</label><input value={form.downstream_applications} onChange={(e) => setForm({ ...form, downstream_applications: e.target.value })} /></div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={!form.title.trim() || saving}>{saving ? "Creating..." : "Report Incident"}</button>
            <button className="btn btn-secondary" onClick={() => navigate(basePath)}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  );
}
