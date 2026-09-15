import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import type { ScopeCoverage } from "../api";

const STATUS_LABELS: Record<string, string> = {
  matched: "Matched",
  undeclared: "Undeclared",
  unmanaged: "Unmanaged",
  non_compliant: "Non-compliant",
  out_of_scope: "Out of scope",
};

type Props = {
  coverage: ScopeCoverage | undefined;
};

export default function ScopeCoveragePanel({ coverage }: Props) {
  if (!coverage) {
    return (
      <div className="panel" id="org-coverage">
        <div className="panel-header">
          <strong>Scope coverage</strong>
        </div>
        <div className="panel-body">
          <p className="muted">Loading coverage…</p>
        </div>
      </div>
    );
  }

  const { summary, records, exceptions, synced_at, reconciled } = coverage;
  const open = summary.exception_count;
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const toggleExpanded = (idx: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };
  const exceptionByTitle = Object.fromEntries(exceptions.map((e) => [e.title, e]));
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  return (
    <div className="panel" id="org-coverage">
      <div className="panel-header">
        <strong>Scope coverage</strong>
        <span className={`coverage-pill${reconciled ? " coverage-pill-ok" : open ? " coverage-pill-warn" : ""}`}>
          {reconciled ? "Reconciled" : open ? `${open} exception${open === 1 ? "" : "s"}` : "No in-scope inventory"}
        </span>
      </div>
      <div className="panel-body coverage-panel-body">
        <p className="panel-intro">
          Compare declared asset inventory with the latest Intune device sync. Fix exceptions before assessment.
        </p>

        <div className="coverage-summary-grid">
          <div className="coverage-stat">
            <span className="coverage-stat-value">{summary.declared_in_scope}</span>
            <span className="coverage-stat-label">In-scope declared</span>
          </div>
          <div className="coverage-stat">
            <span className="coverage-stat-value">{summary.live_devices}</span>
            <span className="coverage-stat-label">Intune devices</span>
          </div>
          <div className="coverage-stat">
            <span className="coverage-stat-value">{summary.matched}</span>
            <span className="coverage-stat-label">Matched</span>
          </div>
          <div className="coverage-stat">
            <span className="coverage-stat-value">{open}</span>
            <span className="coverage-stat-label">Exceptions</span>
          </div>
        </div>

        {synced_at ? (
          <p className="muted field-hint">Last Intune sync: {synced_at.replace("T", " ").replace("+00:00", " UTC")}</p>
        ) : (
          <p className="muted field-hint">
            No Intune sync yet.{" "}
            <Link to="/integrations">Run Intune connector</Link> (Try demo works offline).
          </p>
        )}

        {records.length > 0 && (
          <div className="coverage-table-wrap">
            <h4 className="coverage-subheading">Register</h4>
            <table className="coverage-table">
              <thead>
                <tr>
                  <th style={{ width: 20 }}></th>
                  <th>Asset</th>
                  <th>Type</th>
                  <th>In scope</th>
                  <th>Status</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {records.map((row, idx) => {
                  const exc = exceptionByTitle[row.asset_name];
                  const isExpanded = expanded.has(idx) && !!exc;
                  const isExpandable = !!exc;
                  return [
                    <tr key={`${row.asset_name}-${idx}`}
                      onClick={isExpandable ? () => toggleExpanded(idx) : undefined}
                      style={isExpandable ? { cursor: "pointer" } : undefined}
                    >
                      <td style={{ width: 20 }}>
                        {isExpandable && <span style={{ fontSize: "0.65rem" }}>{isExpanded ? "▼" : "▶"}</span>}
                      </td>
                      <td>{row.asset_name}</td>
                      <td className="muted">{row.asset_type || "—"}</td>
                      <td>{row.in_scope || "—"}</td>
                      <td>
                        <span className={`coverage-badge coverage-badge-${row.status}`}>
                          {STATUS_LABELS[row.status] || row.status}
                        </span>
                      </td>
                      <td className="muted">{row.source}</td>
                    </tr>,
                    isExpanded && exc ? (
                      <tr key={`${row.asset_name}-detail-${idx}`}>
                        <td></td>
                        <td colSpan={5} style={{ padding: "0.25rem 0.75rem 0.5rem" }}>
                          <p className="muted" style={{ margin: 0, fontSize: "0.8rem" }}>{exc.detail}</p>
                          {exc.control_ids && exc.control_ids.length > 0 && (
                            <p className="coverage-control-links" style={{ margin: "0.25rem 0 0" }}>
                              {exc.control_ids.slice(0, 3).map((cid) => (
                                <Link key={cid} to={`${fwBase}/controls/${encodeURIComponent(cid)}`}>{cid}</Link>
                              ))}
                            </p>
                          )}
                        </td>
                      </tr>
                    ) : null,
                  ];
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
