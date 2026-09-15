import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export type HelpViewKey =
  | "Dashboard"
  | "Organization"
  | "Controls"
  | "Export"
  | "Readiness"
  | "Integrations"
  | "Policies";

type ViewHelp = {
  title: string;
  summary: string;
  tips: string[];
};

let helpCache: { views: Record<string, ViewHelp> } | null = null;

function renderTip(text: string) {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
}

type Props = {
  view: HelpViewKey;
};

export default function ViewHelpPanel({ view }: Props) {
  const [content, setContent] = useState<ViewHelp | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (helpCache?.views[view]) {
      setContent(helpCache.views[view]);
      return;
    }
    api
      .help()
      .then((data) => {
        helpCache = data as { views: Record<string, ViewHelp> };
        setContent(helpCache.views[view] ?? null);
      })
      .catch(console.error);
  }, [view]);

  if (!content) return null;

  return (
    <div className="panel view-help-panel">
      <button type="button" className="panel-header view-help-toggle" onClick={() => setOpen(!open)}>
        <strong>About {content.title}</strong>
        <span className="muted">{open ? "Hide tips" : "Show tips"}</span>
      </button>
      {open && (
        <div className="panel-body">
          <p className="muted">{content.summary}</p>
          <ul className="view-help-tips">
            {content.tips.map((tip) => (
              <li key={tip}>{renderTip(tip)}</li>
            ))}
          </ul>
          <p className="muted view-help-more">
            More in <Link to="/help">Help</Link>.
          </p>
        </div>
      )}
    </div>
  );
}
