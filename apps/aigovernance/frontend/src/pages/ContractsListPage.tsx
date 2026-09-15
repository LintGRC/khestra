import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { FileText, Trash2 } from "lucide-react";
import { useActiveFrameworks } from "./AiGovFrameworkContext";
import { AI_GOV_FRAMEWORKS } from "./aiGovFrameworks";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";

const API = "/api/ai-governance";

const STATUS_COLORS: Record<string, string> = {
  not_started: "var(--surface),var(--muted)",
  in_progress: "var(--warning-soft, #fef3c7),var(--warning, #92400e)",
  signed: "var(--success-soft, #dcfce7),var(--success, #166534)",
  expired: "var(--danger-soft, #fee2e2),var(--danger, #991b1b)",
};

export function ContractsListPage() {
  const { activeFrameworks } = useActiveFrameworks();
  const [allContracts, setAllContracts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterFw, setFilterFw] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  function load() {
    setLoading(true);
    fetch(`${API}/contracts`).then(r => r.json()).then(d => setAllContracts(d.contracts || [])).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this contract record?")) return;
    await fetch(`${API}/contracts/${id}`, { method: "DELETE" });
    load();
  }

  const byFw: Record<string, any[]> = {};
  for (const fw of activeFrameworks) {
    byFw[fw] = allContracts.filter(c => c.framework === fw);
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div className="aigov-page-header" style={{ marginBottom: 0 }}>
          <h1>Contracts</h1>
          <p>{allContracts.length} contract types across {activeFrameworks.length} frameworks</p>
        </div>
        <NavLink to="/aigov/contracts/seed" className="btn btn-secondary btn-sm"><FileText size={14} /> Seed Templates</NavLink>
      </div>

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search contracts..." />
        <FilterSelect value={filterFw} onChange={setFilterFw} options={AI_GOV_FRAMEWORKS.filter(fw => activeFrameworks.includes(fw.key)).map(fw => ({ value: fw.key, label: fw.label }))} placeholder="All frameworks" />
        <FilterSelect value={filterStatus} onChange={setFilterStatus} options={[
          { value: "not_started", label: "Not Started" },
          { value: "in_progress", label: "In Progress" },
          { value: "signed", label: "Signed" },
          { value: "expired", label: "Expired" },
        ]} placeholder="All status" />
      </FilterBar>

      {loading ? (
        <p className="muted">Loading...</p>
      ) : allContracts.length === 0 ? (
        <div className="panel" style={{ textAlign: "center", padding: "2rem" }}>
          <p className="muted">No contract records yet. Use "Seed Templates" to populate the 13 contract types from framework catalogs.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {AI_GOV_FRAMEWORKS.filter(fw => activeFrameworks.includes(fw.key)).map(fw => {
            const contracts = byFw[fw.key].filter(c => {
              if (filterStatus && c.status !== filterStatus) return false;
              if (search) {
                const q = search.toLowerCase();
                if (!c.name?.toLowerCase().includes(q) && !c.counterparty?.toLowerCase().includes(q)) return false;
              }
              return true;
            });
            if (filterFw && fw.key !== filterFw) return null;
            if (contracts.length === 0) return null;
            const signed = contracts.filter(c => c.status === "signed").length;
            return (
              <div key={fw.key}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <h3 style={{ margin: 0, color: fw.color }}>{fw.label}</h3>
                  <span className="muted" style={{ fontSize: 12 }}>{signed}/{contracts.length} signed</span>
                </div>
                <div className="panel-stack" style={{ gap: 6 }}>
                  {contracts.map(c => {
                    const sc = STATUS_COLORS[c.status] || STATUS_COLORS.not_started;
                    return (
                      <div key={c.id} className="panel" style={{ padding: 10, borderLeft: `3px solid ${sc.split(",")[1] || "var(--muted)"}` }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
                            <FileText size={14} style={{ color: fw.color }} />
                            <div style={{ flex: 1 }}>
                              <NavLink to={`/aigov/contracts/${c.id}`} style={{ fontWeight: 600, textDecoration: "none", color: "inherit", fontSize: 14 }}>{c.name}</NavLink>
                              {c.counterparty && <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>{c.counterparty}</span>}
                            </div>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: sc.split(",")[0], color: sc.split(",")[1] }}>{c.status?.replace(/_/g, " ")}</span>
                            {c.expiry_date && <span className="muted" style={{ fontSize: 11 }}>Exp: {c.expiry_date}</span>}
                            <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(c.id)}><Trash2 size={12} /></button>
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
