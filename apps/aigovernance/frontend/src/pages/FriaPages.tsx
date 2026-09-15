import { useEffect, useState } from "react";
import { NavLink, useParams, useNavigate } from "react-router-dom";
import { Plus, ArrowLeft, Shield, Upload, Download, Copy } from "lucide-react";
import { FilterBar, FilterSelect } from "@shared/filter-bar";

const API = "/api/ai-governance";

export function FriaListPage() {
  const [frias, setFrias] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");
  useEffect(() => {
    const qs = status ? `?status=${status}` : "";
    fetch(`${API}/frias${qs}`).then((r) => r.json()).then((d) => setFrias(d.frias || [])).finally(() => setLoading(false));
  }, [status]);

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div className="aigov-page-header" style={{ marginBottom: 0 }}>
          <h1>FRIA</h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => window.open(`${API}/frias/export/csv`)}><Download size={14} /> CSV</button>
          <NavLink to="/aigov/frias/new" className="btn btn-primary"><Plus size={14} /> New FRIA</NavLink>
        </div>
      </div>

      <FilterBar>
        <FilterSelect value={status} onChange={setStatus} options={[
          { value: "draft", label: "Draft" },
          { value: "submitted", label: "Submitted" },
          { value: "approved", label: "Approved" },
          { value: "rejected", label: "Rejected" },
        ]} placeholder="All status" />
      </FilterBar>

      {loading ? <p className="muted" style={{ fontSize: 13 }}>Loading...</p> : frias.length === 0 ? (
        <div className="aigov-empty">
          <Shield size={32} />
          <h3>No FRIAs yet</h3>
          <p>Create your first Fundamental Rights Impact Assessment</p>
          <NavLink to="/aigov/frias/new" className="btn btn-primary"><Plus size={14} /> New FRIA</NavLink>
        </div>
      ) : (
        <div className="panel-stack" style={{ gap: 8 }}>
          {frias.map((f) => (
            <NavLink key={f.id} to={`/aigov/frias/${f.id}`} className="panel" style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", textDecoration: "none", color: "inherit" }}>
              <Shield size={16} style={{ color: "var(--primary)", flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500, fontSize: 14 }}>{f.system_name}</div>
                <div className="muted" style={{ fontSize: 12 }}>{f.risk_classification} · {f.deployer_entity} · {f.created_at?.slice(0, 10)}</div>
              </div>
              <span className={`badge ${f.status === "approved" ? "met" : f.status === "rejected" ? "" : "neutral"}`}
                style={f.status === "rejected" ? { background: "var(--danger-soft)", color: "var(--danger)" } : {}}>
                {f.status}
              </span>
            </NavLink>
          ))}
        </div>
      )}
    </>
  );
}

export function FriaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [fria, setFria] = useState<any>(null);
  const [commentText, setCommentText] = useState("");
  const [evidenceLabel, setEvidenceLabel] = useState("");
  const [uploading, setUploading] = useState(false);

  useEffect(() => { if (id) fetch(`${API}/fria/${id}`).then((r) => r.json()).then((d) => setFria(d.fria)); }, [id]);

  if (!fria) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  async function handleAction(action: string) {
    await fetch(`${API}/fria/${id}/${action}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reviewed_by: "Admin" }) });
    const d = await fetch(`${API}/fria/${id}`).then((r) => r.json());
    setFria(d.fria);
  }
  async function handleComment() {
    if (!commentText.trim()) return;
    await fetch(`${API}/fria/${id}/comments`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ author: "Reviewer", text: commentText }) });
    setCommentText("");
    const d = await fetch(`${API}/fria/${id}`).then((r) => r.json());
    setFria(d.fria);
  }
  async function handleEvidenceUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData(); form.append("file", file); form.append("label", evidenceLabel);
    await fetch(`${API}/fria/${id}/evidence`, { method: "POST", body: form });
    const d = await fetch(`${API}/fria/${id}`).then((r) => r.json());
    setFria(d.fria); setEvidenceLabel(""); setUploading(false); e.target.value = "";
  }
  async function handleEvidenceDelete(eid: string) {
    await fetch(`${API}/fria/${id}/evidence/${eid}`, { method: "DELETE" });
    const d = await fetch(`${API}/fria/${id}`).then((r) => r.json());
    setFria(d.fria);
  }
  async function handleCopy() {
    const r = await fetch(`${API}/fria/${id}/copy`, { method: "POST" });
    const d = await r.json();
    navigate(`/aigov/frias/${d.id}`);
  }
  async function handleExportCSV() { window.open(`${API}/frias/export/csv`, "_blank"); }

  return (
    <>
      <NavLink to="/aigov/frias/list" style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--muted)", textDecoration: "none", marginBottom: 12 }}>
        <ArrowLeft size={12} /> Back
      </NavLink>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 600, margin: "0 0 4px" }}>{fria.system_name}</h1>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="badge neutral">{fria.status}</span>
            <span className="muted" style={{ fontSize: 12 }}>{fria.risk_classification} · {fria.deployer_entity}</span>
          </div>
        </div>
        <div className="controls-toolbar-options" style={{ display: "flex", gap: 8 }}>
          <button onClick={handleCopy} className="btn btn-secondary btn-sm"><Copy size={14} /> Copy</button>
          <button onClick={handleExportCSV} className="btn btn-secondary btn-sm"><Download size={14} /> CSV</button>
          {fria.status === "draft" && <button onClick={() => handleAction("submit")} className="btn btn-primary btn-sm">Submit</button>}
          {fria.status === "submitted" && (
            <><button onClick={() => handleAction("approve")} className="btn btn-primary btn-sm" style={{ background: "var(--success)" }}>Approve</button>
              <button onClick={() => handleAction("reject")} className="btn btn-primary btn-sm" style={{ background: "var(--danger)" }}>Reject</button></>
          )}
        </div>
      </div>

      <div className="panel-stack" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>System</strong></div>
          {field("Description", fria.system_description)}
          {field("Purpose", fria.system_purpose)}
          {field("Deployer", fria.deployer_entity)}
          {field("Developer", fria.developer_entity)}
          {field("Use Frequency", fria.use_frequency)}
        </div>
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Risk &amp; Rights</strong></div>
          {field("Classification", fria.risk_classification)}
          {field("Affected Rights", fria.affected_rights?.join(", "))}
          {field("Impact", fria.impact_description)}
          {field("Groups Affected", fria.affected_groups)}
          <div style={{ fontSize: 12, marginTop: 4 }}><span className="muted" style={{ width: 100, display: "inline-block" }}>Scale</span><span style={{ color: "var(--text)" }}>{fria.scale || "-"}</span></div>
          <div style={{ fontSize: 12 }}><span className="muted" style={{ width: 100, display: "inline-block" }}>Geography</span><span style={{ color: "var(--text)" }}>{(fria.geography || []).join(", ") || "-"}</span></div>
        </div>
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Measures</strong></div>
          {field("Technical", fria.technical_measures)}
          {field("Organizational", fria.organizational_measures)}
          {field("Oversight", fria.oversight_measures)}
          {field("Risk Remediation", fria.risk_remediation)}
          {field("Complaint Mechanism", fria.complaint_mechanism)}
        </div>
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Human Oversight</strong></div>
          {field("Override Capability", fria.override_capability ? "Yes" : "No")}
          {field("Assessor", fria.assessor_name)}
          {field("Role", fria.assessor_role)}
          {field("Date", fria.assessor_date?.slice(0, 10))}
          {field("Stakeholders", fria.consulted_stakeholders)}
        </div>

        {(fria.risk_assessments || []).length > 0 && (
          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Risk Assessments</strong></div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {fria.risk_assessments.map((ra: any, i: number) => (
                <div key={i} style={{ padding: 8, background: "var(--info-soft)", borderRadius: "var(--radius)", fontSize: 12 }}>
                  <div style={{ fontWeight: 500 }}>{ra.right}</div>
                  <div className="muted">L:{ra.likelihood} × I:{ra.impact} = {ra.likelihood * ra.impact}</div>
                  {ra.mitigation && <div className="muted" style={{ marginTop: 2 }}>Mitigation: {ra.mitigation}</div>}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Evidence ({fria.evidence?.length || 0})</strong></div>
          {fria.evidence?.length > 0 && fria.evidence.map((e: any) => (
            <div key={e.id} style={{ fontSize: 12, padding: "6px 0", borderBottom: "1px solid var(--border-subtle)" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span><span style={{ fontWeight: 500 }}>{e.label}</span> <span className="muted">({e.filename})</span></span>
                <button className="icon-btn icon-btn--danger" onClick={() => handleEvidenceDelete(e.id)}>✕</button>
              </div>
              {/\.(png|jpg|jpeg|gif|webp|svg)$/i.test(e.filename) && (
                <img src={`${API}/fria/${id}/evidence/${e.id}`} alt={e.label} style={{ maxHeight: 100, marginTop: 4, borderRadius: 4, border: "1px solid var(--border)", objectFit: "contain", maxWidth: "100%" }} />
              )}
            </div>
          ))}
          {(!fria.evidence || fria.evidence.length === 0) && <p className="muted" style={{ fontSize: 12 }}>No evidence.</p>}
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <input placeholder="Label" value={evidenceLabel} onChange={(e) => setEvidenceLabel(e.target.value)} style={{ flex: 1 }} />
            <button className="btn btn-secondary btn-sm" onClick={() => document.getElementById("fr-ev")?.click()} disabled={uploading}><Upload size={14} /></button>
            <input id="fr-ev" type="file" hidden onChange={handleEvidenceUpload} />
          </div>
        </div>

        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Comments</strong></div>
          {(fria.comments || []).length === 0 && <p className="muted" style={{ fontSize: 12 }}>No comments.</p>}
          {fria.comments?.map((c: any) => (
            <div key={c.id} style={{ fontSize: 11, padding: "4px 0", borderBottom: "1px solid var(--border-subtle)" }}>
              <span style={{ fontWeight: 500 }}>{c.author}</span>: {c.text}
              <div className="muted" style={{ fontSize: 10 }}>{c.created_at?.slice(0, 16).replace("T", " ")}</div>
            </div>
          ))}
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <input placeholder="Add comment..." value={commentText} onChange={(e) => setCommentText(e.target.value)} style={{ flex: 1 }} />
            <button onClick={handleComment} className="btn btn-secondary btn-sm">Send</button>
          </div>
        </div>
      </div>
    </>
  );
}

export function FriaNewPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    system_name: "", system_description: "", system_purpose: "", deployer_entity: "",
    developer_entity: "", risk_classification: "unclassified",
    affected_rights: "", impact_description: "", affected_groups: "", scale: "", geography: "",
    technical_measures: "", organizational_measures: "", oversight_measures: "",
    override_capability: false, assessor_name: "", assessor_role: "", assessor_date: "",
    consulted_stakeholders: "",
    use_frequency: "", risk_remediation: "", complaint_mechanism: "",
  });
  const [riskAssessments, setRiskAssessments] = useState<Array<{right: string; likelihood: number; impact: number; mitigation: string}>>([]);

  const steps = ["System", "Rights Impact", "Measures", "Review"];

  async function handleSubmit() {
    if (!form.system_name.trim()) return;
    const r = await fetch(`${API}/fria`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        affected_rights: form.affected_rights.split(",").map((s: string) => s.trim()).filter(Boolean),
        geography: form.geography.split(",").map((s: string) => s.trim()).filter(Boolean),
        risk_assessments: riskAssessments,
      }),
    });
    const d = await r.json();
    navigate(`/aigov/frias/${d.id}`);
  }

  return (
    <div style={{ maxWidth: 600, margin: "0 auto" }}>
      <NavLink to="/aigov/frias/list" style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--muted)", textDecoration: "none", marginBottom: 12 }}><ArrowLeft size={12} /> Back</NavLink>
      <div className="aigov-page-header">
        <h1>New FRIA</h1>
      </div>
      <div className="aigov-wizard-steps">
        {steps.map((s, i) => (
          <div key={s} className={`aigov-wizard-step ${step === i ? "aigov-wizard-step--active" : step > i ? "aigov-wizard-step--done" : ""}`}>{s}</div>
        ))}
      </div>

      {step === 0 && (
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>System Information</strong></div>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>System Name *</label><input value={form.system_name} onChange={(e) => setForm({ ...form, system_name: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea value={form.system_description} onChange={(e) => setForm({ ...form, system_description: e.target.value })} rows={2} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Purpose</label><textarea value={form.system_purpose} onChange={(e) => setForm({ ...form, system_purpose: e.target.value })} rows={2} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Deployer Entity</label><input value={form.deployer_entity} onChange={(e) => setForm({ ...form, deployer_entity: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Developer Entity</label><input value={form.developer_entity} onChange={(e) => setForm({ ...form, developer_entity: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Risk Classification</label><input value={form.risk_classification} onChange={(e) => setForm({ ...form, risk_classification: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Use Frequency &amp; Period</label><textarea value={form.use_frequency} onChange={(e) => setForm({ ...form, use_frequency: e.target.value })} rows={2} placeholder="How often and over what period the system is used (e.g. daily, 24/7, batch processing weekly)" /></div>
          </div>
          <button onClick={() => setStep(1)} className="btn btn-primary" style={{ marginTop: 12 }}>Next: Rights Impact</button>
        </div>
      )}

      {step === 1 && (
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Rights Impact</strong></div>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Affected Rights (comma-sep)</label><input value={form.affected_rights} onChange={(e) => setForm({ ...form, affected_rights: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Impact Description</label><textarea value={form.impact_description} onChange={(e) => setForm({ ...form, impact_description: e.target.value })} rows={2} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Affected Groups</label><input value={form.affected_groups} onChange={(e) => setForm({ ...form, affected_groups: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Scale</label><input value={form.scale} onChange={(e) => setForm({ ...form, scale: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Geography (csv)</label><input value={form.geography} onChange={(e) => setForm({ ...form, geography: e.target.value })} placeholder="EU, US, UK" /></div>
          </div>

          <h4 style={{ fontSize: 12, fontWeight: 600, margin: "12px 0 8px", color: "var(--primary)" }}>Risk Assessments</h4>
          {riskAssessments.map((ra, i) => (
            <div key={i} style={{ display: "flex", gap: 4, alignItems: "center", marginBottom: 4, fontSize: 12 }}>
              <input value={ra.right} onChange={(e) => { const n = [...riskAssessments]; n[i].right = e.target.value; setRiskAssessments(n); }} placeholder="Right" style={{ flex: 1 }} />
              <input type="number" value={ra.likelihood} onChange={(e) => { const n = [...riskAssessments]; n[i].likelihood = Number(e.target.value); setRiskAssessments(n); }} placeholder="L" style={{ width: 40 }} />
              <input type="number" value={ra.impact} onChange={(e) => { const n = [...riskAssessments]; n[i].impact = Number(e.target.value); setRiskAssessments(n); }} placeholder="I" style={{ width: 40 }} />
              <span className="muted" style={{ fontSize: 11 }}>{ra.likelihood * ra.impact}</span>
              <button type="button" onClick={() => setRiskAssessments(riskAssessments.filter((_, j) => j !== i))} className="icon-btn icon-btn--danger">✕</button>
            </div>
          ))}
          <button type="button" onClick={() => setRiskAssessments([...riskAssessments, { right: "", likelihood: 1, impact: 1, mitigation: "" }])} className="btn btn-secondary btn-sm">+ Add Risk</button>
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={() => setStep(0)} className="btn btn-secondary">Back</button>
            <button onClick={() => setStep(2)} className="btn btn-primary">Next: Measures</button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Measures &amp; Oversight</strong></div>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Technical Measures</label><textarea value={form.technical_measures} onChange={(e) => setForm({ ...form, technical_measures: e.target.value })} rows={2} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Organizational Measures</label><textarea value={form.organizational_measures} onChange={(e) => setForm({ ...form, organizational_measures: e.target.value })} rows={2} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Oversight Measures</label><textarea value={form.oversight_measures} onChange={(e) => setForm({ ...form, oversight_measures: e.target.value })} rows={2} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Risk Remediation (measures if risks materialize)</label><textarea value={form.risk_remediation} onChange={(e) => setForm({ ...form, risk_remediation: e.target.value })} rows={2} placeholder="Contingency plans, rollback procedures, incident response..." /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Complaint Mechanism</label><textarea value={form.complaint_mechanism} onChange={(e) => setForm({ ...form, complaint_mechanism: e.target.value })} rows={2} placeholder="How affected persons can raise concerns or complaints..." /></div>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, cursor: "pointer", marginBottom: 12 }}>
            <input type="checkbox" checked={form.override_capability} onChange={(e) => setForm({ ...form, override_capability: e.target.checked })} />
            Human override capability available
          </label>
          <div className="form-grid">
            <div><label className="muted" style={{ fontSize: 11 }}>Assessor Name</label><input value={form.assessor_name} onChange={(e) => setForm({ ...form, assessor_name: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Assessor Role</label><input value={form.assessor_role} onChange={(e) => setForm({ ...form, assessor_role: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Date</label><input type="date" value={form.assessor_date} onChange={(e) => setForm({ ...form, assessor_date: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Stakeholders Consulted</label><input value={form.consulted_stakeholders} onChange={(e) => setForm({ ...form, consulted_stakeholders: e.target.value })} /></div>
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={() => setStep(1)} className="btn btn-secondary">Back</button>
            <button onClick={() => setStep(3)} className="btn btn-primary">Review</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Review &amp; Submit</strong></div>
          <div style={{ fontSize: 12, lineHeight: 1.8 }}>
            <strong>System:</strong> {form.system_name}<br />
            <strong>Deployer:</strong> {form.deployer_entity || "-"}<br />
            <strong>Rights:</strong> {form.affected_rights || "-"}<br />
            <strong>Assessments:</strong> {riskAssessments.length}<br />
            <strong>Override:</strong> {form.override_capability ? "Yes" : "No"}<br />
            <strong>Assessor:</strong> {form.assessor_name || "-"}
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={() => setStep(2)} className="btn btn-secondary">Back</button>
            <button onClick={handleSubmit} className="btn btn-primary">Create FRIA</button>
          </div>
        </div>
      )}
    </div>
  );
}

function field(label: string, value: any) {
  if (!value && value !== 0) return null;
  return <div style={{ fontSize: 12, marginBottom: 4 }}><span className="muted" style={{ width: 100, display: "inline-block", flexShrink: 0 }}>{label}</span><span style={{ color: "var(--text)" }}>{String(value)}</span></div>;
}
