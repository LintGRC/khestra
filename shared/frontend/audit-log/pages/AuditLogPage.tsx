import { useEffect, useState } from "react";
import { apiUrl, getApiPrefix } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";

const FRAMEWORK_MAP: Record<string, string> = {
  "/api/soc2": "SOC2",
  "/api/ai-governance": "AIGov",
  "/api/cmmc": "CMMC",
};

function detectFramework(): string | undefined {
  return FRAMEWORK_MAP[getApiPrefix()];
}

type AuditEntry = {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  framework_id: string;
  details: Record<string, any>;
  ip_address: string;
  user_agent: string;
};

function formatTimestamp(ts: string): string {
  return ts?.slice(0, 19).replace("T", " ") || "";
}

function renderDetailValue(val: unknown): string {
  if (val === null || val === undefined) return "-";
  if (typeof val === "boolean") return val ? "true" : "false";
  if (Array.isArray(val)) {
    if (val.length === 0) return "[]";
    if (val.every((v) => typeof v === "string")) return val.join(", ");
    return JSON.stringify(val);
  }
  if (typeof val === "object") return JSON.stringify(val);
  return String(val);
}

const HIDDEN_DETAIL_KEYS = new Set([
  "_integrity_hash", "_outcome", "field_diffs", "denied_path",
  "security", "method", "fields",
]);

export default function AuditLogPage() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fw = detectFramework();
    const qs = fw ? `?framework_id=${fw}` : "";
    (async () => {
      const headers = await authHeaders();
      fetch(apiUrl(`/api/audit-log${qs}`), { headers })
      .then((r) => r.json())
      .then((d) => {
        const items: AuditEntry[] = d.entries || [];
        setEntries(items);
        setExpandedIds(new Set(items.filter((e) => e.details?._outcome === "failure").map((e) => e.id)));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
    })();
  }, []);

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const fw = detectFramework();
  const exportUrl = apiUrl(`/api/audit-log/export${fw ? `?framework_id=${fw}` : ""}`);

  if (loading)
    return (
      <div className="page-stack">
        <p className="muted">Loading...</p>
      </div>
    );

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>{fw === "CMMC" ? "Record of Changes" : "Audit Log"}</h2>
        <div className="page-header-links">
          <a href={exportUrl} className="btn btn-sm" download>Export CSV</a>
        </div>
      </div>

      {entries.length === 0 ? (
        <div className="panel">
          <div className="panel-body">
            <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>
              No audit log entries yet. Changes to organization profile, controls, policies, and
              evidence will appear here.
            </p>
          </div>
        </div>
      ) : (
        <div className="panel" style={{ padding: 0 }}>
          <style>{`
            .audit-row-summary:hover {
              background: var(--primary-soft) !important;
            }
          `}</style>
          {entries.map((entry) => {
            const isExpanded = expandedIds.has(entry.id);
            const outcome = entry.details?._outcome || "success";
            const isFailure = outcome === "failure";
            const diffs: Record<string, { old: unknown; new: unknown }> | undefined = entry.details?.field_diffs;
            const deniedPath: string | undefined = entry.details?.denied_path;
            const method: string | undefined = entry.details?.method;
            const security: boolean = entry.details?.security === true;

            return (
              <div key={entry.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                <div
                  onClick={() => toggleExpand(entry.id)}
                  className="audit-row-summary"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "180px 72px 1fr 1fr 36px",
                    gap: "16px",
                    padding: "5px 12px",
                    fontFamily: "ui-monospace, Menlo, monospace",
                    fontSize: "13px",
                    cursor: "pointer",
                    userSelect: "none",
                    alignItems: "center",
                    background: isExpanded ? "var(--primary-soft)" : undefined,
                  }}
                >
                  <span style={{ color: "var(--muted)", whiteSpace: "nowrap" }}>
                    {formatTimestamp(entry.timestamp)}
                  </span>
                  <span style={{ fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {entry.action.toUpperCase()}
                  </span>
                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--text)" }}>
                    {entry.resource_type}{entry.resource_id ? `/${entry.resource_id}` : ""}
                  </span>
                  <span style={{ color: "var(--muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {entry.user_email}
                  </span>
                  <span style={{
                    textAlign: "right",
                    color: isFailure ? "var(--danger)" : "var(--success)",
                    fontWeight: isFailure ? 700 : 400,
                  }}>
                    {isFailure ? "\u2717" : "\u2713"}
                  </span>
                </div>

                {isExpanded && (() => {
                  const details = entry.details || {};
                  const legacyField = details.field;
                  const legacyOld = details.old;
                  const legacyNew = details.new;
                  const hasLegacyDiff = legacyField && legacyOld !== undefined && legacyNew !== undefined;

                  const exclude = new Set(HIDDEN_DETAIL_KEYS);
                  if (diffs) exclude.add("field_diffs");
                  if (deniedPath) exclude.add("denied_path");
                  if (security) exclude.add("security");
                  if (method) exclude.add("method");
                  if (hasLegacyDiff) { exclude.add("field"); exclude.add("old"); exclude.add("new"); }

                  const remaining = Object.entries(details).filter(([k]) => !exclude.has(k));

                  return (
                  <div style={{
                    padding: "6px 12px 6px 28px",
                    fontFamily: "ui-monospace, Menlo, monospace",
                    fontSize: "12px",
                    lineHeight: "1.8",
                    color: "var(--muted)",
                    background: "var(--primary-soft)",
                  }}>
                    {diffs && Object.keys(diffs).map((field) => {
                      const d = diffs[field];
                      return (
                        <div key={field}>
                          \u2514\u2500 {field.replace(/_/g, " ")}: "
                          <span style={{ color: "var(--text)" }}>{renderDetailValue(d.old)}</span>"
                          {" \u2192 "}"
                          <span style={{ color: "var(--text)", fontWeight: 500 }}>{renderDetailValue(d.new)}</span>"
                        </div>
                      );
                    })}

                    {hasLegacyDiff && (
                      <div>
                        \u2514\u2500 {String(legacyField).replace(/_/g, " ")}: "
                        <span style={{ color: "var(--text)" }}>{renderDetailValue(legacyOld)}</span>"
                        {" \u2192 "}"
                        <span style={{ color: "var(--text)", fontWeight: 500 }}>{renderDetailValue(legacyNew)}</span>"
                      </div>
                    )}

                    {deniedPath && (
                      <div style={{ color: "var(--danger)" }}>
                        \u2514\u2500 denied: {(method || "REQUEST").toUpperCase()} {deniedPath}
                      </div>
                    )}

                    {security && (
                      <div>
                        \u2514\u2500 security event
                      </div>
                    )}

                    {remaining.map(([k, v]) => (
                      <div key={k}>
                        \u2514\u2500 {k.replace(/_/g, " ")}: {renderDetailValue(v)}
                      </div>
                    ))}

                    {entry.ip_address && (
                      <div>\u2514\u2500 source: {entry.ip_address}</div>
                    )}
                    {entry.user_agent && (
                      <div style={{ maxWidth: "100%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        \u2514\u2500 user-agent: {entry.user_agent}
                      </div>
                    )}
                  </div>
                  );
                })()}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
