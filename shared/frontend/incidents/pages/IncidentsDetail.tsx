import { useEffect, useState, useRef } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { apiUrl } from "@shared/apiPrefix";
import { api } from "../api";
import type { Incident, Playbook, CorrectiveAction } from "../types";
import { SEVERITY_LABELS, STATUS_LABELS, FAILURE_MODE_LABELS } from "../types";

const SEV_COLORS: Record<string, string> = {
  critical: "#dc2626", high: "#ea580c", medium: "#ca8a04", low: "#6b7280",
};

function fmtDate(d: string | undefined | null) {
  if (!d) return "";
  return d.slice(0, 10);
}

function daysUntil(deadline: string | undefined): number | null {
  if (!deadline) return null;
  const diff = new Date(deadline).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

function fmtSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const STATUS_ORDER = ["triage", "investigation", "containment", "root_cause_analysis", "remediation", "closed"];

export default function IncidentsDetail({ basePath = "/incidents" }: { basePath?: string }) {
  const { iid } = useParams();
  const navigate = useNavigate();
  const [inc, setInc] = useState<Incident | null>(null);
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"overview" | "telemetry" | "actions" | "evidence" | "reports">("overview");
  const [msg, setMsg] = useState("");
  const [transitioning, setTransitioning] = useState(false);
  const [rcaForm, setRcaForm] = useState({ root_cause: "", contributing_factors: "", lessons_learned: "", blast_radius: "" });
  const [caForm, setCaForm] = useState({ description: "", assigned_to: "", due_date: "" });
  const [telForm, setTelForm] = useState({ prompt: "", response: "", model_parameters: "", anonymized_logs: "" });
  const [reportForm, setReportForm] = useState({ report_type: "initial", submitted_to: "", content: "" });
  const [evidenceLabel, setEvidenceLabel] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const load = async () => {
    if (!iid) return;
    setLoading(true);
    try {
      const d = await api.get(iid);
      setInc(d.incident);
      if (d.incident.failure_mode) {
        try { const pb = await api.playbook(d.incident.failure_mode); setPlaybook(pb.playbook); } catch { /* ignore */ }
      }
      const rca = d.incident.rca || {};
      setRcaForm({
        root_cause: rca.root_cause || "",
        contributing_factors: Array.isArray(rca.contributing_factors) ? rca.contributing_factors.join(", ") : (rca.contributing_factors || ""),
        lessons_learned: rca.lessons_learned || "",
        blast_radius: rca.blast_radius || "",
      });
      const tel = d.incident.telemetry || {};
      setTelForm({
        prompt: tel.prompt || "",
        response: tel.response || "",
        model_parameters: tel.model_parameters ? JSON.stringify(tel.model_parameters, null, 2) : "",
        anonymized_logs: tel.anonymized_logs || "",
      });
    } catch { setMsg("Failed to load incident"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [iid]);

  const doTransition = async (status: string) => {
    setTransitioning(true);
    try {
      await api.transition(iid!, status, undefined, status === "root_cause_analysis" ? {
        root_cause: rcaForm.root_cause,
        contributing_factors: rcaForm.contributing_factors.split(",").map((s: string) => s.trim()).filter(Boolean),
        lessons_learned: rcaForm.lessons_learned,
        blast_radius: rcaForm.blast_radius,
      } : undefined);
      await load();
    } catch (e) { setMsg(String(e)); }
    finally { setTransitioning(false); }
  };

  const handleEvidenceUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    try {
      await api.uploadEvidence(iid!, file, evidenceLabel);
      if (fileRef.current) fileRef.current.value = "";
      setEvidenceLabel("");
      await load();
    } catch (e) { setMsg(String(e)); }
  };

  const handleDeleteEvidence = async (eid: string) => {
    if (!confirm("Delete this evidence?")) return;
    try { await api.deleteEvidence(iid!, eid); await load(); } catch (e) { setMsg(String(e)); }
  };

  const addCa = async () => {
    if (!caForm.description) return;
    try { await api.addCorrectiveAction(iid!, caForm); setCaForm({ description: "", assigned_to: "", due_date: "" }); await load(); } catch (e) { setMsg(String(e)); }
  };

  const updateCa = async (caid: string, data: Partial<CorrectiveAction>) => {
    try { await api.updateCorrectiveAction(iid!, caid, data); await load(); } catch (e) { setMsg(String(e)); }
  };

  const saveTelemetry = async () => {
    try {
      let mp: Record<string, unknown> = {};
      try { mp = JSON.parse(telForm.model_parameters); } catch { mp = { raw: telForm.model_parameters }; }
      await api.saveTelemetry(iid!, { prompt: telForm.prompt, response: telForm.response, model_parameters: mp, anonymized_logs: telForm.anonymized_logs });
      setMsg("Telemetry saved");
      await load();
    } catch (e) { setMsg(String(e)); }
  };

  const createReport = async () => {
    try { await api.createRegulatoryReport(iid!, reportForm); setReportForm({ report_type: "initial", submitted_to: "", content: "" }); await load(); } catch (e) { setMsg(String(e)); }
  };

  const autoClassify = async () => {
    try { await api.autoClassify(iid!); setMsg("Severity auto-classified"); await load(); } catch (e) { setMsg(String(e)); }
  };

  const notifyRegulator = async () => {
    try { await api.notifyRegulator(iid!); await load(); } catch (e) { setMsg(String(e)); }
  };

  const handleDelete = async () => {
    if (!confirm("Delete this incident permanently?")) return;
    try { await api.delete(iid!); navigate(basePath); } catch (e) { setMsg(String(e)); }
  };

  if (loading) return <p className="muted">Loading incident...</p>;
  if (!inc) return <p className="muted">Incident not found.</p>;

  const currentIdx = STATUS_ORDER.indexOf(inc.status);
  const clock = inc.regulatory_clock || {};
  const deadlineDays = daysUntil(clock.deadline);

  return (
    <div className="page-stack">
      {msg && <div className="banner" style={{ background: "var(--info-soft)", padding: "8px 12px", borderRadius: "var(--radius)", marginBottom: 12, fontSize: 13 }}>{msg}<button className="btn-link" style={{ float: "right" }} onClick={() => setMsg("")}>×</button></div>}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
        <div>
          <Link to={basePath} className="muted" style={{ fontSize: 13, textDecoration: "none" }}>← Back to Incidents</Link>
          <h2 style={{ margin: "4px 0 0 0" }}>{inc.title}</h2>
          <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap", marginTop: 4 }}>
            <span className="badge" style={{ background: SEV_COLORS[inc.severity] || "#6b7280", color: "#fff" }}>{SEVERITY_LABELS[inc.severity] || inc.severity}</span>
            <span className="badge badge-warning">{STATUS_LABELS[inc.status] || inc.status}</span>
            {inc.failure_mode && <span className="muted" style={{ fontSize: 12 }}>{FAILURE_MODE_LABELS[inc.failure_mode] || inc.failure_mode}</span>}
            {inc.reporter_name && <span className="muted" style={{ fontSize: 12 }}>Reported by {inc.reporter_name}</span>}
            <span className="muted" style={{ fontSize: 12 }}>{fmtDate(inc.created_at)}</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap", alignItems: "center" }}>
          <button className="btn btn-sm btn-secondary" onClick={() => navigate(`${basePath}/${iid}/edit`)}>Edit</button>
          <button className="btn btn-sm btn-secondary" onClick={autoClassify}>Auto-Classify</button>
          <a className="btn btn-sm btn-secondary" href={api.exportUrl(iid!)} download>CSV</a>
          <a className="btn btn-sm btn-secondary" href={api.regulatorPackUrl(iid!)} download>Regulator Pack</a>
          <button className="btn btn-sm btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      {playbook && inc.status !== "closed" && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-header"><strong>Response Playbook: {playbook.title}</strong></div>
          <div className="panel-body">
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
              {Object.entries(playbook.sections).map(([section, steps]) => (
                <div key={section}>
                  <strong style={{ fontSize: 12 }}>{section}</strong>
                  <ul style={{ paddingLeft: 16, margin: "4px 0 0 0", fontSize: 12 }}>
                    {steps.map((s, i) => <li key={i} className="muted">{s}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div className="panel">
          <div className="panel-header"><strong>Workflow</strong></div>
          <div className="panel-body">
            {STATUS_ORDER.map((s, i) => {
              const isPast = i < currentIdx;
              const isCurrent = i === currentIdx;
              const isFuture = i > currentIdx;
              const nextIdx = currentIdx + 1;
              const canAdvance = i === currentIdx && nextIdx < STATUS_ORDER.length;
              return (
                <div key={s} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 0", borderBottom: i < STATUS_ORDER.length - 1 ? "1px solid var(--border)" : "none" }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: isPast ? "var(--success)" : isCurrent ? "var(--primary)" : "var(--border)", flexShrink: 0 }} />
                  <span style={{ flex: 1, fontSize: 13, fontWeight: isCurrent ? 600 : 400, color: isFuture ? "var(--muted)" : "inherit" }}>{STATUS_LABELS[s]}</span>
                  {canAdvance && (
                    <button className="btn btn-sm btn-primary" disabled={transitioning} onClick={() => doTransition(STATUS_ORDER[nextIdx])}>
                      {transitioning ? "..." : STATUS_ORDER[nextIdx] === "root_cause_analysis" ? "Complete RCA" : STATUS_ORDER[nextIdx] === "containment" ? "Contain" : STATUS_ORDER[nextIdx] === "closed" ? "Close" : `Start ${STATUS_LABELS[STATUS_ORDER[nextIdx]]}`}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><strong>Regulatory Clock</strong></div>
          <div className="panel-body">
            {clock.label && <p style={{ fontSize: 13, fontWeight: 600 }}>{clock.label}</p>}
            {clock.deadline && (
              <p style={{ fontSize: 13, color: deadlineDays !== null && deadlineDays <= 2 ? "var(--danger)" : deadlineDays !== null && deadlineDays <= 5 ? "#ea580c" : "var(--muted)" }}>
                Deadline: {fmtDate(clock.deadline)}
                {deadlineDays !== null && (deadlineDays <= 0 ? <strong> (OVERDUE by {Math.abs(deadlineDays)} days)</strong> : <span> ({deadlineDays} days remaining)</span>)}
              </p>
            )}
            {clock.notified ? (
              <p style={{ fontSize: 12, color: "var(--success)" }}>Notified on {fmtDate(clock.notified_at)}</p>
            ) : (
              <button className="btn btn-sm btn-danger" onClick={notifyRegulator}>Notify Regulator</button>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 4, marginBottom: 16, borderBottom: "1px solid var(--border)", flexWrap: "wrap" }}>
        {(["overview", "telemetry", "actions", "evidence", "reports"] as const).map((t) => (
          <button key={t} className={`btn btn-sm ${tab === t ? "btn-primary" : "btn-ghost"}`} style={{ borderBottom: tab === t ? "2px solid var(--primary)" : "none", borderRadius: 0 }} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="panel">
            <div className="panel-header"><strong>Details</strong></div>
            <div className="panel-body" style={{ fontSize: 13 }}>
              <p><strong>Description:</strong> {inc.description || "N/A"}</p>
              <p><strong>Failure Mode:</strong> {inc.failure_mode ? (FAILURE_MODE_LABELS[inc.failure_mode] || inc.failure_mode) : "N/A"}</p>
              {inc.model_name && <p><strong>Model:</strong> {inc.model_name}</p>}
              {inc.system_id && <p><strong>System:</strong> {inc.system_id}</p>}
              <p><strong>Reporter:</strong> {inc.reporter_name || "N/A"}</p>
              <p><strong>Created:</strong> {fmtDate(inc.created_at)}</p>
              <p><strong>Updated:</strong> {fmtDate(inc.updated_at)}</p>
            </div>
          </div>
          <div className="panel">
            <div className="panel-header"><strong>Impact Assessment</strong></div>
            <div className="panel-body" style={{ fontSize: 13 }}>
              <p><strong>Description:</strong> {inc.impact?.description || "N/A"}</p>
              <p><strong>Inference Calls Affected:</strong> {inc.impact?.affected_inference_pct != null ? `${inc.impact.affected_inference_pct}%` : "N/A"}</p>
              <p><strong>Users Exposed:</strong> {inc.impact?.total_users_exposed != null ? inc.impact.total_users_exposed.toLocaleString() : "N/A"}</p>
              {inc.impact?.downstream_applications?.length ? (
                <p><strong>Downstream:</strong> {inc.impact.downstream_applications.join(", ")}</p>
              ) : null}
            </div>
          </div>
          {inc.rca?.root_cause && (
            <div className="panel" style={{ gridColumn: "1 / -1" }}>
              <div className="panel-header"><strong>Root Cause Analysis</strong></div>
              <div className="panel-body" style={{ fontSize: 13 }}>
                <p><strong>Root Cause:</strong> {inc.rca.root_cause}</p>
                {inc.rca.contributing_factors?.length ? <p><strong>Contributing Factors:</strong> {Array.isArray(inc.rca.contributing_factors) ? inc.rca.contributing_factors.join(", ") : inc.rca.contributing_factors}</p> : null}
                {inc.rca.lessons_learned && <p><strong>Lessons Learned:</strong> {inc.rca.lessons_learned}</p>}
                {inc.rca.blast_radius && <p><strong>Blast Radius:</strong> {inc.rca.blast_radius}</p>}
              </div>
            </div>
          )}
          {inc.history && inc.history.length > 0 && (
            <div className="panel" style={{ gridColumn: "1 / -1" }}>
              <div className="panel-header"><strong>History</strong></div>
              <div className="panel-body" style={{ fontSize: 12, maxHeight: 200, overflow: "auto" }}>
                {inc.history.map((h, i) => (
                  <div key={i} style={{ padding: "4px 0", borderBottom: "1px solid var(--border)", display: "flex", gap: 8 }}>
                    <span className="muted" style={{ whiteSpace: "nowrap" }}>{h.timestamp?.slice(0, 16)}</span>
                    <strong>{h.action}</strong>
                    <span className="muted">{h.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "telemetry" && (
        <div className="panel">
          <div className="panel-header"><strong>Telemetry Snapshot</strong></div>
          <div className="panel-body">
            {inc.telemetry?.snapshot_taken_at && <p className="muted" style={{ fontSize: 11 }}>Last snapshot: {inc.telemetry.snapshot_taken_at}</p>}
            <div className="form-grid">
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Prompt</label><textarea rows={3} value={telForm.prompt} onChange={(e) => setTelForm({ ...telForm, prompt: e.target.value })} /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Response</label><textarea rows={3} value={telForm.response} onChange={(e) => setTelForm({ ...telForm, response: e.target.value })} /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Model Parameters (JSON)</label><textarea rows={3} value={telForm.model_parameters} onChange={(e) => setTelForm({ ...telForm, model_parameters: e.target.value })} style={{ fontFamily: "monospace", fontSize: 11 }} /></div>
              <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Anonymized Logs</label><textarea rows={3} value={telForm.anonymized_logs} onChange={(e) => setTelForm({ ...telForm, anonymized_logs: e.target.value })} style={{ fontFamily: "monospace", fontSize: 11 }} /></div>
            </div>
            <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} onClick={saveTelemetry}>Save Snapshot</button>
          </div>
        </div>
      )}

      {tab === "actions" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="panel">
            <div className="panel-header"><strong>Corrective Actions</strong></div>
            <div className="panel-body">
              {(inc.corrective_actions || []).length === 0 && <p className="muted" style={{ fontSize: 12 }}>No corrective actions.</p>}
              {(inc.corrective_actions || []).map((ca) => (
                <div key={ca.id} style={{ padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 13 }}>
                  <strong>{ca.description}</strong>
                  <div style={{ display: "flex", gap: 8, marginTop: 4, alignItems: "center", flexWrap: "wrap" }}>
                    {ca.assigned_to && <span className="muted">Assigned: {ca.assigned_to}</span>}
                    {ca.due_date && <span className="muted">Due: {ca.due_date}</span>}
                    <select value={ca.status} onChange={(e) => updateCa(ca.id, { status: e.target.value as "pending" | "in_progress" | "completed" })} style={{ fontSize: 11 }}>
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-header"><strong>Root Cause Analysis</strong></div>
            <div className="panel-body">
              <div className="form-grid">
                <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Root Cause</label><textarea rows={2} value={rcaForm.root_cause} onChange={(e) => setRcaForm({ ...rcaForm, root_cause: e.target.value })} /></div>
                <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Contributing Factors (comma-separated)</label><input value={rcaForm.contributing_factors} onChange={(e) => setRcaForm({ ...rcaForm, contributing_factors: e.target.value })} /></div>
                <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Blast Radius / Downstream</label><input value={rcaForm.blast_radius} onChange={(e) => setRcaForm({ ...rcaForm, blast_radius: e.target.value })} /></div>
                <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Lessons Learned</label><textarea rows={2} value={rcaForm.lessons_learned} onChange={(e) => setRcaForm({ ...rcaForm, lessons_learned: e.target.value })} /></div>
              </div>
              <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} onClick={() => doTransition("root_cause_analysis")}>Save RCA</button>
            </div>
          </div>
          <div className="panel" style={{ gridColumn: "1 / -1" }}>
            <div className="panel-header"><strong>Add Corrective Action</strong></div>
            <div className="panel-body">
              <div className="form-grid">
                <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><input value={caForm.description} onChange={(e) => setCaForm({ ...caForm, description: e.target.value })} /></div>
                <div><label className="muted" style={{ fontSize: 11 }}>Assigned To</label><input value={caForm.assigned_to} onChange={(e) => setCaForm({ ...caForm, assigned_to: e.target.value })} /></div>
                <div><label className="muted" style={{ fontSize: 11 }}>Due Date</label><input type="date" value={caForm.due_date} onChange={(e) => setCaForm({ ...caForm, due_date: e.target.value })} /></div>
              </div>
              <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} onClick={addCa} disabled={!caForm.description}>Add</button>
            </div>
          </div>
        </div>
      )}

      {tab === "evidence" && (
        <div className="panel">
          <div className="panel-header"><strong>Evidence ({inc.evidence?.length || 0})</strong></div>
          <div className="panel-body">
            {(inc.evidence || []).length > 0 && (
              <ul style={{ listStyle: "none", padding: 0, margin: "0 0 16px 0" }}>
                {(inc.evidence || []).map((ev) => (
                  <li key={ev.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 13 }}>
                    <div>
                      <strong>{ev.label || ev.filename}</strong>
                      <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>{ev.filename} ({fmtSize(ev.size)})</span>
                      <br /><span className="muted" style={{ fontSize: 11 }}>{fmtDate(ev.uploaded_at)}</span>
                    </div>
                    <div style={{ display: "flex", gap: 4 }}>
                      <a className="btn btn-sm btn-ghost" href={apiUrl(`/api/incidents/${encodeURIComponent(iid!)}/evidence/${ev.id}`)} download>Download</a>
                      <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDeleteEvidence(ev.id)}>Delete</button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <input ref={fileRef} type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.png,.jpg,.jpeg,.txt,.md,.json,.log" />
              <input placeholder="Label (optional)" value={evidenceLabel} onChange={(e) => setEvidenceLabel(e.target.value)} style={{ width: 140, fontSize: 12 }} />
              <button className="btn btn-sm btn-primary" onClick={handleEvidenceUpload}>Upload</button>
            </div>
          </div>
        </div>
      )}

      {tab === "reports" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="panel">
            <div className="panel-header"><strong>Regulatory Reports</strong></div>
            <div className="panel-body">
              {(inc.regulatory_reports || []).length === 0 && <p className="muted" style={{ fontSize: 12 }}>No regulatory reports.</p>}
              {(inc.regulatory_reports || []).map((r) => (
                <div key={r.id} style={{ padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 13 }}>
                  <strong>{r.report_type?.charAt(0).toUpperCase() + r.report_type?.slice(1)} Report</strong>
                  <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>
                    {r.submitted_to && <>Submitted to {r.submitted_to} · </>}
                    Created {fmtDate(r.created_at)}
                    {r.submitted_at && <> · Submitted {fmtDate(r.submitted_at)}</>}
                  </div>
                  {r.content && <p style={{ fontSize: 12, marginTop: 4, whiteSpace: "pre-wrap" }}>{r.content}</p>}
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-header"><strong>Create Report</strong></div>
            <div className="panel-body">
              <div className="form-grid">
                <div><label className="muted" style={{ fontSize: 11 }}>Type</label><select value={reportForm.report_type} onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}><option value="initial">Initial</option><option value="supplemental">Supplemental</option><option value="final">Final</option></select></div>
                <div><label className="muted" style={{ fontSize: 11 }}>Submit To</label><input value={reportForm.submitted_to} onChange={(e) => setReportForm({ ...reportForm, submitted_to: e.target.value })} placeholder="Authority name" /></div>
                <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Content</label><textarea rows={4} value={reportForm.content} onChange={(e) => setReportForm({ ...reportForm, content: e.target.value })} /></div>
              </div>
              <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} onClick={createReport} disabled={!reportForm.submitted_to}>Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
