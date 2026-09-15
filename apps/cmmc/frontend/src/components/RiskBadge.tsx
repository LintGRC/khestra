type Props = {
  level: string;
};

const CLASS: Record<string, string> = {
  Low: "risk-low",
  Moderate: "risk-moderate",
  High: "risk-high",
  Critical: "risk-critical",
};

export default function RiskBadge({ level }: Props) {
  return <span className={`risk-badge ${CLASS[level] || "risk-moderate"}`}>{level}</span>;
}
