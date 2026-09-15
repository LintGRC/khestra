import { useEffect, useState } from "react";
import { api } from "../api";
import ChevronIcon from "./icons/ChevronIcon";

type Preview = {
  gap_count: number;
  collector_count: number;
  remediation_plan: string;
};

type Props = {
  controlId: string;
  canEdit: boolean;
  onApplied: (remediationPlan: string) => void;
};

function truncate(text: string, max = 220): string {
  const t = text.trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max)}…`;
}

export default function CollectorRemediationDraft({ controlId, canEdit, onApplied }: Props) {
  const [preview, setPreview] = useState<Preview | null>(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    api
      .remediationSummary(controlId)
      .then((data) => {
        if (!cancelled) setPreview(data);
      })
      .catch((err) => {
        if (!cancelled) setError(String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [controlId]);

  if (!canEdit || loading || error || !preview?.gap_count) return null;

  const onDraft = async (mode: "replace" | "append") => {
    setApplying(true);
    setError("");
    try {
      const result = await api.applyRemediationSummary(controlId, mode);
      onApplied(result.remediation_plan);
      setApplied(true);
    } catch (err) {
      setError(String(err));
    } finally {
      setApplying(false);
    }
  };

  return (
    <details className="panel collector-draft-panel">
      <summary className="collector-draft-summary" aria-label="Draft mitigation from collector gaps">
        <div className="collector-draft-summary-text">
          <strong>Draft fix plan from collectors</strong>
          <span className="muted collector-draft-subtitle">
            {preview.gap_count} fail/warn check{preview.gap_count === 1 ? "" : "s"} on this control
          </span>
        </div>
        <span className="collector-draft-toggle" aria-hidden="true">
          <span className="collector-draft-toggle-hint">Preview</span>
          <ChevronIcon className="collector-draft-chevron" />
        </span>
      </summary>
      <div className="panel-body">
        <p className="muted collector-draft-lead">
          Drafts the <strong>Plan to fix this gap</strong> field from collector fail/warn results.{" "}
          <strong>Save draft</strong> replaces existing plan text. Does not set owner, target date, or risk.
        </p>
        <div className="collector-draft-preview collector-draft-preview--single">
          <span className="collector-draft-preview-label">Mitigation draft</span>
          <pre className="collector-draft-preview-pre">{truncate(preview.remediation_plan, 480)}</pre>
        </div>
        <div className="btn-row">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={applying || applied}
            onClick={() => onDraft("replace")}
          >
            {applying ? "Drafting…" : applied ? "Draft saved" : "Save draft"}
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            disabled={applying || applied}
            onClick={() => onDraft("append")}
          >
            Add to existing plan
          </button>
        </div>
        {applied && (
          <p className="collector-draft-success">
            Saved below — edit the plan and add owner and target date before export.
          </p>
        )}
        {error && <p className="verify-fail">{error}</p>}
      </div>
    </details>
  );
}
