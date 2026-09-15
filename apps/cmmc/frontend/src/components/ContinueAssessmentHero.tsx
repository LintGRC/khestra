import { Link, useLocation } from "react-router-dom";
import { NextAssessment } from "../api";

type Props = {
  next: NextAssessment | null;
  onContinue: (controlId: string) => void;
};

export default function ContinueAssessmentHero({ next, onContinue }: Props) {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  if (next?.next_control_id) {
    return (
      <div className="hero-card hero-card-primary">
        <div className="hero-card-body">
          <p className="hero-card-eyebrow">Next control</p>
          <h3 className="hero-card-title">{next.next_control_id}</h3>
          {next.next_control_name && (
            <p className="muted hero-card-subtitle control-requirement-text" title={next.next_control_name}>
              {next.next_control_name}
            </p>
          )}
          {next.next_control_status && (
            <span className={`badge ${next.next_control_status === "MET" ? "met" : next.next_control_status === "NOT MET" ? "gap" : "neutral"}`}>
              {next.next_control_status}
            </span>
          )}
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => onContinue(next.next_control_id!)}
        >
          Open control
        </button>
      </div>
    );
  }

  return (
    <div className="hero-card hero-card-success">
      <div className="hero-card-body">
        <p className="hero-card-eyebrow">Controls reviewed</p>
        <h3 className="hero-card-title">No pending controls in current view</h3>
        <p className="muted hero-card-subtitle">Verify narratives and evidence, then proceed to export.</p>
      </div>
      <Link className="btn btn-primary" to={`${fwBase}/export`}>
        Export center
      </Link>
    </div>
  );
}
