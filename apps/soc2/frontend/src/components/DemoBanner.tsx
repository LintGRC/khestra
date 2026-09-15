type Props = {
  label: string;
  onClear: () => void;
  clearing: boolean;
};

export default function DemoBanner({ label, onClear, clearing }: Props) {
  return (
    <div className="banner info demo-banner">
      <strong>Sample workspace — {label}</strong>
      <span className="muted">SOC 2 Type II readiness demo with synthetic evidence.</span>
      <button type="button" className="btn btn-secondary btn-sm" disabled={clearing} onClick={onClear}>
        {clearing ? "Clearing…" : "Exit demo"}
      </button>
    </div>
  );
}
