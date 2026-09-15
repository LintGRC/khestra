import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { exceptionApi } from "../api";
import type { ExceptionItem, Stats, Reminder } from "../types";
import { FilterBar, FilterSearch, FilterButtons } from "@shared/filter-bar";

function statusBadge(s: string) {
  const cls: Record<string, string> = {
    open: "badge-muted",
    pending_approval: "badge-warning",
    approved: "badge-success",
    rejected: "badge-danger",
    expired: "badge-danger",
    closed: "badge-muted",
  };
  return <span className={`badge ${cls[s] || "badge-muted"}`}>{s.replace(/_/g, " ")}</span>;
}

function riskBadge(r: string) {
  const cls: Record<string, string> = {
    low: "badge-muted",
    medium: "badge-warning",
    high: "badge-danger",
    critical: "badge-danger",
  };
  return <span className={`badge ${cls[r] || "badge-muted"}`}>{r}</span>;
}

function mkLabel(
  items: ExceptionItem[],
  filterKey: string,
  predicate: (e: ExceptionItem) => boolean,
) {
  const count = items.filter(predicate).length;
  return { key: filterKey, count };
}

export default function ExceptionDashboard({ title = "Exception", titlePlural, basePath = "/exceptions" }: { title?: string; titlePlural?: string; basePath?: string }) {
  const plural = titlePlural ?? `${title}s`;
  const lowerPlural = plural.toLowerCase();
  const navigate = useNavigate();
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [reminders, setReminders] = useState<{ expired: Reminder[]; urgent: Reminder[]; upcoming: Reminder[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [seeding, setSeeding] = useState(false);

  const load = async () => {
    try {
      const [excData, statsData, remData] = await Promise.all([
        exceptionApi.list(),
        exceptionApi.stats(),
        exceptionApi.reminders().catch(() => null),
      ]);
      setExceptions(excData.exceptions || []);
      setStats(statsData);
      setReminders(remData);
    } catch (e) {
      console.error(e);
      setError(`Failed to load ${lowerPlural}. Is the backend running?`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await exceptionApi.seed();
      setLoading(true);
      setError(null);
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setSeeding(false);
    }
  };

  const filters = [
    mkLabel(exceptions, "all", () => true),
    mkLabel(exceptions, "open", (e) => e.status === "open" || e.status === "pending_approval"),
    mkLabel(exceptions, "approved", (e) => e.status === "approved"),
    mkLabel(exceptions, "expired", (e) => e.is_expired || e.status === "expired"),
    mkLabel(exceptions, "closed", (e) => e.status === "closed"),
    mkLabel(exceptions, "rejected", (e) => e.status === "rejected"),
  ];

  const filtered = exceptions.filter((e) => {
    if (filter === "all") return true;
    if (filter === "open") return e.status === "open" || e.status === "pending_approval";
    if (filter === "expired") return e.is_expired || e.status === "expired";
    return e.status === filter;
  }).filter((e) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      e.title?.toLowerCase().includes(q) ||
      e.control_id?.toLowerCase().includes(q) ||
      e.owner?.toLowerCase().includes(q) ||
      e.framework?.toLowerCase().includes(q)
    );
  });

  if (loading) {
    return (
      <div className="page-stack">
        <p className="muted">Loading {lowerPlural}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-stack">
        <div className="banner error">{error}</div>
      </div>
    );
  }

  const needsAttention = reminders
    ? [...reminders.expired, ...reminders.urgent]
    : [];

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>{plural}</h2>
          <p className="muted">
            {stats ? `${stats.total} total · ${stats.approved} approved · ${stats.expired} expired · ${stats.expiring_soon} expiring soon` : ""}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button className="btn btn-sm btn-ghost" onClick={() => exceptionApi.downloadCsv()}>
            Export CSV
          </button>
          <button className="btn btn-sm btn-ghost" onClick={() => exceptionApi.downloadPortfolioPdf()}>
            Portfolio PDF
          </button>
          <button className="btn btn-primary" onClick={() => navigate(`${basePath}/new`)}>
            + New {title}
          </button>
        </div>
      </div>

      {exceptions.length === 0 && (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No {lowerPlural} yet. Create your first {title.toLowerCase()} or load sample data.</p>
            <button className="btn btn-sm btn-ghost" style={{ marginTop: "0.75rem" }} onClick={handleSeed} disabled={seeding}>
              {seeding ? "Loading..." : "Load Sample Data"}
            </button>
          </div>
        </div>
      )}

      {stats && exceptions.length > 0 && (
        <div className="stats" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))", gap: "0.75rem" }}>
          {[
            { label: "Total", value: stats.total, color: "var(--text)" },
            { label: "Approved", value: stats.approved, color: "var(--success)" },
            { label: "Pending", value: stats.pending_approval, color: "var(--warning)" },
            { label: "Expired", value: stats.expired, color: "var(--danger)" },
            { label: "Expiring", value: stats.expiring_soon, color: "var(--warning)" },
          ].map((s) => (
            <div key={s.label} className="stat-card" style={{ textAlign: "center", padding: "1rem 0.75rem" }}>
              <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {needsAttention.length > 0 && (
        <div className="panel" style={{ borderLeft: "3px solid var(--danger)" }}>
          <div className="panel-header"><h3>Attention Required ({needsAttention.length})</h3></div>
          <div className="panel-body">
            <div className="evidence-review-list">
              {needsAttention.slice(0, 5).map((r) => (
                <div key={r.id} className="evidence-review-item" style={{ borderLeft: `3px solid ${r.is_expired ? "var(--danger)" : "var(--warning)"}` }}>
                  <Link to={`${basePath}/${r.id}`} style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                    {r.title}
                  </Link>
                  <span className="muted" style={{ fontSize: "0.78rem" }}>
                    {r.is_expired ? "Expired" : `${r.days_left} days left`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {exceptions.length > 0 && (
        <>
          <FilterBar>
            <FilterSearch value={search} onChange={setSearch} placeholder={`Search ${lowerPlural}...`} />
            <FilterButtons
              items={filters.map((f) => ({
                key: f.key,
                label: f.key === "all" ? "All" : f.key.replace(/_/g, " "),
                count: f.count,
              }))}
              active={filter}
              onChange={setFilter}
            />
          </FilterBar>

          <div className="panel">
            <div className="panel-body">
              {filtered.length === 0 ? (
                <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>
                  No {lowerPlural} match this filter.
                </p>
              ) : (
                filtered.map((exc) => (
                  <Link
                    key={exc.id}
                    to={`${basePath}/${exc.id}`}
                    style={{ display: "block", border: "1px solid var(--border)", borderRadius: "8px", padding: "1rem", marginBottom: "0.75rem", textDecoration: "none", color: "inherit" }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.35rem" }}>
                      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                        {statusBadge(exc.status)}
                        {riskBadge(exc.risk_level)}
                        <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{exc.title}</span>
                      </div>
                      <span className="muted" style={{ fontSize: "0.78rem", whiteSpace: "nowrap" }}>
                        Score: {exc.risk_score}/25
                      </span>
                    </div>
                    <p style={{ fontSize: "0.85rem", margin: "0.25rem 0", color: "var(--muted)" }}>
                      {exc.description?.slice(0, 150)}{exc.description?.length > 150 ? "..." : ""}
                    </p>
                    <div style={{ fontSize: "0.75rem", color: "var(--muted)", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                      <span>{exc.control_reference || exc.control_id}</span>
                      <span>{exc.framework}</span>
                      <span>Owner: {exc.owner}</span>
                      {exc.expires_at && (
                        <span style={{ color: exc.is_expired ? "var(--danger)" : "inherit" }}>
                          {exc.is_expired ? "Expired" : `${exc.days_left}d left`}
                        </span>
                      )}
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
