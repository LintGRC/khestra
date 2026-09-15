import { useEffect, useState } from "react";
import { NavLink, useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, FileText, Trash2, Users, AlertTriangle, Upload, FolderOpen } from "lucide-react";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";
import { apiUrl } from "@shared/apiPrefix";

const API = "/api/ai-governance";

export function SystemsDetailPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [system, setSystem] = useState<any>(null);
  const [tab, setTab] = useState<"overview" | "timeline" | "changes" | "versions" | "literacy" | "model-card" | "compliance" | "evidence">("overview");
  const [fwTab, setFwTab] = useState(() => activeFrameworks[0] || "eu_ai_act");
  const [deployEnv, setDeployEnv] = useState("production");
  const [deployBy, setDeployBy] = useState("");
  const [evidenceLabel, setEvidenceLabel] = useState("");
  const [uploading, setUploading] = useState(false);
  const [tagInput, setTagInput] = useState("");
  const [cfKey, setCfKey] = useState("");
  const [cfValue, setCfValue] = useState("");

  useEffect(() => {
    if (!id) return;
    fetch(`${API}/systems/${id}`)
      .then((r) => r.json())
      .then((d) => setSystem(d.system));
  }, [id]);

  useEffect(() => {
    if (!activeFrameworks.includes(fwTab as any)) {
      setFwTab(activeFrameworks[0] || "eu_ai_act");
    }
  }, [activeFrameworks]);

  if (!system) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  const tierColors: Record<string, [string, string]> = {
    unacceptable: ["var(--danger-soft)", "var(--danger)"], high: ["var(--danger-soft)", "var(--danger)"],
    limited: ["var(--warning-soft)", "var(--warning)"], minimal: ["var(--success-soft)", "var(--success)"],
    gpa: ["var(--info-soft)", "var(--info)"], unclassified: ["var(--surface)", "var(--muted)"],
  };
  const [tierBg, tierColor] = tierColors[system.risk_classification] || ["var(--surface)", "var(--muted)"];

  async function handleAction(action: string) {
    await fetch(`${API}/systems/${id}/${action}`, { method: "POST" });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system);
  }
  async function handleDelete() {
    if (!confirm("Delete this system?")) return;
    await fetch(`${API}/systems/${id}`, { method: "DELETE" });
    navigate("/aigov/systems");
  }
  async function handleExportPDF() { window.open(`${API}/systems/${id}/export`, "_blank"); }
  async function handleAddTag() {
    if (!tagInput.trim()) return;
    const tags = [...(system.tags || []), tagInput.trim()];
    await fetch(`${API}/systems/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tags }) });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system); setTagInput("");
  }
  async function handleRemoveTag(tag: string) {
    const tags = (system.tags || []).filter((t: string) => t !== tag);
    await fetch(`${API}/systems/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tags }) });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system);
  }
  async function handleAddCf() {
    if (!cfKey.trim()) return;
    const cf = { ...(system.custom_fields || {}), [cfKey.trim()]: cfValue.trim() };
    await fetch(`${API}/systems/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ custom_fields: cf }) });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system); setCfKey(""); setCfValue("");
  }
  async function handleRemoveCf(key: string) {
    const cf = { ...(system.custom_fields || {}) }; delete cf[key];
    await fetch(`${API}/systems/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ custom_fields: cf }) });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system);
  }
  async function handleDeploy() {
    await fetch(`${API}/systems/${id}/deploy`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ environment: deployEnv, deployed_by: deployBy }) });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system); setDeployBy("");
  }
  async function handleEvidenceUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file); form.append("label", evidenceLabel);
    await fetch(`${API}/systems/${id}/evidence`, { method: "POST", body: form });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system); setEvidenceLabel(""); setUploading(false); e.target.value = "";
  }
  async function handleEvidenceDelete(eid: string) {
    await fetch(`${API}/systems/${id}/evidence/${eid}`, { method: "DELETE" });
    const d = await fetch(`${API}/systems/${id}`).then((r) => r.json());
    setSystem(d.system);
  }

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <NavLink to="/aigov/systems" style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--muted)", textDecoration: "none", marginBottom: 8 }}>
            <ArrowLeft size={12} /> Back to Systems
          </NavLink>
          <h1 style={{ fontSize: 20, fontWeight: 600, margin: "0 0 4px" }}>{system.name}</h1>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span className="badge" style={{ background: tierBg, color: tierColor, fontWeight: 600 }}>{system.risk_classification}</span>
            <span className="muted" style={{ fontSize: 12 }}>{system.deployment_status} · {system.environment || ""}</span>
            <span className="muted" style={{ fontSize: 12 }}>{system.approval_status || "draft"}</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 8, flexWrap: "wrap" }}>
            {(system.tags || []).map((t: string) => (
              <span key={t} className="badge" style={{ background: "var(--primary-soft)", color: "var(--primary)", display: "inline-flex", alignItems: "center", gap: 3 }}>
                {t}
                <button onClick={() => handleRemoveTag(t)} className="icon-btn" style={{ fontSize: 12, lineHeight: 1, padding: 0, width: "auto", height: "auto" }}>&times;</button>
              </span>
            ))}
            <input placeholder="+tag" value={tagInput} onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddTag()}
              style={{ width: 60, padding: "2px 6px" }} />
          </div>
        </div>
        <div className="controls-toolbar-options" style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={handleExportPDF}><FileText size={14} /> Model Card</button>
          <NavLink to={`/aigov/systems/${system.id}/edit`} className="btn btn-secondary btn-sm"><FileText size={14} /> Edit</NavLink>
          <NavLink to={`/aigov/systems/${system.id}/conformity`} className="btn btn-secondary btn-sm"><FileText size={14} /> Conformity</NavLink>
          <NavLink to={`/aigov/systems/${system.id}/dossier`} className="btn btn-secondary btn-sm"><FolderOpen size={14} /> Dossier</NavLink>
          <button className="btn btn-secondary btn-sm" onClick={handleDelete} style={{ color: "var(--danger)" }}><Trash2 size={14} /> Delete</button>
        </div>
      </div>

      <div className="aigov-tabs">
        {(["overview", "timeline", "changes", "versions", "literacy", "model-card", "compliance", "evidence"] as const).map((t) => (
          <button key={t} className={`aigov-tab${tab === t ? " aigov-tab--active" : ""}`} onClick={() => setTab(t)}>
            {t === "model-card" ? "Model Card" : t === "literacy" ? "AI Literacy" : t === "compliance" ? "Compliance" : t === "evidence" ? "Evidence Gaps" : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="panel-stack" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Details</strong></h3>
            {field("Description", system.description)}
            {field("Purpose", system.purpose)}
            {field("Foundation Model", system.foundation_model)}
            {field("Vendor", system.vendor)}
            {field("Actor Role", system.is_fine_tuned ? "Provider (substantially modified — Art. 25)" : system.foundation_model ? "Deployer (vendor model as-is)" : "")}
          </div>
          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Ownership</strong></h3>
            {field("Owner", system.owner)}
            {field("Business Owner", system.business_owner)}
            {field("Technical Owner", system.technical_owner)}
            {field("Risk Owner", system.risk_owner)}
          </div>
          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Risk</strong></h3>
            {field("Risk Tier", system.risk_classification)}
            {field("Score", system.risk_assessment?.score)}
            {field("Classified", system.risk_assessment?.classified_at?.slice(0, 10))}
            {system.risk_assessment?.flags?.length > 0 && (
              <div style={{ marginTop: 8 }}>
                {system.risk_assessment.flags.map((f: string) => (
                  <div key={f} style={{ fontSize: 11, color: "var(--danger)" }}><AlertTriangle size={10} style={{ display: "inline" }} /> {f}</div>
                ))}
              </div>
            )}
            <NavLink to={`/aigov/systems/${system.id}/classify`} className="btn btn-primary btn-sm" style={{ marginTop: 8, display: "inline-flex" }}>Edit Classification</NavLink>
          </div>
          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Transparency &amp; Data</strong></h3>
            {field("Public-facing", system.is_public_facing ? "Yes" : "No")}
            {field("Transparency URL", system.transparency_notice_url)}
            {field("Input Sources", system.input_data_sources)}
            {field("Processing", system.processing_location)}
            {field("Output Dest", system.output_destinations)}
          </div>
          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Approval</strong></h3>
            {field("Status", system.approval_status)}
            {system.reviewed_by && field("Reviewed By", system.reviewed_by)}
            {system.reviewed_at && field("Reviewed", system.reviewed_at.slice(0, 10))}
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              {system.approval_status === "draft" && <button onClick={() => handleAction("submit")} className="btn btn-primary btn-sm">Submit</button>}
              {system.approval_status === "submitted" && (<><button onClick={() => handleAction("approve")} className="btn btn-primary btn-sm" style={{ background: "var(--success)" }}>Approve</button><button onClick={() => handleAction("reject")} className="btn btn-primary btn-sm" style={{ background: "var(--danger)" }}>Reject</button></>)}
            </div>
          </div>

          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Governance Score</strong></h3>
            {(() => {
              const checks = [
                { label: "Name & Description", ok: !!(system.name && system.description) },
                { label: "Owner assigned", ok: !!system.owner },
                { label: "Purpose defined", ok: !!system.purpose },
                { label: "Risk classified", ok: system.risk_assessment?.score !== undefined },
                { label: "Evidence attached", ok: (system.evidence?.length || 0) > 0 },
                { label: "Business owner", ok: !!system.business_owner },
                { label: "Technical owner", ok: !!system.technical_owner },
                { label: "Risk owner", ok: !!system.risk_owner },
                { label: "Deployment set", ok: !!system.deployment_status },
              ];
              const score = Math.round(checks.filter((c) => c.ok).length / checks.length * 100);
              const color = score >= 80 ? "var(--success)" : score >= 50 ? "var(--warning)" : "var(--danger)";
              return (
                <>
                  <div style={{ textAlign: "center", marginBottom: 12 }}>
                    <p className="aigov-risk-score" style={{ color }}>{score}%</p>
                    <p className="muted" style={{ fontSize: 11 }}>{checks.filter((c) => c.ok).length}/{checks.length} fields</p>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                    {checks.map((c) => (
                      <div key={c.label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
                        <span style={{ color: c.ok ? "var(--success)" : "var(--danger)", fontSize: 14 }}>{c.ok ? "✓" : "✗"}</span>
                        <span style={{ color: c.ok ? "var(--text)" : "var(--muted)" }}>{c.label}</span>
                      </div>
                    ))}
                  </div>
                </>
              );
            })()}
          </div>

          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Deploy</strong></h3>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <select value={deployEnv} onChange={(e) => setDeployEnv(e.target.value)} style={{ flex: 1 }}>
                <option value="development">Development</option><option value="staging">Staging</option><option value="production">Production</option>
              </select>
              <input placeholder="By" value={deployBy} onChange={(e) => setDeployBy(e.target.value)} style={{ flex: 1 }} />
              <button onClick={handleDeploy} className="btn btn-primary btn-sm" style={{ flexShrink: 0 }}>Deploy</button>
            </div>
            {system.deployments?.length > 0 && (
              <div style={{ maxHeight: 120, overflowY: "auto" }}>
                {system.deployments.slice().reverse().map((d: any) => (
                  <div key={d.id} className="muted" style={{ fontSize: 11, padding: "2px 0" }}>
                    {d.timestamp?.slice(0, 10)} → {d.environment} {d.deployed_by ? `by ${d.deployed_by}` : ""}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Evidence ({system.evidence?.length || 0})</strong>
            </h3>
            {system.evidence?.length > 0 && system.evidence.map((e: any) => (
              <div key={e.id} style={{ fontSize: 12, padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>{e.label} <span className="muted">({e.filename})</span></span>
                  <button className="icon-btn icon-btn--danger" onClick={() => handleEvidenceDelete(e.id)}><Trash2 size={12} /></button>
                </div>
                {/\.(png|jpg|jpeg|gif|webp|svg)$/i.test(e.filename) && (
                  <img src={`${API}/systems/${id}/evidence/${e.id}`} alt={e.label} style={{ maxHeight: 120, marginTop: 4, borderRadius: 4, border: "1px solid var(--border)", objectFit: "contain", maxWidth: "100%" }} />
                )}
              </div>
            ))}
            {(!system.evidence || system.evidence.length === 0) && <p className="muted" style={{ fontSize: 12 }}>No evidence.</p>}
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <input placeholder="Label" value={evidenceLabel} onChange={(e) => setEvidenceLabel(e.target.value)} style={{ flex: 1 }} />
              <button className="btn btn-secondary btn-sm" onClick={() => document.getElementById("evup")?.click()} disabled={uploading}><Upload size={14} /></button>
              <input id="evup" type="file" hidden onChange={handleEvidenceUpload} />
            </div>
          </div>

          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Custom Fields</strong></h3>
            {system.custom_fields && Object.keys(system.custom_fields).length > 0 ? (
              Object.entries(system.custom_fields).map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, padding: "4px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                  <span><strong>{k}:</strong> {String(v)}</span>
                  <button className="icon-btn icon-btn--danger" onClick={() => handleRemoveCf(k)}><Trash2 size={12} /></button>
                </div>
              ))
            ) : <p className="muted" style={{ fontSize: 12 }}>No custom fields.</p>}
            <div style={{ display: "flex", gap: 4, marginTop: 8 }}>
              <input placeholder="Key" value={cfKey} onChange={(e) => setCfKey(e.target.value)} style={{ flex: 1 }} />
              <input placeholder="Value" value={cfValue} onChange={(e) => setCfValue(e.target.value)} style={{ flex: 1 }} />
              <button onClick={handleAddCf} className="btn btn-secondary btn-sm">Add</button>
            </div>
          </div>

          <div className="panel" style={{ padding: 16, gridColumn: "span 2" }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Framework Compliance</strong></h3>
            <FrameworkStatusBar sid={id!} API={API} onAssess={(fw) => { setFwTab(fw as any); setTab("compliance"); }} />
          </div>

          <div className="panel" style={{ padding: 16 }}>
            <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Framework Mapping</strong></h3>
            {(() => {
              const checks = [
                { label: "ISO 42001", ok: true, detail: "System inventory" },
                { label: "EU AI Act Art. 5", ok: system.risk_classification !== "unacceptable", detail: "Not prohibited" },
                { label: "EU AI Act Art. 6", ok: system.risk_classification !== "unclassified", detail: "Risk classified" },
                { label: "EU AI Act Art. 11", ok: !!(system.description && system.purpose), detail: "Documentation" },
                { label: "EU AI Act Art. 14", ok: !!system.business_owner, detail: "Human oversight" },
                { label: "NIST GOV 1.1", ok: !!system.owner, detail: "Accountability" },
                { label: "NIST MAP 2.4", ok: !!(system.input_data_sources || system.data_inputs?.length), detail: "Data mapping" },
                { label: "NIST MANAGE 4.1", ok: system.deployment_status === "production", detail: "Change control" },
              ];
              return (
                <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                  {checks.map((c) => (
                    <div key={c.label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
                      <span style={{ color: c.ok ? "var(--success)" : "var(--danger)", fontSize: 12 }}>{c.ok ? "✓" : "✗"}</span>
                      <span style={{ color: c.ok ? "var(--text)" : "var(--muted)" }}>{c.label}</span>
                      <span className="muted" style={{ marginLeft: "auto" }}>{c.detail}</span>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {tab === "timeline" && <TimelineTab history={system.history || []} />}
      {tab === "changes" && <ChangesTab sid={id!} API={API} />}
      {tab === "versions" && <VersionsTab sid={id!} API={API} />}
      {tab === "literacy" && <LiteracyTab sid={id!} API={API} logs={system.ai_literacy_log || []} />}
      {tab === "model-card" && (
        <div className="panel-stack">
          {modelCardPanel("Performance Metrics", system.performance_metrics)}
          {modelCardPanel("Known Limitations", system.known_limitations)}
          {modelCardPanel("Out-of-Scope Uses", system.out_of_scope_uses)}
          {modelCardPanel("Human Oversight", system.human_oversight)}
          {modelCardPanel("Bias & Fairness", system.bias_fairness_notes)}
          {modelCardPanel("Training Data", system.training_data)}
          {!system.performance_metrics && !system.known_limitations && !system.out_of_scope_uses && !system.human_oversight && !system.bias_fairness_notes && !system.training_data && (
            <div className="panel" style={{ padding: 16 }}>
              <p className="muted" style={{ fontSize: 12, textAlign: "center" }}>No model card data yet. <NavLink to={`/aigov/systems/${system.id}/edit`}>Add it here.</NavLink></p>
            </div>
          )}
        </div>
      )}
      {tab === "compliance" && (
        <div>
          <div className="aigov-tabs" style={{ marginBottom: 12 }}>
            {AI_GOV_FRAMEWORKS.filter(f => activeFrameworks.includes(f.key)).map((f) => (
              <button key={f.key} className={`aigov-tab${fwTab === f.key ? " aigov-tab--active" : ""}`} onClick={() => setFwTab(f.key)}>
                {f.label}
              </button>
            ))}
        </div>
        <UnifiedComplianceTab system={system} sid={id!} API={API} framework={fwTab} />
      </div>
      )}
      {tab === "evidence" && <EvidenceGapsTab sid={id!} system={system} />}
    </>
  );
}

function field(label: string, value: any) {
  if (!value && value !== 0) return null;
  return <div style={{ display: "flex", fontSize: 12, marginBottom: 4 }}><span className="muted" style={{ width: 100, flexShrink: 0 }}>{label}</span><span style={{ color: "var(--text)" }}>{String(value)}</span></div>;
}

function modelCardPanel(label: string, value: any) {
  return (
    <div className="panel" style={{ padding: 16 }}>
      <h3 className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>{label}</strong></h3>
      {value ? <p style={{ fontSize: 12, whiteSpace: "pre-wrap", margin: 0 }}>{value}</p> : <p className="muted" style={{ fontSize: 12 }}>Not specified.</p>}
    </div>
  );
}

function FrameworkStatusBar({ sid, API, onAssess }: { sid: string; API: string; onAssess: (fw: string) => void }) {
  const [statuses, setStatuses] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled(
      ["eu_ai_act", "nist_ai_rmf", "iso_42001"].map(fw =>
        fetch(`${API}/systems/${sid}/conformity?framework=${fw}`)
          .then(r => r.json())
          .then(d => ({ fw, conformity: d.conformity }))
      )
    ).then(results => {
      const map: Record<string, any> = {};
      results.forEach(r => {
        if (r.status === "fulfilled" && r.value) {
          const arts = r.value.conformity?.articles || {};
          const total = Object.keys(arts).length;
          const done = Object.values(arts).filter((a: any) => a?.status && a.status !== "missing").length;
          map[r.value.fw] = { assessed: total > 0, pct: total ? Math.round((done / total) * 100) : 0, total, done };
        }
      });
      setStatuses(map);
      setLoading(false);
    });
  }, [sid]);

  const fws = [
    { key: "eu_ai_act", label: "EU AI Act", color: "var(--primary)", icon: "EU" },
    { key: "nist_ai_rmf", label: "NIST AI RMF", color: "#2563eb", icon: "NI" },
    { key: "iso_42001", label: "ISO 42001", color: "#7c3aed", icon: "IS" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {fws.map(fw => {
        const st = statuses[fw.key];
        const assessed = st?.assessed;
        return (
          <div key={fw.key} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--surface)", cursor: "pointer" }} onClick={() => onAssess(fw.key)}>
            <span style={{ width: 28, height: 28, borderRadius: 6, background: fw.color + "18", color: fw.color, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 10, flexShrink: 0 }}>{fw.icon}</span>
            <span style={{ fontWeight: 600, fontSize: "0.8rem", flex: 1 }}>{fw.label}</span>
            {loading ? (
              <span className="muted" style={{ fontSize: "0.7rem" }}>...</span>
            ) : assessed ? (
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 50, background: "var(--border)", borderRadius: 3, height: 5, overflow: "hidden" }}>
                  <div style={{ width: `${st.pct}%`, height: "100%", borderRadius: 3, background: st.pct >= 80 ? "var(--success)" : st.pct >= 30 ? "var(--warning)" : "var(--danger)" }} />
                </div>
                <span style={{ fontSize: "0.7rem", color: st.pct >= 80 ? "var(--success)" : st.pct >= 30 ? "var(--warning)" : "var(--danger)", fontWeight: 600 }}>{st.done}/{st.total}</span>
              </div>
            ) : (
              <span className="muted" style={{ fontSize: "0.7rem" }}>Not started</span>
            )}
            <span style={{ fontSize: 14, color: "var(--muted)" }}>&rsaquo;</span>
          </div>
        );
      })}
    </div>
  );
}

function VersionsTab({ sid, API }: { sid: string; API: string }) {
  const [versions, setVersions] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ version: "", release_date: "", change_log: "", status: "development", created_by: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch(`${API}/systems/${sid}/versions`).then(r => r.json()).then(d => setVersions(d.versions || [])).catch(() => {});
  }, [sid]);

  async function handleCreate() {
    if (!form.version.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API}/systems/${sid}/versions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      const d = await fetch(`${API}/systems/${sid}/versions`).then(r => r.json());
      setVersions(d.versions || []);
      setShowForm(false);
      setForm({ version: "", release_date: "", change_log: "", status: "development", created_by: "" });
    } catch { /* */ } finally { setSaving(false); }
  }

  async function handleDelete(vid: string) {
    if (!confirm("Delete this version?")) return;
    await fetch(`${API}/systems/${sid}/versions/${vid}`, { method: "DELETE" });
    const d = await fetch(`${API}/systems/${sid}/versions`).then(r => r.json());
    setVersions(d.versions || []);
  }

  const statusColors: Record<string, string> = {
    development: "var(--muted)", staging: "var(--warning)", production: "var(--success)", deprecated: "var(--danger)",
  };

  return (
    <div>
      <div className="panel" style={{ padding: 16, marginBottom: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <strong>Version History</strong>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "+ New Version"}</button>
        </div>
        {showForm && (
          <div className="form-grid" style={{ marginBottom: 12 }}>
            <div><label className="muted" style={{ fontSize: 11 }}>Version *</label><input value={form.version} onChange={e => setForm({ ...form, version: e.target.value })} placeholder="2.0.0" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Release date</label><input type="date" value={form.release_date} onChange={e => setForm({ ...form, release_date: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Status</label><select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}><option value="development">Development</option><option value="staging">Staging</option><option value="production">Production</option><option value="deprecated">Deprecated</option></select></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Created by</label><input value={form.created_by} onChange={e => setForm({ ...form, created_by: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Change log</label><textarea rows={2} value={form.change_log} onChange={e => setForm({ ...form, change_log: e.target.value })} placeholder="What changed in this version?" /></div>
            <div><button className="btn btn-primary" onClick={handleCreate} disabled={saving || !form.version.trim()}>{saving ? "Creating..." : "Create Version"}</button></div>
          </div>
        )}
        {versions.length === 0 ? (
          <p className="muted" style={{ fontSize: 13 }}>No versions recorded yet.</p>
        ) : (
          <div style={{ position: "relative", paddingLeft: 20 }}>
            <div style={{ position: "absolute", left: 8, top: 4, bottom: 4, width: 2, background: "var(--border)" }} />
            {versions.map((v, i) => (
              <div key={v.id} style={{ position: "relative", paddingBottom: i < versions.length - 1 ? 16 : 0 }}>
                <div style={{ position: "absolute", left: -15, top: 4, width: 12, height: 12, borderRadius: "50%", background: statusColors[v.status] || "var(--muted)", border: "2px solid var(--bg)" }} />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <strong style={{ fontSize: 14 }}>{v.version}</strong>
                    <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 6px", borderRadius: "var(--radius)", background: "var(--surface)", color: statusColors[v.status] || "var(--muted)", marginLeft: 8 }}>{v.status}</span>
                    {v.release_date && <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>{v.release_date}</span>}
                    {v.created_by && <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>by {v.created_by}</span>}
                  </div>
                  <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(v.id)}>✕</button>
                </div>
                {v.change_log && <p style={{ fontSize: 12, margin: "4px 0 0", color: "var(--muted)" }}>{v.change_log}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineTab({ history }: { history: any[] }) {
  return (
    <div className="panel" style={{ padding: 16 }}>
      <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Lifecycle Timeline</strong></div>
      <div style={{ position: "relative", paddingLeft: 16 }}>
        <div style={{ position: "absolute", left: 6, top: 0, bottom: 0, width: 2, background: "var(--border)" }} />
        {[...history].reverse().map((h, i) => (
          <div key={i} style={{ position: "relative", paddingBottom: i < history.length - 1 ? "16px" : "0" }}>
            <div style={{
              position: "absolute", left: -19, top: 3, width: 10, height: 10, borderRadius: "50%",
              background: h.action?.includes("approved") ? "var(--success)" : h.action?.includes("rejected") ? "var(--danger)" : h.action?.includes("submitted") ? "var(--warning)" : "var(--primary)",
            }} />
            <div className="muted" style={{ fontSize: 11 }}>{h.timestamp?.slice(0, 16).replace("T", " ") || ""}</div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>{h.detail || h.action || "Event"}</div>
          </div>
        ))}
        {history.length === 0 && <p className="muted" style={{ fontSize: 13 }}>No history recorded yet.</p>}
      </div>
    </div>
  );
}

function ChangesTab({ sid, API }: { sid: string; API: string }) {
  const [changes, setChanges] = useState<any[]>([]);
  const [form, setForm] = useState({ change_type: "prompt", description: "", reason: "", requested_by: "", risk_review: "low" });

  useEffect(() => {
    fetch(`${API}/systems/${sid}/changes`).then((r) => r.json()).then((d) => setChanges(d.changes || []));
  }, [sid]);

  async function handleCreate() {
    await fetch(`${API}/systems/${sid}/changes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
    const d = await fetch(`${API}/systems/${sid}/changes`).then((r) => r.json());
    setChanges(d.changes || []);
    setForm({ change_type: "prompt", description: "", reason: "", requested_by: "", risk_review: "low" });
  }

  return (
    <div className="panel-stack">
      <div className="panel" style={{ padding: 16 }}>
        <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Request Change</strong></div>
        <div className="form-grid">
          <div><label className="muted" style={{ fontSize: 11 }}>Type</label><select value={form.change_type} onChange={(e) => setForm({ ...form, change_type: e.target.value })}><option value="prompt">Prompt</option><option value="model">Model</option><option value="rag">RAG</option><option value="settings">Settings</option><option value="other">Other</option></select></div>
          <div><label className="muted" style={{ fontSize: 11 }}>Requested by</label><input value={form.requested_by} onChange={(e) => setForm({ ...form, requested_by: e.target.value })} /></div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} /></div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Reason</label><textarea value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} rows={2} /></div>
        </div>
        <button onClick={handleCreate} className="btn btn-primary btn-sm" style={{ marginTop: 8 }}>Submit Change</button>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Change History</strong></div>
        {changes.map((c) => (
          <div key={c.id} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 12 }}>
            <div>
              <span style={{ fontWeight: 500 }}>{c.change_type}</span> — {c.description}
              <div className="muted" style={{ fontSize: 11 }}>{c.timestamp?.slice(0, 16).replace("T", " ") || ""} · {c.requested_by}</div>
            </div>
            <span className={`badge ${c.approval_status === "approved" ? "met" : c.approval_status === "rejected" ? "" : "neutral"}`}
              style={c.approval_status === "rejected" ? { background: "var(--danger-soft)", color: "var(--danger)" } : {}}>
              {c.approval_status}
            </span>
          </div>
        ))}
        {changes.length === 0 && <p className="muted" style={{ fontSize: 12 }}>No changes recorded.</p>}
      </div>
    </div>
  );
}

function UnifiedComplianceTab({ system, sid, API, framework }: { system: any; sid: string; API: string; framework: string }) {
  const [articles, setArticles] = useState<any[]>([]);
  const [conformity, setConformity] = useState<any>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [pmsPlan, setPmsPlan] = useState(system.pms_plan || "");
  const [caForm, setCaForm] = useState({ title: "", description: "", source: "conformity_assessment", severity: "medium", related_article: "", root_cause: "", action_plan: "", assigned_to: "", deadline: "" });
  const [caShowForm, setCaShowForm] = useState(false);
  const [caSaving, setCaSaving] = useState(false);
  const [pmsSaving, setPmsSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [caExpanded, setCaExpanded] = useState(false);
  const [objectivesByArticle, setObjectivesByArticle] = useState<Record<string, string[]>>({});

  const isHighRisk = ["high", "unacceptable"].includes(system.risk_classification);
  const isGPAI = system.risk_classification === "gpa";
  const isEU = framework === "eu_ai_act";
  const cl: Record<string, string> = {
    prohibited: "Prohibited Practices", classification: "Classification", requirements: "Core Requirements", provider: "Provider Obligations", deployer: "Deployer Obligations",
    limited: "Transparency", gpai: "GPAI", post_market: "Post-Market",
    govern: "GOVERN", map: "MAP", measure: "MEASURE", manage: "MANAGE",
    context: "Context", leadership: "Leadership", planning: "Planning", support: "Support", operation: "Operation", evaluation: "Evaluation", improvement: "Improvement", annex_a: "Annex A",
  };

  function load() {
    Promise.all([
      fetch(`${API}/systems/${sid}/conformity/articles?framework=${framework}`).then(r => r.json()).then(d => setArticles(d.articles || [])),
      fetch(`${API}/systems/${sid}/conformity?framework=${framework}`).then(r => r.json()).then(d => setConformity(d.conformity)),
      fetch(`${API}/systems/${sid}/corrective-actions`).then(r => r.json()).then(d => setActions(d.actions || [])),
      fetch(`${API}/systems/${sid}/objectives?framework=${framework}`).then(r => r.json()).then(data => {
        const byArticle: Record<string, string[]> = {};
        for (const fwName of Object.keys(data.frameworks || {})) {
          for (const obj of data.frameworks[fwName]) {
            byArticle[obj.article_id] = obj.objectives;
          }
        }
        setObjectivesByArticle(byArticle);
      }),
    ]).finally(() => setLoading(false));
  }

  useEffect(() => { if (sid) load(); }, [sid, framework]);

  if (loading) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  const statusArticles = conformity?.articles || {};
  const totalArts = articles.length;
  const doneArts = Object.values(statusArticles).filter((a: any) => a?.status && a.status !== "missing").length;
  const artPct = totalArts ? Math.round((doneArts / totalArts) * 100) : 0;

  const severityColors: Record<string, string> = {
    critical: "var(--danger)", high: "var(--danger)", medium: "var(--warning)", low: "var(--muted)",
  };
  const caStatusColors: Record<string, string> = {
    open: "var(--danger)", in_progress: "var(--warning)", resolved: "var(--success)", closed: "var(--muted)",
  };
  const sourceLabels: Record<string, string> = {
    conformity_assessment: "Conformity", incident: "Incident", audit: "Audit", monitoring: "Monitoring", other: "Other",
  };

  async function handleCaCreate() {
    if (!caForm.title.trim()) return;
    setCaSaving(true);
    try {
      await fetch(`${API}/systems/${sid}/corrective-actions`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(caForm),
      });
      setCaForm({ title: "", description: "", source: "conformity_assessment", severity: "medium", related_article: "", root_cause: "", action_plan: "", assigned_to: "", deadline: "" });
      setCaShowForm(false);
      await load();
    } catch {}
    setCaSaving(false);
  }

  async function handleCaUpdate(aid: string, updates: any) {
    await fetch(`${API}/corrective-actions/${aid}`, {
      method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(updates),
    });
    await load();
  }

  async function handleCaDelete(aid: string) {
    if (!confirm("Delete this corrective action?")) return;
    await fetch(`${API}/corrective-actions/${aid}`, { method: "DELETE" });
    await load();
  }

  async function handleSavePms() {
    setPmsSaving(true);
    try {
      await fetch(`${API}/systems/${sid}`, {
        method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pms_plan: pmsPlan }),
      });
    } catch {}
    setPmsSaving(false);
  }

  const fwDesc: Record<string, string> = {
    eu_ai_act: "Risk-based regulation \u2014 classify, assess, and monitor high-risk AI systems.",
    nist_ai_rmf: "Govern, map, measure, and manage AI risks across four functions.",
    iso_42001: "AI management system standard with context, planning, support, operations, and evaluation.",
  };

  return (
    <div>
      {/* Framework Guide */}
      <p className="muted" style={{ fontSize: 11, margin: "0 0 12px", lineHeight: 1.4 }}>{fwDesc[framework] || ""}</p>

      {/* Section 1: Conformity Assessment */}
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <strong>Assessment ({doneArts}/{totalArts} controls)</strong>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <span style={{ fontWeight: 700, fontSize: 16, color: artPct >= 80 ? "var(--success)" : artPct >= 30 ? "var(--warning)" : "var(--danger)" }}>{artPct}%</span>
            <NavLink to={`/aigov/systems/${sid}/conformity?framework=${framework}`} className="btn btn-primary btn-sm"><FileText size={14} /> Full Assessment</NavLink>
          </div>
        </div>
        <div className="panel-body" style={{ padding: "0.5rem 1rem 1rem" }}>
          <div style={{ width: "100%", background: "var(--border)", borderRadius: 4, height: 6, overflow: "hidden", marginBottom: 8 }}>
            <div style={{ width: `${artPct}%`, height: "100%", borderRadius: 4, background: artPct >= 80 ? "var(--success)" : artPct >= 30 ? "var(--warning)" : "var(--danger)" }} />
          </div>
          {articles.length === 0 ? (
            <p className="muted" style={{ fontSize: 12 }}>No articles apply to this risk tier.</p>
          ) : (
            (() => {
              const byCat: Record<string, any[]> = {};
              articles.forEach(a => { byCat[a.category] = byCat[a.category] || []; byCat[a.category].push(a); });
              return Object.entries(byCat).map(([cat, arts]) => (
                <div key={cat} style={{ marginBottom: 8 }}>
                  <div style={{ fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em", color: "var(--muted)", marginBottom: 4, padding: "0 4px" }}>{cl[cat] || cat}</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: 4 }}>
                    {arts.map(art => {
                      const s = statusArticles[art.id];
                      const st = s?.status || "missing";
                      const colors: Record<string, string> = { compliant: "var(--success)", partial: "var(--warning)", missing: "var(--danger)", na: "var(--muted)" };
                      const labels: Record<string, string> = { compliant: "C", partial: "P", missing: "M", na: "N/A" };
                      return (
                        <div key={art.id} style={{ fontSize: 11, padding: "3px 4px" }}>
                          <details style={{ cursor: "pointer" }}>
                            <summary style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
                              <span style={{ width: 16, height: 16, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", background: colors[st] + "20", color: colors[st], fontWeight: 700, fontSize: 8, flexShrink: 0 }}>{labels[st]}</span>
                              <span style={{ fontFamily: "monospace", fontWeight: 600, flexShrink: 0 }}>{art.ref}</span>
                              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>{art.title}</span>
                              {objectivesByArticle[art.id] && (() => {
                                const cid = art.control_id || "";
                                const ans = (system?.answers || {})[cid] || {};
                                const done = (ans.obj_examine_done ? 1 : 0) + (ans.obj_interview_done ? 1 : 0) + (ans.obj_test_done ? 1 : 0);
                                const total = objectivesByArticle[art.id].length;
                                return <span style={{ fontSize: 9, flexShrink: 0, color: done === total ? "var(--success)" : "var(--muted)" }}>{done}/{total}</span>;
                              })()}
                            </summary>
                            {objectivesByArticle[art.id] && (
                              <ul style={{ margin: "4px 0 0 0", padding: "0 0 0 16px", listStyle: "none" }}>
                                {objectivesByArticle[art.id].map((obj, i) => (
                                  <li key={i} style={{ marginBottom: 2, lineHeight: 1.4, color: "var(--text-muted)", fontSize: 10 }}>{obj}</li>
                                ))}
                              </ul>
                            )}
                          </details>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ));
            })()
          )}
        </div>
      </div>

      {/* Section 2: Corrective Actions */}
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <strong>Corrective Actions ({actions.length})</strong>
          <button className="btn btn-sm btn-ghost" onClick={() => setCaShowForm(!caShowForm)}>{caShowForm ? "Cancel" : "+ New"}</button>
        </div>
        {caShowForm && (
          <div className="panel-body" style={{ borderBottom: "1px solid var(--border)", padding: "0.75rem 1rem" }}>
            <div className="form-grid" style={{ marginBottom: 8 }}>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Title *</label><input value={caForm.title} onChange={e => setCaForm({ ...caForm, title: e.target.value })} placeholder="Non-conformity found" style={{ fontSize: "0.8rem" }} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Source</label><select value={caForm.source} onChange={e => setCaForm({ ...caForm, source: e.target.value })} style={{ fontSize: "0.8rem" }}>{Object.entries(sourceLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Related Article</label><input value={caForm.related_article} onChange={e => setCaForm({ ...caForm, related_article: e.target.value })} placeholder="Art. 9" style={{ fontSize: "0.8rem" }} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Severity</label><select value={caForm.severity} onChange={e => setCaForm({ ...caForm, severity: e.target.value })} style={{ fontSize: "0.8rem" }}><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option></select></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Assigned To</label><input value={caForm.assigned_to} onChange={e => setCaForm({ ...caForm, assigned_to: e.target.value })} style={{ fontSize: "0.8rem" }} /></div>
              <div><label className="muted" style={{ fontSize: 11 }}>Deadline</label><input type="date" value={caForm.deadline} onChange={e => setCaForm({ ...caForm, deadline: e.target.value })} style={{ fontSize: "0.8rem" }} /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Action Plan</label><textarea rows={2} value={caForm.action_plan} onChange={e => setCaForm({ ...caForm, action_plan: e.target.value })} placeholder="Steps to resolve" style={{ fontSize: "0.8rem" }} /></div>
            </div>
            <button className="btn btn-primary btn-sm" disabled={!caForm.title || caSaving} onClick={handleCaCreate}>{caSaving ? "Creating..." : "Create"}</button>
          </div>
        )}
        <div className="panel-body" style={{ padding: "0.5rem 1rem" }}>
          {actions.length === 0 ? (
            <p className="muted" style={{ fontSize: 11 }}>No open corrective actions.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {actions.slice(0, caExpanded ? actions.length : 5).map(a => (
                <div key={a.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, fontSize: 11, padding: "4px 8px", background: "var(--surface)", borderRadius: 4, border: "1px solid var(--border)" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <span style={{ fontWeight: 500 }}>{a.title}</span>
                    <span className="badge" style={{ background: severityColors[a.severity] + "18", color: severityColors[a.severity], fontWeight: 600, fontSize: 9, marginLeft: 4 }}>{a.severity}</span>
                    <span className="badge" style={{ background: caStatusColors[a.status] + "18", color: caStatusColors[a.status], fontWeight: 600, fontSize: 9, marginLeft: 2 }}>{a.status.replace("_", " ")}</span>
                    {a.related_article && <span className="muted" style={{ marginLeft: 6 }}>{a.related_article}</span>}
                  </div>
                  <div style={{ display: "flex", gap: 2, flexShrink: 0 }}>
                    {a.status === "open" && <button className="btn btn-sm btn-ghost" style={{ fontSize: 9, padding: "1px 6px" }} onClick={() => handleCaUpdate(a.id, { status: "in_progress" })}>Start</button>}
                    {a.status !== "resolved" && a.status !== "closed" && <button className="btn btn-sm btn-ghost" style={{ fontSize: 9, padding: "1px 6px", color: "var(--success)" }} onClick={() => handleCaUpdate(a.id, { status: "resolved", resolution_notes: "Resolved" })}>Resolve</button>}
                    {a.status === "resolved" && <button className="btn btn-sm btn-ghost" style={{ fontSize: 9, padding: "1px 6px" }} onClick={() => handleCaUpdate(a.id, { status: "closed" })}>Close</button>}
                    <button className="icon-btn icon-btn--danger" onClick={() => handleCaDelete(a.id)}><Trash2 size={10} /></button>
                  </div>
                </div>
              ))}
              {actions.length > 5 && (
                <button className="btn-link" style={{ fontSize: 10, textAlign: "center", cursor: "pointer", border: "none", background: "none", color: "var(--primary)" }} onClick={() => setCaExpanded(!caExpanded)}>
                  {caExpanded ? "Show fewer" : `Show all ${actions.length}`}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Section 3: Post-Market Monitoring (EU AI Act high-risk only) */}
      {isEU && isHighRisk && (
        <div className="panel" style={{ marginBottom: 12 }}>
          <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>Post-Market Monitoring (Art. 61)</strong>
            {isHighRisk && <span className="badge badge-warning" style={{ fontSize: 9 }}>Required</span>}
          </div>
          <div className="panel-body" style={{ padding: "0.5rem 1rem 1rem" }}>
            <label className="muted" style={{ fontSize: 11 }}>Monitoring Plan</label>
            <textarea rows={3} value={pmsPlan} onChange={e => setPmsPlan(e.target.value)}
              placeholder="Describe your post-market monitoring plan..."
              style={{ width: "100%", fontSize: "0.8rem", resize: "vertical", marginTop: 4 }} />
            <button className="btn btn-primary btn-sm" style={{ marginTop: 6 }} disabled={pmsSaving} onClick={handleSavePms}>
              {pmsSaving ? "Saving..." : "Save Plan"}
            </button>
          </div>
        </div>
      )}

      {/* Section 4: GPAI Transparency (EU AI Act GPAI only) */}
      {isEU && isGPAI && (
        <div className="panel" style={{ marginBottom: 12 }}>
          <div className="panel-header"><strong>GPAI Transparency (Art. 48\u201350)</strong></div>
          <div className="panel-body" style={{ padding: "0.75rem 1rem" }}>
            <div className="muted" style={{ fontSize: 11, marginBottom: 8 }}>General-purpose AI transparency obligations. Edit in the system settings.</div>
            <NavLink to={`/aigov/systems/${sid}/edit`} className="btn btn-secondary btn-sm" style={{ fontSize: 10 }}>Edit GPAI Documentation</NavLink>
          </div>
        </div>
      )}

      {articles.length === 0 && !isEU && !isGPAI && (
        <div className="panel" style={{ padding: 16 }}>
          <p className="muted" style={{ fontSize: 12, textAlign: "center" }}>No requirements apply to this risk tier for this framework.</p>
        </div>
      )}
      {articles.length === 0 && isEU && !isHighRisk && !isGPAI && (
        <div className="panel" style={{ padding: 16 }}>
          <p className="muted" style={{ fontSize: 12, textAlign: "center" }}>No EU AI Act requirements apply to this risk tier.</p>
        </div>
      )}
    </div>
  );
}

function EvidenceGapsTab({ sid, system: _system }: { sid: string; system: any }) {
  const { activeFrameworks } = useActiveFrameworks();
  const [evidenceByControl, setEvidenceByControl] = useState<Record<string, number>>({});
  const [articlesByFw, setArticlesByFw] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(true);
  const [fwTab, setFwTab] = useState(() => activeFrameworks[0] || "eu_ai_act");

  useEffect(() => {
    if (!activeFrameworks.includes(fwTab as any)) {
      setFwTab(activeFrameworks[0] || "eu_ai_act");
    }
  }, [activeFrameworks]);

  useEffect(() => {
    Promise.all([
      fetch(apiUrl("/api/evidence-hub?framework_id=AIGov")).then(r => r.json()).catch(() => ({ evidence: [] })),
      Promise.all(
        activeFrameworks.map(fw =>
          fetch(`${API}/systems/${sid}/conformity/articles?framework=${fw}`)
            .then(r => r.json()).then(d => ({ fw, articles: d.articles || [] }))
            .catch(() => ({ fw, articles: [] }))
        )
      ),
    ]).then(([evData, fwData]) => {
      const byControl: Record<string, number> = {};
      for (const item of (evData.evidence || [])) {
        for (const m of (item.mappings || [])) {
          if (m.framework_id === "AIGov" && m.control_id) {
            byControl[m.control_id] = (byControl[m.control_id] || 0) + 1;
          }
        }
      }
      setEvidenceByControl(byControl);
      const byFw: Record<string, any[]> = {};
      for (const d of fwData) {
        byFw[d.fw] = d.articles;
      }
      setArticlesByFw(byFw);
      setLoading(false);
    });
  }, [sid, activeFrameworks]);

  const fws = AI_GOV_FRAMEWORKS.filter(f => activeFrameworks.includes(f.key));

  const articles = articlesByFw[fwTab] || [];
  const covered = articles.filter(a => (evidenceByControl[a.id] || 0) > 0).length;
  const total = articles.length;

  return (
    <div>
      <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <strong>Evidence Coverage</strong>
          <span style={{ fontWeight: 700, fontSize: 18, color: covered === total && total > 0 ? "var(--success)" : "var(--warning)" }}>
            {covered}/{total} controls have evidence
          </span>
        </div>
        {total > 0 && (
          <div style={{ width: "100%", background: "var(--border)", borderRadius: 6, height: 8, marginTop: 8, overflow: "hidden" }}>
            <div style={{ width: `${Math.round((covered / total) * 100)}%`, height: "100%", borderRadius: 6, background: covered === total ? "var(--success)" : "var(--warning)", transition: "width 0.3s" }} />
          </div>
        )}
      </div>

      <div className="aigov-tabs" style={{ marginBottom: 12 }}>
        {fws.map(f => (
          <button key={f.key} className={`aigov-tab${fwTab === f.key ? " aigov-tab--active" : ""}`} onClick={() => setFwTab(f.key)}>{f.label}</button>
        ))}
      </div>

      {loading ? (
        <p className="muted" style={{ padding: 16, fontSize: 12 }}>Loading evidence data...</p>
      ) : articles.length === 0 ? (
        <p className="muted" style={{ padding: 16, fontSize: 12 }}>No controls defined for this framework. Run a conformity assessment first.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {articles.map(a => {
            const count = evidenceByControl[a.id] || 0;
            const hasEvidence = count > 0;
            return (
              <div key={a.id} className="panel" style={{
                padding: "8px 12px",
                borderLeft: `3px solid ${hasEvidence ? "var(--success)" : "var(--danger)"}`,
                display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12,
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500, fontSize: 12 }}>
                    <span style={{ fontFamily: "monospace", marginRight: 6, color: "var(--primary)", fontWeight: 700 }}>{a.ref}</span>
                    {a.title}
                  </div>
                  <div style={{ fontSize: 11, color: hasEvidence ? "var(--success)" : "var(--danger)", marginTop: 2 }}>
                    {hasEvidence ? `${count} evidence file(s) attached` : "No evidence attached"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
                  <NavLink to={`/aigov/systems/${sid}/conformity?framework=${fwTab}`} className="btn btn-sm btn-ghost" style={{ fontSize: 10, padding: "4px 8px" }}>Assess</NavLink>
                  <NavLink to={`/aigov/evidence?framework=AIGov&control=${a.id}`} className="btn btn-sm btn-primary" style={{ fontSize: 10, padding: "4px 8px" }}>
                    {hasEvidence ? "View" : "Upload"}
                  </NavLink>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function LiteracyTab({ sid, API, logs }: { sid: string; API: string; logs: any[] }) {
  const [entries, setEntries] = useState<any[]>(logs);
  const [form, setForm] = useState({ person_name: "", role: "deployer", training_type: "tabletop", training_date: "", notes: "" });

  async function handleAdd() {
    const r = await fetch(`${API}/systems/${sid}/literacy`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
    const d = await r.json();
    setEntries([d.entry, ...entries]);
    setForm({ person_name: "", role: "deployer", training_type: "tabletop", training_date: "", notes: "" });
  }
  async function handleDelete(eid: string) {
    await fetch(`${API}/systems/${sid}/literacy/${eid}`, { method: "DELETE" });
    setEntries(entries.filter((e) => e.id !== eid));
  }

  return (
    <div className="panel-stack">
      <div className="panel" style={{ padding: 16 }}>
        <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Add Training Entry</strong></div>
        <div className="form-grid">
          <div><label className="muted" style={{ fontSize: 11 }}>Person name</label><input value={form.person_name} onChange={(e) => setForm({ ...form, person_name: e.target.value })} /></div>
          <div><label className="muted" style={{ fontSize: 11 }}>Role</label><select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="deployer">Deployer</option><option value="operator">Operator</option><option value="reviewer">Reviewer</option><option value="risk_owner">Risk Owner</option><option value="other">Other</option></select></div>
          <div><label className="muted" style={{ fontSize: 11 }}>Training Type</label><select value={form.training_type} onChange={(e) => setForm({ ...form, training_type: e.target.value })}><option value="tabletop">Tabletop</option><option value="onboarding">Onboarding</option><option value="annual">Annual</option><option value="workshop">Workshop</option><option value="other">Other</option></select></div>
          <div><label className="muted" style={{ fontSize: 11 }}>Date</label><input type="date" value={form.training_date} onChange={(e) => setForm({ ...form, training_date: e.target.value })} /></div>
          <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Notes</label><textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} /></div>
        </div>
        <button onClick={handleAdd} className="btn btn-primary btn-sm" style={{ marginTop: 8 }}><Users size={14} /> Add Entry</button>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>AI Literacy Log ({entries.length})</strong></div>
        {entries.map((e) => (
          <div key={e.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 12 }}>
            <div>
              <span style={{ fontWeight: 500 }}>{e.person_name}</span> — {e.role} · {e.training_type}
              <div className="muted" style={{ fontSize: 11 }}>{e.training_date || e.created_at?.slice(0, 10)}</div>
            </div>
            <button className="icon-btn icon-btn--danger" onClick={() => handleDelete(e.id)}><Trash2 size={12} /></button>
          </div>
        ))}
        {entries.length === 0 && <p className="muted" style={{ fontSize: 12 }}>No training records.</p>}
      </div>
    </div>
  );
}


