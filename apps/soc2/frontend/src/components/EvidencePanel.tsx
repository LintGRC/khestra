import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { EmptyState } from "./ui/Skeleton";

type EvidenceItem = {
  filename: string;
  upload_date: string;
  sha256?: string;
  is_auto?: boolean;
  review_status?: string;
  valid_from?: string;
  valid_to?: string | null;
};

type Props = {
  controlId: string;
  evidence: EvidenceItem[];
  canEdit: boolean;
  reviewer?: string;
  onUpdated: () => void;
};

export default function EvidencePanel({
  controlId,
  evidence,
  canEdit,
  reviewer = "Reviewer",
  onUpdated,
}: Props) {
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState("");
  const [removing, setRemoving] = useState<string | null>(null);
  const [reviewing, setReviewing] = useState<string | null>(null);

  const onUpload = async (fileList: FileList | null) => {
    if (!fileList?.length) return;
    setUploading(true);
    setMsg("");
    try {
      await api.uploadEvidence(controlId, fileList[0]);
      setMsg("Uploaded.");
      onUpdated();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setUploading(false);
    }
  };

  const onDelete = async (filename: string) => {
    if (!window.confirm(`Remove "${filename}"? This cannot be undone.`)) return;
    setRemoving(filename);
    setMsg("");
    try {
      await api.deleteEvidence(controlId, filename);
      onUpdated();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setRemoving(null);
    }
  };

  const onReview = async (filename: string, status: string) => {
    setReviewing(filename);
    setMsg("");
    try {
      await api.reviewEvidence(controlId, filename, { reviewer, status, comment: "" });
      onUpdated();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setReviewing(null);
    }
  };

  return (
    <section className="panel evidence-panel">
      <div className="panel-header">
        <strong>Evidence ({evidence.length})</strong>
      </div>
      <div className="panel-body">
        <p className="muted">
          Attach policies, screenshots, or connect integrations for automatic collection.
        </p>
        {evidence.length === 0 ? (
          <EmptyState
            compact
            title="No evidence linked"
            description={
              canEdit
                ? "Upload a file below or connect an integration."
                : "No artifacts linked to this criterion yet."
            }
          >
            {canEdit && (
              <Link className="btn btn-secondary btn-sm" to="/integrations">
                Open integrations
              </Link>
            )}
          </EmptyState>
        ) : (
          <ul className="evidence-list">
            {evidence.map((ev) => {
              const isAuto = ev.is_auto ?? ev.filename.startsWith("collector_");
              const busy = removing === ev.filename || reviewing === ev.filename;
              return (
                <li key={ev.filename} className="evidence-row">
                  <div className="evidence-meta">
                    <strong className="evidence-filename">{ev.filename}</strong>
                    <span className="muted">{ev.upload_date}</span>
                    {ev.valid_from && (
                      <span className="muted" style={{ fontSize: 11 }}>
                        {ev.valid_from}{ev.valid_to ? ` — ${ev.valid_to}` : " (point-in-time)"}
                      </span>
                    )}
                    {isAuto ? (
                      <span className="badge badge-info">Auto</span>
                    ) : (
                      <span className="badge">Manual</span>
                    )}
                    {ev.review_status === "approved" && (
                      <span className="badge badge-success">Approved</span>
                    )}
                    {ev.review_status === "rejected" && (
                      <span className="badge badge-danger">Rejected</span>
                    )}
                    {ev.review_status === "pending" && (
                      <span className="badge badge-warning">Pending</span>
                    )}
                    {ev.sha256 && (
                      <code className="evidence-sha" title={ev.sha256}>
                        {ev.sha256.slice(0, 12)}…
                      </code>
                    )}
                  </div>
                  <div className="evidence-actions-cell">
                    <a
                      className="btn btn-secondary btn-sm"
                      href={api.evidenceDownloadUrl(controlId, ev.filename)}
                      download
                    >
                      Download
                    </a>
                    {canEdit && ev.review_status === "pending" && (
                      <>
                        <button
                          type="button"
                          className="btn btn-sm btn-success"
                          disabled={busy}
                          onClick={() => onReview(ev.filename, "approved")}
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          className="btn btn-sm btn-danger"
                          disabled={busy}
                          onClick={() => onReview(ev.filename, "rejected")}
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {canEdit && !isAuto && (
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        disabled={busy}
                        onClick={() => onDelete(ev.filename)}
                      >
                        {removing === ev.filename ? "Removing…" : "Remove"}
                      </button>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
        {canEdit && (
          <div className="evidence-upload">
            <input
              type="file"
              disabled={uploading}
              accept=".pdf,.png,.jpg,.jpeg,.json,.conf,.txt,.csv"
              onChange={(e) => {
                onUpload(e.target.files);
                e.target.value = "";
              }}
            />
          </div>
        )}
        {msg && <p className="muted">{msg}</p>}
      </div>
    </section>
  );
}
