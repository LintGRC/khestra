import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { Shield, Plus, FileText, CheckCircle, AlertTriangle, Clock } from "lucide-react";

const API = "/api/ai-governance";

export function FriaLandingPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/frias/dashboard`).then((r) => r.json()).then(setStats).catch(() => {});
  }, []);

  return (
    <>
      <div className="aigov-page-header">
        <h1>Fundamental Rights Impact Assessments</h1>
        <p>Assess and document the impact of AI systems on fundamental rights under EU AI Act Article 27</p>
      </div>

      {stats && (
        <div className="stats" style={{ marginBottom: "1.5rem" }}>
          {[
            { label: "Total FRIAs", value: stats.total, color: "var(--primary)" },
            { label: "Approved", value: stats.by_status?.approved || 0, color: "var(--success)" },
            { label: "Submitted", value: stats.by_status?.submitted || 0, color: "var(--warning)" },
            { label: "Draft", value: stats.by_status?.draft || 0, color: "var(--muted)" },
          ].map((s) => (
            <NavLink key={s.label} to={`/aigov/frias/list?status=${s.label.toLowerCase()}`} className="stat-card" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
              <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </NavLink>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 12, marginBottom: "1.5rem" }}>
        <NavLink to="/aigov/frias/new" className="btn btn-primary"><Plus size={14} /> New FRIA</NavLink>
        <NavLink to="/aigov/frias/list" className="btn btn-secondary"><FileText size={14} /> View All</NavLink>
      </div>

      <div className="aigov-feature-grid">
        {[
          { icon: Shield, title: "System Assessment", desc: "Document the AI system, its purpose, deployer, and developer entity" },
          { icon: CheckCircle, title: "Rights Impact", desc: "Identify affected fundamental rights and assess severity of impact" },
          { icon: AlertTriangle, title: "Risk Heatmap", desc: "Visualize likelihood vs impact across all risk assessments" },
          { icon: Clock, title: "Review & Approve", desc: "Submit, approve, or reject with full audit trail" },
        ].map((f) => (
          <div key={f.title} className="aigov-feature-card">
            <div className="aigov-feature-icon"><f.icon /></div>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </>
  );
}
