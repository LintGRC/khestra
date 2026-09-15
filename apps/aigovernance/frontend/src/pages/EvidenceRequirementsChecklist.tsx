import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { CheckCircle, Circle, AlertTriangle, Upload } from "lucide-react";
import { apiUrl } from "@shared/apiPrefix";
import { displayClause } from "@shared/refs/format";

const FRAMEWORK_LABELS: Record<string, string> = {
  eu_ai_act: "EU AI Act",
  nist_ai_rmf: "NIST AI RMF",
  iso_42001: "ISO 42001",
  owasp_agentic: "OWASP Agentic",
  owasp_llm: "OWASP LLM",
};

type ArtifactType = "structured" | "evidence_upload" | "external";

type ArtifactItem = {
  id: string;
  name: string;
  refs: string;
  type: ArtifactType;
  controlId?: string;
  guidance: string;
  actionLabel: string;
  actionLink: string;
};

type EvidenceMapping = {
  framework_id: string;
  control_id: string;
};

type EvidenceItem = {
  id: string;
  mappings: EvidenceMapping[];
};

const FRAMEWORK_ARTIFACTS: Record<string, ArtifactItem[]> = {
  eu_ai_act: [
    { id: "eu-tech-doc", name: "Technical Documentation Package", refs: "Art. 11, 18", type: "evidence_upload", controlId: "EU-11", guidance: "Upload system design docs, development methodology, training data specs, accuracy/robustness metrics.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-rm-docs", name: "Risk Management Documentation", refs: "Art. 9", type: "evidence_upload", controlId: "EU-9", guidance: "Upload risk identification, analysis, evaluation, and mitigation records for the AI system.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-data-gov", name: "Data Governance Documentation", refs: "Art. 10", type: "evidence_upload", controlId: "EU-10", guidance: "Upload data provenance, bias detection, and data quality assessment records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-human-oversight", name: "Human Oversight Design Documentation", refs: "Art. 14", type: "evidence_upload", controlId: "EU-14", guidance: "Upload human-machine interface design docs, override procedures, and operator training materials.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-logs", name: "Automated Logs / Record-Keeping", refs: "Art. 12", type: "evidence_upload", guidance: "Upload system activity logs, event logs, and audit trails demonstrating record-keeping compliance.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-transparency", name: "Transparency Notices / User Information", refs: "Art. 13, 50", type: "evidence_upload", guidance: "Upload transparency notices, user-facing documentation explaining system purpose, limitations, and risks.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-conformity", name: "Conformity Assessment Report", refs: "Art. 19, Annex VI", type: "evidence_upload", guidance: "Upload the EU Declaration of Conformity or the conformity assessment report.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-eu-db", name: "EU Database Registration Confirmation", refs: "Art. 71", type: "evidence_upload", guidance: "Upload the confirmation email/document from the EU AI system registration database.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-pm-monitoring", name: "Post-Market Monitoring Reports", refs: "Art. 61", type: "evidence_upload", guidance: "Upload post-market monitoring plans and periodic monitoring reports.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-qms", name: "Quality Management System Records", refs: "Art. 17", type: "evidence_upload", guidance: "Upload QMS documentation including quality procedures, review records, and audit results.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-literacy", name: "AI Literacy Training Records", refs: "Art. 4", type: "evidence_upload", guidance: "Upload training completion records, attendance sheets, and training materials for AI literacy.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "eu-incident", name: "Serious Incident Reports", refs: "Art. 21, 73", type: "structured", guidance: "Incidents are tracked as structured objects in the Incidents module.", actionLabel: "View Incidents", actionLink: "/aigov/incidents" },
    { id: "eu-fria", name: "Fundamental Rights Impact Assessment", refs: "Art. 27", type: "structured", guidance: "FRIAs are created and managed in the FRIA module.", actionLabel: "View FRIAs", actionLink: "/aigov/frias" },
  ],
  nist_ai_rmf: [
    { id: "nist-impact", name: "AI Impact Assessments", refs: "MAP 2.4", type: "evidence_upload", guidance: "Upload impact assessments including intended purpose, use context, and stakeholder impact analysis.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "nist-gov-minutes", name: "AI Governance Committee Minutes", refs: "GOVERN 1.1, 1.5", type: "evidence_upload", guidance: "Upload meeting minutes, attendance records, and decisions from AI governance committee meetings.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "nist-incident-exercise", name: "Incident Response Exercise Records", refs: "MANAGE 4.1", type: "evidence_upload", guidance: "Upload incident response test plans, exercise reports, and lessons learned.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "nist-docs-repo", name: "AI Documentation Repository Evidence", refs: "MANAGE 5.5", type: "evidence_upload", guidance: "Upload documentation inventory, version control records, and documentation review evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "nist-change-mgmt", name: "Change Management Records", refs: "MANAGE 4.4", type: "evidence_upload", guidance: "Upload change requests, approval records, deployment logs, and rollback procedures.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "nist-logging", name: "Automated Logging & Monitoring Records", refs: "MEASURE 3.6", type: "evidence_upload", guidance: "Upload system monitoring dashboards, alert configurations, and log retention policies.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "nist-third-party", name: "Third-Party AI Risk Assessments", refs: "MAP 2.5", type: "structured", guidance: "Third-party AI vendors are tracked in the Vendor Management module.", actionLabel: "View Vendors", actionLink: "/aigov/vendors" },
    { id: "nist-continuous", name: "Continuous Improvement Review Records", refs: "MANAGE 4.3", type: "structured", guidance: "Review cycles are tracked in the Review Cycles module.", actionLabel: "View Review Cycles", actionLink: "/aigov/review-cycles" },
  ],
  iso_42001: [
    { id: "iso-context", name: "Context & Interested Parties Analysis", refs: "4.1, 4.2", type: "evidence_upload", guidance: "Upload analysis of external/internal context, interested party requirements, and scope justification.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-objectives", name: "AI Objectives & Metrics Records", refs: "6.2", type: "evidence_upload", guidance: "Upload AI objectives register, measurable targets, and performance metrics tracking.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-competence", name: "Competence & Training Records", refs: "7.2, 7.3", type: "evidence_upload", guidance: "Upload training records, competence assessments, certification evidence, and skills matrices.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-operational", name: "AI Operational Control Records", refs: "8.1", type: "evidence_upload", guidance: "Upload operational procedures, runbooks, shift handover logs, and operational checklists.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-monitoring", name: "AI System Monitoring & Performance Data", refs: "9.1, A.6", type: "evidence_upload", guidance: "Upload monitoring dashboards, performance reports, drift detection logs, and alert histories.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-continual", name: "Continual Improvement Evidence", refs: "10.1, 10.2", type: "evidence_upload", guidance: "Upload improvement plans, corrective action records, and effectiveness reviews.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-resource", name: "AI Resource Allocation Records", refs: "7.1", type: "evidence_upload", guidance: "Upload resource budgets, staffing plans, infrastructure allocation, and capacity planning docs.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-communication", name: "Communication Records (AI)", refs: "7.4", type: "evidence_upload", guidance: "Upload internal/external AI communications, stakeholder notifications, and reporting records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "iso-audit", name: "Internal Audit Reports (AI)", refs: "9.2", type: "structured", guidance: "Internal audits are tracked as Evaluation objects with type 'internal_audit'.", actionLabel: "View Evaluations", actionLink: "/aigov/evaluations" },
    { id: "iso-mgmt-review", name: "Management Review Minutes", refs: "9.3", type: "structured", guidance: "Management reviews are tracked in the Review Cycles module.", actionLabel: "View Review Cycles", actionLink: "/aigov/review-cycles" },
  ],
  owasp_agentic: [
    { id: "owasp-goal-hijack", name: "Goal Hijack Controls & Incident Evidence", refs: "ASI01", type: "evidence_upload", controlId: "OWASP-1", guidance: "Upload prompt-injection defenses, input sanitization evidence, and any goal-hijack incident records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-tool-misuse", name: "Tool Governance & Misuse Evidence", refs: "ASI02", type: "evidence_upload", controlId: "OWASP-2", guidance: "Upload tool allow-lists, permission reviews, and evidence of safe tool invocation patterns.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-identity", name: "Agent Identity & Privilege Controls", refs: "ASI03", type: "evidence_upload", controlId: "OWASP-3", guidance: "Upload agent identity documentation, delegation-chain reviews, and privilege-scope records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-supply-chain", name: "Agentic Supply Chain Records", refs: "ASI04", type: "evidence_upload", controlId: "OWASP-4", guidance: "Upload SBOMs, model/tool provenance records, and third-party agent dependency reviews.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-code-exec", name: "Code Execution Guard Evidence", refs: "ASI05", type: "evidence_upload", controlId: "OWASP-5", guidance: "Upload sandboxing, code-execution review, and runtime isolation documentation.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-memory-poisoning", name: "Memory & Context Integrity Evidence", refs: "ASI06", type: "evidence_upload", controlId: "OWASP-6", guidance: "Upload memory-store validation, context-integrity checks, and poisoning-detection records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-inter-agent", name: "Inter-Agent Communication Security", refs: "ASI07", type: "evidence_upload", controlId: "OWASP-7", guidance: "Upload message authentication, encryption, and inter-agent trust-verification evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-cascading", name: "Cascading Failure & Blast-Radius Controls", refs: "ASI08", type: "evidence_upload", controlId: "OWASP-8", guidance: "Upload circuit-breaker, rate-limit, and cascade-recovery documentation and tests.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-human-trust", name: "Human-Agent Trust Safeguards", refs: "ASI09", type: "evidence_upload", controlId: "OWASP-9", guidance: "Upload human-approval workflows, explainability reviews, and over-reliance mitigations.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "owasp-rogue-agents", name: "Rogue Agent Monitoring & Containment", refs: "ASI10", type: "evidence_upload", controlId: "OWASP-10", guidance: "Upload behavior monitoring, quarantine, and kill-switch procedure evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
  ],
  owasp_llm: [
    { id: "llm-prompt-injection", name: "Prompt Injection Defenses", refs: "LLM01:2025", type: "evidence_upload", controlId: "OWASP-LLM-1", guidance: "Upload prompt-injection testing results, input filtering rules, and adversarial test evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-info-disclosure", name: "Sensitive Information Disclosure Controls", refs: "LLM02:2025", type: "evidence_upload", controlId: "OWASP-LLM-2", guidance: "Upload data sanitization evidence, output filtering rules, and disclosure testing records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-supply-chain", name: "LLM Supply Chain Records", refs: "LLM03:2025", type: "evidence_upload", controlId: "OWASP-LLM-3", guidance: "Upload model provenance, dependency SBOMs, and third-party model review evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-data-poisoning", name: "Data & Model Poisoning Defenses", refs: "LLM04:2025", type: "evidence_upload", controlId: "OWASP-LLM-4", guidance: "Upload training-data integrity checks, poisoning detection, and supply-chain validation records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-output-handling", name: "Output Handling & Validation", refs: "LLM05:2025", type: "evidence_upload", controlId: "OWASP-LLM-5", guidance: "Upload output validation, sanitization, and encoding policies and test evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-excessive-agency", name: "Excessive Agency Controls", refs: "LLM06:2025", type: "evidence_upload", controlId: "OWASP-LLM-6", guidance: "Upload agent permission scopes, tool allow-lists, and function-call authorization reviews.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-prompt-leakage", name: "System Prompt Leakage Testing", refs: "LLM07:2025", type: "evidence_upload", controlId: "OWASP-LLM-7", guidance: "Upload system prompt design, sensitive-data audit, and leakage testing records.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-vector-embedding", name: "Vector & Embedding Security", refs: "LLM08:2025", type: "evidence_upload", controlId: "OWASP-LLM-8", guidance: "Upload RAG pipeline security reviews, vector store access controls, and embedding poisoning tests.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-misinformation", name: "Misinformation Mitigations", refs: "LLM09:2025", type: "evidence_upload", controlId: "OWASP-LLM-9", guidance: "Upload hallucination testing, groundedness validation, and content verification processes.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
    { id: "llm-unbounded", name: "Unbounded Consumption Controls", refs: "LLM10:2025", type: "evidence_upload", controlId: "OWASP-LLM-10", guidance: "Upload rate limiting, quota enforcement, and resource usage monitoring evidence.", actionLabel: "Upload to Hub", actionLink: "/aigov/evidence" },
  ],
};

export function EvidenceRequirementsChecklist({ activeTab }: { activeTab: string }) {
  const [evidenceMap, setEvidenceMap] = useState<Set<string>>(new Set());
  const [loadingEvidence, setLoadingEvidence] = useState(true);
  const [requesting, setRequesting] = useState<string | null>(null);

  useEffect(() => {
    fetch(apiUrl("/api/evidence-hub?framework_id=AIGov"))
      .then(r => r.json())
      .then(data => {
        const items: EvidenceItem[] = data.evidence || [];
        const mapped = new Set<string>();
        for (const item of items) {
          for (const m of item.mappings) {
            if (m.framework_id === "AIGov" && m.control_id) {
              mapped.add(m.control_id);
            }
          }
        }
        setEvidenceMap(mapped);
      })
      .catch(() => setEvidenceMap(new Set()))
      .finally(() => setLoadingEvidence(false));
  }, []);

  async function handleCreateRequest(a: ArtifactItem) {
    setRequesting(a.id);
    try {
      await fetch(apiUrl("/api/evidence-hub/requests"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          control_id: a.controlId || "",
          title: a.name,
          description: `Required for ${displayClause(FRAMEWORK_LABELS[activeTab] || "", a.refs)}. ${a.guidance}`,
          assigned_to: "",
          due_date: "",
        }),
      });
    } catch {}
    setRequesting(null);
  }

  const artifacts = FRAMEWORK_ARTIFACTS[activeTab] || [];

  const typeIcon = (t: ArtifactType) => {
    switch (t) {
      case "structured": return <CheckCircle size={14} style={{ color: "var(--info)" }} />;
      case "evidence_upload": return <Upload size={14} style={{ color: "var(--warning)" }} />;
      case "external": return <AlertTriangle size={14} style={{ color: "var(--muted)" }} />;
    }
  };

  const typeLabel = (t: ArtifactType) => {
    switch (t) {
      case "structured": return "Structured";
      case "evidence_upload": return "Upload";
      case "external": return "External";
    }
  };

  const isComplete = (a: ArtifactItem) => {
    if (a.type === "external") return false;
    if (a.type === "structured") return true;
    if (a.type === "evidence_upload" && a.controlId) return evidenceMap.has(a.controlId);
    return false;
  };

  const done = artifacts.filter(isComplete).length;
  const total = artifacts.length;

  return (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ marginBottom: 4 }}>Artifact Requirements Checklist</h3>
      <p className="muted" style={{ fontSize: 12, marginBottom: 12 }}>
        Required evidence artifacts mapped to framework controls. {done}/{total} complete.
        {loadingEvidence && " Checking evidence hub..."}
      </p>

      {artifacts.length === 0 && (
        <p className="muted" style={{ fontSize: 12 }}>No artifact requirements defined for this framework.</p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {artifacts.map(a => {
          const done = isComplete(a);
          return (
            <div key={a.id} className="panel" style={{
              padding: "10px 14px",
              borderLeft: `3px solid ${done ? "var(--success)" : "var(--danger)"}`,
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    {done ? <CheckCircle size={16} style={{ color: "var(--success)", flexShrink: 0 }} /> : <Circle size={16} style={{ color: "var(--danger)", flexShrink: 0 }} />}
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{a.name}</span>
                    <span className="muted" style={{ fontSize: 10, fontFamily: "monospace" }}>{displayClause(FRAMEWORK_LABELS[activeTab] || "", a.refs)}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                    <span className="badge" style={{
                      background: a.type === "structured" ? "var(--info-soft, #e0f2fe)" : a.type === "evidence_upload" ? "var(--warning-soft, #fef3c7)" : "var(--surface)",
                      color: a.type === "structured" ? "var(--info)" : a.type === "evidence_upload" ? "var(--warning)" : "var(--muted)",
                      fontSize: 10, padding: "1px 6px",
                    }}>
                      {typeIcon(a.type)} {typeLabel(a.type)}
                    </span>
                    <span style={{ fontSize: 11, color: "var(--muted)", lineHeight: 1.3 }}>{a.guidance}</span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
                  {!done && a.controlId && (
                    <button className="btn btn-sm btn-ghost" onClick={() => handleCreateRequest(a)} disabled={requesting === a.id}
                      style={{ fontSize: 10, padding: "4px 8px", whiteSpace: "nowrap" }}>
                      {requesting === a.id ? "..." : "Request"}
                    </button>
                  )}
                  <NavLink to={a.actionLink} className="btn btn-sm btn-primary" style={{ fontSize: 10, padding: "4px 10px", whiteSpace: "nowrap" }}>
                    {a.actionLabel}
                  </NavLink>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
