import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type MyWork } from "../api";
import PageIntro from "../components/PageIntro";

export default function MyWorkPage() {
  const [data, setData] = useState<MyWork | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.myWork()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-stack"><p className="muted">Loading your work…</p></div>;
  if (!data) return <div className="page-stack"><p className="muted">Could not load work items.</p></div>;

  const sections = [
    {
      title: "Overdue",
      count: data.overdue_count,
      color: "var(--danger)",
      items: data.overdue,
      empty: "No overdue controls",
    },
    {
      title: "Due Soon (7 days)",
      count: data.due_soon_count,
      color: "var(--warning)",
      items: data.due_soon,
      empty: "Nothing due soon",
    },
    {
      title: "Needs Evidence Review",
      count: data.needs_review_count,
      color: "var(--info-soft)",
      items: data.needs_review,
      empty: "No evidence pending review",
    },
    {
      title: "Missing Evidence (MET controls)",
      count: data.missing_evidence_count,
      color: "var(--warning)",
      items: data.missing_evidence,
      empty: "All MET controls have evidence",
    },
  ];

  return (
    <div className="page-stack">
      <PageIntro title="My Work" />

      {/* Stats */}
      <div className="dashboard-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))" }}>
        <div className="stat-card">
          <span className="stat-label">Assigned</span>
          <span className="stat-value">{data.assigned_count}</span>
          <span className="stat-sub">controls</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Overdue</span>
          <span className="stat-value" style={{ color: data.overdue_count > 0 ? "var(--danger)" : undefined }}>{data.overdue_count}</span>
          <span className="stat-sub">controls</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Due soon</span>
          <span className="stat-value" style={{ color: data.due_soon_count > 0 ? "var(--warning)" : undefined }}>{data.due_soon_count}</span>
          <span className="stat-sub">controls</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">To review</span>
          <span className="stat-value">{data.needs_review_count}</span>
          <span className="stat-sub">evidence items</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Requests</span>
          <span className="stat-value">{data.pending_requests_count}</span>
          <span className="stat-sub">pending</span>
        </div>
      </div>

      {/* Sections */}
      {sections.map((sec) => (
        <section className="panel" key={sec.title}>
          <div className="panel-header">
            <h3>{sec.title}</h3>
            {sec.count > 0 && <span className="badge" style={{ background: sec.color, color: "#fff" }}>{sec.count}</span>}
          </div>
          <div className="panel-body">
            {sec.items.length === 0 ? (
              <p className="muted" style={{ margin: 0 }}>{sec.empty}</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Control</th>
                    <th>Category</th>
                    <th>Name</th>
                    <th>Status</th>
                    {"days_left" in (sec.items[0] || {}) && <th>Days left</th>}
                    {"days_overdue" in (sec.items[0] || {}) && <th>Overdue by</th>}
                    {"filename" in (sec.items[0] || {}) && <th>File</th>}
                    {"upload_date" in (sec.items[0] || {}) && <th>Uploaded</th>}
                  </tr>
                </thead>
                <tbody>
                  {sec.items.map((item: any, i: number) => (
                    <tr key={i}>
                      <td>
                        <Link to={`/criteria/${item.control_id}`} className="btn-link">{item.control_id}</Link>
                      </td>
                      <td>{item.category}</td>
                      <td>{item.name || item.filename || ""}</td>
                      <td>{item.status || ""}</td>
                      {"days_left" in item && <td>{item.days_left}d</td>}
                      {"days_overdue" in item && <td style={{ color: "var(--danger)" }}>{item.days_overdue}d</td>}
                      {"upload_date" in item && <td>{item.upload_date}</td>}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>
      ))}

      {/* Pending Requests */}
      {data.pending_requests.length > 0 && (
        <section className="panel">
          <div className="panel-header">
            <h3>Pending Evidence Requests</h3>
            <span className="badge badge-warning">{data.pending_requests_count}</span>
          </div>
          <div className="panel-body">
            <table className="data-table">
              <thead>
                <tr><th>Control</th><th>Title</th><th>Due</th><th>Created</th></tr>
              </thead>
              <tbody>
                {data.pending_requests.map((req) => (
                  <tr key={req.request_id}>
                    <td><Link to={`/criteria/${req.control_id}`} className="btn-link">{req.control_id}</Link></td>
                    <td>{req.title}</td>
                    <td>{req.due_date || "—"}</td>
                    <td>{req.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Pending Approval */}
      {data.pending_approval.length > 0 && (
        <section className="panel">
          <div className="panel-header">
            <h3>Exceptions Pending Approval</h3>
            <span className="badge badge-warning">{data.pending_approval_count}</span>
          </div>
          <div className="panel-body">
            <table className="data-table">
              <thead>
                <tr><th>Control</th><th>Description</th><th>Risk</th></tr>
              </thead>
              <tbody>
                {data.pending_approval.map((exc) => (
                  <tr key={exc.id}>
                    <td><Link to={`/criteria/${exc.control_id}`} className="btn-link">{exc.control_id}</Link></td>
                    <td>{exc.description?.slice(0, 60) || "—"}</td>
                    <td><span className={`badge badge-${exc.risk_level === "critical" ? "danger" : exc.risk_level === "high" ? "warning" : "muted"}`}>{exc.risk_level}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
