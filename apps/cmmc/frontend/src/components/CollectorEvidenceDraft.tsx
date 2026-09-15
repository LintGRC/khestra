import { useEffect, useState } from "react";
import { api } from "../api";
import ChevronIcon from "./icons/ChevronIcon";

type Preview = {
  collector_count: number;
  examine: string;
  test: string;
};

type Props = {
  controlId: string;
  canEdit: boolean;
  variant: "evidence" | "document";
  onApplied: (examine: string, test: string) => void;
  onGoToDocumentStep?: () => void;
};

function truncate(text: string, max = 140): string {
  const t = text.trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max)}…`;
}

export default function CollectorEvidenceDraft({
  controlId,
  canEdit,
  variant,
  onApplied,
  onGoToDocumentStep,
}: Props) {
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
      .evidenceSummary(controlId)
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

  if (!canEdit || loading || error || !preview?.collector_count) return null;

  const onDraft = async () => {
    setApplying(true);
    setError("");
    try {
      const result = await api.applyEvidenceSummary(controlId, "append");
      onApplied(result.examine, result.test);
      setApplied(true);
    } catch (err) {
      setError(String(err));
    } finally {
      setApplying(false);
    }
  };

  if (variant === "document") {
    return (
      <div className="collector-draft-inline">
        <p className="muted collector-draft-lead">
          <strong>{preview.collector_count}</strong> collector file
          {preview.collector_count === 1 ? "" : "s"} attached — draft the policy and test fields below from
          those results.
        </p>
        <div className="btn-row">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            disabled={applying || applied}
            onClick={onDraft}
          >
            {applying ? "Drafting…" : applied ? "Draft applied" : "Draft policy & test"}
          </button>
        </div>
        {applied && (
          <p className="collector-draft-success">Review the fields below — edit anything that needs your judgment.</p>
        )}
        {error && <p className="verify-fail">{error}</p>}
      </div>
    );
  }

  return (
    <details className="panel collector-draft-panel">
      <summary className="collector-draft-summary" aria-label="Draft policy and test from collector files">
        <div className="collector-draft-summary-text">
          <strong>Draft policy &amp; test</strong>
          <span className="muted collector-draft-subtitle">
            From {preview.collector_count} collector file{preview.collector_count === 1 ? "" : "s"}
          </span>
        </div>
        <span className="collector-draft-toggle" aria-hidden="true">
          <span className="collector-draft-toggle-hint">Preview</span>
          <ChevronIcon className="collector-draft-chevron" />
        </span>
      </summary>
      <div className="panel-body">
        <p className="muted collector-draft-lead">
          Builds text for <strong>Policy review</strong> and <strong>Technical test</strong> on the Describe step.
          Does not change SSP narrative or control status.
        </p>
        <div className="collector-draft-preview">
          <div>
            <span className="collector-draft-preview-label">Policy review</span>
            <p>{truncate(preview.examine)}</p>
          </div>
          <div>
            <span className="collector-draft-preview-label">Technical test</span>
            <p>{truncate(preview.test)}</p>
          </div>
        </div>
        <div className="btn-row">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={applying || applied}
            onClick={onDraft}
          >
            {applying ? "Drafting…" : applied ? "Draft saved" : "Save draft to this control"}
          </button>
          {applied && onGoToDocumentStep && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={onGoToDocumentStep}>
              Review on Describe step →
            </button>
          )}
        </div>
        {applied && (
          <p className="collector-draft-success">
            Saved to this control. Open Describe to review the policy and test fields.
          </p>
        )}
        {error && <p className="verify-fail">{error}</p>}
      </div>
    </details>
  );
}
