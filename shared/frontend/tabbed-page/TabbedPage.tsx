import { useState, type ReactNode } from "react";

export type Tab = {
  id: string;
  label: string;
  content: ReactNode;
  badge?: number | string;
};

export default function TabbedPage({
  title,
  tabs,
  defaultTab,
}: {
  title: string;
  tabs: Tab[];
  defaultTab?: string;
}) {
  const [active, setActive] = useState(defaultTab || tabs[0]?.id || "");

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>{title}</h2>
      </div>

      <div style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--border)", marginBottom: "1rem" }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActive(t.id)}
            style={{
              padding: "8px 16px",
              border: "none",
              background: "none",
              cursor: "pointer",
              fontSize: 13,
              fontWeight: active === t.id ? 600 : 400,
              color: active === t.id ? "var(--primary)" : "var(--muted)",
              borderBottom: active === t.id ? "2px solid var(--primary)" : "2px solid transparent",
              marginBottom: -1,
              transition: "color 0.15s, border-color 0.15s",
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            {t.label}
            {t.badge != null && (
              <span style={{ fontSize: 10, fontWeight: 600, padding: "1px 6px", borderRadius: "var(--radius)", background: "var(--primary-soft)", color: "var(--primary)" }}>
                {t.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {tabs.find((t) => t.id === active)?.content}
    </div>
  );
}
