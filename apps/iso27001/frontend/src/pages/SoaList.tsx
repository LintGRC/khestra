import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api, authenticatedDownload, type SoaResponse, type SoaRow } from "../api";

const STATUSES = ["implemented", "partially implemented", "not implemented", "excluded"];

export default function SoaList() {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(iso27001)/)?.[0] ?? "";
  const [data, setData] = useState<SoaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sectionFilter, setSectionFilter] = useState("");
  const [savingId, setSavingId] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const load = () => {
    api.soa()
      .then(setData)
      .catch((e) => setError(String(e)));
  };
  useEffect(load, []);

  const rows = data?.rows ?? [];
  const sections = useMemo(() => {
    const out = new Map<string, SoaRow[]>();
    for (const r of rows) {
      const list = out.get(r.section) ?? [];
      list.push(r);
      out.set(r.section, list);
    }
    return [...out.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [rows]);

  const filteredSections = useMemo(() => {
    const out: Array<[string, SoaRow[]]> = [];
    for (const [section, list] of sections) {
      if (sectionFilter && section !== sectionFilter) continue;
      const kept = list.filter((r) => {
        if (filter && !`${r.control_id} ${r.title}`.toLowerCase().includes(filter.toLowerCase())) return false;
        if (statusFilter && r.status !== statusFilter) return false;
        return true;
      });
      if (kept.length) out.push([section, kept]);
    }
    return out;
  }, [sections, filter, statusFilter, sectionFilter]);

  const filteredTotal = filteredSections.reduce((n, [, list]) => n + list.length, 0);
  const rollup = data?.rollup;
  const counts = rollup?.counts ?? {};

  const patchStatus = async (row: SoaRow, status: string) => {
    if (status === row.status) return;
    setSavingId(row.control_id);
    setSaveError(null);
    try {
      await api.updateSoa(row.control_id, { status });
      const fresh = await api.soa();
      setData(fresh);
    } catch (e) {
      setSaveError(`Failed to update ${row.control_id}: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSavingId(null);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="page-stack">
      <section className="page-header no-print">
        <div>
          <h2>Statement of Applicability</h2>
          <p className="muted">ISO/IEC 27001:2022 controls — mark implementation status and exclusions.</p>
        </div>
        <div className="button-row">
          <button type="button" className="btn btn-secondary" onClick={handlePrint}>
            Print / PDF
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => authenticatedDownload("/api/soa/export.csv", "iso27001_soa.csv")}
          >
            Export CSV
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => authenticatedDownload("/api/soa/export.xlsx", "iso27001_soa.xlsx")}
          >
            Export XLSX
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => authenticatedDownload("/api/soa/export.docx", "iso27001_soa.docx")}
          >
            Export DOCX
          </button>
        </div>
      </section>

      <div className="banner info no-print">
        <strong>ISO/IEC 27001:2022 Amd 1:2024:</strong> Clauses 4.1 and 4.2 require the organization
        to determine whether climate change is a relevant issue for its ISMS. Ensure the Clause 6.1
        risk assessment addresses climate-related factors.
      </div>

      {error && <div className="banner error no-print">{error}</div>}
      {saveError && (
        <div className="banner error no-print">
          {saveError}{" "}
          <button type="button" className="btn-link" onClick={() => setSaveError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {rollup && (
        <div className="metric-grid no-print">
          <div className="metric-card">
            <div className="metric-value">{rollup.total}</div>
            <div className="metric-label">Controls in SoA</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{counts.implemented ?? 0}</div>
            <div className="metric-label">Implemented</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{counts["partially implemented"] ?? 0}</div>
            <div className="metric-label">Partially implemented</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{counts["not implemented"] ?? 0}</div>
            <div className="metric-label">Not implemented</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{counts.excluded ?? 0}</div>
            <div className="metric-label">Excluded</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{rollup.applicable_total}</div>
            <div className="metric-label">Applicable</div>
          </div>
        </div>
      )}

      <div className="card no-print">
        <div className="filter-bar">
          <input
            className="input"
            placeholder="Search controls…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <select className="select" value={sectionFilter} onChange={(e) => setSectionFilter(e.target.value)}>
            <option value="">All sections</option>
            {sections.map(([s]) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select className="select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <span className="muted" style={{ marginLeft: "auto" }}>
            {filteredTotal} / {rows.length} controls
          </span>
        </div>
      </div>

      <div className="card soa-table-wrap">
        <table className="table soa-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th className="no-print">Status</th>
              <th>Applicable</th>
            </tr>
          </thead>
          {filteredSections.map(([section, list]) => (
            <tbody key={section}>
              <tr className="soa-section-row">
                <td colSpan={4}>
                  <strong>{section}</strong>
                  <span className="muted">
                    {" "}
                    — {list.filter((r) => r.status === "implemented").length} implemented of {list.length}
                  </span>
                </td>
              </tr>
              {list.map((r) => (
                <tr key={r.control_id}>
                  <td className="soa-id">
                    <Link to={`${fwBase}/soa/${encodeURIComponent(r.control_id)}`}>{r.control_id}</Link>
                  </td>
                  <td>
                    <div className="soa-title">{r.title}</div>
                    {r.justification && <div className="muted soa-just">{r.justification}</div>}
                  </td>
                  <td className="no-print">
                    <select
                      className="select soa-status-select"
                      value={r.status}
                      disabled={savingId === r.control_id}
                      onChange={(e) => patchStatus(r, e.target.value)}
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </td>
                  <td className={r.applicable ? "soa-applicable" : "soa-excluded"}>
                    {r.applicable ? "Yes" : "No"}
                  </td>
                </tr>
              ))}
            </tbody>
          ))}
        </table>
        {filteredSections.length === 0 && (
          <p className="muted" style={{ textAlign: "center", padding: "1.5rem" }}>
            No controls match the current filters.
          </p>
        )}
      </div>
    </div>
  );
}