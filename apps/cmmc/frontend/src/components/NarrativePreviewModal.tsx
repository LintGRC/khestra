import { useEffect, useRef, useState } from "react";
import { api } from "../api";

type Props = {
  open: boolean;
  controlId: string;
  currentNarrative: string;
  canEdit: boolean;
  /** Chosen on Control Detail before opening — feed current SSP text into AI when true. */
  includeCurrentNarrative: boolean;
  onApply: (narrative: string, ingested: string[]) => void;
  onClose: () => void;
  availableIngested: string[];
  onApproveDraft?: () => void | Promise<void>;
};

const COOLDOWN_MS = 5000;
const MAX_COUNT = 4;

export default function NarrativePreviewModal({
  open,
  controlId,
  currentNarrative,
  canEdit,
  includeCurrentNarrative,
  onApply,
  onClose,
  availableIngested,
  onApproveDraft,
}: Props) {
  const [narrative, setNarrative] = useState("");
  const [ingested, setIngested] = useState<string[]>([]);
  const [method, setMethod] = useState("");
  const [collectorCount, setCollectorCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [aiError, setAiError] = useState<string | null>(null);
  const [rateLimitMsg, setRateLimitMsg] = useState("");
  const [draftCreated, setDraftCreated] = useState(false);

  const genCount = useRef(0);
  const genLastAt = useRef(0);
  const isInitial = useRef(true);
  const currentRef = useRef<HTMLTextAreaElement | null>(null);
  const generatedRef = useRef<HTMLTextAreaElement | null>(null);

  const fitPreview = (el: HTMLTextAreaElement | null) => {
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.max(el.scrollHeight, 160)}px`;
  };

  useEffect(() => {
    if (!open) return;
    requestAnimationFrame(() => {
      fitPreview(currentRef.current);
      fitPreview(generatedRef.current);
    });
  }, [open, currentNarrative, narrative, loading]);

  const doGenerate = async () => {
    setError("");
    setRateLimitMsg("");

    const now = Date.now();
    if (!isInitial.current && now - genLastAt.current < COOLDOWN_MS) {
      const s = Math.ceil((COOLDOWN_MS - (now - genLastAt.current)) / 1000);
      setRateLimitMsg(`Please wait ${s}s before generating again`);
      return;
    }

    if (genCount.current >= MAX_COUNT) {
      setRateLimitMsg(`Maximum generations (${MAX_COUNT}) reached for this control. Refresh the page to try again.`);
      return;
    }

    setLoading(true);
    try {
      const result = await api.generateNarrative(controlId, true, true, includeCurrentNarrative);
      setNarrative(result.narrative);
      setIngested(result.ingested || []);
      setMethod(result.method);
      setCollectorCount(result.collector_count);
      setAiError(result.ai_error);
      setDraftCreated(!!result.draft_created);
      if (!isInitial.current) {
        genCount.current += 1;
        genLastAt.current = Date.now();
      } else {
        genCount.current = 1;
        genLastAt.current = Date.now();
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
      isInitial.current = false;
    }
  };

  useEffect(() => {
    if (!open) return;
    isInitial.current = true;
    genCount.current = 0;
    genLastAt.current = 0;
    setNarrative("");
    setIngested([]);
    setMethod("");
    setCollectorCount(0);
    setError("");
    setRateLimitMsg("");
    setAiError(null);
    setDraftCreated(false);
    // Mode was chosen on the control page; generate immediately with that choice.
    const timer = setTimeout(() => void doGenerate(), 0);
    return () => clearTimeout(timer);
  }, [open, controlId, includeCurrentNarrative]);

  const handleApply = () => {
    if (!narrative) return;
    onApply(narrative, ingested);
  };

  if (!open) return null;

  const ingestedLabel = (s: string) => {
    const map: Record<string, string> = {
      existing_narrative: "Existing narrative",
      org_profile: "Org Profile",
      objectives: "171A Objectives",
      mappings: "Mappings",
      policies: "Policies",
      evidence: "Evidence",
      assets: "Assets",
      team: "Team",
      subcontractors: "Subcontractors",
      assessment_plan: "Assessment Plan",
      remediation: "Remediation",
    };
    return map[s] || s;
  };

  return (
    <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }} role="presentation">
      <div
        className="modal-panel narrative-preview-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Generate narrative"
      >
        <header className="modal-header">
          <h3>Generate narrative{loading ? "…" : ""}</h3>
          {!loading && method && (
            <span className="muted" style={{ marginLeft: 8, fontSize: "0.85rem" }}>
              Source: {method}{collectorCount > 0 ? ` · ${collectorCount} collector(s)` : ""}
              {" · "}
              {includeCurrentNarrative ? "tighten current" : "all inputs"}
            </span>
          )}
          <button type="button" className="btn-link btn-sm" onClick={onClose}>
            Close
          </button>
        </header>
        <div className="modal-body">
          {rateLimitMsg && (
            <p className="banner warning">{rateLimitMsg}</p>
          )}
          {error && (
            <p className="banner warning">{error}</p>
          )}
          {aiError && (
            <p className="banner error">AI fallback error: {aiError}</p>
          )}
          {draftCreated && (
            <p className="banner warning">
              AI draft saved as <strong>pending</strong> — your current narrative is untouched until you approve it.
            </p>
          )}
          <div className="narrative-preview-grid">
            <div className="narrative-preview-pane">
              <label>Current narrative</label>
              <textarea
                ref={currentRef}
                className="narrative-preview-textarea ssp-narrative-textarea"
                readOnly
                rows={8}
                value={currentNarrative || "(empty)"}
              />
            </div>
            <div className="narrative-preview-pane">
              <label>Generated narrative</label>
              <textarea
                ref={generatedRef}
                className="narrative-preview-textarea ssp-narrative-textarea"
                readOnly
                rows={8}
                value={loading ? "Generating…" : narrative || "(empty)"}
              />
              {method ? (
                <div className="narrative-sources" style={{ marginTop: 8 }}>
                  <div className="muted" style={{ marginBottom: 6, fontSize: "0.8rem" }}>
                    Inputs used for this draft
                    {method === "ai" ? " (sent to AI)" : ""}:
                  </div>
                  {method === "preserved"
                    ? <span className="pill">Manual</span>
                    : (ingested.length ? ingested : availableIngested).map((s) => (
                        <span key={s} className="pill" title={`Included in context: ${ingestedLabel(s)}`}>
                          {ingestedLabel(s)}
                        </span>
                      ))}
                </div>
              ) : availableIngested.length > 0 && (
                <div className="narrative-sources" style={{ marginTop: 8 }}>
                  <span className="muted" style={{ marginRight: 8, fontSize: "0.8rem" }}>
                    Available inputs:
                  </span>
                  {availableIngested.map((s) => (
                    <span key={s} className="pill">{ingestedLabel(s)}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        <footer className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            disabled={loading || !canEdit || !!rateLimitMsg}
            onClick={() => {
              isInitial.current = false;
              void doGenerate();
            }}
          >
            {loading ? "Generating…" : "Regenerate"}
          </button>
          <button
            type="button"
            className="btn btn-primary"
            disabled={loading || !narrative}
            onClick={draftCreated && onApproveDraft ? () => void onApproveDraft!() : handleApply}
          >
            {draftCreated ? "Approve draft" : "Apply"}
          </button>
        </footer>
      </div>
    </div>
  );
}
