import { useEffect, useState } from "react";
import { TabbedPage } from "@shared/tabbed-page";
import RiskDashboard from "@shared/risk-register/pages/RiskDashboard";
import { FileText, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

const API = "/api/ai-governance";

function FriaTab() {
  const [frias, setFrias] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API}/frias`)
      .then((r) => r.json())
      .then((d) => setFrias(d.frias || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading...</p>;

  return (
    <div>
      <button className="btn btn-primary btn-sm" onClick={() => navigate("/aigov/frias/new")} style={{ marginBottom: 16 }}>
        <Plus size={14} /> New FRIA
      </button>
      {frias.length === 0 ? (
        <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>
          No FRIA records yet. Create a Fundamental Rights Impact Assessment for high-risk AI systems.
        </p>
      ) : (
        <div className="panel" style={{ padding: 0 }}>
          {frias.map((f: any) => (
            <div key={f.id} style={{ display: "flex", gap: 8, padding: "10px 12px", borderBottom: "1px solid var(--border-subtle)", alignItems: "center", cursor: "pointer" }} onClick={() => navigate(`/aigov/frias/${f.id}`)}>
              <FileText size={14} style={{ color: "var(--primary)", flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <strong>{f.title || f.system_name || "FRIA"}</strong>
                <div className="muted" style={{ fontSize: 11 }}>{f.system_name ? `System: ${f.system_name}` : ""}{f.created_at ? ` · ${f.created_at.slice(0, 10)}` : ""}</div>
              </div>
              <span className={`badge ${f.status === "approved" ? "badge-success" : f.status === "draft" ? "badge-muted" : "badge-warning"}`}>{f.status || "draft"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function RisksPage() {
  return (
    <TabbedPage
      title="Risk Register"
      tabs={[
        { id: "risks", label: "Risk Register", content: <RiskDashboard /> },
        { id: "fria", label: "FRIA", content: <FriaTab /> },
      ]}
    />
  );
}

export { RiskDashboard as RisksListPage };
