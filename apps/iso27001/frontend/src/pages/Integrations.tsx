import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type ConnectorInfo } from "../api";

const INTERVAL_LABELS: Record<string, string> = {
  manual: "Manual",
  daily: "Daily",
  weekly: "Weekly",
};

function statusBadge(status: string) {
  const m: Record<string, string> = {
    pass: "badge-success",
    fail: "badge-danger",
    warn: "badge-warning",
    error: "badge-danger",
    never: "badge-muted",
    ok: "badge-success",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status}</span>;
}

export default function IntegrationsPage() {
  const [connectors, setConnectors] = useState<ConnectorInfo[]>([]);
  const [dueConnectors, setDueConnectors] = useState<string[]>([]);
  const [driftEvents, setDriftEvents] = useState<{ connector_id: string; check_id: string; event_type: string; summary: string; timestamp: string }[]>([]);
  const [monitorStates, setMonitorStates] = useState<Record<string, ConnectorInfo["monitor"]>>({});
  const [recentRuns, setRecentRuns] = useState<{ connector_id: string; completed_at: string; status: string; summary: string; fixture: boolean }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [forms, setForms] = useState<Record<string, Record<string, string>>>({});
  const [running, setRunning] = useState<string | null>(null);
  const [runningDue, setRunningDue] = useState(false);
  const [lastResult, setLastResult] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const d = await api.collectors();
      setConnectors(d.connectors);
      setDueConnectors(d.monitoring?.due_connectors ?? []);
      const states: Record<string, ConnectorInfo["monitor"]> = {};
      (d.monitoring?.connectors ?? []).forEach((s) => {
        if (s) states[s.connector_id] = s;
      });
      setMonitorStates(states);
      setDriftEvents(d.drift_events ?? []);
      setRecentRuns(d.monitoring?.recent_runs ?? []);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const configuredCount = useMemo(() => connectors.filter((c) => c.configured).length, [connectors]);
  const dueCount = dueConnectors.length;
  const needsAttention = dueCount > 0 || driftEvents.length > 0;

  const onSaveCreds = async (connectorId: string) => {
    const creds = forms[connectorId] || {};
    try {
      await api.saveCollectorCredentials(connectorId, creds);
      setLastResult(`Saved credentials for ${connectorId}.`);
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    }
  };

  const onClearCreds = async (connectorId: string) => {
    if (!confirm(`Remove credentials for ${connectorId}?`)) return;
    try {
      await api.deleteCollectorCredentials(connectorId);
      setLastResult(`Removed credentials for ${connectorId}.`);
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    }
  };

  const onScheduleChange = async (
    connectorId: string,
    patch: { enabled?: boolean; interval?: string; attach_on_run?: boolean },
  ) => {
    try {
      await api.patchCollectorSchedule(connectorId, patch);
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    }
  };

  const onRun = async (connectorId: string, useFixture: boolean) => {
    setRunning(connectorId);
    setLastResult("");
    try {
      const result = await api.runCollector(connectorId, { use_fixture: useFixture, attach: true });
      const attached = result.attached?.length ?? 0;
      const drift = result.drift_events?.length ?? 0;
      setLastResult(
        `${connectorId}: ${result.run?.summary ?? "run complete"}. Attached ${attached} control link(s). Drift events: ${drift}.`,
      );
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    } finally {
      setRunning(null);
    }
  };

  const onRunDue = async () => {
    setRunningDue(true);
    setLastResult("");
    try {
      const result = await api.runDueCollectors(false);
      setLastResult(`Ran ${result.ran_count ?? 0} due connector(s).`);
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    } finally {
      setRunningDue(false);
    }
  };

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Integrations</h2>
          <p className="muted">
            Connect cloud systems to collect evidence automatically. Results map to ISO 27001 controls via the shared
            evidence layer.
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={onRunDue} disabled={runningDue || dueCount === 0}>
          {runningDue ? "Running due…" : `Run due (${dueCount})`}
        </button>
      </div>

      {lastResult && (
        <div className="banner info" style={{ marginBottom: 12 }}>
          {lastResult}{" "}
          <button type="button" className="btn-link" onClick={() => setLastResult("")}>Dismiss</button>
        </div>
      )}
      {error && <div className="banner danger" style={{ marginBottom: 12 }}>{error}</div>}

      <div className="metric-grid" style={{ marginBottom: 16 }}>
        <div className="metric-card"><div className="metric-value">{configuredCount}</div><div className="metric-label">Configured</div></div>
        <div className="metric-card"><div className="metric-value">{connectors.length}</div><div className="metric-label">Connectors</div></div>
        <div className="metric-card"><div className="metric-value">{dueCount}</div><div className="metric-label">Due now</div></div>
        <div className="metric-card"><div className="metric-value">{driftEvents.length}</div><div className="metric-label">Drift events</div></div>
      </div>

      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          <div className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                    <th style={{ padding: "0.75rem 0.5rem" }}>Connector</th>
                    <th style={{ padding: "0.75rem 0.5rem" }}>Status</th>
                    <th style={{ padding: "0.75rem 0.5rem" }}>Schedule</th>
                    <th style={{ padding: "0.75rem 0.5rem" }}>Last run</th>
                    <th style={{ padding: "0.75rem 0.5rem" }}>Credentials</th>
                    <th style={{ padding: "0.75rem 0.5rem" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {connectors.map((c) => {
                    const mon = monitorStates[c.id] ?? c.monitor;
                    return (
                      <tr key={c.id} style={{ borderBottom: "1px solid var(--border-subtle)", verticalAlign: "top" }}>
                        <td style={{ padding: "0.65rem 0.5rem" }}>
                          <strong>{c.name}</strong>
                          {c.beta && <span className="badge badge-warning" style={{ marginLeft: 6 }}>beta</span>}
                          <div className="muted" style={{ fontSize: 12 }}>{c.description}</div>
                          {c.permissions_hint && (
                            <div className="muted" style={{ fontSize: 11 }}>Needs: {c.permissions_hint}</div>
                          )}
                        </td>
                        <td style={{ padding: "0.65rem 0.5rem" }}>
                          {c.configured ? <span className="badge badge-success">configured</span> : <span className="badge badge-muted">not configured</span>}
                          {mon && (
                            <div style={{ marginTop: 4 }}>
                              {statusBadge(mon.last_status)}
                              {mon.last_error && <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>{mon.last_error}</div>}
                            </div>
                          )}
                        </td>
                        <td style={{ padding: "0.65rem 0.5rem" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <label style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                              <input
                                type="checkbox"
                                checked={mon?.enabled ?? false}
                                onChange={(e) => onScheduleChange(c.id, { enabled: e.target.checked })}
                              />
                              Enabled
                            </label>
                            <select
                              value={mon?.interval ?? "manual"}
                              onChange={(e) => onScheduleChange(c.id, { interval: e.target.value })}
                              style={{ fontSize: 12 }}
                            >
                              {Object.entries(INTERVAL_LABELS).map(([k, v]) => (
                                <option key={k} value={k}>{v}</option>
                              ))}
                            </select>
                          </div>
                          <div style={{ fontSize: 12, marginTop: 4 }}>
                            <label style={{ display: "flex", alignItems: "center", gap: 4 }}>
                              <input
                                type="checkbox"
                                checked={mon?.attach_on_run ?? true}
                                onChange={(e) => onScheduleChange(c.id, { attach_on_run: e.target.checked })}
                              />
                              Attach evidence on run
                            </label>
                          </div>
                        </td>
                        <td style={{ padding: "0.65rem 0.5rem", fontSize: 12 }}>
                          {mon?.last_run_at ? (
                            <>
                              {mon.last_run_at.slice(0, 16).replace("T", " ")}
                              {mon && (mon.check_count > 0 || mon.pass_count > 0) && (
                                <div className="muted" style={{ fontSize: 11 }}>
                                  {mon.check_count} checks · {mon.pass_count} pass / {mon.fail_count} fail / {mon.warn_count} warn
                                </div>
                              )}
                            </>
                          ) : "—"}
                        </td>
                        <td style={{ padding: "0.65rem 0.5rem" }}>
                          {c.configured ? (
                            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                              <span className="badge badge-success" style={{ fontSize: 11 }}>saved</span>
                              <button className="btn btn-sm btn-ghost" style={{ fontSize: 11, color: "var(--danger)" }} onClick={() => onClearCreds(c.id)}>
                                Remove
                              </button>
                            </div>
                          ) : (
                            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                              {c.required_fields.map((f) => (
                                <input
                                  key={f}
                                  type="password"
                                  value={forms[c.id]?.[f] ?? ""}
                                  onChange={(e) =>
                                    setForms((prev) => ({ ...prev, [c.id]: { ...prev[c.id], [f]: e.target.value } }))
                                  }
                                  placeholder={f}
                                  style={{ fontSize: 12, width: 160 }}
                                />
                              ))}
                              <button className="btn btn-sm btn-primary" style={{ fontSize: 11, width: 160 }} onClick={() => onSaveCreds(c.id)}>
                                Save
                              </button>
                            </div>
                          )}
                        </td>
                        <td style={{ padding: "0.65rem 0.5rem" }}>
                          <div style={{ display: "flex", gap: 4, flexDirection: "column", width: 130 }}>
                            <button className="btn btn-sm btn-secondary" style={{ fontSize: 11 }} disabled={running === c.id} onClick={() => onRun(c.id, false)}>
                              {running === c.id ? "Running…" : "Run"}
                            </button>
                            <button className="btn btn-sm btn-ghost" style={{ fontSize: 11 }} disabled={running === c.id} onClick={() => onRun(c.id, true)}>
                              Try demo (fixture)
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <p className="muted" style={{ fontSize: 12, marginBottom: 16 }}>
            Use <strong>Try demo (fixture)</strong> to attach sample evidence without credentials. The ISO 27001 app
            runs the shared collector engine; evidence lands in the Evidence Hub mapped to the controls each check
            covers.
          </p>

          {needsAttention && (
            <div className="panel" style={{ marginBottom: 16 }}>
              <div className="panel-body">
                <h4 style={{ margin: "0 0 8px" }}>Drift events</h4>
                {driftEvents.length === 0 ? (
                  <p className="muted" style={{ fontSize: 13 }}>No drift events.</p>
                ) : (
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                        <th style={{ padding: "0.5rem" }}>Connector</th>
                        <th style={{ padding: "0.5rem" }}>Check</th>
                        <th style={{ padding: "0.5rem" }}>Event</th>
                        <th style={{ padding: "0.5rem" }}>Summary</th>
                        <th style={{ padding: "0.5rem" }}>Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {driftEvents.slice(0, 10).map((e, i) => (
                        <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                          <td style={{ padding: "0.5rem" }}>{e.connector_id}</td>
                          <td style={{ padding: "0.5rem" }}>{e.check_id}</td>
                          <td style={{ padding: "0.5rem" }}>{statusBadge(e.event_type)}</td>
                          <td style={{ padding: "0.5rem" }}>{e.summary}</td>
                          <td style={{ padding: "0.5rem" }} className="muted">{e.timestamp?.slice(0, 16).replace("T", " ")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {recentRuns.length > 0 && (
            <div className="panel">
              <div className="panel-body">
                <h4 style={{ margin: "0 0 8px" }}>Recent runs</h4>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                      <th style={{ padding: "0.5rem" }}>Connector</th>
                      <th style={{ padding: "0.5rem" }}>Status</th>
                      <th style={{ padding: "0.5rem" }}>Fixture</th>
                      <th style={{ padding: "0.5rem" }}>Summary</th>
                      <th style={{ padding: "0.5rem" }}>Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentRuns.slice(0, 8).map((r, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                        <td style={{ padding: "0.5rem" }}>{r.connector_id}</td>
                        <td style={{ padding: "0.5rem" }}>{statusBadge(r.status)}</td>
                        <td style={{ padding: "0.5rem" }}>{r.fixture ? "yes" : "no"}</td>
                        <td style={{ padding: "0.5rem" }}>{r.summary}</td>
                        <td style={{ padding: "0.5rem" }} className="muted">{r.completed_at?.slice(0, 16).replace("T", " ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
