import { useEffect, useState } from "react";
import { reviewsApi } from "../api";
import type { ReviewItem } from "../types";
import { REVIEW_TYPE_LABELS } from "../types";
import { FilterBar, FilterButtons } from "@shared/filter-bar";

function statusBadge(status: string) {
  const m: Record<string, string> = {
    pending: "badge-muted",
    in_progress: "badge-info",
    completed: "badge-success",
    overdue: "badge-danger",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace(/_/g, " ")}</span>;
}

function defaultFrameworkId(): string {
  const path = typeof window !== "undefined" ? window.location.pathname : "";
  const match = path.match(/^\/(cmmc|soc2|aigov|iso27001)/);
  const map: Record<string, string> = { cmmc: "CMMC", soc2: "SOC2", aigov: "AI Gov", iso27001: "ISO 27001" };
  return map[match?.[1] || ""] || "SOC2";
}

export default function ReviewsList() {
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    title: "",
    type: "",
    frequency: "",
    scheduled_date: "",
    framework_id: defaultFrameworkId(),
    description: "",
  });

  const load = () => {
    setLoading(true);
    reviewsApi.list(filter ? { type: filter } : undefined)
      .then((d) => setReviews(d.reviews || []))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      await reviewsApi.create(form);
      setShowCreate(false);
      setForm({ title: "", type: "", frequency: "", scheduled_date: "", framework_id: defaultFrameworkId(), description: "" });
      load();
    } finally { setCreating(false); }
  };

  const handleComplete = async (r: ReviewItem) => {
    try {
      await reviewsApi.update(r.id, { status: "completed", completed_date: new Date().toISOString().slice(0, 10) });
      load();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this review?")) return;
    try { await reviewsApi.delete(id); load(); } catch { /* ignore */ }
  };

  const overdue = reviews.filter((r) => r.status === "overdue" || (r.scheduled_date && r.scheduled_date < new Date().toISOString().slice(0, 10) && r.status !== "completed"));

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Reviews</h2>
          <p className="muted">{reviews.length} reviews · {overdue.length} overdue</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "+ New Review"}
        </button>
      </div>

      {showCreate && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <form onSubmit={handleCreate}>
            <div className="form-grid">
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Title *</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g., Q2 2026 Access Review" />
              </div>
              <div>
                <label className="muted" style={{ fontSize: 11 }}>Type</label>
                <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="">— Select —</option>
                  {Object.entries(REVIEW_TYPE_LABELS).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="muted" style={{ fontSize: 11 }}>Frequency</label>
                <select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
                  <option value="">— Select —</option>
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                  <option value="annual">Annual</option>
                  <option value="one_time">One-time</option>
                </select>
              </div>
              <div>
                <label className="muted" style={{ fontSize: 11 }}>Scheduled Date</label>
                <input type="date" value={form.scheduled_date} onChange={(e) => setForm({ ...form, scheduled_date: e.target.value })} />
              </div>
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Description</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Scope and objectives" />
              </div>
            </div>
            <button className="btn btn-primary" style={{ marginTop: 12 }} disabled={creating}>
              {creating ? "Creating..." : "Create Review"}
            </button>
          </form>
        </div>
      )}

      <FilterBar>
        <FilterButtons
          items={[
            { key: "", label: "All" },
            ...Object.entries(REVIEW_TYPE_LABELS).map(([k, v]) => ({ key: k, label: v })),
          ]}
          active={filter}
          onChange={(k) => setFilter(filter === k ? "" : k)}
        />
        <span className="filter-count">{reviews.length} review{reviews.length !== 1 ? "s" : ""}</span>
      </FilterBar>

      {loading ? (
        <p className="muted">Loading...</p>
      ) : reviews.length === 0 ? (
        <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No reviews yet.</p></div></div>
      ) : (
        <div className="panel">
          <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Title</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Type</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Frequency</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Scheduled</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Status</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((r) => (
                  <tr key={r.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td style={{ padding: "0.65rem 0.5rem", fontWeight: 500 }}>{r.title}</td>
                    <td style={{ padding: "0.65rem 0.5rem" }}>
                      <span className="badge badge-muted">{REVIEW_TYPE_LABELS[r.type] || r.type}</span>
                    </td>
                    <td style={{ padding: "0.65rem 0.5rem", fontSize: "0.8rem", color: "var(--muted)" }}>{r.frequency || "—"}</td>
                    <td style={{ padding: "0.65rem 0.5rem", fontSize: "0.8rem" }}>{r.scheduled_date?.slice(0, 10) || "—"}</td>
                    <td style={{ padding: "0.65rem 0.5rem" }}>{statusBadge(r.status)}</td>
                    <td style={{ padding: "0.65rem 0.5rem" }}>
                      <div style={{ display: "flex", gap: 4 }}>
                        {r.status !== "completed" && (
                          <button className="btn btn-sm btn-ghost" style={{ fontSize: 11 }} onClick={() => handleComplete(r)}>Complete</button>
                        )}
                        <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)", fontSize: 11 }} onClick={() => handleDelete(r.id)}>Del</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
