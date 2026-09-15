import { FormEvent, useEffect, useState } from "react";
import { api, ExceptionItem } from "../api";

export default function ExceptionPanel({
  controlId,
  canEdit,
  exceptions: initialExceptions,
}: {
  controlId: string;
  canEdit: boolean;
  exceptions: ExceptionItem[];
}) {
  const [exceptions, setExceptions] = useState<ExceptionItem[]>(initialExceptions);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    description: "",
    compensating_controls: "",
    risk_acceptance: "",
    risk_level: "medium",
    expiry_date: "",
    control_id: controlId,
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setExceptions(initialExceptions);
  }, [initialExceptions]);

  const controlExceptions = exceptions.filter((e) => e.control_id === controlId);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.createException(form);
      setExceptions((prev) => [...prev, res.exception]);
      setShowForm(false);
      setForm({ ...form, description: "", compensating_controls: "", risk_acceptance: "" });
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdate(id: string, status: string) {
    try {
      const res = await api.updateException(id, { status });
      setExceptions((prev) => prev.map((e) => (e.id === id ? res.exception : e)));
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this exception?")) return;
    try {
      await api.deleteException(id);
      setExceptions((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      console.error(err);
    }
  }

  const statusBadge = (s: string) => {
    const cls: Record<string, string> = {
      pending_approval: "badge-warning",
      approved: "badge-success",
      rejected: "badge-danger",
      expired: "badge-danger",
    };
    return <span className={`badge ${cls[s] || "badge-muted"}`}>{s.replace(/_/g, " ")}</span>;
  };

  const riskBadge = (r: string) => {
    const cls: Record<string, string> = {
      low: "badge-muted", medium: "badge-warning", high: "badge-danger", critical: "badge-danger",
    };
    return <span className={`badge ${cls[r] || "badge-muted"}`}>{r}</span>;
  };

  return (
    <div className="panel exception-panel">
      <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Exceptions & POA&M ({controlExceptions.length})</h3>
        {canEdit && (
          <button className="btn btn-sm" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ New Exception"}
          </button>
        )}
      </div>

      {showForm && (
        <form className="panel-body exception-form" onSubmit={handleCreate}>
          <label>
            Why is this exception needed?
            <textarea
              rows={3}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder="e.g., Legacy system cannot support MFA until Q4 migration..."
              required
            />
          </label>
          <label>
            Compensating controls
            <textarea
              rows={3}
              value={form.compensating_controls}
              onChange={(e) => setForm((f) => ({ ...f, compensating_controls: e.target.value }))}
              placeholder="e.g., Network segmentation, manual access review every 30 days..."
              required
            />
          </label>
          <label>
            Risk acceptance rationale
            <textarea
              rows={2}
              value={form.risk_acceptance}
              onChange={(e) => setForm((f) => ({ ...f, risk_acceptance: e.target.value }))}
              placeholder="e.g., Compensating controls reduce residual risk to acceptable level..."
            />
          </label>
          <div className="form-row">
            <label>
              Risk level
              <select value={form.risk_level} onChange={(e) => setForm((f) => ({ ...f, risk_level: e.target.value }))}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>
            <label>
              Review / expiry date
              <input
                type="date"
                value={form.expiry_date}
                onChange={(e) => setForm((f) => ({ ...f, expiry_date: e.target.value }))}
              />
            </label>
          </div>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving..." : "Create Exception"}
          </button>
        </form>
      )}

      <div className="panel-body">
        {controlExceptions.length === 0 && !showForm && (
          <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>
            No exceptions recorded for this criterion.
          </p>
        )}
        {controlExceptions.map((exc) => (
          <div key={exc.id} className="exception-card" style={{ border: "1px solid var(--border-color)", borderRadius: "8px", padding: "1rem", marginBottom: "0.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                {statusBadge(exc.status)}
                {riskBadge(exc.risk_level)}
                {exc.expiry_date && <span className="muted" style={{ fontSize: "0.8rem" }}>Expires: {exc.expiry_date}</span>}
              </div>
              {canEdit && (
                <div style={{ display: "flex", gap: "0.25rem" }}>
                  {exc.status === "pending_approval" && (
                    <>
                      <button className="btn btn-sm btn-success" onClick={() => handleUpdate(exc.id, "approved")}>Approve</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleUpdate(exc.id, "rejected")}>Reject</button>
                    </>
                  )}
                  <button className="btn btn-sm btn-ghost" onClick={() => handleDelete(exc.id)}>Delete</button>
                </div>
              )}
            </div>
            <p style={{ fontSize: "0.9rem", marginBottom: "0.5rem" }}>{exc.description}</p>
            {exc.compensating_controls && (
              <p style={{ fontSize: "0.85rem", marginBottom: "0.25rem" }}>
                <strong>Compensating controls:</strong> {exc.compensating_controls}
              </p>
            )}
            {exc.risk_acceptance && (
              <p style={{ fontSize: "0.85rem", marginBottom: "0.25rem" }}>
                <strong>Risk acceptance:</strong> {exc.risk_acceptance}
              </p>
            )}
            <div style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
              Created by {exc.created_by} on {exc.created_at?.slice(0, 10)}
              {exc.approved_by && ` · Approved by ${exc.approved_by}`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
