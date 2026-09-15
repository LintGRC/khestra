import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { vendorApi, vendorTitle, vendorTerm } from "../api";
import type { VendorItem } from "../types";
import { FilterBar, FilterButtons, FilterCount } from "@shared/filter-bar";

const FW_COLORS: Record<string, string> = {
  SOC2: "#2563eb", AIGov: "#7c3aed", CMMC: "#059669",
};

function statusBadge(status: string) {
  const m: Record<string, string> = {
    pending: "badge-muted",
    sent: "badge-warning",
    responded: "badge-info",
    assessed: "badge-warning",
    approved: "badge-success",
    rejected: "badge-danger",
    under_review: "badge-warning",
  };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status.replace(/_/g, " ")}</span>;
}

function riskBadge(score: number | null) {
  if (score == null) return <>—</>;
  if (score >= 80) return <span className="badge badge-success">Low Risk ({score})</span>;
  if (score >= 50) return <span className="badge badge-warning">Medium ({score})</span>;
  return <span className="badge badge-danger">High Risk ({score})</span>;
}

export default function VendorDashboard() {
  const navigate = useNavigate();
  const [vendors, setVendors] = useState<VendorItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<string[]>([]);
  const [seeding, setSeeding] = useState(false);

  const load = async () => {
    try {
      const data = await vendorApi.list();
      setVendors(data.vendors || []);
    } catch (e) {
      console.error(e);
      setError("Failed to load vendors. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this vendor permanently?")) return;
    try { await vendorApi.delete(id); await load(); } catch { /* ignore */ }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try { await vendorApi.seed(); await load(); } catch { /* ignore */ }
    finally { setSeeding(false); }
  };

  const filtered = vendors.filter((v) => {
    if (filter === "all") return true;
    if (filter === "pending") return v.status === "pending" || v.status === "sent";
    if (filter === "approved") return v.status === "approved";
    if (filter === "high_risk") return (v.risk_score ?? 100) < 50;
    return v.status === filter;
  });

  const vendorCounts = {
    all: vendors.length,
    pending: vendors.filter((v) => v.status === "pending" || v.status === "sent").length,
    approved: vendors.filter((v) => v.status === "approved").length,
    high_risk: vendors.filter((v) => (v.risk_score ?? 100) < 50).length,
  };

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;
  if (error) return <div className="page-stack"><div className="banner error">{error}</div></div>;

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>{vendorTitle()}</h2>
          <p className="muted">
            {vendors.length} {vendorTerm(vendors.length)} ·{" "}
            {vendors.filter((v) => v.status === "approved").length} approved ·{" "}
            {vendors.filter((v) => (v.risk_score ?? 100) < 50).length} high risk
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <button className="btn btn-ghost btn-sm" onClick={() => window.open(vendorApi.exportCsvUrl())}>Export CSV</button>
          <button className="btn btn-primary btn-sm" onClick={() => navigate("new")}>+ New {vendorTerm()}</button>
        </div>
      </div>

      {selected.length > 1 && (
        <div className="panel" style={{ padding: "8px 16px", marginBottom: 12, borderLeft: "3px solid var(--primary)" }}>
          <span style={{ fontWeight: 600, fontSize: 13 }}>{selected.length} selected</span>
          <button className="btn btn-sm btn-secondary" style={{ marginLeft: 8 }} onClick={() => navigate(`compare?ids=${selected.join(",")}`)}>Compare</button>
          <button className="btn btn-sm btn-ghost" style={{ marginLeft: 4 }} onClick={() => setSelected([])}>Clear</button>
        </div>
      )}

      <FilterBar>
        <FilterButtons
          items={[
            { key: "all", label: "All", count: vendorCounts.all },
            { key: "pending", label: "Pending", count: vendorCounts.pending },
            { key: "approved", label: "Approved", count: vendorCounts.approved },
            { key: "high_risk", label: "High Risk", count: vendorCounts.high_risk },
          ]}
          active={filter}
          onChange={setFilter}
        />
        <FilterCount value={vendors.length} label="vendor" />
      </FilterBar>

      <div className="panel">
        <div className="panel-body">
          {filtered.length === 0 ? (
            <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>
              {vendors.length === 0 ? `No ${vendorTerm(2).toLowerCase()} yet.` : `No ${vendorTerm(2).toLowerCase()} match this filter.`}
              {vendors.length === 0 && (
                <><br /><button className="btn btn-sm btn-ghost" style={{ marginTop: 8 }} onClick={handleSeed} disabled={seeding}>{seeding ? "Loading..." : `Load Sample ${vendorTerm(2)}`}</button></>
              )}
            </p>
          ) : (
            filtered.map((v) => (
              <div key={v.id} style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "1rem", marginBottom: "0.5rem", cursor: "pointer" }} onClick={() => navigate(v.id)}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap", marginBottom: "0.25rem" }}>
                      <input type="checkbox" checked={selected.includes(v.id)} onChange={() => setSelected((prev) => prev.includes(v.id) ? prev.filter((x) => x !== v.id) : [...prev, v.id])} onClick={(e) => e.stopPropagation()} style={{ width: "auto" }} />
                      <strong style={{ fontSize: "1rem", color: "var(--link)" }}>{v.name}</strong>
                      {statusBadge(v.status)}
                      {riskBadge(v.risk_score)}
                      {v.category && <span className="badge badge-muted">{v.category.replace(/_/g, " ")}</span>}
                      {(v.frameworks || []).map((fw) => (
                        <span key={fw} style={{ display: "inline-block", fontSize: 10, fontWeight: 600, padding: "1px 6px", borderRadius: "var(--radius)", color: "#fff", background: FW_COLORS[fw] || "var(--muted)" }}>{fw}</span>
                      ))}
                    </div>
                    {v.product_service && <p style={{ fontSize: "0.85rem", margin: "0.25rem 0" }}>{v.product_service}</p>}
                    <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.25rem" }}>
                      {v.contact_name && `${v.contact_name} · `}{v.contact_email && `${v.contact_email} · `}{v.created_at?.slice(0, 10)}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "0.35rem" }} onClick={(e) => e.stopPropagation()}>
                    <Link to={v.id} className="btn btn-sm btn-ghost" onClick={(e) => e.stopPropagation()}>View</Link>
                    <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={(e) => { e.stopPropagation(); handleDelete(v.id); }}>Delete</button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
