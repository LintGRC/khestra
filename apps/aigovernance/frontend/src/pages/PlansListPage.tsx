import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { Plus, Trash2, FileText } from "lucide-react";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";

const API = "/api/ai-governance";

const STATUS_COLORS: Record<string, string> = {
  draft: "var(--surface),var(--muted)",
  under_review: "var(--warning-soft, #fef3c7),var(--warning, #92400e)",
  approved: "var(--success-soft, #dcfce7),var(--success, #166534)",
  archived: "var(--surface),var(--muted)",
};

export function PlansListPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const [allPlans, setAllPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterFw, setFilterFw] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  function load() {
    setLoading(true);
    fetch(`${API}/plans`).then(r => r.json()).then(d => {
      setAllPlans(d.plans || []);
    }).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this plan?")) return;
    await fetch(`${API}/plans/${id}`, { method: "DELETE" });
    load();
  }

  const byFw: Record<string, any[]> = {};
  for (const fw of activeFrameworks) {
    byFw[fw] = allPlans.filter(p => p.framework === fw);
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div className="aigov-page-header" style={{ marginBottom: 0 }}>
          <h1>Plans</h1>
          <p>{allPlans.length} total plans</p>
        </div>
        <NavLink to="/aigov/plans/seed" className="btn btn-secondary btn-sm"><Plus size={14} /> Seed Templates</NavLink>
      </div>

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search plans..." />
        <FilterSelect value={filterFw} onChange={setFilterFw} options={AI_GOV_FRAMEWORKS.filter(fw => activeFrameworks.includes(fw.key)).map(fw => ({ value: fw.key, label: fw.label }))} placeholder="All frameworks" />
        <FilterSelect value={filterStatus} onChange={setFilterStatus} options={[
          { value: "draft", label: "Draft" },
          { value: "under_review", label: "Under Review" },
          { value: "approved", label: "Approved" },
          { value: "archived", label: "Archived" },
        ]} placeholder="All status" />
      </FilterBar>

      {loading ? (
        <p className="muted">Loading...</p>
      ) : allPlans.length === 0 ? (
        <div className="panel" style={{ textAlign: "center", padding: "2rem" }}>
          <p className="muted">No plans yet. Use "Seed Templates" to create the 19 required plans from framework catalogs, then customize them.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {AI_GOV_FRAMEWORKS.filter(fw => activeFrameworks.includes(fw.key)).map(fw => {
            const plans = byFw[fw.key].filter(p => {
              if (filterStatus && p.status !== filterStatus) return false;
              if (search) {
                const q = search.toLowerCase();
                if (!p.name?.toLowerCase().includes(q) && !p.description?.toLowerCase().includes(q)) return false;
              }
              return true;
            });
            if (filterFw && fw.key !== filterFw) return null;
            if (plans.length === 0) return null;
            const approved = plans.filter(p => p.status === "approved").length;
            return (
              <div key={fw.key}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <h3 style={{ margin: 0, color: fw.color }}>{fw.label}</h3>
                  <span className="muted" style={{ fontSize: 12 }}>{approved}/{plans.length} approved</span>
                </div>
                <div className="panel-stack" style={{ gap: 6 }}>
                  {plans.map(p => {
                    const sc = STATUS_COLORS[p.status] || STATUS_COLORS.draft;
                    return (
                      <div key={p.id} className="panel" style={{ padding: 10, borderLeft: `3px solid ${sc.split(",")[1] || "var(--muted)"}` }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
                            <FileText size={14} style={{ color: fw.color }} />
                            <div style={{ flex: 1 }}>
                              <NavLink to={`/aigov/plans/${p.id}`} style={{ fontWeight: 600, textDecoration: "none", color: "inherit", fontSize: 14 }}>{p.name}</NavLink>
                              {p.due_date && <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>Due: {p.due_date}</span>}
                            </div>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: sc.split(",")[0], color: sc.split(",")[1] }}>{p.status?.replace(/_/g, " ")}</span>
                            {p.owner && <span className="muted" style={{ fontSize: 11 }}>{p.owner}</span>}
                            <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(p.id)}><Trash2 size={12} /></button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
