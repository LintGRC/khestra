import { FormEvent, useState } from "react";
import { api, ControlComment } from "../api";

type Props = {
  controlId: string;
  comments: ControlComment[];
  canEdit: boolean;
  onUpdated: (comments: ControlComment[]) => void;
};

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function ControlCommentsPanel({ controlId, comments, canEdit, onUpdated }: Props) {
  const [text, setText] = useState("");
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setPosting(true);
    setError("");
    try {
      const r = await api.postControlComment(controlId, text.trim());
      onUpdated(r.comments);
      setText("");
    } catch (err) {
      setError(String(err));
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="panel control-comments-panel">
      <div className="panel-header">
        <strong>Team notes</strong>
      </div>
      <div className="panel-body">
        {comments.length > 0 && (
          <ul className="control-comments-list">
            {[...comments].reverse().map((c) => (
              <li key={c.id} className="control-comment">
                <div className="control-comment-meta">
                  <strong>{c.author}</strong>
                  <span className="muted">{formatWhen(c.created_at)}</span>
                </div>
                <p>{c.text}</p>
              </li>
            ))}
          </ul>
        )}
        {canEdit && (
          <form className="control-comment-form" onSubmit={onSubmit}>
            <label htmlFor={`comment-${controlId}`}>Add comment</label>
            <textarea
              id={`comment-${controlId}`}
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={3}
              placeholder="e.g. Need screenshot of conditional access policy"
            />
            <div className="btn-row">
              <button type="submit" className="btn btn-secondary btn-sm" disabled={posting || !text.trim()}>
                {posting ? "Posting…" : "Post comment"}
              </button>
            </div>
            {error && <p className="muted">{error}</p>}
          </form>
        )}
      </div>
    </div>
  );
}
