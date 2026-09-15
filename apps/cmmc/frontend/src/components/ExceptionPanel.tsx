import { FormEvent, useEffect, useState } from "react";
import { api, ExceptionItem } from "../api";

export default function ExceptionPanel({
  controlId,
  canEdit,
}: {
  controlId: string;
  canEdit: boolean;
}) {
  const [allExceptions, setAllExceptions] = useState<ExceptionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    description: "",
    compensating_controls: "",
    risk_acceptance: "",
    risk_level: "medium",
    expiry_date: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.listExceptions()
      .then((data) => setAllExceptions(data.exceptions || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const exceptions = allExceptions.filter((e) => e.control_id === controlId);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.createException({
        control_id: controlId,
        description: form.description,
        compensating_controls: form.compensating_controls,
        risk_acceptance: form.risk_acceptance,
        risk_level: form.risk_level,
        expiry_date: form.expiry_date,
        created_by: "user",
      });
      setAllExceptions((prev) => [...prev, res.exception]);
      setShowForm(false);
      setForm({ description: "", compensating_controls: "", risk_acceptance: "", risk_level: "medium", expiry_date: "" });
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateStatus(id: string, status: string) {
    try {
      const res = await api.updateException(id, { status });
      setAllExceptions((prev) => prev.map((e) => (e.id === id ? res.exception : e)));
    } catch (err) {
      console.error(err);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this exception?")) return;
    try {
      await api.deleteException(id);
      setAllExceptions((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      console.error(err);
    }
  }

  const statusBadge = (s: string) => {
    const cls: Record<string, string> = {
      open: "badge-warning",
      pending_approval: "badge-warning",
      approved: "badge-success",
      rejected: "badge-danger",
      expired: "badge-danger",
      closed: "badge-muted",
    };
    return <span className={`badge ${cls[s] || "badge-muted"}`}>{s.replace(/_/g, " ")}</span>;
  };

  const riskBadge = (r: string) => {
    const cls: Record<string, string> = {
      low: "badge-muted",
      medium: "badge-warning",
      high: "badge-danger",
      critical: "badge-danger",
    };
    return <span className={`badge ${cls[r] || "badge-muted"}`}>{r}</span>;
  };

  const milestoneCount = (exc: ExceptionItem) => {
    const ms = exc.milestones || [];
    const done = ms.filter((m) => m.status === "completed").length;
    return ms.length ? `${done}/${ms.length}` : "";
  };

  if (loading) return null;

  return (
    <div className="panel exception-panel" style={{ marginTop: "1.5rem" }}>
      <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>Exceptions ({exceptions.length})</strong>
        {canEdit && (
          <button className="btn btn-sm" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ New Exception"}
          </button>
        )}
      </div>

      {showForm && (
        <form className="panel-body" onSubmit={handleCreate} style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: "1rem" }}>
          <div className="form-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            <div style={{ gridColumn: "span 2" }}>
              <label>Why is this exception needed?</label>
              <textarea rows={2} value={form.description} required
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="e.g., Legacy system cannot support required control until Q1 migration..."
              />
            </div>
            <div style={{ gridColumn: "span 2" }}>
              <label>Compensating controls</label>
              <textarea rows={2} value={form.compensating_controls}
                onChange={(e) => setForm((f) => ({ ...f, compensating_controls: e.target.value }))}
                placeholder="e.g., Network segmentation, monthly manual review..."
              />
            </div>
            <div>
              <label>Risk level</label>
              <select value={form.risk_level} onChange={(e) => setForm((f) => ({ ...f, risk_level: e.target.value }))}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label>Expiry date</label>
              <input type="date" value={form.expiry_date} onChange={(e) => setForm((f) => ({ ...f, expiry_date: e.target.value }))} />
            </div>
            <div style={{ gridColumn: "span 2" }}>
              <label>Risk acceptance rationale</label>
              <textarea rows={2} value={form.risk_acceptance}
                onChange={(e) => setForm((f) => ({ ...f, risk_acceptance: e.target.value }))}
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-sm" disabled={saving} style={{ marginTop: "0.5rem" }}>
            {saving ? "Saving..." : "Create Exception"}
          </button>
        </form>
      )}

      <div className="panel-body">
        {exceptions.length === 0 && !showForm && (
          <p className="muted" style={{ textAlign: "center", padding: "1rem", fontSize: "0.85rem" }}>
            No exceptions for this control.
          </p>
        )}
        {exceptions.map((exc) => (
          <div key={exc.id} style={{ border: "1px solid var(--border-color)", borderRadius: "6px", padding: "0.75rem", marginBottom: "0.5rem", fontSize: "0.85rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.35rem" }}>
              <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap", alignItems: "center" }}>
                {statusBadge(exc.status)}
                {riskBadge(exc.risk_level)}
                {exc.expiry_date && <span className="muted" style={{ fontSize: "0.8rem" }}>Expires: {exc.expiry_date}</span>}
                {exc.expiry_date && exc.expiry_date < new Date().toISOString().slice(0, 10) && exc.status !== "closed" && exc.status !== "rejected" && (
                  <span className="badge badge-danger" style={{ fontSize: "0.75rem" }}>OVERDUE</span>
                )}
              </div>
              {canEdit && (
                <div style={{ display: "flex", gap: "0.25rem" }}>
                  {exc.status === "pending_approval" && (
                    <>
                      <button className="btn btn-sm btn-success" onClick={() => handleUpdateStatus(exc.id, "approved")} title="Approve">✓</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleUpdateStatus(exc.id, "rejected")} title="Reject">✗</button>
                    </>
                  )}
                  {exc.status !== "rejected" && exc.status !== "closed" && exc.status !== "expired" && exc.status !== "approved" && (
                    <button className="btn btn-sm btn-success" onClick={() => handleUpdateStatus(exc.id, "pending_approval")} title="Submit for approval">↑</button>
                  )}
                  <button className="btn btn-sm btn-ghost" onClick={() => handleDelete(exc.id)} title="Delete">×</button>
                </div>
              )}
            </div>
            <p style={{ marginBottom: "0.25rem" }}>{exc.description}</p>
            {exc.compensating_controls && (
              <p className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                <strong>Compensating:</strong> {exc.compensating_controls}
              </p>
            )}
            {(exc.milestones || []).length > 0 && (
              <div style={{ marginTop: "0.35rem" }}>
                <span className="muted" style={{ fontSize: "0.75rem" }}>Milestones: </span>
                <span style={{ fontSize: "0.75rem" }}>{milestoneCount(exc)}</span>
                {exc.milestones!.map((m) => (
                  <div key={m.id} style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.75rem", marginTop: "0.15rem" }}>
                    <span>{m.status === "completed" ? "✓" : "○"}</span>
                    <span>{m.description}</span>
                    {m.target_date && <span className="muted">— due {m.target_date}</span>}
                    {m.completion_date && <span className="muted">(done {m.completion_date})</span>}
                  </div>
                ))}
              </div>
            )}
            <div className="muted" style={{ fontSize: "0.7rem", marginTop: "0.25rem" }}>
              Created by {exc.created_by || "unknown"} on {(exc.created_at || "").slice(0, 10)}
              {exc.approved_by && ` · Approved by ${exc.approved_by}`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
