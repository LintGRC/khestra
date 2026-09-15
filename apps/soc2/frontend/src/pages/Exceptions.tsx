import { useEffect, useState } from "react";
import { TabbedPage } from "@shared/tabbed-page";
import ExceptionDashboard from "@shared/exception-tracker/pages/ExceptionDashboard";
import { findingApi, FindingItem } from "@shared/audit-findings";
import { FilterBar, FilterButtons } from "@shared/filter-bar";

function FindingsTab() {
  const [findings, setFindings] = useState<FindingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("open");

  useEffect(() => {
    findingApi.list()
      .then((data) => setFindings(data.findings || []))
      .catch((e) => { console.error(e); setError("Failed to load findings."); })
      .finally(() => setLoading(false));
  }, []);

  function sevColor(s: string): string {
    const m: Record<string, string> = { observation: "badge-muted", improvement: "badge-warning", minor: "badge-warning", major: "badge-danger", material: "badge-danger" };
    return m[s] || "badge-muted";
  }

  const filtered = findings.filter((f) => {
    if (filter === "open") return f.status !== "closed" && f.status !== "resolved";
    if (filter === "closed") return f.status === "closed" || f.status === "resolved";
    return f.status === filter;
  });

  if (loading) return <p className="muted">Loading...</p>;
  if (error) return <div className="banner error">{error}</div>;

  const filterCounts = {
    open: findings.filter((x) => x.status !== "closed" && x.status !== "resolved").length,
    closed: findings.filter((x) => x.status === "closed" || x.status === "resolved").length,
    acknowledged: findings.filter((x) => x.status === "acknowledged").length,
    disputed: findings.filter((x) => x.status === "disputed").length,
  };

  return (
    <div>
      <FilterBar>
        <FilterButtons
          items={[
            { key: "open", label: "Open", count: filterCounts.open },
            { key: "closed", label: "Closed", count: filterCounts.closed },
            { key: "acknowledged", label: "Acknowledged", count: filterCounts.acknowledged },
            { key: "disputed", label: "Disputed", count: filterCounts.disputed },
          ]}
          active={filter}
          onChange={setFilter}
        />
      </FilterBar>
      {filtered.length === 0 ? <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No findings match this filter.</p> : (
        <div className="panel"><div className="panel-body">
          {filtered.map((f) => (
            <div key={f.id} style={{ display: "flex", justifyContent: "space-between", padding: "0.75rem 0", borderBottom: "1px solid var(--border)" }}>
              <div>
                <strong>{f.title || f.id}</strong>
                <div className="muted" style={{ fontSize: "0.75rem" }}>{f.control_ids?.length ? `${f.control_ids.join(", ")} · ` : ""}{f.owner ? `Owner: ${f.owner} · ` : ""}{f.created_at?.slice(0, 10)}</div>
              </div>
              <div style={{ display: "flex", gap: 4, alignItems: "flex-start", flexShrink: 0 }}>
                <span className={`badge ${sevColor(f.severity)}`}>{f.severity}</span>
                <span className="badge badge-muted">{f.status}</span>
              </div>
            </div>
          ))}
        </div></div>
      )}
    </div>
  );
}

export default function ExceptionsPage() {
  return <TabbedPage title="Exceptions & Findings" tabs={[
    { id: "exceptions", label: "Exceptions", content: <ExceptionDashboard /> },
    { id: "findings", label: "Audit Findings", content: <FindingsTab /> },
  ]} />;
}
