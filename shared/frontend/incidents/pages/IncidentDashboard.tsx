import { useEffect, useState } from "react";
import { api } from "../api";

const SEV_COLORS: Record<string, string> = {
  critical: "#dc2626", high: "#ea580c", medium: "#ca8a04", low: "#6b7280",
};
const SEV_LABELS: Record<string, string> = {
  critical: "Critical", high: "High", medium: "Medium", low: "Low",
};
const STATUS_LABELS: Record<string, string> = {
  triage: "Triage", investigation: "Investigation", containment: "Containment",
  root_cause_analysis: "RCA", remediation: "Remediation", closed: "Closed",
};
const FM_LABELS: Record<string, string> = {
  prompt_injection: "Prompt Injection", model_poisoning: "Model Poisoning",
  model_drift: "Model Drift", data_exfiltration: "Data Exfiltration",
  systemic_bias: "Systemic Bias", security_breach: "Security Breach",
  agent_failure: "Agent Failure", other: "Other",
};

export default function IncidentDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.stats().then(setStats).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading dashboard...</p>;
  if (!stats) return <p className="muted">Failed to load stats.</p>;

  const severityTotal = (Object.values(stats.by_severity || {}) as number[]).reduce((a, b) => a + b, 0);
  const statusTotal = (Object.values(stats.by_status || {}) as number[]).reduce((a, b) => a + b, 0);
  const fmTotal = (Object.values(stats.by_failure_mode || {}) as number[]).reduce((a, b) => a + b, 0);

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Incident Dashboard</h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginBottom: 24 }}>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{stats.total || 0}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Total Incidents</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--danger)" }}>{stats.open || 0}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Open</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: stats.overdue_regulatory > 0 ? "var(--danger)" : "var(--success)" }}>{stats.overdue_regulatory || 0}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Overdue Regulatory</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{(stats.by_severity?.critical || 0)}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Critical</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {severityTotal > 0 && (
          <div className="panel">
            <div className="panel-header"><strong>By Severity</strong></div>
            <div className="panel-body">
              {Object.entries(stats.by_severity || {}).map(([k, v]: [string, any]) => {
                const pct = Math.round((Number(v) / severityTotal) * 100);
                return (
                  <div key={k} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, color: SEV_COLORS[k] }}>{SEV_LABELS[k] || k}</span>
                      <span>{v} ({pct}%)</span>
                    </div>
                    <div style={{ height: 8, background: "var(--border)", borderRadius: 4, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${pct}%`, background: SEV_COLORS[k] || "#6b7280", borderRadius: 4 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {statusTotal > 0 && (
          <div className="panel">
            <div className="panel-header"><strong>By Status</strong></div>
            <div className="panel-body">
              {Object.entries(stats.by_status || {}).map(([k, v]: [string, any]) => {
                const pct = Math.round((Number(v) / statusTotal) * 100);
                return (
                  <div key={k} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: 4 }}>
                      <span>{STATUS_LABELS[k] || k}</span>
                      <span>{v} ({pct}%)</span>
                    </div>
                    <div style={{ height: 8, background: "var(--border)", borderRadius: 4, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${pct}%`, background: k === "closed" ? "var(--success)" : k === "containment" ? "var(--danger)" : "var(--warning)", borderRadius: 4 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {fmTotal > 0 && (
        <div className="panel" style={{ marginBottom: 24 }}>
          <div className="panel-header"><strong>By Failure Mode</strong></div>
          <div className="panel-body">
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr className="muted" style={{ fontSize: "0.8rem", textAlign: "left" }}>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Failure Mode</th>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Count</th>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>%</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats.by_failure_mode || {}).map(([k, v]: [string, any]) => (
                  <tr key={k} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "8px 12px" }}>{FM_LABELS[k] || k}</td>
                    <td style={{ padding: "8px 12px" }}>{v}</td>
                    <td style={{ padding: "8px 12px" }}>{Math.round((Number(v) / fmTotal) * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {stats.total === 0 && (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No incidents yet. Report an incident to see dashboard stats.</p>
          </div>
        </div>
      )}
    </div>
  );
}
