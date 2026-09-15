import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { policyApi } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import type { PolicyItem, AttestationItem, TemplateItem } from "../types";
import { LIVE_FRAMEWORKS } from "../types";
import CrossFrameworkMappingPanel from "./CrossFrameworkMappingPanel";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";
import "../policy-dashboard.css";

function initialFramework(_defaultFramework?: string): string {
  const fromUrl = new URLSearchParams(window.location.search).get("framework");
  if (fromUrl) return fromUrl;
  return "";
}

export default function PolicyDashboard({ defaultFramework, hideHeader = false }: { defaultFramework?: string; hideHeader?: boolean }) {
  const navigate = useNavigate();
  const [, setSearchParams] = useSearchParams();
  const [policies, setPolicies] = useState<PolicyItem[]>([]);
  const [attestations, setAttestations] = useState<AttestationItem[]>([]);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dueReview, setDueReview] = useState<{ overdue: number; upcoming: number }>({ overdue: 0, upcoming: 0 });
  const [attesting, setAttesting] = useState<Record<string, boolean>>({});
  const [generating, setGenerating] = useState<Record<string, boolean>>({});
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const [selectedPolicyId, setSelectedPolicyId] = useState<string | null>(null);
  const [frameworkFilter, setFrameworkFilter] = useState(initialFramework(defaultFramework));
  const [sort, setSort] = useState<{ col: "name" | "version" | "controls" | "attestations" | "updated"; dir: "asc" | "desc" }>({ col: "updated", dir: "desc" });
  const toggleSort = (col: typeof sort.col) => {
    setSort((prev) => ({ col, dir: prev.col === col && prev.dir === "asc" ? "desc" : "asc" }));
  };

  const load = async () => {
    const [p, a, t, dr] = await Promise.all([
      policyApi.list(frameworkFilter || undefined),
      policyApi.attestations(),
      policyApi.templates(),
      fetch(apiUrl("/api/policies/due-review"))
        .then((r) => (r.ok ? r.json() : { policies: [], count: 0 }))
        .catch(() => ({ policies: [], count: 0 })),
    ]);
    setPolicies(p.policies || []);
    setAttestations(a.attestations || []);
    setTemplates(t.templates || []);
    const due = dr.policies || [];
    setDueReview({
      overdue: due.filter((d: any) => d.urgency === "overdue").length,
      upcoming: due.filter((d: any) => d.urgency === "upcoming").length,
    });
  };

  useEffect(() => {
    load()
      .catch((e) => {
        console.error(e);
        setError("Failed to load policies. Is the backend running?");
      })
      .finally(() => setLoading(false));
  }, [frameworkFilter]);

  async function handleGenerate(policyId: string, templateKey: string) {
    setGenerating((p) => ({ ...p, [policyId]: true }));
    try {
      await policyApi.generate(policyId, templateKey);
      navigate(policyId);
    } catch (err) {
      console.error(err);
      setError(`Generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
    setGenerating((p) => ({ ...p, [policyId]: false }));
  }

  async function handleAttest(policyId: string) {
    setAttesting((p) => ({ ...p, [policyId]: true }));
    try {
      await policyApi.attest({ policy_id: policyId, user_name: "" });
      await load();
    } catch (err) {
      console.error(err);
    }
    setAttesting((p) => ({ ...p, [policyId]: false }));
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this policy and all its attestations?")) return;
    try {
      await policyApi.delete(id);
      if (selectedPolicyId === id) setSelectedPolicyId(null);
      await load();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleSaveContent(policyId: string) {
    try {
      await policyApi.update(policyId, { content: editContent });
      await load();
      setEditingId(null);
      setEditContent("");
    } catch (err) {
      console.error(err);
    }
  }

  function startEdit(policy: PolicyItem) {
    setEditingId(policy.id);
    setEditContent(policy.content || "");
  }

  function attestStatus(policyId: string) {
    const atts = attestations.filter((a) => a.policy_id === policyId);
    if (atts.length === 0) return { count: 0, latest: null };
    const sorted = [...atts].sort((a, b) => b.date.localeCompare(a.date));
    return { count: atts.length, latest: sorted[0] };
  }

  const [searchQuery, setSearchQuery] = useState("");

  const filteredPolicies = policies.filter((p) => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!p.name.toLowerCase().includes(q) && !(p.description || "").toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const sortedPolicies = [...filteredPolicies].sort((a, b) => {
    switch (sort.col) {
      case "version":
        return sort.dir === "asc" ? a.version.localeCompare(b.version) : b.version.localeCompare(a.version);
      case "controls":
        return sort.dir === "asc" ? a.mapped_controls.length - b.mapped_controls.length : b.mapped_controls.length - a.mapped_controls.length;
      case "attestations": {
        const ca = attestStatus(a.id).count;
        const cb = attestStatus(b.id).count;
        return sort.dir === "asc" ? ca - cb : cb - ca;
      }
      case "updated": {
        const da = a.updated_at || "";
        const db = b.updated_at || "";
        const cmp = da.localeCompare(db);
        return sort.dir === "asc" ? cmp : -cmp;
      }
      default: {
        const na = (a.name || "").toLowerCase();
        const nb = (b.name || "").toLowerCase();
        const cmp = na.localeCompare(nb);
        return sort.dir === "asc" ? cmp : -cmp;
      }
    }
  });

  if (loading)
    return (
      <div className="page-stack">
        <p className="muted">Loading...</p>
      </div>
    );
  if (error)
    return (
      <div className="page-stack">
        <div className="banner error">{error}</div>
      </div>
    );

  const selectedPolicy = selectedPolicyId
    ? policies.find((p) => p.id === selectedPolicyId)
    : null;

  if (selectedPolicy) {
    return (
      <div className="page-stack">
        <div>
          <div>
            <button className="btn btn-sm btn-ghost policy-back-btn" onClick={() => setSelectedPolicyId(null)}>
              &larr; Back to all policies
            </button>
            <h2>{selectedPolicy.name}</h2>
            <p className="muted">
              v{selectedPolicy.version} &middot; Updated {selectedPolicy.updated_at?.slice(0, 10)}
            </p>
          </div>
        </div>

        <div className="panel">
          <div className="panel-body">
            <p>{selectedPolicy.description}</p>
            <div className="policy-detail-controls">
              {selectedPolicy.mapped_controls.map((cid) => (
                <code key={cid} style={{ fontSize: "0.75rem" }}>{cid}</code>
              ))}
            </div>
          </div>
        </div>

        {editingId === selectedPolicy.id ? (
          <div className="panel">
            <div className="panel-header">Content Editor</div>
            <div className="panel-body">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={14}
                className="policy-monospace"
              />
              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                <button className="btn btn-sm btn-primary" onClick={() => handleSaveContent(selectedPolicy.id)}>
                  Save
                </button>
                <button className="btn btn-sm btn-ghost" onClick={() => { setEditingId(null); setEditContent(""); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        ) : selectedPolicy.content ? (
          <div className="panel">
            <div className="panel-header">
              Document Content
              <button className="btn btn-sm btn-ghost" style={{ marginLeft: "auto" }} onClick={() => startEdit(selectedPolicy)}>
                Edit
              </button>
            </div>
            <div className="panel-body">
              <pre className="policy-monospace" style={{ whiteSpace: "pre-wrap", margin: 0 }}>
                {selectedPolicy.content}
              </pre>
            </div>
          </div>
        ) : null}

        <CrossFrameworkMappingPanel policyId={selectedPolicy.id} />

        <div className="panel">
          <div className="panel-header">Attestations</div>
          <div className="panel-body">
            {(() => {
              const st = attestStatus(selectedPolicy.id);
              return st.count > 0 ? (
                <div className="policy-ack-row">
                  {st.count} attestation(s) &middot;
                  Last: {st.latest?.date?.slice(0, 10)} by {st.latest?.user_name || "\u2014"}
                </div>
              ) : (
                <p className="muted policy-ack-row">No attestations yet</p>
              );
            })()}
            <button
              className="btn btn-sm btn-primary"
              style={{ marginTop: "0.5rem" }}
              onClick={() => handleAttest(selectedPolicy.id)}
              disabled={attesting[selectedPolicy.id]}
            >
              {attesting[selectedPolicy.id] ? "..." : "Acknowledge"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="policy-header">
        {!hideHeader && (
          <div>
            <h2>Policies &amp; Attestations</h2>
            <div className="policy-header-meta">
              <span className="badge badge-muted">{policies.length} policies</span>
              <span className="badge badge-muted">{attestations.length} attestations</span>
              <span className="badge badge-muted">{templates.length} templates</span>
            </div>
          </div>
        )}
      </div>

      {(dueReview.overdue > 0 || dueReview.upcoming > 0) && (
        <div className={`banner ${dueReview.overdue > 0 ? "error" : "info"}`} style={{ marginBottom: "0.75rem" }}>
          {dueReview.overdue > 0 ? (
            <span><strong>{dueReview.overdue}</strong> polic{dueReview.overdue === 1 ? "y" : "ies"} overdue for review.</span>
          ) : (
            <span><strong>{dueReview.upcoming}</strong> polic{dueReview.upcoming === 1 ? "y" : "ies"} due for review within 30 days.</span>
          )}
          {dueReview.overdue > 0 && dueReview.upcoming > 0 && (
            <span> Also <strong>{dueReview.upcoming}</strong> upcoming.</span>
          )}
        </div>
      )}

      <FilterBar>
        <FilterSelect value={frameworkFilter} onChange={(v) => { setFrameworkFilter(v); setSearchParams(v ? { framework: v } : {}, { replace: true }); }} options={[{ value: "", label: "All frameworks" }, ...LIVE_FRAMEWORKS.map((fw) => ({ value: fw.id, label: fw.shortLabel }))]} placeholder="All frameworks" />
        <FilterSearch value={searchQuery} onChange={setSearchQuery} placeholder="Search policies…" />
        <button className="btn btn-primary" style={{ marginLeft: "auto" }} onClick={() => navigate("new")}>+ New Policy</button>
      </FilterBar>

      {filteredPolicies.length === 0 ? (
        <div className="panel">
          <div className="panel-body">
            <div className="empty-state">
              <p className="empty-state-title">{searchQuery ? "No policies match your search." : "No policies defined yet."}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="panel policy-table-wrap">
          <table className="policy-table">
            <thead>
              <tr>
                <th style={{ cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort("name")}>
                  Policy Name {sort.col === "name" ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                </th>
                <th style={{ width: 60, cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort("version")}>
                  Ver {sort.col === "version" ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                </th>
                <th style={{ cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort("controls")}>
                  Controls {sort.col === "controls" ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                </th>
                <th style={{ width: 100, cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort("attestations")}>
                  Attestations {sort.col === "attestations" ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                </th>
                <th style={{ width: 90, cursor: "pointer", userSelect: "none" }} onClick={() => toggleSort("updated")}>
                  Updated {sort.col === "updated" ? (sort.dir === "asc" ? "↑" : "↓") : ""}
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedPolicies.map((p) => {
                const status = attestStatus(p.id);
                const hasContent = (p.content || "").length > 0;
                return (
                  <tr key={p.id} onClick={() => navigate(p.id)}>
                    <td>
                      <div className="policy-name">{p.name}</div>
                      {p.description && <div className="policy-name-desc">{p.description}</div>}
                    </td>
                    <td>
                      <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>v{p.version}</span>
                    </td>
                    <td>
                      <div className="policy-controls">
                        {p.mapped_controls.slice(0, 4).map((cid) => (
                          <code key={cid} style={{ fontSize: "0.75rem" }}>{cid}</code>
                        ))}
                        {p.mapped_controls.length > 4 && <span className="muted" style={{ fontSize: "0.75rem" }}>+{p.mapped_controls.length - 4}</span>}
                      </div>
                    </td>
                    <td className="policy-attest-cell">
                      {status.count > 0 ? (
                        <div>
                          <div className="policy-attest-count">{status.count}</div>
                          <div className="policy-attest-date">{status.latest?.date?.slice(0, 10)}</div>
                        </div>
                      ) : (
                        <span className="muted policy-empty-cell">—</span>
                      )}
                    </td>
                    <td className="policy-date-cell">
                      {p.updated_at ? p.updated_at.slice(0, 10) : "—"}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <div className="policy-actions" onClick={(e) => e.stopPropagation()}>
                        {!hasContent ? (
                          <select value="" onChange={(e) => { if (e.target.value) handleGenerate(p.id, e.target.value); }} disabled={generating[p.id]}>
                            <option value="">Generate</option>
                            {templates
                              .filter((t) => !frameworkFilter || t.framework_tags?.some((tag) => tag.toLowerCase() === frameworkFilter || tag.toLowerCase().includes(frameworkFilter)))
                              .map((t) => (
                                <option key={t.key} value={t.key}>{t.short_name}</option>
                              ))}
                          </select>
                        ) : (
                          <a href={`${policyApi.exportUrl(p.id)}?client_id=default`} target="_blank" rel="noopener noreferrer" title="Download">&#x2193;</a>
                        )}
                        <button onClick={() => handleAttest(p.id)} disabled={attesting[p.id]} title="Attest">{attesting[p.id] ? "…" : "\u2713"}</button>
                        <button className="delete-btn" onClick={() => handleDelete(p.id)} title="Delete">&#x2715;</button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}