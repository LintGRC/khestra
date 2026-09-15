import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, MyWorkReport } from "../api";

type Props = {
  onBrowseAssigned: () => void;
  onSetUserName?: () => void;
};

function statusClass(status: string) {
  if (status === "MET" || status === "NOT APPLICABLE" || status === "INHERITED") return "met";
  if (status === "NOT MET" || status === "NOT STARTED") return "gap";
  return "neutral";
}

export default function ControlsMyWorkPanel({ onBrowseAssigned, onSetUserName }: Props) {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const [report, setReport] = useState<MyWorkReport | null>(null);

  useEffect(() => {
    api.myWork().then(setReport).catch(console.error);
  }, []);

  if (!report) return null;

  if (report.needs_user_name) {
    return (
      <div className="banner info controls-my-work-banner">
        <strong>My assignments</strong> — set your name in{" "}
        <button type="button" className="btn-link" onClick={onSetUserName}>
          Workspace &amp; settings
        </button>
        {" "}(bottom of left sidebar). Add team names on{" "}
        <Link to={`${fwBase}/organization`}>Organization</Link> → Assessment team, save, then pick your name.
      </div>
    );
  }

  if (report.assigned_count === 0) {
    return (
      <div className="panel controls-my-work-panel">
        <div className="panel-header">
          <strong>My assignments</strong>
          <span className="muted">{report.current_user_name}</span>
        </div>
        <div className="panel-body">
          <p className="muted">No open items assigned to you. Assign an owner on a control POA&amp;M or document step.</p>
        </div>
      </div>
    );
  }

  const preview = report.controls.slice(0, 8);

  return (
    <div className="panel controls-my-work-panel">
      <div className="panel-header">
        <strong>My assignments</strong>
        <span className="muted">
          {report.assigned_count} open
          {report.overdue_count > 0 && ` · ${report.overdue_count} overdue`}
        </span>
      </div>
      <div className="panel-body" style={{ padding: 0 }}>
        <ul className="controls-queue-list">
          {preview.map((row) => (
            <li key={row.id}>
              <Link className="controls-queue-row" to={`${fwBase}/controls/${encodeURIComponent(row.id)}`}>
                <span className="controls-queue-id">{row.id}</span>
                <span className="controls-queue-meta">
                  <span className="muted controls-queue-name control-requirement-text" title={row.name}>{row.name}</span>
                  <span className="controls-queue-chips">
                    <span className={`badge ${statusClass(row.status)}`}>{row.status}</span>
                    {row.overdue && <span className="badge gap">Overdue</span>}
                    {row.status === "MET" && !row.has_narrative && (
                      <span className="badge neutral">Needs narrative</span>
                    )}
                    {row.comment_count > 0 && (
                      <span className="badge neutral">{row.comment_count} note{row.comment_count === 1 ? "" : "s"}</span>
                    )}
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
      {report.assigned_count > preview.length && (
        <div className="panel-footer">
          <button type="button" className="btn-link" onClick={onBrowseAssigned}>
            View all {report.assigned_count} assigned controls →
          </button>
        </div>
      )}
    </div>
  );
}
