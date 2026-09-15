import { useState } from "react";
import { CollectorInfo, ConnectorMonitorState, RunResultInfo } from "../../api";
import { COLLECTOR_FIELD_LABELS } from "./collectorFieldLabels";

type Props = {
  connector: CollectorInfo;
  isDue: boolean;
  running: boolean;
  formValues: Record<string, string>;
  lastRunResult?: RunResultInfo | null;
  onFormChange: (field: string, value: string) => void;
  onSaveCreds: () => void;
  onScheduleChange: (patch: { enabled?: boolean; interval?: string; attach_on_run?: boolean }) => void;
  onRun: (useFixture: boolean) => void;
};

function getHealthInfo(
  mon: ConnectorMonitorState | null | undefined,
  configured: boolean,
): { cls: string; label: string } {
  if (!configured) return { cls: "collector-dot--idle", label: "Not configured" };
  if (!mon?.last_run_at) return { cls: "collector-dot--idle", label: "Never run" };

  const s = mon.last_status;
  if (s === "healthy") return { cls: "collector-dot--pass", label: "Healthy" };
  if (s === "degraded") return { cls: "collector-dot--error", label: "Degraded" };
  if (s === "broken") return { cls: "collector-dot--fail", label: "Broken" };

  if (s === "pass" || s === "warn" || s === "fail") return { cls: "collector-dot--pass", label: "Healthy" };
  if (s === "error") return { cls: "collector-dot--error", label: "Degraded" };

  return { cls: "collector-dot--idle", label: s || "Unknown" };
}

export default function CollectorCard({
  connector: c,
  isDue,
  running,
  formValues,
  lastRunResult,
  onFormChange,
  onSaveCreds,
  onScheduleChange,
  onRun,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const [collapsed, setCollapsed] = useState(true);
  const mon = c.monitor;
  const health = getHealthInfo(mon, c.configured);

  const primaryAction = c.configured ? (
    <button
      type="button"
      className="btn btn-primary btn-sm"
      disabled={running}
      onClick={() => onRun(false)}
    >
      {running ? "Running…" : "Collect & attach"}
    </button>
  ) : (
    <button
      type="button"
      className="btn btn-primary btn-sm"
      disabled={running}
      onClick={() => onRun(true)}
      title="Offline demo using bundled fixture data"
    >
      {running ? "Running…" : "Try demo"}
    </button>
  );

  return (
    <section className={`panel collector-card${expanded ? " collector-card--expanded" : ""}`}>
      <div className="collector-card-compact">
        <div className="collector-card-compact-main">
          <div className="collector-card-title-row">
            <h2>{c.name} {c.beta && <span className="badge badge-beta">Beta</span>}</h2>
            <span className={`collector-dot ${health.cls}`} title={health.label} />
            <span className="collector-health-label">{health.label}</span>
            {isDue && <span className="badge badge-warn">Due</span>}
          </div>
          <p className="muted collector-card-tagline">{c.description}</p>
          {mon?.last_run_at && (
            <p className="muted collector-last-run">
              Last run: {mon.last_run_at}
            </p>
          )}
          {mon?.last_error && (
            <p className="collector-error-banner">
              Last run error: {mon.last_error}
            </p>
          )}
        </div>
        <div className="collector-card-compact-actions">
          {primaryAction}
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            aria-expanded={expanded}
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? "Hide setup" : "Configure"}
          </button>
        </div>
      </div>

      {lastRunResult && (
        <div className={`collector-run-result${collapsed ? " collector-run-result--collapsed" : ""}`}>
          <div className="collector-run-result-header" onClick={() => setCollapsed((v) => !v)} role="button" tabIndex={0}>
            <span>{lastRunResult.summary}</span>
            <button type="button" className="collector-run-result-toggle" onClick={(e) => { e.stopPropagation(); setCollapsed((v) => !v); }}>
              {collapsed ? "\u25B6" : "\u25BC"}
            </button>
          </div>
          {!collapsed && (
            <>
              {lastRunResult.checks.length > 0 && (
                <div className="collector-run-checks">
                  {lastRunResult.checks.map((check, i) => (
                    <div key={i} className={`collector-run-check collector-run-check--${check.status}`}>
                      <span className={`collector-dot collector-dot--${check.status}`} />
                      <div className="collector-run-check-body">
                        <span className="collector-run-check-name">{check.check_name}</span>
                        {check.evidence && <span className="collector-run-check-evidence">{check.evidence}</span>}
                      </div>
                      <span className="collector-run-check-status">{check.status}</span>
                    </div>
                  ))}
                </div>
              )}
              <div className="collector-run-footer">
                <span>Attached {lastRunResult.attached} evidence link(s). Drift events: {lastRunResult.drift}.</span>
              </div>
            </>
          )}
        </div>
      )}

      {expanded && (
        <div className="collector-card-details">
          <div className="collector-details-section">
            <h3 className="collector-details-heading">Schedule</h3>
            <p className="muted collector-hint" style={{ marginTop: 0 }}>
              The server checks due connectors about every 15 minutes. Each run attaches the latest
              result to mapped controls and appends a copy in Evidence Hub history.
            </p>
            <div className="collector-schedule">
              <label className="collector-schedule-toggle">
                <input
                  type="checkbox"
                  checked={mon?.enabled ?? false}
                  onChange={(e) => {
                    const enabled = e.target.checked;
                    if (enabled && (mon?.interval ?? "manual") === "manual") {
                      onScheduleChange({ enabled: true, interval: "daily" });
                    } else {
                      onScheduleChange({ enabled });
                    }
                  }}
                />
                Scheduled collection
              </label>
              <label className="collector-field collector-field-inline">
                <span>Interval</span>
                <select
                  value={mon?.interval ?? "manual"}
                  onChange={(e) => {
                    const interval = e.target.value;
                    if (interval === "manual") {
                      onScheduleChange({ interval: "manual", enabled: false });
                    } else {
                      onScheduleChange({ interval, enabled: true });
                    }
                  }}
                >
                  <option value="manual">Manual only</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </label>
              <label className="collector-schedule-toggle">
                <input
                  type="checkbox"
                  checked={mon?.attach_on_run ?? true}
                  onChange={(e) => onScheduleChange({ attach_on_run: e.target.checked })}
                />
                Attach evidence on run
              </label>
              {(mon?.attach_on_run ?? true) === false && (
                <p className="muted collector-hint" style={{ color: "var(--warning, #b45309)" }}>
                  Scheduled runs will collect without writing to controls or Evidence Hub.
                </p>
              )}
            </div>
          </div>

          <div className="collector-details-section">
            <h3 className="collector-details-heading">Credentials</h3>
            {c.permissions_hint && (
              <p className="muted collector-hint">
                <strong>Permissions:</strong> {c.permissions_hint}
              </p>
            )}
            <div className="collector-fields">
              {[...c.required_fields, ...c.optional_fields].map((field) => {
                const saved = c.configured_fields?.includes(field) ?? false;
                const value = formValues[field] ?? "";
                return (
                  <label key={field} className="collector-field">
                    <span>
                      {COLLECTOR_FIELD_LABELS[field] || field}
                      {c.required_fields.includes(field) ? " *" : ""}
                      {saved && !value && <span className="collector-field-saved">Saved</span>}
                    </span>
                    <input
                      type={
                        field.toLowerCase().includes("secret") || field === "token" ? "password" : "text"
                      }
                      value={value}
                      placeholder={
                        saved && !value
                          ? "••••••••"
                          : c.optional_fields.includes(field)
                            ? "Optional"
                            : ""
                      }
                      onChange={(e) => onFormChange(field, e.target.value)}
                    />
                  </label>
                );
              })}
            </div>
          </div>

          <div className="collector-actions">
            <button type="button" className="btn btn-secondary" onClick={onSaveCreds}>
              Save credentials
            </button>
            {c.configured && (
              <button
                type="button"
                className="btn btn-primary"
                disabled={running}
                onClick={() => onRun(false)}
              >
                {running ? "Running…" : "Collect & attach"}
              </button>
            )}
            <button
              type="button"
              className="btn btn-secondary"
              disabled={running}
              onClick={() => onRun(true)}
              title="Offline demo using bundled fixture data"
            >
              Demo (fixture)
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
