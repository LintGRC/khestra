import { useEffect, useState } from "react";
import { trainingApi } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import type { TrainingModule, TrainingAssignment, TrainingModuleUpdate, TrainingStats, TrainingAlerts } from "../types";
import { TRAINING_STATUSES } from "../types";
import { FilterBar, FilterSelect, FilterSearch, FilterCount } from "@shared/filter-bar";

type Person = { id: string; name: string; email: string };

const STATUS_LABELS: Record<string, string> = {
  assigned: "Assigned", in_progress: "In Progress", completed: "Completed",
  overdue: "Overdue", exempt: "Exempt",
};

function statusBadge(status: string) {
  const m: Record<string, string> = {
    assigned: "badge-muted", in_progress: "badge-warning",
    completed: "badge-success", overdue: "badge-danger", exempt: "badge-info",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{STATUS_LABELS[status] || status}</span>;
}

type Tab = "overview" | "modules" | "assignments";

export default function TrainingPage() {
  const [tab, setTab] = useState<Tab>("overview");

  // Dashboard state
  const [stats, setStats] = useState<TrainingStats | null>(null);
  const [alerts, setAlerts] = useState<TrainingAlerts | null>(null);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  // Modules state
  const [modules, setModules] = useState<TrainingModule[]>([]);
  const [modulesLoading, setModulesLoading] = useState(true);
  const [showNewModule, setShowNewModule] = useState(false);
  const [newModForm, setNewModForm] = useState({ title: "", description: "", category: "", renewal_period_days: 365, control_ids: [] as string[] });
  const [editModId, setEditModId] = useState<string | null>(null);
  const [editModForm, setEditModForm] = useState<TrainingModuleUpdate>({});
  const [savingModule, setSavingModule] = useState(false);

  // Bulk assign state
  const [assignModId, setAssignModId] = useState<string | null>(null);
  const [people, setPeople] = useState<Person[]>([]);
  const [selectedPersonIds, setSelectedPersonIds] = useState<Set<string>>(new Set());
  const [peopleSearch, setPeopleSearch] = useState("");
  const [assigning, setAssigning] = useState(false);

  // Assignments state
  const [assignments, setAssignments] = useState<TrainingAssignment[]>([]);
  const [assignmentsLoading, setAssignmentsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [moduleFilter, setModuleFilter] = useState("all");
  const [selectedAssignmentIds, setSelectedAssignmentIds] = useState<Set<string>>(new Set());
  const [bulkDate, setBulkDate] = useState("");
  const [bulkProcessing, setBulkProcessing] = useState(false);

  const loadDashboard = async () => {
    setDashboardLoading(true);
    try {
      const [s, a] = await Promise.all([
        trainingApi.stats(),
        trainingApi.alerts(),
      ]);
      setStats(s);
      setAlerts(a);
    } catch { /* ignore */ }
    finally { setDashboardLoading(false); }
  };

  const loadModules = async () => {
    setModulesLoading(true);
    try {
      const data = await trainingApi.listModules();
      setModules(data.modules || []);
    } catch { /* ignore */ }
    finally { setModulesLoading(false); }
  };

  const loadAssignments = async () => {
    setAssignmentsLoading(true);
    try {
      const params: Record<string, string> = {};
      if (moduleFilter !== "all") params.module_id = moduleFilter;
      if (statusFilter !== "all") params.status = statusFilter;
      const data = await trainingApi.listAssignments(params);
      setAssignments(data.assignments || []);
    } catch { /* ignore */ }
    finally { setAssignmentsLoading(false); }
  };

  const loadPeople = async () => {
    try {
      const res = await fetch(apiUrl("/api/personnel"));
      const data = await res.json();
      setPeople(data.personnel || []);
    } catch { setPeople([]); }
  };

  useEffect(() => { loadDashboard(); }, []);
  useEffect(() => { loadModules(); }, []);
  useEffect(() => { loadAssignments(); }, [moduleFilter, statusFilter]);
  useEffect(() => { if (assignModId) loadPeople(); }, [assignModId]);

  // ── Sync Assignments ──

  const handleSyncAssignments = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const res = await trainingApi.autoAssign();
      setSyncResult(`Created ${res.created} new assignments${res.error ? ` (${res.error})` : ""}.`);
      await Promise.all([loadDashboard(), loadAssignments()]);
    } catch { setSyncResult("Sync failed."); }
    finally { setSyncing(false); }
  };

  // ── Module CRUD ──

  const handleCreateModule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newModForm.title.trim()) return;
    setSavingModule(true);
    try {
      await trainingApi.createModule({
        title: newModForm.title,
        description: newModForm.description,
        category: newModForm.category,
        renewal_period_days: newModForm.renewal_period_days,
        control_ids: newModForm.control_ids.length > 0 ? newModForm.control_ids : undefined,
      });
      setNewModForm({ title: "", description: "", category: "", renewal_period_days: 365, control_ids: [] });
      setShowNewModule(false);
      await Promise.all([loadModules(), loadDashboard()]);
    } catch { /* ignore */ }
    finally { setSavingModule(false); }
  };

  const startEditModule = (m: TrainingModule) => {
    setEditModId(m.id);
    setEditModForm({
      title: m.title,
      description: m.description,
      category: m.category,
      is_required: m.is_required,
      renewal_period_days: m.renewal_period_days,
      control_ids: m.control_ids || [],
    });
  };

  const saveEditModule = async (id: string) => {
    setSavingModule(true);
    try {
      await trainingApi.updateModule(id, editModForm);
      setEditModId(null);
      setEditModForm({});
      await loadModules();
    } catch { /* ignore */ }
    finally { setSavingModule(false); }
  };

  const handleDeleteModule = async (id: string) => {
    if (!confirm("Delete this module and all its assignments?")) return;
    try {
      await trainingApi.deleteModule(id);
      await Promise.all([loadModules(), loadDashboard()]);
    } catch { /* ignore */ }
  };

  // ── Bulk Assign ──

  const togglePerson = (pid: string) => {
    setSelectedPersonIds((prev) => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid);
      else next.add(pid);
      return next;
    });
  };

  const handleBulkAssign = async () => {
    if (!assignModId || selectedPersonIds.size === 0) return;
    setAssigning(true);
    try {
      await trainingApi.bulkAssign({
        module_id: assignModId,
        person_ids: Array.from(selectedPersonIds),
        assigned_date: new Date().toISOString().slice(0, 10),
      });
      setAssignModId(null);
      setSelectedPersonIds(new Set());
      setPeopleSearch("");
      await Promise.all([loadAssignments(), loadDashboard()]);
    } catch { /* ignore */ }
    finally { setAssigning(false); }
  };

  // ── Assignment CRUD ──

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      const body: Record<string, string> = { status };
      if (status === "completed") {
        body.completion_date = new Date().toISOString().slice(0, 10);
      }
      await trainingApi.updateAssignment(id, body);
      await Promise.all([loadAssignments(), loadDashboard()]);
    } catch { /* ignore */ }
  };

  const handleBulkComplete = async () => {
    if (selectedAssignmentIds.size === 0 || !bulkDate) return;
    setBulkProcessing(true);
    try {
      await trainingApi.bulkComplete({
        assignment_ids: Array.from(selectedAssignmentIds),
        completion_date: bulkDate,
      });
      setSelectedAssignmentIds(new Set());
      setBulkDate("");
      await Promise.all([loadAssignments(), loadDashboard()]);
    } catch { /* ignore */ }
    finally { setBulkProcessing(false); }
  };

  const handleDeleteAssignment = async (id: string) => {
    if (!confirm("Delete this assignment?")) return;
    try {
      await trainingApi.deleteAssignment(id);
      await Promise.all([loadAssignments(), loadDashboard()]);
    } catch { /* ignore */ }
  };

  const handleLinkEvidence = async (id: string) => {
    const url = prompt("Upload certificate to Evidence Hub first, then paste the evidence item URL or ID:");
    if (!url || !url.trim()) return;
    try {
      await trainingApi.updateAssignment(id, { evidence_id: url.trim() });
      await loadAssignments();
    } catch { /* ignore */ }
  };

  const toggleAssignment = (aid: string) => {
    setSelectedAssignmentIds((prev) => {
      const next = new Set(prev);
      if (next.has(aid)) next.delete(aid);
      else next.add(aid);
      return next;
    });
  };

  const toggleAllAssignments = () => {
    if (selectedAssignmentIds.size === filteredAssignments.length) {
      setSelectedAssignmentIds(new Set());
    } else {
      setSelectedAssignmentIds(new Set(filteredAssignments.map((a) => a.id)));
    }
  };

  // ── Filtered data ──

  const filteredAssignments = assignments.filter((a) => {
    if (search) {
      const q = search.toLowerCase();
      if (!a.person_name.toLowerCase().includes(q) && !a.person_email.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const filteredPeople = people.filter((p) => {
    if (peopleSearch) {
      const q = peopleSearch.toLowerCase();
      return p.name.toLowerCase().includes(q) || p.email.toLowerCase().includes(q);
    }
    return true;
  });

  const moduleOptions = [
    { value: "all", label: "All modules" },
    ...modules.map((m) => ({ value: m.id, label: m.title })),
  ];
  const statusOptions = [
    { value: "all", label: "All statuses" },
    ...TRAINING_STATUSES.map((s) => ({ value: s, label: STATUS_LABELS[s] || s })),
  ];

  // ── Helpers ──

  const rateColor = (rate: number) => rate >= 0.8 ? "var(--success)" : rate >= 0.5 ? "var(--warning)" : "var(--danger)";
  const ratePct = (rate: number) => Math.round(rate * 100);

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Training Tracker</h2>
          <p className="muted">Manage training modules, assignments, and completion tracking.</p>
        </div>
      </div>

      {/* Alert Banner */}
      {alerts && (alerts.overdue_count > 0 || alerts.expiring_soon_count > 0) && (
        <div className="banner warning" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>
            {alerts.overdue_count > 0 && <strong>{alerts.overdue_count} overdue</strong>}
            {alerts.overdue_count > 0 && alerts.expiring_soon_count > 0 && <span> \u00B7 </span>}
            {alerts.expiring_soon_count > 0 && <span>{alerts.expiring_soon_count} expiring within 30 days</span>}
          </span>
          <button className="btn btn-ghost btn-sm" onClick={() => setTab("assignments")}>View Assignments</button>
        </div>
      )}

      {/* Tabs */}
      <div className="tab-bar" style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--border)" }}>
        <button
          className={`btn ${tab === "overview" ? "btn-primary" : "btn-ghost"}`}
          style={{ borderRadius: 0, borderBottom: tab === "overview" ? "2px solid var(--primary)" : "2px solid transparent" }}
          onClick={() => setTab("overview")}
        >
          Overview
        </button>
        <button
          className={`btn ${tab === "modules" ? "btn-primary" : "btn-ghost"}`}
          style={{ borderRadius: 0, borderBottom: tab === "modules" ? "2px solid var(--primary)" : "2px solid transparent" }}
          onClick={() => setTab("modules")}
        >
          Modules ({modules.length})
        </button>
        <button
          className={`btn ${tab === "assignments" ? "btn-primary" : "btn-ghost"}`}
          style={{ borderRadius: 0, borderBottom: tab === "assignments" ? "2px solid var(--primary)" : "2px solid transparent" }}
          onClick={() => setTab("assignments")}
        >
          Assignments
        </button>
      </div>

      {/* ─── TAB: Overview ─── */}
      {tab === "overview" && (
        <>
          {dashboardLoading ? (
            <p className="muted">Loading...</p>
          ) : !stats ? (
            <div className="panel" style={{ padding: "1rem" }}><p className="muted" style={{ margin: 0 }}>Could not load stats.</p></div>
          ) : (
            <>
              {/* Stat Cards */}
              <div className="stats stats-compact" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.75rem" }}>
                {[
                  { label: "Total Modules", value: stats.total_modules, tone: "ok" },
                  { label: "Total Assignments", value: stats.total_assignments, tone: "ok" },
                  { label: "Completion Rate", value: `${ratePct(stats.completion_rate)}%`, tone: stats.completion_rate >= 0.8 ? "success" : stats.completion_rate >= 0.5 ? "warning" : "danger" },
                  { label: "Overdue", value: stats.overdue, tone: stats.overdue > 0 ? "danger" : "ok" },
                ].map((card) => (
                  <div key={card.label} className={`stat-card stat-${card.tone}`} style={{ padding: "1rem", borderRadius: "var(--radius)", background: "var(--surface)", border: "1px solid var(--border)" }}>
                    <div className="stat-label" style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: "0.25rem" }}>{card.label}</div>
                    <div className="stat-value" style={{ fontSize: "1.5rem", fontWeight: 700 }}>{card.value}</div>
                  </div>
                ))}
              </div>

              {/* Per-Module Progress */}
              <div className="panel" style={{ padding: "1rem" }}>
                <h4 style={{ margin: "0 0 0.75rem" }}>Module Completion</h4>
                {stats.per_module.length === 0 ? (
                  <p className="muted" style={{ margin: 0 }}>No modules yet.</p>
                ) : (
                  <div style={{ display: "grid", gap: "0.75rem" }}>
                    {stats.per_module.map((m) => {
                      const mod = modules.find((x) => x.id === m.module_id);
                      const pct = ratePct(m.rate);
                      return (
                        <div key={m.module_id}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem", fontSize: "0.85rem" }}>
                            <span style={{ fontWeight: 600 }}>{mod?.title || "Unknown"}</span>
                            <span style={{ color: "var(--muted)" }}>{m.completed}/{m.total} ({pct}%)</span>
                          </div>
                          <div style={{ height: 8, background: "var(--border-subtle)", borderRadius: 4, overflow: "hidden" }}>
                            <div style={{ height: "100%", width: `${pct}%`, background: rateColor(m.rate), borderRadius: 4, transition: "width 0.3s" }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Recent Overdue */}
              {alerts && alerts.overdue.length > 0 && (
                <div className="panel" style={{ padding: "1rem" }}>
                  <h4 style={{ margin: "0 0 0.5rem", color: "var(--danger)" }}>Overdue ({alerts.overdue_count})</h4>
                  {alerts.overdue.slice(0, 5).map((a) => (
                    <div key={a.id} style={{ display: "flex", gap: "0.75rem", padding: "0.35rem 0", borderBottom: "1px solid var(--border-subtle)", fontSize: "0.85rem" }}>
                      <span style={{ fontWeight: 600, minWidth: 100 }}>{a.person_name}</span>
                      <span className="muted">{a.module_title}</span>
                      <span style={{ color: "var(--danger)", marginLeft: "auto" }}>Expired {a.expiry_date?.slice(0, 10)}</span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* ─── TAB: Modules ─── */}
      {tab === "modules" && (
        <>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem", flexWrap: "wrap" }}>
            <button className="btn btn-primary btn-sm" onClick={() => setShowNewModule(!showNewModule)}>
              {showNewModule ? "Cancel" : "+ New Module"}
            </button>
            <button className="btn btn-secondary btn-sm" onClick={handleSyncAssignments} disabled={syncing}>
              {syncing ? "Syncing..." : "Sync Assignments"}
            </button>
          </div>

          {syncResult && <div className="banner info" style={{ marginBottom: "0.5rem" }}>{syncResult}</div>}

          {showNewModule && (
            <form onSubmit={handleCreateModule} className="panel" style={{ padding: "1rem", marginBottom: "1rem" }}>
              <div style={{ display: "grid", gap: "0.75rem" }}>
                <label>
                  Title *
                  <input
                    value={newModForm.title}
                    onChange={(e) => setNewModForm({ ...newModForm, title: e.target.value })}
                    placeholder="Security Awareness 2026"
                    required
                    style={{ width: "100%" }}
                  />
                </label>
                <div style={{ display: "flex", gap: "0.75rem" }}>
                  <label style={{ flex: 1 }}>
                    Category
                    <input
                      value={newModForm.category}
                      onChange={(e) => setNewModForm({ ...newModForm, category: e.target.value })}
                      placeholder="security_awareness"
                      style={{ width: "100%" }}
                    />
                  </label>
                  <label style={{ width: 140 }}>
                    Renewal (days)
                    <input
                      type="number"
                      value={newModForm.renewal_period_days}
                      onChange={(e) => setNewModForm({ ...newModForm, renewal_period_days: parseInt(e.target.value) || 365 })}
                      style={{ width: "100%" }}
                    />
                  </label>
                </div>
                <label>
                  Description
                  <textarea
                    value={newModForm.description}
                    onChange={(e) => setNewModForm({ ...newModForm, description: e.target.value })}
                    placeholder="Annual security awareness training covering phishing, data handling, and incident reporting."
                    rows={2}
                    style={{ width: "100%" }}
                  />
                </label>
                <label>
                  Control IDs (comma-separated)
                  <input
                    value={newModForm.control_ids.join(", ")}
                    onChange={(e) => setNewModForm({ ...newModForm, control_ids: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })}
                    placeholder="AT.L2-3.2.1, AT.L2-3.2.2"
                    style={{ width: "100%" }}
                  />
                </label>
              </div>
              <div className="panel-footer" style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", padding: "0.75rem 0 0" }}>
                <button className="btn btn-primary btn-sm" type="submit" disabled={savingModule || !newModForm.title.trim()}>
                  {savingModule ? "Creating..." : "Create Module"}
                </button>
              </div>
            </form>
          )}

          {modulesLoading ? (
            <p className="muted">Loading...</p>
          ) : modules.length === 0 ? (
            <div className="panel" style={{ padding: "1rem" }}><p className="muted" style={{ margin: 0 }}>No training modules yet.</p></div>
          ) : (
            <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
              <div style={{ overflowX: "auto" }}>
                <table className="data-table" style={{ width: "100%" }}>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Required</th>
                      <th>Renewal</th>
                      <th>Controls</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {modules.map((m) => (
                      <tr key={m.id}>
                        <td>
                          {editModId === m.id ? (
                            <input
                              value={editModForm.title || ""}
                              onChange={(e) => setEditModForm({ ...editModForm, title: e.target.value })}
                              style={{ width: "100%" }}
                            />
                          ) : (
                            <span style={{ fontWeight: 600 }}>{m.title}</span>
                          )}
                          {editModId === m.id && editModForm.description !== undefined && (
                            <textarea
                              value={editModForm.description || ""}
                              onChange={(e) => setEditModForm({ ...editModForm, description: e.target.value })}
                              rows={2}
                              style={{ width: "100%", marginTop: 4, fontSize: "13px" }}
                            />
                          )}
                        </td>
                        <td>
                          {editModId === m.id ? (
                            <input
                              value={editModForm.category || ""}
                              onChange={(e) => setEditModForm({ ...editModForm, category: e.target.value })}
                              style={{ width: "100%" }}
                            />
                          ) : (
                            <span className="muted">{m.category || "-"}</span>
                          )}
                        </td>
                        <td>
                          {editModId === m.id ? (
                            <select
                              value={editModForm.is_required ? "yes" : "no"}
                              onChange={(e) => setEditModForm({ ...editModForm, is_required: e.target.value === "yes" })}
                            >
                              <option value="yes">Yes</option>
                              <option value="no">No</option>
                            </select>
                          ) : (
                            <span>{m.is_required ? "Yes" : "No"}</span>
                          )}
                        </td>
                        <td>
                          {editModId === m.id ? (
                            <input
                              type="number"
                              value={editModForm.renewal_period_days || 365}
                              onChange={(e) => setEditModForm({ ...editModForm, renewal_period_days: parseInt(e.target.value) || 365 })}
                              style={{ width: 80 }}
                            />
                          ) : (
                            <span>{m.renewal_period_days}d</span>
                          )}
                        </td>
                        <td>
                          {editModId === m.id ? (
                            <input
                              value={(editModForm.control_ids || []).join(", ")}
                              onChange={(e) => setEditModForm({ ...editModForm, control_ids: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })}
                              placeholder="AT.L2-3.2.1"
                              style={{ width: "100%", minWidth: 140 }}
                            />
                          ) : (
                            <span className="muted" style={{ fontSize: "12px", fontFamily: "monospace" }}>
                              {(m.control_ids || []).join(", ") || "-"}
                            </span>
                          )}
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: "0.25rem", alignItems: "center", flexWrap: "wrap" }}>
                            {editModId === m.id ? (
                              <>
                                <button className="btn btn-primary btn-sm" onClick={() => saveEditModule(m.id)} disabled={savingModule}>
                                  Save
                                </button>
                                <button className="btn btn-ghost btn-sm" onClick={() => { setEditModId(null); setEditModForm({}); }}>
                                  Cancel
                                </button>
                              </>
                            ) : (
                              <>
                                <button className="btn btn-ghost btn-sm" onClick={() => startEditModule(m)}>Edit</button>
                                <button className="btn btn-secondary btn-sm" onClick={() => setAssignModId(m.id)}>Assign</button>
                                <button className="btn btn-danger btn-sm" onClick={() => handleDeleteModule(m.id)}>Delete</button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Bulk Assign Modal */}
          {assignModId && (
            <div className="panel" style={{ padding: "1rem", marginTop: "0.75rem", border: "2px solid var(--primary)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <h4 style={{ margin: 0 }}>
                  Assign &ldquo;{modules.find((m) => m.id === assignModId)?.title || ""}&rdquo;
                </h4>
                <button className="btn btn-ghost btn-sm" onClick={() => { setAssignModId(null); setSelectedPersonIds(new Set()); setPeopleSearch(""); }}>Close</button>
              </div>

              <input
                placeholder="Search people..."
                value={peopleSearch}
                onChange={(e) => setPeopleSearch(e.target.value)}
                style={{ width: "100%", marginBottom: "0.5rem" }}
              />

              <div style={{ maxHeight: 240, overflowY: "auto", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: "0.25rem" }}>
                {filteredPeople.length === 0 ? (
                  <p className="muted" style={{ padding: "0.5rem", margin: 0 }}>No people found.</p>
                ) : (
                  filteredPeople.map((p) => (
                    <label key={p.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 0.5rem", cursor: "pointer", borderRadius: 4, background: selectedPersonIds.has(p.id) ? "var(--primary-soft)" : "transparent" }}>
                      <input
                        type="checkbox"
                        checked={selectedPersonIds.has(p.id)}
                        onChange={() => togglePerson(p.id)}
                      />
                      <span style={{ fontWeight: 500 }}>{p.name}</span>
                      <span className="muted" style={{ fontSize: "13px" }}>{p.email}</span>
                    </label>
                  ))
                )}
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "0.75rem" }}>
                <span className="muted" style={{ fontSize: "13px", alignSelf: "center" }}>
                  {selectedPersonIds.size} selected
                </span>
                <button className="btn btn-primary btn-sm" onClick={handleBulkAssign} disabled={assigning || selectedPersonIds.size === 0}>
                  {assigning ? "Assigning..." : `Assign to ${selectedPersonIds.size} people`}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* ─── TAB: Assignments ─── */}
      {tab === "assignments" && (
        <>
          <FilterBar>
            <FilterSearch value={search} onChange={setSearch} placeholder="Search by name or email..." />
            <FilterSelect value={moduleFilter} onChange={setModuleFilter} options={moduleOptions} placeholder="Module" />
            <FilterSelect value={statusFilter} onChange={setStatusFilter} options={statusOptions} placeholder="Status" />
            <FilterCount value={filteredAssignments.length} label="assignment" />
          </FilterBar>

          {/* Bulk complete bar */}
          {selectedAssignmentIds.size > 0 && (
            <div className="banner info" style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.5rem 0.75rem" }}>
              <span style={{ fontWeight: 600 }}>{selectedAssignmentIds.size} selected</span>
              <label style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                Complete date:
                <input type="date" value={bulkDate} onChange={(e) => setBulkDate(e.target.value)} />
              </label>
              <button className="btn btn-primary btn-sm" onClick={handleBulkComplete} disabled={bulkProcessing || !bulkDate}>
                {bulkProcessing ? "Processing..." : "Mark Complete"}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => { setSelectedAssignmentIds(new Set()); setBulkDate(""); }}>Clear</button>
            </div>
          )}

          {assignmentsLoading ? (
            <p className="muted">Loading...</p>
          ) : filteredAssignments.length === 0 ? (
            <div className="panel" style={{ padding: "1rem" }}><p className="muted" style={{ margin: 0 }}>No assignments found.</p></div>
          ) : (
            <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
              <div style={{ overflowX: "auto" }}>
                <table className="data-table" style={{ width: "100%" }}>
                  <thead>
                    <tr>
                      <th style={{ width: 36 }}>
                        <input
                          type="checkbox"
                          checked={selectedAssignmentIds.size === filteredAssignments.length && filteredAssignments.length > 0}
                          onChange={toggleAllAssignments}
                        />
                      </th>
                      <th>Person</th>
                      <th>Module</th>
                      <th>Status</th>
                      <th>Completed</th>
                      <th>Expires</th>
                      <th>Evidence</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAssignments.map((a) => {
                      const mod = modules.find((m) => m.id === a.module_id);
                      return (
                        <tr key={a.id}>
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedAssignmentIds.has(a.id)}
                              onChange={() => toggleAssignment(a.id)}
                            />
                          </td>
                          <td>
                            <div style={{ fontWeight: 600 }}>{a.person_name || "Unknown"}</div>
                            <div className="muted" style={{ fontSize: "12px" }}>{a.person_email}</div>
                          </td>
                          <td>{mod?.title || a.module_id.slice(0, 8)}</td>
                          <td>
                            <select
                              value={a.status}
                              onChange={(e) => handleUpdateStatus(a.id, e.target.value)}
                              style={{ padding: "2px 4px", fontSize: "12px" }}
                            >
                              {TRAINING_STATUSES.map((s) => (
                                <option key={s} value={s}>{STATUS_LABELS[s] || s}</option>
                              ))}
                            </select>
                            {' '}{statusBadge(a.status)}
                          </td>
                          <td style={{ fontSize: "13px" }}>{a.completion_date ? a.completion_date.slice(0, 10) : "-"}</td>
                          <td style={{ fontSize: "13px" }}>
                            {a.expiry_date ? (
                              <span style={{ color: a.expiry_date < new Date().toISOString().slice(0, 10) ? "var(--danger)" : undefined }}>
                                {a.expiry_date.slice(0, 10)}
                              </span>
                            ) : "-"}
                          </td>
                          <td>
                            {a.evidence_id ? (
                              <span style={{ fontSize: "12px", color: "var(--primary)", cursor: "pointer" }} title={a.evidence_id}>
                                View
                              </span>
                            ) : (
                              <button className="btn btn-ghost btn-sm" onClick={() => handleLinkEvidence(a.id)} style={{ fontSize: "11px", padding: "2px 6px" }}>
                                + Link
                              </button>
                            )}
                          </td>
                          <td>
                            {a.status === "exempt" && a.exemption_reason && (
                              <span className="muted" style={{ fontSize: "11px", cursor: "help" }} title={`Exempted by ${a.exempted_by || "?"} on ${a.exempted_date || "?"}: ${a.exemption_reason}`}>
                                ⓘ
                              </span>
                            )}
                            <button className="btn btn-danger btn-sm" onClick={() => handleDeleteAssignment(a.id)} style={{ fontSize: "11px", padding: "2px 6px", marginLeft: 4 }}>Remove</button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
