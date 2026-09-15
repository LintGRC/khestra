import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";

const TYPE_LABELS: Record<string, string> = {
  policy_review: "Policy review",
  evidence_request: "Evidence request",
  evidence_expiring: "Evidence expiring",
  risk_review: "Risk review",
  acceptance_expiry: "Acceptance expiry",
  control_test: "Control test",
};

const TYPE_LINKS: Record<string, string> = {
  policy_review: "policies",
  evidence_request: "evidence",
  evidence_expiring: "evidence",
  risk_review: "risks",
  acceptance_expiry: "risks",
  control_test: "control-tests",
};

const TYPE_BADGE: Record<string, string> = {
  policy_review: "badge-success",
  evidence_request: "badge-warning",
  evidence_expiring: "badge-danger",
  risk_review: "badge-muted",
  acceptance_expiry: "badge-info",
  control_test: "badge-muted",
};

type CalendarItem = {
  id: string;
  type: string;
  title: string;
  date: string;
  status: "overdue" | "upcoming";
  days_remaining: number;
  framework_id: string;
  link: string;
  details: string;
};

async function calFetch(path: string): Promise<any> {
  const headers = await authHeaders();
  const r = await fetch(apiUrl(path), { headers });
  if (!r.ok) throw new Error(String(r.status));
  return r.json();
}

export default function ComplianceCalendarPage({ frameworkId = "" }: { frameworkId?: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const fwBase = location.pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  useEffect(() => {
    const params = new URLSearchParams({ window_days: "45" });
    if (frameworkId) params.set("framework_id", frameworkId);
    calFetch(`/api/compliance-calendar?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [frameworkId]);

  if (loading) return <p className="muted">Loading compliance calendar…</p>;
  if (!data) return <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>Compliance calendar unavailable.</p></div></div>;

  const overdue = (data.overdue || []) as CalendarItem[];
  const upcoming = (data.upcoming || []) as CalendarItem[];
  const all = (data.items || []) as CalendarItem[];
  const byDate = new Map<string, CalendarItem[]>();
  for (const it of all) {
    const key = it.date;
    if (!byDate.has(key)) byDate.set(key, []);
    byDate.get(key)!.push(it);
  }
  const dateKeys = [...byDate.keys()].sort();
  const visible = dateFilter
    ? (byDate.get(dateFilter) || [])
    : upcoming;
  const go = (it: CalendarItem) => {
    const base = TYPE_LINKS[it.type] || it.link || "policies";
    navigate(`${fwBase}/${base}`);
  };

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Compliance calendar</h2>
        <p className="muted">Policy reviews, evidence requests, expiring evidence, risk reviews, and control tests across your program.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 20 }}>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{data.total ?? 0}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Due in window</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--danger)" }}>{data.overdue_count ?? 0}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Overdue</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--success)" }}>{data.upcoming_count ?? 0}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Upcoming</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{dateKeys.length}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Dates with items</div>
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 16, padding: "10px 14px", display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center" }}>
        <span className="muted" style={{ fontSize: 12, marginRight: 4 }}>Jump to date:</span>
        {dateKeys.map((k) => (
          <button
            key={k}
            className={`btn btn-sm ${dateFilter === k ? "btn-primary" : "btn-ghost"}`}
            style={{ fontSize: 11 }}
            onClick={() => setDateFilter(dateFilter === k ? "" : k)}
            title={`${byDate.get(k)!.length} item(s)`}
          >
            {k.slice(5)} · {byDate.get(k)!.length}
          </button>
        ))}
      </div>

      {overdue.length > 0 && (
        <div className="panel" style={{ marginBottom: 20 }}>
          <div className="panel-header"><strong style={{ color: "var(--danger)" }}>Overdue ({overdue.length})</strong></div>
          <div className="panel-body" style={{ padding: 0 }}>
            {overdue.map((it) => (
              <div key={it.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 14px", borderBottom: "1px solid var(--border-subtle)" }}>
                <span className={`badge ${TYPE_BADGE[it.type] || "badge-muted"}`} style={{ fontSize: 10, flexShrink: 0 }}>{TYPE_LABELS[it.type] || it.type}</span>
                <button className="btn-link" style={{ flex: 1, textAlign: "left" }} onClick={() => go(it)}>{it.title}</button>
                <span className="muted" style={{ fontSize: 11, flexShrink: 0 }}>due {it.date} · {it.days_remaining}d ago</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="panel">
        <div className="panel-header">
          <strong>{dateFilter ? `Items on ${dateFilter}` : `Upcoming (${upcoming.length})`}</strong>
          {dateFilter && <button className="btn btn-sm btn-ghost" onClick={() => setDateFilter("")}>Clear filter</button>}
        </div>
        {visible.length === 0 ? (
          <div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>{dateFilter ? "No items on this date." : "Nothing due in the next 45 days. Keep it that way."}</p></div>
        ) : (
          <div className="panel-body" style={{ padding: 0 }}>
            {visible.map((it) => (
              <div key={it.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 14px", borderBottom: "1px solid var(--border-subtle)" }}>
                <span className={`badge ${TYPE_BADGE[it.type] || "badge-muted"}`} style={{ fontSize: 10, flexShrink: 0 }}>{TYPE_LABELS[it.type] || it.type}</span>
                <button className="btn-link" style={{ flex: 1, textAlign: "left" }} onClick={() => go(it)}>{it.title}</button>
                {it.framework_id && <span className="muted" style={{ fontSize: 11, flexShrink: 0 }}>{it.framework_id}</span>}
                <span className="muted" style={{ fontSize: 11, flexShrink: 0 }}>
                  {it.date}{it.days_remaining > 0 ? ` · ${it.days_remaining}d` : " · today"}
                </span>
                {it.details && <span className="muted" style={{ fontSize: 11, flexShrink: 0, maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{it.details}</span>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
