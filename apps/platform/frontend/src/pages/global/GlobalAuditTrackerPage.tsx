import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FilterBar, FilterSearch, FilterSelect, FilterCount } from "@shared/filter-bar";
import { authFetchJson } from "./authFetch";

const FRAMEWORKS = [
  { id: "cmmc", label: "CMMC", color: "#059669", queryValue: "CMMC", api: "/api/cmmc" },
  { id: "soc2", label: "SOC 2", color: "#2563eb", queryValue: "SOC2", api: "/api/soc2" },
  { id: "aigov", label: "AI Governance", color: "#7c3aed", queryValue: "AIGov", api: "/api/ai-governance" },
];

type AuditItem = {
  id: string;
  title: string;
  framework: string;
  audit_type: string;
  start_date: string;
  end_date: string;
  status: string;
  auditor_name: string;
  _fwId: string;
  _fwLabel: string;
  _fwColor: string;
  _detailPath: string;
};

function statusBadge(status: string) {
  const m: Record<string, string> = {
    planned: "badge-muted", in_progress: "badge-warning", frozen: "badge-info",
    completed: "badge-success", cancelled: "badge-muted",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace("_", " ")}</span>;
}

export default function GlobalAuditTrackerPage() {
  const navigate = useNavigate();
  const [byFramework, setByFramework] = useState<Record<string, AuditItem[]>>({});
  const [loading, setLoading] = useState(true);
  const [filterFw, setFilterFw] = useState<string | "all">("all");
  const [filterType, setFilterType] = useState<string | "all">("all");
  const [filterStatus, setFilterStatus] = useState<string | "all">("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    Promise.all(
      FRAMEWORKS.map((fw) =>
        authFetchJson<{ audits?: any[] }>(`${fw.api}/audit-center/audits?framework=${fw.queryValue}`)
          .then((d) => ({ fwId: fw.id, items: (d.audits || []).map((a: any) => ({
            ...a,
            _fwId: fw.id,
            _fwLabel: fw.label,
            _fwColor: fw.color,
            _detailPath: `/${fw.id}/audits/${a.id}`,
          })) }))
          .catch(() => ({ fwId: fw.id, items: [] as AuditItem[] }))
      )
    ).then((results) => {
      const map: Record<string, AuditItem[]> = {};
      results.forEach((r) => { map[r.fwId] = r.items; });
      setByFramework(map);
      setLoading(false);
    });
  }, []);

  const allAudits: AuditItem[] = useMemo(() => {
    const fws = filterFw === "all" ? FRAMEWORKS : FRAMEWORKS.filter((fw) => fw.id === filterFw);
    let items: AuditItem[] = [];
    fws.forEach((fw) => { items = items.concat(byFramework[fw.id] || []); });

    if (filterType !== "all") items = items.filter((a) => a.audit_type === filterType);
    if (filterStatus !== "all") items = items.filter((a) => a.status === filterStatus);
    if (search) {
      const q = search.toLowerCase();
      items = items.filter((a) =>
        a.title.toLowerCase().includes(q) ||
        a.auditor_name?.toLowerCase().includes(q) ||
        a.framework?.toLowerCase().includes(q)
      );
    }
    return items.sort((a, b) => ((a as any).created_at || "").localeCompare((b as any).created_at || ""));
  }, [byFramework, filterFw, filterType, filterStatus, search]);

  const typeOptions = [{ value: "all", label: "All types" }, ...["internal", "external", "readiness", "certification", "surveillance"].map((t) => ({ value: t, label: t.replace("_", " ") }))];
  const statusOptions = [{ value: "all", label: "All statuses" }, ...["planned", "in_progress", "frozen", "completed", "cancelled"].map((s) => ({ value: s, label: s.replace("_", " ") }))];

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;

  return (
    <div>
      <div className="page-intro">
        <div className="page-intro-head">
          <h1 className="page-intro-title">Audits</h1>
        </div>
      </div>
      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search by title, auditor..." />
        <FilterSelect value={filterFw} onChange={setFilterFw} options={FRAMEWORKS.map(fw => ({ value: fw.id, label: fw.label }))} placeholder="All frameworks" />
        <FilterSelect value={filterType} onChange={setFilterType} options={typeOptions} placeholder="Type" />
        <FilterSelect value={filterStatus} onChange={setFilterStatus} options={statusOptions} placeholder="Status" />
        <FilterCount value={allAudits.length} label="audit" />
      </FilterBar>
      <div className="panel" style={{ padding: 0 }}>
        {allAudits.length === 0 ? (
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
              {allAudits.map((a, i) => (
                <tr key={`${a._fwId}-${a.id}-${i}`} onClick={() => navigate(a._detailPath)} style={{ cursor: "pointer" }}>
                  <td style={{ fontWeight: 600 }}>{a.title}</td>
                  <td><span style={{ color: a._fwColor, fontWeight: 600 }}>{a._fwLabel}</span></td>
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
