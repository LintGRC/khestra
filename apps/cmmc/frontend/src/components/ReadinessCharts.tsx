type BarRow = { label: string; value: number; title?: string };

export function HorizontalBarChart({ rows, maxValue }: { rows: BarRow[]; maxValue?: number }) {
  if (!rows.length) return <p className="muted">No data yet.</p>;
  const max = maxValue ?? Math.max(...rows.map((r) => r.value), 1);
  return (
    <div className="hbar-chart">
      {rows.map((row) => (
        <div key={`${row.label}-${row.title ?? ""}`} className="hbar-row">
          <span className="hbar-label" title={row.title || row.label}>
            {row.label}
          </span>
          <div className="hbar-track" aria-hidden>
            <div className="hbar-fill" style={{ width: `${(row.value / max) * 100}%` }} />
          </div>
          <span className="hbar-value">{row.value}</span>
        </div>
      ))}
    </div>
  );
}

export function SeverityChart({ counts }: { counts: Record<string, number> }) {
  const order = ["Critical", "High", "Moderate", "Low"];
  const rows = order.filter((k) => counts[k]).map((k) => ({ label: k, value: counts[k] }));
  const colors: Record<string, string> = {
    Critical: "#dc2626",
    High: "#f97316",
    Moderate: "#fbbf24",
    Low: "#22c55e",
  };
  const total = rows.reduce((s, r) => s + r.value, 0) || 1;
  return (
    <div className="severity-chart">
      <div className="severity-bar" role="img" aria-label="POA&M items by severity">
        {rows.map((row) => (
          <div
            key={row.label}
            className="severity-segment"
            style={{ width: `${(row.value / total) * 100}%`, background: colors[row.label] || "#94a3b8" }}
            title={`${row.label}: ${row.value}`}
          />
        ))}
      </div>
      <div className="severity-legend">
        {rows.map((row) => (
          <span key={row.label} className="severity-legend-item">
            <span className="severity-dot" style={{ background: colors[row.label] }} />
            {row.label} ({row.value})
          </span>
        ))}
      </div>
    </div>
  );
}

export function BurndownChart({
  points,
  currentScore,
  targetScore = 110,
}: {
  points: { control_id: string; cumulative_score: number }[];
  currentScore: number;
  targetScore?: number;
}) {
  if (!points.length) {
    return <p className="muted">No open gaps — burndown projects score as gaps close.</p>;
  }
  const w = 100;
  const h = 48;
  const scores = [currentScore, ...points.map((p) => p.cumulative_score), targetScore];
  const min = Math.min(...scores) - 5;
  const max = targetScore + 5;
  const range = max - min || 1;
  const y = (score: number) => h - ((score - min) / range) * h;
  const coords = [
    { x: 0, y: y(currentScore) },
    ...points.map((p, i) => ({
      x: ((i + 1) / points.length) * w,
      y: y(p.cumulative_score),
    })),
  ];
  const linePoints = coords.map((c) => `${c.x},${c.y}`).join(" ");
  const targetY = y(targetScore);
  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${w} ${h}`} className="burndown-chart" preserveAspectRatio="none" role="img" aria-label="SPRS burndown projection">
        <line x1="0" y1={targetY} x2={w} y2={targetY} stroke="#cbd5e1" strokeDasharray="1 1" vectorEffect="non-scaling-stroke" />
        <polyline fill="none" stroke="var(--success)" strokeWidth="0.35" vectorEffect="non-scaling-stroke" points={linePoints} />
      </svg>
      <p className="muted chart-caption">
        Projected SPRS if each gap moves to MET, in control list order ({currentScore} → {points[points.length - 1]?.cumulative_score}; dashed = {targetScore} max). Illustrative — not a schedule.
      </p>
    </div>
  );
}
