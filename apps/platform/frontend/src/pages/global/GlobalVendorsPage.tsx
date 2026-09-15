import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authFetchJson } from "./authFetch";
import { frameworkDetailBase } from "@shared/apiPrefix";

const CORE_API = "/api/core";

type Vendor = { id: string; name: string; status: string; risk_score: number | null; product_service?: string; contact_name?: string; contact_email?: string };

const statusColors: Record<string, string> = {
  active: "var(--success)", pending: "var(--warning)", approved: "var(--success)",
  rejected: "var(--danger)", under_review: "var(--warning)", inactive: "var(--muted)",
};

function riskBadge(score: number | null) {
  if (score == null) return <span style={{ fontSize: 10, color: "var(--muted)" }}>—</span>;
  const color = score >= 80 ? "var(--success)" : score >= 50 ? "var(--warning)" : "var(--danger)";
  const label = score >= 80 ? "Low" : score >= 50 ? "Med" : "High";
  return <span className="badge" style={{ borderColor: color, color, fontWeight: 600, fontSize: 10 }}>{label} ({score})</span>;
}

export default function GlobalVendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);

  useEffect(() => {
    authFetchJson<{ vendors?: Vendor[] }>(`${CORE_API}/vendors`)
      .then((d) => setVendors(d.vendors || []))
      .catch(() => setVendors([]));
  }, []);

  return (
    <div>
      <div className="page-intro">
        <h1 className="page-intro-title">Vendors</h1>
      </div>
      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">Total vendors</div>
          <div className="stat-value">{vendors.length}</div>
        </div>
      </div>
      <div className="panel-stack">
        <div className="panel">
          <div className="panel-header">
            <strong>All vendors</strong>
            <div className="panel-header-meta">
              <span className="muted">{vendors.length} vendors</span>
              <Link to={`${frameworkDetailBase("vendor-new")}/vendors/new`} className="btn btn-primary btn-xs" style={{ fontSize: 11, textDecoration: "none" }}>+ New</Link>
            </div>
          </div>
          <div>
            {vendors.length === 0 ? (
              <p className="muted" style={{ padding: "1rem", margin: 0 }}>No vendors.</p>
            ) : (
              vendors.slice(0, 15).map((v) => (
                <Link
                  key={v.id}
                  to={`${frameworkDetailBase("vendors")}/vendors/${v.id}`}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "0.75rem 1rem", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", color: "inherit", fontSize: "0.875rem" }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, marginBottom: 2 }}>{v.name}</div>
                    <div className="muted" style={{ fontSize: "0.75rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {v.product_service || v.contact_name || "No description"}
                      {v.contact_email ? ` · ${v.contact_email}` : ""}
                    </div>
                  </div>
                  {riskBadge(v.risk_score)}
                  <span className="badge" style={{ borderColor: statusColors[v.status] || "var(--muted)", color: statusColors[v.status] || "var(--muted)", fontWeight: 600, fontSize: 10, flexShrink: 0 }}>
                    {v.status?.replace(/_/g, " ") || "pending"}
                  </span>
                </Link>
              ))
            )}
          </div>
          {vendors.length > 15 && (
            <div style={{ padding: "0.65rem 1rem", fontSize: "0.8125rem", borderTop: "1px solid var(--border-subtle)" }}>
              <Link to={`${frameworkDetailBase("vendors")}/vendors`} style={{ color: "var(--primary)" }}>View all {vendors.length} vendors →</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
