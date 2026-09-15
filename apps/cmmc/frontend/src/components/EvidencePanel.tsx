import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, apiUrl, EvidenceHistorySummary, EvidenceItem } from "../api";
import { authHeaders } from "@shared/accessToken";
import CheckIcon from "./icons/CheckIcon";
import XIcon from "./icons/XIcon";
import { EmptyState } from "./ui/Skeleton";

type Props = {
  controlId: string;
  evidence: EvidenceItem[];
  historySummary?: EvidenceHistorySummary[];
  canEdit: boolean;
  onUpdated: () => void;
  expectedEvidenceTypes?: string[];
};

const EVIDENCE_TYPES = [
  { value: "policy", label: "Policy" },
  { value: "certificate", label: "Certificate" },
  { value: "diagram", label: "Diagram" },
  { value: "scan_report", label: "Vulnerability Scan" },
  { value: "training_record", label: "Training Record" },
  { value: "screenshot", label: "Screenshot" },
  { value: "config_export", label: "Configuration Export" },
  { value: "audit_report", label: "Audit Report" },
  { value: "other", label: "Other" },
];

export default function EvidencePanel({
  controlId,
  evidence,
  historySummary = [],
  canEdit,
  onUpdated,
  expectedEvidenceTypes = [],
}: Props) {
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [integrityStatus, setIntegrityStatus] = useState<Record<string, boolean>>({});
  const [removing, setRemoving] = useState<string | null>(null);
  const [evidenceType, setEvidenceType] = useState("other");
  const [displayTitle, setDisplayTitle] = useState("");
  const [evidenceVersion, setEvidenceVersion] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const [viewingContent, setViewingContent] = useState<{ filename: string; data: string } | null>(null);
  const [loadedHistory, setLoadedHistory] = useState<EvidenceHistorySummary[] | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const evidenceFingerprint = useMemo(
    () => evidence.map((e) => `${e.filename}:${e.sha256}`).join("|"),
    [evidence],
  );

  useEffect(() => {
    let cancelled = false;
    const items = evidence.filter((ev) => ev.sha256);
    if (!items.length) {
      setIntegrityStatus({});
      return;
    }

    Promise.all(
      items.map(async (ev) => {
        try {
          if (ev.is_hub_evidence && ev.hub_id) {
            const headers = await authHeaders();
            const res = await fetch(apiUrl(`/api/evidence-hub/${encodeURIComponent(ev.hub_id)}/verify`), { headers });
            if (!res.ok) return { filename: ev.filename, ok: false };
            const data = await res.json();
            return { filename: ev.filename, ok: data.verified };
          }
          const r = await api.verifyEvidence(controlId, ev.filename);
          return { filename: ev.filename, ok: r.verified };
        } catch {
          return { filename: ev.filename, ok: false };
        }
      }),
    ).then((results) => {
      if (cancelled) return;
      setIntegrityStatus(Object.fromEntries(results.map((r) => [r.filename, r.ok])));
    });

    return () => {
      cancelled = true;
    };
  }, [controlId, evidenceFingerprint]);

  useEffect(() => {
    setLoadedHistory(null);
  }, [controlId, evidenceFingerprint]);

  const downloadUrl = (ev: EvidenceItem) => {
    if (ev.is_hub_evidence && ev.hub_id) {
      return apiUrl(`/api/evidence-hub/${encodeURIComponent(ev.hub_id)}/download`);
    }
    return apiUrl(`/api/controls/${encodeURIComponent(controlId)}/evidence/${encodeURIComponent(ev.filename)}`);
  };

  const onUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("framework_id", "CMMC");
      fd.append("control_id", controlId);
      fd.append("name", file.name);
      fd.append("evidence_type", evidenceType);
      fd.append("display_title", displayTitle || file.name);
      fd.append("evidence_version", evidenceVersion);
      const headers = await authHeaders();
      const res = await fetch(apiUrl("/api/evidence-hub/upload-and-map"), { method: "POST", body: fd, headers });
      if (!res.ok) throw new Error(await res.text());
      setUploadMsg(`Attached "${displayTitle || file.name}".`);
      setDisplayTitle("");
      setEvidenceVersion("");
      setEvidenceType("other");
      if (fileRef.current) fileRef.current.value = "";
      onUpdated();
    } catch (err) {
      setUploadMsg(String(err));
    } finally {
      setUploading(false);
    }
  };

  const onRemove = async (ev: EvidenceItem) => {
    if (!window.confirm(`Remove "${ev.filename}" from this control? This cannot be undone.`)) return;
    setRemoving(ev.hub_id || ev.filename);
    try {
      if (ev.is_hub_evidence && ev.hub_id) {
        const headers = await authHeaders();
        const res = await fetch(apiUrl(`/api/evidence-hub/${encodeURIComponent(ev.hub_id)}/map/CMMC/${encodeURIComponent(controlId)}`), {
          method: "DELETE",
          headers,
        });
        if (!res.ok) throw new Error(await res.text());
      } else {
        await api.deleteEvidence(controlId, ev.filename);
      }
      setIntegrityStatus((s) => {
        const next = { ...s };
        delete next[ev.filename];
        return next;
      });
      onUpdated();
    } catch (err) {
      setUploadMsg(String(err));
    } finally {
      setRemoving(null);
    }
  };

  const evidenceKey = (ev: EvidenceItem) => ev.hub_id || `${ev.filename}:${ev.sha256}`;

  /** Primary list = latest only (API already returns view=latest for hub). */
  const currentEvidence = useMemo(() => {
    const parseDate = (d: string) => {
      const t = Date.parse(d);
      return Number.isNaN(t) ? 0 : t;
    };
    return [...evidence].sort((a, b) => parseDate(b.upload_date) - parseDate(a.upload_date));
  }, [evidence]);

  const periodTrailCount = useMemo(
    () => historySummary.reduce((n, s) => n + Math.max(0, (s.count || 0) - 1), 0),
    [historySummary],
  );

  const isFresh = (uploadDate: string) => {
    const t = Date.parse(uploadDate);
    if (Number.isNaN(t)) return true;
    return Date.now() - t < 7 * 24 * 60 * 60 * 1000;
  };

  const provenanceLine = (ev: EvidenceItem) => {
    const p = ev.provenance;
    if (!p) {
      if (ev.period_covered) return `period ${ev.period_covered}`;
      return null;
    }
    const collector = (ev.filename || "").startsWith("collector_");
    if (!collector && p.method === "Manual upload") {
      const period = p.period_covered || ev.period_covered || ev.upload_date;
      return period ? `Manual · period ${period}` : null;
    }
    if (!collector) return null;
    const parts = [
      p.connector_name || p.connector_id,
      p.check_name || p.check_id,
      p.period_covered || ev.period_covered
        ? `period ${p.period_covered || ev.period_covered}`
        : p.collected_at
          ? `collected ${p.collected_at}`
          : "",
      p.status ? String(p.status) : "",
      p.review_status && p.review_status !== "approved" ? `review: ${p.review_status}` : "",
    ].filter(Boolean);
    return parts.length ? parts.join(" · ") : null;
  };

  const renderRow = (ev: EvidenceItem) => {
    const integrity = ev.sha256 ? integrityStatus[ev.filename] : undefined;
    const collector = (ev.filename || "").startsWith("collector_");
    const prov = provenanceLine(ev);
    return (
      <li key={evidenceKey(ev)} className="evidence-row">
        <div className="evidence-meta">
          <strong>{ev.display_title || ev.filename}</strong>
          {collector && (
            <span className="badge badge-muted" style={{ fontSize: "0.65rem", marginLeft: 6 }}>Latest</span>
          )}
          {collector && !isFresh(ev.upload_date) && (
            <span className="badge badge-warn" style={{ fontSize: "0.65rem", marginLeft: 4 }}>Stale</span>
          )}
          {ev.evidence_type && ev.evidence_type !== "other" && (
            <span className="muted" style={{ fontSize: 10, marginLeft: 4 }}>({ev.evidence_type})</span>
          )}
          {prov && <span className="evidence-provenance muted">{prov}</span>}
          <span className="muted">{ev.upload_date}</span>
          {ev.sha256 && (
            <span className="evidence-hash-row">
              <code className="evidence-hash" title={ev.sha256}>
                SHA-256: {ev.sha256.slice(0, 16)}…
              </code>
              {integrity === true && (
                <span
                  className="evidence-integrity evidence-integrity--ok"
                  title="Stored file matches recorded SHA-256"
                  aria-label="Integrity OK"
                >
                  <CheckIcon />
                </span>
              )}
            </span>
          )}
          {integrity === false && (
            <span className="evidence-integrity evidence-integrity--fail" role="alert">
              Integrity failed — file may be corrupted or tampered
            </span>
          )}
        </div>
        <div className="evidence-actions">
          <a className="btn btn-secondary btn-sm" href={downloadUrl(ev)} download>
            Download
          </a>
          {ev.is_hub_evidence && ev.hub_id && ev.filename?.endsWith(".json") && (
            <button type="button" className="btn btn-sm btn-ghost" onClick={async () => {
              try {
                const headers = await authHeaders();
                const r = await fetch(apiUrl(`/api/evidence-hub/${encodeURIComponent(ev.hub_id!)}/content`), { headers });
                if (!r.ok) return;
                setViewingContent({ filename: ev.filename, data: await r.text() });
              } catch { /* ignore */ }
            }}>View</button>
          )}
          {canEdit && (
            <button
              type="button"
              className="icon-btn icon-btn--danger evidence-remove-btn"
              disabled={removing === (ev.hub_id || ev.filename)}
              aria-label={
                removing === (ev.hub_id || ev.filename) ? "Removing evidence" : `Remove ${ev.filename}`
              }
              title="Remove"
              onClick={() => onRemove(ev)}
            >
              <XIcon />
            </button>
          )}
        </div>
      </li>
    );
  };

  const trail = loadedHistory || historySummary;
  const priorPeriodTotal = trail.reduce((n, s) => n + Math.max(0, (s.count || 0) - 1), 0);

  return (
    <div className="evidence-panel">
      <label className="evidence-panel-label">
        Evidence ({currentEvidence.length}
        {periodTrailCount > 0 ? ` current · ${periodTrailCount} prior periods` : ""})
      </label>
      {expectedEvidenceTypes.length > 0 && (
        <div className="expected-evidence-box">
          <p className="muted" style={{ margin: "0 0 4px", fontWeight: 600 }}>Evidence guidance:</p>
          {[...new Set(expectedEvidenceTypes)].map((et) => (
            <div key={et} style={{ padding: "2px 0" }}>
              <span className="muted">{et}</span>
            </div>
          ))}
        </div>
      )}
      {canEdit && (
        <>
          <div className="evidence-upload" style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 8 }}>
            <input ref={fileRef} type="file" disabled={uploading} accept=".pdf,.png,.jpg,.jpeg,.json,.conf,.txt,.csv" />
            <div className="evidence-upload-row">
              <select
                value={evidenceType}
                onChange={(e) => setEvidenceType(e.target.value)}
              >
                {EVIDENCE_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Display title (defaults to filename)"
                value={displayTitle}
                onChange={(e) => setDisplayTitle(e.target.value)}
              />
              <input
                type="text"
                placeholder="Version"
                value={evidenceVersion}
                onChange={(e) => setEvidenceVersion(e.target.value)}
              />
              <button type="button" className="btn btn-sm btn-primary" disabled={uploading} onClick={onUpload}>
                {uploading ? "Uploading..." : "Upload"}
              </button>
            </div>
          </div>
          {uploadMsg && <p className="muted">{uploadMsg}</p>}
        </>
      )}
      {currentEvidence.length > 0 ? (
        <ul className="evidence-list">
          {currentEvidence.map((ev) => renderRow(ev))}
        </ul>
      ) : (
        <EmptyState
          compact
          title="No evidence attached"
          description={
            canEdit
              ? "Upload files above, or connect an integration to collect evidence automatically."
              : "No files have been linked to this control yet."
          }
        >
          {canEdit && (
            <Link className="btn btn-secondary btn-sm" to="/integrations">
              Open integrations
            </Link>
          )}
        </EmptyState>
      )}

      {(periodTrailCount > 0 || (historySummary?.length ?? 0) > 0) && (
        <details
          className="evidence-history"
          onToggle={(e) => {
            const open = (e.currentTarget as HTMLDetailsElement).open;
            if (open && !loadedHistory && !historyLoading) {
              setHistoryLoading(true);
              void (async () => {
                try {
                  const headers = await authHeaders();
                  const res = await fetch(apiUrl(`/api/controls/${encodeURIComponent(controlId)}/evidence-history`), { headers });
                  if (!res.ok) throw new Error(await res.text());
                  const data = await res.json();
                  setLoadedHistory(data.summary || historySummary);
                } catch {
                  setLoadedHistory(historySummary);
                } finally {
                  setHistoryLoading(false);
                }
              })();
            }
          }}
        >
          <summary className="evidence-history-summary">
            Collection periods ({priorPeriodTotal || periodTrailCount} prior day
            {(priorPeriodTotal || periodTrailCount) === 1 ? "" : "s"})
          </summary>
          <p className="muted" style={{ fontSize: "0.8rem", margin: "0.35rem 0 0.5rem" }}>
            One artifact is kept per collection day. Same-day re-runs keep the latest; older days stay for the audit window.
          </p>
          {historyLoading && <p className="muted">Loading period history…</p>}
          {!historyLoading && trail.map((group) => (
            <div key={group.filename} className="evidence-period-group">
              <strong style={{ fontSize: "0.8rem" }}>{group.periods?.[0]?.display_title || group.filename}</strong>
              <span className="muted" style={{ fontSize: "0.75rem", marginLeft: 8 }}>
                {group.oldest === group.newest ? group.newest : `${group.oldest} → ${group.newest}`}
                {" · "}{group.count} period{group.count === 1 ? "" : "s"}
              </span>
              <ul className="evidence-list">
                {(group.periods || []).slice(1).map((p) => (
                  <li key={`${group.filename}:${p.period_covered}:${p.hub_id}`} className="evidence-row evidence-row--history">
                    <div className="evidence-meta">
                      <span className="evidence-provenance muted">
                        period {p.period_covered}{p.status ? ` · ${p.status}` : ""}
                      </span>
                      {p.upload_date && <span className="muted">{p.upload_date}</span>}
                      {p.sha256 && (
                        <code className="evidence-hash" title={p.sha256}>SHA-256: {p.sha256.slice(0, 16)}…</code>
                      )}
                    </div>
                    <div className="evidence-actions">
                      {p.hub_id && (
                        <a className="btn btn-secondary btn-sm" href={apiUrl(`/api/evidence-hub/${encodeURIComponent(p.hub_id)}/download`)} download>
                          Download
                        </a>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </details>
      )}

      {viewingContent && (
        <div style={{ position: "fixed", inset: 0, zIndex: 1000, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }} onClick={() => setViewingContent(null)}>
          <div style={{ background: "var(--surface)", borderRadius: "var(--radius)", width: "80vw", maxWidth: 800, maxHeight: "80vh", display: "flex", flexDirection: "column", boxShadow: "0 4px 24px rgba(0,0,0,0.3)" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", borderBottom: "1px solid var(--border)" }}>
              <strong style={{ fontSize: "0.85rem", fontFamily: "monospace" }}>{viewingContent.filename}</strong>
              <button type="button" className="btn btn-sm btn-ghost" onClick={() => setViewingContent(null)}>×</button>
            </div>
            <pre style={{ margin: 0, padding: 14, overflow: "auto", fontSize: "0.75rem", lineHeight: 1.5, whiteSpace: "pre-wrap", wordBreak: "break-all", fontFamily: "monospace", flex: 1 }}>
              {(() => { try { return JSON.stringify(JSON.parse(viewingContent.data), null, 2); } catch { return viewingContent.data; } })()}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
