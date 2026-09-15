import { useEffect, useState } from "react";
import { authFetch } from "../api";

type ConnectorInfo = {
  id: string;
  name: string;
  description: string;
  required_fields: string[];
  configured: boolean;
};

export default function IntegrationsPage() {
  const [connectors, setConnectors] = useState<ConnectorInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authFetch("/api/collectors")
      .then((r) => r.json())
      .then((d) => setConnectors(d.connectors || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading integrations…</p>;

  return (
    <div>
      <h1>Integrations</h1>
      <p className="muted">Connect your tools to automatically collect evidence for AI Governance controls.</p>
      <div className="card-grid" style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
        {connectors.map((c) => (
          <div key={c.id} className="panel" style={{ padding: "1rem" }}>
            <h3>{c.name}</h3>
            <p className="muted" style={{ fontSize: "0.85rem" }}>{c.description}</p>
            <p style={{ marginTop: "0.5rem" }}>
              <span className={`badge ${c.configured ? "badge-ok" : "badge-missing"}`}>
                {c.configured ? "Configured" : "Not configured"}
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
