import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { auditApi } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import type { Audit, EvidenceRequest } from "../types";
import { AUDIT_STATUSES, AUDIT_TYPES, REQUEST_STATUSES } from "../types";

function statusBadge(status: string) {
  const m: Record<string, string> = {
    planned: "badge-muted", in_progress: "badge-warning", frozen: "badge-info",
    completed: "badge-success", cancelled: "badge-muted",
    open: "badge-muted", submitted: "badge-info",
    approved: "badge-success", rejected: "badge-danger", waived: "badge-warning",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace("_", " ")}</span>;
}

type AuditLogEntry = {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
};

export default function AuditDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [audit, setAudit] = useState<Audit | null>(null);
  const [requests, setRequests] = useState<EvidenceRequest[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    title: "", framework: "", audit_type: "", status: "",
    start_date: "", end_date: "", auditor_name: "", auditor_email: "",
    scope_notes: "", preparation_notes: "", control_id: "",
  });
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [reqForm, setReqForm] = useState({ title: "", control_id: "", description: "", assigned_to: "", due_date: "" });
  const [saving, setSaving] = useState(false);

  const load = async () => {
    if (!id) return;
    try {
      const [{ audit }, { requests }] = await Promise.all([
        auditApi.get(id),
        auditApi.listRequests(id),
      ]);
      setAudit(audit);
      setRequests(requests || []);

      try {
        const qs = audit.framework ? `?framework_id=${audit.framework}` : "";
        const res = await fetch(apiUrl(`/api/audit-log${qs}`));
        const logData = await res.json();
        const entries: AuditLogEntry[] = (logData.entries || []).filter((e: any) => {
          if (!audit.start_date && !audit.end_date) return false;
          const ts = e.timestamp?.slice(0, 10);
          if (!ts) return false;
          if (audit.start_date && ts < audit.start_date.slice(0, 10)) return false;
          if (audit.end_date && ts > audit.end_date.slice(0, 10)) return false;
          return true;
        });
        setAuditLog(entries);
      } catch { /* non-critical */ }
    } catch {
      setError("Failed to load audit.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const startEdit = () => {
    if (!audit) return;
    setEditForm({
      title: audit.title, framework: audit.framework, audit_type: audit.audit_type,
      status: audit.status, start_date: audit.start_date, end_date: audit.end_date,
      auditor_name: audit.auditor_name, auditor_email: audit.auditor_email,
      scope_notes: audit.scope_notes, preparation_notes: audit.preparation_notes,
      control_id: audit.control_id || "",
    });
    setEditing(true);
  };

  const saveEdit = async () => {
    if (!id || !audit) return;
    setSaving(true);
    try {
      const { audit: updated } = await auditApi.update(id, editForm);
      setAudit(updated);
      setEditing(false);
    } catch { /* ignore */ }
    finally { setSaving(false); }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!id || !audit) return;
    try {
      const { audit: updated } = await auditApi.update(id, { status: newStatus });
      setAudit(updated);
    } catch { /* ignore */ }
  };

  const handleFreeze = async () => {
    if (!id) return;
    try {
      const { audit: updated } = await auditApi.freeze(id);
      setAudit(updated);
    } catch { /* ignore */ }
  };

  const handleDelete = async () => {
    if (!id || !confirm("Delete this audit and all evidence requests?")) return;
    try {
      await auditApi.delete(id);
      navigate("..", { replace: true });
    } catch { /* ignore */ }
  };

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !reqForm.title.trim()) return;
    setSaving(true);
    try {
      await auditApi.createRequest(id, reqForm);
      setReqForm({ title: "", control_id: "", description: "", assigned_to: "", due_date: "" });
      setShowRequestForm(false);
      const { requests: updated } = await auditApi.listRequests(id);
      setRequests(updated || []);
    } catch { /* ignore */ }
    finally { setSaving(false); }
  };

  const handleDeleteRequest = async (reqId: string) => {
    if (!id || !confirm("Delete this evidence request?")) return;
    try {
      await auditApi.deleteRequest(id, reqId);
      setRequests(requests.filter((r) => r.id !== reqId));
    } catch { /* ignore */ }
  };

  const handleRequestStatus = async (reqId: string, status: string) => {
    if (!id) return;
    try {
      await auditApi.updateRequest(id, reqId, { status });
      setRequests(requests.map((r) => r.id === reqId ? { ...r, status } : r));
    } catch { /* ignore */ }
  };

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;
  if (error || !audit) return <div className="page-stack"><div className="banner error">{error || "Audit not found."}</div></div>;

  const changeHistory = auditLog.slice(0, 100);

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          {editing ? (
            <input value={editForm.title} onChange={(e) => setEditForm({ ...editForm, title: e.target.value })} style={{ fontSize: "1.25rem", fontWeight: 700, width: "100%" }} />
          ) : (
            <h2 style={{ margin: 0 }}>{audit.title}</h2>
          )}
          <p className="muted" style={{ marginTop: 4 }}>
            {audit.framework && `${audit.framework} \u00B7 `}
            {audit.audit_type?.replace("_", " ") || "Audit"} {statusBadge(audit.status)}
            {audit.start_date && ` \u00B7 ${audit.start_date.slice(0, 10)} \u2192 ${audit.end_date?.slice(0, 10) || ""}`}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexShrink: 0 }}>
          {audit.status === "planned" && <button className="btn btn-primary btn-sm" onClick={() => handleStatusChange("in_progress")}>Start Audit</button>}
          {audit.status === "in_progress" && <button className="btn btn-secondary btn-sm" onClick={handleFreeze}>Freeze</button>}
          {audit.status !== "completed" && audit.status !== "cancelled" && <button className="btn btn-secondary btn-sm" onClick={() => handleStatusChange("completed")}>Complete</button>}
          <button className="btn btn-secondary btn-sm" onClick={editing ? saveEdit : startEdit} disabled={saving}>{editing ? "Save" : "Edit"}</button>
          <button className="btn btn-danger btn-sm" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      {editing && <div className="banner info" style={{ marginBottom: "1rem" }}>Editing audit metadata. Click Save when done.</div>}

      <div className="panel" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", padding: "1rem" }}>
        {([
          ["Framework", "framework", "text"],
          ["Audit Type", "audit_type", "select"],
          ["Status", "status", "select"],
          ["Start Date", "start_date", "date"],
          ["End Date", "end_date", "date"],
          ["Auditor Name", "auditor_name", "text"],
          ["Auditor Email", "auditor_email", "text"],
          ["Control ID", "control_id", "text"],
        ] as const).map(([label, key, type]) => (
          <div key={key}>
            <label style={{ fontWeight: 600, fontSize: "0.85rem", color: "var(--muted)" }}>{label}</label>
            {editing ? (
              type === "select" ? (
                <select
                  value={(editForm as any)[key]}
                  onChange={(e) => setEditForm({ ...editForm, [key]: e.target.value })}
                  style={{ width: "100%" }}
                >
                  {(key === "audit_type" ? AUDIT_TYPES : AUDIT_STATUSES).map((opt) => (
                    <option key={opt} value={opt}>{opt.replace("_", " ")}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={type}
                  value={(editForm as any)[key]}
                  onChange={(e) => setEditForm({ ...editForm, [key]: e.target.value })}
                  style={{ width: "100%" }}
                />
              )
            ) : (
              <p style={{ margin: 0 }}>{(audit as any)[key] || "-"}</p>
            )}
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div className="panel" style={{ padding: "1rem" }}>
          <h4 style={{ margin: "0 0 0.5rem" }}>Scope</h4>
          {editing ? (
            <textarea value={editForm.scope_notes} onChange={(e) => setEditForm({ ...editForm, scope_notes: e.target.value })} rows={4} style={{ width: "100%" }} />
          ) : (
            <p className="muted" style={{ margin: 0, whiteSpace: "pre-wrap" }}>{audit.scope_notes || "No scope notes."}</p>
          )}
        </div>
        <div className="panel" style={{ padding: "1rem" }}>
          <h4 style={{ margin: "0 0 0.5rem" }}>Preparation Notes</h4>
          {editing ? (
            <textarea value={editForm.preparation_notes} onChange={(e) => setEditForm({ ...editForm, preparation_notes: e.target.value })} rows={4} style={{ width: "100%" }} />
          ) : (
            <p className="muted" style={{ margin: 0, whiteSpace: "pre-wrap" }}>{audit.preparation_notes || "No preparation notes."}</p>
          )}
        </div>
      </div>

      <div className="panel" style={{ padding: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
          <h4 style={{ margin: 0 }}>Evidence Requests ({requests.length})</h4>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowRequestForm(!showRequestForm)}>
            {showRequestForm ? "Cancel" : "+ Request"}
          </button>
        </div>

        {showRequestForm && (
          <form onSubmit={handleCreateRequest} style={{ marginBottom: "1rem", padding: "0.75rem", background: "var(--primary-soft)", borderRadius: "var(--radius)" }}>
            <label>
              Title *
              <input value={reqForm.title} onChange={(e) => setReqForm({ ...reqForm, title: e.target.value })} placeholder="Firewall configuration audit" style={{ width: "100%" }} />
            </label>
            <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
              <label style={{ flex: 1 }}>
                Control ID
                <input value={reqForm.control_id} onChange={(e) => setReqForm({ ...reqForm, control_id: e.target.value })} placeholder="SC.L2-3.13.1" style={{ width: "100%" }} />
              </label>
              <label style={{ flex: 1 }}>
                Assigned To
                <input value={reqForm.assigned_to} onChange={(e) => setReqForm({ ...reqForm, assigned_to: e.target.value })} placeholder="jane@example.com" style={{ width: "100%" }} />
              </label>
              <label style={{ flex: 1 }}>
                Due Date
                <input type="date" value={reqForm.due_date} onChange={(e) => setReqForm({ ...reqForm, due_date: e.target.value })} style={{ width: "100%" }} />
              </label>
            </div>
            <button className="btn btn-primary btn-sm" type="submit" disabled={saving || !reqForm.title.trim()} style={{ marginTop: "0.5rem" }}>
              {saving ? "Sending..." : "Send Request"}
            </button>
          </form>
        )}

        {requests.length === 0 ? (
          <p className="muted" style={{ margin: 0 }}>No evidence requests yet.</p>
        ) : (
          <table className="data-table" style={{ width: "100%" }}>
            <thead>
              <tr>
                <th>Title</th>
                <th>Control</th>
                <th>Assigned To</th>
                <th>Status</th>
                <th>Due</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 600 }}>{r.title}</td>
                  <td style={{ fontFamily: "ui-monospace, monospace", fontSize: "13px" }}>{r.control_id || "-"}</td>
                  <td>{r.assigned_to || "-"}</td>
                  <td>
                    <select value={r.status} onChange={(e) => handleRequestStatus(r.id, e.target.value)} style={{ padding: "2px 4px", fontSize: "12px" }}>
                      {REQUEST_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td>{r.due_date ? r.due_date.slice(0, 10) : "-"}</td>
                  <td>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDeleteRequest(r.id)} style={{ fontSize: "11px", padding: "2px 6px" }}>Remove</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="panel" style={{ padding: "1rem" }}>
        <h4 style={{ margin: "0 0 0.75rem" }}>
          Change History
          {audit.start_date && audit.end_date && (
            <span className="muted" style={{ fontWeight: 400, fontSize: "0.85rem", marginLeft: "0.5rem" }}>
              {audit.start_date.slice(0, 10)} \u2013 {audit.end_date.slice(0, 10)}
            </span>
          )}
        </h4>

        {changeHistory.length === 0 ? (
          <p className="muted" style={{ margin: 0 }}>
            {audit.start_date && audit.end_date
              ? "No system changes recorded during this audit period."
              : "Set a date range on this audit to see system changes during that period."}
          </p>
        ) : (
          <div style={{ fontFamily: "ui-monospace, Menlo, monospace", fontSize: "13px", lineHeight: "1.8" }}>
            {changeHistory.map((e) => (
              <div key={e.id} style={{ display: "flex", gap: "12px", padding: "3px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                <span style={{ color: "var(--muted)", whiteSpace: "nowrap", minWidth: 140 }}>{e.timestamp?.slice(0, 19).replace("T", " ")}</span>
                <span style={{ fontWeight: 600, minWidth: 80 }}>{e.action.toUpperCase()}</span>
                <span style={{ color: "var(--text)" }}>{e.resource_type}/{e.resource_id}</span>
                <span style={{ color: "var(--muted)", marginLeft: "auto" }}>{e.user_email}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
