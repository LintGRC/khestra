import { useState } from "react";
import { ControlReadiness } from "../api";
import CheckIcon from "./icons/CheckIcon";

type Props = {
  readiness: ControlReadiness | undefined;
};

const badgeCls = (pct: number) => {
  if (pct === 100) return "readiness-badge readiness-badge--ok";
  if (pct >= 50) return "readiness-badge readiness-badge--warn";
  return "readiness-badge readiness-badge--fail";
};

const summaryLabel = (r: ControlReadiness) =>
  `${r.done_count}/${r.required_count} — ${r.readiness_label}`;

export default function ReadinessChecklist({ readiness }: Props) {
  const [collapsed, setCollapsed] = useState(false);
  if (!readiness) return null;

  return (
    <div className="panel readiness-checklist-panel">
      <div
        className="panel-header"
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}
        onClick={() => setCollapsed((c) => !c)}
      >
        <strong>Control Readiness</strong>
        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className={badgeCls(readiness.readiness_pct)}>
            {summaryLabel(readiness)}
          </span>
          <span style={{ fontSize: "0.65rem", color: "var(--muted)" }}>{collapsed ? "▼" : "▲"}</span>
        </span>
      </div>
      {!collapsed && (
        <div className="panel-body">
          <div className="readiness-progress">
            <div
              className="readiness-progress-fill"
              style={{ width: `${readiness.readiness_pct}%` }}
            />
          </div>
          <ul className="readiness-items">
            {readiness.items.map((item) => (
              <li
                key={item.id}
                className={`readiness-item${item.done ? " done" : ""}${item.required ? " required" : " optional"}`}
                title={item.hint}
              >
                <span
                  className={
                    item.done
                      ? item.required
                        ? "readiness-dot readiness-dot--ok"
                        : "readiness-dot readiness-dot--faded"
                      : item.required
                      ? "readiness-dot readiness-dot--warn"
                      : "readiness-dot readiness-dot--ghost"
                  }
                >
                  {item.done ? <CheckIcon /> : null}
                </span>
                <span className="readiness-label">{item.label}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
