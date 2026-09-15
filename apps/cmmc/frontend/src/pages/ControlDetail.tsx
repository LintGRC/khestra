import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api, authFetch, ControlDetail, ControlGuidance, ControlMeta, ControlReadiness, ReadinessItem } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import { useLayout } from "../Layout";
import RiskBadge from "../components/RiskBadge";
import EvidencePanel from "../components/EvidencePanel";
import CollectorEvidenceDraft from "../components/CollectorEvidenceDraft";
import CollectorRemediationDraft from "../components/CollectorRemediationDraft";
import ReadinessChecklist from "../components/ReadinessChecklist";
import AutoBadge from "../components/AutoBadge";
import AutomationCoverageBadge from "../components/AutomationCoverageBadge";
import ControlDetailWizard, { WizardStepDef } from "../components/ControlDetailWizard";
import ControlCommentsPanel from "../components/ControlCommentsPanel";

import SspControlPreview from "../components/SspControlPreview";
import OwnerSelect from "../components/OwnerSelect";
import NarrativePreviewModal from "../components/NarrativePreviewModal";
import { PageSkeleton } from "../components/ui/Skeleton";
import { personnelApi } from "@shared/personnel/api";

const SSP_PLACEHOLDER_RE = /\[[^\]]+\]/g;
const _GAP_STATUSES = new Set(["NOT STARTED", "IN PROGRESS", "INCOMPLETE", "DEFERRED"]);

type ObjectiveAssessment = {
  total: number;
  metOrNa: number;
  notMet: number;
  notStarted: number;
  /** Advisory status from objectives only — does not overwrite control status. */
  computed: string;
  applicableIncomplete: number;
};

function assessObjectives(
  objectives: { letter?: string; status?: string }[] | undefined,
): ObjectiveAssessment | null {
  if (!objectives?.length) return null;
  let metOrNa = 0;
  let notMet = 0;
  let notStarted = 0;
  const statuses = new Set<string>();
  for (const o of objectives) {
    const s = (o.status || "NOT_STARTED").toUpperCase().trim();
    if (s === "NOT_STARTED" || s === "NOT STARTED") {
      notStarted += 1;
      statuses.add("NOT_STARTED");
    } else if (s === "NA" || s === "NOT APPLICABLE" || s === "N/A") {
      metOrNa += 1;
      statuses.add("NA");
    } else if (s === "MET") {
      metOrNa += 1;
      statuses.add("MET");
    } else if (s === "NOT_MET" || s === "NOT MET") {
      notMet += 1;
      statuses.add("NOT MET");
    } else {
      notStarted += 1;
      statuses.add("NOT_STARTED");
    }
  }
  const total = objectives.length;
  const applicableIncomplete = notStarted + notMet;
  let computed = "IN PROGRESS";
  if (notStarted > 0) computed = "INCOMPLETE";
  else if (statuses.has("NOT MET") && statuses.has("MET")) computed = "IN PROGRESS";
  else if (statuses.has("NOT MET")) computed = "NOT MET";
  else if (statuses.has("MET") && !statuses.has("NA")) computed = "MET";
  else if (statuses.has("MET") && statuses.has("NA")) computed = "MET";
  else if (statuses.size === 1 && statuses.has("NA")) computed = "NOT APPLICABLE";
  return { total, metOrNa, notMet, notStarted, computed, applicableIncomplete };
}

function computeReadiness(control: ControlDetail, form: Partial<ControlDetail>): ControlReadiness {
  const profile = control.linking_profile;
  const items: ReadinessItem[] = [];
  const status = (form.status || control.status || "NOT STARTED").trim();
  const narrative = (form.implementation_narrative || "").trim();
  const evidence = control.evidence || [];
  const assessorNotes = (form.assessor_notes || "").trim();

  if (status === "NOT APPLICABLE") {
    items.push({ id: "na_justification", label: "N/A justification", done: assessorNotes.length > 20, required: true, hint: "Explain why this control is not applicable to your environment" });
    items.push({ id: "narrative", label: "Implementation narrative (optional for N/A)", done: true, required: false, hint: "Helpful context for assessors but not required when marked N/A" });
    items.push({ id: "status", label: "Status determined", done: true, required: true, hint: "Control marked not applicable" });
  } else {
    items.push({ id: "narrative", label: "Implementation narrative", done: narrative.length > 0, required: true, hint: "Write how your organization meets this control" });
    items.push({ id: "evidence", label: `Evidence uploaded (${evidence.length})`, done: evidence.length > 0, required: true, hint: "Upload evidence to the Evidence Hub" });

    const reqPolicies = profile?.policies ? (Array.isArray(profile.policies) ? profile.policies : (profile.policies as { suggested?: string[] })?.suggested ?? []) : [];
    if (reqPolicies.length > 0) {
      const linkedTitles = new Set((form.linked_policies || []).map((p) => (p as Record<string, unknown>)?.title as string ?? ""));
      const matched = reqPolicies.filter((rp) => linkedTitles.has(rp)).length;
      items.push({ id: "policies", label: `Policy linked (${matched}/${reqPolicies.length})`, done: matched >= reqPolicies.length, required: true, hint: `Suggested: ${reqPolicies.slice(0, 3).join(", ")}` });
    }

    if (profile?.assets != null) {
      items.push({ id: "assets", label: "Asset linked", done: (form.linked_assets || []).length > 0, required: true, hint: "Link an asset to this control" });
    }

    if (profile?.team) {
      items.push({ id: "team", label: "Team member linked", done: (form.linked_team || []).length > 0, required: true, hint: "Link a team member to this control" });
    }

    items.push({ id: "owner", label: "Owner assigned", done: Boolean((form.owner || "").trim()), required: true, hint: "Assign a responsible owner" });
    items.push({ id: "status", label: "Status determined", done: status !== "NOT STARTED", required: true, hint: "Set the control status above" });

    if (status !== "NOT APPLICABLE" && _GAP_STATUSES.has(status)) {
      items.push({ id: "poam", label: "POA&M entry", done: (form.remediation_plan || "").trim().length > 0, required: true, hint: "Describe the gap, planned remediation, owner, and target date" });
    }
  }

  const required = items.filter((it) => it.required);
  const requiredDone = required.filter((it) => it.done);
  const pct = required.length > 0 ? Math.round((requiredDone.length / required.length) * 100) : 100;
  const label = pct === 100 ? "Complete" : pct >= 50 ? "Needs work" : "Incomplete";

  return { items, readiness_pct: pct, readiness_label: label, required_count: required.length, done_count: requiredDone.length };
}

function narrativePlaceholders(text: string): string[] {
  return [...new Set(text.match(SSP_PLACEHOLDER_RE) ?? [])].filter((ph) => !ph.startsWith("[Add "));
}

const BASE_STEPS: WizardStepDef[] = [
  { id: "status", title: "Status", caption: "Is this control in place? Pick a status and review what auditors expect below." },
  { id: "evidence", title: "Evidence", caption: "Attach files (policies, screenshots, configs) or run an automated config check." },
  { id: "document", title: "Describe", caption: "Generate a narrative from your org profile and evidence, then review and save." },
  { id: "poam", title: "Fix plan", caption: "For gaps — who will fix this, by when, and what needs to happen (POA&M)." },
];

export default function ControlDetailPage() {
  const { controlId } = useParams();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const { dashboard, refreshDashboard, canEdit, settings, canValidate } = useLayout();
  const [control, setControl] = useState<ControlDetail | null>(null);
  const [guidance, setGuidance] = useState<ControlGuidance | null>(null);
  const [meta, setMeta] = useState<ControlMeta | null>(null);
  const [form, setForm] = useState<Partial<ControlDetail>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [exportingProof, setExportingProof] = useState(false);
  const [step, setStep] = useState(0);
  const [sprsPreview, setSprsPreview] = useState<string | null>(null);
  const [validationMsg, setValidationMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [navIds, setNavIds] = useState<string[]>([]);
  const [nextAssessment, setNextAssessment] = useState<Awaited<ReturnType<typeof api.nextControl>> | null>(null);

  const [comments, setComments] = useState<ControlDetail["comments"]>([]);
  const [teamMembers, setTeamMembers] = useState<string[]>([]);
  const [editorMode, setEditorMode] = useState<"edit" | "ssp">("edit");
  const [ingested, setIngested] = useState<string[] | null>(null);
  const [manuallyEdited, setManuallyEdited] = useState(false);
  const [narrativeModalOpen, setNarrativeModalOpen] = useState(false);
  const [draftActionLoading, setDraftActionLoading] = useState(false);
  const [tightenCurrentNarrative, setTightenCurrentNarrative] = useState(false);
  const [linkedFindings, setLinkedFindings] = useState<Record<string, unknown>[]>([]);
  const [availablePolicies, setAvailablePolicies] = useState<Record<string, unknown>[]>([]);
  const [availableAssets, setAvailableAssets] = useState<Record<string, unknown>[]>([]);
  const [availablePersonnel, setAvailablePersonnel] = useState<Record<string, unknown>[]>([]);
  const [showAddPolicy, setShowAddPolicy] = useState(false);
  const [showAddAsset, setShowAddAsset] = useState(false);
  const [showAddTeam, setShowAddTeam] = useState(false);
  const [showAllPolicies, setShowAllPolicies] = useState(false);
  const [showAddSubcontractor, setShowAddSubcontractor] = useState(false);
  const [availableSubcontractors, setAvailableSubcontractors] = useState<Record<string, unknown>[]>([]);
  const [linkedRisks, setLinkedRisks] = useState<Record<string, unknown>[]>([]);
  const [linkedIncidents, setLinkedIncidents] = useState<Record<string, unknown>[]>([]);
  const [linkedAudits, setLinkedAudits] = useState<Record<string, unknown>[]>([]);
  const [linkedTraining, setLinkedTraining] = useState<Record<string, unknown>[]>([]);
  const isExecutive = settings?.current_role === "Executive";
  const poamOpen = form.status && !["MET", "NOT APPLICABLE", "INHERITED"].includes(form.status);
  const hasCollectorEvidence = useMemo(
    () => (control?.evidence ?? []).some((ev) => ev.filename.startsWith("collector_")),
    [control?.evidence],
  );
  const collectorEvidenceKey = useMemo(
    () =>
      (control?.evidence ?? [])
        .filter((ev) => ev.filename.startsWith("collector_"))
        .map((ev) => ev.filename)
        .join("|"),
    [control?.evidence],
  );
  const steps = useMemo(
    () => {
      const s = poamOpen ? [...BASE_STEPS] : BASE_STEPS.filter((st) => st.id !== "poam");
      if (control?.id) {
        return s.map((st) => ({
          ...st,
          caption: (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.1rem" }}>
              <strong style={{ fontSize: "1.05rem", letterSpacing: "-0.01em" }}>{control.id}</strong>
              <div className="muted" style={{ lineHeight: "1.4" }}>{control.name}</div>
            </div>
          ),
        }));
      }
      return s;
    },
    [poamOpen, control?.id, control?.name],
  );
  const documentStepIndex = useMemo(() => steps.findIndex((s) => s.id === "document"), [steps]);
  const currentStepId = steps[step]?.id ?? "status";

  const liveReadiness = useMemo(
    () => control ? computeReadiness(control, form) : undefined,
    [control, form],
  );

  const goToDocumentStep = () => {
    if (documentStepIndex >= 0) setStep(documentStepIndex);
  };


  useEffect(() => {
    if (!controlId) return;
    Promise.all([api.control(controlId), api.controlGuidance(controlId), api.controlMeta(controlId)]).then(([c, g, m]) => {
      setControl(c);
      setGuidance(g);
      setMeta(m);
      setForm(c);
      setComments(c.comments || []);
      setTeamMembers(c.team_members || settings?.team_members || []);
      const i: string[] = ["org_profile"];
      if (c.implementation_narrative?.trim()) i.unshift("existing_narrative");
      if (c.objectives?.length) i.push("objectives");
      if ((c.linked_policies?.length || 0) + (c.linked_assets?.length || 0) > 0) i.push("mappings");
      if (c.evidence?.length) i.push("evidence");
      if (c.linked_team?.length) i.push("team");
      if (c.linked_subcontractors?.length) i.push("subcontractors");
      if (c.examine || c.interview || c.test) i.push("assessment_plan");
      if (c.remediation_plan) i.push("remediation");
      setIngested(i);
    }).catch((err) => {
      setError("Failed to load control. Please refresh the page.");
      console.error("Control load error:", err);
    });
    api.controls().then((data) => setNavIds(data.controls.map((c) => c.id))).catch(console.error);
    api.nextControl().then(setNextAssessment).catch(console.error);
    authFetch(`/api/findings?control_id=${encodeURIComponent(controlId)}`)
      .then((r) => r.ok ? r.json() : { findings: [] })
      .then((d) => setLinkedFindings(d.findings || []))
      .catch(() => setLinkedFindings([]));
    authFetch("/api/policies?framework_tag=cmmc")
      .then((r) => r.ok ? r.json() : { policies: [] })
      .then((d) => setAvailablePolicies(d.policies || []))
      .catch(() => setAvailablePolicies([]));
    authFetch("/api/assets")
      .then((r) => r.ok ? r.json() : { assets: [] })
      .then((d) => setAvailableAssets(d.assets || []))
      .catch(() => setAvailableAssets([]));
    personnelApi.list().then(d => setAvailablePersonnel(d.personnel || [])).catch(() => {});
    authFetch(`/api/risks/by-control/${encodeURIComponent(controlId)}`, { credentials: "include" })
      .then((r) => r.ok ? r.json() : { risks: [] })
      .then((d) => setLinkedRisks(d.risks || []))
      .catch(() => setLinkedRisks([]));
    authFetch(`/api/incidents?control_id=${encodeURIComponent(controlId)}`, { credentials: "include" })
      .then((r) => r.ok ? r.json() : { incidents: [] })
      .then((d) => setLinkedIncidents(d.incidents || []))
      .catch(() => setLinkedIncidents([]));
    authFetch(`/api/audit-center/audits?control_id=${encodeURIComponent(controlId)}`, { credentials: "include" })
      .then((r) => r.ok ? r.json() : { audits: [] })
      .then((d) => setLinkedAudits(d.audits || []))
      .catch(() => setLinkedAudits([]));
    authFetch(`/api/training/modules?control_id=${encodeURIComponent(controlId)}`, { credentials: "include" })
      .then((r) => r.ok ? r.json() : { modules: [] })
      .then((d) => setLinkedTraining(d.modules || []))
      .catch(() => setLinkedTraining([]));
    authFetch("/api/vendors")
      .then((r) => r.ok ? r.json() : { vendors: [] })
      .then((d) => setAvailableSubcontractors(d.vendors || []))
      .catch(() => setAvailableSubcontractors([]));
  }, [controlId]);

  useEffect(() => {
    setStep(0);
    setSaved(false);
    setEditorMode("edit");
    setManuallyEdited(false);
  }, [controlId]);

  useEffect(() => {
    if (step >= steps.length) setStep(Math.max(0, steps.length - 1));
  }, [step, steps.length]);

  useEffect(() => {
    if (!controlId || !form.status || form.status === control?.status) {
      setSprsPreview(null);
      return;
    }
    api.sprsPreview(controlId, form.status).then((p) => {
      setSprsPreview(`SPRS would change ${dashboard?.sprs_score ?? p.current_score} → ${p.projected_score} (${p.delta})`);
    }).catch(() => setSprsPreview(null));
  }, [controlId, form.status, control?.status, dashboard?.sprs_score]);

  const setField = (key: keyof ControlDetail, value: string) => {
    setForm((f) => ({ ...f, [key]: value }));
  };

  const saveControl = async () => {
    if (!controlId) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.patchControl(controlId, form);
      await refreshDashboard();
      setSaved(true);
      setSprsPreview(null);
      setManuallyEdited(false);
      const updated = await api.control(controlId);
      setControl(updated);
      setForm(updated);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setError(`Save failed: ${err}`);
    } finally {
      setSaving(false);
    }
  };

  const handleApplyNarrative = (narrative: string, newIngested: string[]) => {
    if (manuallyEdited && !window.confirm("This will overwrite your unsaved changes. Continue?")) return;
    setField("implementation_narrative", narrative);
    setForm((f) => ({ ...f, ai_generated: true }));
    setIngested(newIngested);
    setManuallyEdited(false);
    setNarrativeModalOpen(false);
  };

  const refreshControlAfterDraft = async () => {
    if (!controlId) return;
    const c = await api.control(controlId);
    setControl(c);
    return c;
  };

  const handleApproveDraft = async () => {
    if (!controlId) return;
    setDraftActionLoading(true);
    try {
      await api.approveAiDraft(controlId);
      const c = await refreshControlAfterDraft();
      if (c) setForm(c);
    } catch (err) {
      setError(`Approve failed: ${err}`);
    } finally {
      setDraftActionLoading(false);
    }
  };

  const handleRejectDraft = async () => {
    if (!controlId) return;
    setDraftActionLoading(true);
    try {
      await api.rejectAiDraft(controlId);
      await refreshControlAfterDraft();
    } catch (err) {
      setError(`Reject failed: ${err}`);
    } finally {
      setDraftActionLoading(false);
    }
  };

  const handleApproveDraftFromModal = async () => {
    setNarrativeModalOpen(false);
    await handleApproveDraft();
  };

  // Refreshes display-only control data (evidence list, automation coverage,
  // etc.) after an evidence/remediation-draft action. Deliberately does NOT
  // overwrite `form` — form holds in-progress, unsaved edits (status,
  // narrative, objectives...) made before the user clicks the main Save
  // button, and blindly replacing it with the server snapshot here would
  // silently discard those edits (e.g. a status change picked "MET" but
  // never persisted, because a later evidence/remediation draft apply reset
  // it back to the server's stale "NOT MET" before the real save fired).
  const onEvidenceUpdated = async () => {
    if (!controlId) return;
    const c = await api.control(controlId);
    setControl(c);
  };

  const onEvidenceSummaryApplied = (examine: string, test: string) => {
    setForm((f) => ({ ...f, examine, test }));
    onEvidenceUpdated();
  };

  const onValidateConfig = async (file: File) => {
    if (!controlId) return;
    setValidationMsg(null);
    try {
      const r = await api.validateConfig(controlId, file);
      if (r.passed) {
        setValidationMsg(`Validation passed: ${r.details.filter((d) => d.passed).map((d) => d.rule).join(", ")}`);
        // See onEvidenceUpdated: refresh display-only control data without
        // clobbering unsaved form edits.
        const c = await api.control(controlId);
        setControl(c);
      } else {
        const failed = r.details.filter((d) => !d.passed).map((d) => d.rule);
        setValidationMsg(`Failed rules: ${failed.join("; ")}`);
      }
    } catch (err) {
      setValidationMsg(String(err));
    }
  };

  const narrativeText = form.implementation_narrative || "";
  const placeholders = narrativePlaceholders(narrativeText);
  const narrativeRef = useRef<HTMLTextAreaElement | null>(null);

  const fitNarrativeHeight = () => {
    const el = narrativeRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.max(el.scrollHeight, 140)}px`;
  };

  useEffect(() => {
    fitNarrativeHeight();
  }, [narrativeText, step]);

  if (!control || !guidance) {
    if (error) return <div className="page"><p className="banner error">{error}</p></div>;
    return <PageSkeleton variant="detail" />;
  }

  const status = form.status || control.status || "";
  const examine = (form.examine ?? control.examine ?? "").trim();
  const interview = (form.interview ?? control.interview ?? "").trim();
  const test = (form.test ?? control.test ?? "").trim();
  const hasPolicy = Boolean(examine || interview);
  const hasTechnical = Boolean(test) || (control.evidence?.length ?? 0) > 0;
  const documentedOnly = status === "MET" && hasPolicy && !hasTechnical;

  const navIndex = controlId ? navIds.indexOf(controlId) : -1;
  const prevId = navIndex > 0 ? navIds[navIndex - 1] : null;
  const nextId = navIndex >= 0 && navIndex < navIds.length - 1 ? navIds[navIndex + 1] : null;
  const continueId = nextAssessment?.next_control_id;

  const renderGuidanceBody = () => (
    <>
      {guidance.org_context_used && guidance.stack_pattern && (
        <p className="muted guidance-stack-note">
          Starter uses your environment profile ({guidance.stack_pattern}). Edit before saving.
        </p>
      )}
      {guidance.plain_summary && <p className="guidance-plain">{guidance.plain_summary}</p>}
      {guidance.catalog_description && (
        <p>
          <span className="guidance-label">Typical implementation:</span>{" "}
          {guidance.catalog_description}
        </p>
      )}
      {guidance.objectives.length > 0 && (
        <>
          <p className="guidance-label">Assessment objectives (NIST 800-171A):</p>
          <ul className="guidance-list">
            {guidance.objectives.map((o) => (
              <li key={o}>{o}</li>
            ))}
          </ul>
        </>
      )}
      {guidance.evidence_hints.length > 0 && (
        <>
          <p className="guidance-label">Evidence auditors look for:</p>
          <ul className="guidance-list">
            {guidance.evidence_hints.map((h) => (
              <li key={h}>{h}</li>
            ))}
          </ul>
        </>
      )}
      {guidance.minimum_proof && guidance.minimum_proof.evidence_types.length > 0 && (
        <>
          <p className="guidance-label">Automated evidence collectors can help with:</p>
          <ul className="guidance-list">
            {guidance.minimum_proof.evidence_types.map((item) => (
              <li key={item.type}>
                {item.label}
                {item.connectors.length > 0 && (
                  <span className="muted"> — run {item.connectors.join(", ")} on Integrations</span>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
      {guidance.objectives.length === 0 && guidance.family_prompts.length > 0 && (
        <p className="muted guidance-caption">No catalog objectives for this control — use family prompts below.</p>
      )}
      {guidance.family_prompts.length > 0 && (
        <>
          <p className="guidance-label">Family-level prompts ({guidance.family}):</p>
          <ul className="guidance-list">
            {guidance.family_prompts.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </>
      )}
    </>
  );

  const renderStatusFields = () => (
    <div className="form-grid">
      <div>
        <label htmlFor="status">How is this control implemented?</label>
        <select
          id="status"
          value={form.status || ""}
          disabled={!canEdit}
          onChange={(e) => setField("status", e.target.value)}
        >
          {control.status_options.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        {sprsPreview && <p className="muted sprs-preview">{sprsPreview}</p>}
        <div className="control-coverage-row">
          <AutoBadge badge={control.auto_badge} />
          <AutomationCoverageBadge coverage={control.automation_coverage} />
        </div>
      </div>
      <div>
        <label htmlFor="maturity">Maturity</label>
        <select
          id="maturity"
          value={form.maturity || ""}
          disabled={!canEdit}
          onChange={(e) => setField("maturity", e.target.value)}
        >
          {(control.maturity_options ?? []).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
    </div>
  );

  const renderObjectivesSection = () => {
    const objs = form.objectives ?? control.objectives ?? [];
    if (objs.length === 0) return null;
    const assessment = assessObjectives(objs);
    const controlStatus = (form.status || control.status || "").toUpperCase().trim();
    const metWithoutObjectives =
      controlStatus === "MET" && assessment != null && assessment.applicableIncomplete > 0;
    const notMetDespiteObjectives =
      controlStatus === "NOT MET" && assessment != null && assessment.applicableIncomplete === 0 && assessment.metOrNa === assessment.total;

    return (
      <div className="objectives-section">
        <h3>Assessment objectives (NIST 800-171A)</h3>
        {assessment && (
          <p className="objectives-advisory">
            Objectives: <strong>{assessment.metOrNa}/{assessment.total}</strong> Met or N/A
            {" · "}Advisory status: <strong>{assessment.computed}</strong>
          </p>
        )}
        {metWithoutObjectives && (
          <div className="banner warning objectives-mismatch" role="status">
            Status is Met, but {assessment!.applicableIncomplete} of {assessment!.total} objectives are still open.
          </div>
        )}
        {notMetDespiteObjectives && (
          <div className="banner warning objectives-mismatch" role="status">
            All objectives are Met or N/A, but control status is Not Met.
          </div>
        )}
        <div className="objectives-list">
          {objs.map((obj, i) => {
            const currentStatus = form.objectives?.[i]?.status ?? obj.status ?? "NOT_STARTED";
            const hasGuidance = obj.deliverable && obj.kind;
            const kindLabel: Record<string, string> = {
              policy: "written policy",
              config: "config evidence",
              evidence: "evidence",
              test: "test result",
              diagram: "diagram",
            };
            const isMet = currentStatus === "MET" || currentStatus === "NA";
            return (
              <div key={obj.letter} className="objective-item" data-status={currentStatus}>
                <span className="objective-letter">{obj.letter}</span>
                <span className="objective-text">{obj.text}</span>
                <select
                  className="objective-status-select"
                  value={currentStatus}
                  disabled={!canEdit}
                  onChange={(e) => {
                    const updated = [...(form.objectives ?? objs)];
                    updated[i] = { ...updated[i], status: e.target.value };
                    setForm((f: Partial<ControlDetail>) => ({ ...f, objectives: updated }));
                  }}
                  aria-label={`Objective ${obj.letter} status`}
                >
                  <option value="NOT_STARTED">Not Started</option>
                  <option value="MET">Met</option>
                  <option value="NOT_MET">Not Met</option>
                  <option value="NA">N/A</option>
                </select>
                {hasGuidance && (
                  <details className="objective-guidance">
                    <summary>
                      {isMet ? (
                        <span className="objective-guidance-met">{obj.deliverable}</span>
                      ) : (
                        <span className="objective-guidance-needed">
                          {obj.deliverable} ({kindLabel[obj.kind || "evidence"] || obj.kind})
                        </span>
                      )}
                    </summary>
                    {obj.how && <p className="objective-guidance-body">{obj.how}</p>}
                  </details>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderNarrativeField = () => (
    <>
      {control.ai_draft && (
        <div className="panel" style={{ marginTop: 10, borderColor: "var(--warning)" }}>
          <div className="panel-body" style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <span className="badge badge-warning" style={{ flexShrink: 0 }}>AI draft · pending review</span>
            <span className="muted" style={{ flex: 1, fontSize: "0.85rem", minWidth: 180 }}>
              Generated {control.ai_draft_created_at ? control.ai_draft_created_at.slice(0, 16).replace("T", " ") : ""}
              {control.ai_draft_method ? ` · source: ${control.ai_draft_method}` : ""} — your current narrative is untouched until approved.
            </span>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={!canEdit || draftActionLoading}
              onClick={handleApproveDraft}
            >
              Approve & replace
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={!canEdit || draftActionLoading}
              onClick={handleRejectDraft}
            >
              Reject
            </button>
          </div>
        </div>
      )}
      <label htmlFor="narrative">SSP description</label>
      <p className="field-hint muted">How your organization meets this control — this text is included in your System Security Plan export.</p>
      <textarea
        id="narrative"
        ref={narrativeRef}
        className={`ssp-narrative-textarea${placeholders.length > 0 ? " has-ssp-placeholders" : ""}`}
        value={narrativeText}
        disabled={!canEdit}
        onChange={(e) => {
          setField("implementation_narrative", e.target.value);
          setManuallyEdited(true);
          requestAnimationFrame(fitNarrativeHeight);
        }}
        rows={6}
      />
      <div className="btn-row" style={{ alignItems: "center", flexWrap: "nowrap", gap: 12 }}>
        {(control.ai_generated || form.ai_generated) && (
          <span className="badge badge-warning" title="Generated by AI — review facts before approving for auditors">
            AI draft · needs review
          </span>
        )}
        <button type="button" className="btn-primary btn-sm" onClick={async () => {
          if (controlId) {
            try { await api.patchControl(controlId, form); } catch {}
          }
          setNarrativeModalOpen(true);
        }} disabled={!canEdit}>
          AI Draft
        </button>
        <label className="muted" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.85rem", margin: 0, flexShrink: 0 }}>
          <input
            type="checkbox"
            style={{ width: "auto" }}
            checked={tightenCurrentNarrative}
            disabled={!canEdit || !narrativeText.trim()}
            onChange={(e) => setTightenCurrentNarrative(e.target.checked)}
          />
          use current narrative
        </label>
      </div>
    </>
  );

  const renderDocumentFields = () => (
    <div className="form-grid">
      <div className="span-2">
        {renderNarrativeField()}
      </div>
      {renderComplianceFields()}
      {hasCollectorEvidence && canEdit && (
        <div className="span-2">
          <CollectorEvidenceDraft
            key={control.id + collectorEvidenceKey}
            controlId={control.id}
            canEdit={canEdit}
            variant="document"
            onApplied={onEvidenceSummaryApplied}
          />
        </div>
      )}
      <div>
        <label htmlFor="examine">Policy or document to review</label>
        <p className="field-hint muted">What policy, SOP, or document would an assessor review?</p>
        <input id="examine" value={form.examine || ""} disabled={!canEdit} onChange={(e) => setField("examine", e.target.value)} />
      </div>
      <div>
        <label htmlFor="interview">Who to interview</label>
        <p className="field-hint muted">Interview — e.g. system administrator, ISO</p>
        <input id="interview" value={form.interview || ""} disabled={!canEdit} onChange={(e) => setField("interview", e.target.value)} />
      </div>
      <div>
        <label htmlFor="test">Technical test or check</label>
        <p className="field-hint muted">What test or verification would an assessor run?</p>
        <input id="test" value={form.test || ""} disabled={!canEdit} onChange={(e) => setField("test", e.target.value)} />
      </div>
      {documentedOnly && (
        <div className="span-2 banner warning documented-only-warning">
          <strong>Documented only</strong> — policy or interview mapping exists but no technical evidence
          (test, config validation, or uploaded file). Consider status: <strong>Partially Met</strong>.
        </div>
      )}
      <div className="span-2">
        <label htmlFor="notes">Internal notes</label>
        <p className="field-hint muted">For your team only — not included in the SSP export</p>
        <textarea id="notes" value={form.assessor_notes || ""} disabled={!canEdit} onChange={(e) => setField("assessor_notes", e.target.value)} rows={3} />
      </div>
      <div className="span-2">
        <OwnerSelect
          id="assignee"
          label="Assigned to"
          value={form.owner || ""}
          teamMembers={teamMembers}
          disabled={!canEdit}
          onChange={(v) => setField("owner", v)}
        />
      </div>
    </div>
  );

  const renderComplianceFields = () => {
    const cid = control.id || "";
    const isFips = cid === "SC.L2-3.13.11";
    const isIr = cid.startsWith("IR.L2-3.6");
    const isSc = cid.startsWith("SC.L2-3.13");
    if (!isFips && !isIr && !isSc) return null;
    return (
      <div className="compliance-section span-2">
        <h3>Compliance details (DFARS / FIPS)</h3>
        {isFips && (
          <div>
            <label htmlFor="fips_cert">FIPS Certificate Number</label>
            <p className="field-hint muted">NIST FIPS 140-2/140-3 validation certificate number (e.g. Cert. #4287)</p>
            <input id="fips_cert" value={form.fips_certificate_number || ""} disabled={!canEdit}
              onChange={(e) => setField("fips_certificate_number", e.target.value)} />
          </div>
        )}
        {isSc && (
          <div>
            <label htmlFor="cloud_auth">Cloud Authorization Status</label>
            <p className="field-hint muted">FedRAMP authorization or equivalency status for cloud services processing CUI</p>
            <select id="cloud_auth" value={form.cloud_authorization_status || ""} disabled={!canEdit}
              onChange={(e) => setField("cloud_authorization_status", e.target.value)}>
              <option value="">Not specified</option>
              <option value="FedRAMP Moderate">FedRAMP Moderate</option>
              <option value="FedRAMP High">FedRAMP High</option>
              <option value="FedRAMP Equivalent">FedRAMP Equivalent</option>
              <option value="Not Authorized">Not Authorized</option>
            </select>
          </div>
        )}
        {isIr && (
          <div>
            <label>
              <input type="checkbox" checked={!!form.dfars_72hr_reporting_enabled} disabled={!canEdit}
                onChange={(e) => setForm((f) => ({ ...f, dfars_72hr_reporting_enabled: e.target.checked }))} />
              {" "}DFARS 72-hour incident reporting configured (DIBNet / DoD reporting)
            </label>
          </div>
        )}
      </div>
    );
  };

  const onRemediationSummaryApplied = (remediationPlan: string) => {
    setForm((f) => ({ ...f, remediation_plan: remediationPlan }));
    onEvidenceUpdated();
  };

  const renderPoamFields = () => (
    <div className="form-grid">
      {hasCollectorEvidence && canEdit && poamOpen && (
        <div className="span-2">
          <CollectorRemediationDraft
            key={control.id + collectorEvidenceKey}
            controlId={control.id}
            canEdit={canEdit}
            onApplied={onRemediationSummaryApplied}
          />
        </div>
      )}
      <div className="span-2">
        <label htmlFor="remediation">Plan to fix this gap</label>
        <p className="field-hint muted">Goes on your POA&amp;M (Plan of Action &amp; Milestones) export</p>
        <textarea id="remediation" value={form.remediation_plan || ""} disabled={!canEdit} onChange={(e) => setField("remediation_plan", e.target.value)} rows={3} />
      </div>
      <div>
        <OwnerSelect
          id="owner"
          label="Remediation owner"
          value={form.owner || ""}
          teamMembers={teamMembers}
          disabled={!canEdit}
          onChange={(v) => setField("owner", v)}
        />
      </div>
      <div>
        <label htmlFor="target">Target date</label>
        <input id="target" type="date" value={(form.target_date || "").slice(0, 10)} disabled={!canEdit} onChange={(e) => setField("target_date", e.target.value)} />
      </div>
      <div>
        <label htmlFor="cost">Estimated cost</label>
        <input id="cost" value={form.estimated_cost || ""} disabled={!canEdit} onChange={(e) => setField("estimated_cost", e.target.value)} />
      </div>
      <div>
        <label htmlFor="likelihood">Likelihood</label>
        <select id="likelihood" value={form.likelihood || ""} disabled={!canEdit} onChange={(e) => setField("likelihood", e.target.value)}>
          {(control.likelihood_options ?? []).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="impact">Impact</label>
        <select id="impact" value={form.impact || ""} disabled={!canEdit} onChange={(e) => setField("impact", e.target.value)}>
          {(control.impact_options ?? []).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
      {meta && (
        <div className="span-2">
          <p className="muted">POA&M remediation priority</p>
          <RiskBadge level={meta.risk_level} />
        </div>
      )}
    </div>
  );

  const renderEvidenceSection = () => (
    <>
      {hasCollectorEvidence && canEdit && (
        <CollectorEvidenceDraft
          key={control.id + collectorEvidenceKey}
          controlId={control.id}
          canEdit={canEdit}
          variant="evidence"
          onApplied={onEvidenceSummaryApplied}
          onGoToDocumentStep={goToDocumentStep}
        />
      )}
      <EvidencePanel
        controlId={control.id}
        evidence={control.evidence}
        historySummary={control.evidence_history_summary || []}
        canEdit={canEdit}
        onUpdated={onEvidenceUpdated}
        expectedEvidenceTypes={control?.linking_profile?.evidence_types || []}
      />
      {meta?.validation_rules && canValidate && (
        <div className="validation-block">
          <label>Config validation ({control.id})</label>
          <p className="muted">
            Upload a config file to auto-check:{" "}
            {meta.validation_rules.rules.map((r) => r.description).join("; ")}
          </p>
          <input
            type="file"
            accept={meta.validation_rules.file_types.join(",")}
            disabled={!canEdit}
            onChange={(e) => e.target.files?.[0] && onValidateConfig(e.target.files[0])}
          />
          {validationMsg && <p className="muted">{validationMsg}</p>}
        </div>
      )}
    </>
  );

  const renderWizardStep = () => {
    if (currentStepId === "status") {
      return (
        <>
          <div className="guidance-inline">{renderGuidanceBody()}</div>
          {renderStatusFields()}
          {renderObjectivesSection()}
        </>
      );
    }
    if (currentStepId === "evidence") return renderEvidenceSection();
    if (currentStepId === "document") return renderDocumentFields();
    if (currentStepId === "poam") return renderPoamFields();
    return null;
  };

  function renderLinkedSection(kind: "policies" | "assets" | "team") {
    const profile = control?.linking_profile;
    const kindKey = kind === "policies" ? "policies" : kind === "assets" ? "assets" : "team";
    const requirement = profile?.[kindKey];

    if (requirement === null || requirement === undefined) return null;

    const suggested: string[] = Array.isArray(requirement) ? requirement : (requirement as { suggested?: string[] })?.suggested ?? [];

    const linked = (Array.isArray(form[kind === "policies" ? "linked_policies" : kind === "assets" ? "linked_assets" : "linked_team"])
      ? form[kind === "policies" ? "linked_policies" : kind === "assets" ? "linked_assets" : "linked_team"]
      : []) as Record<string, unknown>[] | string[];
    const showState = kind === "policies" ? showAddPolicy : kind === "assets" ? showAddAsset : showAddTeam;
    const setShow = kind === "policies" ? setShowAddPolicy : kind === "assets" ? setShowAddAsset : setShowAddTeam;
    const label = kind === "policies" ? "Linked Policies" : kind === "assets" ? "Linked Assets" : "Linked Team";
    const fieldKey = kind === "policies" ? "linked_policies" : kind === "assets" ? "linked_assets" : "linked_team";

    const available: Record<string, unknown>[] = kind === "policies" ? availablePolicies :
      kind === "assets" ? availableAssets :
      availablePersonnel;

    const getId = (item: unknown) => {
      if (kind === "team") {
        if (typeof item === "string") return item;
        return String((item as Record<string, unknown>)?.id ?? "");
      }
      return String((item as Record<string, unknown>)?.id ?? (item as Record<string, unknown>)?.asset_id ?? "");
    };
    const getLabel = (item: unknown) => {
      if (kind === "team") {
        if (typeof item === "string") return item;
        return String((item as Record<string, unknown>)?.name ?? "");
      }
      return String((item as Record<string, unknown>)?.title ?? (item as Record<string, unknown>)?.name ?? (item as Record<string, unknown>)?.asset_name ?? "");
    };

    const alreadyLinked = new Set(linked.map((l) => {
      if (kind === "team") {
        if (typeof l === "string") return l;
        return String((l as Record<string, unknown>)?.id ?? "");
      }
      return String((l as Record<string, unknown>)?.id ?? (l as Record<string, unknown>)?.asset_id ?? "");
    }));

    const availablePool = kind === "assets" && suggested.length > 0
      ? available.filter((a) => {
          const t = String((a as Record<string, unknown>)?.asset_type ?? (a as Record<string, unknown>)?.type ?? "");
          return suggested.includes(t);
        })
      : available;
    const filteredAvailable = availablePool.filter((a) => !alreadyLinked.has(getId(a)));

    const linkedTypeNames = new Set(
      linked.map((l) =>
        kind === "assets"
          ? String((l as Record<string, unknown>)?.asset_type ?? (l as Record<string, unknown>)?.type ?? "")
          : kind === "policies"
          ? String((l as Record<string, unknown>)?.title ?? "")
          : kind === "team"
          ? String(l)
          : ""
      ).filter(Boolean)
    );
    const suggestedAvailable = suggested.filter((s) => !linkedTypeNames.has(s));

    return (
      <div className="panel" key={kind}>
        <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <strong>{label} ({linked.length})</strong>
            {suggested.length > 0 && (
              <span className="muted" style={{ fontSize: "0.8rem", marginLeft: 8 }}>
                Suggested: {suggested.join(", ")}
              </span>
            )}
          </div>
          {canEdit && (
            <button className="btn btn-sm btn-ghost" onClick={() => setShow(!showState)}>
              {showState ? "Cancel" : "+ Add"}
            </button>
          )}
        </div>
        {showState && canEdit && (
          <div className="panel-body" style={{ maxHeight: "auto", overflowY: "auto" }}>
            {kind !== "assets" && kind !== "team" && suggestedAvailable.length > 0 && (
              <div style={{ marginBottom: 8 }}>
                <p className="muted" style={{ fontSize: "0.75rem", marginBottom: 4 }}>Recommended for this control:</p>
                {suggestedAvailable.map((s) => (
                  <button
                    key={s}
                    className="btn btn-sm btn-ghost"
                    style={{ display: "block", width: "100%", textAlign: "left", padding: "4px 8px", marginBottom: 2, fontWeight: 500 }}
                      onClick={() => {
                        const toAdd = [...linked, { name: s, title: s }];
                        setFormField(fieldKey, toAdd);
                        setShow(false);
                      }}
                  >
                    {s} ✓
                  </button>
                ))}
              </div>
            )}
            {kind === "policies" && !showAllPolicies && filteredAvailable.length > 0 && (
              <button
                className="btn btn-sm btn-ghost"
                style={{ display: "block", width: "100%", textAlign: "left", padding: "4px 8px", marginBottom: 2, color: "var(--primary)" }}
                onClick={() => setShowAllPolicies(true)}
              >
                Show all policies ({filteredAvailable.length} more) ▾
              </button>
            )}
            {(kind !== "policies" || showAllPolicies) && (
              filteredAvailable.length === 0 ? (
                <p className="muted">
                  {kind === "assets" && suggested.length > 0
                    ? `No assets with type: ${suggested.join(", ")}. Add matching assets in Organization → Asset inventory.`
                    : `No more ${kind} available to link.`}
                </p>
              ) : (
                <>
                  {kind === "policies" && (
                    <button
                      className="btn btn-sm btn-ghost"
                      style={{ display: "block", width: "100%", textAlign: "left", padding: "4px 8px", marginBottom: 2, color: "var(--primary)" }}
                      onClick={() => setShowAllPolicies(false)}
                    >
                      ▴ Hide full list
                    </button>
                  )}
                  {filteredAvailable.map((item) => {
                    return (
                      <button
                        key={getId(item)}
                        className="btn btn-sm btn-ghost"
                        style={{ display: "block", width: "100%", textAlign: "left", padding: "4px 8px", marginBottom: 2 }}
                        onClick={() => {
                          const toAdd = kind === "team" ? [...linked, { id: item.id, name: item.name } as Record<string, unknown>] : [...linked, item];
                          setFormField(fieldKey, toAdd);
                          setShow(false);
                        }}
                      >
                        {getLabel(item)}
                        {kind === "policies" ? ` (v${item.version ?? "?"})` : ""}
                      </button>
                    );
                  })}
                </>
              )
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

  function renderLinkedSubcontractors() {
    const profile = control?.linking_profile;
    const suggested: string[] = profile?.subcontractors ?? [];
    const linked = (Array.isArray(form.linked_subcontractors) ? form.linked_subcontractors : []) as Record<string, unknown>[];
    const label = "Linked Subcontractors";

    const getId = (item: unknown) => String((item as Record<string, unknown>)?.id ?? "");
    const getLabel = (item: unknown) => String((item as Record<string, unknown>)?.title ?? (item as Record<string, unknown>)?.name ?? "");
    const alreadyLinked = new Set(linked.map((l) => getId(l)));
    const filteredAvailable = availableSubcontractors.filter((s) => !alreadyLinked.has(getId(s)));

    return (
      <div className="panel">
        <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <strong>{label} ({linked.length})</strong>
            {suggested.length > 0 && (
              <span className="muted" style={{ fontSize: "0.8rem", marginLeft: 8 }}>
                Suggested types: {suggested.join(", ")}
              </span>
            )}
          </div>
          {canEdit && (
            <button className="btn btn-sm btn-ghost" onClick={() => setShowAddSubcontractor(!showAddSubcontractor)}>
              {showAddSubcontractor ? "Cancel" : "+ Add"}
            </button>
          )}
        </div>
        {linked.length > 0 && (
          <div className="panel-body" style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
            {linked.map((s) => (
              <div key={getId(s)} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.25rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                <span>{getLabel(s)}</span>
                {canEdit && (
                  <button className="btn btn-sm btn-danger" onClick={() => {
                    const next = linked.filter((l) => getId(l) !== getId(s));
                    setFormField("linked_subcontractors", next);
                  }}>
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
        {showAddSubcontractor && canEdit && (
          <div className="panel-body" style={{ maxHeight: 200, overflowY: "auto" }}>
            {filteredAvailable.length === 0 ? (
              <p className="muted">No more subcontractors available to link.</p>
            ) : (
              filteredAvailable.map((s) => (
                <button
                  key={getId(s)}
                  className="btn btn-sm btn-ghost"
                  style={{ display: "block", width: "100%", textAlign: "left", padding: "4px 8px", marginBottom: 2 }}
                  onClick={() => {
                    const toAdd = [...linked, { id: getId(s), name: getLabel(s) }];
                    setFormField("linked_subcontractors", toAdd);
                    setShowAddSubcontractor(false);
                  }}
                >
                  {getLabel(s)}
                </button>
              ))
            )}
          </div>
        )}
      </div>
    );
  }

  const setFormField = (key: string, value: unknown) =>
    setForm((f) => ({ ...f, [key]: value }));

  const exportProofPackage = async () => {
    if (!controlId) return;
    setExportingProof(true);
    try {
      await api.downloadProofPackage(controlId);
    } catch (err) {
      setError(String(err));
    } finally {
      setExportingProof(false);
    }
  };

  return (
    <>
      <div className="control-detail-nav">
        <p className="muted">
          <Link to={`${fwBase}/controls`}>← Controls</Link> · {control.family} · {control.weight_badge || `${control.weight} PT`}
        </p>
        <div className="control-detail-nav-buttons">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            disabled={exportingProof}
            onClick={() => exportProofPackage()}
            title="Download auditor proof package (JSON)"
          >
            {exportingProof ? "Exporting…" : "Export proof package"}
          </button>
          <a
            className="btn btn-secondary btn-sm"
            href={apiUrl(`/api/evidence-hub/export?framework_id=CMMC&control_id=${encodeURIComponent(control.id)}`)}
            download
            title="Download all evidence files mapped to this control (ZIP + manifest)"
          >
            Evidence package
          </a>
          {prevId && (
            <Link className="btn btn-secondary btn-sm" to={`${fwBase}/controls/${encodeURIComponent(prevId)}`}>
              ← Previous
            </Link>
          )}
          {nextId && (
            <Link className="btn btn-secondary btn-sm" to={`${fwBase}/controls/${encodeURIComponent(nextId)}`}>
              Next →
            </Link>
          )}
          {continueId && continueId !== controlId && (
            <Link
              className="btn btn-primary btn-sm"
              to={`${fwBase}/controls/${encodeURIComponent(continueId)}`}
            >
              Continue assessment
            </Link>
          )}
        </div>
      </div>

      {control.scope_context && (
        <div className={`banner ${control.scope_context.kind === "scoping" ? "warning" : "info"} scope-banner`}>
          <strong>{control.scope_context.title}</strong>
          {control.scope_context.org_responsibility ? (
            <div className="scope-detail">
              <p><strong>Your org:</strong> {control.scope_context.org_responsibility}</p>
              {control.scope_context.provider_responsibility && (
                <p><strong>Provider:</strong> {control.scope_context.provider_responsibility}</p>
              )}
              {control.scope_context.citation && (
                <p className="muted"><em>Citation:</em> {control.scope_context.citation}</p>
              )}
            </div>
          ) : (
            <p className="muted">{control.scope_context.detail}</p>
          )}
        </div>
      )}

      {meta?.dependencies_at_risk && meta.dependencies_at_risk.length > 0 && (
        <div className="banner warning">
          Related controls at risk: {meta.dependencies_at_risk.join(", ")}
        </div>
      )}

      {meta?.at_risk_points ? (
        <div className="banner warning">
          At risk: −{meta.at_risk_points} points from score of 110 if unchanged
        </div>
      ) : (
        <div className="banner success">No SPRS deduction at current status</div>
      )}

      <ReadinessChecklist readiness={liveReadiness} />

      {isExecutive ? (
        <div className="panel">
          <div className="panel-header"><strong>{control.id}</strong></div>
          <div className="panel-body">
            <label htmlFor="exec-status">Status</label>
            <select
              id="exec-status"
              value={form.status || ""}
              disabled={!canEdit}
              onChange={(e) => setField("status", e.target.value)}
            >
              {control.status_options.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <div className="btn-row">
              <button type="button" className="btn-primary" disabled={saving || !canEdit} onClick={() => saveControl()}>
                Save
              </button>
            </div>
          </div>
        </div>
      ) : (
        <>
          <ControlDetailWizard
            steps={steps}
            step={step}
            onStepChange={setStep}
            editorMode={editorMode}
            onEditorModeChange={setEditorMode}
            saving={saving}
            saved={saved}
            canEdit={canEdit}
            onSave={saveControl}
          >
            {editorMode === "ssp" ? (
              <SspControlPreview control={control} form={form} />
            ) : (
              renderWizardStep()
            )}
          </ControlDetailWizard>

          <div className="panel-stack">
            {renderLinkedSection("policies")}
            {renderLinkedSection("assets")}
            {renderLinkedSection("team")}
            {renderLinkedSubcontractors()}
            {linkedFindings.length > 0 && (
              <div className="panel">
                <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <strong>Related Findings ({linkedFindings.length})</strong>
                  <Link to={`${fwBase}/findings`} className="btn btn-sm btn-ghost">
                    View All
                  </Link>
                </div>
                <div className="panel-body">
                  {linkedFindings.map((f) => (
                    <div key={f.id as string} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.35rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span className={`badge ${f.severity === "critical" || f.severity === "high" ? "badge-danger" : f.severity === "medium" ? "badge-warning" : "badge-muted"}`}>
                          {f.severity as string}
                        </span>
                        <span>
                          <Link to={`${fwBase}/findings`} style={{ fontWeight: 500 }}>{f.title as string}</Link>
                          <p className="muted" style={{ fontSize: "0.78rem", margin: "1px 0 0" }}>
                            {(f.status as string)?.replace(/_/g, " ")} · Owner: {f.owner as string}
                          </p>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="panel">
              <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <strong>Linked Risks ({linkedRisks.length})</strong>
                  {control?.linking_profile?.risk_types && control.linking_profile.risk_types.length > 0 && (
                    <span className="muted" style={{ fontSize: "0.8rem", marginLeft: 8 }}>
                      Types: {control.linking_profile.risk_types.join(", ")}
                    </span>
                  )}
                </div>
                {canEdit && (
                  <button className="btn btn-sm btn-ghost" onClick={() => controlId && navigate(`${fwBase}/risks?action=new&control_id=${encodeURIComponent(controlId)}`)}>
                    + Add
                  </button>
                )}
              </div>
              {linkedRisks.length > 0 ? (
                <div className="panel-body">
                  {linkedRisks.map((r) => (
                    <div key={r.id as string} className="risk-card">
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <strong>{r.title as string}</strong>
                          <p className="muted" style={{ fontSize: "0.8rem", margin: "2px 0 0" }}>
                            Residual: {r.residual_level as string} ({r.residual_score as number}) · Status: {(r.status as string)?.replace(/_/g, " ")}
                          </p>
                        </div>
                        <span
                          className={`risk-badge ${
                            r.residual_level === "critical" || r.residual_level === "high"
                              ? "risk-critical"
                              : r.residual_level === "medium"
                                ? "risk-high"
                                : "risk-low"
                          }`}
                        >
                          {r.residual_level as string}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="panel">
              <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>Linked Incidents ({linkedIncidents.length})</strong>
                {canEdit && (
                  <button className="btn btn-sm btn-ghost" onClick={() => controlId && navigate(`${fwBase}/incidents/new?control_id=${encodeURIComponent(controlId)}`)}>
                    + Add
                  </button>
                )}
              </div>
              {linkedIncidents.length > 0 ? (
                <div className="panel-body">
                  {linkedIncidents.map((inc) => (
                    <div key={inc.id as string} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.35rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span className={`badge ${inc.severity === "critical" || inc.severity === "high" ? "badge-danger" : inc.severity === "medium" ? "badge-warning" : "badge-muted"}`}>
                          {inc.severity as string}
                        </span>
                        <span>
                          <strong style={{ fontWeight: 500 }}>{inc.title as string}</strong>
                          <p className="muted" style={{ fontSize: "0.78rem", margin: "1px 0 0" }}>
                            {(inc.status as string)?.replace(/_/g, " ")} · {inc.model_name as string || "N/A"}
                          </p>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="panel">
              <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>Linked Audits ({linkedAudits.length})</strong>
                {canEdit && (
                  <button className="btn btn-sm btn-ghost" onClick={() => controlId && navigate(`${fwBase}/audits/new?control_id=${encodeURIComponent(controlId)}`)}>
                    + Add
                  </button>
                )}
              </div>
              {linkedAudits.length > 0 ? (
                <div className="panel-body">
                  {linkedAudits.map((audit) => (
                    <div key={audit.id as string} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.35rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                      <div>
                        <strong style={{ fontWeight: 500 }}>{audit.title as string}</strong>
                        <p className="muted" style={{ fontSize: "0.78rem", margin: "1px 0 0" }}>
                          {audit.audit_type as string} · Status: {(audit.status as string)?.replace(/_/g, " ")} · {audit.start_date as string || "N/A"}
                        </p>
                      </div>
                      <span className={`badge ${audit.status === "completed" ? "badge-success" : audit.status === "in_progress" ? "badge-warning" : "badge-muted"}`}>
                        {(audit.status as string)?.replace(/_/g, " ")}
                      </span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="panel">
              <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong>Linked Training ({linkedTraining.length})</strong>
                {canEdit && (
                  <button className="btn btn-sm btn-ghost" onClick={() => controlId && navigate(`${fwBase}/training`)}>
                    + Add
                  </button>
                )}
              </div>
              {linkedTraining.length > 0 ? (
                <div className="panel-body">
                  {linkedTraining.map((mod) => (
                    <div key={mod.id as string} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.35rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                      <div>
                        <strong style={{ fontWeight: 500 }}>{mod.title as string}</strong>
                        <p className="muted" style={{ fontSize: "0.78rem", margin: "1px 0 0" }}>
                          {mod.category as string || "General"} · Renewal: {mod.renewal_period_days as number}d
                        </p>
                      </div>
                      <span className={`badge ${mod.is_required ? "badge-warning" : "badge-muted"}`}>
                        {mod.is_required ? "Required" : "Optional"}
                      </span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>

          </div>
        </>
      )}

      {controlId && (
        <div style={{ marginTop: "1.25rem" }}>
          <ControlCommentsPanel
            controlId={controlId}
            comments={comments || []}
            canEdit={canEdit}
            onUpdated={(next) => {
              setComments(next);
              setControl((c) => (c ? { ...c, comments: next } : c));
            }}
          />
        </div>
      )}

      <NarrativePreviewModal
        open={narrativeModalOpen}
        controlId={controlId!}
        currentNarrative={form.implementation_narrative || ""}
        canEdit={canEdit}
        includeCurrentNarrative={tightenCurrentNarrative}
        onApply={handleApplyNarrative}
        onApproveDraft={handleApproveDraftFromModal}
        onClose={() => setNarrativeModalOpen(false)}
        availableIngested={ingested ?? []}
      />

    </>
  );
}
