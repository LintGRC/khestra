import { DriftEvent, EvidenceFreshness } from "../../api";

type Props = {
  freshness: EvidenceFreshness | null;
  driftEvents: DriftEvent[];
};

export default function MonitoringStatusPanel({ freshness, driftEvents }: Props) {
  const actionableDrift = driftEvents.filter((e) => e.event_type !== "first_run");
  const baselineCount = driftEvents.filter((e) => e.event_type === "first_run").length;

  return (
    <div className="integrations-status-grid">
      {freshness && (
        <section className="panel freshness-panel">
          <div className="panel-header">
            <strong>Evidence freshness</strong>
            <span className="muted">{freshness.max_age_days}-day window</span>
          </div>
          <div className="panel-body">
            <p className="muted">
              Stale checks: {freshness.stale_check_count} · Stale controls with collector evidence:{" "}
              {freshness.stale_control_count}
            </p>
            {(freshness.stale_controls?.length ?? 0) > 0 ? (
              <ul className="collector-run-list">
                {(freshness.stale_controls ?? []).slice(0, 12).map((c) => (
                  <li key={c.control_id}>
                    <strong>{c.control_id}</strong> — last upload {c.latest_upload || "unknown"}
                  </li>
                ))}
                {(freshness.stale_controls?.length ?? 0) > 12 && (
                  <li className="muted">
                    +{(freshness.stale_controls?.length ?? 0) - 12} more stale control
                    {(freshness.stale_controls?.length ?? 0) - 12 === 1 ? "" : "s"}
                  </li>
                )}
              </ul>
            ) : (
              <p className="muted">All collector evidence is within the freshness window.</p>
            )}
          </div>
        </section>
      )}

      {driftEvents.length > 0 && (
        <section className="panel drift-panel">
          <div className="panel-header">
            <strong>Drift &amp; changes</strong>
          </div>
          <div className="panel-body">
            <p className="muted drift-panel-lead">
              Regressions and recoveries mean check results changed between runs. Baseline runs are
              listed below when present.
            </p>
            {actionableDrift.length > 0 ? (
              <ul className="drift-event-list">
                {actionableDrift.slice(0, 12).map((e) => (
                  <li key={e.id} className={`drift-event drift-event--${e.event_type}`}>
                    <div className="drift-event-header">
                      <span className="drift-event-type">{e.event_type}</span>
                      <span className="drift-event-target">
                        <strong>{e.connector_id}</strong> / {e.check_id}
                      </span>
                    </div>
                    <p>{e.summary}</p>
                    <span className="muted">{e.timestamp}</span>
                  </li>
                ))}
                {actionableDrift.length > 12 && (
                  <p className="muted">+{actionableDrift.length - 12} more drift events</p>
                )}
              </ul>
            ) : (
              <p className="muted">No regressions or config drift yet — only baseline runs recorded.</p>
            )}
            {baselineCount > 0 && (
              <details className="drift-baseline-details">
                <summary>Baseline runs ({baselineCount})</summary>
                <ul className="drift-event-list">
                  {driftEvents
                    .filter((e) => e.event_type === "first_run")
                    .slice(0, 20)
                    .map((e) => (
                      <li key={e.id} className="drift-event drift-event--first_run">
                        <div className="drift-event-header">
                          <span className="drift-event-type">baseline</span>
                          <span className="drift-event-target">
                            <strong>{e.connector_id}</strong> / {e.check_id}
                          </span>
                        </div>
                        <p>{e.summary}</p>
                      </li>
                    ))}
                </ul>
              </details>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
