import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiUrl } from "@shared/apiPrefix";

const ACTION_LABELS: Record<string, string> = {
  reported: "Reported",
  triage: "Triaged",
  investigation: "Investigation Started",
  containment: "Containment",
  root_cause_analysis: "RCA Completed",
  remediation: "Remediation Started",
  closed: "Closed",
  regulator_notified: "Regulator Notified",
  telemetry_snapshot: "Telemetry Captured",
  bulk: "Bulk Operation",
};

export default function IncidentNotifications({ basePath = "/incidents" }: { basePath?: string }) {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(apiUrl("/api/notifications"))
      .then((r) => r.json())
      .then((d) => {
        setNotifications(d.notifications || []);
        setUnread(d.unread || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading notifications...</p>;

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Notifications</h2>
        <p className="muted">
          {notifications.length > 0
            ? `${unread} unread · ${notifications.length} total`
            : "No notifications yet"}
        </p>
      </div>

      {notifications.length === 0 ? (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No notifications yet. Activity from incidents will appear here.</p>
          </div>
        </div>
      ) : (
        <div className="panel">
          <div className="panel-body" style={{ padding: 0 }}>
            {notifications.map((n, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  gap: 12,
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--border)",
                  alignItems: "flex-start",
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: i < unread ? "var(--primary)" : "var(--border)",
                    marginTop: 6,
                    flexShrink: 0,
                  }}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 8 }}>
                    <strong style={{ fontSize: "0.85rem" }}>
                      {ACTION_LABELS[n.action] || n.action}
                    </strong>
                    <span className="muted" style={{ fontSize: "0.75rem", whiteSpace: "nowrap" }}>
                      {n.timestamp?.slice(0, 16).replace("T", " ")}
                    </span>
                  </div>
                  <p style={{ fontSize: "0.8rem", margin: "2px 0 0 0" }}>
                    <Link to={`${basePath}/${n.source_id}`} style={{ textDecoration: "none" }}>
                      {n.source_title}
                    </Link>
                    {n.detail && <span className="muted"> — {n.detail}</span>}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
