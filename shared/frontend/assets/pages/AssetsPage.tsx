import { useEffect, useState, useRef } from "react";
import { assetsApi } from "../api";
import type { AssetItem } from "../types";
import { FilterSearch } from "@shared/filter-bar";

const ASSET_TYPES = ["IT_INFRASTRUCTURE", "SAAS", "AI_MODEL", "DATASET", "CLOUD", "NETWORK", "OTHER"];

export default function AssetsPage() {
  const [assets, setAssets] = useState<AssetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");
  const importRef = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<AssetItem>>({});
  const [sort, setSort] = useState<{ col: string; dir: "asc" | "desc" }>({ col: "name", dir: "asc" });

  const load = () =>
    assetsApi.list()
      .then((d) => setAssets(d.assets || []))
      .catch(() => setMsg("Failed to load assets"))
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleImport = async (file: File) => {
    try {
      const d = await assetsApi.importCsv(file);
      setMsg(`Imported ${d.imported} asset(s).`);
      await load();
    } catch (e) { setMsg(String(e)); }
    if (importRef.current) importRef.current.value = "";
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this asset?")) return;
    try { await assetsApi.delete(id); await load(); } catch (e) { setMsg(String(e)); }
  };

  const startEdit = (a: AssetItem) => {
    setEditingId(a.id);
    setEditForm({ name: a.name, type: a.type, owner: a.owner, description: a.description, environment: a.environment, data_classification: a.data_classification, location: a.location, handles_cui: a.handles_cui, criticality: a.criticality });
  };

  const saveEdit = async () => {
    if (!editingId) return;
    try { await assetsApi.update(editingId, editForm); setEditingId(null); await load(); } catch (e) { setMsg(String(e)); }
  };

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", type: "", owner: "", description: "", environment: "", data_classification: "", location: "", handles_cui: false, criticality: "" });

  const handleCreate = async () => {
    if (!form.name.trim()) return;
    try {
      await assetsApi.create(form);
      setShowForm(false);
      setForm({ name: "", type: "", owner: "", description: "", environment: "", data_classification: "", location: "", handles_cui: false, criticality: "" });
      await load();
    } catch (e) { setMsg(String(e)); }
  };

  const filtered = assets.filter((a) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return a.name.toLowerCase().includes(q) || a.type.toLowerCase().includes(q) || a.owner.toLowerCase().includes(q) || a.environment.toLowerCase().includes(q);
  });

  const toggleSort = (col: string) => {
    setSort((prev) => ({ col, dir: prev.col === col && prev.dir === "asc" ? "desc" : "asc" }));
  };

  const sorted = [...filtered].sort((a, b) => {
    if (sort.col === "criticality") {
      const order: Record<string, number> = { "": 0, Low: 1, Medium: 2, High: 3, Critical: 4 };
      const va = order[a.criticality] ?? 0;
      const vb = order[b.criticality] ?? 0;
      return sort.dir === "asc" ? va - vb : vb - va;
    }
    if (sort.col === "handles_cui") {
      const va = a.handles_cui ? 1 : 0;
      const vb = b.handles_cui ? 1 : 0;
      return sort.dir === "asc" ? va - vb : vb - va;
    }
    const va = ((a as any)[sort.col] ?? "").toLowerCase();
    const vb = ((b as any)[sort.col] ?? "").toLowerCase();
    const cmp = va.localeCompare(vb);
    return sort.dir === "asc" ? cmp : -cmp;
  });

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Assets</h2>
        <p className="muted">{assets.length} assets</p>
      </div>

      {msg && <div className="banner info" style={{ marginBottom: 12 }}>{msg}<button className="btn-link" style={{ float: "right" }} onClick={() => setMsg("")}>×</button></div>}

      <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap", alignItems: "center" }}>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "+ New Asset"}</button>
        <button className="btn btn-ghost btn-sm" onClick={() => importRef.current?.click()}>Import CSV</button>
        <a className="btn btn-ghost btn-sm" href={assetsApi.exportCsvUrl()}>Export CSV</a>
        <input ref={importRef} type="file" accept=".csv" hidden onChange={(e) => e.target.files?.[0] && handleImport(e.target.files[0])} />
        <FilterSearch value={search} onChange={setSearch} placeholder="Search assets..." />
      </div>

      {showForm && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Name *</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., AWS Production Account" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Type</label><select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}><option value="">-- Select --</option>{ASSET_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}</select></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Owner</label><input value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} placeholder="team@company.com" /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief description" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Environment</label><input value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })} placeholder="production, staging, dev" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Data Classification</label><input value={form.data_classification} onChange={(e) => setForm({ ...form, data_classification: e.target.value })} placeholder="public, internal, confidential" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Location</label><input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="us-east-1, on-prem" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Criticality</label><select value={form.criticality} onChange={(e) => setForm({ ...form, criticality: e.target.value })}><option value="">--</option><option value="Low">Low</option><option value="Medium">Medium</option><option value="High">High</option><option value="Critical">Critical</option></select></div>
            <div className="span-2"><label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, cursor: "pointer" }}><input type="checkbox" checked={form.handles_cui} onChange={(e) => setForm({ ...form, handles_cui: e.target.checked })} style={{ width: "auto" }} /> Handles CUI</label></div>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleCreate}>Create Asset</button>
        </div>
      )}

      {loading ? (
        <p className="muted">Loading...</p>
      ) : filtered.length === 0 ? (
        <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>{assets.length === 0 ? "No assets yet." : "No assets match your search."}</p></div></div>
      ) : (
        <div className="panel">
          <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                  {(["name", "type", "owner", "environment", "criticality", "handles_cui"] as const).map((col) => (
                    <th key={col} style={{ padding: "0.75rem 0.5rem", cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort(col)}>
                      {col === "handles_cui" ? "CUI" : col.charAt(0).toUpperCase() + col.slice(1)} {sort.col === col ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                    </th>
                  ))}
                  <th style={{ padding: "0.75rem 0.5rem" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((a) => (
                  <tr key={a.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    {editingId === a.id ? (
                      <td colSpan={7} style={{ padding: "0.5rem" }}>
                        <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
                          <input value={editForm.name || ""} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} style={{ width: 120, fontSize: 12 }} />
                          <select value={editForm.type || ""} onChange={(e) => setEditForm({ ...editForm, type: e.target.value })} style={{ width: 110, fontSize: 12 }}>
                            <option value="">--</option>
                            {ASSET_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                          </select>
                          <input value={editForm.owner || ""} onChange={(e) => setEditForm({ ...editForm, owner: e.target.value })} style={{ width: 100, fontSize: 12 }} />
                          <input value={editForm.environment || ""} onChange={(e) => setEditForm({ ...editForm, environment: e.target.value })} style={{ width: 90, fontSize: 12 }} />
                          <select value={editForm.criticality || ""} onChange={(e) => setEditForm({ ...editForm, criticality: e.target.value })} style={{ width: 90, fontSize: 12 }}>
                            <option value="">--</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                            <option value="Critical">Critical</option>
                          </select>
                          <label style={{ fontSize: 11, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 3 }}>
                            <input type="checkbox" checked={editForm.handles_cui || false} onChange={(e) => setEditForm({ ...editForm, handles_cui: e.target.checked })} style={{ width: "auto" }} /> CUI
                          </label>
                          <input value={editForm.description || ""} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} placeholder="Description" style={{ width: 120, fontSize: 12 }} />
                          <button className="btn btn-primary btn-sm" style={{ fontSize: 11 }} onClick={saveEdit}>Save</button>
                          <button className="btn btn-ghost btn-sm" style={{ fontSize: 11 }} onClick={() => setEditingId(null)}>Cancel</button>
                        </div>
                      </td>
                    ) : (
                      <>
                        <td style={{ padding: "0.75rem 0.5rem", fontWeight: 500 }}>{a.name}</td>
                        <td style={{ padding: "0.75rem 0.5rem" }}>{a.type || "—"}</td>
                        <td style={{ padding: "0.75rem 0.5rem", color: "var(--muted)" }}>{a.owner || "—"}</td>
                        <td style={{ padding: "0.75rem 0.5rem" }}>{a.environment || "—"}</td>
                        <td style={{ padding: "0.75rem 0.5rem" }}>{a.criticality ? <span className="badge badge-muted">{a.criticality}</span> : "—"}</td>
                        <td style={{ padding: "0.75rem 0.5rem" }}>{a.handles_cui ? <span className="badge badge-danger">CUI</span> : "—"}</td>
                        <td style={{ padding: "0.75rem 0.5rem" }}>
                          <div style={{ display: "flex", gap: 4 }}>
                            <button className="btn btn-sm btn-ghost" style={{ fontSize: 11 }} onClick={() => startEdit(a)}>Edit</button>
                            <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)", fontSize: 11 }} onClick={() => handleDelete(a.id)}>Delete</button>
                          </div>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
