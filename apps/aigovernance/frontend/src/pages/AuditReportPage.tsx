import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { CheckCircle, AlertTriangle, Download, FileText } from "lucide-react";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { FW_LABELS, FW_COLORS } from "./aiGovFrameworks";
import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { policyApi } from "@shared/policy-manager/api";

const API = "/api/ai-governance";

type SystemSummary = {
  id: string;
  name: string;
  risk_classification: string;
  deployment_status: string;
  evidence_count: number;
  conformity: Record<string, { done: number; total: number; pct: number }>;
};

type ReportData = {
  systems: SystemSummary[];
  policies: { total: number; approved: number };
  plans: { total: number; approved: number };
  contracts: { total: number; signed: number };
  evidence: { total: number; approved: number; byControl: Set<string>; totalControls: number };
  generatedAt: string;
};

export function AuditReportPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function load() {
      const headers = await authHeaders();
      const [systemsRes, policiesRes, plansRes, contractsRes, _evStats, evItemsRes] = await Promise.all([
        fetch(`${API}/systems`, { headers }).then(r => r.json()).catch(() => ({ systems: [] })),
        policyApi.list("aigov").catch(() => ({ policies: [] })),
        fetch(`${API}/plans`, { headers }).then(r => r.json()).catch(() => ({ plans: [] })),
        fetch(`${API}/contracts`, { headers }).then(r => r.json()).catch(() => ({ contracts: [] })),
        fetch(apiUrl("/api/evidence-hub/stats"), { headers }).then(r => r.json()).catch(() => ({})),
        fetch(apiUrl("/api/evidence-hub?framework_id=AIGov"), { headers }).then(r => r.json()).catch(() => ({ evidence: [] })),
      ]);

      const allSystems: any[] = systemsRes.systems || [];
      const allPolicies: any[] = policiesRes.policies || [];
      const allPlans: any[] = plansRes.plans || [];
      const allContracts: any[] = contractsRes.contracts || [];
      const evItems: any[] = evItemsRes.evidence || [];
      const approvedEv = evItems.filter((e: any) => e.review_status === "approved").length;

      const byControl = new Set<string>();
      let totalControls = 0;
      for (const item of evItems) {
        for (const m of (item.mappings || [])) {
          if (m.framework_id === "AIGov" && m.control_id) {
            byControl.add(m.control_id);
            totalControls++;
          }
        }
      }

      const systems: SystemSummary[] = await Promise.all(
        allSystems.map(async (s: any) => {
          const fws = activeFrameworks;
          const conformity: Record<string, { done: number; total: number; pct: number }> = {};
          for (const fw of fws) {
            try {
              const res = await fetch(`${API}/systems/${s.id}/conformity?framework=${fw}`, { headers });
              const d = await res.json();
              const articles = d.conformity?.articles || {};
              const ids = Object.keys(articles);
              const total = ids.length;
              const done = ids.filter(k => articles[k]?.status && articles[k].status !== "missing").length;
              conformity[fw] = { done, total, pct: total ? Math.round((done / total) * 100) : 0 };
            } catch {
              conformity[fw] = { done: 0, total: 0, pct: 0 };
            }
          }
          const systemEv = evItems.filter((e: any) =>
            e.mappings?.some((m: any) => m.framework_id === "AIGov" && (
              Object.keys(conformity).some(fw => conformity[fw].total > 0)
            ))
          );
          return {
            id: s.id,
            name: s.name,
            risk_classification: s.risk_classification || "unclassified",
            deployment_status: s.deployment_status || "unknown",
            evidence_count: systemEv.length,
            conformity,
          };
        })
      );

      setData({
        systems,
        policies: { total: allPolicies.length, approved: allPolicies.filter((p: any) => p.status === "approved").length },
        plans: { total: allPlans.length, approved: allPlans.filter((p: any) => p.status === "approved").length },
        contracts: { total: allContracts.length, signed: allContracts.filter((c: any) => c.status === "signed").length },
        evidence: { total: evItems.length, approved: approvedEv, byControl, totalControls },
        generatedAt: new Date().toISOString().slice(0, 16).replace("T", " "),
      });
      setLoading(false);
    }
    load();
  }, []);

  async function handleExport() {
    setExporting(true);
    try {
      const headers = await authHeaders();
      const blob = await fetch(apiUrl("/api/evidence-hub/export?framework_id=AIGov"), { headers }).then(r => r.blob());
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `aigov-audit-package-${new Date().toISOString().slice(0, 10)}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {}
    setExporting(false);
  }

  if (loading) return <p className="muted" style={{ padding: 24 }}>Generating audit report...</p>;
  if (!data) return <p className="muted" style={{ padding: 24 }}>Failed to load report data.</p>;

  const overallPct = (() => {
    const checks = [
      data.policies.approved >= data.policies.total,
      data.plans.approved >= data.plans.total,
      data.contracts.signed >= data.contracts.total,
      data.evidence.total > 0,
      data.systems.length > 0,
    ];
    return Math.round((checks.filter(Boolean).length / checks.length) * 100);
  })();

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ margin: 0 }}>Audit Readiness Report</h1>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>Generated {data.generatedAt} · AI Governance</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
            <FileText size={14} /> Export PDF
          </button>
          <button className="btn btn-primary btn-sm" onClick={handleExport} disabled={exporting}>
            <Download size={14} /> {exporting ? "Exporting..." : "Download Evidence Package"}
          </button>
        </div>
      </div>

      <div className="panel-stack" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: overallPct >= 80 ? "var(--success)" : overallPct >= 50 ? "var(--warning)" : "var(--danger)" }}>{overallPct}%</div>
          <div className="muted" style={{ fontSize: 11 }}>Audit Readiness</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{data.systems.length}</div>
          <div className="muted" style={{ fontSize: 11 }}>AI Systems</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{data.policies.approved}/{data.policies.total}</div>
          <div className="muted" style={{ fontSize: 11 }}>Policies Approved</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{data.plans.approved}/{data.plans.total}</div>
          <div className="muted" style={{ fontSize: 11 }}>Plans Approved</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{data.contracts.signed}/{data.contracts.total}</div>
          <div className="muted" style={{ fontSize: 11 }}>Contracts Signed</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{data.evidence.total}</div>
          <div className="muted" style={{ fontSize: 11 }}>Evidence Files · {data.evidence.approved} approved</div>
        </div>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <h3 style={{ margin: "0 0 12px" }}>Per-Framework Compliance</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {activeFrameworks.map(fw => {
            const assessed = data.systems.filter(s => (s.conformity[fw]?.total || 0) > 0);
            const avgPct = assessed.length > 0
              ? Math.round(assessed.reduce((sum, s) => sum + (s.conformity[fw]?.pct || 0), 0) / assessed.length)
              : 0;
            const totalDone = assessed.reduce((sum, s) => sum + (s.conformity[fw]?.done || 0), 0);
            const totalTotal = assessed.reduce((sum, s) => sum + (s.conformity[fw]?.total || 0), 0);
            return (
              <div key={fw} style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 12px", borderRadius: 6, border: "1px solid var(--border)" }}>
                <span style={{ width: 36, height: 36, borderRadius: 8, background: FW_COLORS[fw] + "18", color: FW_COLORS[fw], display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 10 }}>{FW_LABELS[fw].slice(0, 2)}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{FW_LABELS[fw]}</div>
                  <div className="muted" style={{ fontSize: 11 }}>{assessed.length} systems assessed · {totalDone}/{totalTotal} controls compliant</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: avgPct >= 80 ? "var(--success)" : avgPct >= 30 ? "var(--warning)" : "var(--danger)" }}>{avgPct}%</div>
                  <div style={{ width: 80, background: "var(--border)", borderRadius: 3, height: 5, overflow: "hidden", marginTop: 2 }}>
                    <div style={{ width: `${avgPct}%`, height: "100%", borderRadius: 3, background: avgPct >= 80 ? "var(--success)" : avgPct >= 30 ? "var(--warning)" : "var(--danger)" }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="panel" style={{ padding: 0 }}>
        <div className="panel-header" style={{ padding: "12px 16px" }}><strong>Systems Detail &amp; Evidence Coverage</strong></div>
        <div style={{ overflowX: "auto" }}>
          <table className="table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--surface-secondary, var(--surface))" }}>
                <th style={{ padding: "8px 12px", textAlign: "left" }}>System</th>
                <th style={{ padding: "8px 12px", textAlign: "left" }}>Risk</th>
                {activeFrameworks.map(fw => (
                  <th key={fw} style={{ padding: "8px 12px", textAlign: "center" }}>{FW_LABELS[fw]?.split(" ")[0]}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.systems.map(s => (
                <tr key={s.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                  <td style={{ padding: "8px 12px" }}>
                    <NavLink to={`/aigov/systems/${s.id}`} style={{ fontWeight: 500, color: "var(--primary)", textDecoration: "none" }}>{s.name}</NavLink>
                  </td>
                  <td style={{ padding: "8px 12px" }}>
                    <span className="badge" style={{ fontSize: 10 }}>{s.risk_classification}</span>
                  </td>
                  {activeFrameworks.map(fw => {
                    const c = s.conformity[fw];
                    const pct = c?.pct ?? 0;
                    const display = c?.total ? `${c.done}/${c.total} (${pct}%)` : "—";
                    return (
                      <td key={fw} style={{ padding: "8px 12px", textAlign: "center" }}>
                        <span style={{ color: pct >= 80 ? "var(--success)" : pct > 0 ? "var(--warning)" : "var(--muted)", fontWeight: 500 }}>{display}</span>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <h3 style={{ margin: "0 0 12px" }}>Evidence Overview</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
          <div className="panel" style={{ padding: 12, textAlign: "center", margin: 0 }}>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{data.evidence.total}</div>
            <div className="muted" style={{ fontSize: 11 }}>Total Files Uploaded</div>
          </div>
          <div className="panel" style={{ padding: 12, textAlign: "center", margin: 0 }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: "var(--success)" }}>{data.evidence.approved}</div>
            <div className="muted" style={{ fontSize: 11 }}>Approved for Audit</div>
          </div>
          <div className="panel" style={{ padding: 12, textAlign: "center", margin: 0 }}>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{data.evidence.byControl.size}</div>
            <div className="muted" style={{ fontSize: 11 }}>Controls with Evidence</div>
          </div>
          <div className="panel" style={{ padding: 12, textAlign: "center", margin: 0 }}>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{data.evidence.totalControls}</div>
            <div className="muted" style={{ fontSize: 11 }}>Total Control Mappings</div>
          </div>
        </div>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <h3 style={{ margin: "0 0 8px" }}>Open Items</h3>
        <div style={{ fontSize: 12, display: "flex", flexDirection: "column", gap: 6 }}>
          {data.policies.total > 0 && data.policies.approved < data.policies.total && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><AlertTriangle size={14} style={{ color: "var(--danger)", flexShrink: 0 }} />
              <span>{data.policies.total - data.policies.approved} policies still in draft</span>
              <NavLink to="/aigov/policies" className="btn btn-ghost btn-sm" style={{ fontSize: 10, padding: "2px 8px", marginLeft: "auto" }}>Review</NavLink>
            </div>
          )}
          {data.plans.total > 0 && data.plans.approved < data.plans.total && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><AlertTriangle size={14} style={{ color: "var(--warning)", flexShrink: 0 }} />
              <span>{data.plans.total - data.plans.approved} plans not yet approved</span>
              <NavLink to="/aigov/plans" className="btn btn-ghost btn-sm" style={{ fontSize: 10, padding: "2px 8px", marginLeft: "auto" }}>Review</NavLink>
            </div>
          )}
          {data.contracts.total > 0 && data.contracts.signed < data.contracts.total && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><AlertTriangle size={14} style={{ color: "var(--warning)", flexShrink: 0 }} />
              <span>{data.contracts.total - data.contracts.signed} contracts not yet signed</span>
              <NavLink to="/aigov/contracts" className="btn btn-ghost btn-sm" style={{ fontSize: 10, padding: "2px 8px", marginLeft: "auto" }}>Review</NavLink>
            </div>
          )}
          {data.evidence.total === 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><AlertTriangle size={14} style={{ color: "var(--danger)", flexShrink: 0 }} />
              <span>No evidence files uploaded — required for audit</span>
              <NavLink to="/aigov/evidence" className="btn btn-ghost btn-sm" style={{ fontSize: 10, padding: "2px 8px", marginLeft: "auto" }}>Upload</NavLink>
            </div>
          )}
          {data.systems.filter(s => Object.values(s.conformity).every(c => c.total === 0)).length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><AlertTriangle size={14} style={{ color: "var(--danger)", flexShrink: 0 }} />
              <span>{data.systems.filter(s => Object.values(s.conformity).every(c => c.total === 0)).length} systems with no conformity assessment</span>
            </div>
          )}
          {data.policies.approved >= data.policies.total && data.plans.approved >= data.plans.total &&
           data.contracts.signed >= data.contracts.total && data.evidence.total > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><CheckCircle size={14} style={{ color: "var(--success)", flexShrink: 0 }} />
              <span>All tracked items are populated. Review per-control evidence coverage for completeness.</span>
              <NavLink to="/aigov/readiness" className="btn btn-ghost btn-sm" style={{ fontSize: 10, padding: "2px 8px", marginLeft: "auto" }}>Artifact Checklist</NavLink>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
