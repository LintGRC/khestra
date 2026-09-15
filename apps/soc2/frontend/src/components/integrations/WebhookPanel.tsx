import { useEffect, useState } from "react";
import { WebhookCollectorInfo } from "../../api";

type Props = {
  webhooks: WebhookCollectorInfo[];
  envWebhookToken: boolean;
  webhookName: string;
  webhookSource: string;
  newWebhookToken: string | null;
  onWebhookNameChange: (value: string) => void;
  onWebhookSourceChange: (value: string) => void;
  onCreate: () => void;
  onDelete: (collectorId: string) => void;
};

export default function WebhookPanel({
  webhooks,
  envWebhookToken,
  webhookName,
  webhookSource,
  newWebhookToken,
  onWebhookNameChange,
  onWebhookSourceChange,
  onCreate,
  onDelete,
}: Props) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const apiOrigin = typeof window !== "undefined" ? window.location.origin : "";

  useEffect(() => {
    if (newWebhookToken) setOpen(true);
  }, [newWebhookToken]);

  return (
    <details
      className="panel webhook-panel"
      open={open}
      onToggle={(e) => setOpen(e.currentTarget.open)}
    >
      <summary className="webhook-panel-summary">
        <span>
          <strong>Webhook ingestion</strong>
          <span className="muted webhook-panel-subtitle">Arm&apos;s-length · advanced</span>
        </span>
        <span className="muted">{webhooks.length} collector{webhooks.length === 1 ? "" : "s"}</span>
      </summary>

      <div className="panel-body">
        <p className="muted">
          Push metadata-only evidence from scripts, edge collectors, or partner tools. No CUI in the
          payload — attach summaries and counts only. POST to <code>/api/webhook/external</code> with{" "}
          <code>Authorization: Bearer &lt;token&gt;</code>.
          {envWebhookToken && (
            <>
              {" "}
              A global token is also configured via <code>CMMC_WEBHOOK_TOKEN</code> or <code>WEBHOOK_TOKEN</code>.
            </>
          )}
        </p>

        <div className="collector-fields">
          <label className="collector-field">
            <span>Display name</span>
            <input
              value={webhookName}
              onChange={(e) => onWebhookNameChange(e.target.value)}
              placeholder="CrowdStrike edge scanner"
            />
          </label>
          <label className="collector-field">
            <span>Source system ID</span>
            <input
              value={webhookSource}
              onChange={(e) => onWebhookSourceChange(e.target.value)}
              placeholder="crowdstrike-edge"
            />
          </label>
        </div>
        <div className="collector-actions">
          <button type="button" className="btn btn-primary" onClick={onCreate}>
            Create webhook collector
          </button>
        </div>

        {newWebhookToken && (
          <div className="webhook-token-reveal">
            <p>
              <strong>Bearer token</strong> (copy now):
            </p>
            <code className="webhook-token">{newWebhookToken}</code>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => {
                navigator.clipboard.writeText(newWebhookToken);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
            >
              {copied ? "Copied!" : "Copy token"}
            </button>
            <pre className="webhook-curl">{`curl -X POST '${apiOrigin}/api/webhook/external' \\
  -H 'Authorization: Bearer ${newWebhookToken}' \\
  -H 'Content-Type: application/json' \\
  -d '{"checks":[{"check_id":"endpoint-coverage","check_name":"Endpoint coverage","status":"pass","evidence":"42 of 45 hosts reporting","control_ids":["SI.L2-3.14.2"]}]}'`}</pre>
          </div>
        )}

        {webhooks.length > 0 && (
          <ul className="webhook-list">
            {webhooks.map((w) => (
              <li key={w.id} className="webhook-list-item">
                <div>
                  <strong>{w.name}</strong> ({w.source_system}) — {w.ingest_count} ingest(s)
                  {w.last_ingest_at && <> · last {w.last_ingest_at}</>}
                  {w.token_hint && <> · token {w.token_hint}</>}
                </div>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => onDelete(w.id)}>
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </details>
  );
}
