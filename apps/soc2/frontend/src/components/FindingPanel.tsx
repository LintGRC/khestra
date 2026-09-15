import { FormEvent, useEffect, useState } from "react";
import { findingApi, FindingItem } from "@shared/audit-findings";

const SEVERITIES = ["critical", "high", "medium", "low", "info"];

export default function FindingPanel({
  controlId,
  canEdit,
  findings: initialFindings,
}: {
  controlId: string;
  canEdit: boolean;
  findings: FindingItem[];
}) {
  const [findings, setFindings] = useState<FindingItem[]>(initialFindings);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    title: "", description: "", severity: "medium",
    control_ids: [controlId], owner: "",
  });

  useEffect(() => { setFindings(initialFindings); }, [initialFindings]);
  const controlFindings = findings.filter((f) => f.control_ids?.includes(controlId));

  function sevColor(s: string): string {
    const m: Record<string, string> = { critical: "badge-danger", high: "badge-danger", medium: "badge-warning", low: "badge-muted", info: "badge-muted" };
    return m[s] || "badge-muted";
  }

  function statusColor(s: string): string {
    const m: Record<string, string> = { open: "badge-danger", in_progress: "badge-warning", in_remediation: "badge-warning", resolved: "badge-success", verified: "badge-success", closed: "badge-muted", dismissed: "badge-muted" };
    return m[s] || "badge-muted";
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await findingApi.create({
        title: form.title,
        description: form.description,
        severity: form.severity,
        control_ids: [controlId],
        owner: form.owner,
        source: "audit",
      });
      setFindings((prev) => [...prev, res.finding]);
      setShowForm(false);
      setForm((f) => ({ ...f, title: "", description: "" }));
    } catch (err) { console.error(err); } finally { setSaving(false); }
  }

  async function handleStatus(id: string, status: string) {
    try {
      const res = await findingApi.update(id, { status });
      setFindings((prev) => prev.map((f) => (f.id === id ? res.finding : f)));
    } catch (err) { console.error(err); }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this finding?")) return;
    try { await findingApi.delete(id); setFindings((prev) => prev.filter((f) => f.id !== id)); }
    catch (err) { console.error(err); }
  }

  return (
    <div className="panel">
      <div className="panel-header" style={{ display: "flex", justifyContent: "space-between" }}>
        <h3>Audit Findings ({controlFindings.length})</h3>
        {canEdit && <button className="btn btn-sm" onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "+ Log Finding"}</button>}
      </div>

      {showForm && (
        <form className="panel-body" onSubmit={handleCreate}>
          <label>Title <input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} required /></label>
          <label>Description <textarea rows={2} value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} required /></label>
          <div className="form-row">
            <label>Severity
              <select value={form.severity} onChange={(e) => setForm((f) => ({ ...f, severity: e.target.value }))}>
                {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </label>
            <label>Owner
              <input value={form.owner} onChange={(e) => setForm((f) => ({ ...f, owner: e.target.value }))} placeholder="email or username" />
            </label>
          </div>
          <button className="btn btn-primary" disabled={saving}>{saving ? "Saving..." : "Log Finding"}</button>
        </form>
      )}

      <div className="panel-body">
        {controlFindings.length === 0 && !showForm && <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No audit findings for this criterion.</p>}
        {controlFindings.map((f) => (
          <div key={f.id} style={{ border: "1px solid var(--border-color)", borderRadius: "8px", padding: "1rem", marginBottom: "0.5rem", borderLeft: `4px solid ${f.severity === "critical" || f.severity === "high" ? "var(--danger)" : "var(--warning)"}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                <span className={`badge ${sevColor(f.severity)}`}>{f.severity}</span>
                <span className={`badge ${statusColor(f.status)}`}>{f.status.replace(/_/g, " ")}</span>
              </div>
              {canEdit && (
                <div style={{ display: "flex", gap: "0.25rem" }}>
                  {f.status === "open" && <button className="btn btn-sm" onClick={() => handleStatus(f.id, "in_remediation")}>Start Fix</button>}
                  {f.status === "in_remediation" && <button className="btn btn-sm btn-success" onClick={() => handleStatus(f.id, "closed")}>Close</button>}
                  {f.status !== "closed" && <button className="btn btn-sm btn-ghost" onClick={() => handleStatus(f.id, "closed")}>Close</button>}
                  <button className="btn btn-sm btn-ghost" onClick={() => handleDelete(f.id)}>Delete</button>
                </div>
              )}
            </div>
            <p style={{ fontWeight: 600 }}>{f.title}</p>
            <p style={{ fontSize: "0.9rem", marginBottom: "0.25rem" }}>{f.description}</p>
            <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.5rem" }}>
              {f.owner && `Owner: ${f.owner} · `}
              {f.created_by && `Created by: ${f.created_by} · `}
              {f.created_at?.slice(0, 10)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
