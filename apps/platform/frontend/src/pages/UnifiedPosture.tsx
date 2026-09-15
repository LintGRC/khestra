import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authHeaders } from "@shared/accessToken";
import type { FrameworkId } from "../framework/frameworks";

type PostureFrameworkId = FrameworkId | "cis";

type PostureControl = {
  control_id: string;
  name: string;
  attested_status: string | null;
};

type PostureCheck = {
  check_id: string;
  check_name: string;
  status: string;
  last_run_at: string | null;
  remediation?: string;
  console_url?: string;
  controls: PostureControl[];
};

type CapabilityRow = {
  capability: string;
  check_count: number;
  collector_badge: string;
  attested_count: number;
  checks: PostureCheck[];
};

type PostureResponse = {
  framework: string;
  generated_at: string;
  capabilities: CapabilityRow[];
  source?: string;
};

const PREFIXES: Record<string, string> = {
  cmmc: "/api/cmmc",
  soc2: "/api/soc2",
  aigovernance: "/api/ai-governance",
  iso27001: "/api/iso27001",
  cis: "/api/core",
};

const FRAMEWORK_LABELS: Record<string, string> = {
  cmmc: "CMMC",
  soc2: "SOC 2",
  aigovernance: "AI Gov",
  iso27001: "ISO 27001",
  cis: "CIS",
};

const BADGE_TONES: Record<string, string> = {
  pass: "badge badge-success",
  partial: "badge badge-warning",
  warn: "badge badge-warning",
  fail: "badge badge-danger",
  error: "badge badge-danger",
  uncollected: "badge badge-muted",
};

function toneFor(status: string | null): string {
  return BADGE_TONES[status ?? "uncollected"] ?? "badge";
}

function statusLabel(status: string | null): string {
  const map: Record<string, string> = {
    pass: "Pass",
    partial: "Partial",
    warn: "Review",
    fail: "Fail",
    error: "Error",
    uncollected: "No evidence",
  };
  return map[status ?? "uncollected"] ?? status ?? "";
}

export default function UnifiedPosturePage() {
  const [postures, setPostures] = useState<Record<string, PostureResponse | null>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const headersThen = (url: string) =>
      authHeaders().then((headers) => fetch(url, { headers }).then((r) => (r.ok ? r.json() : null)));

    Promise.all(
      (Object.keys(PREFIXES) as PostureFrameworkId[]).map(async (fw) => {
        let data = await headersThen(`${PREFIXES[fw]}/collectors/posture?framework=${fw}`).catch(() => null);
        // Free tier: fall back to posture computed from approved manual evidence.
        if (!data) {
          data = await headersThen(`/api/posture?framework=${fw}`).catch(() => null);
        }
        return [fw, data as PostureResponse | null] as const;
      }),
    ).then((entries) => {
      const merged: Record<string, PostureResponse | null> = {};
      for (const [fw, data] of entries) merged[fw] = data;
      setPostures(merged);
      setLoading(false);
    });
  }, []);

  const available = (Object.keys(postures) as PostureFrameworkId[]).filter(
    (fw) => postures[fw] != null,
  );
  const rows = aggregateCapabilities(available, postures);

  if (loading) {
    return <div className="panel"><div className="panel-body">Loading unified control posture…</div></div>;
  }

  const fullyGreen = rows.filter((r) => r.best === "pass").length;
  const totalChecks = available.reduce(
    (sum, fw) => sum + (postures[fw]?.capabilities ?? []).reduce((s, c) => s + c.check_count, 0),
    0,
  );
  const manualOnly =
    available.length > 0 && available.every((fw) => postures[fw]?.source === "manual");

  return (
    <div className="page">
      <div className="page-header">
        <h1>Unified Control Posture</h1>
        <p>
          One shared evidence collection, applied across every framework. Each capability row
          shows which controls it satisfies and how the platform's collector checks are doing.
        </p>
        {manualOnly && (
          <p className="muted" style={{ marginTop: "0.25rem", fontSize: "0.82rem" }}>
            Manually assessed — computed from approved evidence in the Evidence Hub. Continuous
            monitoring requires the collectors edition.
          </p>
        )}
        <div className="page-intro-actions" style={{ marginTop: "0.75rem" }}>
          <Link to="/remediation" className="btn btn-primary btn-xs" style={{ textDecoration: "none" }}>
            Remediation Queue
          </Link>
          <Link to="/collectors" className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            Collectors
          </Link>
          <Link to="/cmmc/export" className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            OSCAL POA&amp;M Export
          </Link>
        </div>
      </div>

      <div className="stats">
        <div className="stat-card">
          <div className="stat-value">{fullyGreen}</div>
          <div className="stat-label">Capabilities fully passing</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{rows.length}</div>
          <div className="stat-label">Capabilities monitored</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totalChecks}</div>
          <div className="stat-label">Collector checks applied</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{available.length}</div>
          <div className="stat-label">Frameworks connected</div>
        </div>
      </div>

      {rows.length === 0 && (
        <div className="banner">
          No collector data available yet. Run a connector from any framework's Integrations
          page to populate the unified posture view.
        </div>
      )}

      {rows.map((row) => (
        <div key={row.capability} className="panel posture-row">
          <div className="panel-header">
            <span className="panel-title">{row.capability}</span>
            <span className={toneFor(row.best)}>{statusLabel(row.best)}</span>
          </div>
          <div className="panel-body">
            {row.checks.map((check) => (
              <div key={check.check_id} className="posture-check">
                <div className="posture-check-name">
                  <span className={toneFor(check.status)}>{statusLabel(check.status)}</span>
                  <span className="posture-check-id">{check.check_name}</span>
                </div>
                <div className="posture-badges">
                  {check.controls.map((ctl) => (
                    <span key={ctl.control_id} className="posture-badge" title={ctl.name}>
                      <span className="posture-badge-fw">{FRAMEWORK_LABELS[check.framework] ?? check.framework}</span>
                      <span className="posture-badge-id">{ctl.control_id}</span>
                      {ctl.attested_status ? (
                        <span className={`posture-attested${ctl.attested_status === "MET" || ctl.attested_status === "implemented" ? " is-met" : ""}`}>
                          {ctl.attested_status}
                        </span>
                      ) : (
                        <span className="posture-attested is-unattested">not attested</span>
                      )}
                    </span>
                  ))}
                </div>
                {check.controls.length > 0 && (
                  <div className="posture-crosswalk">
                    Satisfies{" "}
                    {check.controls
                      .map((ctl) => `${FRAMEWORK_LABELS[check.framework] ?? check.framework} ${ctl.control_id}`)
                      .join(" · ")}
                  </div>
                )}
                {check.status !== "pass" && check.remediation && (
                  <div className="posture-remediation">
                    <strong>How to fix:</strong> {check.remediation}
                    {check.console_url && (
                      <a
                        className="posture-console-link"
                        href={check.console_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View in console ↗
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

type CapabilityRowAgg = {
  capability: string;
  best: string;
  checks: (PostureCheck & { framework: string })[];
};

function aggregateCapabilities(
  frameworks: string[],
  postures: Record<string, PostureResponse | null>,
): CapabilityRowAgg[] {
  const byCap: Map<string, CapabilityRowAgg> = new Map();
  for (const fw of frameworks) {
    const resp = postures[fw];
    if (!resp) continue;
    for (const cap of resp.capabilities) {
      const row = byCap.get(cap.capability) ?? {
        capability: cap.capability,
        best: "uncollected",
        checks: [],
      };
      for (const check of cap.checks) {
        row.checks.push({ ...check, framework: resp.framework });
        row.best = worseOf(row.best, check.status);
      }
      byCap.set(cap.capability, row);
    }
  }
  return [...byCap.values()].sort((a, b) => a.capability.localeCompare(b.capability));
}

const WORSE_ORDER: Record<string, number> = {
  fail: 5,
  error: 4,
  warn: 3,
  partial: 2,
  pass: 1,
  uncollected: 0,
};

function worseOf(a: string, b: string): string {
  return WORSE_ORDER[a] >= WORSE_ORDER[b] ? a : b;
}
