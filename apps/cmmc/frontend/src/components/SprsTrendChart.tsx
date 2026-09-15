type Props = {
  history: { timestamp: string; score: number }[];
};

export default function SprsTrendChart({ history }: Props) {
  if (!history || history.length < 2) {
    return <p className="muted">Change control statuses to capture SPRS snapshots over time.</p>;
  }
  const w = 100;
  const h = 48;
  const scores = history.map((h) => h.score);
  const min = Math.min(...scores, 0);
  const max = Math.max(...scores, 110);
  const range = max - min || 1;
  const points = scores
    .map((s, i) => {
      const x = (i / (scores.length - 1)) * w;
      const y = h - ((s - min) / range) * h;
      return `${x},${y}`;
    })
    .join(" ");
  const latest = history[history.length - 1];
  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${w} ${h}`} className="sprs-trend-chart" preserveAspectRatio="none" role="img" aria-label="SPRS trend">
        <polyline fill="none" stroke="var(--primary)" strokeWidth="0.35" vectorEffect="non-scaling-stroke" points={points} />
      </svg>
      <p className="muted chart-caption">
        Latest: {latest.score}/110 · {latest.timestamp}
      </p>
    </div>
  );
}
