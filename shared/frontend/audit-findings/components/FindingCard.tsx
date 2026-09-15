import { useState, useEffect } from "react";
import { findingApi } from "../api";
import type { FindingItem, CorrectiveAction } from "../types";

type Props = {
  finding: FindingItem;
  onDelete: (id: string) => void;
  onControlClick?: (controlId: string) => void;
  onCreatePoam?: (finding: FindingItem) => void;
};

const STATUS_OPTIONS = [
  "open", "in_progress", "in_remediation", "resolved", "verified", "closed", "dismissed",
];

const STATUS_LABELS: Record<string, string> = {
  open: "Open",
  in_progress: "In Progress",
  in_remediation: "In Remediation",
  resolved: "Resolved",
  verified: "Verified",
  closed: "Closed",
  dismissed: "Dismissed",
};

function sevClass(s: string): string {
  if (s === "critical" || s === "high") return "badge-danger";
  if (s === "medium") return "badge-warning";
  return "badge-muted";
}

function sevBorderColor(s: string): string {
  if (s === "critical" || s === "high") return "var(--danger)";
  if (s === "medium") return "var(--warning)";
  return "var(--border)";
}

export default function FindingCard({ finding, onDelete, onControlClick, onCreatePoam }: Props) {
  const [status, setStatus] = useState(finding.status);
  const [savingStatus, setSavingStatus] = useState(false);

  const [expanded, setExpanded] = useState(false);
  const [actions, setActions] = useState<CorrectiveAction[]>([]);
  const [loadingActions, setLoadingActions] = useState(false);
  const [actionsLoaded, setActionsLoaded] = useState(false);

  const [showAddForm, setShowAddForm] = useState(false);
  const [savingAction, setSavingAction] = useState(false);
  const [actionForm, setActionForm] = useState({ title: "", description: "", owner: "" });

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (expanded && !actionsLoaded) {
      loadActions();
    }
  }, [expanded]);

  const loadActions = async () => {
    setLoadingActions(true);
    try {
      const data = await findingApi.listActions(finding.id);
      setActions(data.actions || []);
      setActionsLoaded(true);
    } catch {
      setError("Failed to load corrective actions.");
    } finally {
      setLoadingActions(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    setError(null);
    setSavingStatus(true);
    setStatus(newStatus);
    try {
      await findingApi.update(finding.id, { status: newStatus });
    } catch {
      setStatus(finding.status);
      setError("Failed to update status.");
    } finally {
      setSavingStatus(false);
    }
  };

  const handleCreateAction = async () => {
    if (!actionForm.title.trim()) return;
    setError(null);
    setSavingAction(true);
    try {
      await findingApi.createAction(finding.id, {
        title: actionForm.title.trim(),
        description: actionForm.description.trim(),
        owner: actionForm.owner.trim(),
      });
      setActionForm({ title: "", description: "", owner: "" });
      setShowAddForm(false);
      await loadActions();
    } catch {
      setError("Failed to create corrective action.");
    } finally {
      setSavingAction(false);
    }
  };

  const handleToggleAction = async (action: CorrectiveAction) => {
    setError(null);
    const newStatus = action.status === "completed" ? "open" : "completed";
    setActions((prev) =>
      prev.map((a) => (a.id === action.id ? { ...a, status: newStatus } : a)),
    );
    try {
      await findingApi.updateAction(finding.id, action.id, { status: newStatus });
    } catch {
      setActions((prev) =>
        prev.map((a) => (a.id === action.id ? { ...a, status: action.status } : a)),
      );
      setError("Failed to update corrective action.");
    }
  };

  const handleDeleteAction = async (actionId: string) => {
    if (!confirm("Delete this corrective action?")) return;
    setError(null);
    try {
      await findingApi.deleteAction(finding.id, actionId);
      setActions((prev) => prev.filter((a) => a.id !== actionId));
    } catch {
      setError("Failed to delete corrective action.");
    }
  };

  const openCount = actions.filter((a) => a.status !== "completed").length;

  return (
    <div
      className="panel finding-card"
      style={{ borderLeft: `4px solid ${sevBorderColor(finding.severity)}` }}
    >
      <div className="finding-card__header">
        <div className="finding-card__tags">
          <span className={`badge ${sevClass(finding.severity)}`}>
            {finding.severity}
          </span>
          {finding.control_ids?.map((cid) => (
            <span
              key={cid}
              className="badge"
              style={onControlClick ? { cursor: "pointer", textDecoration: "underline" } : undefined}
              onClick={onControlClick ? () => onControlClick(cid) : undefined}
            >
              {cid}
            </span>
          ))}
          {finding.source && (
            <span className="badge badge-muted">
              {finding.source.replace(/_/g, " ")}
            </span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <select
            value={status}
            disabled={savingStatus}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="finding-status-select"
          >
            {STATUS_OPTIONS.map((k) => (
              <option key={k} value={k}>
                {STATUS_LABELS[k]}
              </option>
            ))}
          </select>
          {onCreatePoam && (
            <button
              className="btn btn-sm btn-ghost"
              style={{ color: "var(--warning)" }}
              onClick={() => onCreatePoam(finding)}
            >
              POA&M
            </button>
          )}
          <button
            className="btn btn-sm btn-ghost"
            style={{ color: "var(--danger)" }}
            onClick={() => onDelete(finding.id)}
          >
            Delete
          </button>
        </div>
      </div>

      <div className="finding-card__body">
        <h4 className="finding-card__title">{finding.title}</h4>
        {finding.description && (
          <p className="finding-card__description">{finding.description}</p>
        )}
        {finding.remediation && (
          <div className="finding-card__remediation">
            <strong>How to fix:</strong> {finding.remediation}
          </div>
        )}

        <div className="finding-card__meta">
          {finding.owner && (
            <>
              <span>Owner: {finding.owner}</span>
              <span className="finding-card__meta-dot">·</span>
            </>
          )}
          {finding.created_by && (
            <>
              <span>{finding.created_by}</span>
              <span className="finding-card__meta-dot">·</span>
            </>
          )}
          <span>{finding.created_at?.slice(0, 10)}</span>
        </div>

        {error && (
          <div style={{ marginTop: "0.5rem" }}>
            <div className="banner error" style={{ marginBottom: 0 }}>
              {error}
            </div>
          </div>
        )}
      </div>

      <div className="finding-card__actions-section">
        <button
          className="finding-card__actions-toggle"
          onClick={() => setExpanded(!expanded)}
        >
          <span className="finding-card__actions-toggle-arrow">
            {expanded ? "▼" : "▶"}
          </span>
          <span>
            Actions
            <span className="finding-card__actions-toggle-count">
              {" "}({actions.length})
            </span>
            {openCount > 0 && (
              <span className="finding-card__actions-toggle-badge">
                {" "}· {openCount} open
              </span>
            )}
          </span>
        </button>

        {expanded && (
          <div className="finding-card__actions-list">
          {loadingActions ? (
            <p className="finding-card__actions-empty">Loading...</p>
          ) : (
            <>
              {actions.length === 0 && !showAddForm && (
                <p className="finding-card__actions-empty">
                  No corrective actions.
                </p>
              )}

              {actions.map((a) => (
                <div key={a.id} className="finding-action-item">
                  <input
                    type="checkbox"
                    checked={a.status === "completed"}
                    onChange={() => handleToggleAction(a)}
                  />
                  <div className="finding-action-title-wrap">
                    <span
                      className={`finding-action-title${a.status === "completed" ? " finding-action-title--done" : ""}`}
                    >
                      {a.title}
                    </span>
                    {a.description && (
                      <span className="finding-action-desc">{a.description}</span>
                    )}
                  </div>
                  {a.owner && (
                    <span className="finding-action-owner">{a.owner}</span>
                  )}
                  {a.target_date && (
                    <span className="finding-action-date">
                      {a.target_date.slice(0, 10)}
                    </span>
                  )}
                  <button
                    className="btn btn-sm btn-ghost"
                    style={{ color: "var(--danger)", fontSize: "0.8rem", flexShrink: 0 }}
                    onClick={() => handleDeleteAction(a.id)}
                  >
                    ✕
                  </button>
                </div>
              ))}

              {showAddForm ? (
                <div className="finding-card__add-form">
                  <input
                    placeholder="Action title"
                    value={actionForm.title}
                    onChange={(e) =>
                      setActionForm((f) => ({ ...f, title: e.target.value }))
                    }
                  />
                  <input
                    placeholder="Owner (optional)"
                    value={actionForm.owner}
                    onChange={(e) =>
                      setActionForm((f) => ({ ...f, owner: e.target.value }))
                    }
                  />
                  <div className="finding-card__add-buttons">
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={handleCreateAction}
                      disabled={savingAction || !actionForm.title.trim()}
                    >
                      {savingAction ? "Creating..." : "Add"}
                    </button>
                    <button
                      className="btn btn-sm btn-ghost"
                      onClick={() => {
                        setShowAddForm(false);
                        setActionForm({ title: "", description: "", owner: "" });
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  className="btn btn-sm btn-ghost"
                  style={{ marginTop: "0.25rem", fontSize: "0.82rem" }}
                  onClick={() => setShowAddForm(true)}
                >
                  + Add Corrective Action
                </button>
              )}
            </>
          )}
        </div>
      )}
      </div>
    </div>
  );
}
