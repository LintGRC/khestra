import { useEffect, useState } from "react";
import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";

const MATURITY_COLORS = ["#9ca3af", "#fbbf24", "#3b82f6", "#22c55e", "#16a34a"];

type MaturityPanel = {
  available: boolean;
  levels: string[];
  counts: number[];
  total: number;
  automated: number;
  scoped_total: number;
  note: string;
};

type FindingsPanel = {
  available: boolean;
  by_family: { family: string; counts: Record<string, number> }[];
  recurring_count: number;
  note: string;
};

type ExceptionsPanel = {
  available: boolean;
  quarters: string[];
  by_status: Record<string, number[]>;
  note: string;
};

type RisksPanel = {
  available: boolean;
  total_risks: number;
  unowned_count: number;
  oldest_unowned_days: number;
  oldest_open_days: number;
  decisions_made: number;
  note: string;
};

type Summary = {
  framework_id: string;
  period_months: number;
  maturity_distribution: MaturityPanel;
  findings_recurrence: FindingsPanel;
  exception_trend: ExceptionsPanel;
  decision_velocity: RisksPanel;
};

function EmptyPanel({ note }: { note: string }) {
  return (
    <div className="panel" style={{ opacity: 0.75 }}>
      <div className="panel-body" style={{ fontSize: "0.85rem", color: "var(--muted)", textAlign: "center", padding: "1.5rem" }}>
        {note}
      </div>
    </div>
  );
}

function MaturityPanelView({ d }: { d: MaturityPanel }) {
  const max = Math.max(...d.counts, 1);
  const pct = (n: number) => Math.round((n / max) * 100);
  const autoPct = d.scoped_total ? Math.round((d.automated / d.scoped_total) * 100) : 0;
  return (
    <div className="panel">
      <div className="panel-header"><strong>Control maturity</strong></div>
      <div className="panel-body">
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 55%", minWidth: 260 }}>
            {d.levels.map((lvl, i) => (
              <div key={lvl} style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", marginBottom: 4 }}>
                  <span>{lvl}</span>
                  <span className="muted">{d.counts[i]}</span>
                </div>
                <div style={{ height: 10, background: "var(--border-subtle)", borderRadius: 5, overflow: "hidden" }}>
                  <div style={{ width: `${pct(d.counts[i])}%`, height: "100%", background: MATURITY_COLORS[i] }} />
                </div>
              </div>
            ))}
            <p className="muted" style={{ fontSize: "0.75rem", marginTop: 10 }}>
              {d.total} of {d.scoped_total} controls rated. Scale: Ad Hoc → Optimized (5-step maturity curve).
            </p>
          </div>
          <div style={{ flex: "1 1 30%", minWidth: 200, textAlign: "center" }}>
            <div
              style={{
                width: 130,
                height: 130,
                margin: "0 auto",
                borderRadius: "50%",
                background: `conic-gradient(var(--success) 0 ${autoPct}%, var(--border-subtle) ${autoPct}% 100%)`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div style={{ width: 96, height: 96, background: "var(--panel)", borderRadius: "50%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                <strong style={{ fontSize: "1.4rem" }}>{autoPct}%</strong>
                <span className="muted" style={{ fontSize: "0.7rem" }}>automated</span>
              </div>
            </div>
            <p className="muted" style={{ fontSize: "0.75rem", marginTop: 8 }}>
              {d.automated} of {d.scoped_total} controls enforced by collectors vs human operation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function FindingsPanelView({ d }: { d: FindingsPanel }) {
  const years = [...new Set(d.by_family.flatMap((f) => Object.keys(f.counts)))].sort();
  return (
    <div className="panel">
      <div className="panel-header">
        <strong>Findings recurrence</strong>
        {d.recurring_count > 0 && (
          <span className="badge badge-warning" title="Families with findings in consecutive years">
            {d.recurring_count} recurring
          </span>
        )}
      </div>
      <div className="panel-body">
        {d.by_family.length === 0 ? (
          <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No findings recorded.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: "6px 10px", borderBottom: "1px solid var(--border-subtle)" }}>Control area</th>
                {years.map((y) => (
                  <th key={y} style={{ padding: "6px 10px", borderBottom: "1px solid var(--border-subtle)" }}>{y}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {d.by_family.map((f) => {
                const ys = Object.keys(f.counts).sort();
                const recurring = ys.some((y, i) => i > 0 && parseInt(y) - parseInt(ys[i - 1]) === 1);
                return (
                  <tr key={f.family} style={recurring ? { background: "color-mix(in srgb, var(--warning) 12%, transparent)" } : undefined}>
                    <td style={{ padding: "6px 10px", borderBottom: "1px solid var(--border-subtle)", fontWeight: 600 }}>
                      {f.family}
                      {recurring && <span className="badge badge-warning" style={{ marginLeft: 8, fontSize: 10 }}>recurring</span>}
                    </td>
                    {years.map((y) => (
                      <td key={y} style={{ padding: "6px 10px", borderBottom: "1px solid var(--border-subtle)", textAlign: "center" }}>
                        {f.counts[y] || "—"}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
        <p className="muted" style={{ fontSize: "0.75rem", marginTop: 8 }}>
          Recurring = same control area flagged in consecutive years.
        </p>
      </div>
    </div>
  );
}

function ExceptionsPanelView({ d }: { d: ExceptionsPanel }) {
  const statuses = Object.keys(d.by_status);
  const totals = statuses.map((s) => d.by_status[s].reduce((a, b) => a + b, 0));
  const maxTotal = Math.max(...totals, 1);
  const colors = ["#dc2626", "#ea580c", "#eab308", "#22c55e", "#6b7280", "#3b82f6"];
  return (
    <div className="panel">
      <div className="panel-header"><strong>Exception trend</strong></div>
      <div className="panel-body">
        {d.quarters.length === 0 ? (
          <p className="muted" style={{ textAlign: "center", padding: "1rem" }}>No exceptions recorded.</p>
        ) : (
          <div>
            <div style={{ display: "flex", gap: 16, alignItems: "flex-end", minHeight: 130, padding: "0 6px" }}>
              {d.quarters.map((q, qi) => {
                const statusTotals = statuses.map((s) => d.by_status[s][qi] || 0);
                const qTotal = statusTotals.reduce((a, b) => a + b, 0);
                return (
                  <div key={q} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                    <div style={{ width: "100%", maxWidth: 56, height: 110, display: "flex", flexDirection: "column-reverse", gap: 1 }}>
                      {statuses.map((s, si) => {
                        const n = d.by_status[s][qi] || 0;
                        return n > 0 ? (
                          <div key={s} title={`${s}: ${n}`} style={{ height: `${(n / maxTotal) * 100}%`, minHeight: 4, background: colors[si % colors.length] }} />
                        ) : null;
                      })}
                      {qTotal === 0 && <div style={{ flex: 1, borderBottom: "1px dashed var(--border-subtle)" }} />}
                    </div>
                    <span className="muted" style={{ fontSize: "0.7rem" }}>{q}</span>
                  </div>
                );
              })}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 12, fontSize: "0.75rem" }}>
              {statuses.map((s, si) => (
                <span key={s} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <span style={{ width: 10, height: 10, background: colors[si % colors.length], display: "inline-block" }} />
                  {s} ({totals[si]})
                </span>
              ))}
            </div>
            <p className="muted" style={{ fontSize: "0.75rem", marginTop: 8 }}>
              Are exceptions reducing, increasing, or being normalised?
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function VelocityPanelView({ d }: { d: RisksPanel }) {
  const cards = [
    { label: "Risks without owner", value: d.unowned_count, hint: "Signal present, no decision owner" },
    { label: "Oldest unowned", value: `${d.oldest_unowned_days}d`, hint: "Age of oldest ownerless risk" },
    { label: "Oldest open risk", value: `${d.oldest_open_days}d`, hint: "Age of oldest non-closed risk" },
    { label: "Decisions made", value: d.decisions_made, hint: "Risks with a review date" },
  ];
  return (
    <div className="panel">
      <div className="panel-header"><strong>Decision velocity</strong></div>
      <div className="panel-body">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
          {cards.map((c) => (
            <div key={c.label} style={{ border: "1px solid var(--border-subtle)", borderRadius: 8, padding: "12px 14px", textAlign: "center" }}>
              <div style={{ fontSize: "1.6rem", fontWeight: 700 }}>{c.value}</div>
              <div style={{ fontSize: "0.8rem" }}>{c.label}</div>
              <div className="muted" style={{ fontSize: "0.7rem", marginTop: 4 }}>{c.hint}</div>
            </div>
          ))}
        </div>
        <p className="muted" style={{ fontSize: "0.75rem", marginTop: 10 }}>
          How fast does a risk signal become a decision with an owner and a date?
        </p>
      </div>
    </div>
  );
}

export default function EffectivenessDashboard({ frameworkId = "" }: { frameworkId?: string }) {
  const [data, setData] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams({ period: "12" });
    if (frameworkId) params.set("framework", frameworkId);
    authHeaders()
      .then((headers) => fetch(apiUrl(`/api/effectiveness/summary?${params.toString()}`), { headers }))
      .then((r) => (r.ok ? r.json() : Promise.reject(String(r.status))))
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [frameworkId]);

  if (loading) return <p className="muted">Loading program effectiveness…</p>;
  if (!data)
    return (
      <div className="panel">
        <div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>Program effectiveness unavailable.</p></div>
      </div>
    );

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Program effectiveness</h2>
        <p className="muted">
          Is governance making risk more visible, decisions more consistent, and remediation more predictable?
          {frameworkId ? ` Framework: ${frameworkId}.` : " All frameworks."}
        </p>
      </div>

      {data.maturity_distribution.available ? (
        <MaturityPanelView d={data.maturity_distribution} />
      ) : (
        <EmptyPanel note={data.maturity_distribution.note} />
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))", gap: 16 }}>
        {data.findings_recurrence.available ? (
          <FindingsPanelView d={data.findings_recurrence} />
        ) : (
          <EmptyPanel note={data.findings_recurrence.note} />
        )}
        {data.exception_trend.available ? (
          <ExceptionsPanelView d={data.exception_trend} />
        ) : (
          <EmptyPanel note={data.exception_trend.note} />
        )}
      </div>

      {data.decision_velocity.available ? (
        <VelocityPanelView d={data.decision_velocity} />
      ) : (
        <EmptyPanel note={data.decision_velocity.note} />
      )}
    </div>
  );
}
