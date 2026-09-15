import { useEffect, useState } from "react";

type HelpView = { title: string; summary: string; tips: string[] };
type HelpData = { views: Record<string, HelpView>; faq: { q: string; a: string }[] };

const VIEW_ORDER = ["Dashboard", "Organization", "Controls", "Readiness", "Export", "Integrations"] as const;

function renderTip(text: string) {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
}

type Props = {
  getHelp: () => Promise<HelpData>;
};

export default function HelpPage({ getHelp }: Props) {
  const [data, setData] = useState<HelpData | null>(null);

  useEffect(() => {
    getHelp().then(setData).catch(console.error);
  }, [getHelp]);

  if (!data) return <div className="panel" style={{ padding: "2rem", textAlign: "center", color: "var(--muted)" }}>Loading help…</div>;

  return (
    <div className="panel-stack help-page">
      {VIEW_ORDER.map((key) => {
        const view = data.views[key];
        if (!view) return null;
        return (
          <div key={key} className="panel">
            <div className="panel-header">
              <strong>{view.title}</strong>
            </div>
            <div className="panel-body">
              <p>{view.summary}</p>
              <ul>
                {view.tips.map((t) => (
                  <li key={t}>{renderTip(t)}</li>
                ))}
              </ul>
            </div>
          </div>
        );
      })}
      <div className="panel">
        <div className="panel-header">
          <strong>FAQ</strong>
        </div>
        <div className="panel-body">
          {data.faq.map((item) => (
            <div key={item.q} className="help-faq-item">
              <strong>{item.q}</strong>
              <p className="muted">{renderTip(item.a)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
