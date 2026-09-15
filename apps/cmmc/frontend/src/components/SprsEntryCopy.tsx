import { useEffect, useState } from "react";
import { apiUrl, authFetch, authenticatedDownload } from "../api";

type Props = {
  canDownload?: boolean;
};

export default function SprsEntryCopy({ canDownload = true }: Props) {
  const [text, setText] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    authFetch("/api/readiness/sprs-entry-text")
      .then((r) => r.json())
      .then((d: { text: string }) => setText(d.text))
      .catch(console.error);
  }, []);

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <strong>SPRS Entry Summary (PIEE handoff)</strong>
        {canDownload && (
          <button type="button" className="btn-link" onClick={() => authenticatedDownload(apiUrl("/api/export/sprs-summary"), "SPRS-Summary.txt")}>
            Download .txt
          </button>
        )}
      </div>
      <div className="panel-body">
        <p className="muted">
          Reference for PIEE manual entry — copy values into the portal. The tool does not submit to SPRS automatically.
        </p>
        <textarea
          className="sprs-copy-area"
          readOnly
          value={text || "Loading SPRS entry summary…"}
          rows={14}
        />
        <div className="btn-row">
          <button type="button" className="btn-secondary" disabled={!text} onClick={onCopy}>
            {copied ? "Copied!" : "Copy to clipboard"}
          </button>
        </div>
      </div>
    </div>
  );
}
