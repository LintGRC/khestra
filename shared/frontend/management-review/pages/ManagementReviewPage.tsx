import { useCallback, useEffect, useState } from "react";
import { managementReviewApi } from "../api";
import type {
  ActionItem,
  Attendee,
  ManagementReview,
  ReviewInput,
  ReviewOutput,
} from "../types";
import { OUTPUT_CATEGORY_LABELS } from "../types";

function statusBadge(status: string) {
  const m: Record<string, string> = {
    scheduled: "badge-muted",
    in_progress: "badge-info",
    completed: "badge-success",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace(/_/g, " ")}</span>;
}

interface Draft {
  title: string;
  date: string;
  attendees: Attendee[];
  inputs: ReviewInput[];
  outputs: ReviewOutput[];
  action_items: ActionItem[];
  minutes: string;
}

const EMPTY_DRAFT: Draft = {
  title: "",
  date: "",
  attendees: [],
  inputs: [],
  outputs: [],
  action_items: [],
  minutes: "",
};

export default function ManagementReviewPage() {
  const [records, setRecords] = useState<ManagementReview[]>([]);
  const [stats, setStats] = useState<{ total: number; by_status: Record<string, number>; open_actions_latest: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [draft, setDraft] = useState<Draft>({ ...EMPTY_DRAFT });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    managementReviewApi.list()
      .then((d) => setRecords(d.records || []))
      .catch(() => setError("Failed to load management reviews."))
      .finally(() => setLoading(false));
    managementReviewApi.stats().then(setStats).catch(() => undefined);
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = async () => {
    const { inputs } = await managementReviewApi.inputs();
    setDraft({
      ...EMPTY_DRAFT,
      inputs: inputs.map((i) => ({ key: i.key, label: i.label, reviewed: false, note: "" })),
    });
    setShowCreate(true);
  };

  const save = async () => {
    if (!draft.title.trim()) {
      setError("Title is required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await managementReviewApi.create({ ...draft, status: "scheduled" });
      setShowCreate(false);
      setDraft({ ...EMPTY_DRAFT });
      load();
    } catch {
      setError("Failed to create management review.");
    } finally {
      setSaving(false);
    }
  };

  const transition = async (r: ManagementReview, to: string) => {
    try {
      await managementReviewApi.update(r.id, { status: to });
      load();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this management review?")) return;
    try { await managementReviewApi.remove(id); load(); } catch { /* ignore */ }
  };

  const setInput = (i: number, patch: Partial<ReviewInput>) => {
    const next = [...draft.inputs];
    next[i] = { ...next[i], ...patch };
    setDraft({ ...draft, inputs: next });
  };

  const setOutput = (i: number, patch: Partial<ReviewOutput>) => {
    const next = [...draft.outputs];
    next[i] = { ...next[i], ...patch };
    setDraft({ ...draft, outputs: next });
  };

  const setAction = (i: number, patch: Partial<ActionItem>) => {
    const next = [...draft.action_items];
    next[i] = { ...next[i], ...patch };
    setDraft({ ...draft, action_items: next });
  };

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Management Review</h2>
          <p className="muted">
            ISO/IEC 27001 clause 9.3 — top management reviews the ISMS at planned intervals to ensure continuing
            suitability, adequacy and effectiveness
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => (showCreate ? setShowCreate(false) : openCreate())}>
          {showCreate ? "Cancel" : "+ New Review"}
        </button>
      </div>

      {stats && (
        <div className="metric-grid" style={{ marginBottom: 16 }}>
          <div className="metric-card"><div className="metric-value">{stats.total}</div><div className="metric-label">Total reviews</div></div>
          <div className="metric-card"><div className="metric-value">{stats.by_status?.completed ?? 0}</div><div className="metric-label">Completed</div></div>
          <div className="metric-card"><div className="metric-value">{stats.by_status?.in_progress ?? 0}</div><div className="metric-label">In progress</div></div>
          <div className="metric-card"><div className="metric-value">{stats.open_actions_latest}</div><div className="metric-label">Open actions (latest)</div></div>
        </div>
      )}

      {error && <div className="banner danger" style={{ marginBottom: 12 }}>{error}</div>}

      {showCreate && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <h4 style={{ margin: "0 0 12px" }}>New Management Review</h4>
          <div className="form-grid">
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>Title *</label>
              <input value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} placeholder="e.g., Q3 2026 Management Review" />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Date</label>
              <input type="date" value={draft.date} onChange={(e) => setDraft({ ...draft, date: e.target.value })} />
            </div>
            <div>
              <label className="muted" style={{ fontSize: 11 }}>Attendees (name — role, one per line)</label>
              <textarea
                value={draft.attendees.map((a) => (a.role ? `${a.name} — ${a.role}` : a.name)).join("\n")}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    attendees: e.target.value.split("\n").map((line) => {
                      const [name, ...rest] = line.split("—").map((s) => s.trim());
                      return { name: name || "", role: rest.join("—").trim() };
                    }).filter((a) => a.name),
                  })
                }
                style={{ width: "100%", minHeight: 56 }}
              />
            </div>
          </div>

          <h5 style={{ margin: "14px 0 6px" }}>Review inputs (9.3.2)</h5>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {draft.inputs.map((inp, i) => (
              <label key={inp.key} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
                <input type="checkbox" checked={inp.reviewed} onChange={(e) => setInput(i, { reviewed: e.target.checked })} />
                <span style={{ flex: 1 }}>{inp.label}</span>
                {inp.reviewed && (
                  <input
                    value={inp.note || ""}
                    onChange={(e) => setInput(i, { note: e.target.value })}
                    placeholder="Note"
                    style={{ flex: 1, maxWidth: 260 }}
                  />
                )}
              </label>
            ))}
          </div>

          <h5 style={{ margin: "14px 0 6px" }}>Outputs & decisions (9.3.3)</h5>
          {draft.outputs.map((o, i) => (
            <div key={i} style={{ display: "flex", gap: 6, marginBottom: 6 }}>
              <input value={o.decision} onChange={(e) => setOutput(i, { decision: e.target.value })} placeholder="Decision" style={{ flex: 2 }} />
              <select value={o.category} onChange={(e) => setOutput(i, { category: e.target.value })} style={{ flex: 1 }}>
                {Object.entries(OUTPUT_CATEGORY_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
              <input value={o.owner} onChange={(e) => setOutput(i, { owner: e.target.value })} placeholder="Owner" style={{ flex: 1 }} />
              <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => setDraft({ ...draft, outputs: draft.outputs.filter((_, j) => j !== i) })}>✕</button>
            </div>
          ))}
          <button className="btn btn-sm btn-ghost" onClick={() => setDraft({ ...draft, outputs: [...draft.outputs, { decision: "", category: "other", owner: "", target_date: "" }] })}>
            + Add output
          </button>

          <h5 style={{ margin: "14px 0 6px" }}>Action items</h5>
          {draft.action_items.map((a, i) => (
            <div key={i} style={{ display: "flex", gap: 6, marginBottom: 6 }}>
              <input value={a.description} onChange={(e) => setAction(i, { description: e.target.value })} placeholder="Action" style={{ flex: 2 }} />
              <input value={a.owner} onChange={(e) => setAction(i, { owner: e.target.value })} placeholder="Owner" style={{ flex: 1 }} />
              <input type="date" value={a.target_date} onChange={(e) => setAction(i, { target_date: e.target.value })} style={{ flex: 1 }} />
              <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => setDraft({ ...draft, action_items: draft.action_items.filter((_, j) => j !== i) })}>✕</button>
            </div>
          ))}
          <button className="btn btn-sm btn-ghost" onClick={() => setDraft({ ...draft, action_items: [...draft.action_items, { description: "", owner: "", target_date: "", status: "open" }] })}>
            + Add action
          </button>

          <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
            <button className="btn btn-primary" onClick={save} disabled={saving}>{saving ? "Saving..." : "Create Review"}</button>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <p className="muted">Loading...</p>
      ) : records.length === 0 ? (
        <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No management reviews yet. Clause 9.3 requires periodic top-management review of the ISMS.</p></div></div>
      ) : (
        <div className="panel">
          <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Title</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Date</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Attendees</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Inputs reviewed</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Outputs</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Status</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => {
                  const reviewed = (r.inputs || []).filter((i) => i.reviewed).length;
                  return (
                    <tr key={r.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                      <td style={{ padding: "0.65rem 0.5rem", fontWeight: 500 }}>{r.title}</td>
                      <td style={{ padding: "0.65rem 0.5rem" }}>{r.date?.slice(0, 10) || "—"}</td>
                      <td style={{ padding: "0.65rem 0.5rem", fontSize: 12 }}>{(r.attendees || []).length}</td>
                      <td style={{ padding: "0.65rem 0.5rem", fontSize: 12 }}>{reviewed}/{r.inputs?.length ?? 0}</td>
                      <td style={{ padding: "0.65rem 0.5rem", fontSize: 12 }}>{(r.outputs || []).length}</td>
                      <td style={{ padding: "0.65rem 0.5rem" }}>{statusBadge(r.status)}</td>
                      <td style={{ padding: "0.65rem 0.5rem" }}>
                        <div style={{ display: "flex", gap: 4 }}>
                          {r.status === "scheduled" && (
                            <button className="btn btn-sm btn-ghost" style={{ fontSize: 11 }} onClick={() => transition(r, "in_progress")}>Start</button>
                          )}
                          {r.status === "in_progress" && (
                            <button className="btn btn-sm btn-ghost" style={{ fontSize: 11 }} onClick={() => transition(r, "completed")}>Complete</button>
                          )}
                          <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)", fontSize: 11 }} onClick={() => handleDelete(r.id)}>Del</button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
