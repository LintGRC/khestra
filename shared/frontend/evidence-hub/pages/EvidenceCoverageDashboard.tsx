import { useEffect, useState } from "react";
import { apiUrl } from "@shared/apiPrefix";

type Stats = {
  total_evidence: number;
  total_mappings: number;
  total_file_size: number;
  by_review_status: Record<string, number>;
  by_framework: Record<string, { evidence_count: number; control_count: number; mapping_count: number }>;
  recent_uploads: { id: string; name: string; filename: string; uploaded_at: string; uploaded_by: string }[];
};

function fmtSize(bytes: number) {
  if (!bytes) return "0 B";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const FW_LABELS: Record<string, string> = { SOC2: "SOC 2", AIGov: "AI Gov", CMMC: "CMMC", "ISO 27001": "ISO 27001" };

export default function EvidenceCoverageDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(apiUrl("/api/evidence-hub/stats"))
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading coverage data...</p>;
  if (!stats) return <p className="muted">Failed to load coverage data.</p>;

  const fwNames = Object.keys(stats.by_framework || {});
  const reviewTotal = Object.values(stats.by_review_status || {}).reduce((a: number, b: number) => a + b, 0);

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Evidence Coverage</h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 24 }}>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{stats.total_evidence}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Evidence Files</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{stats.total_mappings}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Control Mappings</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{fmtSize(stats.total_file_size)}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Total Storage</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{fwNames.length}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Frameworks</div>
        </div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <a className="btn btn-secondary btn-sm" href={apiUrl("/api/evidence-hub/export")} download>
          Export All ZIP
        </a>
      </div>

      {fwNames.length > 0 && (
        <div className="panel" style={{ marginBottom: 24 }}>
          <div className="panel-header"><strong>By Framework</strong></div>
          <div className="panel-body">
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr className="muted" style={{ fontSize: "0.8rem", textAlign: "left" }}>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Framework</th>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Evidence</th>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Controls</th>
                  <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Mappings</th>
                </tr>
              </thead>
              <tbody>
                {fwNames.map((fw) => {
                  const f = stats.by_framework![fw];
                  return (
                    <tr key={fw} style={{ borderBottom: "1px solid var(--border)" }}>
                      <td style={{ padding: "8px 12px", fontWeight: 600 }}>{FW_LABELS[fw] || fw}</td>
                      <td style={{ padding: "8px 12px" }}>{f.evidence_count}</td>
                      <td style={{ padding: "8px 12px" }}>{f.control_count}</td>
                      <td style={{ padding: "8px 12px" }}>{f.mapping_count}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {reviewTotal > 0 && (
          <div className="panel">
            <div className="panel-header"><strong>Review Status</strong></div>
            <div className="panel-body">
              {["pending", "approved", "rejected"].map((s) => {
                const count = stats.by_review_status?.[s] || 0;
                if (!count) return null;
                const pct = Math.round((count / reviewTotal) * 100);
                const colors: Record<string, string> = { pending: "var(--warning)", approved: "var(--success)", rejected: "var(--danger)" };
                return (
                  <div key={s} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: 4 }}>
                      <span style={{ textTransform: "capitalize" }}>{s}</span>
                      <span>{count} ({pct}%)</span>
                    </div>
                    <div style={{ height: 8, background: "var(--border)", borderRadius: 4, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${pct}%`, background: colors[s], borderRadius: 4 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {stats.recent_uploads?.length > 0 && (
          <div className="panel">
            <div className="panel-header"><strong>Recent Uploads</strong></div>
            <div className="panel-body">
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {stats.recent_uploads.map((u) => (
                  <li key={u.id} style={{ fontSize: "0.8rem", padding: "4px 0", borderBottom: "1px solid var(--border)" }}>
                    <strong>{u.name}</strong>
                    <span className="muted" style={{ marginLeft: 8 }}>{u.filename}</span>
                    <br />
                    <span className="muted">{u.uploaded_by} &middot; {u.uploaded_at?.slice(0, 10)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
