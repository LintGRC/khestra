import { useCallback, useEffect, useMemo, useState } from "react";
import { api, CollectorsDashboard, EvidenceFreshness } from "../api";
import PageIntro from "../components/PageIntro";
import ActionFeedback from "../components/integrations/ActionFeedback";
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
  const [lastResult, setLastResult] = useState("");
  const [webhooks, setWebhooks] = useState<Awaited<ReturnType<typeof api.webhooks>>["collectors"]>([]);
  const [envWebhookToken, setEnvWebhookToken] = useState(false);
  const [webhookName, setWebhookName] = useState("");
  const [webhookSource, setWebhookSource] = useState("");
  const [newWebhookToken, setNewWebhookToken] = useState<string | null>(null);
  const [runningDue, setRunningDue] = useState(false);

  const applyDashboard = (data: CollectorsDashboard) => {
    setConnectors(data.connectors);
    setDriftEvents(data.drift_events);
    setFreshness(data.freshness);
    setDueConnectors(data.monitoring.due_connectors);
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

  const configuredCount = useMemo(() => connectors.filter((c) => c.configured).length, [connectors]);
  const driftCount = useMemo(
    () => driftEvents.filter((e) => e.event_type !== "first_run").length,
    [driftEvents],
  );
  const staleControlCount = freshness?.stale_control_count ?? 0;
  const dueCount = dueConnectors.length;
  const needsAttention = dueCount > 0 || staleControlCount > 0 || driftCount > 0;

  const onSaveCreds = async (connectorId: string) => {
    const creds = forms[connectorId] || {};
    try {
      await api.saveCollectorCredentials(connectorId, creds);
      await refresh();
      setLastResult(`Saved credentials for ${connectorId}.`);
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
        `${connectorId}: ${result.run.summary}. Attached ${attached} criteria link(s). Drift events: ${drift}.`,
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
      const result = await api.runDue(false);
      setLastResult(`Ran ${result.ran_count ?? 0} due connector(s).`);
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    } finally {
      setRunningDue(false);
    }
  };

  const onCreateWebhook = async () => {
    if (!webhookName.trim() || !webhookSource.trim()) {
      setLastResult("Webhook name and source system are required.");
      return;
    }
    try {
      const result = await api.createWebhook(webhookName.trim(), webhookSource.trim());
      setNewWebhookToken(result.webhook_token);
      setWebhookName("");
      setWebhookSource("");
      setLastResult(`Created webhook collector "${result.collector.name}". ${result.usage}`);
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    }
  };

  const onDeleteWebhook = async (collectorId: string) => {
    try {
      await api.deleteWebhook(collectorId);
      setLastResult("Webhook collector deleted.");
      await refresh();
    } catch (err) {
      setLastResult(String(err));
    }
  };

  return (
    <div className="page-stack integrations-page">
      <PageIntro title="Integrations" summary="Connect cloud systems to collect evidence. Results map to SOC 2 criteria via the shared evidence layer." />

      {lastResult && <ActionFeedback message={lastResult} onDismiss={() => setLastResult("")} />}
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
          runningDue={runningDue}
          runDueDisabled={dueCount === 0}
          onRunDue={onRunDue}
        />
      )}

      {!loading && (
      <div className="integrations-sections panel-stack">
        <h3 className="page-section-heading">Connectors</h3>
        <p className="muted integrations-section-lead">
          Use <strong>Try demo</strong> to attach sample evidence without credentials. Evidence maps to CC criteria
          automatically.
        </p>
        <div className="panel-stack">
          {connectors.map((c) => (
            <CollectorCard
              key={c.id}
              connector={c}
              isDue={dueConnectors.includes(c.id)}
              running={running === c.id}
              formValues={forms[c.id] ?? {}}
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
