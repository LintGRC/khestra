import { ReadinessScores } from "../api";
import { pctTone } from "../lib/readinessTone";

type Props = {
  scores: ReadinessScores;
  className?: string;
};

const ROWS: [string, keyof ReadinessScores][] = [
  ["Assessment", "assessment_readiness"],
  ["Documentation", "documentation_readiness"],
  ["Evidence", "evidence_readiness"],
  ["Audit readiness", "audit_readiness"],
];

export default function ReadinessMetricBars({ scores, className }: Props) {
  return (
    <div className={className ? `metric-bars ${className}` : "metric-bars"}>
      {ROWS.map(([label, key]) => {
        const pct = scores[key] as number;
        const tone = pctTone(pct);
        return (
          <div key={label} className="metric-bar-row">
            <span className="metric-bar-label">{label}</span>
            <div className="metric-bar-track" aria-hidden>
              <div
                className={`metric-bar-fill metric-bar-fill-${tone}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="metric-bar-pct">{pct}%</span>
          </div>
        );
      })}
    </div>
  );
}
