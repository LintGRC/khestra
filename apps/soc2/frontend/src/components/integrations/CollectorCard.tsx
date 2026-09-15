import { useState } from "react";
import { CollectorInfo } from "../../api";
import { COLLECTOR_FIELD_LABELS } from "./collectorFieldLabels";

type Props = {
  connector: CollectorInfo;
  isDue: boolean;
  running: boolean;
  formValues: Record<string, string>;
  onFormChange: (field: string, value: string) => void;
  onSaveCreds: () => void;
  onScheduleChange: (patch: { enabled?: boolean; interval?: string; attach_on_run?: boolean }) => void;
  onRun: (useFixture: boolean) => void;
};

export default function CollectorCard({
  connector: c,
  isDue,
  running,
  formValues,
  onFormChange,
  onSaveCreds,
  onScheduleChange,
  onRun,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const mon = c.monitor;

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
            <h2>{c.name}</h2>
            <span className={`badge ${c.configured ? "badge-ok" : "badge-muted"}`}>
              {c.configured ? "Configured" : "Not configured"}
            </span>
            {isDue && <span className="badge badge-warn">Due</span>}
          </div>
          <p className="muted collector-card-tagline">{c.description}</p>
          {mon?.last_run_at && (
            <p className="muted collector-last-run">
              Last run: {mon.last_run_at} · {mon.last_status}
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

      {expanded && (
        <div className="collector-card-details">
          <div className="collector-details-section">
            <h3 className="collector-details-heading">Schedule</h3>
            <div className="collector-schedule">
              <label className="collector-schedule-toggle">
                <input
                  type="checkbox"
                  checked={mon?.enabled ?? false}
                  onChange={(e) => onScheduleChange({ enabled: e.target.checked })}
                />
                Scheduled collection
              </label>
              <label className="collector-field collector-field-inline">
                <span>Interval</span>
                <select
                  value={mon?.interval ?? "manual"}
                  onChange={(e) => onScheduleChange({ interval: e.target.value })}
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
