import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { Plus, Search, ExternalLink, Trash2, Download, Clock } from "lucide-react";
import { FilterBar, FilterSearch, FilterSelect, FilterCheckbox } from "@shared/filter-bar";

const API = "/api/ai-governance";

function actorRole(sys: any): { label: string; color: string } | null {
  if (sys.is_fine_tuned) return { label: "Provider obligations (fine-tuned)", color: "var(--warning)" };
  if (sys.foundation_model) return { label: "Deployer (vendor model)", color: "var(--info)" };
  return null;
}

export function SystemsListPage() {
  const [allSystems, setAllSystems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [filterTier, setFilterTier] = useState("");
  const [showArchived, setShowArchived] = useState(false);

  function load() {
    setLoading(true);
    fetch(`${API}/systems`).then((r) => r.json()).then((d) => setAllSystems(d.systems || [])).finally(() => setLoading(false));
  }
  useEffect(() => { load(); }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this system?")) return;
    await fetch(`${API}/systems/${id}`, { method: "DELETE" }); load();
  }
  async function handleBulk(action: string) {
    const ids = allSystems.filter((s: any) => s._selected).map((s: any) => s.id);
    if (!ids.length) return;
    await fetch(`${API}/systems/bulk`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ids, action }) });
    load();
  }
  function toggleSelect(id: string) {
    setAllSystems((prev) => prev.map((s) => (s.id === id ? { ...s, _selected: !s._selected } : s)));
  }

  const filtered = allSystems.filter((s) => {
    if (!showArchived && s.archived) return false;
    if (filterStatus && s.deployment_status !== filterStatus) return false;
    if (filterTier && s.risk_classification !== filterTier) return false;
    if (search && !s.name?.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });
  const selected = allSystems.filter((s: any) => s._selected);

  const tierColors: Record<string, string> = {
    unacceptable: "var(--danger-soft),var(--danger)", high: "var(--danger-soft),var(--danger)",
    limited: "var(--warning-soft),var(--warning)", minimal: "var(--success-soft),var(--success)",
    gpa: "var(--info-soft),var(--info)", unclassified: "var(--surface),var(--muted)",
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
        <div className="aigov-page-header" style={{ marginBottom: 0 }}>
          <h1>AI Systems</h1>
          <p>{filtered.length} of {allSystems.length} systems</p>
        </div>
        <div className="controls-toolbar-options" style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => window.open(`${API}/systems/export/csv`)}><Download size={14} /> CSV</button>
          <button className="btn btn-secondary btn-sm" onClick={() => fetch(`${API}/seed`, { method: "POST" }).then(() => window.location.reload())}>Seed</button>
          <NavLink to="/aigov/systems/new" className="btn btn-primary"><Plus size={14} /> Register System</NavLink>
        </div>
      </div>

      {selected.length > 0 && (
        <div className="panel" style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", marginBottom: 12, background: "var(--primary-soft)" }}>
          <span style={{ fontSize: 12 }}>{selected.length} selected</span>
          <button className="btn btn-secondary btn-sm" onClick={() => handleBulk("archive")}>Archive</button>
          <button className="btn btn-secondary btn-sm" onClick={() => handleBulk("unarchive")}>Restore</button>
          <button className="btn btn-secondary btn-sm" onClick={() => handleBulk("delete")} style={{ color: "var(--danger)" }}>Delete</button>
        </div>
      )}

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} />
        <FilterSelect value={filterStatus} onChange={setFilterStatus} options={[
          { value: "development", label: "Development" },
          { value: "staging", label: "Staging" },
          { value: "production", label: "Production" },
          { value: "deprecated", label: "Deprecated" },
        ]} placeholder="All status" />
        <FilterSelect value={filterTier} onChange={setFilterTier} options={[
          { value: "unacceptable", label: "Unacceptable" },
          { value: "high", label: "High" },
          { value: "limited", label: "Limited" },
          { value: "minimal", label: "Minimal" },
          { value: "gpa", label: "GPA" },
          { value: "unclassified", label: "Unclassified" },
        ]} placeholder="All tiers" />
        <FilterCheckbox label="Show archived" checked={showArchived} onChange={setShowArchived} />
      </FilterBar>

      {loading ? <p className="muted" style={{ fontSize: 13 }}>Loading...</p> : filtered.length === 0 ? (
        <div className="aigov-empty">
          <Search size={32} />
          <h3>No systems found</h3>
          <p>Try adjusting your filters or register a new system.</p>
          <NavLink to="/aigov/systems/new" className="btn btn-primary"><Plus size={14} /> Register System</NavLink>
        </div>
      ) : (
        <div className="panel" style={{ padding: 0, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                <th style={{ padding: "0.75rem 0.5rem", width: 30 }}></th>
                <th style={{ padding: "0.75rem 0.5rem" }}>Name</th>
                <th style={{ padding: "0.75rem 0.5rem" }}>Risk Tier</th>
                <th style={{ padding: "0.75rem 0.5rem" }}>Status</th>
                <th style={{ padding: "0.75rem 0.5rem" }}>Owner</th>
                <th style={{ padding: "0.75rem 0.5rem" }}>Tags</th>
                <th style={{ padding: "0.75rem 0.5rem", width: 60 }}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((sys) => {
                const [bg, color] = (tierColors[sys.risk_classification] || "var(--surface),var(--muted)").split(",");
                const isOverdue = sys.review_date && new Date(sys.review_date) < new Date();
                return (
                  <tr key={sys.id} style={{ borderBottom: "1px solid var(--border)", opacity: sys.archived ? 0.6 : 1 }}>
                    <td style={{ padding: "0.5rem" }}>
                      <input type="checkbox" checked={!!sys._selected} onChange={() => toggleSelect(sys.id)} style={{ width: "auto" }} />
                    </td>
                    <td style={{ padding: "0.5rem" }}>
                      <NavLink to={`/aigov/systems/${sys.id}`} style={{ fontWeight: 500, color: "var(--text)", textDecoration: "none" }}>{sys.name}</NavLink>
                      {sys.archived && <span className="badge neutral" style={{ marginLeft: 4 }}>Archived</span>}
                      {isOverdue && <span style={{ marginLeft: 4, fontSize: 11, color: "var(--danger)" }}><Clock size={10} style={{ display: "inline" }} /> Overdue</span>}
                      {actorRole(sys) && (
                        <span className="badge" title="EU AI Act Art. 25 — substantial modification flips deployer to provider obligations" style={{ marginLeft: 4, fontSize: 10, background: "var(--border-subtle)", color: actorRole(sys)!.color }}>{actorRole(sys)!.label}</span>
                      )}
                    </td>
                    <td style={{ padding: "0.5rem" }}>
                      <span className="badge" style={{ background: bg, color, fontWeight: 600 }}>{sys.risk_classification}</span>
                    </td>
                    <td style={{ padding: "0.5rem" }}><span className="muted" style={{ fontSize: 12 }}>{sys.deployment_status}</span></td>
                    <td style={{ padding: "0.5rem" }}><span className="muted" style={{ fontSize: 12 }}>{sys.owner || "—"}</span></td>
                    <td style={{ padding: "0.5rem" }}>
                      <div style={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
                        {(sys.tags || []).slice(0, 3).map((t: string) => (
                          <span key={t} style={{ fontSize: 10, background: "var(--primary-soft)", color: "var(--primary)", padding: "1px 5px", borderRadius: 3 }}>{t}</span>
                        ))}
                      </div>
                    </td>
                    <td style={{ padding: "0.5rem", whiteSpace: "nowrap" }}>
                      <NavLink to={`/aigov/systems/${sys.id}`} style={{ color: "var(--muted)", marginRight: 4 }}><ExternalLink size={14} /></NavLink>
                      <button className="icon-btn icon-btn--danger" onClick={() => handleDelete(sys.id)}><Trash2 size={14} /></button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
