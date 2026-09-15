import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiUrl } from "@shared/apiPrefix";

interface Props {
  frameworkId: string;
  fwBase: string;
  fetchOverdue?: boolean;
}

export function EvidenceSummaryBadge({ frameworkId, fwBase, fetchOverdue = true }: Props) {
  const [summary, setSummary] = useState<{ fresh: number; stale: number; overdue: number } | null>(null);

  useEffect(() => {
    const p: Promise<unknown>[] = [
      fetch(apiUrl(`/api/evidence-hub/freshness?framework_id=${frameworkId}`)).then(r => r.json()),
    ];
    if (fetchOverdue) {
      p.push(fetch(apiUrl("/api/evidence-hub/requests/overdue")).then(r => r.json()));
    }
    Promise.all(p)
      .then(([freshness, overdue]) => {
        const overdueCount = overdue ? (overdue as any).requests?.length || 0 : 0;
        setSummary({
          fresh: (freshness as any).fresh || 0,
          stale: ((freshness as any).stale || 0) + ((freshness as any).expired || 0),
          overdue: overdueCount,
        });
      })
      .catch(() => setSummary({ fresh: 0, stale: 0, overdue: 0 }));
  }, [frameworkId, fetchOverdue]);

  if (!summary) return null;

  return (
    <Link
      to={`${fwBase}/evidence`}
      style={{
        display: "inline-flex", alignItems: "center", gap: 6,
        padding: "4px 12px", borderRadius: "var(--radius)",
        border: "1px solid var(--border-subtle)", background: "var(--surface)",
        textDecoration: "none", color: "inherit", fontSize: 13, fontWeight: 500,
      }}
    >
      <span style={{
        width: 8, height: 8, borderRadius: "50%",
        background: summary.stale > 0 ? "var(--warning)"
          : summary.overdue > 0 ? "var(--danger)" : "var(--success)",
        flexShrink: 0,
      }} />
      {summary.stale > 0 || summary.overdue > 0 ? (
        <span>
          <strong>{summary.stale} stale</strong>
          {summary.overdue > 0 && <span className="muted"> · {summary.overdue} overdue</span>}
        </span>
      ) : (
        <span>{summary.fresh} evidence items</span>
      )}
      <span style={{ color: "var(--muted)", fontSize: 11 }}>→</span>
    </Link>
  );
}
