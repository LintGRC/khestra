import { useEffect, useRef, useState } from "react";
import { useParams, NavLink } from "react-router-dom";
import { vendorApi, detectFrameworkId, vendorTerm } from "../api";
import type { VendorItem, VendorRemediation, VendorActivity } from "../types";

const FW_COLORS: Record<string, string> = {
  SOC2: "#2563eb", AIGov: "#7c3aed", CMMC: "#059669",
};

function statusBadge(status: string) {
  const m: Record<string, string> = {
    pending: "badge-muted",
    sent: "badge-warning",
    responded: "badge-info",
    assessed: "badge-warning",
    approved: "badge-success",
    rejected: "badge-danger",
    under_review: "badge-warning",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace(/_/g, " ")}</span>;
}

export default function VendorDetail() {
  const { id } = useParams<{ id: string }>();
  const [vendor, setVendor] = useState<VendorItem | null>(null);
  const [tab, setTab] = useState("overview");
  const [assessments, setAssessments] = useState<{ area: string; score: number; finding: string }[]>([]);
  const [fullAssessment, setFullAssessment] = useState<any>(null);
  const [findings, setFindings] = useState<any[]>([]);
  const [remediations, setRemediations] = useState<VendorRemediation[]>([]);
  const [runningAssess, setRunningAssess] = useState(false);
  const [activityLog, setActivityLog] = useState<VendorActivity[]>([]);
  const [magicLink, setMagicLink] = useState<string | null>(null);
  const [sendingQ, setSendingQ] = useState(false);
  const [remediationText, setRemediationText] = useState("");
  const [savingQ, setSavingQ] = useState(false);
  const [linking, setLinking] = useState<string | null>(null);
  const certInputRef = useRef<HTMLInputElement>(null);
  const currentFw = detectFrameworkId();

  const [questionnaire, setQuestionnaire] = useState<Record<string, any>>({
    data_governance: false,
    bias_testing: false,
    explainability: false,
    security: false,
    incident_response: false,
    human_oversight: false,
    data_retention: "",
    training_data: "",
    third_party_data: "",
  });

  useEffect(() => {
    if (!id) return;
    loadVendor();
    loadAssessments();
    loadRemediations();
    loadActivity();
  }, [id]);

  async function loadVendor() {
    try {
      const { vendor: v } = await vendorApi.get(id!);
      setVendor(v);
    } catch (err) {
      console.error(err);
    }
  }

  async function loadAssessments() {
    try {
      const { assessment } = await vendorApi.assessment(id!);
      if (assessment) {
        setFullAssessment(assessment);
        setFindings(assessment.findings || []);
        const cs: any = assessment.category_scores;
        const scores = Array.isArray(cs) ? cs : Object.entries(cs || {}).map(([cat, score]: [string, any]) => ({
          category: cat,
          score: typeof score === 'number' ? score : 0,
          finding: score >= 80 ? 'low' : score >= 60 ? 'medium' : score >= 40 ? 'high' : 'critical',
        }));
        setAssessments(
          scores.map((s: any) => ({
            area: s.category,
            score: s.score,
            finding: s.finding,
          })) || [],
        );
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function loadRemediations() {
    try {
      const { remediations: r } = await vendorApi.remediations(id!);
      setRemediations(r || []);
    } catch (err) {
      console.error(err);
    }
  }

  async function loadActivity() {
    try {
      const { activities: a } = await vendorApi.activity(id!);
      setActivityLog(a || []);
    } catch (err) {
      console.error(err);
    }
  }

  async function saveQuestionnaire() {
    setSavingQ(true);
    try {
      await vendorApi.saveDraft(
        id!,
        Object.entries(questionnaire).map(([k, v]) => ({ questionId: k, value: v })),
      );
    } catch (err) {
      console.error(err);
    } finally {
      setSavingQ(false);
    }
  }

  async function addAssessment() {
    setRunningAssess(true);
    try {
      await vendorApi.runAssessment(id!);
      await loadVendor();
      await loadAssessments();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningAssess(false);
    }
  }

  async function addRemediation() {
    if (!remediationText.trim()) return;
    try {
      const dueDate = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
      await vendorApi.createRemediation(id!, {
        description: remediationText.trim(),
        owner: "Admin",
        due_date: dueDate,
        assessment_id: "",
      });
      setRemediationText("");
      await loadRemediations();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleStatus(status: string) {
    if (!vendor) return;
    try {
      await vendorApi.update(id!, { status: status as any });
      await loadVendor();
      await loadActivity();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleSendQuestionnaire() {
    if (!id) return;
    setSendingQ(true);
    try {
      const res = await vendorApi.sendQuestionnaire(id);
      if (res.link) setMagicLink(res.link);
      const { vendor: v } = await vendorApi.get(id);
      setVendor(v);
    } catch (err) {
      console.error(err);
    }
    setSendingQ(false);
  }

  async function handleLinkFramework(fw: string) {
    if (!id) return;
    setLinking(fw);
    try {
      await vendorApi.linkFramework(id, fw);
      await loadVendor();
    } catch (err) {
      console.error(err);
    } finally {
      setLinking(null);
    }
  }

  async function handleUnlinkFramework(fw: string) {
    if (!id) return;
    setLinking(fw);
    try {
      await vendorApi.unlinkFramework(id, fw);
      await loadVendor();
    } catch (err) {
      console.error(err);
    } finally {
      setLinking(null);
    }
  }

  async function handleCertUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !id) return;
    try {
      await vendorApi.uploadCert(id, file);
      await loadVendor();
    } catch (err) {
      console.error(err);
    }
    e.target.value = "";
  }

  if (!vendor) {
    return <div className="page-stack"><p className="muted" style={{ padding: 24 }}>Loading vendor...</p></div>;
  }

  if (vendor && !vendor.name) {
    return <div className="page-stack"><div className="banner error">{vendorTerm()} not found</div></div>;
  }

  const tabs = ["overview", "assessment", "remediation", "activity"];

  return (
    <>
      <NavLink
        to=".."
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 4,
          fontSize: 12,
          color: "var(--muted)",
          textDecoration: "none",
          marginBottom: 12,
        }}
      >
        ← Back
      </NavLink>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "1rem",
        }}
      >
        <div>
          <h2 style={{ margin: "0 0 4px" }}>{vendor.name}</h2>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {statusBadge(vendor.status)}
            <span className="muted" style={{ fontSize: 12 }}>
              {vendor.category?.replace(/_/g, " ")} · {vendor.ai_service_type}
            </span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, flexDirection: "column", alignItems: "flex-end" }}>
          <div style={{ display: "flex", gap: 8 }}>
            {(vendor.status === "pending" || vendor.status === "sent") && (
              <button
                onClick={handleSendQuestionnaire}
                className="btn btn-primary btn-sm"
                disabled={sendingQ}
              >
                {sendingQ ? "Sending..." : "Send Questionnaire"}
              </button>
            )}
            {(vendor.status === "pending" || vendor.status === "sent" || vendor.status === "responded" || vendor.status === "assessed") && (
              <>
                <button
                  onClick={() => handleStatus("approved")}
                  className="btn btn-primary btn-sm"
                  style={{ background: "var(--success)" }}
                >
                  Approve
                </button>
                <button
                  onClick={() => handleStatus("rejected")}
                  className="btn btn-primary btn-sm"
                  style={{ background: "var(--danger)" }}
                >
                  Reject
                </button>
              </>
            )}
          </div>
          {magicLink && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 11,
                background: "var(--info-soft)",
                padding: "6px 10px",
                borderRadius: "var(--radius)",
                maxWidth: 400,
              }}
            >
              <span
                style={{
                  flex: 1,
                  minWidth: 0,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {window.location.origin}{magicLink}
              </span>
              <button
                className="btn btn-secondary btn-sm"
                style={{ fontSize: 10, flexShrink: 0 }}
                onClick={() =>
                  navigator.clipboard.writeText(`${window.location.origin}${magicLink}`)
                }
              >
                Copy
              </button>
            </div>
          )}
        </div>
      </div>

      <div style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--border)", marginBottom: "1rem" }}>
        {tabs.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: "8px 16px",
              border: "none",
              background: "none",
              cursor: "pointer",
              fontSize: 13,
              fontWeight: tab === t ? 600 : 400,
              color: tab === t ? "var(--primary)" : "var(--muted)",
              borderBottom: tab === t ? "2px solid var(--primary)" : "2px solid transparent",
              marginBottom: -1,
              transition: "color 0.15s, border-color 0.15s",
            }}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="panel-stack" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Vendor Info</strong>
            </div>
            <div style={{ fontSize: 12, lineHeight: 1.8 }}>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Category</span>
                {vendor.category?.replace(/_/g, " ") || "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>AI Service Type</span>
                {vendor.ai_service_type || "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Tier</span>
                {vendor.tier || "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Risk Score</span>
                {vendor.risk_score ?? "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Contact</span>
                {vendor.contact_email || vendor.contact_name || "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Created</span>
                {vendor.created_at?.slice(0, 10)}
              </div>
              <div style={{ marginTop: 8, display: "flex", gap: 4, flexWrap: "wrap" }}>
                {(vendor.frameworks || []).map((fw) => (
                  <span
                    key={fw}
                    style={{
                      fontSize: 10,
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: "var(--radius)",
                      color: "#fff",
                      background: FW_COLORS[fw] || "var(--muted)",
                    }}
                  >
                    {fw}
                  </span>
                ))}
                {currentFw && !(vendor.frameworks || []).includes(currentFw) && (
                  <button
                    className="btn btn-sm btn-ghost"
                    style={{ fontSize: 10 }}
                    onClick={() => handleLinkFramework(currentFw)}
                    disabled={linking === currentFw}
                  >
                    {linking === currentFw ? "..." : `+ Link to ${currentFw}`}
                  </button>
                )}
                {currentFw && (vendor.frameworks || []).includes(currentFw) && (
                  <button
                    className="btn btn-sm btn-ghost"
                    style={{ fontSize: 10, color: "var(--danger)" }}
                    onClick={() => handleUnlinkFramework(currentFw)}
                    disabled={linking === currentFw}
                  >
                    {linking === currentFw ? "..." : `Unlink ${currentFw}`}
                  </button>
                )}
              </div>
            </div>
          </div>
          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Cross-Border</strong>
            </div>
            <div style={{ fontSize: 12, lineHeight: 1.8 }}>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Data Residency</span>
                {(vendor.data_residency || []).join(", ") || "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>Transfer Mechanism</span>
                {vendor.transfer_mechanism || "-"}
              </div>
              <div>
                <span className="muted" style={{ width: 120, display: "inline-block" }}>DPA in Place</span>
                {vendor.dpa_in_place ? "Yes" : "No"}
              </div>
            </div>
          </div>

          {detectFrameworkId() === "CMMC" && (
            <div className="panel" style={{ padding: 16 }}>
              <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
                <strong>CMMC / NIST 800-171</strong>
              </div>
              <div style={{ fontSize: 12, lineHeight: 1.8 }}>
                <div>
                  <span className="muted" style={{ width: 120, display: "inline-block" }}>Handles CUI</span>
                  {vendor.handles_cui ? "Yes" : "No"}
                </div>
                <div>
                  <span className="muted" style={{ width: 120, display: "inline-block" }}>CMMC Level</span>
                  {vendor.cmmc_level ? `Level ${vendor.cmmc_level}` : "-"}
                </div>
                <div>
                  <span className="muted" style={{ width: 120, display: "inline-block" }}>SPRS Score</span>
                  {vendor.sprs_score != null ? vendor.sprs_score : "-"}
                </div>
                <div>
                  <span className="muted" style={{ width: 120, display: "inline-block" }}>Flow-down Clause</span>
                  {vendor.flow_down_clause_signed || "-"}
                </div>
                <div>
                  <span className="muted" style={{ width: 120, display: "inline-block" }}>CUI Categories</span>
                  {(vendor.cui_categories || []).join(", ") || "-"}
                </div>
                <div>
                  <span className="muted" style={{ width: 120, display: "inline-block" }}>Last Assessment</span>
                  {vendor.last_assessment_date?.slice(0, 10) || "-"}
                </div>
              </div>
            </div>
          )}

          {detectFrameworkId() === "SOC2" && (
            <div className="panel" style={{ padding: 16 }}>
              <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
                <strong>SOC 2 Vendor Fields</strong>
              </div>
              <div style={{ fontSize: 12, lineHeight: 1.8, display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 16px" }}>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>SOC Report Type</span>
                  <select value={vendor.soc_report_type || ""} onChange={e => { const v = { ...vendor, soc_report_type: e.target.value }; setVendor(v); vendorApi.update(id!, { soc_report_type: e.target.value }); }} style={{ fontSize: 11, width: "100%" }}>
                    <option value="">—</option>
                    <option value="SOC 2 Type I">SOC 2 Type I</option>
                    <option value="SOC 2 Type II">SOC 2 Type II</option>
                    <option value="SOC 3">SOC 3</option>
                    <option value="SOC 1 Type I">SOC 1 Type I</option>
                    <option value="SOC 1 Type II">SOC 1 Type II</option>
                  </select>
                </div>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>Opinion</span>
                  <select value={vendor.soc_report_opinion || ""} onChange={e => { vendorApi.update(id!, { soc_report_opinion: e.target.value }); }} style={{ fontSize: 11, width: "100%" }}>
                    <option value="">—</option>
                    <option value="Unqualified">Unqualified (Clean)</option>
                    <option value="Qualified">Qualified</option>
                    <option value="Adverse">Adverse</option>
                    <option value="Disclaimer">Disclaimer</option>
                  </select>
                </div>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>Coverage Start</span>
                  <input type="date" value={vendor.soc_report_coverage_start?.slice(0, 10) || ""} onChange={e => { vendorApi.update(id!, { soc_report_coverage_start: e.target.value }); }} style={{ fontSize: 11, width: "100%" }} />
                </div>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>Coverage End</span>
                  <input type="date" value={vendor.soc_report_coverage_end?.slice(0, 10) || ""} onChange={e => { vendorApi.update(id!, { soc_report_coverage_end: e.target.value }); }} style={{ fontSize: 11, width: "100%" }} />
                </div>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>SOC Report Date</span>
                  <input type="date" value={vendor.soc_report_date?.slice(0, 10) || ""} onChange={e => { vendorApi.update(id!, { soc_report_date: e.target.value }); }} style={{ fontSize: 11, width: "100%" }} />
                </div>
                <div style={{ position: "relative" }}>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>Next Review Due</span>
                  <input type="date" value={vendor.next_review_due?.slice(0, 10) || ""} onChange={e => { vendorApi.update(id!, { next_review_due: e.target.value }); }} style={{ fontSize: 11, width: "100%" }} />
                  {vendor.next_review_due && (() => { const d = new Date(vendor.next_review_due); const n = new Date(); const days = Math.round((d.getTime() - n.getTime()) / 86400000); return days < 0 ? <span style={{ position: "absolute", right: 0, top: 0, fontSize: 9, color: "var(--danger)", fontWeight: 600 }}>OVERDUE</span> : days <= 30 ? <span style={{ position: "absolute", right: 0, top: 0, fontSize: 9, color: "var(--warning)", fontWeight: 600 }}>{days}d</span> : null; })()}
                </div>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>Last Review Date</span>
                  <input type="date" value={vendor.review_date?.slice(0, 10) || ""} onChange={e => { vendorApi.update(id!, { review_date: e.target.value }); }} style={{ fontSize: 11, width: "100%" }} />
                </div>
                <div>
                  <span className="muted" style={{ display: "block", marginBottom: 2 }}>Data Types Handled</span>
                  <input value={(vendor.data_types || []).join(", ")} onChange={e => { vendorApi.update(id!, { data_types: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }); }} placeholder="Comma-separated" style={{ fontSize: 11, width: "100%" }} />
                </div>
              </div>
            </div>
          )}

          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Certs ({vendor.certificates?.length || 0})</strong>
            </div>
            {vendor.certificates?.map((c) => (
              <div
                key={c.id}
                style={{
                  fontSize: 12,
                  padding: "4px 0",
                  borderBottom: "1px solid var(--border-subtle)",
                }}
              >
                <span style={{ fontWeight: 500 }}>{c.filename}</span>
                <div className="muted">
                  {c.type} · uploaded {c.uploaded_at?.slice(0, 10)}
                </div>
              </div>
            ))}
            {(!vendor.certificates || vendor.certificates.length === 0) && (
              <p className="muted" style={{ fontSize: 12 }}>No certs.</p>
            )}
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => certInputRef.current?.click()}
              style={{ marginTop: 8 }}
            >
              Upload Cert
            </button>
            <input
              ref={certInputRef}
              type="file"
              hidden
              onChange={handleCertUpload}
            />
          </div>

          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Questionnaire Summary</strong>
            </div>
            <div style={{ fontSize: 12, lineHeight: 1.8 }}>
              <div>
                <span className="muted" style={{ width: 130, display: "inline-block" }}>Data Governance</span>
                {questionnaire.data_governance ? "Yes" : "No"}
              </div>
              <div>
                <span className="muted" style={{ width: 130, display: "inline-block" }}>Bias Testing</span>
                {questionnaire.bias_testing ? "Yes" : "No"}
              </div>
              <div>
                <span className="muted" style={{ width: 130, display: "inline-block" }}>Explainability</span>
                {questionnaire.explainability ? "Yes" : "No"}
              </div>
              <div>
                <span className="muted" style={{ width: 130, display: "inline-block" }}>Security</span>
                {questionnaire.security ? "Yes" : "No"}
              </div>
              <div>
                <span className="muted" style={{ width: 130, display: "inline-block" }}>Incident Response</span>
                {questionnaire.incident_response ? "Yes" : "No"}
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === "assessment" && (
        <div className="panel-stack" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Questionnaire</strong>
            </div>
            <div className="form-grid" style={{ fontSize: 12 }}>
              {Object.entries({
                data_governance: "Data Governance",
                bias_testing: "Bias Testing",
                explainability: "Explainability",
                security: "Security",
                incident_response: "Incident Response",
                human_oversight: "Human Oversight",
              }).map(([k, label]) => (
                <label
                  key={k}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    cursor: "pointer",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={questionnaire[k]}
                    onChange={(e) =>
                      setQuestionnaire((q: any) => ({ ...q, [k]: e.target.checked }))
                    }
                    style={{ width: "auto" }}
                  />
                  {label}
                </label>
              ))}
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Data Retention Policy</label>
                <input
                  value={questionnaire.data_retention}
                  onChange={(e) =>
                    setQuestionnaire((q: any) => ({ ...q, data_retention: e.target.value }))
                  }
                />
              </div>
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Training Data Sources</label>
                <input
                  value={questionnaire.training_data}
                  onChange={(e) =>
                    setQuestionnaire((q: any) => ({ ...q, training_data: e.target.value }))
                  }
                />
              </div>
              <div className="span-2">
                <label className="muted" style={{ fontSize: 11 }}>Third-Party Data</label>
                <input
                  value={questionnaire.third_party_data}
                  onChange={(e) =>
                    setQuestionnaire((q: any) => ({ ...q, third_party_data: e.target.value }))
                  }
                />
              </div>
            </div>
            <button
              onClick={saveQuestionnaire}
              className="btn btn-primary"
              style={{ marginTop: 12 }}
              disabled={savingQ}
            >
              {savingQ ? "Saving..." : "Save"}
            </button>
          </div>
          <div className="panel" style={{ padding: 16 }}>
            <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
              <strong>Assessment Results</strong>
            </div>
            {!fullAssessment ? (
              <>
                <p className="muted" style={{ fontSize: 12, marginBottom: 12 }}>No assessment yet. Submit the questionnaire first, then run an assessment.</p>
                <button onClick={addAssessment} className="btn btn-secondary btn-sm" disabled={runningAssess}>
                  {runningAssess ? "Running..." : "Run Assessment"}
                </button>
              </>
            ) : (
              <>
                <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "2.5rem", fontWeight: 700, color: fullAssessment.overall_score >= 80 ? "var(--success)" : fullAssessment.overall_score >= 60 ? "var(--warning)" : "var(--danger)" }}>
                      {fullAssessment.overall_score}
                    </div>
                    <div className="muted" style={{ fontSize: 11 }}>Overall Score</div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ height: 12, background: "var(--border)", borderRadius: 6, overflow: "hidden", marginBottom: 4 }}>
                      <div style={{ height: "100%", width: `${fullAssessment.overall_score}%`, background: fullAssessment.overall_score >= 80 ? "var(--success)" : fullAssessment.overall_score >= 60 ? "var(--warning)" : "var(--danger)", borderRadius: 6 }} />
                    </div>
                    <span className={`badge ${fullAssessment.overall_level === "low" ? "badge-success" : fullAssessment.overall_level === "medium" ? "badge-warning" : "badge-danger"}`} style={{ textTransform: "capitalize" }}>
                      {fullAssessment.overall_level}
                    </span>
                  </div>
                </div>

                {fullAssessment.summary && (
                  <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 16, padding: 8, background: "var(--surface-muted, rgba(0,0,0,0.03))", borderRadius: "var(--radius)" }}>
                    {fullAssessment.summary}
                  </div>
                )}

                {assessments.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div className="muted" style={{ fontSize: 11, marginBottom: 8 }}>CATEGORY SCORES</div>
                    {assessments.map((a, i) => (
                      <div key={i} style={{ marginBottom: 8 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 2 }}>
                          <span>{a.area.replace(/_/g, " ")}</span>
                          <span style={{ fontWeight: 600 }}>{a.score}/100</span>
                        </div>
                        <div style={{ height: 6, background: "var(--border)", borderRadius: 3, overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${a.score}%`, background: a.score >= 80 ? "var(--success)" : a.score >= 60 ? "var(--warning)" : "var(--danger)", borderRadius: 3 }} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {findings.length > 0 && (
                  <div>
                    <div className="muted" style={{ fontSize: 11, marginBottom: 8 }}>FINDINGS ({findings.length})</div>
                    {findings.map((f: any, i: number) => (
                      <div key={i} style={{ fontSize: 12, padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                          <span style={{ color: f.severity === "high" || f.severity === "critical" ? "var(--danger)" : "var(--warning)", fontSize: 14 }}>⚠</span>
                          <span className={`badge ${f.severity === "critical" ? "badge-danger" : f.severity === "high" ? "badge-danger" : f.severity === "medium" ? "badge-warning" : "badge-muted"}`} style={{ textTransform: "capitalize", fontSize: 10 }}>{f.severity}</span>
                          <span style={{ fontWeight: 500 }}>{f.description || f.finding || ""}</span>
                        </div>
                        {f.recommendation && <div className="muted" style={{ marginLeft: 24, fontSize: 11 }}>{f.recommendation}</div>}
                        {f.issue && <div className="muted" style={{ marginLeft: 24, fontSize: 11 }}>{f.issue}{f.matches ? ` (matched: ${f.matches.join(", ")})` : ""}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {tab === "remediation" && (
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
            <strong>Remediation Items</strong>
          </div>
          {remediations.length === 0 && (
            <p className="muted" style={{ fontSize: 12 }}>No remediation items.</p>
          )}
          {remediations.map((r) => (
            <div
              key={r.id}
              style={{
                fontSize: 12,
                padding: "8px 0",
                borderBottom: "1px solid var(--border-subtle)",
              }}
            >
              <div style={{ fontWeight: 500 }}>{r.description}</div>
              <div className="muted">
                Owner: {r.owner} · Due: {r.due_date?.slice(0, 10)} ·{" "}
                <span
                  className={`badge ${r.status === "closed" || r.status === "resolved" ? "badge-success" : "badge-warning"}`}
                  style={{ fontSize: 10 }}
                >
                  {r.status}
                </span>
              </div>
            </div>
          ))}
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <input
              value={remediationText}
              onChange={(e) => setRemediationText(e.target.value)}
              placeholder="New remediation..."
              style={{ flex: 1 }}
            />
            <button onClick={addRemediation} className="btn btn-secondary btn-sm">
              Add
            </button>
          </div>
        </div>
      )}

      {tab === "activity" && (
        <div className="panel" style={{ padding: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}>
            <strong>Activity Log</strong>
          </div>
          {activityLog.length === 0 && (
            <p className="muted" style={{ fontSize: 12 }}>No activity recorded.</p>
          )}
          {activityLog.map((a) => (
            <div
              key={a.id}
              style={{
                fontSize: 11,
                padding: "4px 0",
                borderBottom: "1px solid var(--border-subtle)",
              }}
            >
              <span style={{ fontWeight: 500 }}>{a.action}</span>{" "}
              {(a as any).detail || (a as any).notes || ""}
              <span className="muted">
                {" "}
                · {(a as any).performed_by || "system"} ·{" "}
                {(a.timestamp || (a as any).created_at)?.slice(0, 16).replace("T", " ")}
              </span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
