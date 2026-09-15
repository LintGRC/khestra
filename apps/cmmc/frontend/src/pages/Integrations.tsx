import { useCallback, useEffect, useMemo, useState } from "react";
import { api, CollectorsDashboard, EvidenceFreshness, RunResultInfo, SchedulerStatus } from "../api";
import PageIntro from "../components/PageIntro";
import CollectorCard from "../components/integrations/CollectorCard";
import IntegrationsSummary from "../components/integrations/IntegrationsSummary";
import MonitoringStatusPanel from "../components/integrations/MonitoringStatusPanel";
import WebhookPanel from "../components/integrations/WebhookPanel";
import { PanelSkeleton } from "../components/ui/Skeleton";

export default function IntegrationsPage() {
  const [connectors, setConnectors] = useState<CollectorsDashboard["connectors"]>([]);
  const [driftEvents, setDriftEvents] = useState<CollectorsDashboard["drift_events"]>([]);
  const [freshness, setFreshness] = useState<EvidenceFreshness | null>(null);
  const [dueConnectors, setDueConnectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [forms, setForms] = useState<Record<string, Record<string, string>>>({});
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, RunResultInfo>>({});
  const [webhooks, setWebhooks] = useState<Awaited<ReturnType<typeof api.webhooks>>["collectors"]>([]);
  const [envWebhookToken, setEnvWebhookToken] = useState(false);
  const [webhookName, setWebhookName] = useState("");
  const [webhookSource, setWebhookSource] = useState("");
  const [newWebhookToken, setNewWebhookToken] = useState<string | null>(null);
  const [scheduler, setScheduler] = useState<SchedulerStatus>({ alive: false, last_check_at: null, last_error: null, ran_count: 0, error_count: 0 });
  const [filter, setFilter] = useState<"all" | "connected">("connected");
  const [aiKeyState, setAiKeyState] = useState<{ has_ai_key: boolean; source: string }>({ has_ai_key: false, source: "none" });
  const [aiKeyInput, setAiKeyInput] = useState("");
  const [aiKeyBusy, setAiKeyBusy] = useState(false);

  const refreshAiKey = useCallback(async () => {
    try {
      const status = await api.aiKeyStatus();
      setAiKeyState(status);
    } catch {
      // status endpoint is best-effort on the Integrations page
    }
  }, []);

  const onSaveAiKey = async () => {
    if (!aiKeyInput.trim()) return;
    setAiKeyBusy(true);
    try {
      await api.saveAiKey(aiKeyInput.trim());
      setAiKeyInput("");
      await refreshAiKey();
    } catch (err) {
      setError(String(err));
    } finally {
      setAiKeyBusy(false);
    }
  };

  const onRemoveAiKey = async () => {
    setAiKeyBusy(true);
    try {
      await api.deleteAiKey();
      await refreshAiKey();
    } catch (err) {
      setError(String(err));
    } finally {
      setAiKeyBusy(false);
    }
  };

  const applyDashboard = (data: CollectorsDashboard) => {
    setConnectors(data.connectors);
    setDriftEvents(data.drift_events);
    setFreshness(data.freshness);
    setDueConnectors(data.monitoring.due_connectors);
    const latestRuns: Record<string, RunResultInfo> = {};
    for (const r of data.recent_runs ?? []) {
      if (r.fixture) continue;
      if (!latestRuns[r.connector_id]) {
        latestRuns[r.connector_id] = {
          summary: r.summary,
          checks: r.checks.map((c) => ({
            check_name: c.check_name,
            status: c.status,
            evidence: c.evidence,
            detail: c.detail,
          })),
          attached: 0,
          drift: r.drift_events?.length ?? 0,
        };
      }
    }
    setResults(latestRuns);
  };

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [dashboard, webhookData] = await Promise.all([api.collectors(), api.webhooks()]);
      applyDashboard(dashboard);
      setWebhooks(webhookData.collectors);
      setEnvWebhookToken(webhookData.env_token_configured);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    refreshAiKey();
  }, [refreshAiKey]);

  useEffect(() => {
    const poll = () => api.schedulerStatus().then(setScheduler).catch(() => {});
    poll();
    const id = setInterval(poll, 30000);
    return () => clearInterval(id);
  }, []);

  const configuredCount = useMemo(() => connectors.filter((c) => c.configured).length, [connectors]);
  const driftCount = useMemo(
    () => driftEvents.filter((e) => e.event_type !== "first_run").length,
    [driftEvents],
  );
  const staleControlCount = freshness?.stale_control_count ?? 0;
  const dueCount = dueConnectors.length;
  const needsAttention = dueCount > 0 || staleControlCount > 0 || driftCount > 0;
  const visibleConnectors = useMemo(() => {
    const sorted = [...connectors].sort((a, b) => a.name.localeCompare(b.name));
    if (filter === "all") return sorted;
    return sorted.filter((c) => c.configured);
  }, [connectors, filter]);

  const onSaveCreds = async (connectorId: string) => {
    const creds = forms[connectorId] || {};
    try {
      await api.saveCollectorCredentials(connectorId, creds);
      await refresh();
    } catch (err) {
      setResults((prev) => ({ ...prev, [connectorId]: { summary: String(err), checks: [], attached: 0, drift: 0 } }));
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
      setResults((prev) => ({ ...prev, [connectorId]: { summary: String(err), checks: [], attached: 0, drift: 0 } }));
    }
  };

  const onRun = async (connectorId: string, useFixture: boolean) => {
    setRunning(connectorId);
    try {
      const result = await api.runCollector(connectorId, { use_fixture: useFixture, attach: true });
      setResults((prev) => ({
        ...prev,
        [connectorId]: {
          summary: result.run.summary,
          checks: result.run.checks.map((c) => ({ check_name: c.check_name, status: c.status, evidence: c.evidence, detail: c.detail })),
          attached: result.attached?.length ?? 0,
          drift: result.drift_events?.length ?? 0,
        },
      }));
      await refresh();
    } catch (err) {
      setResults((prev) => ({ ...prev, [connectorId]: { summary: String(err), checks: [], attached: 0, drift: 0 } }));
    } finally {
      setRunning(null);
    }
  };

  const onCreateWebhook = async () => {
    if (!webhookName.trim() || !webhookSource.trim()) {
      return;
    }
    try {
      const result = await api.createWebhook(webhookName.trim(), webhookSource.trim());
      setNewWebhookToken(result.collector.webhook_token || null);
      setWebhookName("");
      setWebhookSource("");
      await refresh();
    } catch (err) {
      setError(String(err));
    }
  };

  const onDeleteWebhook = async (collectorId: string) => {
    try {
      await api.deleteWebhook(collectorId);
      await refresh();
    } catch (err) {
      setError(String(err));
    }
  };

  const onRunDue = async () => {
    setRunning("__due__");
    try {
      await api.runDueCollectors(true);
      await refresh();
    } catch (err) {
      console.error("Due runs failed:", err);
    } finally {
      setRunning(null);
    }
  };

  return (
    <div className="integrations-page">
      <PageIntro view="Integrations" title="Integrations" />

      {loading && (
        <div className="panel-stack">
          <div className="panel">
            <div className="panel-body">
              <PanelSkeleton rows={2} />
            </div>
          </div>
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className="panel">
              <div className="panel-body">
                <PanelSkeleton rows={4} />
              </div>
            </div>
          ))}
        </div>
      )}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && (
        <IntegrationsSummary
          configuredCount={configuredCount}
          totalCount={connectors.length}
          dueCount={dueCount}
          staleControlCount={staleControlCount}
          driftCount={driftCount}
          runningDue={running === "__due__"}
          runDueDisabled={running !== null || dueCount === 0}
          onRunDue={onRunDue}
          schedulerAlive={scheduler.alive}
          schedulerLastCheck={scheduler.last_check_at}
        />
      )}

      {!loading && (
      <div className="integrations-sections panel-stack">
        <h3 className="page-section-heading">Connectors</h3>
        <div className="integrations-filter-bar">
          <button
            type="button"
            className={filter === "connected" ? "btn btn-sm btn-primary" : "btn btn-sm btn-secondary"}
            onClick={() => setFilter("connected")}
          >
            Connected ({configuredCount})
          </button>
          <button
            type="button"
            className={filter === "all" ? "btn btn-sm btn-primary" : "btn btn-sm btn-secondary"}
            onClick={() => setFilter("all")}
          >
            All ({connectors.length})
          </button>
        </div>
        <div className="panel-stack">
          {visibleConnectors.map((c) => (
            <CollectorCard
              key={c.id}
              connector={c}
              isDue={dueConnectors.includes(c.id)}
              running={running === c.id}
              formValues={forms[c.id] ?? {}}
              lastRunResult={results[c.id]}
              onFormChange={(field, value) =>
                setForms((prev) => ({
                  ...prev,
                  [c.id]: { ...prev[c.id], [field]: value },
                }))
              }
              onSaveCreds={() => onSaveCreds(c.id)}
              onScheduleChange={(patch) => onScheduleChange(c.id, patch)}
              onRun={(useFixture) => onRun(c.id, useFixture)}
            />
          ))}
        </div>

        {needsAttention && (
          <>
            <h3 className="page-section-heading">Needs attention</h3>
            <MonitoringStatusPanel freshness={freshness} driftEvents={driftEvents} />
          </>
        )}

        <h3 className="page-section-heading">AI (bring your own key)</h3>
        <div className="panel">
          <div className="panel-body ai-key-panel">
            <p className="ai-key-status">
              {aiKeyState.has_ai_key
                ? `AI polish is available (key source: ${aiKeyState.source})`
                : "AI polish is off — add your own API key below."}
            </p>
            {aiKeyState.has_ai_key && aiKeyState.source === "stored" && (
              <p className="ai-key-masked">Stored key: •••••••• (encrypted at rest on this server)</p>
            )}
            <div className="ai-key-form">
              <input
                type="password"
                className="input"
                placeholder={aiKeyState.source === "stored" ? "Replace stored key" : "Paste your OpenAI-compatible API key"}
                value={aiKeyInput}
                disabled={aiKeyBusy}
                onChange={(e) => setAiKeyInput(e.target.value)}
              />
              <button
                type="button"
                className="btn btn-sm btn-primary"
                disabled={aiKeyBusy || !aiKeyInput.trim()}
                onClick={onSaveAiKey}
              >
                Save key
              </button>
              {aiKeyState.source === "stored" && (
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  disabled={aiKeyBusy}
                  onClick={onRemoveAiKey}
                >
                  Remove
                </button>
              )}
            </div>
            <p className="ai-key-note">
              The key stays on your server (encrypted, under the local data directory) and is never
              sent back to the UI or included in any export.
            </p>
          </div>
        </div>

        <h3 className="page-section-heading">Advanced</h3>
        <WebhookPanel
          webhooks={webhooks}
          envWebhookToken={envWebhookToken}
          webhookName={webhookName}
          webhookSource={webhookSource}
          newWebhookToken={newWebhookToken}
          onWebhookNameChange={setWebhookName}
          onWebhookSourceChange={setWebhookSource}
          onCreate={onCreateWebhook}
          onDelete={onDeleteWebhook}
        />
      </div>
      )}
    </div>
  );
}
