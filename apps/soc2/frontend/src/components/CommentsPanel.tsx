import { useState } from "react";
import { api, type CommentItem } from "../api";

type Props = {
  controlId: string;
  comments: CommentItem[];
  disabled?: boolean;
  onUpdated: () => void;
};

function CommentRow({ c, controlId, disabled, onUpdated, isReply }: { c: CommentItem; controlId: string; disabled?: boolean; onUpdated: () => void; isReply?: boolean }) {
  const [showReply, setShowReply] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);

  const sendReply = async () => {
    const trim = replyText.trim();
    if (!trim) return;
    setSending(true);
    try {
      await api.addComment(controlId, trim, c.id);
      setReplyText("");
      setShowReply(false);
      onUpdated();
    } catch (err) { console.error(err); }
    finally { setSending(false); }
  };

  const remove = async () => {
    try {
      await api.deleteComment(controlId, c.id);
      onUpdated();
    } catch (err) { console.error(err); }
  };

  const highlight = (text: string) => {
    return text.replace(/@(\w+)/g, '<strong style="color:var(--primary)">@$1</strong>');
  };

  return (
    <div style={{ marginLeft: isReply ? 24 : 0, marginBottom: 8, padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <span style={{ fontWeight: 500, fontSize: 13 }}>{c.author || "Anonymous"}</span>
          <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>{c.created_at}</span>
        </div>
        {!disabled && (
          <button type="button" className="btn-link" onClick={remove} style={{ fontSize: 11, color: "var(--danger)" }}>
            Remove
          </button>
        )}
      </div>
      <p style={{ margin: "4px 0 0", fontSize: 13, whiteSpace: "pre-wrap", lineHeight: 1.5 }} dangerouslySetInnerHTML={{ __html: highlight(c.text) }} />
      {!disabled && !isReply && (
        <button type="button" className="btn-link" style={{ fontSize: 11, marginTop: 4 }} onClick={() => setShowReply(!showReply)}>
          {showReply ? "Cancel" : "Reply"}
        </button>
      )}
      {showReply && (
        <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
          <input value={replyText} onChange={e => setReplyText(e.target.value)} placeholder="Write a reply…" style={{ flex: 1, fontSize: 12, padding: "4px 8px" }}
            onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) sendReply(); }} />
          <button type="button" className="btn btn-sm btn-primary" onClick={sendReply} disabled={sending || !replyText.trim()}>
            {sending ? "…" : "Post"}
          </button>
        </div>
      )}
    </div>
  );
}

export default function CommentsPanel({ controlId, comments, disabled, onUpdated }: Props) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);

  const add = async () => {
    const trim = text.trim();
    if (!trim) return;
    setSending(true);
    try {
      await api.addComment(controlId, trim);
      setText("");
      onUpdated();
    } catch (err) { console.error(err); }
    finally { setSending(false); }
  };

  const topLevel = comments.filter(c => !c.parent_id);
  const replies = comments.filter(c => c.parent_id);
  const getReplies = (parentId: string) => replies.filter(r => r.parent_id === parentId);

  return (
    <div>
      {topLevel.length > 0 ? (
        <div style={{ marginBottom: 12 }}>
          {topLevel.map(c => (
            <div key={c.id}>
              <CommentRow c={c} controlId={controlId} disabled={disabled} onUpdated={onUpdated} />
              {getReplies(c.id).map(r => (
                <CommentRow key={r.id} c={r} controlId={controlId} disabled={disabled} onUpdated={onUpdated} isReply />
              ))}
            </div>
          ))}
        </div>
      ) : (
        <p className="muted" style={{ fontSize: 13 }}>No comments yet.</p>
      )}

      {!disabled && (
        <div style={{ display: "flex", gap: 8 }}>
          <textarea value={text} onChange={e => setText(e.target.value)}
            placeholder="Add a comment…" rows={2} style={{ flex: 1, resize: "vertical" }}
            onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) add(); }} />
          <button type="button" className="btn btn-primary btn-sm" onClick={add}
            disabled={sending || !text.trim()} style={{ alignSelf: "flex-end" }}>
            {sending ? "…" : "Post"}
          </button>
        </div>
      )}
    </div>
  );
}
