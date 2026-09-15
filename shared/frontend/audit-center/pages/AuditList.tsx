import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { auditApi } from "../api";
import type { Audit } from "../types";
import { AUDIT_STATUSES, AUDIT_TYPES } from "../types";
import { FilterBar, FilterSelect, FilterSearch, FilterCount } from "@shared/filter-bar";

function statusBadge(status: string) {
  const m: Record<string, string> = {
    planned: "badge-muted",
    in_progress: "badge-warning",
    frozen: "badge-info",
    completed: "badge-success",
    cancelled: "badge-muted",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace("_", " ")}</span>;
}

type Props = {
  frameworkFilter?: string;
};

export default function AuditList({ frameworkFilter }: Props) {
  const navigate = useNavigate();
  const [audits, setAudits] = useState<Audit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const load = async () => {
    try {
      const data = await auditApi.list(frameworkFilter ? { framework: frameworkFilter } : undefined);
      setAudits(data.audits || []);
    } catch (e) {
      console.error(e);
      setError("Failed to load audits. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [frameworkFilter]);

  const typeOptions = [{ value: "all", label: "All types" }, ...AUDIT_TYPES.map((t) => ({ value: t, label: t.replace("_", " ") }))];
  const statusOptions = [{ value: "all", label: "All statuses" }, ...AUDIT_STATUSES.map((s) => ({ value: s, label: s.replace("_", " ") }))];

  const filtered = audits.filter((a) => {
    if (typeFilter !== "all" && a.audit_type !== typeFilter) return false;
    if (statusFilter !== "all" && a.status !== statusFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        a.title.toLowerCase().includes(q) ||
        a.auditor_name.toLowerCase().includes(q) ||
        a.framework.toLowerCase().includes(q)
      );
    }
    return true;
  });

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;
  if (error) return <div className="page-stack"><div className="banner error">{error}</div></div>;

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Audits</h2>
          <p className="muted">{audits.length} total</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => navigate("new")}>+ New Audit</button>
      </div>

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search by title, auditor, framework..." />
        <FilterSelect value={typeFilter} onChange={setTypeFilter} options={typeOptions} placeholder="Type" />
        <FilterSelect value={statusFilter} onChange={setStatusFilter} options={statusOptions} placeholder="Status" />
        <FilterCount value={filtered.length} label="audit" />
      </FilterBar>

      <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
        {filtered.length === 0 ? (
          <p className="muted" style={{ padding: "1rem", margin: 0 }}>No audits found.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
          <table className="data-table" style={{ width: "100%" }}>
            <thead>
              <tr>
                <th>Title</th>
                <th>Framework</th>
                <th>Type</th>
                <th>Date Range</th>
                <th>Auditor</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a) => (
                <tr key={a.id} onClick={() => navigate(a.id)} style={{ cursor: "pointer" }}>
                  <td style={{ fontWeight: 600 }}>{a.title}</td>
                  <td>{a.framework || "-"}</td>
                  <td style={{ textTransform: "capitalize" }}>{a.audit_type?.replace("_", " ") || "-"}</td>
                  <td>{a.start_date ? `${a.start_date.slice(0, 10)} \u2192 ${a.end_date?.slice(0, 10) || ""}` : "-"}</td>
                  <td>{a.auditor_name || "-"}</td>
                  <td>{statusBadge(a.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        )}
      </div>
    </div>
  );
}
