type Props = {
  configuredCount: number;
  totalCount: number;
  dueCount: number;
  staleControlCount: number;
  driftCount: number;
  runningDue: boolean;
  runDueDisabled: boolean;
  onRunDue: () => void;
  schedulerAlive: boolean | null;
  schedulerLastCheck: string | null;
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
  schedulerAlive,
  schedulerLastCheck,
}: Props) {
  const lastCheckLabel = (() => {
    if (!schedulerLastCheck) return null;
    const d = new Date(schedulerLastCheck);
    if (Number.isNaN(d.getTime())) return schedulerLastCheck;
    return d.toLocaleString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      timeZoneName: "short",
    });
  })();

  return (
    <div className="stats integrations-summary">
      {schedulerAlive !== null && (
        <div className="stat-card">
          <div className="stat-label">Scheduler</div>
          <div className="stat-value" style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                display: "inline-block",
                background: schedulerAlive ? "var(--ok, #2d6a4f)" : "var(--danger, #b91c1c)",
              }}
            />
            {schedulerAlive ? "Running" : "Stopped"}
          </div>
          {lastCheckLabel && (
            <div className="stat-sub" style={{ fontSize: "0.7rem", color: "var(--muted, #6c757d)" }}>
              Last poll: {lastCheckLabel}
            </div>
          )}
        </div>
      )}
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
