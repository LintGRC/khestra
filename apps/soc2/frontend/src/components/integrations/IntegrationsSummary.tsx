type Props = {
  configuredCount: number;
  totalCount: number;
  dueCount: number;
  staleControlCount: number;
  driftCount: number;
  runningDue: boolean;
  runDueDisabled: boolean;
  onRunDue: () => void;
};

export default function IntegrationsSummary({
  configuredCount,
  totalCount,
  dueCount,
  staleControlCount,
  driftCount,
  runningDue,
  runDueDisabled,
  onRunDue,
}: Props) {
  return (
    <div className="stats integrations-summary">
      <div className="stat-card">
        <div className="stat-label">Configured</div>
        <div className="stat-value">
          {configuredCount}/{totalCount}
        </div>
      </div>
      {dueCount > 0 && (
        <div className="stat-card stat-warn integrations-stat-action">
          <div className="stat-label">Due for run</div>
          <div className="integrations-stat-row">
            <div className="stat-value">{dueCount}</div>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={runDueDisabled}
              onClick={onRunDue}
            >
              {runningDue ? "Running…" : "Run due"}
            </button>
          </div>
        </div>
      )}
      {staleControlCount > 0 && (
        <div className="stat-card stat-warn">
          <div className="stat-label">Stale controls</div>
          <div className="stat-value">{staleControlCount}</div>
        </div>
      )}
      {driftCount > 0 && (
        <div className="stat-card stat-warn">
          <div className="stat-label">Drift events</div>
          <div className="stat-value">{driftCount}</div>
        </div>
      )}
    </div>
  );
}
