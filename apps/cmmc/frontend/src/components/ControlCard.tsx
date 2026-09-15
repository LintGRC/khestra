import { Link } from "react-router-dom";
import { ControlSummary } from "../api";
import SprsWeightBadge, { focusAnchorId } from "./SprsWeightBadge";

type Props = {
  control: ControlSummary;
  focused: boolean;
  canEdit: boolean;
  statusOptions: string[];
  saving: boolean;
  executiveView?: boolean;
  onStatusChange: (id: string, status: string) => void;
};

function statusClass(status: string) {
  if (status === "MET" || status === "NOT APPLICABLE" || status === "INHERITED") return "met";
  if (status === "NOT MET" || status === "NOT STARTED") return "gap";
  return "neutral";
}

const COLLECTOR_DOT: Record<string, { cls: string; title: string }> = {
  pass: { cls: "collector-dot--pass", title: "Automated checks: all passing" },
  fail: { cls: "collector-dot--fail", title: "Automated checks: some failing" },
  error: { cls: "collector-dot--error", title: "Automated check error — collector may be broken" },
  uncollected: { cls: "collector-dot--idle", title: "No automated check data yet" },
};

function reviewedPct(status: string, hasNarrative: boolean) {
  if (status === "NOT STARTED") return 0;
  if (["MET", "NOT APPLICABLE", "INHERITED"].includes(status)) {
    return hasNarrative || status !== "MET" ? 100 : 50;
  }
  return 40;
}

function atRisk(status: string) {
  return !["MET", "NOT APPLICABLE", "INHERITED"].includes(status);
}

export default function ControlCard({
  control,
  focused,
  canEdit,
  statusOptions,
  saving,
  executiveView,
  onStatusChange,
}: Props) {
  const anchor = focusAnchorId(control.id);

  if (executiveView) {
    const pct = reviewedPct(control.status, control.has_narrative);
    return (
      <article
        id={anchor}
        className={`control-card control-card-executive${focused ? " control-card-focused" : ""}`}
      >
        <div className="control-card-head">
          <Link to={control.id}>
            <strong className="control-id-text">{control.id}</strong>
          </Link>
          <span className={`badge ${statusClass(control.status)}`}>{control.status}</span>
        </div>
        <div className="executive-progress">
          <div className="executive-progress-track">
            <div className="executive-progress-fill" style={{ width: `${pct}%` }} />
          </div>
          <span className="muted">{pct}% reviewed</span>
        </div>
        {canEdit && (
          <select
            className="inline-status"
            value={control.status}
            disabled={saving}
            onChange={(e) => onStatusChange(control.id, e.target.value)}
          >
            {statusOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        )}
      </article>
    );
  }

  return (
    <article
      id={anchor}
      className={`control-card${focused ? " control-card-focused" : ""}`}
    >
      <div className="control-card-head">
        <div className="control-card-title">
          <Link to={`${encodeURIComponent(control.id)}`}>
            <strong className="control-id-text">{control.id}</strong>
          </Link>
          <div className="muted control-card-name">{control.name}</div>
          {atRisk(control.status) ? (
            <div className="control-deduction control-deduction-risk">
              At risk: −{control.weight_hint || control.weight} points from score of 110 if unchanged
            </div>
          ) : (
            <div className="control-deduction control-deduction-none">No SPRS deduction at current status</div>
          )}
        </div>
        <div className="control-card-meta">
          <SprsWeightBadge
            label={control.weight_badge || `${control.weight} PT`}
            tier={control.weight_tier || "standard"}
            status={control.status}
            title={`${control.status} · ${control.weight_hint || control.weight} PT`}
          />
        </div>
      </div>

      <div className="control-card-body">
        <div className="control-card-fields">
          <label className="sr-only" htmlFor={`status-${control.id}`}>Status</label>
          {canEdit ? (
            <select
              id={`status-${control.id}`}
              className="inline-status"
              value={control.status}
              disabled={saving}
              onChange={(e) => onStatusChange(control.id, e.target.value)}
            >
              {statusOptions.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          ) : (
            <span className={`badge ${statusClass(control.status)}`}>{control.status}</span>
          )}
          {control.collector_status && COLLECTOR_DOT[control.collector_status] && (
            <span
              className={`collector-dot ${COLLECTOR_DOT[control.collector_status].cls}`}
              title={COLLECTOR_DOT[control.collector_status].title}
            />
          )}
          <span className="muted control-card-chips">
            {control.has_narrative ? "SSP description ✓" : "Needs SSP description"}
            {" · "}
            {control.evidence_count ? `${control.evidence_count} file(s)` : "No files attached"}
          </span>
        </div>
        <Link className="btn btn-secondary btn-sm" to={`${encodeURIComponent(control.id)}`}>
          Review &amp; document
        </Link>
      </div>
    </article>
  );
}
