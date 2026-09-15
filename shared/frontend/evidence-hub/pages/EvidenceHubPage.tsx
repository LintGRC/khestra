import React, { useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";
import { FilterBar, FilterSearch, FilterSelect, FilterCount } from "@shared/filter-bar";
import AutomationCoverageMatrix from "../components/AutomationCoverageMatrix";

async function hubFetch(path: string, init?: RequestInit): Promise<Response> {
  const headers = await authHeaders(init?.headers);
  return fetch(apiUrl(path), { ...init, headers });
}

const FW_LABELS: Record<string, string> = { SOC2: "SOC 2", AIGov: "AI Gov", CMMC: "CMMC", ISO27001: "ISO 27001" };
const FW_OPTIONS = ["SOC2", "AIGov", "CMMC", "ISO27001"];

type EvidenceItem = {
  id: string;
  name: string;
  filename: string;
  description: string;
  tags: string[];
  uploaded_by: string;
  uploaded_at: string;
  sha256: string;
  file_size: number;
  mime_type: string;
  review_status: string;
  reviewer: string;
  review_comment: string;
  reviewed_at: string;
  mappings: { id: string; framework_id: string; control_id: string }[];
  evidence_type: string;
  display_title: string;
  evidence_version: string;
  period_covered?: string;
  auto_status: string;
  auto_summary: string;
  source_check?: string;
  provider?: string;
};

type SortField = "name" | "evidence_type" | "review_status" | "uploaded_at" | "mappings";
type SortDir = "asc" | "desc";

function fmtSize(bytes: number) {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatAutoSummary(s: string) {
  try {
    return JSON.stringify(JSON.parse(s), null, 2);
  } catch {
    return s;
  }
}

function AutoSummary({ summary }: { summary: string }) {
  const pretty = formatAutoSummary(summary || "");
  if (pretty === summary) return <span className="muted">{summary}</span>;
  return (
    <pre style={{ margin: 0, fontSize: 11, lineHeight: 1.5, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
      {pretty}
    </pre>
  );
}

function reviewBadge(status: string) {
  const m: Record<string, string> = { pending: "badge-warning", approved: "badge-success", rejected: "badge-danger" };
  return <span className={`badge ${m[status] || "badge-muted"}`}>{status}</span>;
}

function PaginationPages({ page, totalPages, onPageChange }: { page: number; totalPages: number; onPageChange: (p: number) => void }) {
  if (totalPages <= 1) return null;
  const pages: (number | "ellipsis")[] = [];
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) pages.push(i);
  } else {
    pages.push(1);
    if (page > 3) pages.push("ellipsis");
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) pages.push(i);
    if (page < totalPages - 2) pages.push("ellipsis");
    pages.push(totalPages);
  }
  return (
    <div className="pagination-pages">
      <button disabled={page === 1} onClick={() => onPageChange(page - 1)}>‹</button>
      {pages.map((p, i) =>
        p === "ellipsis" ? <span key={`e${i}`} className="pagination-ellipsis">…</span> :
        <button key={p} className={p === page ? "active" : ""} onClick={() => onPageChange(p)}>{p}</button>
      )}
      <button disabled={page === totalPages} onClick={() => onPageChange(page + 1)}>›</button>
    </div>
  );
}

export default function EvidenceHubPage() {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterFw, setFilterFw] = useState("");
  const [filterSource, setFilterSource] = useState("");
  const [filterReview, setFilterReview] = useState("");
  const [filterView, setFilterView] = useState("latest");
  const [searchQ, setSearchQ] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", tags: "" });
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const [tab, setTab] = useState<"evidence" | "coverage" | "requests" | "automation">("evidence");
  const [stats, setStats] = useState<any>(null);
  const [requests, setRequests] = useState<any[]>([]);
  const [reqForm, setReqForm] = useState({ framework_id: "", control_id: "", title: "", description: "", assigned_to: "", due_date: "" });
  const [reqSaving, setReqSaving] = useState(false);
  const reqQs = filterFw ? `?framework_id=${filterFw}` : "";
  const [viewingContent, setViewingContent] = useState<{ id: string; filename: string; data: string } | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortField, setSortField] = useState<SortField>("uploaded_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const navigate = useNavigate();
  const location = useLocation();
  const fwBase = location.pathname.match(/^\/(cmmc|soc2|aigov|iso27001)/)?.[0] ?? "";

  const load = () => {
    const params = new URLSearchParams();
    if (filterFw) params.set("framework_id", filterFw);
    params.set("view", filterView || "latest");
    const qs = `?${params.toString()}`;
    hubFetch(`/api/evidence-hub${qs}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((d) => setEvidence(d.evidence || []))
      .catch(() => setEvidence([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filterFw, filterView]);

  const filtered = evidence.filter((ev) => {
    if (filterSource === "auto" && !ev.uploaded_by?.startsWith("collector:")) return false;
    if (filterSource === "manual" && ev.uploaded_by?.startsWith("collector:")) return false;
    if (filterReview && ev.review_status !== filterReview) return false;
    if (searchQ) {
      const q = searchQ.toLowerCase();
      if (!ev.name.toLowerCase().includes(q) && !ev.description.toLowerCase().includes(q) && !ev.filename.toLowerCase().includes(q) && !(ev.source_check || "").toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    let cmp = 0;
    switch (sortField) {
      case "name":
        cmp = (a.display_title || a.name).localeCompare(b.display_title || b.name);
        break;
      case "evidence_type":
        cmp = a.evidence_type.localeCompare(b.evidence_type);
        break;
      case "review_status":
        cmp = a.review_status.localeCompare(b.review_status);
        break;
      case "uploaded_at":
        cmp = (a.uploaded_at || "").localeCompare(b.uploaded_at || "");
        break;
      case "mappings":
        cmp = (a.mappings?.length || 0) - (b.mappings?.length || 0);
        break;
    }
    return sortDir === "asc" ? cmp : -cmp;
  });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  const sortIndicator = (field: SortField) => {
    if (sortField !== field) return <span className="sort-indicator">⇅</span>;
    return <span className="sort-indicator">{sortDir === "asc" ? "↑" : "↓"}</span>;
  };

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const paginatedEvidence = sorted.slice((page - 1) * pageSize, page * pageSize);

  useEffect(() => { if (page > totalPages) setPage(1); }, [totalPages]);
  useEffect(() => { setPage(1); setExpandedId(null); }, [sortField, sortDir]);
  useEffect(() => { setExpandedId(null); }, [filterFw, filterSource, filterReview, searchQ]);

  useEffect(() => {
    if (tab === "coverage") {
      hubFetch("/api/evidence-hub/stats")
        .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
        .then(setStats)
        .catch(() => {});
    }
  }, [tab]);

  useEffect(() => {
    if (tab === "requests") {
      hubFetch(`/api/evidence-hub/requests${reqQs}`)
        .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
        .then((d) => setRequests(d.requests || []))
        .catch(() => {});
    }
  }, [tab, filterFw]);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("name", form.name || file.name);
      fd.append("description", form.description);
      fd.append("tags", JSON.stringify(form.tags.split(",").map((t) => t.trim()).filter(Boolean)));
      fd.append("uploaded_by", "user@company.com");
      await hubFetch("/api/evidence-hub/upload", { method: "POST", body: fd });
      setShowForm(false);
      setForm({ name: "", description: "", tags: "" });
      setFile(null);
      await load();
    } catch { /* ignore */ }
    finally { setUploading(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this evidence?")) return;
    await hubFetch(`/api/evidence-hub/${id}`, { method: "DELETE" });
    await load();
  };

  const handleReview = async (eid: string, status: string) => {
    await hubFetch(`/api/evidence-hub/${eid}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, reviewer: "user@company.com", comment: "" }),
    });
    await load();
  };

  const handleMap = async (eid: string, fw: string, ctrl: string) => {
    if (!ctrl.trim()) return;
    await hubFetch(`/api/evidence-hub/${eid}/map`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ framework_id: fw, control_id: ctrl.trim(), mapped_by: "user" }),
    });
    await load();
  };

  const handleUnmap = async (eid: string, fw: string, ctrl: string) => {
    await hubFetch(`/api/evidence-hub/${eid}/map/${fw}/${ctrl}`, { method: "DELETE" });
    await load();
  };

  const [mapForm, setMapForm] = useState<{ eid: string; fw: string; ctrl: string } | null>(null);

  const handleBulkReview = async (status: string) => {
    if (selectedIds.size === 0) return;
    if (!confirm(`Mark ${selectedIds.size} evidence items as "${status}"?`)) return;
    try {
      await hubFetch("/api/evidence-hub/bulk-review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eids: Array.from(selectedIds), status, reviewer: "user@company.com" }),
      });
      setSelectedIds(new Set());
      await load();
    } catch { /* ignore */ }
  };

  const toggleSelectAll = () => {
    const pageIds = new Set(paginatedEvidence.map(ev => ev.id));
    const allSelected = [...pageIds].every(id => selectedIds.has(id));
    const next = new Set(selectedIds);
    pageIds.forEach(id => allSelected ? next.delete(id) : next.add(id));
    setSelectedIds(next);
  };

  const evidenceTab = tab !== "evidence" ? null : (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap", alignItems: "center" }}>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Upload Evidence"}
        </button>
        <a className="btn btn-secondary btn-sm" href={apiUrl(`/api/evidence-hub/export${filterFw ? `?framework_id=${filterFw}` : ""}`)} download>
          Export ZIP
        </a>
        <span className="muted" style={{ fontSize: 12 }}>Filter by framework:</span>
        {["", ...FW_OPTIONS].map((fw) => (
          <button key={fw} className={`btn btn-sm ${filterFw === fw ? "btn-primary" : "btn-ghost"}`} onClick={() => { setFilterFw(fw); setPage(1); }}>
            {fw || "All"}
          </button>
        ))}
      </div>

      <FilterBar>
        <FilterSearch value={searchQ} onChange={(v) => { setSearchQ(v); setPage(1); }} placeholder="Search evidence..." />
        <FilterSelect
          value={filterView}
          onChange={(v) => { setFilterView(v || "latest"); setPage(1); }}
          options={[
            { value: "latest", label: "Latest per check" },
            { value: "by_period", label: "By collection day" },
            { value: "archived", label: "Archived periods" },
            { value: "all", label: "All non-archived" },
          ]}
          placeholder="Latest per check"
        />
        <FilterSelect value={filterSource} onChange={(v) => { setFilterSource(v); setPage(1); }} options={[{ value: "manual", label: "Manual" }, { value: "auto", label: "Auto" }]} placeholder="All Sources" />
        <FilterSelect value={filterReview} onChange={(v) => { setFilterReview(v); setPage(1); }} options={[{ value: "pending", label: "Pending" }, { value: "approved", label: "Approved" }, { value: "rejected", label: "Rejected" }]} placeholder="All Statuses" />
        <FilterCount value={filtered.length} />
      </FilterBar>
      {filterView === "latest" && (
        <p className="muted" style={{ fontSize: "0.78rem", margin: "0 0 0.75rem" }}>
          Showing the latest automation result per check. Switch to “By collection day” to see one artifact per day in the retention window.
        </p>
      )}
      {filterView === "by_period" && (
        <p className="muted" style={{ fontSize: "0.78rem", margin: "0 0 0.75rem" }}>
          One collector artifact per collection day (same-day re-runs collapsed). Older days soft-archive after the retention window.
        </p>
      )}

      {showForm && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <div className="form-grid">
            <div className="span-2">
              <label className="muted" style={{ fontSize: 11 }}>File *</label>
              <input ref={fileRef} type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              {file && <span className="muted" style={{ fontSize: 11, marginLeft: 8 }}>{file.name} ({fmtSize(file.size)})</span>}
            </div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Name (defaults to filename)</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., AWS IAM Screenshot" /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief description of the evidence" /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Tags (comma-separated)</label><input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="access-control, aws, iam" /></div>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>
      )}

      {loading ? (
        <p className="muted">Loading...</p>
      ) : filtered.length === 0 ? (
        <div className="panel"><div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>{evidence.length === 0 ? "No evidence yet. Upload evidence and map it to framework controls." : "No evidence matches your filters."}</p></div></div>
      ) : (
        <div className="panel">
          {selectedIds.size > 0 && (
            <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "0.5rem 1rem", borderBottom: "1px solid var(--border)", background: "var(--info-soft)" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>{selectedIds.size} selected</span>
              <button className="btn btn-sm btn-success" onClick={() => handleBulkReview("approved")}>Approve All</button>
              <button className="btn btn-sm btn-danger" onClick={() => handleBulkReview("rejected")}>Reject All</button>
              <button className="btn btn-sm btn-ghost" style={{ marginLeft: "auto" }} onClick={() => setSelectedIds(new Set())}>Clear</button>
            </div>
          )}
          <div className="data-table-wrap" style={{ maxHeight: "min(70vh, 720px)" }}>
            <table className="evidence-table">
              <thead>
                <tr>
                  <th style={{ width: 36 }}>
                    <input type="checkbox" checked={paginatedEvidence.length > 0 && paginatedEvidence.every(ev => selectedIds.has(ev.id))} onChange={toggleSelectAll} onClick={(e) => e.stopPropagation()} />
                  </th>
                  <th onClick={() => toggleSort("name")}>Title {sortIndicator("name")}</th>
                  <th onClick={() => toggleSort("evidence_type")}>Type {sortIndicator("evidence_type")}</th>
                  <th onClick={() => toggleSort("review_status")}>Status {sortIndicator("review_status")}</th>
                  <th>Source</th>
                  <th onClick={() => toggleSort("mappings")}>Mappings {sortIndicator("mappings")}</th>
                  <th onClick={() => toggleSort("uploaded_at")}>Date {sortIndicator("uploaded_at")}</th>
                  <th style={{ width: 80 }}></th>
                </tr>
              </thead>
              <tbody>
                {paginatedEvidence.map((ev) => (
                  <React.Fragment key={ev.id}>
                    <tr className={expandedId === ev.id ? "row-expanded" : ""} style={{ cursor: "pointer" }} onClick={() => setExpandedId(expandedId === ev.id ? null : ev.id)}>
                      <td style={{ width: 36 }} onClick={(e) => e.stopPropagation()}>
                        <input type="checkbox" checked={selectedIds.has(ev.id)} onChange={() => {
                          const next = new Set(selectedIds);
                          if (next.has(ev.id)) next.delete(ev.id); else next.add(ev.id);
                          setSelectedIds(next);
                        }} />
                      </td>
                      <td>
                        <span className="cell-title">
                        {ev.display_title || ev.name}
                        </span>
                        {(ev.period_covered || ev.evidence_version) && (
                          <span className="muted" style={{ marginLeft: 6, fontSize: 10 }}>
                            period {ev.period_covered || ev.evidence_version}
                          </span>
                        )}
                      </td>
                      <td>
                        <span className="muted">{ev.evidence_type && ev.evidence_type !== "other" ? ev.evidence_type : "—"}</span>
                      </td>
                      <td>{reviewBadge(ev.review_status || "pending")}</td>
                      <td>
                        {ev.uploaded_by?.startsWith("collector:") ? (
                          <span title={ev.provider ? `Provider: ${ev.provider}` : "Automatically collected"} style={{ display: "inline-flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                            <span className="badge badge-success" style={{ fontSize: 10 }}>Structured (API pull)</span>
                            {ev.source_check && <code style={{ fontSize: 10 }} title={ev.provider || "Collector check"}>{ev.source_check}</code>}
                          </span>
                        ) : (
                          <span className="badge" style={{ fontSize: 10, background: "var(--border-subtle)", color: "var(--muted)" }}>Document (manual)</span>
                        )}
                      </td>
                      <td>
                        <div className="cell-mappings">
                          {(ev.mappings || []).slice(0, 3).map((m) => (
                            <span key={m.id} className="badge" style={{ fontSize: 10, background: "var(--info-soft)", color: "var(--info)", cursor: "pointer" }} onClick={(e) => {
                              e.stopPropagation();
                              if (m.framework_id === "AIGov") return;
                              navigate(`${fwBase}/${m.framework_id === "SOC2" ? "criteria" : "controls"}/${encodeURIComponent(m.control_id)}`);
                            }}>
                              {FW_LABELS[m.framework_id] || m.framework_id}:{m.control_id}
                            </span>
                          ))}
                          {(ev.mappings?.length || 0) > 3 && <span className="muted" style={{ fontSize: 10 }}>+{ev.mappings.length - 3}</span>}
                        </div>
                      </td>
                      <td className="muted">{ev.uploaded_at?.slice(0, 10) || "—"}</td>
                      <td>
                        <button className="btn btn-sm btn-ghost" style={{ fontSize: 16, lineHeight: 1, padding: "2px 6px", cursor: "pointer" }} title="Show details">
                          {expandedId === ev.id ? "▴" : "▾"}
                        </button>
                      </td>
                    </tr>
                    {expandedId === ev.id && (
                      <tr className="evidence-detail-row">
                        <td colSpan={8}>
                          <div className="evidence-detail-panel">
                            {ev.description && <p style={{ margin: "0 0 0.5rem", fontSize: "0.82rem" }}>{ev.description}</p>}
                            <dl className="evidence-detail-grid">
                              <div><dt>Filename</dt><dd>{ev.filename || "—"}</dd></div>
                              <div><dt>Size</dt><dd>{ev.file_size > 0 ? fmtSize(ev.file_size) : "—"}</dd></div>
                              <div><dt>Uploaded by</dt><dd>{ev.uploaded_by || "—"}</dd></div>
                              {ev.source_check && <div><dt>Source check</dt><dd style={{ fontFamily: "monospace", fontSize: 11 }}>{ev.source_check}</dd></div>}
                              {ev.provider && <div><dt>Provider</dt><dd>{ev.provider}</dd></div>}
                              <div><dt>SHA-256</dt><dd style={{ fontFamily: "monospace", fontSize: 11, wordBreak: "break-all" }}>{ev.sha256 ? `${ev.sha256.slice(0, 24)}…` : "—"}</dd></div>
                              {ev.tags?.length > 0 && <div><dt>Tags</dt><dd>{ev.tags.join(", ")}</dd></div>}
                            </dl>
                            {ev.auto_status && (
                              <div style={{ fontSize: "0.8rem", marginBottom: 6, display: "flex", gap: 6, alignItems: "center" }}>
                                {ev.auto_status === "pass" || ev.auto_status === "ok" ? <span className="badge badge-success" style={{ fontSize: 10 }}>PASS</span>
                                  : ev.auto_status === "warn" || ev.auto_status === "warning" ? <span className="badge badge-warning" style={{ fontSize: 10 }}>WARN</span>
                                  : ev.auto_status === "fail" ? <span className="badge badge-danger" style={{ fontSize: 10 }}>FAIL</span>
                                  : <span className="badge badge-danger" style={{ fontSize: 10 }}>ERROR</span>}
                                <AutoSummary summary={ev.auto_summary} />
                              </div>
                            )}
                            {ev.reviewer && ev.reviewed_at && (
                              <div style={{ fontSize: "0.75rem", marginBottom: 6, color: "var(--muted)" }}>
                                Reviewed by {ev.reviewer} on {ev.reviewed_at?.slice(0, 10)}{ev.review_comment ? `: ${ev.review_comment}` : ""}
                              </div>
                            )}
                            <div className="evidence-detail-actions">
                              {ev.filename && (
                                <a className="btn btn-sm btn-secondary" href={apiUrl(`/api/evidence-hub/${ev.id}/download`)} download>Download</a>
                              )}
                              {(ev.mime_type === "application/json" || ev.filename?.endsWith(".json")) && (
                                <button className="btn btn-sm btn-ghost" onClick={async () => {
                                  try {
                                    const r = await hubFetch(`/api/evidence-hub/${ev.id}/content`);
                                    if (!r.ok) return;
                                    setViewingContent({ id: ev.id, filename: ev.filename, data: await r.text() });
                                  } catch { /* ignore */ }
                                }}>View JSON</button>
                              )}
                              {ev.review_status === "pending" && (
                                <>
                                  <button className="btn btn-sm btn-success" onClick={() => handleReview(ev.id, "approved")}>Approve</button>
                                  <button className="btn btn-sm btn-danger" onClick={() => handleReview(ev.id, "rejected")}>Reject</button>
                                </>
                              )}
                              <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)", marginLeft: "auto" }} onClick={() => handleDelete(ev.id)}>Delete</button>
                            </div>
                            <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid var(--border)" }}>
                              <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>Mapped Controls</div>
                              <div style={{ display: "flex", gap: 4, flexWrap: "wrap", alignItems: "center" }}>
                                {(ev.mappings || []).map((m) => (
                                  <span key={m.id} style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: "var(--info-soft, #dbeafe)", color: "var(--info, #1d4ed8)", cursor: "pointer" }} onClick={(e) => {
                                    e.stopPropagation();
                                    if (m.framework_id === "AIGov") return;
                                    navigate(`${fwBase}/${m.framework_id === "SOC2" ? "criteria" : "controls"}/${encodeURIComponent(m.control_id)}`);
                                  }}>
                                    {FW_LABELS[m.framework_id] || m.framework_id}: {m.control_id}
                                    <button style={{ fontSize: 10, padding: 0, cursor: "pointer", border: "none", background: "none", color: "inherit" }} onClick={(e) => { e.stopPropagation(); handleUnmap(ev.id, m.framework_id, m.control_id); }}>×</button>
                                  </span>
                                ))}
                                <button className="btn btn-sm btn-ghost" style={{ fontSize: 10 }} onClick={() => setMapForm(mapForm?.eid === ev.id ? null : { eid: ev.id, fw: "", ctrl: "" })}>+ Map</button>
                              </div>
                              {mapForm?.eid === ev.id && (
                                <div style={{ display: "flex", gap: 4, marginTop: 6, alignItems: "center" }}>
                                  <select value={mapForm.fw} onChange={(e) => setMapForm({ ...mapForm, fw: e.target.value })} style={{ fontSize: 11 }}>
                                    <option value="">Framework</option>
                                    {FW_OPTIONS.map((f) => <option key={f} value={f}>{FW_LABELS[f] || f}</option>)}
                                  </select>
                                  <input value={mapForm.ctrl} onChange={(e) => setMapForm({ ...mapForm, ctrl: e.target.value })} placeholder="Control ID" style={{ fontSize: 11, width: 100 }} />
                                  <button className="btn btn-sm btn-primary" style={{ fontSize: 10 }} onClick={() => { if (mapForm.fw && mapForm.ctrl) { handleMap(ev.id, mapForm.fw, mapForm.ctrl); setMapForm(null); } }}>Save</button>
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pagination-bar">
            <div className="pagination-info">
              Showing {filtered.length === 0 ? 0 : (page - 1) * pageSize + 1}–{Math.min(page * pageSize, filtered.length)} of {filtered.length}
            </div>
            <PaginationPages page={page} totalPages={totalPages} onPageChange={setPage} />
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--muted)" }}>
              <span>Rows:</span>
              <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }} style={{ fontSize: "0.8rem", padding: "2px 4px" }}>
                {[25, 50, 100].map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const coverageTab = tab !== "coverage" ? null : (
    <div>
      {!stats ? (
        <p className="muted">Loading coverage data...</p>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 24 }}>
            <div className="panel" style={{ padding: 16, textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 700 }}>{stats.total_evidence || 0}</div>
              <div className="muted" style={{ fontSize: "0.8rem" }}>Evidence Files</div>
            </div>
            <div className="panel" style={{ padding: 16, textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 700 }}>{stats.total_mappings || 0}</div>
              <div className="muted" style={{ fontSize: "0.8rem" }}>Control Mappings</div>
            </div>
            <div className="panel" style={{ padding: 16, textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 700 }}>{fmtSize(stats.total_file_size || 0)}</div>
              <div className="muted" style={{ fontSize: "0.8rem" }}>Total Storage</div>
            </div>
            <div className="panel" style={{ padding: 16, textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 700 }}>{Object.keys(stats.by_framework || {}).length}</div>
              <div className="muted" style={{ fontSize: "0.8rem" }}>Frameworks</div>
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <a className="btn btn-secondary btn-sm" href={apiUrl("/api/evidence-hub/export")} download>Export All ZIP</a>
          </div>

          {Object.keys(stats.by_framework || {}).length > 0 && (
            <div className="panel" style={{ marginBottom: 24 }}>
              <div className="panel-header"><strong>By Framework</strong></div>
              <div className="panel-body">
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr className="muted" style={{ fontSize: "0.8rem", textAlign: "left" }}>
                      <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Framework</th>
                      <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Evidence</th>
                      <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Controls</th>
                      <th style={{ padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>Mappings</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.by_framework || {}).map(([fw, f]: [string, any]) => (
                      <tr key={fw} style={{ borderBottom: "1px solid var(--border)" }}>
                        <td style={{ padding: "8px 12px", fontWeight: 600 }}>{FW_LABELS[fw] || fw}</td>
                        <td style={{ padding: "8px 12px" }}>{f.evidence_count}</td>
                        <td style={{ padding: "8px 12px" }}>{f.control_count}</td>
                        <td style={{ padding: "8px 12px" }}>{f.mapping_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {Object.keys(stats.by_review_status || {}).length > 0 && (
            <div className="panel">
              <div className="panel-header"><strong>Review Status</strong></div>
              <div className="panel-body">
                {["pending", "approved", "rejected"].map((s) => {
                  const count = stats.by_review_status?.[s] || 0;
                  const total = (Object.values(stats.by_review_status || {}) as number[]).reduce((a, b) => a + b, 0);
                  if (!total) return null;
                  const pct = Math.round((count / total) * 100);
                  const colors: Record<string, string> = { pending: "var(--warning)", approved: "var(--success)", rejected: "var(--danger)" };
                  return (
                    <div key={s} style={{ marginBottom: 8 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: 4 }}>
                        <span style={{ textTransform: "capitalize" }}>{s}</span>
                        <span>{count} ({pct}%)</span>
                      </div>
                      <div style={{ height: 8, background: "var(--border)", borderRadius: 4, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${pct}%`, background: colors[s], borderRadius: 4 }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );

  const requestsTab = tab !== "requests" ? null : (
    <div>
      <div style={{ marginBottom: 12 }}>
        <div className="panel" style={{ padding: 16 }}>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Title *</label><input value={reqForm.title} onChange={(e) => setReqForm({ ...reqForm, title: e.target.value })} placeholder="e.g. MFA evidence for CC6.1" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Control ID</label><input value={reqForm.control_id} onChange={(e) => setReqForm({ ...reqForm, control_id: e.target.value })} placeholder="e.g. CC6.1" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Assigned To</label><input value={reqForm.assigned_to} onChange={(e) => setReqForm({ ...reqForm, assigned_to: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Due Date</label><input type="date" value={reqForm.due_date} onChange={(e) => setReqForm({ ...reqForm, due_date: e.target.value })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea rows={2} value={reqForm.description} onChange={(e) => setReqForm({ ...reqForm, description: e.target.value })} /></div>
          </div>
          <button className="btn btn-primary btn-sm" style={{ marginTop: 8 }} disabled={!reqForm.title || reqSaving} onClick={async () => {
            if (!reqForm.title) return;
            setReqSaving(true);
            try {
              await hubFetch("/api/evidence-hub/requests", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...reqForm, framework_id: filterFw || reqForm.framework_id }) });
              setReqForm({ framework_id: "", control_id: "", title: "", description: "", assigned_to: "", due_date: "" });
              const r = await hubFetch(`/api/evidence-hub/requests${reqQs}`).then((r) => r.json());
              setRequests(r.requests || []);
            } catch { /* ignore */ }
            finally { setReqSaving(false); }
          }}>{reqSaving ? "Creating..." : "Create Request"}</button>
        </div>
      </div>

      {requests.length === 0 ? (
        <p className="muted">No evidence requests. Create one above.</p>
      ) : (
        <div className="panel">
          <div className="panel-body" style={{ padding: 0 }}>
            {requests.map((req: any) => (
              <div key={req.id} style={{ padding: "10px 16px", borderBottom: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                  <div>
                    <strong>{req.title}</strong>
                    <span className="muted" style={{ marginLeft: 8, fontSize: 12 }}>{req.control_id}</span>
                  </div>
                  <span className={`badge ${req.status === "fulfilled" ? "badge-success" : req.status === "cancelled" ? "badge-muted" : "badge-warning"}`}>{req.status}</span>
                </div>
                <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                  {req.assigned_to && <>Assigned to: {req.assigned_to} · </>}
                  {req.due_date && <>Due: {req.due_date} · </>}
                  Created: {req.created_at?.slice(0, 10)}
                </div>
                {req.description && <p style={{ fontSize: 12, margin: "4px 0 0 0", color: "var(--muted)" }}>{req.description}</p>}
                {req.status === "open" && (
                  <div style={{ marginTop: 6 }}>
                    <button className="btn btn-sm btn-success" style={{ marginRight: 6 }} onClick={async () => {
                      await hubFetch(`/api/evidence-hub/requests/${req.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: "fulfilled" }) });
                      const r = await hubFetch(`/api/evidence-hub/requests${reqQs}`).then((r) => r.json());
                      setRequests(r.requests || []);
                    }}>Mark Fulfilled</button>
                    <button className="btn btn-sm btn-ghost" onClick={async () => {
                      await hubFetch(`/api/evidence-hub/requests/${req.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: "cancelled" }) });
                      const r = await hubFetch(`/api/evidence-hub/requests${reqQs}`).then((r) => r.json());
                      setRequests(r.requests || []);
                    }}>Cancel</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Evidence Hub</h2>
      </div>

      <div style={{ display: "flex", gap: 4, marginBottom: 16, borderBottom: "1px solid var(--border)" }}>
        <button className={`btn btn-sm ${tab === "evidence" ? "btn-primary" : "btn-ghost"}`} style={{ borderBottom: tab === "evidence" ? "2px solid var(--primary)" : "none", borderRadius: 0 }} onClick={() => setTab("evidence")}>Evidence</button>
        <button className={`btn btn-sm ${tab === "coverage" ? "btn-primary" : "btn-ghost"}`} style={{ borderBottom: tab === "coverage" ? "2px solid var(--primary)" : "none", borderRadius: 0 }} onClick={() => setTab("coverage")}>Coverage</button>
        <button className={`btn btn-sm ${tab === "requests" ? "btn-primary" : "btn-ghost"}`} style={{ borderBottom: tab === "requests" ? "2px solid var(--primary)" : "none", borderRadius: 0 }} onClick={() => setTab("requests")}>Requests</button>
        <button className={`btn btn-sm ${tab === "automation" ? "btn-primary" : "btn-ghost"}`} style={{ borderBottom: tab === "automation" ? "2px solid var(--primary)" : "none", borderRadius: 0 }} onClick={() => setTab("automation")}>Automation</button>
      </div>

      {evidenceTab}
      {coverageTab}
      {requestsTab}
      {tab === "automation" && (
        <div className="panel" style={{ padding: 16 }}>
          <AutomationCoverageMatrix
            framework={filterFw || "SOC2"}
            onNavigate={(criterionId) => navigate(`${fwBase}/criteria/${encodeURIComponent(criterionId)}`)}
          />
        </div>
      )}

      {viewingContent && (
        <div style={{ position: "fixed", inset: 0, zIndex: 1000, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }} onClick={() => setViewingContent(null)}>
          <div style={{ background: "var(--surface)", borderRadius: "var(--radius)", width: "80vw", maxWidth: 900, maxHeight: "85vh", display: "flex", flexDirection: "column", boxShadow: "0 4px 24px rgba(0,0,0,0.3)" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
              <strong style={{ fontSize: "0.9rem", fontFamily: "monospace" }}>{viewingContent.filename}</strong>
              <div style={{ display: "flex", gap: 8 }}>
                <a className="btn btn-sm btn-ghost" href={apiUrl(`/api/evidence-hub/${viewingContent.id}/download`)} download>Download</a>
                <button className="btn btn-sm btn-ghost" onClick={() => setViewingContent(null)}>×</button>
              </div>
            </div>
            <pre style={{ margin: 0, padding: 16, overflow: "auto", fontSize: "0.8rem", lineHeight: 1.5, whiteSpace: "pre-wrap", wordBreak: "break-all", fontFamily: "monospace", flex: 1 }}>
              {(() => { try { return JSON.stringify(JSON.parse(viewingContent.data), null, 2); } catch { return viewingContent.data; } })()}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
