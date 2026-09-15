import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authHeaders } from "@shared/accessToken";
import { authFetchJson } from "./authFetch";

const API = "/api/core";

type ConnectorMeta = {
  id: string;
  name: string;
  description: string;
  required_fields: string[];
  optional_fields?: string[];
  permissions_hint?: string;
  configured?: boolean;
  missing?: string[];
  import_only?: boolean;
  monitor?: { status: string; last_run_at?: string; last_status?: string } | null;
};

type CheckRow = {
  check_id: string;
  check_name: string;
  status: string;
  evidence: string;
  remediation: string;
  console_url: string;
};

type RunResult = {
  connector_id: string;
  summary: string;
  fixture: boolean;
  checks: CheckRow[];
};

type RunResponse = {
  run: RunResult;
  attached?: unknown[];
};

type CollectorsResponse = {
  connectors: ConnectorMeta[];
  monitoring?: { scheduled?: number; enabled?: number };
  recent_runs?: { connector_id: string; summary: string; completed_at: string; fixture?: boolean }[];
};

function statusTone(status: string): string {
  if (status === "pass") return "badge-success";
  if (status === "fail") return "badge-danger";
  if (status === "warn") return "badge-warning";
  return "badge-muted";
}

export default function CollectorsPage() {
  const [data, setData] = useState<CollectorsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, RunResult>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  const load = () => {
    authHeaders()
      .then(async (headers) => {
        const res = await fetch(`${API}/collectors`, { headers });
        if (res.status === 404) {
          setUnavailable(true);
          return;
        }
        if (!res.ok) throw new Error(String(res.status));
        setData((await res.json()) as CollectorsResponse);
      })
      .catch(() => setError("Failed to load collectors. Is the backend running?"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const runConnector = async (id: string) => {
    setRunning(id);
    setError(null);
    try {
      const res = await authFetchJson<RunResponse>(`${API}/collectors/${id}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_fixture: true, attach: true }),
      });
      setResults((prev) => ({ ...prev, [id]: res.run }));
      setExpanded((prev) => ({ ...prev, [id]: true }));
      load();
    } catch {
      setError(`Failed to run ${id}. Check connector credentials.`);
    } finally {
      setRunning(null);
    }
  };

  const importFile = async (id: string, file: File) => {
    setRunning(id);
    setError(null);
    try {
      const { authHeaders } = await import("@shared/accessToken");
      const headers = await authHeaders();
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/collectors/${id}/import`, {
        method: "POST",
        headers,
        body: form,
      });
      if (!res.ok) throw new Error(`import failed: ${res.status}`);
      const data = (await res.json()) as RunResponse;
      setResults((prev) => ({ ...prev, [id]: data.run }));
      setExpanded((prev) => ({ ...prev, [id]: true }));
      load();
    } catch {
      setError(`Failed to import for ${id}. Upload valid JSON output.`);
    } finally {
      setRunning(null);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading collectors…</div>;
  }

  if (unavailable) {
    return (
      <div>
        <div className="page-intro">
          <h1 className="page-intro-title">Collectors</h1>
          <p className="page-intro-summary">
            Automated evidence collection requires the collectors edition.
          </p>
        </div>
        <div className="panel">
          <div className="panel-body">
            <p className="muted">
              This deployment does not include the automated collectors. Everything else in this
              workspace — assessments, manual evidence, posture, and audit exports — works
              without them.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const connectors = data?.connectors ?? [];

  return (
    <div>
      <div className="page-intro">
        <h1 className="page-intro-title">Collectors</h1>
        <p className="page-intro-summary">
          Run evidence scans against your connected tools. Each connector checks the controls in
          scope and reports what needs fixing.
        </p>
        <div className="page-intro-actions" style={{ marginTop: "0.75rem" }}>
          <Link to="/posture" className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            Unified Posture
          </Link>
          <Link to="/remediation" className="btn btn-outline btn-xs" style={{ textDecoration: "none" }}>
            Remediation Queue
          </Link>
        </div>
      </div>

      {error && (
        <div className="banner error" style={{ marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      {connectors.length === 0 && (
        <div className="panel">
          <div className="panel-body">
            <p className="muted">No connectors registered.</p>
          </div>
        </div>
      )}

      <div className="panel-stack">
        {connectors.map((c) => {
          const result = results[c.id];
          const isOpen = expanded[c.id] && !!result;
          return (
            <div className="panel" key={c.id}>
              <div className="panel-header">
                <strong>{c.name}</strong>
                <div className="panel-header-meta">
                  {c.configured ? (
                    <span className="badge badge-success">configured</span>
                  ) : (
                    <span className="badge badge-muted" title={(c.missing ?? []).join(", ")}>
                      {c.import_only ? "import connector" : "needs credentials"}
                    </span>
                  )}
                  {c.monitor?.last_run_at && (
                    <span className="muted" style={{ fontSize: "0.75rem" }}>
                      last run {c.monitor.last_run_at.slice(0, 16).replace("T", " ")}
                    </span>
                  )}
                  {c.import_only ? (
                    <label className="btn btn-primary btn-xs" style={{ cursor: "pointer", margin: 0 }}>
                      {running === c.id ? "Importing…" : "Import JSON"}
                      <input
                        type="file"
                        accept=".json,application/json"
                        style={{ display: "none" }}
                        disabled={running === c.id}
                        onChange={(e) => {
                          const f = e.target.files?.[0];
                          if (f) importFile(c.id, f);
                          e.target.value = "";
                        }}
                      />
                    </label>
                  ) : (
                    <button
                      className="btn btn-primary btn-xs"
                      disabled={running === c.id}
                      onClick={() => runConnector(c.id)}
                    >
                      {running === c.id ? "Running…" : "Run now"}
                    </button>
                  )}
                </div>
              </div>
              <div className="panel-body">
                <p className="muted" style={{ fontSize: "0.8rem", margin: 0 }}>
                  {c.description}
                </p>
                {result && isOpen && (
                  <div style={{ marginTop: "0.75rem" }}>
                    <p style={{ fontSize: "0.8rem", fontWeight: 600 }}>
                      {result.summary}
                      {result.fixture && <span className="badge badge-muted" style={{ marginLeft: "0.5rem" }}>fixture</span>}
                    </p>
                    <div style={{ marginTop: "0.5rem" }}>
                      {result.checks.map((ch) => (
                        <div
                          key={ch.check_id}
                          style={{
                            border: "1px solid var(--border)",
                            borderRadius: 6,
                            padding: "0.5rem 0.6rem",
                            marginBottom: "0.4rem",
                          }}
                        >
                          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                            <span className={`badge ${statusTone(ch.status)}`}>{ch.status}</span>
                            <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>{ch.check_name}</span>
                            {ch.console_url && (
                              <a
                                href={ch.console_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn btn-ghost btn-xs"
                                style={{ marginLeft: "auto", fontSize: 11, textDecoration: "none" }}
                              >
                                View in console ↗
                              </a>
                            )}
                          </div>
                          {ch.status !== "pass" && ch.remediation && (
                            <div
                              style={{
                                fontSize: "0.78rem",
                                color: "var(--muted)",
                                marginTop: "0.35rem",
                                lineHeight: 1.45,
                              }}
                            >
                              <strong>How to fix:</strong> {ch.remediation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {result && !isOpen && (
                  <button
                    className="btn btn-ghost btn-xs"
                    style={{ marginTop: "0.5rem" }}
                    onClick={() => setExpanded((p) => ({ ...p, [c.id]: true }))}
                  >
                    Show results
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
