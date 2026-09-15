import { useEffect, useState } from "react";
import { CheckCircle, Circle, AlertTriangle, Plus, Trash2 } from "lucide-react";
import { FilterBar, FilterButtons } from "@shared/filter-bar";

const ROLE_LABELS: Record<string, string> = {
  provider: "Provider", deployer: "Deployer", operator: "Operator",
  reviewer: "Reviewer", risk_owner: "Risk Owner", provider_repr: "Provider Rep.",
};

const ROLE_COLORS: Record<string, string> = {
  provider: "var(--primary)", deployer: "var(--info)", operator: "var(--warning)",
  reviewer: "var(--success)", risk_owner: "var(--danger)", provider_repr: "var(--muted)",
};

type CompetenceRecord = {
  id: string;
  person_name: string;
  role: string;
  qualification: string;
  provider: string;
  date_completed: string;
  expiry_date: string;
  status: string;
  notes: string;
};

type CompetenceGap = {
  role: string;
  qualification: string;
  framework: string;
  ref: string;
  description: string;
};

type RoleRequirement = {
  qualification: string;
  framework: string;
  ref: string;
  description: string;
};

export function CompetencePage() {
  const [records, setRecords] = useState<CompetenceRecord[]>([]);
  const [roleReqs, setRoleReqs] = useState<Record<string, RoleRequirement[]>>({});
  const [gaps, setGaps] = useState<CompetenceGap[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterRole, setFilterRole] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ person_name: "", role: "deployer", qualification: "", provider: "", date_completed: "", expiry_date: "", notes: "" });
  const [tab, setTab] = useState<"matrix" | "gaps" | "requirements">("matrix");

  const API = "/api/ai-governance";

  async function loadData() {
    const [recRes, rolesRes, gapsRes] = await Promise.all([
      fetch(`${API}/competence`).then(r => r.json()).catch(() => ({ competence: [] })),
      fetch(`${API}/competence/roles`).then(r => r.json()).catch(() => ({ roles: {} })),
      fetch(`${API}/competence/gaps`).then(r => r.json()).catch(() => ({ gaps: [] })),
    ]);
    setRecords(recRes.competence || []);
    setRoleReqs(rolesRes.roles || {});
    setGaps(gapsRes.gaps || []);
    setLoading(false);
  }

  useEffect(() => { loadData(); }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await fetch(`${API}/competence`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ person_name: "", role: "deployer", qualification: "", provider: "", date_completed: "", expiry_date: "", notes: "" });
    setShowForm(false);
    loadData();
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this competence record?")) return;
    await fetch(`${API}/competence/${id}`, { method: "DELETE" });
    loadData();
  }

  const roles = Object.keys(roleReqs);
  const filtered = filterRole ? records.filter(r => r.role === filterRole) : records;
  const people = [...new Set(records.map(r => r.person_name))];
  const totalCurrent = records.filter(r => r.status === "current").length;
  const totalExpiring = records.filter(r => r.status === "expiring").length;
  const totalExpired = records.filter(r => r.status === "expired").length;

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ margin: 0 }}>AI Competence &amp; Certification</h1>
          <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>Role-based competence tracking across all frameworks</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>
          <Plus size={14} /> {showForm ? "Cancel" : "Add Record"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <h4 style={{ margin: "0 0 12px" }}>New Competence Record</h4>
          <div className="form-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
            <div><label className="muted" style={{ fontSize: 11 }}>Person Name *</label><input value={form.person_name} onChange={e => setForm({ ...form, person_name: e.target.value })} required /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Role *</label>
              <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} required>
                {Object.entries(ROLE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div><label className="muted" style={{ fontSize: 11 }}>Qualification *</label>
              <select value={form.qualification} onChange={e => setForm({ ...form, qualification: e.target.value })} required>
                <option value="">Select...</option>
                {[...new Set(Object.values(roleReqs).flat().map(r => r.qualification))].map(q => <option key={q} value={q}>{q}</option>)}
              </select>
            </div>
            <div><label className="muted" style={{ fontSize: 11 }}>Provider</label><input value={form.provider} onChange={e => setForm({ ...form, provider: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Date Completed *</label><input type="date" value={form.date_completed} onChange={e => setForm({ ...form, date_completed: e.target.value })} required /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Expiry Date</label><input type="date" value={form.expiry_date} onChange={e => setForm({ ...form, expiry_date: e.target.value })} /></div>
            <div style={{ gridColumn: "1 / -1" }}><label className="muted" style={{ fontSize: 11 }}>Notes</label><textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} rows={2} /></div>
          </div>
          <button type="submit" className="btn btn-primary btn-sm" style={{ marginTop: 12 }}>Save Record</button>
        </form>
      )}

      <div className="panel-stack" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{records.length}</div>
          <div className="muted" style={{ fontSize: 11 }}>Total Certifications</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: "var(--success)" }}>{totalCurrent}</div>
          <div className="muted" style={{ fontSize: 11 }}>Current</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: totalExpiring > 0 ? "var(--warning)" : "var(--text)" }}>{totalExpiring}</div>
          <div className="muted" style={{ fontSize: 11 }}>Expiring</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: totalExpired > 0 ? "var(--danger)" : "var(--text)" }}>{totalExpired}</div>
          <div className="muted" style={{ fontSize: 11 }}>Expired</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{people.length}</div>
          <div className="muted" style={{ fontSize: 11 }}>Personnel Tracked</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: gaps.length > 0 ? "var(--danger)" : "var(--success)" }}>{gaps.length}</div>
          <div className="muted" style={{ fontSize: 11 }}>Competence Gaps</div>
        </div>
      </div>

      <div className="aigov-tabs" style={{ marginBottom: 12 }}>
        <button className={`aigov-tab${tab === "matrix" ? " aigov-tab--active" : ""}`} onClick={() => setTab("matrix")}>
                    Competence Matrix
        </button>
        <button className={`aigov-tab${tab === "gaps" ? " aigov-tab--active" : ""}`} onClick={() => setTab("gaps")}>
                    Gap Analysis ({gaps.length})
        </button>
        <button className={`aigov-tab${tab === "requirements" ? " aigov-tab--active" : ""}`} onClick={() => setTab("requirements")}>
                    Required by Role
        </button>
      </div>

      {loading && <p className="muted" style={{ padding: 16 }}>Loading...</p>}

      {tab === "matrix" && !loading && (
        <div>
          <FilterBar>
            <FilterButtons
              label="Filter by role:"
              items={[
                { key: "", label: "All" },
                ...roles.map(r => ({
                  key: r,
                  label: ROLE_LABELS[r] || r,
                  color: ROLE_COLORS[r],
                })),
              ]}
              active={filterRole}
              onChange={setFilterRole}
            />
          </FilterBar>

          <div className="panel" style={{ padding: 0, overflowX: "auto" }}>
            <table className="table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--surface-secondary, var(--surface))" }}>
                  <th style={{ padding: "8px 12px", textAlign: "left", position: "sticky", left: 0, background: "var(--surface)" }}>Person</th>
                  <th style={{ padding: "8px 12px", textAlign: "left" }}>Role</th>
                  <th style={{ padding: "8px 12px", textAlign: "left" }}>Qualification</th>
                  <th style={{ padding: "8px 12px", textAlign: "center" }}>Completed</th>
                  <th style={{ padding: "8px 12px", textAlign: "center" }}>Expires</th>
                  <th style={{ padding: "8px 12px", textAlign: "center" }}>Status</th>
                  <th style={{ padding: "8px 12px", textAlign: "right" }} />
                </tr>
              </thead>
              <tbody>
                {filtered.map(r => {
                  const isExpired = r.expiry_date && r.expiry_date < new Date().toISOString().slice(0, 10);
                  const isExpiring = r.expiry_date && !isExpired && r.expiry_date < new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
                  const status = isExpired ? "expired" : isExpiring ? "expiring" : r.status;
                  return (
                    <tr key={r.id} style={{ borderBottom: "1px solid var(--border-subtle)", opacity: status === "expired" ? 0.6 : 1 }}>
                      <td style={{ padding: "8px 12px", fontWeight: 500 }}>{r.person_name}</td>
                      <td style={{ padding: "8px 12px" }}>
                        <span className="badge" style={{ background: ROLE_COLORS[r.role] + "18", color: ROLE_COLORS[r.role], fontSize: 10 }}>{ROLE_LABELS[r.role] || r.role}</span>
                      </td>
                      <td style={{ padding: "8px 12px" }}>{r.qualification}</td>
                      <td style={{ padding: "8px 12px", textAlign: "center", fontSize: 11, color: "var(--muted)" }}>{r.date_completed?.slice(0, 10)}</td>
                      <td style={{ padding: "8px 12px", textAlign: "center", fontSize: 11, color: status === "expired" ? "var(--danger)" : status === "expiring" ? "var(--warning)" : "var(--muted)" }}>
                        {r.expiry_date || "—"}
                      </td>
                      <td style={{ padding: "8px 12px", textAlign: "center" }}>
                        <span className="badge" style={{
                          background: status === "current" ? "var(--success-soft, #dcfce7)" : status === "expiring" ? "var(--warning-soft, #fef3c7)" : "var(--danger-soft, #fee2e2)",
                          color: status === "current" ? "var(--success)" : status === "expiring" ? "var(--warning)" : "var(--danger)",
                          fontSize: 10,
                        }}>{status}</span>
                      </td>
                      <td style={{ padding: "8px 12px", textAlign: "right" }}>
                        <button className="icon-btn icon-btn--danger" onClick={() => handleDelete(r.id)}><Trash2 size={12} /></button>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr><td colSpan={7} style={{ padding: 24, textAlign: "center" }} className="muted">No records found for this role.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "gaps" && !loading && (
        <div>
          <div className="panel" style={{ padding: 16, marginBottom: 12 }}>
            <p style={{ fontSize: 12, margin: 0 }}>
              {gaps.length === 0 ? (
                <><CheckCircle size={14} style={{ color: "var(--success)" }} /> All required competencies are covered by at least one person per role.</>
              ) : (
                <><AlertTriangle size={14} style={{ color: "var(--danger)" }} /> {gaps.length} missing competence{gaps.length > 1 ? "s" : ""} — no one has been recorded with these qualifications for the required role.</>
              )}
            </p>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {gaps.map((g, i) => (
              <div key={i} className="panel" style={{ padding: "10px 14px", borderLeft: "3px solid var(--danger)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <Circle size={14} style={{ color: "var(--danger)", flexShrink: 0 }} />
                      <span style={{ fontWeight: 600, fontSize: 13 }}>{g.qualification}</span>
                      <span className="badge" style={{ background: ROLE_COLORS[g.role] + "18", color: ROLE_COLORS[g.role], fontSize: 9 }}>{ROLE_LABELS[g.role] || g.role}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 3 }}>
                      {g.framework} ({g.ref}) — {g.description}
                    </div>
                  </div>
                  <button className="btn btn-sm btn-primary" onClick={() => {
                    setForm({ person_name: "", role: g.role, qualification: g.qualification, provider: "", date_completed: new Date().toISOString().slice(0, 10), expiry_date: "", notes: "" });
                    setShowForm(true);
                    setTab("matrix");
                  }} style={{ fontSize: 10, padding: "4px 8px", flexShrink: 0 }}>
                    <Plus size={12} /> Add
                  </button>
                </div>
              </div>
            ))}
            {gaps.length === 0 && (
              <div className="panel" style={{ padding: 24, textAlign: "center" }}><span className="muted">No competence gaps found.</span></div>
            )}
          </div>
        </div>
      )}

      {tab === "requirements" && !loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {roles.map(r => {
            const reqs = roleReqs[r] || [];
            return (
              <div key={r} className="panel" style={{ padding: 16 }}>
                <h4 style={{ margin: "0 0 8px", display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ width: 24, height: 24, borderRadius: 6, background: ROLE_COLORS[r] + "18", color: ROLE_COLORS[r], display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700 }}>{ROLE_LABELS[r]?.slice(0, 2)}</span>
                  {ROLE_LABELS[r] || r}
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {reqs.map((req, i) => {
                    const hasPerson = records.some(rec => rec.role === r && rec.qualification === req.qualification);
                    return (
                      <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 8px", borderRadius: 4, background: "var(--surface-secondary, var(--surface))" }}>
                        {hasPerson ? <CheckCircle size={14} style={{ color: "var(--success)", flexShrink: 0 }} /> : <Circle size={14} style={{ color: "var(--danger)", flexShrink: 0 }} />}
                        <div style={{ flex: 1 }}>
                          <span style={{ fontWeight: 500, fontSize: 12 }}>{req.qualification}</span>
                          <span className="muted" style={{ fontSize: 10, marginLeft: 8 }}>{req.framework} ({req.ref})</span>
                          <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>{req.description}</div>
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
