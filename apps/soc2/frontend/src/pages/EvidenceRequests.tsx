import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, EvidenceRequest } from "../api";
import { useLayout } from "../Layout";
import PageIntro from "../components/PageIntro";
import { PageSkeleton, EmptyState } from "../components/ui/Skeleton";

export default function EvidenceRequestsPage() {
  const { canEdit } = useLayout();
  const [requests, setRequests] = useState<EvidenceRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ control_id: "", title: "", assigned_to: "", due_date: "", description: "" });
  const [saving, setSaving] = useState(false);

  const reload = async () => {
    const data = await api.evidenceRequests();
    setRequests(data.requests);
  };

  useEffect(() => {
    reload().catch(console.error).finally(() => setLoading(false));
  }, []);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.control_id || !form.title) return;
    setSaving(true);
    try {
      await api.createEvidenceRequest(form);
      setForm({ control_id: "", title: "", assigned_to: "", due_date: "", description: "" });
      setShowForm(false);
      await reload();
    } finally {
      setSaving(false);
    }
  };

  const onStatusChange = async (id: string, status: string) => {
    await api.patchEvidenceRequest(id, { status });
    await reload();
  };

  if (loading) return <PageSkeleton variant="default" />;

  const openReqs = requests.filter((r) => r.status === "open");
  const closedReqs = requests.filter((r) => r.status !== "open");

  return (
    <div className="page-stack">
      <PageIntro title="Evidence Requests" />

      {canEdit && (
        <div className="controls-toolbar">
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "New request"}
          </button>
        </div>
      )}

      {showForm && (
        <form className="panel panel-form" onSubmit={onSubmit}>
          <div className="panel-body">
          <div className="form-row">
            <label>
              Criterion
              <input
                required
                placeholder="e.g. CC6.1"
                value={form.control_id}
                onChange={(e) => setForm((f) => ({ ...f, control_id: e.target.value }))}
              />
            </label>
            <label>
              Title
              <input
                required
                placeholder="e.g. MFA configuration evidence"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              />
            </label>
          </div>
          <div className="form-row">
            <label>
              Assigned to
              <input
                placeholder="Control owner name"
                value={form.assigned_to}
                onChange={(e) => setForm((f) => ({ ...f, assigned_to: e.target.value }))}
              />
            </label>
            <label>
              Due date
              <input
                type="date"
                value={form.due_date}
                onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
              />
            </label>
          </div>
          <label>
            Description
            <textarea
              rows={2}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </label>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Creating…" : "Create request"}
          </button>
          </div>
        </form>
      )}

      {openReqs.length > 0 && (
        <>
          <h3 className="page-section-heading">Open requests ({openReqs.length})</h3>
          <div className="panel-stack">
            {openReqs.map((req) => (
              <div key={req.id} className="panel request-card">
                <div className="panel-header">
                  <strong>
                    <Link to={`/criteria/${encodeURIComponent(req.control_id)}`}>{req.control_id}</Link>
                    {" — "}{req.title}
                  </strong>
                  <span className={`badge ${req.due_date && new Date(req.due_date) < new Date() ? "badge-danger" : "badge-warning"}`}>
                    {req.status}
                  </span>
                </div>
                <div className="panel-body">
                  {req.description && <p className="muted">{req.description}</p>}
                  <div className="request-meta">
                    {req.assigned_to && <span>Assigned to: <strong>{req.assigned_to}</strong></span>}
                    {req.due_date && <span>Due: <strong>{req.due_date}</strong></span>}
                    <span className="muted">Created: {req.created_at}</span>
                  </div>
                  {canEdit && (
                    <div className="request-actions">
                      <button className="btn btn-sm btn-success" onClick={() => onStatusChange(req.id, "fulfilled")}>
                        Mark fulfilled
                      </button>
                      <button className="btn btn-sm btn-secondary" onClick={() => onStatusChange(req.id, "cancelled")}>
                        Cancel
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {openReqs.length === 0 && closedReqs.length === 0 && (
        <EmptyState
          title="No evidence requests"
          description="Create requests to assign evidence collection to control owners."
        />
      )}

      {closedReqs.length > 0 && (
        <details className="dashboard-details">
          <summary>Closed requests ({closedReqs.length})</summary>
          <div className="dashboard-details-body panel-stack">
            {closedReqs.map((req) => (
              <div key={req.id} className="panel request-card">
                <div className="panel-header">
                  <strong>{req.control_id} — {req.title}</strong>
                  <span className="badge">{req.status}</span>
                </div>
                <div className="panel-body">
                  {req.assigned_to && <span className="muted">Assigned to: {req.assigned_to}</span>}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
