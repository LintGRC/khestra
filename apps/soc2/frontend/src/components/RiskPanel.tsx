import { FormEvent, useEffect, useState } from "react";
import { api, RiskItem } from "../api";

const LEVELS = ["low", "medium", "high", "critical"];
const TREATMENTS = ["mitigate", "accept", "transfer", "avoid"];

function levelColor(level: string): string {
  const m: Record<string, string> = { low: "badge-muted", medium: "badge-warning", high: "badge-danger", critical: "badge-danger" };
  return m[level] || "badge-muted";
}

export default function RiskPanel({
  controlId,
  canEdit,
  risks: initialRisks,
}: {
  controlId: string;
  canEdit: boolean;
  risks: RiskItem[];
}) {
  const [risks, setRisks] = useState<RiskItem[]>(initialRisks);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    title: "", description: "", category: "operational", control_id: controlId,
    inherent_likelihood: "medium", inherent_impact: "medium",
    residual_likelihood: "low", residual_impact: "low",
    treatment: "mitigate", controls: "", owner: "", review_date: "",
  });

  useEffect(() => { setRisks(initialRisks); }, [initialRisks]);
  const controlRisks = risks.filter((r) => r.control_id === controlId);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.createRisk(form);
      setRisks((prev) => [...prev, res.risk]);
      setShowForm(false);
      setForm((f) => ({ ...f, title: "", description: "", controls: "" }));
    } catch (err) { console.error(err); } finally { setSaving(false); }
  }

  async function handleStatus(id: string, status: string) {
    try {
      const res = await api.updateRisk(id, { status });
      setRisks((prev) => prev.map((r) => (r.id === id ? res.risk : r)));
    } catch (err) { console.error(err); }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this risk?")) return;
    try { await api.deleteRisk(id); setRisks((prev) => prev.filter((r) => r.id !== id)); }
    catch (err) { console.error(err); }
  }

  return (
    <div className="panel">
      <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Risk Register ({controlRisks.length})</h3>
        {canEdit && <button className="btn btn-sm" onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "+ Add Risk"}</button>}
      </div>

      {showForm && (
        <form className="panel-body risk-form" onSubmit={handleCreate}>
          <label>Risk title <input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} required /></label>
          <label>Description <textarea rows={2} value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} required /></label>
          <div className="form-row" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
            <label>Inherent likelihood
              <select value={form.inherent_likelihood} onChange={(e) => setForm((f) => ({ ...f, inherent_likelihood: e.target.value }))}>
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </label>
            <label>Inherent impact
              <select value={form.inherent_impact} onChange={(e) => setForm((f) => ({ ...f, inherent_impact: e.target.value }))}>
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </label>
            <label>Treatment
              <select value={form.treatment} onChange={(e) => setForm((f) => ({ ...f, treatment: e.target.value }))}>
                {TREATMENTS.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>
          </div>
          <div className="form-row" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
            <label>Residual likelihood
              <select value={form.residual_likelihood} onChange={(e) => setForm((f) => ({ ...f, residual_likelihood: e.target.value }))}>
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </label>
            <label>Residual impact
              <select value={form.residual_impact} onChange={(e) => setForm((f) => ({ ...f, residual_impact: e.target.value }))}>
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </label>
            <label>Review date <input type="date" value={form.review_date} onChange={(e) => setForm((f) => ({ ...f, review_date: e.target.value }))} /></label>
          </div>
          <label>Controls / mitigation <textarea rows={2} value={form.controls} onChange={(e) => setForm((f) => ({ ...f, controls: e.target.value }))} placeholder="What controls reduce this risk?" /></label>
          <button className="btn btn-primary" disabled={saving}>{saving ? "Saving..." : "Add Risk"}</button>
        </form>
      )}

      <div className="panel-body">
        {controlRisks.length === 0 && !showForm && <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No risks recorded for this criterion.</p>}
        {controlRisks.map((risk) => (
          <div key={risk.id} style={{ border: "1px solid var(--border-color)", borderRadius: "8px", padding: "1rem", marginBottom: "0.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem", flexWrap: "wrap", gap: "0.5rem" }}>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                <span className={`badge ${levelColor(risk.residual_level)}`}>{risk.residual_level} ({risk.residual_score})</span>
                <span className="badge badge-muted">inherent: {risk.inherent_level} ({risk.inherent_score})</span>
                <span className="badge badge-muted">{risk.treatment}</span>
                <span className="badge badge-muted">{risk.status.replace(/_/g, " ")}</span>
              </div>
              {canEdit && (
                <div style={{ display: "flex", gap: "0.25rem" }}>
                  {risk.status === "identified" && <button className="btn btn-sm" onClick={() => handleStatus(risk.id, "in_treatment")}>Start Treatment</button>}
                  {risk.status === "in_treatment" && <button className="btn btn-sm btn-success" onClick={() => handleStatus(risk.id, "accepted")}>Accept</button>}
                  {risk.status !== "closed" && <button className="btn btn-sm btn-ghost" onClick={() => handleStatus(risk.id, "closed")}>Close</button>}
                  <button className="btn btn-sm btn-ghost" onClick={() => handleDelete(risk.id)}>Delete</button>
                </div>
              )}
            </div>
            <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{risk.title}</p>
            <p style={{ fontSize: "0.9rem", marginBottom: "0.25rem" }}>{risk.description}</p>
            {risk.controls && <p style={{ fontSize: "0.85rem" }}><strong>Controls:</strong> {risk.controls}</p>}
            <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.5rem" }}>
              Owner: {risk.owner} · Created: {risk.created_at?.slice(0, 10)}
              {risk.review_date && ` · Review: ${risk.review_date}`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
