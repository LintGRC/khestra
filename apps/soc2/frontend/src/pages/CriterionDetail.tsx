import { FormEvent, useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api, ControlDetail, ControlTest, ExceptionItem, RiskItem } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import { findingApi, FindingItem } from "@shared/audit-findings";
import { useLayout } from "../Layout";
import EvidencePanel from "../components/EvidencePanel";
import { EvidenceUploader } from "@shared/evidence-hub";
import ExceptionPanel from "../components/ExceptionPanel";
import CommentsPanel from "../components/CommentsPanel";
import RiskPanel from "../components/RiskPanel";
import FindingPanel from "../components/FindingPanel";
import { PageSkeleton } from "../components/ui/Skeleton";

export default function CriterionDetailPage() {
  const { controlId } = useParams();
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const { canEdit, refreshDashboard, settings } = useLayout();
  const [control, setControl] = useState<ControlDetail | null>(null);
  const [form, setForm] = useState<Partial<ControlDetail>>({});
  const [saving, setSaving] = useState(false);
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [findings, setFindings] = useState<FindingItem[]>([]);
  const [tests, setTests] = useState<ControlTest[]>([]);
  const [showTestForm, setShowTestForm] = useState(false);
  const [testForm, setTestForm] = useState({ test_procedure: "", frequency: "quarterly", sample_size: 1, sampling_methodology: "", notes: "" });
  const [recordingTest, setRecordingTest] = useState<string | null>(null);
  const [resultForm, setResultForm] = useState({ result: "pass", notes: "" });
  const [testResults, setTestResults] = useState<Record<string, any[]>>({});
  const [showGuide, setShowGuide] = useState(false);

  useEffect(() => {
    if (control && control.status === "NOT STARTED" && !localStorage.getItem("criterion-guide-dismissed")) {
      setShowGuide(true);
    }
  }, [control]);

  const [availablePolicies, setAvailablePolicies] = useState<Record<string, unknown>[]>([]);
  const [availableAssets, setAvailableAssets] = useState<Record<string, unknown>[]>([]);
  const [availablePersonnel, setAvailablePersonnel] = useState<Record<string, unknown>[]>([]);
  const [showAddPolicy, setShowAddPolicy] = useState(false);
  const [showAddAsset, setShowAddAsset] = useState(false);
  const [showAddTeam, setShowAddTeam] = useState(false);
  const [autoCollectors, setAutoCollectors] = useState<string[]>([]);

  // `resetForm` controls whether the in-progress edit state gets replaced by
  // the freshly-fetched server snapshot. Only safe right after the main form
  // has been fully saved (or on initial mount, before any edits exist) —
  // callers that reload after a side action (evidence upload, PoF status
  // change, comment add, etc.) must NOT reset the form, or they will
  // silently discard any unsaved edits (e.g. a status change picked but not
  // yet saved) still sitting in `form`.
  const reload = async (opts: { resetForm?: boolean } = {}) => {
    if (!controlId) return;
    const c = await api.control(controlId);
    setControl(c);
    if (opts.resetForm) setForm(c);
    try {
      const { exceptions: excs } = await api.listExceptions(controlId);
      setExceptions(excs || []);
      const { risks: r } = await api.listRisks();
      setRisks(r || []);
      const { findings: fnds } = await findingApi.list();
      setFindings(fnds || []);
    } catch {}
    try { const { policies: p } = await api.listPolicies(); setAvailablePolicies((p || []) as Record<string, unknown>[]); } catch {}
    try { const { assets: a } = await api.listAssets(); setAvailableAssets((a || []) as Record<string, unknown>[]); } catch {}
    try { const { personnel: pe } = await api.listPersonnel(); setAvailablePersonnel((pe || []) as Record<string, unknown>[]); } catch {}
    try { const { personnel: pe } = await api.listPersonnel(); setAvailablePersonnel((pe || []) as Record<string, unknown>[]); } catch {}
    try {
      const { tests: t } = await api.listTests(controlId);
      setTests(t || []);
    } catch {}
    // Fetch auto-collectors from shared mapping
    try {
      const res = await fetch(`/api/collectors/criteria/${encodeURIComponent(controlId)}/collectors?framework=soc2`);
      if (res.ok) setAutoCollectors(await res.json());
    } catch {}
    await refreshDashboard();
  };

  useEffect(() => {
    reload({ resetForm: true }).catch(console.error);
  }, [controlId]);

  const onSave = async (e: FormEvent) => {
    e.preventDefault();
    if (!controlId) return;
    setSaving(true);
    try {
      await api.patchControl(controlId, {
        status: form.status,
        operating_status: form.operating_status,
        implementation_narrative: form.implementation_narrative,
        assessor_notes: form.assessor_notes,
        owner: form.owner,
        target_date: form.target_date,
        remediation_plan: form.remediation_plan,
        frequency: form.frequency,
        last_review_date: form.last_review_date,
        next_review_date: form.next_review_date,
        linked_policies: form.linked_policies,
        linked_assets: form.linked_assets,
        linked_team: form.linked_team,
      });
      await reload({ resetForm: true });
    } finally {
      setSaving(false);
    }
  };

  async function handleCreateTest() {
    if (!controlId || !testForm.test_procedure.trim()) return;
    try {
      await api.createTest({ control_id: controlId, ...testForm });
      setTestForm({ test_procedure: "", frequency: "quarterly", sample_size: 1, sampling_methodology: "", notes: "" });
      setShowTestForm(false);
      const { tests: t } = await api.listTests(controlId);
      setTests(t || []);
    } catch {}
  }

  async function handleRecordResult(testId: string) {
    try {
      await api.addTestResult(testId, resultForm);
      setRecordingTest(null);
      setResultForm({ result: "pass", notes: "" });
      const { tests: t } = await api.listTests(controlId);
      setTests(t || []);
      const { results: r } = await api.getTestResults(testId);
      setTestResults((prev) => ({ ...prev, [testId]: r }));
    } catch {}
  }

  async function handleShowResults(testId: string) {
    if (testResults[testId]) {
      setTestResults((prev) => { const n = { ...prev }; delete n[testId]; return n; });
      return;
    }
    try {
      const { results: r } = await api.getTestResults(testId);
      setTestResults((prev) => ({ ...prev, [testId]: r }));
    } catch {}
  }

  if (!control) return <PageSkeleton variant="detail" />;

  const pendingReview = control.evidence.filter((e) => e.review_status === "pending").length;
  const reviewer = (settings?.current_user_name || settings?.current_role || "Reviewer").trim();

  function renderLinkedSection(kind: "policies" | "assets" | "team") {
    const profile = control?.linking_profile;
    const kindKey = kind === "policies" ? "policies" : kind === "assets" ? "assets" : "team";
    const requirement = profile?.[kindKey as keyof typeof profile];

    if (requirement === null || requirement === undefined) return null;

    const showState = kind === "policies" ? showAddPolicy : kind === "assets" ? showAddAsset : showAddTeam;
    const setShow = kind === "policies" ? setShowAddPolicy : kind === "assets" ? setShowAddAsset : setShowAddTeam;
    const label = kind === "policies" ? "Linked Policies" : kind === "assets" ? "Linked Assets" : "Linked Team";
    const fieldKey = kind === "policies" ? "linked_policies" : kind === "assets" ? "linked_assets" : "linked_team";

    const linked = (Array.isArray(form[fieldKey as keyof typeof form]) ? form[fieldKey as keyof typeof form] : []) as Record<string, unknown>[] | string[];

    const available: Record<string, unknown>[] = kind === "policies" ? availablePolicies :
      kind === "assets" ? availableAssets :
      availablePersonnel;

    const getId = (item: unknown) => {
      if (kind === "team") return String((item as Record<string, unknown>)?.id ?? String(item));
      return String((item as Record<string, unknown>)?.id ?? (item as Record<string, unknown>)?.asset_id ?? "");
    };
    const getLabel = (item: unknown) => {
      if (kind === "team") return String((item as Record<string, unknown>)?.name ?? String(item));
      return String((item as Record<string, unknown>)?.title ?? (item as Record<string, unknown>)?.name ?? (item as Record<string, unknown>)?.asset_name ?? "");
    };

    const alreadyLinked = new Set(linked.map((l) => {
      if (kind === "team") return String((l as Record<string, unknown>)?.id ?? String(l));
      return String((l as Record<string, unknown>)?.id ?? "");
    }));
    const filteredAvailable = available.filter((a) => !alreadyLinked.has(getId(a)));

    const setFormField = (key: string, value: unknown) =>
      setForm((f) => ({ ...f, [key]: value }));

    return (
      <div className="panel" key={kind}>
        <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <strong>{label} ({linked.length})</strong>
          {canEdit && (
            <button type="button" className="btn btn-sm btn-ghost" onClick={() => setShow(!showState)}>
              {showState ? "Cancel" : "+ Add"}
            </button>
          )}
        </div>
        {showState && canEdit && (
          <div className="panel-body" style={{ maxHeight: "200px", overflowY: "auto" }}>
            {filteredAvailable.length === 0 ? (
              <p className="muted" style={{ fontSize: "0.85rem" }}>
                No more {kind} available to link.
              </p>
            ) : (
              filteredAvailable.map((item) => (
                <button
                  key={getId(item)}
                  type="button"
                  className="btn btn-sm btn-ghost"
                  style={{ display: "block", width: "100%", textAlign: "left", padding: "4px 8px", marginBottom: 2 }}
                  onClick={() => {
                    const toAdd = kind === "team" ? { id: (item as Record<string, unknown>)?.id, name: (item as Record<string, unknown>)?.name } : item;
                    setFormField(fieldKey, [...linked, toAdd]);
                    setShow(false);
                  }}
                >
                  {getLabel(item)}
                  {kind === "policies" && ` (v${(item as Record<string, unknown>)?.version ?? "?"})`}
                </button>
              ))
            )}
          </div>
        )}
        {linked.length > 0 && (
          <div className="panel-body">
            {linked.map((item) => (
              <div key={getId(item)} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "2px 0", fontSize: "0.9rem" }}>
                <span>{getLabel(item)}</span>
                {canEdit && (
                  <button
                    type="button"
                    className="btn btn-xs btn-ghost"
                    style={{ color: "var(--danger)", fontSize: "0.75rem" }}
                    onClick={() => {
                      const updated = linked.filter((l) => getId(l) !== getId(item));
                      setFormField(fieldKey, updated);
                    }}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="criterion-detail-page page-stack">
      <p className="muted criterion-detail-back">
        <Link to={`${fwBase}/criteria`}>← Criteria</Link>
        {control && control.id && (
          <a
            className="btn btn-secondary btn-sm"
            style={{ marginLeft: 12, verticalAlign: "middle" }}
            href={apiUrl(`/api/evidence-hub/export?framework_id=SOC2&control_id=${encodeURIComponent(control.id)}`)}
            download
            title="Download all evidence files mapped to this criterion (ZIP + manifest)"
          >
            Evidence package
          </a>
        )}
      </p>

      {showGuide && (
        <div style={{
          background: "var(--info-soft)", border: "1px solid var(--primary)", borderRadius: 8, padding: 16, marginBottom: 12, position: "relative",
        }}>
          <button className="btn btn-ghost btn-sm" style={{ position: "absolute", top: 8, right: 8 }} onClick={() => { setShowGuide(false); localStorage.setItem("criterion-guide-dismissed", "1"); }}>✕</button>
          <strong style={{ fontSize: 13 }}>First-time assessment guide</strong>
          <ol style={{ margin: "8px 0 0 16px", fontSize: 12, lineHeight: 1.6 }}>
            <li><strong>Review the description</strong> — Understand what this criterion requires.</li>
            <li><strong>Check Points of Focus</strong> — Each PoF has evidence hints (click to expand).</li>
            <li><strong>Upload evidence</strong> — Screenshots, logs, configs that demonstrate the control.</li>
            <li><strong>Set a status</strong> — MET if implemented, NOT MET if not addressed, NOT APPLICABLE if irrelevant.</li>
            <li><strong>Write a narrative</strong> — Describe how your organization implements this control.</li>
          </ol>
        </div>
      )}

      {pendingReview > 0 && (
        <div className="banner warning">
          {pendingReview} evidence item(s) pending review.
        </div>
      )}

      <header className="panel">
        <div className="panel-body">
          <p className="control-family">{control.category}</p>
          <h2>{control.code} — {control.name}</h2>
          <p className="muted">{control.description}</p>
        </div>
      </header>

      {/* ── Evidence Guidance ── */}
      {control.evidence_guidance && (
        <div className="panel" style={{ borderLeft: "3px solid var(--primary)", background: "var(--info-soft)" }}>
          <div className="panel-body">
            <p style={{ fontSize: "0.78rem", margin: 0, lineHeight: 1.5, color: "var(--muted)" }}>
              <strong>Evidence guidance:</strong> {control.evidence_guidance.text}
            </p>
            {autoCollectors.length > 0 && (
              <p style={{ fontSize: "0.75rem", marginTop: 4, color: "var(--success)" }}>
                Auto-collectors: {autoCollectors.join(", ")}
              </p>
            )}
          </div>
        </div>
      )}

      {/* ── Points of Focus ── */}
      {control.points_of_focus && control.points_of_focus.length > 0 && (
        <div className="panel">
          <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>
              <strong>Points of Focus</strong>{" "}
              <span className="badge badge-muted" style={{ fontSize: "0.75rem" }}>
                {control.pof_addressed || 0}/{control.pof_total || control.points_of_focus.length}
              </span>
            </span>
          </div>
          <div className="panel-body">
            {control.points_of_focus.map((pof) => {
              const st = control.pof_statuses?.[pof.id];
              const stVal = st?.status || "not_applicable";
              return (
                <div
                  key={pof.id}
                  className="pof-row"
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 8,
                    padding: "6px 0",
                    borderBottom: "1px solid var(--border-subtle)",
                    fontSize: "0.85rem",
                  }}
                >
                  <span
                    className="pof-theme-badge"
                    style={{
                      fontSize: "0.65rem",
                      background: "var(--muted-bg)",
                      padding: "2px 6px",
                      borderRadius: 4,
                      whiteSpace: "nowrap",
                      minWidth: 90,
                      textAlign: "center",
                      color: stVal === "addressed" ? "var(--success)" : "var(--text-muted)",
                    }}
                  >
                    {pof.theme}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div>{pof.text}</div>
                    {pof.evidence_hints && pof.evidence_hints.length > 0 && (
                      <details style={{ marginTop: 4, fontSize: "0.72rem", color: "var(--text-muted)" }}>
                        <summary style={{ cursor: "pointer" }}>Evidence hints</summary>
                        <ul style={{ margin: "4px 0 0 16px", padding: 0 }}>
                          {pof.evidence_hints.map((h, i) => (
                            <li key={i} style={{ marginBottom: 2 }}>{h}</li>
                          ))}
                        </ul>
                      </details>
                    )}
                  </div>
                  <select
                    value={stVal}
                    disabled={!canEdit}
                    onChange={async (e) => {
                      const newStatus = e.target.value;
                      const existing = control.pof_statuses?.[pof.id];
                      try {
                        await api.patchPof(control.id, pof.id, newStatus as any, existing?.justification || "");
                        await reload();
                      } catch (err) {
                        console.error("Failed to update PoF", err);
                      }
                    }}
                    style={{
                      fontSize: "0.75rem",
                      width: 100,
                      borderColor: stVal === "addressed" ? "var(--success)" : "var(--border)",
                      color: stVal === "addressed" ? "var(--success)" : "var(--text-muted)",
                    }}
                  >
                    <option value="not_applicable">Not Applicable</option>
                    <option value="addressed">Addressed</option>
                  </select>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <form className="panel control-detail-form" onSubmit={onSave}>
        <div className="panel-body">
          <label>
            Status <span title="Your assessment of design effectiveness: MET = control is designed and operating as intended; NOT MET = does not meet the criterion; NOT STARTED = not yet evaluated." style={{cursor:'help',color:'var(--text-muted)'}}>ⓘ</span>
            <select
              value={form.status || control.status}
              disabled={!canEdit}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
            >
              {control.status_options.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>
            Operating Effectiveness <span title="PASS = controls operated effectively during testing; FAIL = controls did not operate as designed; NOT TESTED = no testing evidence yet." style={{cursor:'help',color:'var(--text-muted)'}}>ⓘ</span>
            <select
              value={form.operating_status || control.operating_status || "NOT TESTED"}
              disabled={!canEdit}
              onChange={(e) => setForm((f) => ({ ...f, operating_status: e.target.value }))}
              style={{ borderColor: (form.operating_status || control.operating_status) === "PASS" ? "var(--success)" : (form.operating_status || control.operating_status) === "FAIL" ? "var(--danger)" : undefined }}
            >
              {(control.operating_status_options || ["NOT TESTED", "PASS", "FAIL", "NEEDS REVIEW"]).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          <label>
            Control narrative
            <textarea
              rows={6}
              disabled={!canEdit}
              value={form.implementation_narrative || ""}
              onChange={(e) => setForm((f) => ({ ...f, implementation_narrative: e.target.value }))}
              placeholder="How your organization satisfies this criterion…"
            />
          </label>
          <label>
            Assessor notes
            <textarea
              rows={3}
              disabled={!canEdit}
              value={form.assessor_notes || ""}
              onChange={(e) => setForm((f) => ({ ...f, assessor_notes: e.target.value }))}
            />
          </label>
          <div className="form-row">
            <label>
              Owner <span title="Who is responsible for ensuring this control is implemented and evidence is collected?" style={{cursor:'help',color:'var(--text-muted)'}}>ⓘ</span>
              <input
                disabled={!canEdit}
                value={form.owner || ""}
                onChange={(e) => setForm((f) => ({ ...f, owner: e.target.value }))}
              />
            </label>
            <label>
              Target date <span title="When do you expect this control to be fully implemented and tested?" style={{cursor:'help',color:'var(--text-muted)'}}>ⓘ</span>
              <input
                disabled={!canEdit}
                value={form.target_date || ""}
                onChange={(e) => setForm((f) => ({ ...f, target_date: e.target.value }))}
              />
            </label>
          </div>
          <label>
            Remediation plan
            <textarea
              rows={3}
              disabled={!canEdit}
              value={form.remediation_plan || ""}
              onChange={(e) => setForm((f) => ({ ...f, remediation_plan: e.target.value }))}
            />
          </label>
          <div className="form-row">
            <label>
              Frequency <span title="How often is this control tested or reviewed? Common: Continuous (automated), Monthly, Quarterly, Annually." style={{cursor:'help',color:'var(--text-muted)'}}>ⓘ</span>
              <select
                value={form.frequency || ""}
                disabled={!canEdit}
                onChange={(e) => setForm((f) => ({ ...f, frequency: e.target.value }))}
              >
                {(control.frequency_options || ["", "Continuous", "Daily", "Weekly", "Monthly", "Quarterly", "Annually", "Ad-hoc"]).map((s) => (
                  <option key={s} value={s}>{s || "—"}</option>
                ))}
              </select>
            </label>
            <label>
              Last review date
              <input
                disabled={!canEdit}
                value={form.last_review_date || ""}
                onChange={(e) => setForm((f) => ({ ...f, last_review_date: e.target.value }))}
                placeholder="YYYY-MM-DD"
              />
            </label>
            <label>
              Next review date
              <input
                disabled={!canEdit}
                value={form.next_review_date || ""}
                onChange={(e) => setForm((f) => ({ ...f, next_review_date: e.target.value }))}
                placeholder="YYYY-MM-DD"
              />
            </label>
          </div>
          {canEdit && (
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
          )}
        </div>
      </form>

      <EvidenceUploader
        frameworkId="SOC2"
        controlId={control.id}
        onEvidenceCreated={() => reload().catch(console.error)}
        label="Upload to shared Evidence Hub:"
      />

      <EvidencePanel
        controlId={control.id}
        evidence={control.evidence}
        canEdit={canEdit}
        reviewer={reviewer}
        onUpdated={() => reload().catch(console.error)}
      />

      <ExceptionPanel
        controlId={control.id}
        canEdit={canEdit}
        exceptions={exceptions}
      />

      <RiskPanel
        controlId={control.id}
        canEdit={canEdit}
        risks={risks}
      />

      <FindingPanel
        controlId={control.id}
        canEdit={canEdit}
        findings={findings}
      />

      <div className="panel">
        <div className="panel-header"><strong>Comments ({control.comments?.length || 0})</strong></div>
        <div className="panel-body">
          <CommentsPanel
            controlId={control.id}
            comments={control.comments || []}
            disabled={!canEdit}
            onUpdated={() => reload().catch(console.error)}
          />
        </div>
      </div>

      {renderLinkedSection("policies")}
      {renderLinkedSection("assets")}
      {renderLinkedSection("team")}

      <div className="panel">
        <div className="panel-header">
          <h3>Tests of Controls ({tests.length})</h3>
          {canEdit && (
            <button className="btn btn-secondary btn-sm" onClick={() => setShowTestForm(!showTestForm)}>
              {showTestForm ? "Cancel" : "New Test"}
            </button>
          )}
        </div>
        <div className="panel-body">
          {showTestForm && (
            <div style={{ marginBottom: 12, padding: 12, border: "1px solid var(--border)", borderRadius: "var(--radius)", background: "var(--bg)" }}>
              <label style={{ fontSize: 12 }}>Test Procedure
                <textarea rows={3} value={testForm.test_procedure} onChange={(e) => setTestForm((f) => ({ ...f, test_procedure: e.target.value }))} placeholder="Describe the test steps…" />
              </label>
              <div className="form-row" style={{ marginTop: 8 }}>
                <label style={{ fontSize: 12 }}>Frequency
              <select value={testForm.frequency} onChange={(e) => setTestForm((f) => ({ ...f, frequency: e.target.value }))}>
                    {(control.frequency_options || ["", "Continuous", "Daily", "Weekly", "Monthly", "Quarterly", "Annually", "Ad-hoc"]).map((s) => <option key={s} value={s}>{s || "—"}</option>)}
                  </select>
                </label>
                <label>
                  Methodology
                  <select value={testForm.sampling_methodology} onChange={(e) => setTestForm((f) => ({ ...f, sampling_methodology: e.target.value }))}>
                    <option value="">—</option>
                    <option value="attribute_sampling">Attribute Sampling</option>
                    <option value="statistical_sampling">Statistical Sampling</option>
                    <option value="full_population">Full Population</option>
                    <option value="judgmental">Judgmental Selection</option>
                  </select>
                </label>
                <label style={{ fontSize: 12 }}>Sample Size
                  <input type="number" min={1} value={testForm.sample_size} onChange={(e) => setTestForm((f) => ({ ...f, sample_size: parseInt(e.target.value) || 1 }))} />
                </label>
              </div>
              <label style={{ fontSize: 12 }}>Notes
                <input value={testForm.notes} onChange={(e) => setTestForm((f) => ({ ...f, notes: e.target.value }))} placeholder="Optional notes" />
              </label>
              <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} onClick={handleCreateTest} disabled={!testForm.test_procedure.trim()}>Create Test</button>
            </div>
          )}

          {tests.length === 0 && !showTestForm && (
            <p className="muted" style={{ fontSize: 13 }}>No test cases defined. {canEdit ? "Click \"New Test\" to add one." : ""}</p>
          )}

          {tests.map((t) => (
            <div key={t.id} style={{ padding: "10px 0", borderBottom: "1px solid var(--border-subtle)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>{t.test_procedure}</div>
                  <div style={{ display: "flex", gap: 8, fontSize: 11, color: "var(--muted)", flexWrap: "wrap" }}>
                    <span>Frequency: {t.frequency}</span>
                    <span>Sample: {t.sample_size}</span>
                    {t.sampling_methodology && <span style={{ fontStyle: "italic" }}>Method: {t.sampling_methodology.replace(/_/g, " ")}</span>}
                    <span>Status: <span style={{ fontWeight: 600, color: t.status === "pass" ? "var(--success)" : t.status === "fail" ? "var(--danger)" : t.status === "needs_review" ? "var(--warning)" : "var(--muted)" }}>{t.status.replace("_", " ")}</span></span>
                    {t.last_tested && <span>Last tested: {t.last_tested.slice(0, 10)}</span>}
                    {t.next_test_due && <span>Due: {t.next_test_due.slice(0, 10)}</span>}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleShowResults(t.id)}>
                    Results ({testResults[t.id] ? "" : "…"})
                  </button>
                  {canEdit && (
                    <button className="btn btn-secondary btn-sm" onClick={() => { setRecordingTest(t.id); setResultForm({ result: "pass", notes: "" }); }}>
                      Record Result
                    </button>
                  )}
                </div>
              </div>

              {recordingTest === t.id && (
                <div style={{ marginTop: 8, padding: 10, border: "1px solid var(--border)", borderRadius: "var(--radius)" }}>
                  <div className="form-row" style={{ marginBottom: 6 }}>
                    <label style={{ fontSize: 12 }}>Result
                      <select value={resultForm.result} onChange={(e) => setResultForm((f) => ({ ...f, result: e.target.value }))}>
                        {["pass", "fail", "needs_review"].map((r) => <option key={r} value={r}>{r.replace("_", " ")}</option>)}
                      </select>
                    </label>
                  </div>
                  <label style={{ fontSize: 12 }}>Notes
                    <input value={resultForm.notes} onChange={(e) => setResultForm((f) => ({ ...f, notes: e.target.value }))} placeholder="Optional notes" />
                  </label>
                  <div style={{ display: "flex", gap: 4, marginTop: 6 }}>
                    <button className="btn btn-primary btn-sm" onClick={() => handleRecordResult(t.id)}>Save</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => setRecordingTest(null)}>Cancel</button>
                  </div>
                </div>
              )}

              {testResults[t.id] && (
                <div style={{ marginTop: 8 }}>
                  {testResults[t.id].length === 0 && <p className="muted" style={{ fontSize: 11 }}>No results recorded.</p>}
                  {testResults[t.id].map((r: any) => (
                    <div key={r.id} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, padding: "4px 8px", background: "var(--bg)", borderRadius: "var(--radius)", marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, color: r.result === "pass" ? "var(--success)" : r.result === "fail" ? "var(--danger)" : "var(--warning)" }}>{r.result.toUpperCase()}</span>
                      <span className="muted">{r.tested_at?.slice(0, 10)}</span>
                      {r.tested_by && <span>by {r.tested_by}</span>}
                      {r.notes && <span className="muted">— {r.notes}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
