import { useState, useEffect, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Incident } from "../types";
import { SEVERITY_LABELS, STATUS_LABELS, FAILURE_MODE_LABELS } from "../types";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#dc2626", high: "#ea580c", medium: "#ca8a04", low: "#6b7280",
};

interface IncidentsListProps {
  basePath?: string;
}

export default function IncidentsList({ basePath = "/incidents" }: IncidentsListProps) {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [failureModeFilter, setFailureModeFilter] = useState("");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, string> = {};
      if (debouncedSearch) params.q = debouncedSearch;
      if (statusFilter) params.status = statusFilter;
      if (severityFilter) params.severity = severityFilter;
      if (failureModeFilter) params.failure_mode = failureModeFilter;
      const data = await api.list(params);
      setIncidents(data.incidents || []);
      setTotal(data.total);
    } catch (e) {
      setError("Failed to load incidents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [debouncedSearch, statusFilter, severityFilter, failureModeFilter]);

  useEffect(() => {
    api.stats().then(setStats).catch(() => {});
  }, []);

  const handleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleSelectAll = () => {
    if (selectedIds.size === incidents.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(incidents.map((i) => i.id)));
    }
  };

  const clearSelection = () => setSelectedIds(new Set());

  const handleSeed = async () => {
    setSeeding(true);
    try { await api.seed(); await load(); } catch { /* ignore */ }
    finally { setSeeding(false); }
  };

  const handleBulk = async (action: string, value?: string) => {
    if (selectedIds.size === 0) return;
    const ids = Array.from(selectedIds);
    if (action === "delete") {
      if (!confirm(`Delete ${ids.length} incident(s)?`)) return;
      await Promise.all(ids.map((id) => api.delete(id)));
    } else if (action === "close") {
      await api.bulk(ids, "close");
    } else if (action === "severity") {
      const v = value || prompt("Enter new severity (critical/high/medium/low):");
      if (!v || !["critical", "high", "medium", "low"].includes(v)) return;
      await api.bulk(ids, "severity", v);
    }
    clearSelection();
    await load();
  };

  const registryClocks = useMemo(() => {
    const result: Record<string, { label: string; color: string }> = {};
    for (const inc of incidents) {
      const clock = inc.regulatory_clock;
      if (!clock?.deadline) continue;
      const diff = new Date(clock.deadline).getTime() - Date.now();
      const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
      if (days <= 0) result[inc.id] = { label: "OVERDUE", color: "#dc2626" };
      else if (days <= 2) result[inc.id] = { label: `${days}d left`, color: "#dc2626" };
      else if (days <= 5) result[inc.id] = { label: `${days}d left`, color: "#ea580c" };
      else result[inc.id] = { label: `${days}d left`, color: "var(--muted)" };
    }
    return result;
  }, [incidents]);

  if (loading && incidents.length === 0) {
    return <div className="page-stack"><p className="muted">Loading incidents...</p></div>;
  }

  if (error) {
    return <div className="page-stack"><div className="banner error">{error}</div></div>;
  }

  const allSelected = incidents.length > 0 && selectedIds.size === incidents.length;

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Incidents</h2>
        <p className="muted">{total} total{total > 0 && ` · ${incidents.length} shown`}</p>
        <div style={{ marginTop: 8 }}>
          <button className="btn btn-sm btn-ghost" onClick={() => window.open(api.exportCsvUrl(), "_blank")}>Export CSV</button>
          <button className="btn btn-primary" style={{ marginLeft: 8 }} onClick={() => navigate(`${basePath}/new`)}>+ New Incident</button>
        </div>
      </div>

      {stats && (
        <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700 }}>{stats.total || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>Total</div>
          </div>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700, color: "var(--danger)" }}>{stats.open || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>Open</div>
          </div>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700, color: stats.overdue_regulatory > 0 ? "var(--danger)" : "var(--success)" }}>{stats.overdue_regulatory || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>Overdue</div>
          </div>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700, color: "#dc2626" }}>{stats.by_severity?.critical || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>Critical</div>
          </div>
        </div>
      )}

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} />
        <FilterSelect value={statusFilter} onChange={setStatusFilter} options={Object.entries(STATUS_LABELS).map(([k, v]) => ({ value: k, label: v }))} placeholder="All Statuses" />
        <FilterSelect value={severityFilter} onChange={setSeverityFilter} options={Object.entries(SEVERITY_LABELS).map(([k, v]) => ({ value: k, label: v }))} placeholder="All Severities" />
        <FilterSelect value={failureModeFilter} onChange={setFailureModeFilter} options={Object.entries(FAILURE_MODE_LABELS).map(([k, v]) => ({ value: k, label: v }))} placeholder="All Failure Modes" />
      </FilterBar>

      {selectedIds.size > 0 && (
        <div className="panel" style={{ position: "sticky", top: 0, zIndex: 10, borderLeft: "3px solid var(--primary)", marginBottom: "0.75rem" }}>
          <div className="panel-body" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
            <span style={{ fontWeight: 600, fontSize: "0.875rem" }}>{selectedIds.size} selected</span>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <button className="btn btn-sm btn-secondary" onClick={() => handleBulk("close")}>Close</button>
              <button className="btn btn-sm btn-secondary" onClick={() => handleBulk("severity")}>Change Severity</button>
              <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleBulk("delete")}>Delete</button>
              <button className="btn btn-sm btn-ghost" onClick={clearSelection}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {incidents.length === 0 ? (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">
              {debouncedSearch || statusFilter || severityFilter || failureModeFilter
                ? "No incidents match your filters."
                : "No incidents yet."}
            </p>
            <div style={{ marginTop: "0.75rem" }}>
              <button className="btn btn-primary" onClick={() => navigate(`${basePath}/new`)}>Report Incident</button>
              <button className="btn btn-sm btn-ghost" style={{ marginLeft: 8 }} onClick={handleSeed} disabled={seeding}>
                {seeding ? "Loading..." : "Load Sample Data"}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div style={{ border: "1px solid var(--border)", borderRadius: "var(--radius)", background: "var(--panel-bg, #fff)" }}>
          <div style={{ padding: "8px 16px", borderBottom: "1px solid var(--border)" }}>
            <input type="checkbox" checked={allSelected} onChange={handleSelectAll} style={{ width: "auto", verticalAlign: "top", marginTop: 3 }} />
            <span className="muted" style={{ marginLeft: 6, fontSize: 13, lineHeight: "20px" }}>Select all</span>
          </div>
          {incidents.map((inc) => (
            <div key={inc.id} style={{ padding: "8px 16px", borderBottom: "1px solid var(--border)" }}>
              <input type="checkbox" checked={selectedIds.has(inc.id)} onChange={() => handleSelect(inc.id)} style={{ width: "auto", verticalAlign: "top", marginTop: 3 }} />
              <span className={`badge ${inc.status === "closed" ? "badge-success" : inc.status === "containment" ? "badge-danger" : "badge-warning"}`} style={{ marginLeft: 6, verticalAlign: "top" }}>
                {STATUS_LABELS[inc.status] || inc.status}
              </span>
              <span className="badge" style={{ backgroundColor: SEVERITY_COLORS[inc.severity] || "#6b7280", color: "#fff", marginLeft: 4, verticalAlign: "top" }}>
                {SEVERITY_LABELS[inc.severity] || inc.severity}
              </span>
              <Link to={`${basePath}/${inc.id}`} style={{ fontWeight: 600, textDecoration: "none", color: "inherit", marginLeft: 6, lineHeight: "20px" }}>
                {inc.title}
              </Link>
              <br />
              <span className="muted" style={{ fontSize: 12, marginLeft: 24, lineHeight: "20px" }}>
                {inc.failure_mode && <>{FAILURE_MODE_LABELS[inc.failure_mode] || inc.failure_mode} · </>}
                {inc.created_at?.slice(0, 10)}
                {registryClocks[inc.id] && (
                  <> · <span style={{ color: registryClocks[inc.id].color, fontWeight: 600 }}>{registryClocks[inc.id].label}</span></>
                )}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
