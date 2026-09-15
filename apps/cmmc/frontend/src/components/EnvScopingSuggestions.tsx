import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../api";

function focusLink(controlId: string) {
  return `/controls?focus=${encodeURIComponent(controlId)}`;
}

export default function EnvScopingSuggestions() {
  const [suggestions, setSuggestions] = useState<
    { control_id: string; suggestion: string; reason: string }[]
  >([]);
  const [loaded, setLoaded] = useState(false);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    api
      .alerts()
      .then((data) => {
        setSuggestions(data.env_suggestions || []);
        setLoaded(true);
      })
      .catch(console.error);
  }, []);

  if (!loaded) return null;

  if (suggestions.length === 0) {
    return (
      <div className="banner info">
        <strong>Environment scope</strong> — answer the environment questions on{" "}
        <Link to="/organization">Organization</Link> to unlock N/A suggestions and stronger readiness checks.
      </div>
    );
  }

  const visible = showAll ? suggestions : suggestions.slice(0, 8);

  return (
    <div className="panel priority-review-panel">
      <div className="panel-header">
        <strong>Scoping suggestions ({suggestions.length})</strong>
      </div>
      <div className="panel-body">
        <p className="muted">
          Based on your environment answers — confirm <strong>Not Applicable</strong> before changing status.
        </p>
        <div className="priority-list">
          {visible.map((item) => (
            <Link key={item.control_id} className="priority-control-link" to={focusLink(item.control_id)}>
              <div className="priority-control-row">
                <div className="priority-control-body">
                  <div className="priority-control-id">{item.control_id}</div>
                  <div className="priority-control-meta muted">
                    {item.reason}
                    {item.suggestion ? ` · ${item.suggestion}` : ""}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
        {suggestions.length > 8 && (
          <button type="button" className="btn-link" onClick={() => setShowAll(!showAll)}>
            {showAll ? "Show fewer" : `Show ${suggestions.length - 8} more`}
          </button>
        )}
      </div>
    </div>
  );
}
