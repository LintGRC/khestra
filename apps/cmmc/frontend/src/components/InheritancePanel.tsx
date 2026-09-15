import { Link } from "react-router-dom";
import { useState } from "react";
import { InheritanceHint, InheritanceMapRow, ScopingSuggestion } from "../api";

type Props = {
  envScopeComplete: boolean;
  envScopeSummary: string;
  hints: InheritanceHint[];
  mapRows: InheritanceMapRow[];
  suggestions: ScopingSuggestion[];
};

function controlLink(controlId: string) {
  return `/controls?focus=${encodeURIComponent(controlId)}`;
}

export default function InheritancePanel({
  envScopeComplete,
  envScopeSummary,
  hints,
  mapRows,
  suggestions,
}: Props) {
  const [mapOpen, setMapOpen] = useState(false);
  const [extraHints, setExtraHints] = useState(false);
  const [extraSuggestions, setExtraSuggestions] = useState(false);

  if (!envScopeComplete && hints.length === 0 && mapRows.length === 0 && suggestions.length === 0) {
    return null;
  }

  const visibleHints = extraHints ? hints : hints.slice(0, 5);
  const visibleSuggestions = extraSuggestions ? suggestions : suggestions.slice(0, 8);

  return (
    <div className="inheritance-section">
      {envScopeSummary && <p className="muted">{envScopeSummary.replace(/\n/g, " · ")}</p>}

      {hints.length > 0 && (
        <div className="panel priority-review-panel">
          <div className="panel-header">
            <strong>Cloud / SaaS inheritance hints ({hints.length})</strong>
          </div>
          <div className="panel-body">
            <p className="muted">
              Shared responsibility — click a control to review. Mark <strong>Inherited</strong> only with provider evidence.
            </p>
            <div className="priority-list">
              {visibleHints.map((item) => (
                <Link key={`${item.control_id}-${item.provider}`} className="priority-control-link" to={controlLink(item.control_id)}>
                  <div className="priority-control-row">
                    <div className="priority-control-body">
                      <div className="priority-control-id">{item.control_id}</div>
                      <div className="priority-control-meta muted">
                        {item.provider}: {item.note}
                        {item.status ? ` · ${item.status}` : ""}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            {hints.length > 5 && (
              <button type="button" className="btn-link" onClick={() => setExtraHints(!extraHints)}>
                {extraHints ? "Show fewer" : `Show ${hints.length - 5} more`}
              </button>
            )}
          </div>
        </div>
      )}

      {mapRows.length > 0 && (
        <div className="panel">
          <button
            type="button"
            className="panel-header inheritance-map-toggle"
            aria-expanded={mapOpen}
            onClick={() => setMapOpen(!mapOpen)}
          >
            <strong>Shared responsibility map ({mapRows.length} controls)</strong>
          </button>
          {mapOpen && (
            <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
              <p className="muted" style={{ padding: "0.75rem 1rem 0" }}>
                Org vs provider split — use when marking Inherited or writing narratives.
              </p>
              <table className="inheritance-map-table">
                <thead>
                  <tr>
                    <th>Control</th>
                    <th>Provider</th>
                    <th>Level</th>
                    <th>Org owns</th>
                    <th>Provider owns</th>
                  </tr>
                </thead>
                <tbody>
                  {mapRows.map((row) => (
                    <tr key={`${row.control_id}-${row.provider}`}>
                      <td>
                        <Link to={controlLink(row.control_id)}>{row.control_id}</Link>
                      </td>
                      <td>{row.provider}</td>
                      <td>{row.inheritance_level}</td>
                      <td>{row.org_responsibility}</td>
                      <td>{row.provider_responsibility}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="panel priority-review-panel">
          <div className="panel-header">
            <strong>Scoping suggestions ({suggestions.length})</strong>
          </div>
          <div className="panel-body">
            <p className="muted">
              Based on your environment answers — confirm <strong>Not Applicable</strong> before changing status.
            </p>
            <div className="priority-list">
              {visibleSuggestions.map((item) => (
                <Link key={item.control_id} className="priority-control-link" to={controlLink(item.control_id)}>
                  <div className="priority-control-row">
                    <div className="priority-control-body">
                      <div className="priority-control-id">{item.control_id}</div>
                      <div className="priority-control-meta muted">
                        {item.reason}
                        {item.status ? ` · ${item.status}` : ""}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            {suggestions.length > 8 && (
              <button type="button" className="btn-link" onClick={() => setExtraSuggestions(!extraSuggestions)}>
                {extraSuggestions ? "Show fewer" : `Show ${suggestions.length - 8} more`}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
