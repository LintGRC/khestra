import { useEffect, useState } from "react";
import { useNavigate, NavLink, useParams } from "react-router-dom";
import { ArrowLeft, Shield } from "lucide-react";

const API = "/api/ai-governance";

const QUESTIONS = [
  { key: "affects_people", label: "Makes decisions affecting people?" },
  { key: "legal_advice", label: "Generates legal advice or binding documents?" },
  { key: "healthcare", label: "Used in healthcare decisions?" },
  { key: "employment", label: "Used in employment decisions?" },
  { key: "financial", label: "Used in financial decisions?" },
  { key: "public_facing", label: "Public-facing application?" },
  { key: "biometric", label: "Uses biometric data?" },
  { key: "personal_info", label: "Processes personal information?" },
  { key: "autonomous", label: "Takes autonomous actions?" },
  { key: "critical_infrastructure", label: "Used in critical infrastructure?" },
  { key: "education", label: "Used in education access?" },
  { key: "law_enforcement", label: "Used in law enforcement?" },
  { key: "migration", label: "Used in migration or border control?" },
  { key: "admin_justice", label: "Used in administration of justice?" },
  { key: "election_influence", label: "Could influence elections?" },
  { key: "human_approval", label: "Human approval always required? (reduces risk)" },
  { key: "prohibited_use", label: "Prohibited use case (social scoring, etc.)?" },
  { key: "general_purpose", label: "General-purpose AI model?" },
];

export function SystemsClassifyPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [system, setSystem] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, boolean>>({});
  const [profile, setProfile] = useState("provider");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/systems/${id}`).then((r) => r.json()).then((d) => {
      setSystem(d.system);
      setAnswers(d.system.risk_assessment?.answers || {});
      setProfile(d.system.ai_profile || "provider");
    });
  }, [id]);

  async function handleClassify() {
    setSaving(true);
    await fetch(`${API}/systems/${id}/classify`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...answers, ai_profile: profile }) });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system);
    setSaving(false);
    navigate(`/aigov/systems/${id}`);
  }

  if (!system) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  return (
    <div style={{ maxWidth: 600, margin: "0 auto" }}>
      <NavLink to={`/aigov/systems/${id}`} style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--muted)", textDecoration: "none", marginBottom: 12 }}>
        <ArrowLeft size={12} /> Back to {system.name}
      </NavLink>
      <div className="aigov-page-header">
        <h1 style={{ display: "flex", alignItems: "center", gap: 8 }}><Shield size={18} /> Risk Classification</h1>
        <p>Answer these questions to determine the EU AI Act risk tier for <strong>{system.name}</strong>. The role you pick changes which articles appear on the conformity work queue.</p>
      </div>
      <div className="panel" style={{ padding: 14, marginBottom: 12 }}>
        <label className="muted" style={{ fontSize: 12, display: "block", marginBottom: 6 }}>Organization role for this system</label>
        <select value={profile} onChange={(e) => setProfile(e.target.value)} style={{ fontSize: 13, padding: "6px 10px" }}>
          <option value="provider">Provider</option>
          <option value="deployer">Deployer</option>
          <option value="gpai">GPAI provider</option>
          <option value="agentic">Agentic application</option>
        </select>
      </div>
      <div className="panel-stack" style={{ gap: 8 }}>
        {QUESTIONS.map((q) => (
          <label key={q.key} className="panel" style={{ display: "flex", alignItems: "start", gap: 8, padding: "12px 14px", cursor: "pointer" }}>
            <input type="checkbox" checked={answers[q.key] || false} onChange={() => setAnswers({ ...answers, [q.key]: !answers[q.key] })} style={{ marginTop: 2 }} />
            <span style={{ fontSize: 13 }}>{q.label}</span>
          </label>
        ))}
      </div>
      <div className="btn-row" style={{ marginTop: 16 }}>
        <button onClick={handleClassify} disabled={saving} className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }}>
          <Shield size={16} /> {saving ? "Classifying..." : "Classify Model"}
        </button>
      </div>
    </div>
  );
}
