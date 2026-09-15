import { Link, useLocation } from "react-router-dom";
import SprsWeightBadge from "./SprsWeightBadge";

export type PriorityRow = {
  id: string;
  name?: string;
  family?: string;
  status?: string;
  weight_tier?: string;
  weight_badge?: string;
};

type Props = {
  rows: PriorityRow[];
  onBrowseAll: () => void;
};

function statusClass(status: string) {
  if (status === "MET" || status === "NOT APPLICABLE" || status === "INHERITED") return "met";
  if (status === "NOT MET" || status === "NOT STARTED") return "gap";
  return "neutral";
}

export default function ControlsPriorityQueue({ rows, onBrowseAll }: Props) {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const visible = rows.slice(0, 12);

  return (
    <div className="panel controls-queue-panel">
      <div className="panel-header">
        <strong>Priority queue</strong>
        <span className="muted">5-point gaps first</span>
      </div>
      <div className="panel-body" style={{ padding: 0 }}>
        {visible.length === 0 ? (
          <p className="muted" style={{ padding: "1rem" }}>
            No open gaps in the current view — browse all controls or mark remaining as MET / N/A.
          </p>
        ) : (
          <ul className="controls-queue-list">
            {visible.map((row) => (
              <li key={row.id}>
                <Link className="controls-queue-row" to={`${fwBase}/controls/${encodeURIComponent(row.id)}`}>
                  <span className="controls-queue-id">{row.id}</span>
                  <span className="controls-queue-meta">
                    {row.name ? (
                      <span className="muted controls-queue-name control-requirement-text" title={row.name}>{row.name}</span>
                    ) : null}
                    <span className="controls-queue-chips">
                      {row.status && (
                        <span className={`badge ${statusClass(row.status)}`}>{row.status}</span>
                      )}
                      {row.weight_badge && (
                        <SprsWeightBadge
                          label={row.weight_badge}
                          tier={row.weight_tier || "standard"}
                          status={row.status}
                        />
                      )}
                    </span>
                  </span>
                  <span className="controls-queue-arrow" aria-hidden>→</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="panel-footer controls-queue-footer">
        <button type="button" className="btn btn-secondary" onClick={onBrowseAll}>
          Browse all controls
        </button>
      </div>
    </div>
  );
}
