import { useEffect, useState } from "react";
import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { useAuth } from "@shared/authContext";

type AuthUser = { id: string; email: string; name: string; role: string; deactivated?: number };

async function authFetch(url: string, init?: RequestInit) {
  const headers = await authHeaders(init?.headers);
  if (!headers.has("Content-Type") && init?.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(apiUrl(url), { ...init, headers });
  if (res.status === 401) {
    localStorage.removeItem("khestra_auth_token");
    window.location.reload();
    throw new Error("Session expired");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail || res.statusText);
  }
  return res;
}

export default function UserManagementPage() {
  const { role: currentRole } = useAuth();
  const isAdmin = currentRole === "Compliance Manager" || currentRole === "Organization Admin";
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: "", name: "", password: "", role: "Executive" });
  const [actionError, setActionError] = useState("");
  const [sort, setSort] = useState<{ col: "name" | "email" | "role" | "status"; dir: "asc" | "desc" }>({ col: "name", dir: "asc" });

  const load = async () => {
    try {
      const res = await authFetch("/api/auth/users");
      const data = await res.json();
      setUsers(data.users || []);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (isAdmin) load(); else setLoading(false); }, [isAdmin]);

  if (!isAdmin) {
    return (
      <div className="page-stack">
        <div className="banner error">You need admin access to manage users.</div>
      </div>
    );
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError("");
    try {
      await authFetch("/api/auth/users", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setShowForm(false);
      setForm({ email: "", name: "", password: "", role: "Executive" });
      await load();
    } catch (err) {
      setActionError(String(err));
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await authFetch(`/api/auth/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ role: newRole }),
      });
      await load();
    } catch (err) {
      setActionError(String(err));
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm("Deactivate this user?")) return;
    try {
      await authFetch(`/api/auth/users/${userId}`, { method: "DELETE" });
      await load();
    } catch (err) {
      setActionError(String(err));
    }
  };

  const toggleSort = (col: typeof sort.col) => {
    setSort((prev) => ({ col, dir: prev.col === col && prev.dir === "asc" ? "desc" : "asc" }));
  };

  const sortedUsers = [...users].sort((a, b) => {
    if (sort.col === "status") {
      const va = a.deactivated ? 1 : 0;
      const vb = b.deactivated ? 1 : 0;
      return sort.dir === "asc" ? va - vb : vb - va;
    }
    const va = (a[sort.col] ?? "").toLowerCase();
    const vb = (b[sort.col] ?? "").toLowerCase();
    const cmp = va.localeCompare(vb);
    return sort.dir === "asc" ? cmp : -cmp;
  });

  const handleResetPassword = async (userId: string) => {
    const newPassword = prompt("Enter new password (min 8 characters):");
    if (!newPassword || newPassword.length < 8) return;
    if (!confirm("Reset password for this user?")) return;
    try {
      await authFetch(`/api/auth/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ password: newPassword }),
      });
      setActionError("");
    } catch (err) {
      setActionError(String(err));
    }
  };

  if (loading) return <div className="page-stack"><p className="muted">Loading users…</p></div>;
  if (error) return <div className="page-stack"><div className="banner error">{error}</div></div>;

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>User Management</h2>
          <p className="muted">{users.filter((u) => !u.deactivated).length} active users</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Add User"}
        </button>
      </div>

      {actionError && <div className="banner error">{actionError}</div>}

      {showForm && (
        <div className="panel" style={{ marginBottom: "1rem" }}>
          <div className="panel-header"><h3>Add User</h3></div>
          <div className="panel-body">
            <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              <input type="password" placeholder="Temporary password (min 8 chars)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8} />
              <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                <option value="Organization Admin">Organization Admin</option>
                <option value="Compliance Manager">Compliance Manager</option>
                <option value="Assessor">Assessor</option>
                <option value="Auditor">Auditor</option>
                <option value="Engineer">Contributor</option>
                <option value="Executive">Viewer</option>
              </select>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button className="btn btn-primary btn-sm" type="submit">Create User</button>
                <button className="btn btn-ghost btn-sm" type="button" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="panel">
        <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: "2px solid var(--border)", textAlign: "left" }}>
                {(["name", "email", "role", "status"] as const).map((col) => (
                  <th key={col} style={{ padding: "10px 12px", fontWeight: 600, cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort(col)}>
                    {col.charAt(0).toUpperCase() + col.slice(1)} {sort.col === col ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                  </th>
                ))}
                <th style={{ padding: "10px 12px", fontWeight: 600 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedUsers.map((u) => (
                <tr key={u.id} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "10px 12px", fontWeight: 500 }}>{u.name || "-"}</td>
                  <td style={{ padding: "10px 12px", color: "var(--muted)" }}>{u.email}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <select value={u.role} onChange={(e) => handleRoleChange(u.id, e.target.value)}>
                <option value="Organization Admin">Organization Admin</option>
                      <option value="Compliance Manager">Compliance Manager</option>
                      <option value="Assessor">Assessor</option>
                      <option value="Auditor">Auditor</option>
                      <option value="Engineer">Contributor</option>
                      <option value="Executive">Viewer</option>
                    </select>
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    {u.deactivated ? <span className="badge" style={{background: "var(--border-subtle)", color: "var(--muted)", border: "1px solid var(--border)"}}>Deactivated</span> : <span className="badge" style={{background: "var(--success-soft)", color: "var(--success)", border: "1px solid var(--success-border)"}}>Active</span>}
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    {!u.deactivated && (
                      <>
                        <button className="btn btn-sm btn-ghost" onClick={() => handleResetPassword(u.id)}>
                          Reset Password
                        </button>
                        <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(u.id)}>
                          Deactivate
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
