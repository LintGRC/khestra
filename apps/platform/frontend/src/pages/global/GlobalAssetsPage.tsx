import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authFetchJson } from "./authFetch";
import { frameworkDetailBase } from "@shared/apiPrefix";

const CORE_API = "/api/core";

type Asset = { id: string; name: string; type: string; owner: string; environment: string; description?: string; created_at?: string };

const typeColors: Record<string, string> = {
  server: "var(--info)", workstation: "var(--primary)", network: "var(--success)",
  cloud: "var(--accent)", application: "var(--warning)", database: "var(--danger)",
  endpoint: "var(--muted)", iot: "var(--info)",
};

export default function GlobalAssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);

  useEffect(() => {
    authFetchJson<{ assets?: Asset[] }>(`${CORE_API}/assets`)
      .then((d) => setAssets(d.assets || []))
      .catch(() => setAssets([]));
  }, []);

  return (
    <div>
      <div className="page-intro">
        <h1 className="page-intro-title">Assets</h1>
      </div>
      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">Total assets</div>
          <div className="stat-value">{assets.length}</div>
        </div>
      </div>
      <div className="panel-stack">
        <div className="panel">
          <div className="panel-header">
            <strong>All assets</strong>
            <div className="panel-header-meta">
              <span className="muted">{assets.length} assets</span>
              <Link to={`${frameworkDetailBase("assets")}/assets`} className="btn btn-primary btn-xs" style={{ fontSize: 11, textDecoration: "none" }}>View All</Link>
            </div>
          </div>
          <div>
            {assets.length === 0 ? (
              <p className="muted" style={{ padding: "1rem", margin: 0 }}>No assets.</p>
            ) : (
              assets.slice(0, 15).map((a) => (
                <div key={a.id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "0.75rem 1rem", borderBottom: "1px solid var(--border-subtle)", fontSize: "0.875rem" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, marginBottom: 2 }}>{a.name}</div>
                    <div className="muted" style={{ fontSize: "0.75rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {a.description || "No description"}
                      {a.owner ? ` · Owner: ${a.owner}` : ""}
                    </div>
                  </div>
                  <span className="badge" style={{ borderColor: typeColors[a.type?.toLowerCase()] || "var(--muted)", color: typeColors[a.type?.toLowerCase()] || "var(--muted)", fontWeight: 600, fontSize: 10, flexShrink: 0 }}>
                    {a.type || "uncategorized"}
                  </span>
                  {a.environment && (
                    <span className="badge badge-muted" style={{ fontSize: 10, flexShrink: 0 }}>{a.environment}</span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
