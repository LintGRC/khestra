import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authFetchJson } from "./authFetch";
import { frameworkDetailBase } from "@shared/apiPrefix";

const CORE_API = "/api/core";

// Auditor ZIP buttons: framework filter ids are framework-scoped, but the
// export itself is served by the Core service (shared evidence DB).
const ZIP_FRAMEWORKS = [
  { id: "CMMC", label: "CMMC" },
  { id: "SOC2", label: "SOC 2" },
  { id: "AIGov", label: "AI Governance" },
  { id: "ISO27001", label: "ISO 27001" },
];

type EvidenceItem = { id: string; name: string; description?: string; review_status: string; uploaded_at: string; file_size: number; mime_type?: string };

async function downloadAuditorPackage(frameworkId: string) {
  try {
    const { authHeaders } = await import("@shared/accessToken");
    const headers = await authHeaders();
    const r = await fetch(`${CORE_API}/evidence-hub/export?framework_id=${frameworkId}`, { headers });
    if (!r.ok) throw new Error(`export failed: ${r.status}`);
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `khestra-${frameworkId.toLowerCase()}-audit-package.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch {
    // Fall back to a plain navigation download.
    window.open(`${CORE_API}/evidence-hub/export?framework_id=${frameworkId}`, "_blank");
  }
}

const reviewColors: Record<string, string> = {
  pending: "var(--warning)", approved: "var(--success)", rejected: "var(--danger)",
};

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function GlobalEvidencePage() {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    Promise.all([
      authFetchJson<{ evidence?: EvidenceItem[] }>(`${CORE_API}/evidence-hub`)
        .then((d) => d.evidence || [])
        .catch(() => [] as EvidenceItem[]),
      authFetchJson(`${CORE_API}/evidence-hub/stats`).catch(() => ({})),
    ]).then(([ev, st]) => {
      setEvidence(ev);
      setStats(st);
    });
  }, []);

  return (
    <div>
      <div className="page-intro">
        <h1 className="page-intro-title">Evidence Hub</h1>
        <div className="page-intro-actions">
          {ZIP_FRAMEWORKS.map((fw) => (
            <button
              key={fw.id}
              className="btn btn-outline btn-xs"
              onClick={() => downloadAuditorPackage(fw.id)}
              title="Download the auditor-ready evidence package (ZIP with summary PDF, evidence.json, remediation scripts)"
            >
              Auditor ZIP — {fw.label}
            </button>
          ))}
        </div>
      </div>
      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">Total evidence</div>
          <div className="stat-value">{stats?.total_evidence ?? evidence.length}</div>
          <div className="muted" style={{ fontSize: "0.75rem", marginTop: "0.15rem" }}>
            {stats?.total_mappings ?? "—"} mappings · {stats?.total_file_size ? fmtSize(stats.total_file_size) : "—"}
          </div>
        </div>
      </div>
      <div className="panel-stack">
        <div className="panel">
          <div className="panel-header">
            <strong>All evidence</strong>
            <div className="panel-header-meta">
              <span className="muted">{evidence.length} files</span>
              <Link to={`${frameworkDetailBase("evidence")}/evidence`} className="btn btn-primary btn-xs" style={{ fontSize: 11, textDecoration: "none" }}>Browse</Link>
            </div>
          </div>
          <div>
            {evidence.length === 0 ? (
              <p className="muted" style={{ padding: "1rem", margin: 0 }}>No evidence files.</p>
            ) : (
              evidence.slice(0, 15).map((e) => (
                <Link
                  key={e.id}
                  to={`${frameworkDetailBase("evidence")}/evidence`}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "0.75rem 1rem", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", color: "inherit", fontSize: "0.875rem" }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, marginBottom: 2 }}>{e.name}</div>
                    <div className="muted" style={{ fontSize: "0.75rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {e.description || "No description"}
                      {e.mime_type ? ` · ${e.mime_type}` : ""}
                      {e.uploaded_at ? ` · ${e.uploaded_at.slice(0, 10)}` : ""}
                    </div>
                  </div>
                  <span className="muted" style={{ fontSize: "0.75rem", flexShrink: 0 }}>{e.file_size ? fmtSize(e.file_size) : "—"}</span>
                  <span className="badge" style={{ borderColor: reviewColors[e.review_status] || "var(--muted)", color: reviewColors[e.review_status] || "var(--muted)", fontWeight: 600, fontSize: 10, flexShrink: 0 }}>
                    {e.review_status || "pending"}
                  </span>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
