import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { exceptionApi } from "../api";
import type { ExceptionItem, Milestone, HistoryEntry } from "../types";

function statusBadge(s: string) {
  const cls: Record<string, string> = {
    open: "badge-muted",
    pending_approval: "badge-warning",
    approved: "badge-success",
    rejected: "badge-danger",
    expired: "badge-danger",
    closed: "badge-muted",
  };
  return <span className={`badge ${cls[s] || "badge-muted"}`}>{s.replace(/_/g, " ")}</span>;
}

export default function ExceptionDetail({ title = "Exception", basePath = "/exceptions" }: { title?: string; basePath?: string }) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [exc, setExc] = useState<ExceptionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    likelihood: 1,
    impact: 1,
    compensating_controls: "",
    owner: "",
    framework: "",
    control_reference: "",
    expiry_days: 90,
  });
  const [commentText, setCommentText] = useState("");
  const [commentAuthor, setCommentAuthor] = useState("");
  const [milestoneForm, setMilestoneForm] = useState({ description: "", target_date: "", owner: "" });
  const [uploading, setUploading] = useState(false);
  const [reviewNotes, setReviewNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const res = await exceptionApi.get(id);
      setExc(res.exception);
      setEditForm({
        title: res.exception.title || "",
        description: res.exception.description || "",
        likelihood: res.exception.likelihood || 1,
        impact: res.exception.impact || 1,
        compensating_controls: res.exception.compensating_controls || "",
        owner: res.exception.owner || "",
        framework: res.exception.framework || "",
        control_reference: res.exception.control_reference || "",
        expiry_days: res.exception.expiry_days || 90,
      });
    } catch (e) {
      console.error(e);
      setError(`${title} not found.`);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;
  if (error || !exc) return <div className="page-stack"><div className="banner error">{error || "Not found"}</div></div>;

  const riskScore = editForm.likelihood * editForm.impact;
  const riskLevel = riskScore >= 15 ? "critical" : riskScore >= 10 ? "high" : riskScore >= 5 ? "medium" : "low";

  const handleSave = async () => {
    if (!id) return;
    setSaving(true);
    try {
      await exceptionApi.update(id, {
        title: editForm.title,
        description: editForm.description,
        likelihood: editForm.likelihood,
        impact: editForm.impact,
        compensating_controls: editForm.compensating_controls,
        owner: editForm.owner,
        framework: editForm.framework,
        control_reference: editForm.control_reference,
        expiry_days: editForm.expiry_days,
      });
      setEditing(false);
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!id) return;
    try {
      await exceptionApi.update(id, { status: newStatus as ExceptionItem["status"] });
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async () => {
    if (!id || !confirm(`Delete this ${title.toLowerCase()} permanently?`)) return;
    try {
      await exceptionApi.delete(id);
      navigate(basePath);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddComment = async () => {
    if (!id || !commentText.trim()) return;
    try {
      await exceptionApi.addComment(id, commentAuthor || "Anonymous", commentText);
      setCommentText("");
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddMilestone = async () => {
    if (!id || !milestoneForm.description.trim()) return;
    try {
      await exceptionApi.addMilestone(id, milestoneForm.description, milestoneForm.target_date, milestoneForm.owner);
      setMilestoneForm({ description: "", target_date: "", owner: "" });
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpdateMilestone = async (mid: string, updates: Partial<Milestone>) => {
    if (!id) return;
    try {
      await exceptionApi.updateMilestone(id, mid, updates);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteMilestone = async (mid: string) => {
    if (!id || !confirm("Delete this milestone?")) return;
    try {
      await exceptionApi.deleteMilestone(id, mid);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleUploadAttachment = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!id || !e.target.files?.length) return;
    setUploading(true);
    try {
      await exceptionApi.uploadAttachment(id, e.target.files[0]);
      await load();
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleExtend = async () => {
    if (!id) return;
    const days = prompt("Extend by how many days?", "90");
    if (!days) return;
    try {
      exceptionApi.extend(id, parseInt(days), "Extended via UI", "");
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleReview = async (outcome: string) => {
    if (!id) return;
    try {
      await exceptionApi.review(id, outcome, reviewNotes, "");
      setReviewNotes("");
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const sortedComments = [...(exc.comments || [])].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );

  const sortedHistory = [...(exc.history || [])].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
  );

  const isExpired = exc.is_expired || exc.status === "expired";
  const isExpiring = exc.days_left > 0 && exc.days_left <= 14;
  const isApproved = exc.status === "approved";
  const isOpen = exc.status === "open" || exc.status === "pending_approval";

  return (
    <div className="page-stack">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <button className="btn btn-sm btn-ghost" onClick={() => navigate(basePath)}>
            &larr; Back
          </button>
          <h2 style={{ margin: 0 }}>{exc.title}</h2>
          {statusBadge(exc.status)}
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {!editing && (
            <>
              <button className="btn btn-sm btn-ghost" onClick={() => setEditing(true)}>Edit</button>
              <button className="btn btn-sm btn-ghost" onClick={() => exceptionApi.downloadApprovalMemo(exc.id)}>Memo</button>
              <button className="btn btn-sm btn-ghost" onClick={() => exceptionApi.downloadAuditorReport(exc.id)}>Audit Report</button>
              <button className="btn btn-sm btn-danger" onClick={handleDelete}>Delete</button>
            </>
          )}
          {editing && (
            <>
              <button className="btn btn-sm btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
              <button className="btn btn-sm btn-ghost" onClick={() => setEditing(false)}>Cancel</button>
            </>
          )}
        </div>
      </div>

      {(isExpired || isExpiring) && (
        <div className="banner" style={{ background: isExpired ? "var(--danger-soft)" : "var(--warning-soft)", border: `1px solid ${isExpired ? "var(--danger-border)" : "var(--warning-border)"}`, borderRadius: "6px", padding: "0.75rem 1rem" }}>
          {isExpired ? `This ${title.toLowerCase()} has expired. Please review and close or extend.` : `This ${title.toLowerCase()} expires in ${exc.days_left} days.`}
        </div>
      )}

      <div className="dashboard-grid">
        {/* Status Timeline */}
        <div className="panel">
          <div className="panel-header"><h3>Status Timeline</h3></div>
          <div className="panel-body" style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
              <span className="muted">Created</span>
              <span>{exc.created_at?.slice(0, 10)}</span>
            </div>
            {exc.expires_at && (
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                <span className="muted">Expires</span>
                <span style={{ color: isExpired ? "var(--danger)" : "inherit" }}>
                  {exc.expires_at.slice(0, 10)} ({isExpired ? "expired" : `${exc.days_left}d left`})
                </span>
              </div>
            )}
            {exc.approved_by && (
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                <span className="muted">Approved by</span>
                <span>{exc.approved_by}</span>
              </div>
            )}
          </div>
        </div>

        {/* Risk Assessment */}
        <div className="panel">
          <div className="panel-header"><h3>Risk Assessment</h3></div>
          <div className="panel-body" style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <div style={{
              padding: "0.75rem",
              borderRadius: "6px",
              textAlign: "center",
              fontWeight: 700,
              fontSize: "1.1rem",
              background: riskLevel === "critical" ? "var(--danger-soft)" : riskLevel === "high" ? "var(--danger-soft)" : riskLevel === "medium" ? "var(--warning-soft)" : "var(--success-soft)",
              color: riskLevel === "critical" ? "var(--danger)" : riskLevel === "high" ? "var(--danger)" : riskLevel === "medium" ? "var(--warning)" : "var(--success)",
            }}>
              Score: {riskScore}/25 &mdash; {riskLevel.toUpperCase()}
            </div>
            {editing ? (
              <div className="form-row">
                <label style={{ fontSize: "0.85rem" }}>
                  Likelihood
                  <select value={editForm.likelihood} onChange={(e) => setEditForm(f => ({ ...f, likelihood: Number(e.target.value) }))} style={{ marginTop: "0.25rem" }}>
                    {[1, 2, 3, 4, 5].map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </label>
                <label style={{ fontSize: "0.85rem" }}>
                  Impact
                  <select value={editForm.impact} onChange={(e) => setEditForm(f => ({ ...f, impact: Number(e.target.value) }))} style={{ marginTop: "0.25rem" }}>
                    {[1, 2, 3, 4, 5].map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </label>
              </div>
            ) : (
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                <span className="muted">Likelihood: {exc.likelihood}/5</span>
                <span className="muted">Impact: {exc.impact}/5</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Description & Compensating Controls */}
      <div className="panel">
        <div className="panel-header"><h3>Details</h3></div>
        <div className="panel-body panel-form">
          {editing ? (
            <>
              <label>
                Title
                <input value={editForm.title} onChange={(e) => setEditForm(f => ({ ...f, title: e.target.value }))} />
              </label>
              <label>
                Description
                <textarea rows={3} value={editForm.description} onChange={(e) => setEditForm(f => ({ ...f, description: e.target.value }))} />
              </label>
              <div className="form-row">
                <label>
                  Framework
                  <select value={editForm.framework} onChange={(e) => setEditForm(f => ({ ...f, framework: e.target.value }))}>
                    {["SOC2", "CMMC", "AI Gov", "NIST 800-171", "ISO 27001", "HIPAA", "PCI-DSS"].map(f => <option key={f} value={f}>{f}</option>)}
                  </select>
                </label>
                <label>
                  Control Reference
                  <input value={editForm.control_reference} onChange={(e) => setEditForm(f => ({ ...f, control_reference: e.target.value }))} />
                </label>
              </div>
              <div className="form-row">
                <label>
                  Owner
                  <input value={editForm.owner} onChange={(e) => setEditForm(f => ({ ...f, owner: e.target.value }))} />
                </label>
                <label>
                  Expiry (days)
                  <select value={editForm.expiry_days} onChange={(e) => setEditForm(f => ({ ...f, expiry_days: Number(e.target.value) }))}>
                    {[30, 60, 90, 120, 180, 365].map(d => <option key={d} value={d}>{d} days</option>)}
                  </select>
                </label>
              </div>
              <label>
                Compensating Controls
                <textarea rows={3} value={editForm.compensating_controls} onChange={(e) => setEditForm(f => ({ ...f, compensating_controls: e.target.value }))} />
              </label>
            </>
          ) : (
            <>
              <p style={{ fontSize: "0.9rem", marginBottom: "0.75rem" }}>{exc.description}</p>
              <div className="form-row" style={{ fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                <div><span className="muted">Framework:</span> {exc.framework}</div>
                <div><span className="muted">Control:</span> {exc.control_reference || exc.control_id}</div>
                <div><span className="muted">Owner:</span> {exc.owner || "—"}</div>
                <div><span className="muted">Created by:</span> {exc.created_by || "—"}</div>
              </div>
              {exc.compensating_controls && (
                <div style={{ marginTop: "0.5rem" }}>
                  <strong style={{ fontSize: "0.85rem" }}>Compensating Controls</strong>
                  <p style={{ fontSize: "0.85rem", margin: "0.25rem 0 0", whiteSpace: "pre-wrap" }}>{exc.compensating_controls}</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Milestones / POA&M */}
      <div className="panel">
        <div className="panel-header"><h3>Milestones & POA&M</h3></div>
        <div className="panel-body">
          {(exc.milestones || []).length === 0 && !editing ? (
            <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>
              No milestones defined.
            </p>
          ) : (
            (exc.milestones || []).map((m) => (
              <div key={m.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.6rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>{m.description}</div>
                  <div style={{ fontSize: "0.78rem", color: "var(--muted)", display: "flex", gap: "1rem", marginTop: "0.15rem" }}>
                    <span>Owner: {m.owner || "—"}</span>
                    {m.target_date && <span>Due: {m.target_date}</span>}
                    {m.completion_date && <span>Completed: {m.completion_date}</span>}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                  <select
                    value={m.status}
                    onChange={(e) => handleUpdateMilestone(m.id, { status: e.target.value as Milestone["status"] })}
                    style={{ fontSize: "0.75rem" }}
                  >
                    <option value="not_started">Not Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                  <button className="btn btn-sm btn-ghost" style={{ fontSize: "0.7rem" }} onClick={() => handleDeleteMilestone(m.id)} title="Delete milestone">
                    &times;
                  </button>
                </div>
              </div>
            ))
          )}
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
            <input
              placeholder="Milestone description..."
              value={milestoneForm.description}
              onChange={(e) => setMilestoneForm(f => ({ ...f, description: e.target.value }))}
              style={{ flex: 1 }}
            />
            <input
              type="date"
              value={milestoneForm.target_date}
              onChange={(e) => setMilestoneForm(f => ({ ...f, target_date: e.target.value }))}
              style={{ width: "140px" }}
            />
            <input
              placeholder="Owner"
              value={milestoneForm.owner}
              onChange={(e) => setMilestoneForm(f => ({ ...f, owner: e.target.value }))}
              style={{ width: "120px" }}
            />
            <button className="btn btn-sm btn-primary" onClick={handleAddMilestone}>Add</button>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Comments */}
        <div className="panel">
          <div className="panel-header"><h3>Comments ({sortedComments.length})</h3></div>
          <div className="panel-body">
            {sortedComments.length === 0 ? (
              <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No comments yet.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "300px", overflowY: "auto" }}>
                {sortedComments.map((c) => (
                  <div key={c.id} style={{ padding: "0.6rem", background: "var(--surface-subtle, rgba(128,128,128,0.04))", borderRadius: "6px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: "0.25rem" }}>
                      <strong>{c.author}</strong>
                      <span className="muted">{c.created_at?.slice(0, 10)}</span>
                    </div>
                    <p style={{ fontSize: "0.85rem", margin: 0 }}>{c.body}</p>
                  </div>
                ))}
              </div>
            )}
            <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.5rem" }}>
              <input
                placeholder="Your name"
                value={commentAuthor}
                onChange={(e) => setCommentAuthor(e.target.value)}
                style={{ width: "120px", fontSize: "0.8rem" }}
              />
              <input
                placeholder="Add a comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                style={{ flex: 1, fontSize: "0.8rem" }}
                onKeyDown={(e) => { if (e.key === "Enter") handleAddComment(); }}
              />
              <button className="btn btn-sm btn-primary" onClick={handleAddComment}>Post</button>
            </div>
          </div>
        </div>

        {/* Attachments */}
        <div className="panel">
          <div className="panel-header"><h3>Attachments ({(exc.attachments || []).length})</h3></div>
          <div className="panel-body">
            {(exc.attachments || []).length === 0 ? (
              <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No attachments uploaded.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "200px", overflowY: "auto" }}>
                {(exc.attachments || []).map((a) => (
                  <div key={a.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.4rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                    <a
                      href={exceptionApi.getAttachmentUrl(exc.id, a.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontSize: "0.85rem" }}
                    >
                      {a.filename}
                    </a>
                    <span className="muted" style={{ fontSize: "0.75rem" }}>{a.uploaded_at?.slice(0, 10)}</span>
                  </div>
                ))}
              </div>
            )}
            <div style={{ marginTop: "0.75rem" }}>
              <label className="btn btn-sm btn-ghost" style={{ cursor: "pointer" }}>
                {uploading ? "Uploading..." : "Upload Attachment"}
                <input type="file" hidden onChange={handleUploadAttachment} disabled={uploading} />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="panel">
        <div className="panel-header"><h3>Activity Timeline</h3></div>
        <div className="panel-body" style={{ maxHeight: "250px", overflowY: "auto" }}>
          {sortedHistory.length === 0 ? (
            <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No activity recorded.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {sortedHistory.map((h, i) => (
                <div key={h.id || i} style={{ display: "flex", gap: "0.75rem", padding: "0.4rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                  <span className="muted" style={{ fontSize: "0.75rem", whiteSpace: "nowrap", minWidth: "80px" }}>
                    {h.timestamp?.slice(0, 10)}
                  </span>
                  <span style={{
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    textTransform: "capitalize",
                    minWidth: "100px",
                  }}>
                    {h.action.replace(/_/g, " ")}
                  </span>
                  <span style={{ fontSize: "0.82rem", color: "var(--muted)" }}>
                    {(h as HistoryEntry).detail || h.notes || ""}
                  </span>
                  {(h as HistoryEntry).performed_by && (
                    <span className="muted" style={{ fontSize: "0.75rem", marginLeft: "auto" }}>
                      {(h as HistoryEntry).performed_by}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Lifecycle Actions */}
      <div className="panel">
        <div className="panel-header"><h3>Lifecycle Actions</h3></div>
        <div className="panel-body" style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <span style={{ fontSize: "0.85rem" }}>Status: {statusBadge(exc.status)}</span>
            <select
              value={exc.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              style={{ fontSize: "0.8rem", width: "auto" }}
            >
              {["open", "pending_approval", "approved", "rejected", "closed"].map((s) => (
                <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>

          {(isApproved || isOpen) && (
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
              <button className="btn btn-sm btn-primary" onClick={handleExtend}>Extend / Re-approve</button>
            </div>
          )}

          <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "0.75rem" }}>
            <p style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.5rem" }}>Periodic Review</p>
            <textarea
              rows={2}
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              placeholder="Review notes..."
              style={{ width: "100%", fontSize: "0.85rem", marginBottom: "0.5rem" }}
            />
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <button className="btn btn-sm btn-success" onClick={() => handleReview("close")}>Close {title}</button>
              <button className="btn btn-sm btn-primary" onClick={() => handleReview("extend")}>Mark Effective & Extend</button>
              <button className="btn btn-sm btn-danger" onClick={() => handleReview("escalate")}>Escalate (Re-open)</button>
              <button className="btn btn-sm btn-danger" onClick={() => handleReview("reject")}>Reject</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
