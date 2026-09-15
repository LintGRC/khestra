import { DriftEvent, EvidenceFreshness } from "../../api";

type Props = {
  freshness: EvidenceFreshness | null;
  driftEvents: DriftEvent[];
};

export default function MonitoringStatusPanel({ freshness, driftEvents }: Props) {
  const actionableDrift = driftEvents.filter((e) => e.event_type !== "first_run");
  const baselineCount = driftEvents.filter((e) => e.event_type === "first_run").length;

  return (
    <div className="panel-stack">
      {freshness && (
        <section className="panel">
          <div className="panel-header">
            <strong>Evidence freshness</strong>
            <span className="muted">{freshness.max_age_days}-day window</span>
          </div>
          <div className="panel-body">
            {freshness.stale_checks.length > 0 || freshness.stale_controls.length > 0 ? (
              <>
                {freshness.stale_checks.length > 0 && (
                  <>
                    <p className="col-summary muted">
                      {freshness.stale_check_count} stale check{freshness.stale_check_count !== 1 ? "s" : ""}
                      {freshness.stale_control_count > 0 && (
                        <> · {freshness.stale_control_count} stale control{freshness.stale_control_count !== 1 ? "s" : ""}</>
                      )}
                    </p>
                    <div className="col-grid col-grid--3col">
                      <span className="col-header">Connector</span>
                      <span className="col-header">Check</span>
                      <span className="col-header">Age</span>
                      {freshness.stale_checks.slice(0, 12).map((c) => (
                        <>
                          <strong>{c.connector_id}</strong>
                          <span>{c.check_id}</span>
                          <span className="muted">{c.collected_at || "unknown"}</span>
                        </>
                      ))}
                    </div>
                  </>
                )}
                {freshness.stale_controls.length > 0 && (
                  <>
                    <div className="col-separator">Stale controls</div>
                    <div className="col-grid col-grid--2col">
                      <span className="col-header">Control</span>
                      <span className="col-header">Latest upload</span>
                      {freshness.stale_controls.slice(0, 12).map((c) => (
                        <>
                          <strong>{c.control_id}</strong>
                          <span className="muted">{c.latest_upload || "unknown"}</span>
                        </>
                      ))}
                    </div>
                  </>
                )}
                <p className="muted col-more">
                  {Math.max(freshness.stale_checks.length, freshness.stale_controls.length) > 12 &&
                    `+${freshness.stale_checks.length + freshness.stale_controls.length - 12} more`}
                </p>
              </>
            ) : (
              <p className="muted">
                All connector evidence is within the {freshness.max_age_days}-day freshness window.
              </p>
            )}
          </div>
        </section>
      )}

      {actionableDrift.length > 0 && (
        <section className="panel">
          <div className="panel-header">
            <strong>Drift &amp; changes</strong>
          </div>
          <div className="panel-body">
            <p className="col-summary muted">
              {actionableDrift.length} drift event{actionableDrift.length !== 1 ? "s" : ""}
            </p>
            <div className="col-table">
              <div className="col-table-head">
                <span className="col-header">Type</span>
                <span className="col-header">Connector</span>
                <span className="col-header">Check</span>
                <span className="col-header">When</span>
              </div>
              {actionableDrift.slice(0, 12).map((e) => (
                <div className="col-drift-item" key={e.id}>
                  <div className="col-drift-row">
                    <span className={`drift-type-tag drift-type-tag--${e.event_type}`}>{e.event_type}</span>
                    <strong>{e.connector_id}</strong>
                    <span>{e.check_id}</span>
                    <span className="muted">{e.timestamp}</span>
                  </div>
                  <p className="col-drift-summary">{e.summary}</p>
                </div>
              ))}
            </div>
            {actionableDrift.length > 12 && (
              <p className="muted col-more">+{actionableDrift.length - 12} more drift events</p>
            )}
            {baselineCount > 0 && (
              <details className="col-baseline">
                <summary>Baseline runs ({baselineCount})</summary>
                <div className="col-grid col-grid--2col">
                  <span className="col-header">Connector / Check</span>
                  <span className="col-header">Summary</span>
                  {driftEvents
                    .filter((e) => e.event_type === "first_run")
                    .slice(0, 20)
                    .map((e) => (
                      <>
                        <span>
                          <strong>{e.connector_id}</strong> / {e.check_id}
                        </span>
                        <span className="muted">{e.summary}</span>
                      </>
                    ))}
                </div>
              </details>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
