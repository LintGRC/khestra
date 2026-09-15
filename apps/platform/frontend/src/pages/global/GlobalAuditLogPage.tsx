import { useEffect, useMemo, useState } from "react";
import { FilterBar, FilterSearch, FilterSelect, FilterCheckbox, FilterCount } from "@shared/filter-bar";
import { authFetchJson } from "./authFetch";

const CORE_API = "/api/core";

const FRAMEWORKS = [
  { id: "cmmc", label: "CMMC", color: "#059669", queryValue: "CMMC" },
  { id: "soc2", label: "SOC 2", color: "#2563eb", queryValue: "SOC2" },
  { id: "aigov", label: "AI Governance", color: "#7c3aed", queryValue: "AIGov" },
  { id: "other", label: "Other", color: "#6b7280", queryValue: "" },
];

const FW_BY_QUERY: Record<string, (typeof FRAMEWORKS)[number]> = {};
FRAMEWORKS.forEach((fw) => { if (fw.queryValue) FW_BY_QUERY[fw.queryValue] = fw; });

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

type EnrichedEntry = AuditEntry & {
  _fwId: string;
  _fwLabel: string;
  _fwColor: string;
  _compoundId: string;
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

export default function GlobalAuditLogPage() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [filterFw, setFilterFw] = useState<string | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [failuresOnly, setFailuresOnly] = useState(false);

  useEffect(() => {
    authFetchJson<{ entries?: AuditEntry[] }>(`${CORE_API}/audit-log`)
      .then((d) => {
        const list = d.entries || [];
        setEntries(list);
        const failedIds = list
          .filter((e) => e.details?._outcome === "failure")
          .map((e) => `${e.framework_id}-${e.id}`);
        setExpandedIds(new Set(failedIds));
      })
      .catch(() => setEntries([]))
      .finally(() => setLoading(false));
  }, []);

  const toggleExpand = (compoundId: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(compoundId)) next.delete(compoundId);
      else next.add(compoundId);
      return next;
    });
  };

  const allEntries: EnrichedEntry[] = useMemo(() => {
    let list: EnrichedEntry[] = entries.map((e) => {
      const fw = FW_BY_QUERY[e.framework_id] || FRAMEWORKS[FRAMEWORKS.length - 1];
      return {
        ...e,
        _fwId: fw.id,
        _fwLabel: fw.label,
        _fwColor: fw.color,
        _compoundId: `${fw.id}-${e.id}`,
      };
    });

    if (filterFw !== "all") {
      list = list.filter((e) => e._fwId === filterFw);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (e) =>
          e.user_email?.toLowerCase().includes(q) ||
          e.action?.toLowerCase().includes(q) ||
          e.resource_type?.toLowerCase().includes(q) ||
          e.resource_id?.toLowerCase().includes(q)
      );
    }

    if (failuresOnly) {
      list = list.filter((e) => e.details?._outcome === "failure");
    }

    return list
      .sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || ""))
      .slice(0, 50);
  }, [entries, filterFw, searchQuery, failuresOnly]);

  if (loading) {
    return (
      <div className="page-stack">
        <p className="muted">Loading...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-intro">
        <div className="page-intro-head">
          <div>
            <h1 className="page-intro-title">Audit Log</h1>
          </div>
        </div>
      </div>
      <FilterBar>
        <FilterSearch value={searchQuery} onChange={setSearchQuery} placeholder="Search by user, action, resource..." />
        <FilterSelect value={filterFw} onChange={setFilterFw} options={FRAMEWORKS.map(fw => ({ value: fw.id, label: fw.label }))} placeholder="All frameworks" />
        <FilterCheckbox label="Failures only" checked={failuresOnly} onChange={setFailuresOnly} />
        <FilterCount value={allEntries.length} label="entry" />
      </FilterBar>
      <div className="panel" style={{ padding: 0 }}>
          {allEntries.length === 0 ? (
            <p className="muted" style={{ padding: "1rem", margin: 0 }}>No activity found.</p>
          ) : (
            <>
              <style>{`
                .audit-row-summary:hover {
                  background: var(--primary-soft) !important;
                }
              `}</style>
              {allEntries.map((entry) => {
                const isExpanded = expandedIds.has(entry._compoundId);
                const outcome = entry.details?._outcome || "success";
                const isFailure = outcome === "failure";
                const diffs: Record<string, { old: unknown; new: unknown }> | undefined = entry.details?.field_diffs;
                const deniedPath: string | undefined = entry.details?.denied_path;
                const method: string | undefined = entry.details?.method;
                const security: boolean = entry.details?.security === true;

                return (
                  <div key={entry._compoundId} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <div
                      onClick={() => toggleExpand(entry._compoundId)}
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
                        <span style={{ color: entry._fwColor, fontWeight: 600 }}>{entry._fwLabel}</span>
                        {`: ${entry.resource_type}${entry.resource_id ? `/${entry.resource_id}` : ""}`}
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
            </>
            )}
      </div>
    </div>
  );
}
