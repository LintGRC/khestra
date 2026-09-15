import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authFetchJson } from "./authFetch";
import { frameworkDetailBase } from "@shared/apiPrefix";

const CORE_API = "/api/core";

type Incident = { id: string; title: string; severity: string; status: string; created_at: string; description?: string };

const severityColors: Record<string, string> = {
  critical: "var(--danger)", high: "var(--danger)", medium: "var(--warning)", low: "var(--info)",
};

const statusColors: Record<string, string> = {
  triage: "var(--danger)", investigation: "var(--warning)", containment: "var(--warning)",
  root_cause_analysis: "var(--info)", remediation: "var(--accent)", closed: "var(--success)",
};

export default function GlobalIncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    Promise.all([
      authFetchJson<{ incidents?: Incident[] }>(`${CORE_API}/incidents`)
        .then((d) => d.incidents || [])
        .catch(() => [] as Incident[]),
      authFetchJson(`${CORE_API}/incidents/stats`).catch(() => ({})),
    ]).then(([inc, st]) => {
      setIncidents(inc);
      setStats(st);
    });
  }, []);

  const open = stats?.open ?? stats?.by_status?.open ?? "—";

  return (
    <div>
      <div className="page-intro">
        <h1 className="page-intro-title">Incidents</h1>
      </div>
      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">Total incidents</div>
          <div className="stat-value">{incidents.length}</div>
          <div className="muted" style={{ fontSize: "0.75rem", marginTop: "0.15rem" }}>
            {open !== "—" ? `${open} open` : "—"}
          </div>
        </div>
      </div>
      <div className="panel-stack">
        <div className="panel">
          <div className="panel-header">
            <strong>All incidents</strong>
            <div className="panel-header-meta">
              <span className="muted">{incidents.length} incidents</span>
              <Link to={`${frameworkDetailBase("incident-new")}/incidents/new`} className="btn btn-primary btn-xs" style={{ fontSize: 11, textDecoration: "none" }}>Report</Link>
            </div>
          </div>
          <div>
            {incidents.length === 0 ? (
              <p className="muted" style={{ padding: "1rem", margin: 0 }}>No incidents.</p>
            ) : (
              incidents.slice(0, 15).map((inc) => (
                <Link
                  key={inc.id}
                  to={`${frameworkDetailBase("incidents")}/incidents/${inc.id}`}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "0.75rem 1rem", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", color: "inherit", fontSize: "0.875rem" }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, marginBottom: 2 }}>{inc.title}</div>
                    <div className="muted" style={{ fontSize: "0.75rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {inc.description || "No description"}
                      {inc.created_at ? ` · ${inc.created_at.slice(0, 10)}` : ""}
                    </div>
                  </div>
                  <span className="badge" style={{ borderColor: severityColors[inc.severity?.toLowerCase()] || "var(--muted)", color: severityColors[inc.severity?.toLowerCase()] || "var(--muted)", fontWeight: 600, fontSize: 10, flexShrink: 0 }}>
                    {inc.severity || "—"}
                  </span>
                  <span className="badge" style={{ borderColor: statusColors[inc.status?.toLowerCase()] || "var(--muted)", color: statusColors[inc.status?.toLowerCase()] || "var(--muted)", fontWeight: 600, fontSize: 10, flexShrink: 0 }}>
                    {inc.status?.replace(/_/g, " ") || "—"}
                  </span>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
