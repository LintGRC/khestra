import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { CheckCircle, Circle, FileText, Shield, BookOpen, FolderOpen, ClipboardCheck, Table } from "lucide-react";
import { EvidenceRequirementsChecklist } from "./EvidenceRequirementsChecklist";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";
import { apiUrl } from "@shared/apiPrefix";
import { policyApi } from "@shared/policy-manager/api";

const API = "/api/ai-governance";

type ReadinessState = {
  policies: { total: number; approved: number };
  plans: { total: number; approved: number };
  contracts: { total: number; signed: number };
  systems: number;
  evaluations: number;
  training_datasets: number;
  evidence_count: number;
  freshness: Record<string, number>;
  overdue_requests: number;
};

export function ReadinessChecklistPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const [state, setState] = useState<ReadinessState | null>(null);
  const [activeTab, setActiveTab] = useState(() => activeFrameworks[0] || "eu_ai_act");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeFrameworks.includes(activeTab as any)) {
      setActiveTab(activeFrameworks[0] || "eu_ai_act");
    }
  }, [activeFrameworks]);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/plans`).then(r => r.json()).catch(() => ({ plans: [], total: 0 })),
      fetch(`${API}/contracts`).then(r => r.json()).catch(() => ({ contracts: [], total: 0 })),
      fetch(`${API}/evaluations`).then(r => r.json()).catch(() => ({ evaluations: [], total: 0 })),
      fetch(`${API}/training-datasets`).then(r => r.json()).catch(() => ({ datasets: [], total: 0 })),
      fetch(`${API}/systems`).then(r => r.json()).catch(() => ({ systems: [] })),
      policyApi.list("aigov").catch(() => ({ policies: [] })),
      fetch(apiUrl("/api/evidence-hub/stats")).then(r => r.json()).catch(() => ({})),
      fetch(apiUrl("/api/evidence-hub/freshness?framework_id=AIGov")).then(r => r.json()).catch(() => ({})),
      fetch(apiUrl("/api/evidence-hub/requests/overdue")).then(r => r.json()).catch(() => ({ requests: [] })),
    ]).then(([plans, contracts, evals, training, systems, policies, evStats, fresh, overdue]) => {
      const allSystems = systems.systems || Object.values(systems).filter((v): v is Record<string, unknown> => typeof v === "object" && v !== null && "name" in v);
      const allPlans = plans.plans || [];
      const allContracts = contracts.contracts || [];
      const allPolicies = policies.policies || [];
      const aiEvCount = evStats.by_framework?.AIGov?.evidence_count || 0;
      setState({
        policies: {
          total: allPolicies.length,
          approved: allPolicies.filter((p: any) => p.status === "approved").length,
        },
        plans: {
          total: allPlans.length,
          approved: allPlans.filter((p: any) => p.status === "approved").length,
        },
        contracts: {
          total: allContracts.length,
          signed: allContracts.filter((c: any) => c.status === "signed").length,
        },
        systems: allSystems.length,
        evaluations: evals.total || (evals.evaluations || []).length,
        training_datasets: training.total || (training.datasets || []).length,
        evidence_count: aiEvCount,
        freshness: fresh || {},
        overdue_requests: (overdue.requests || []).length,
      });
    }).finally(() => setLoading(false));
  }, []);

  if (loading || !state) return <p className="muted" style={{ padding: 24 }}>Loading readiness data...</p>;

  const items = [
    { id: "systems", label: "AI Systems Registered", tool: "Systems Registry", link: "/aigov/systems", count: state.systems, total: 1, icon: Shield, color: "var(--primary)" },
    { id: "policies", label: "AI Governance Policies", tool: "Policy Manager", link: "/aigov/policies", count: state.policies.approved, total: state.policies.total, icon: BookOpen, color: "var(--primary)" },
    { id: "plans", label: "Operational Plans", tool: "Plans Manager", link: "/aigov/plans", count: state.plans.approved, total: state.plans.total, icon: FileText, color: "var(--info)" },
    { id: "evaluations", label: "Evaluations (all types)", tool: "Evaluations", link: "/aigov/evaluations", count: state.evaluations, total: 1, icon: ClipboardCheck, color: "var(--info)" },
    { id: "training", label: "Training Data Records", tool: "Training Data", link: "/aigov/training-data", count: state.training_datasets, total: 1, icon: Table, color: "var(--success)" },
    { id: "contracts", label: "Contractual Documents", tool: "Contracts", link: "/aigov/contracts", count: state.contracts.signed, total: state.contracts.total, icon: FileText, color: "var(--warning)" },
    { id: "evidence", label: "Evidence Hub Uploads", tool: "Evidence Hub", link: "/aigov/evidence", count: state.evidence_count, total: 1, icon: FolderOpen, color: "var(--success)",
      freshness: state.freshness.stale + state.freshness.expired > 0
        ? `${state.freshness.stale || 0} stale, ${state.freshness.expired || 0} expired`
        : `${state.freshness.fresh || 0} fresh`,
      freshCount: state.freshness.fresh || 0,
      staleCount: state.freshness.stale || 0,
      expiredCount: state.freshness.expired || 0,
      needRenewal: state.evidence_count > 0 && (state.freshness.stale > 0 || state.freshness.expired > 0),
    },
  ];

  const done = items.filter(i => !(i as any).needRenewal && i.count >= i.total).length;
  const total = items.length;
  const pct = Math.round((done / total) * 100);

  return (
    <div>
      <div className="aigov-page-header" style={{ marginBottom: "1.25rem" }}>
        <h1>Readiness Checklist</h1>
        <p>Audit readiness across all active frameworks</p>
      </div>

      <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
        <div className="panel" style={{ flex: 1, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: pct >= 80 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)" }}>{pct}%</div>
          <div className="muted" style={{ fontSize: 11 }}>Overall Readiness</div>
        </div>
        <div className="panel" style={{ flex: 1, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{done}/{total}</div>
          <div className="muted" style={{ fontSize: 11 }}>Categories Complete</div>
        </div>
        <div className="panel" style={{ flex: 1, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{state.systems}</div>
          <div className="muted" style={{ fontSize: 11 }}>AI Systems</div>
        </div>
      </div>

      {activeFrameworks.length === 0 ? (
        <div className="panel" style={{ padding: 16, marginBottom: 16, textAlign: "center" }}>
          <p className="muted" style={{ margin: 0 }}>
            No AI Governance frameworks selected.{' '}
            <button type="button" className="btn-link" onClick={() => {}}>Open Workspace settings</button> to configure.
          </p>
        </div>
      ) : (
      <div style={{ display: "flex", gap: 8, marginBottom: 16, justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 8 }}>
          {AI_GOV_FRAMEWORKS.filter(f => activeFrameworks.includes(f.key)).map(f => (
          <button key={f.key} className={`btn btn-sm ${activeTab === f.key ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setActiveTab(f.key)}
            style={activeTab === f.key ? { background: f.color, borderColor: f.color } : { color: f.color }}>
            {f.label}
          </button>
        ))}
      </div>
        <button className="btn btn-secondary btn-sm" onClick={() => window.open(apiUrl("/api/evidence-hub/export?framework_id=AIGov"), "_blank")} style={{ fontSize: 11, whiteSpace: "nowrap" }}>
          <FolderOpen size={12} /> Export Audit Package
        </button>
      </div>
      )}

      <div className="panel-stack" style={{ gap: 8 }}>
        {items.map(item => {
          const hasFreshness = !!(item as any).freshness;
          const needRenewal = !!(item as any).needRenewal;
          const isComplete = !needRenewal && item.count >= item.total;
          const pctDone = item.total > 0 ? Math.min(100, Math.round((item.count / item.total) * 100)) : 0;
          return (
            <div key={item.id} className="panel" style={{
              padding: 12,
              borderLeft: `3px solid ${isComplete ? "var(--success)" : "var(--danger)"}`,
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
                  {isComplete ? <CheckCircle size={18} style={{ color: "var(--success)", flexShrink: 0 }} /> : <Circle size={18} style={{ color: "var(--danger)", flexShrink: 0 }} />}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>{item.label}</div>
                    <div className="muted" style={{ fontSize: 11 }}>
                      {item.total > 1 ? `${item.count}/${item.total} complete (${pctDone}%)` : isComplete ? "Complete" : "Needs attention"} · via <strong>{item.tool}</strong>
                      {hasFreshness && (item as any).freshness && (
                        <span style={{ color: "var(--warning)", fontWeight: 600, marginLeft: 6 }}>{(item as any).freshness}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 6, alignItems: "center", flexShrink: 0 }}>
                  {!isComplete && (
                    <NavLink to={item.link} className="btn btn-primary btn-sm" style={{ fontSize: 11, padding: "4px 10px", whiteSpace: "nowrap" }}>
                      {item.total > 1 ? "Review All" : "Add"}
                    </NavLink>
                  )}
                  <NavLink to={item.link} className="btn btn-ghost btn-sm" style={{ fontSize: 11, padding: "4px 10px" }}>View</NavLink>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="panel" style={{ marginTop: 16, padding: 16 }}>
        <h4 style={{ margin: "0 0 8px" }}>Missing Items Guide</h4>
        <p className="muted" style={{ fontSize: 12, margin: 0 }}>
          {state.policies.total > 0 && state.policies.approved < state.policies.total && (
            <>• <strong>{state.policies.total - state.policies.approved} policies</strong> still in draft — open each policy and set status to approved.<br /></>
          )}
          {state.plans.total > 0 && state.plans.approved < state.plans.total && (
            <>• <strong>{state.plans.total - state.plans.approved} plans</strong> still in draft or under review — open each plan, fill in the content, and mark it approved.<br /></>
          )}
          {state.contracts.total > 0 && state.contracts.signed < state.contracts.total && (
            <>• <strong>{state.contracts.total - state.contracts.signed} contracts</strong> not yet signed — identify the counterparty, negotiate, and upload the signed version as evidence.<br /></>
          )}
          {state.evaluations === 0 && (
            <>• <strong>No evaluations</strong> — create evaluations for each AI system to demonstrate testing and monitoring.<br /></>
          )}
          {state.training_datasets === 0 && (
            <>• <strong>No training data records</strong> — document training data provenance for each AI system.<br /></>
          )}
          {state.evidence_count === 0 && (
            <>• <strong>No evidence uploaded</strong> — go to Evidence Hub and upload supporting documents, or use the checklist below to see what's needed.<br /></>
          )}
          {state.evaluations > 0 && state.training_datasets > 0 && state.plans.approved >= state.plans.total && state.contracts.signed >= state.contracts.total && state.evidence_count > 0 && state.policies.approved >= state.policies.total && (
            <>All categories are populated. Review the artifact checklist below for detailed per-control evidence requirements.</>
          )}
        </p>
        {state.plans.total === 0 && (
          <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
            <strong>Quick start:</strong> Go to <NavLink to="/aigov/plans">Plans → Seed Templates</NavLink> to create all 19 required plan templates, then <NavLink to="/aigov/contracts/seed">Contracts → Seed Templates</NavLink> for the 13 contract types. Then customize each one.
          </p>
        )}
      </div>

      {state.freshness.fresh + state.freshness.stale + state.freshness.expired > 0 && (
        <div className="panel" style={{ marginTop: 16, padding: 16, borderLeft: state.freshness.stale > 0 || state.freshness.expired > 0 ? "3px solid var(--warning)" : "3px solid var(--success)" }}>
          <h4 style={{ margin: "0 0 8px" }}>Evidence Health</h4>
          <p className="muted" style={{ fontSize: 12, margin: "0 0 10px" }}>
            {state.freshness.stale > 0 || state.freshness.expired > 0
              ? "Stale or expired evidence may not satisfy auditor requirements. Renew evidence before your next audit cycle."
              : `All ${state.freshness.fresh || 0} evidence items are fresh.`}
          </p>
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            {state.freshness.stale > 0 && (
              <span style={{ padding: "3px 8px", background: "var(--warning-soft)", color: "var(--warning)", borderRadius: 4, fontSize: 12, fontWeight: 600 }}>
                {state.freshness.stale} stale
              </span>
            )}
            {state.freshness.expired > 0 && (
              <span style={{ padding: "3px 8px", background: "var(--danger-soft)", color: "var(--danger)", borderRadius: 4, fontSize: 12, fontWeight: 600 }}>
                {state.freshness.expired} expired
              </span>
            )}
            {state.freshness.fresh > 0 && (
              <span style={{ padding: "3px 8px", background: "var(--success-soft)", color: "var(--success)", borderRadius: 4, fontSize: 12, fontWeight: 600 }}>
                {state.freshness.fresh || 0} fresh
              </span>
            )}
            {state.overdue_requests > 0 && (
              <span style={{ padding: "3px 8px", background: "var(--danger-soft)", color: "var(--danger)", borderRadius: 4, fontSize: 12, fontWeight: 600 }}>
                {state.overdue_requests} overdue request{state.overdue_requests > 1 ? "s" : ""}
              </span>
            )}
          </div>
          <NavLink to="/aigov/evidence" className="btn btn-secondary btn-sm">Review Evidence Hub →</NavLink>
        </div>
      )}

      <EvidenceRequirementsChecklist activeTab={activeTab} />
    </div>
  );
}
