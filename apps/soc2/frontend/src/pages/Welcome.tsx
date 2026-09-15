import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Dashboard, type ReadinessAssessment } from "../api";
import PageIntro from "../components/PageIntro";

const TOUR_STEPS = [
  { title: "1. Organization Profile", text: "Start here. Enter your company name, system description, architecture summary, and boundary. This data powers the System Description report auditors request.", href: "/organization" },
  { title: "2. TSC Scoping", text: "Choose which Trust Services Criteria categories apply to your organization. Security (CC1-CC9) is always required. Add Availability, Confidentiality, Processing Integrity, or Privacy as needed.", href: "/scoping" },
  { title: "3. Environment Scope", text: "Answer operational questions: cloud/SaaS providers, remote access, data processing, and subservice organizations. These answers inform scoping suggestions.", href: "/organization#org-env" },
  { title: "4. Create Policies", text: "Generate policies from 25 built-in templates. Each maps to specific criteria. Once created, assign owners and track review cycles.", href: "/policies" },
  { title: "5. Assess Controls", text: "Review each in-scope criterion. Set status (MET, NOT MET, etc.), write implementation narratives, assign owners, and upload evidence. Track Points of Focus per criterion.", href: "/criteria" },
  { title: "6. Collect Evidence", text: "Upload screenshots, logs, config exports — any artifact demonstrating control operation. Use auto-collectors for cloud services. Review and approve evidence.", href: "/evidence" },
  { title: "7. Review Readiness", text: "Check your composite readiness score. Close open gaps, address missing evidence, and export your audit package when ready.", href: "/readiness" },
];

type OnboardingStep = {
  key: string;
  label: string;
  description: string;
  href: string;
  done: boolean;
  required: boolean;
};

function buildSteps(_dash: Dashboard | null, readiness: ReadinessAssessment | null, scopingCompleted: boolean): OnboardingStep[] {
  const steps: OnboardingStep[] = [
    {
      key: "welcome",
      label: "Welcome",
      description: "Learn about SOC 2 Trust Services Criteria and how this tool helps you prepare for audit.",
      href: "/welcome",
      done: true,
      required: true,
    },
    {
      key: "organization",
      label: "Organization Profile",
      description: "Define your organization, system name, architecture, and team roles.",
      href: "/organization",
      done: (readiness?.profile_score ?? 0) >= 75,
      required: true,
    },
    {
      key: "scoping",
      label: "TSC Scoping",
      description: "Select which Trust Services Criteria categories apply — Security is always required, others are optional.",
      href: "/scoping",
      done: scopingCompleted,
      required: true,
    },
    {
      key: "environment",
      label: "Environment Scope",
      description: "Answer questions about cloud providers, SaaS, remote work, and data processing.",
      href: "/organization#org-env",
      done: (readiness?.assessment_pct ?? 0) > 0,
      required: true,
    },
    {
      key: "policies",
      label: "Policies",
      description: "Create or upload policies that map to SOC 2 controls (Acceptable Use, Access Control, etc.).",
      href: "/policies",
      done: (readiness?.policy_coverage_pct ?? 0) >= 50,
      required: false,
    },
    {
      key: "evidence",
      label: "Evidence Collection",
      description: "Upload evidence artifacts for each control, or connect automated collectors.",
      href: "/evidence",
      done: (readiness?.evidence_coverage_pct ?? 0) >= 50,
      required: true,
    },
    {
      key: "controls",
      label: "Assess Controls",
      description: "Review each control, set status, add implementation narratives, and assign owners.",
      href: "/criteria",
      done: (readiness?.assessment_pct ?? 0) >= 80,
      required: true,
    },
    {
      key: "review",
      label: "Review Readiness",
      description: "Check your readiness score, review gaps, and prepare for audit.",
      href: "/readiness",
      done: readiness?.audit_ready ?? false,
      required: true,
    },
  ];

  return steps;
}

export default function WelcomePage() {
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [readiness, setReadiness] = useState<ReadinessAssessment | null>(null);
  const [scopingCompleted, setScopingCompleted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.dashboard(), api.readinessAssessment(), api.getScope()])
      .then(([d, r, s]) => { setDash(d); setReadiness(r); setScopingCompleted(s.scoping_completed); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-stack"><p className="muted">Loading…</p></div>;

  const steps = buildSteps(dash, readiness, scopingCompleted);
  const doneCount = steps.filter((s) => s.done).length;
  const totalRequired = steps.filter((s) => s.required).length;
  const doneRequired = steps.filter((s) => s.required && s.done).length;
  const progress = Math.round((doneCount / steps.length) * 100);
  const [tourStep, setTourStep] = useState(-1);

  return (
    <div className="page-stack">
      <PageIntro title="Welcome to SOC 2 Compliance" summary="Follow these steps to prepare your organization for a SOC 2 Type II audit." />

      {tourStep >= 0 && (
        <div
          onClick={() => setTourStep(-1)}
          style={{
            position: "fixed", inset: 0, zIndex: 9999,
            background: "rgba(0,0,0,0.5)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff", borderRadius: 12, padding: 32, maxWidth: 480, width: "90%",
              boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
            }}
          >
            <h3 style={{ marginTop: 0 }}>{TOUR_STEPS[tourStep].title}</h3>
            <p style={{ lineHeight: 1.6, color: "#444" }}>{TOUR_STEPS[tourStep].text}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 20 }}>
              <span style={{ fontSize: 12, color: "#999" }}>Step {tourStep + 1} of {TOUR_STEPS.length}</span>
              <div style={{ display: "flex", gap: 8 }}>
                {tourStep > 0 && (
                  <button className="btn btn-sm btn-secondary" onClick={() => setTourStep(tourStep - 1)}>Back</button>
                )}
                {tourStep < TOUR_STEPS.length - 1 ? (
                  <button className="btn btn-sm btn-primary" onClick={() => setTourStep(tourStep + 1)}>Next</button>
                ) : (
                  <button className="btn btn-sm btn-primary" onClick={() => setTourStep(-1)}>Done</button>
                )}
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "center", gap: 4, marginTop: 12 }}>
              {TOUR_STEPS.map((_, i) => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: i === tourStep ? "var(--primary)" : "#ddd",
                }} />
              ))}
            </div>
          </div>
        </div>
      )}

      {readiness?.audit_ready && (
        <div className="banner success">
          You appear audit-ready! Review your exports and schedule your audit.
        </div>
      )}

      {/* Progress */}
      <section className="panel">
        <div className="panel-header">
          <h3>Your Progress</h3>
          <span className="badge badge-muted">{doneCount}/{steps.length} steps</span>
        </div>
        <div className="panel-body">
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 12 }}>
            <div style={{ flex: 1, background: "var(--border-subtle)", borderRadius: 6, height: 12, overflow: "hidden" }}>
              <div style={{
                width: `${progress}%`,
                height: "100%",
                background: progress >= 80 ? "var(--success)" : progress >= 50 ? "var(--warning)" : "var(--primary)",
                borderRadius: 6,
                transition: "width 0.3s",
              }} />
            </div>
            <span style={{ fontWeight: 600, minWidth: 40, textAlign: "right" }}>{progress}%</span>
          </div>
          <p className="muted" style={{ margin: 0 }}>
            {doneRequired} of {totalRequired} required steps complete.
            {readiness && ` Overall readiness: ${readiness.readiness_pct}%.`}
          </p>
        </div>
      </section>

      {/* Steps */}
      <section className="panel">
        <div className="panel-header"><h3>Setup Steps</h3></div>
        <div className="panel-body" style={{ padding: 0 }}>
          {steps.map((step, idx) => (
            <Link
              key={step.key}
              to={step.href}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 14,
                padding: "14px 20px",
                borderBottom: idx < steps.length - 1 ? "1px solid var(--border-subtle)" : "none",
                textDecoration: "none",
                color: "inherit",
                transition: "background 0.15s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              <span style={{
                fontSize: 20,
                width: 32,
                height: 32,
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: step.done ? "var(--success)" : "var(--border-subtle)",
                color: step.done ? "#fff" : "var(--muted)",
                flexShrink: 0,
              }}>
                {step.done ? "✓" : idx + 1}
              </span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 8 }}>
                  {step.label}
                  {step.required && !step.done && <span className="badge badge-warning" style={{ fontSize: 10 }}>Required</span>}
                  {!step.required && <span className="badge badge-muted" style={{ fontSize: 10 }}>Optional</span>}
                </div>
                <p className="muted" style={{ margin: "4px 0 0", fontSize: 13 }}>{step.description}</p>
              </div>
              <span style={{ color: "var(--muted)", fontSize: 18 }}>→</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Quick links */}
      <section className="panel">
        <div className="panel-header"><h3>Quick Actions</h3></div>
        <div className="panel-body" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button className="btn btn-primary btn-sm" onClick={() => setTourStep(0)}>Start Tour</button>
          <Link to="/readiness" className="btn btn-primary btn-sm">View Readiness</Link>
          <Link to="/reports" className="btn btn-secondary btn-sm">Download Reports</Link>
          <Link to="/criteria" className="btn btn-secondary btn-sm">Assess Controls</Link>
          <Link to="/evidence" className="btn btn-secondary btn-sm">Upload Evidence</Link>
        </div>
      </section>
    </div>
  );
}
