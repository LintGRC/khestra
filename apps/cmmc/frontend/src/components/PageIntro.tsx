import { type ReactNode, useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import type { HelpViewKey } from "./ViewHelpPanel";

type ViewHelp = { title: string; summary: string; tips: string[] };

let helpCache: { views: Record<string, ViewHelp> } | null = null;

function renderTip(text: string) {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
}

type Props = {
  view?: HelpViewKey;
  title?: string;
  children?: ReactNode;
};

export default function PageIntro({ view, title, children }: Props) {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const [content, setContent] = useState<ViewHelp | null>(null);
  const [tipsOpen, setTipsOpen] = useState(false);

  useEffect(() => {
    if (!view) return;
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

  return (
    <header className="page-intro">
      <div className="page-intro-head">
        <h2 className="page-intro-title">{title || content?.title || ""}</h2>
        <div className="page-intro-actions">
          {view && content && (
            <button type="button" className="btn-link page-intro-tips-btn" onClick={() => setTipsOpen(!tipsOpen)}>
              {tipsOpen ? "Hide guidance" : "Guidance"}
            </button>
          )}
          {children}
        </div>
      </div>
      {view && content && tipsOpen && (
        <ul className="page-intro-tips">
          {content.tips.map((tip) => (
            <li key={tip}>{renderTip(tip)}</li>
          ))}
          <li className="muted">
            <Link to={`${fwBase}/help`}>Full help →</Link>
          </li>
        </ul>
      )}
    </header>
  );
}
