import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { authHeaders } from "@shared/accessToken";
import { frameworkDetailBase } from "@shared/apiPrefix";
import type { FrameworkId } from "../../framework/frameworks";

const PREFIXES: Record<string, string> = {
  cmmc: "/api/cmmc",
  soc2: "/api/soc2",
  aigovernance: "/api/ai-governance",
  iso27001: "/api/iso27001",
  cis: "/api/core",
};

// Neutral Core namespace for the collector executor (re-scan).
const CORE_API = "/api/core";

const FRAMEWORK_LABELS: Record<string, string> = {
  cmmc: "CMMC",
  soc2: "SOC 2",
  aigovernance: "AI Gov",
  iso27001: "ISO 27001",
  cis: "CIS",
};

type QueueCheck = {
  check_id: string;
  check_name: string;
  status: string;
  framework: string;
  capability: string;
  remediation?: string;
  console_url?: string;
  manual?: boolean;
  controls: { control_id: string }[];
};

type PostureControl = { control_id: string; name: string; attested_status: string | null };
type PostureCheck = {
  check_id: string;
  check_name: string;
  status: string;
  remediation?: string;
  console_url?: string;
  controls: PostureControl[];
};
type CapabilityRow = { capability: string; checks: PostureCheck[] };
type PostureResponse = { framework: string; capabilities: CapabilityRow[]; source?: string };

// Map check-id prefix → connector id used by the run endpoint.
const CONNECTOR_BY_PREFIX: Record<string, string> = {
  aws: "aws", github: "github", entra: "entra", intune: "intune", okta: "okta",
  google: "google_workspace", crowdstrike: "crowdstrike", duo: "duo", jamf: "jamf",
  jira: "jira", jumpcloud: "jumpcloud", kandji: "kandji", linear: "linear",
  sentinel: "sentinel", splunk: "splunk", tenable: "tenable", cloudflare: "cloudflare",
  bamboo: "bamboo",
};

function connectorFor(checkId: string): string {
  const prefix = checkId.split("-")[0];
  return CONNECTOR_BY_PREFIX[prefix] ?? prefix;
}

function statusTone(status: string): string {
  if (status === "fail") return "badge-danger";
  if (status === "warn") return "badge-warning";
  if (status === "error") return "badge-danger";
  return "badge-muted";
}

export default function RemediationQueuePage() {
  const [postures, setPostures] = useState<Record<string, PostureResponse | null>>({});
  const [loading, setLoading] = useState(true);
  const [filterFw, setFilterFw] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("collected");
  const [rescanning, setRescanning] = useState<string | null>(null);

  const load = () => {
    authHeaders().then((headers) => {
      Promise.all(
        (Object.keys(PREFIXES) as (FrameworkId | "cis")[]).map(async (fw) => {
          let d = await fetch(`${PREFIXES[fw]}/collectors/posture?framework=${fw}`, { headers })
            .then((r) => (r.ok ? r.json() : null))
            .catch(() => null);
          // Free tier: fall back to posture computed from approved manual evidence.
          if (!d) {
            d = await fetch(`/api/posture?framework=${fw}`, { headers })
              .then((r) => (r.ok ? r.json() : null))
              .catch(() => null);
          }
          return { fw, d };
        }),
      ).then((results) => {
        const map: Record<string, PostureResponse | null> = {};
        results.forEach(({ fw, d }) => (map[fw] = d));
        setPostures(map);
        setLoading(false);
      });
    });
  };

  useEffect(() => {
    load();
  }, []);

  const rows: QueueCheck[] = useMemo(() => {
    const out: QueueCheck[] = [];
    for (const fw of Object.keys(PREFIXES)) {
      const resp = postures[fw];
      if (!resp) continue;
      for (const cap of resp.capabilities) {
        for (const check of cap.checks) {
          const collected = check.status === "fail" || check.status === "warn" || check.status === "error";
          if (filterStatus === "collected" && !collected) continue;
          if (filterStatus === "all" && check.status === "pass") continue;
          out.push({
            ...check,
            framework: fw,
            capability: cap.capability,
            manual: resp.source === "manual",
            controls: check.controls.map((c) => ({ control_id: c.control_id })),
          });
        }
      }
    }
    return out.filter(
      (r) =>
        (filterFw === "all" || r.framework === filterFw) &&
        (filterStatus !== "collected" || r.status !== "uncollected"),
    );
  }, [postures, filterFw, filterStatus]);

  const connectors = useMemo(() => [...new Set(rows.map((r) => connectorFor(r.check_id)))].sort(), [rows]);

  const rescan = async (checkId: string) => {
    const connector = connectorFor(checkId);
    setRescanning(checkId);
    try {
      await authHeaders().then((headers) =>
        fetch(`${CORE_API}/collectors/${connector}/run`, {
          method: "POST",
          headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify({ use_fixture: true, attach: true }),
        }),
      );
      setTimeout(load, 1500);
    } finally {
      setRescanning(null);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading remediation queue…</div>;
  }

  const failCount = rows.filter((r) => r.status === "fail").length;

  return (
    <div>
      <div className="page-intro">
        <h1 className="page-intro-title">Remediation Queue</h1>
        <p className="page-intro-summary">
          Every collected check that needs attention, with the exact steps to fix it. Run a
          connector again to re-verify after applying a fix.
        </p>
        <div className="page-intro-actions" style={{ marginTop: "0.75rem" }}>
          <Link to="/posture" className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            Unified Posture
          </Link>
          <Link to="/collectors" className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            Collectors
          </Link>
          <Link to={`${frameworkDetailBase("evidence")}/evidence`} className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            Evidence Hub
          </Link>
        </div>
      </div>

      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">Open issues</div>
          <div className="stat-value">{rows.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Failing</div>
          <div className="stat-value">{failCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Connectors</div>
          <div className="stat-value">{connectors.length}</div>
        </div>
      </div>

      <div className="filter-bar" style={{ margin: "0.75rem 0" }}>
        <select value={filterFw} onChange={(e) => setFilterFw(e.target.value)}>
          <option value="all">All frameworks</option>
          {(Object.keys(PREFIXES) as (FrameworkId | "cis")[]).map((fw) => (
            <option key={fw} value={fw}>
              {FRAMEWORK_LABELS[fw] ?? fw}
            </option>
          ))}
        </select>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="collected">Collected (fail/warn/error)</option>
          <option value="all">All non-passing (incl. uncollected)</option>
        </select>
      </div>

      {rows.length === 0 ? (
        <div className="panel">
          <div className="panel-body">
            <p className="muted">Nothing needs attention — run a collector to populate this list.</p>
          </div>
        </div>
      ) : (
        <div className="panel-stack">
          {rows.map((r) => (
            <div className="panel" key={`${r.framework}-${r.check_id}`}>
              <div className="panel-body" style={{ padding: "0.6rem 0.8rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                  <span className={`badge ${statusTone(r.status)}`}>{r.status}</span>
                  <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>{r.check_name}</span>
                  <span className="badge badge-muted">{connectorFor(r.check_id)}</span>
                  <span className="badge badge-muted">{FRAMEWORK_LABELS[r.framework] ?? r.framework}</span>
                  {r.controls.length > 0 && (
                    <span className="muted" style={{ fontSize: "0.72rem" }}>
                      {r.controls.map((c) => c.control_id).join(" · ")}
                    </span>
                  )}
                  <div style={{ marginLeft: "auto", display: "flex", gap: "0.35rem" }}>
                    {r.console_url && (
                      <a
                        href={r.console_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-ghost btn-xs"
                        style={{ fontSize: 11, textDecoration: "none" }}
                      >
                        View in console ↗
                      </a>
                    )}
                    {!r.manual && (
                      <button
                        className="btn btn-outline btn-xs"
                        disabled={rescanning === r.check_id}
                        onClick={() => rescan(r.check_id)}
                      >
                        {rescanning === r.check_id ? "Re-running…" : "Re-scan"}
                      </button>
                    )}
                  </div>
                </div>
                {r.remediation && (
                  <div
                    style={{
                      fontSize: "0.78rem",
                      color: "var(--muted)",
                      marginTop: "0.4rem",
                      lineHeight: 1.45,
                      borderTop: "1px dashed var(--border)",
                      paddingTop: "0.4rem",
                    }}
                  >
                    <strong>How to fix:</strong> {r.remediation}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
