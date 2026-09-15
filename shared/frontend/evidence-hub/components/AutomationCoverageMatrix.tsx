import { useEffect, useState } from "react";
import { apiUrl } from "@shared/apiPrefix";

type MappingsRecord = Record<string, string[]>;

type Props = {
  framework: string;
  onNavigate?: (criterionId: string) => void;
};

export default function AutomationCoverageMatrix({ framework, onNavigate }: Props) {
  const [mappings, setMappings] = useState<MappingsRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(apiUrl(`/api/collectors/mappings?framework=${encodeURIComponent(framework)}`))
      .then((r) => r.json())
      .then((data) => {
        setMappings(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(String(err));
        setLoading(false);
      });
  }, [framework]);

  if (loading) return <p className="muted">Loading mapping coverage…</p>;
  if (error) return <p className="banner error">Failed to load mappings: {error}</p>;
  if (!mappings || Object.keys(mappings).length === 0) {
    return <p className="muted">No collectors mapped to {framework.toUpperCase()} criteria.</p>;
  }

  const allCriteria = new Set<string>();
  const checks = Object.entries(mappings).sort();
  for (const [, criteria] of checks) {
    for (const c of criteria) allCriteria.add(c);
  }

  const totalCollected = checks.filter(([, c]) => c.length > 0).length;
  const criteriaCovered = allCriteria.size;

  return (
    <div>
      <div className="evidence-coverage-cards" style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
        <div className="stat-card" style={{ flex: 1, minWidth: 120 }}>
          <div className="stat-value">{checks.length}</div>
          <div className="stat-label">Total collector checks</div>
        </div>
        <div className="stat-card" style={{ flex: 1, minWidth: 120 }}>
          <div className="stat-value" style={{ color: totalCollected > 0 ? "var(--success)" : "var(--danger)" }}>{totalCollected}</div>
          <div className="stat-label">Checks with {framework.toUpperCase()} mapping</div>
        </div>
        <div className="stat-card" style={{ flex: 1, minWidth: 120 }}>
          <div className="stat-value">{criteriaCovered}</div>
          <div className="stat-label">Criteria covered</div>
        </div>
        <div className="stat-card" style={{ flex: 1, minWidth: 120 }}>
          <div className="stat-value">{checks.length - totalCollected}</div>
          <div className="stat-label">Checks with no mapping</div>
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table className="table" style={{ width: "100%", fontSize: 13 }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left", padding: "8px 12px" }}>Collector Check</th>
              <th style={{ textAlign: "left", padding: "8px 12px" }}>Criteria Mapped</th>
              <th style={{ textAlign: "center", padding: "8px 12px" }}>Count</th>
            </tr>
          </thead>
          <tbody>
            {checks.map(([checkId, criteria]) => (
              <tr key={checkId} style={{ opacity: criteria.length === 0 ? 0.5 : 1 }}>
                <td style={{ padding: "8px 12px", fontWeight: criteria.length > 0 ? 500 : 400 }}>
                  {checkId}
                </td>
                <td style={{ padding: "8px 12px" }}>
                  {criteria.length > 0 ? (
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                      {criteria.map((c) => (
                        <span
                          key={c}
                          onClick={() => onNavigate?.(c)}
                          style={{
                            display: "inline-block",
                            padding: "2px 8px",
                            borderRadius: 4,
                            fontSize: 11,
                            background: "var(--info-soft)",
                            color: "var(--primary)",
                            cursor: onNavigate ? "pointer" : "default",
                            border: "1px solid var(--border-subtle)",
                          }}
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="muted" style={{ fontSize: 11, fontStyle: "italic" }}>
                      No {framework.toUpperCase()} mapping
                    </span>
                  )}
                </td>
                <td style={{ padding: "8px 12px", textAlign: "center" }}>
                  <span className={`badge ${criteria.length > 0 ? "badge-success" : "badge-muted"}`}>
                    {criteria.length}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
