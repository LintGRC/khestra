import { useEffect, useState } from "react";
import { useParams, NavLink, useSearchParams } from "react-router-dom";
import { CheckCircle } from "lucide-react";
import EvidenceUploader from "@shared/evidence-hub/EvidenceUploader";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { FW_LABELS, AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";
import { apiUrl } from "@shared/apiPrefix";
import { renderControlRef } from "@shared/refs/format";
import { postDownload } from "../api";

const API = "/api/ai-governance";

interface Article {
  id: string;
  title: string;
  ref: string;
  category: string;
  summary: string;
  control_id?: string;
}

interface ArticleStatus {
  status: string;
  notes: string;
}

interface Conformity {
  status: string;
  articles: Record<string, ArticleStatus>;
}

type EvidenceItem = {
  id: string;
  name: string;
  mappings: { framework_id: string; control_id: string }[];
};

const STATUS_LABELS: Record<string, string> = {
  compliant: "Compliant",
  partial: "Partial",
  missing: "Missing",
  na: "N/A",
};

const STATUS_COLORS: Record<string, string> = {
  compliant: "var(--success)",
  partial: "var(--warning)",
  missing: "var(--danger)",
  na: "var(--muted)",
};

const FW_CATEGORY_LABELS: Record<string, Record<string, string>> = {
  eu_ai_act: {
    prohibited: "Prohibited Practices (Art. 5)",
    classification: "High-Risk Classification (Art. 6, Annex III)",
    requirements: "Core Requirements (Art. 8\u201315, 43)",
    provider: "Provider Obligations (Art. 16\u201325, 46\u201349)",
    deployer: "Deployer Obligations (Art. 26\u201327)",
    limited: "Transparency Obligations (Art. 50)",
    gpai: "GPAI Obligations (Art. 51\u201356)",
    post_market: "Post-Market & Governance (Art. 57, 60\u201361, 71\u201373)",
  },
  nist_ai_rmf: {
    "GOVERN 1": "GOVERN 1 — Policies, Processes & Practices",
    "GOVERN 2": "GOVERN 2 — Accountability Structures",
    "GOVERN 3": "GOVERN 3 — Diversity, Equity, Inclusion & Accessibility",
    "GOVERN 4": "GOVERN 4 — AI Risk Culture & Communication",
    "GOVERN 5": "GOVERN 5 — Engagement with Relevant AI Actors",
    "GOVERN 6": "GOVERN 6 — Third-Party & Supply Chain AI Risk",
    "MAP 1": "MAP 1 — Context Establishment",
    "MAP 2": "MAP 2 — AI System Categorization",
    "MAP 3": "MAP 3 — Capabilities, Goals & Benefits",
    "MAP 4": "MAP 4 — Risk & Benefit Mapping",
    "MAP 5": "MAP 5 — Impact Characterization",
    "MEASURE 1": "MEASURE 1 — Methods & Metrics",
    "MEASURE 2": "MEASURE 2 — Trustworthiness Evaluation",
    "MEASURE 3": "MEASURE 3 — Risk Tracking Over Time",
    "MEASURE 4": "MEASURE 4 — Measurement Feedback",
    "MANAGE 1": "MANAGE 1 — Risk Prioritization & Response",
    "MANAGE 2": "MANAGE 2 — Benefit & Impact Strategies",
    "MANAGE 3": "MANAGE 3 — Third-Party AI Risk Management",
    "MANAGE 4": "MANAGE 4 — Risk Treatment & Communication",
  },
  iso_42001: {
    context: "Context of the Organization (Clause 4)",
    leadership: "Leadership & Policy (Clause 5)",
    planning: "Planning & Risk Assessment (Clause 6)",
    support: "Support & Competence (Clause 7)",
    operation: "Operation & Lifecycle (Clause 8)",
    evaluation: "Performance Evaluation (Clause 9)",
    improvement: "Improvement (Clause 10)",
    "A.2": "A.2 — Policies related to AI",
    "A.3": "A.3 — Internal organization",
    "A.4": "A.4 — Resources for AI systems",
    "A.5": "A.5 — Assessing impacts of AI systems",
    "A.6": "A.6 — AI system life cycle",
    "A.7": "A.7 — Data for AI systems",
    "A.8": "A.8 — Information for interested parties of AI systems",
    "A.9": "A.9 — Use of AI systems",
    "A.10": "A.10 — Third-party and customer relationships",
  },
  owasp_agentic: {
    agentic: "OWASP Agentic AI Top 10 (2026) — ASI01\u2013ASI10",
  },
  owasp_llm: {
    llm: "OWASP LLM Top 10 (2025) — LLM01\u2013LLM10",
  },
};

export function ConformityAssessmentPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const fw = searchParams.get("framework") || activeFrameworks[0] || "eu_ai_act";
  const [system, setSystem] = useState<any>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [articlesLoaded, setArticlesLoaded] = useState(false);
  const [queueMeta, setQueueMeta] = useState<{ catalog_total?: number; in_queue?: number; profile?: string; tier?: string }>({});
  const [, _setConformity] = useState<Conformity | null>(null);
  const [statuses, setStatuses] = useState<Record<string, ArticleStatus>>({});
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [evidenceByControl, setEvidenceByControl] = useState<Record<string, EvidenceItem[]>>({});
  const [objectivesByArticle, setObjectivesByArticle] = useState<Record<string, string[]>>({});

  useEffect(() => {
    if (!id) return;
    setArticlesLoaded(false);
    Promise.all([
      fetch(`${API}/systems/${id}`).then(r => r.json()).then(d => setSystem(d.system)),
      fetch(`${API}/systems/${id}/conformity/articles?framework=${fw}`).then(r => r.json()).then(d => {
        setArticles(d.articles || []);
        setQueueMeta({ catalog_total: d.catalog_total, in_queue: d.in_queue, profile: d.profile, tier: d.tier });
        setArticlesLoaded(true);
      }),
      fetch(`${API}/systems/${id}/conformity?framework=${fw}`).then(r => r.json()).then(d => d.conformity).then(c => {
        if (c) {
          _setConformity(c);
          setStatuses(c.articles || {});
        }
      }),
      fetch(apiUrl("/api/evidence-hub?framework_id=AIGov")).then(r => r.json()).then(data => {
        const items: EvidenceItem[] = data.evidence || [];
        const byControl: Record<string, EvidenceItem[]> = {};
        for (const item of items) {
          for (const m of item.mappings) {
            if (m.framework_id === "AIGov" && m.control_id) {
              if (!byControl[m.control_id]) byControl[m.control_id] = [];
              byControl[m.control_id].push(item);
            }
          }
        }
        setEvidenceByControl(byControl);
      }).catch(() => {}),
      fetch(`${API}/systems/${id}/objectives?framework=${fw}`).then(r => r.json()).then(data => {
        const byArticle: Record<string, string[]> = {};
        for (const fwName of Object.keys(data.frameworks || {})) {
          for (const obj of data.frameworks[fwName]) {
            byArticle[obj.article_id] = obj.objectives;
          }
        }
        setObjectivesByArticle(byArticle);
      }).catch(() => {}),
    ]);
  }, [id, fw]);

  if (!system || !articlesLoaded) {
    return <p className="muted" style={{ padding: 24 }}>Loading...</p>;
  }

  if (articles.length === 0) {
    return (
      <div className="page-stack" style={{ padding: 24 }}>
        <p>
          No articles in the work queue for this classification
          ({system.risk_classification || "unclassified"} / {system.ai_profile || "provider"})
          under {FW_LABELS[fw] || fw}.
        </p>
        <p className="muted" style={{ fontSize: 13 }}>
          Change the risk tier or organization role on classification, or pick another framework.
        </p>
        <NavLink to={`/aigov/systems/${id}/classify`} className="btn btn-secondary btn-sm">Edit classification</NavLink>
      </div>
    );
  }

  const tierColors: Record<string, [string, string]> = {
    unacceptable: ["var(--danger-soft)", "var(--danger)"], high: ["var(--danger-soft)", "var(--danger)"],
    limited: ["var(--warning-soft)", "var(--warning)"], minimal: ["var(--success-soft)", "var(--success)"],
    gpa: ["var(--info-soft)", "var(--info)"], unclassified: ["var(--surface)", "var(--muted)"],
  };
  const [tierBg, tierColor] = tierColors[system.risk_classification] || ["var(--surface)", "var(--muted)"];

  const total = articles.length;
  const done = Object.values(statuses).filter(a => a.status && a.status !== "missing").length;
  const pct = total ? Math.round((done / total) * 100) : 0;

  const categories = [...new Set(articles.map(a => a.category))];
  const catLabels = FW_CATEGORY_LABELS[fw] || {};

  function setArticleStatus(artId: string, status: string) {
    setStatuses(prev => ({ ...prev, [artId]: { ...prev[artId], status, notes: prev[artId]?.notes || "" } }));
  }

  function setArticleNotes(artId: string, notes: string) {
    setStatuses(prev => ({ ...prev, [artId]: { ...prev[artId], status: prev[artId]?.status || "missing", notes } }));
  }

  function getAnswer(artId: string): any {
    const art = articles.find(a => a.id === artId);
    const cid = art?.control_id || "";
    return (system?.answers || {})[cid] || {};
  }

  async function toggleObjective(artId: string, field: "obj_examine_done" | "obj_interview_done" | "obj_test_done") {
    const art = articles.find(a => a.id === artId);
    const cid = art?.control_id || "";
    if (!cid) return;
    const ans = (system?.answers || {})[cid] || {};
    const current = ans[field] || false;
    setSystem((prev: any) => prev ? {
      ...prev,
      answers: { ...prev.answers, [cid]: { ...ans, [field]: !current } },
    } : prev);
    await fetch(`${API}/systems/${id}`, {
      method: "PATCH", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers: { ...(system?.answers || {}), [cid]: { ...ans, [field]: !current } } }),
    });
  }

  async function handleSave() {
    const missingJust = Object.entries(statuses).filter(
      ([, s]) => s.status === "na" && !(s.notes || "").trim(),
    );
    if (missingJust.length) {
      alert("Not applicable (N/A) requires a justification in the notes field.");
      return;
    }
    setSaving(true);
    try {
      await fetch(`${API}/systems/${id}/conformity?framework=${fw}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          articles: statuses,
          status: done === total ? "completed" : "in_progress",
        }),
      });
    } catch {}
    setSaving(false);
  }

  async function handleExport() {
    setExporting(true);
    try {
      await postDownload(`${API}/systems/${id}/conformity/export?framework=${fw}`, undefined, "conformity-assessment.pdf");
    } catch (e) { alert(`Export failed: ${String(e)}`); }
    setExporting(false);
  }

  async function handleExportDoc(kind: "eu-doc" | "tech-doc" | "soa-export") {
    setExporting(true);
    try {
      await postDownload(`${API}/systems/${id}/conformity/${kind}`, undefined, `${kind}.docx`);
    } catch (e) { alert(`Export failed: ${String(e)}`); }
    setExporting(false);
  }

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <NavLink to={`/aigov/systems/${id}`} style={{ fontSize: "0.85rem", color: "var(--muted)", textDecoration: "none", display: "block", marginBottom: 4 }}>
            &larr; {system.name}
          </NavLink>
          <h2 style={{ margin: 0 }}>{FW_LABELS[fw] || "Conformity"} Assessment</h2>
          <div style={{ display: "flex", gap: 8, marginTop: 8, alignItems: "center" }}>
            <span className="badge" style={{ background: tierBg, color: tierColor, fontWeight: 600 }}>{system.risk_classification}</span>
            <span className="badge badge-muted">{system.ai_profile || queueMeta.profile || "provider"}</span>
            <span className="muted" style={{ fontSize: "0.8rem" }}>Version {system.version}</span>
            {AI_GOV_FRAMEWORKS.filter(f => activeFrameworks.includes(f.key)).map(f => (
              <NavLink key={f.key} to={`/aigov/systems/${id}/conformity?framework=${f.key}`} className={`btn btn-sm ${fw === f.key ? "btn-primary" : "btn-ghost"}`} style={{ fontSize: 10 }}>{f.label}</NavLink>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Assessment"}
          </button>
          <button className="btn btn-secondary btn-sm" onClick={handleExport} disabled={exporting}>
            {exporting ? "Exporting..." : "Export Declaration PDF"}
          </button>
          {fw === "eu_ai_act" && (
            <>
              <button
                className="btn btn-secondary btn-sm"
                disabled={exporting}
                onClick={() => handleExportDoc("eu-doc")}
              >
                EU DoC (Art. 47)
              </button>
              <button
                className="btn btn-secondary btn-sm"
                disabled={exporting}
                onClick={() => handleExportDoc("tech-doc")}
              >
                Tech Documentation (Art. 11)
              </button>
            </>
          )}
          {fw === "iso_42001" && (
            <button
              className="btn btn-secondary btn-sm"
              disabled={exporting}
              onClick={() => handleExportDoc("soa-export")}
            >
              AI SoA (Annex A)
            </button>
          )}
          <button
            className="btn btn-secondary btn-sm"
            disabled={exporting}
            onClick={async () => {
              setExporting(true);
              try {
                await postDownload(`${API}/systems/${id}/dossier/export`, undefined, `regulatory-dossier-${id}.zip`);
              } catch (e) { alert(`Export failed: ${String(e)}`); }
              setExporting(false);
            }}
          >
            {exporting ? "Exporting..." : "Download dossier pack"}
          </button>
        </div>
      </div>

      <div className="panel" style={{ padding: "1rem", marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <strong style={{ fontSize: "0.9rem" }}>Progress</strong>
          <span style={{ fontWeight: 700, fontSize: 18, color: pct >= 80 ? "var(--success)" : pct >= 30 ? "var(--warning)" : "var(--danger)" }}>{pct}%</span>
        </div>
        <div style={{ width: "100%", background: "var(--border)", borderRadius: 6, height: 10, overflow: "hidden" }}>
          <div style={{ width: `${pct}%`, height: "100%", borderRadius: 6, background: pct >= 80 ? "var(--success)" : pct >= 30 ? "var(--warning)" : "var(--danger)", transition: "width 0.3s" }} />
        </div>
        <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: 4 }}>
          {done} of {total} in-queue articles assessed
          {queueMeta.catalog_total != null && queueMeta.catalog_total !== total
            ? ` · ${queueMeta.catalog_total - total} hidden by classification`
            : ""}
        </div>
      </div>

      {categories.map(cat => (
        <div className="panel" key={cat} style={{ marginBottom: 16 }}>
          <div className="panel-header"><strong>{catLabels[cat] || cat}</strong></div>
          <div className="panel-body" style={{ padding: 0 }}>
            {articles.filter(a => a.category === cat).map(art => {
              const s = statuses[art.id];
              const current = s?.status || "missing";
              return (
                <div key={art.id} style={{ padding: "0.75rem 1rem", borderBottom: "1px solid var(--border-subtle)" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 16, alignItems: "start" }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                        <span style={{ fontFamily: "monospace", marginRight: 8, fontWeight: 700, color: "var(--primary)" }}>{renderControlRef(art.control_id || art.ref)}</span>
                        {art.title}
                      </div>
                      <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: 3, lineHeight: 1.4 }}>{art.summary}</div>
                      {objectivesByArticle[art.id] && (
                        <details style={{ marginTop: 6, fontSize: "0.72rem" }}>
                          <summary style={{ color: "var(--primary)", cursor: "pointer" }}>
                            {(() => {
                              const ans = getAnswer(art.id);
                              const done = (ans.obj_examine_done ? 1 : 0) + (ans.obj_interview_done ? 1 : 0) + (ans.obj_test_done ? 1 : 0);
                              return <>{objectivesByArticle[art.id].length} assessment objectives · {done}/3 complete</>;
                            })()}
                          </summary>
                          <ul style={{ margin: "6px 0 0 0", padding: 0, listStyle: "none" }}>
                            {objectivesByArticle[art.id].map((obj, i) => {
                              const fields = ["obj_examine_done", "obj_interview_done", "obj_test_done"] as const;
                              const ans = getAnswer(art.id);
                              const checked = ans[fields[i]] || false;
                              const prefix = obj.startsWith("Examine:") ? "📋" : obj.startsWith("Interview:") ? "🗣️" : "🔬";
                              return (
                                <li key={i} style={{ marginBottom: 4, lineHeight: 1.5, display: "flex", alignItems: "flex-start", gap: 6 }}>
                                  <input
                                    type="checkbox"
                                    checked={checked}
                                    onChange={() => toggleObjective(art.id, fields[i])}
                                    style={{ marginTop: 2, flexShrink: 0 }}
                                  />
                                  <span style={{ color: checked ? "var(--success)" : "var(--text-muted)", textDecoration: checked ? "none" : "none" }}>
                                    {prefix} {obj}
                                  </span>
                                </li>
                              );
                            })}
                          </ul>
                        </details>
                      )}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span className="muted" style={{ fontSize: 10 }}>Status:</span>
                      <select
                        value={current}
                        onChange={e => setArticleStatus(art.id, e.target.value)}
                        style={{ fontSize: "0.75rem", padding: "3px 8px", border: `1px solid ${STATUS_COLORS[current]}`, borderRadius: 4, background: "var(--surface)", color: STATUS_COLORS[current], fontWeight: 600 }}
                      >
                        {Object.entries(STATUS_LABELS).map(([k, v]) => (
                          <option key={k} value={k}>{v}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div style={{ marginTop: 8 }}>
                    <textarea
                      placeholder={current === "na"
                        ? "Justification required: why this control is not applicable"
                        : "Notes, evidence references, or remediation plan..."}
                      value={s?.notes || ""}
                      onChange={e => setArticleNotes(art.id, e.target.value)}
                      rows={2}
                      style={{ width: "100%", fontSize: "0.75rem", padding: "6px 10px", border: "1px solid var(--border)", borderRadius: 4, resize: "vertical", background: "var(--surface)" }}
                    />
                    <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                      {evidenceByControl[art.id]?.length > 0 && (
                        <span style={{ fontSize: 11, color: "var(--success)", display: "flex", alignItems: "center", gap: 4 }}>
                          <CheckCircle size={12} /> {evidenceByControl[art.id].length} evidence file(s) uploaded
                        </span>
                      )}
                      <div style={{ flex: 1, minWidth: 200 }}>
                        <EvidenceUploader frameworkId="AIGov" controlId={art.id} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {fw === "eu_ai_act" && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-header"><strong>Declaration of Conformity (Annex VI)</strong></div>
          <div className="panel-body" style={{ padding: "0.75rem 1rem 1rem" }}>
            <p className="muted" style={{ fontSize: 11, marginBottom: 8 }}>
              The EU Declaration of Conformity is a formal document required by Art. 19 for high-risk AI systems.
              Export the PDF after completing the assessment above.
            </p>
            <button className="btn btn-secondary btn-sm" onClick={handleExport} disabled={exporting}>
              {exporting ? "Exporting..." : "Export Declaration PDF"}
            </button>
          </div>
        </div>
      )}

      {articles.length === 0 && (
        <div className="panel" style={{ padding: 16 }}>
          <p className="muted" style={{ fontSize: 12, textAlign: "center" }}>No requirements apply to this risk tier for {FW_LABELS[fw] || fw}.</p>
        </div>
      )}
    </div>
  );
}
