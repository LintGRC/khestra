import { useEffect, useState } from "react";
import { personnelApi } from "../api";
import type { PersonItem } from "../types";
import ImportProvidersDialog from "../components/ImportProvidersDialog";
import { FilterBar, FilterSearch } from "@shared/filter-bar";

function statusBadge(status: string) {
  const m: Record<string, string> = {
    active: "badge-success", inactive: "badge-muted", invited: "badge-warning",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status}</span>;
}

export default function PersonnelDashboard() {
  const [people, setPeople] = useState<PersonItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInvite, setShowInvite] = useState(false);
  const [inviteName, setInviteName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("");
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ name: "", email: "", role: "", status: "", department: "", mfa_status: "", is_privileged: false, phone: "", location: "", manager: "", external_id: "" });

  const load = async () => {
    try {
      const data = await personnelApi.list();
      setPeople(data.personnel || []);
    } catch { setError("Failed to load personnel."); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const startEdit = (p: PersonItem) => {
    setEditingId(p.id);
    setEditForm({ name: p.name, email: p.email, role: p.role, status: p.status, department: p.department || "", mfa_status: p.mfa_status || "", is_privileged: p.is_privileged || false, phone: p.phone || "", location: p.location || "", manager: p.manager || "", external_id: p.external_id || "" });
  };

  const saveEdit = async () => {
    if (!editingId) return;
    try { await personnelApi.update(editingId, editForm); setEditingId(null); await load(); } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this person from the team?")) return;
    try { await personnelApi.delete(id); await load(); } catch { /* ignore */ }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteName.trim() || !inviteEmail.trim()) return;
    try {
      await personnelApi.create({ name: inviteName.trim(), email: inviteEmail.trim(), role: inviteRole.trim() });
      setShowInvite(false);
      setInviteName(""); setInviteEmail(""); setInviteRole("");
      await load();
    } catch { /* ignore */ }
  };

  const filtered = people.filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return p.name.toLowerCase().includes(q) || p.email.toLowerCase().includes(q) || p.role.toLowerCase().includes(q);
  });

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;
  if (error) return <div className="page-stack"><div className="banner error">{error}</div></div>;

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Team</h2>
          <p className="muted">{people.length} members · {people.filter((p) => p.status === "active").length} active</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowImportDialog(true)}>Import</button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowInvite(true)}>+ Invite Member</button>
        </div>
      </div>

      {showInvite && (
        <div className="panel" style={{ marginBottom: "1rem" }}>
          <div className="panel-header"><h3>Invite Team Member</h3></div>
          <div className="panel-body">
            <form onSubmit={handleInvite} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <input placeholder="Name" value={inviteName} onChange={(e) => setInviteName(e.target.value)} required />
              <input type="email" placeholder="Email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} required />
              <input placeholder="Role (optional)" value={inviteRole} onChange={(e) => setInviteRole(e.target.value)} />
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button className="btn btn-primary btn-sm" type="submit">Invite</button>
                <button className="btn btn-ghost btn-sm" type="button" onClick={() => setShowInvite(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {people.length > 0 && (
        <FilterBar>
          <FilterSearch value={search} onChange={setSearch} placeholder="Search team members..." />
        </FilterBar>
      )}

      {filtered.length === 0 ? (
        <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>{people.length === 0 ? "No team members yet." : "No members match your search."}</p></div></div>
      ) : (
        <div className="panel">
          <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--border)", textAlign: "left" }}>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Name</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Email</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Role</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Department</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>MFA</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Privileged</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Status</th>
                  <th style={{ padding: "10px 12px", fontWeight: 600 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((p) => (
                  <tr key={p.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    {editingId === p.id ? (
                      <td colSpan={8} style={{ padding: "8px 12px" }}>
                        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                          <input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} style={{ width: 140, fontSize: 12 }} />
                          <input value={editForm.email} onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} style={{ width: 160, fontSize: 12 }} />
                          <input value={editForm.role} onChange={(e) => setEditForm({ ...editForm, role: e.target.value })} style={{ width: 100, fontSize: 12 }} />
                          <input value={editForm.phone} onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })} placeholder="Phone" style={{ width: 110, fontSize: 12 }} />
                          <input value={editForm.location} onChange={(e) => setEditForm({ ...editForm, location: e.target.value })} placeholder="Location" style={{ width: 110, fontSize: 12 }} />
                          <select value={editForm.mfa_status} onChange={(e) => setEditForm({ ...editForm, mfa_status: e.target.value })} style={{ width: 90, fontSize: 12 }}>
                            <option value="">MFA: —</option>
                            <option value="enabled">Enabled</option>
                            <option value="disabled">Disabled</option>
                            <option value="exempt">Exempt</option>
                          </select>
                          <label style={{ fontSize: 11, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 3 }}>
                            <input type="checkbox" checked={editForm.is_privileged || false} onChange={(e) => setEditForm({ ...editForm, is_privileged: e.target.checked })} style={{ width: "auto" }} /> Priv
                          </label>
                          <input value={editForm.manager} onChange={(e) => setEditForm({ ...editForm, manager: e.target.value })} placeholder="Manager" style={{ width: 120, fontSize: 12 }} />
                          <input value={editForm.external_id} onChange={(e) => setEditForm({ ...editForm, external_id: e.target.value })} placeholder="Ext ID" style={{ width: 100, fontSize: 12 }} />
                          <select value={editForm.status} onChange={(e) => setEditForm({ ...editForm, status: e.target.value })} disabled={!!p.external_id} style={{ width: 90, fontSize: 12 }}>
                            <option value="active">Active</option>
                            <option value="invited">Invited</option>
                            <option value="inactive">Inactive</option>
                          </select>
                          {p.external_id && <span style={{ fontSize: 10, color: "var(--muted)", whiteSpace: "nowrap" }}>(synced)</span>}
                          <button className="btn btn-primary btn-sm" style={{ fontSize: 11 }} onClick={saveEdit}>Save</button>
                          <button className="btn btn-ghost btn-sm" style={{ fontSize: 11 }} onClick={() => setEditingId(null)}>Cancel</button>
                        </div>
                      </td>
                    ) : (
                      <>
                        <td style={{ padding: "10px 12px", fontWeight: 500 }}>{p.name}</td>
                        <td style={{ padding: "10px 12px", color: "var(--muted)" }}>{p.email}</td>
                        <td style={{ padding: "10px 12px" }}>{p.role || "-"}</td>
                        <td style={{ padding: "10px 12px", color: "var(--muted)", fontSize: "0.8rem" }}>{p.department || "-"}</td>
                        <td style={{ padding: "10px 12px" }}>
                          {p.mfa_status === "enabled" ? <span className="badge badge-success">Enabled</span>
                           : p.mfa_status === "disabled" ? <span className="badge badge-danger">Disabled</span>
                           : p.mfa_status === "exempt" ? <span className="badge badge-warning">Exempt</span>
                            : <>—</>}
                        </td>
                        <td style={{ padding: "10px 12px" }}>
                          {p.is_privileged ? <span className="badge badge-warning">Privileged</span> : "—"}
                        </td>
                        <td style={{ padding: "10px 12px" }}>{statusBadge(p.status)}</td>
                        <td style={{ padding: "10px 12px" }}>
                          <div style={{ display: "flex", gap: 4 }}>
                            <button className="btn btn-sm btn-ghost" style={{ fontSize: 11 }} onClick={() => startEdit(p)}>Edit</button>
                            <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)", fontSize: 11 }} onClick={() => handleDelete(p.id)}>Remove</button>
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
      {showImportDialog && <ImportProvidersDialog onClose={() => { setShowImportDialog(false); load(); }} />}
    </div>
  );
}
