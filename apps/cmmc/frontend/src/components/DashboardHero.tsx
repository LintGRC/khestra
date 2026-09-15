import { Link } from "react-router-dom";
import { Dashboard, Journey } from "../api";

type Props = {
  dashboard: Dashboard;
  journey: Journey | null;
};

export default function DashboardHero({ dashboard, journey }: Props) {
  const needsOrg = dashboard.blockers.some((b) => b.toLowerCase().includes("organization name"));
  const notStarted = dashboard.controls_assessed === 0;

  if (needsOrg || notStarted) {
    return (
      <div className="hero-card hero-card-primary">
        <div className="hero-card-body">
          <p className="hero-card-eyebrow">Initial setup</p>
          <h3 className="hero-card-title">
            {needsOrg ? "Complete organization profile" : "Start control assessment"}
          </h3>
          <p className="muted hero-card-subtitle">
            {needsOrg
              ? "Company name and scope are required before assessing controls or exporting SSP/POA&M."
              : "Work through controls systematically. Prioritize 5-point gaps for SPRS impact."}
          </p>
        </div>
        <Link className="btn btn-primary" to={needsOrg ? "/organization" : "/controls"}>
          {needsOrg ? "Organization profile" : "Open controls"}
        </Link>
      </div>
    );
  }

  const next = journey?.next_step;
  if (next) {
    const href =
      next.view === "System Profile"
        ? "/organization"
        : next.view === "Report Center"
          ? "/export"
          : next.view === "Pre-C3PAO Readiness"
            ? "/readiness"
            : "/controls";
    return (
      <div className="hero-card hero-card-primary">
        <div className="hero-card-body">
          <p className="hero-card-eyebrow">Next action</p>
          <h3 className="hero-card-title">{next.label}</h3>
          <p className="muted hero-card-subtitle">{next.hint}</p>
        </div>
        <Link className="btn btn-primary" to={href}>
          Continue
        </Link>
      </div>
    );
  }

  if (dashboard.export_readiness_pct >= 70 && dashboard.open_gaps === 0) {
    return (
      <div className="hero-card hero-card-success">
        <div className="hero-card-body">
          <p className="hero-card-eyebrow">Export readiness</p>
          <h3 className="hero-card-title">Assessment ready for export</h3>
          <p className="muted hero-card-subtitle">Generate SSP and POA&M packages when review is complete.</p>
        </div>
        <Link className="btn btn-primary" to="/export">
          Export center
        </Link>
      </div>
    );
  }

  return (
    <div className="hero-card hero-card-primary">
      <div className="hero-card-body">
        <p className="hero-card-eyebrow">
          {dashboard.open_gaps > 0 ? "Remaining gaps" : "Assessment in progress"}
        </p>
        <h3 className="hero-card-title">
          {dashboard.open_gaps > 0 ? "Close open control gaps" : "Continue control review"}
        </h3>
        <p className="muted hero-card-subtitle">
          {dashboard.open_gaps > 0
            ? `${dashboard.open_gaps} open gap(s) · SPRS ${dashboard.sprs_score}/${dashboard.sprs_max} · ${dashboard.export_readiness_pct}% export readiness`
            : `${dashboard.open_gaps} open gap(s) · ${dashboard.export_readiness_pct}% export readiness`}
        </p>
      </div>
      <Link className="btn btn-primary" to="/controls">
        {dashboard.open_gaps > 0 ? "Review gaps" : "Open controls"}
      </Link>
    </div>
  );
}
