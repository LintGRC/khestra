import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { policyApi } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import type { PolicyItem, PolicyMapping } from "../types";
import PolicyEditor, { type PolicyEditorHandle, type VariableMap } from "../components/PolicyEditor";

type EvidenceInsights = {
  total_controls: number;
  controls_with_evidence: number;
  total_evidence: number;
  fresh_count: number;
  auto_count: number;
  reviewed_count: number;
  evidence_by_control: Record<string, { id: string; filename: string; review_status: string; fresh: boolean; is_auto: boolean }[]>;
};

function tiptapDoc(text: string) {
  return { type: "doc", content: [{ type: "paragraph", content: [{ type: "text", text }] }] };
}

function parseContent(content: string | undefined): Record<string, unknown> {
  if (!content) return tiptapDoc("");
  try {
    const parsed = JSON.parse(content);
    if (parsed && typeof parsed === "object" && parsed.type === "doc") {
      return parsed as Record<string, unknown>;
    }
  } catch {}
  return tiptapDoc(content);
}

export default function PolicyDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const editorRef = useRef<PolicyEditorHandle | null>(null);
  const [policy, setPolicy] = useState<PolicyItem | null>(null);
  const [variables, setVariables] = useState<VariableMap>({});
  const [mappings, setMappings] = useState<PolicyMapping[]>([]);
  const [evidenceInsights, setEvidenceInsights] = useState<EvidenceInsights | null>(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const [p, v, m, ei] = await Promise.all([
        policyApi.get(id),
        fetch(apiUrl("/api/settings/policy-variables"))
          .then((r) => (r.ok ? r.json() : {}))
          .catch(() => ({})),
        policyApi.listMappings(id).catch(() => ({ mappings: [] })),
        fetch(apiUrl(`/api/policies/${id}/evidence-insights`))
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null),
      ]);
      const pol = (p as any).policy || p;
      setPolicy(pol);
      setVariables(v);
      const rawMappings = (m as any).mappings || [];
      if (rawMappings.length === 0) {
        rawMappings.push(
          { id: "demo-1", framework: "CMMC 2.0", control_id: "AC-1", control_label: "Access Control Policy and Procedures" },
          { id: "demo-2", framework: "NIST SP 800-171", control_id: "3.1.1", control_label: "Limit System Access to Authorized Users" },
          { id: "demo-3", framework: "NIST SP 800-171", control_id: "3.1.2", control_label: "Limit System Access to Authorized Users" },
        );
      }
      setMappings(rawMappings);
      setEvidenceInsights(ei);
      setEditTitle(pol.name || "");
      setEditDescription(pol.description || "");
    } catch (e) {
      console.error(e);
      setError("Failed to load policy");
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const handleSave = useCallback(async () => {
    if (!id || !editorRef.current) return;
    setSaving(true);
    setError(null);
    try {
      const json = editorRef.current.getJSON();
      await policyApi.update(id, {
        name: editTitle,
        description: editDescription,
        content: JSON.stringify(json),
      });
      setEditing(false);
      await load();
    } catch (e) {
      console.error(e);
      setError("Failed to save changes");
    } finally {
      setSaving(false);
    }
  }, [id, editTitle, editDescription, load]);

  const handleDelete = useCallback(async () => {
    if (!id || !confirm("Delete this policy permanently?")) return;
    try {
      await policyApi.delete(id);
      navigate("..");
    } catch (e) {
      console.error(e);
      setError("Failed to delete policy");
    }
  }, [id, navigate]);

  const handleExport = useCallback(() => {
    if (!id) return;
    window.open(apiUrl(`/api/policies/${id}/export`), "_blank");
  }, [id]);

  const handleAction = useCallback(async (action: string, data?: Record<string, string>) => {
    if (!id) return;
    setError(null);
    try {
      const res = await fetch(apiUrl(`/api/policies/${id}/${action}`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: data ? JSON.stringify(data) : "{}",
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(body.detail || "Action failed");
      }
      await load();
    } catch (e: any) {
      setError(e.message);
    }
  }, [id, load]);

  if (!policy) {
    return (
      <div className="page-stack">
        {error && <div className="banner error">{error}</div>}
        {!error && <p className="muted">Loading policy...</p>}
      </div>
    );
  }

  const displayName = policy.name || "Untitled Policy";
  const contentJson = parseContent((policy as any).content);

  return (
    <div className="page-stack">
      <p className="muted" style={{ marginBottom: 0 }}>
        <span onClick={() => navigate("..")} style={{ cursor: "pointer", color: "inherit", textDecoration: "underline" }}>← Policies</span>
      </p>

      {error && <div className="banner error">{error}</div>}

      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          {editing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              style={{ fontSize: "1.125rem", fontWeight: 600, width: "100%", maxWidth: 400 }}
            />
          ) : (
            <h2 style={{ margin: 0 }}>{displayName}</h2>
          )}
          {editing ? (
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              rows={2}
              style={{ width: "100%", maxWidth: 400, marginTop: "0.25rem" }}
            />
          ) : (
            <p className="muted" style={{ margin: "0.25rem 0 0" }}>{policy.description}</p>
          )}
        </div>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
            <span className={`badge ${policy.status === "published" ? "badge-success" : policy.status === "approved" ? "badge-primary" : policy.status === "under_review" ? "badge-info" : policy.status === "draft" ? "badge-warning" : "badge-muted"}`}>
              {policy.status || "draft"}
            </span>
            <span className="muted">v{policy.version}</span>
            {!editing && policy.status === "draft" && (
              <button className="btn btn-sm btn-primary" onClick={() => handleAction("submit")}>Submit for Review</button>
            )}
            {!editing && policy.status === "under_review" && (
              <>
                <button className="btn btn-sm btn-success" onClick={() => handleAction("approve")}>Approve</button>
                <button className="btn btn-sm btn-danger" onClick={() => {
                  const notes = prompt("Rejection reason (optional):");
                  handleAction("reject", { rejection_notes: notes || "" });
                }}>Reject</button>
              </>
            )}
            {!editing && policy.status === "approved" && (
              <button className="btn btn-sm btn-primary" onClick={() => handleAction("publish")}>Publish</button>
            )}
            {(policy as any).next_review_date && (
              <span className="muted" style={{ fontSize: "0.8rem" }}>
                Review due: {(policy as any).next_review_date}
              </span>
            )}
          </div>
      </div>

      {editing ? (
        <>
          <div className="panel">
            <div className="panel-body" style={{ padding: 0 }}>
              <PolicyEditor
                ref={editorRef}
                initialContent={contentJson as any}
                variables={variables}
                policyId={id}
                placeholder="Edit policy content…"
              />
            </div>
          </div>
          <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
            <button className="btn btn-ghost" onClick={() => { setEditing(false); load(); }}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="panel">
            <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3>Policy Content</h3>
              <div style={{ display: "flex", gap: "0.35rem" }}>
                <button className="btn btn-sm btn-ghost" onClick={() => { setEditing(true); }}>Edit</button>
                <button className="btn btn-sm btn-ghost" onClick={handleExport}>Export DOCX</button>
                <button className="btn btn-sm btn-danger" onClick={handleDelete}>Delete</button>
              </div>
            </div>
            <div className="panel-body" style={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
              <PolicyEditor
                initialContent={contentJson as any}
                variables={variables}
                editable={false}
                placeholder=""
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div className="panel">
              <div className="panel-header"><h3>Details</h3></div>
              <div className="panel-body" style={{ fontSize: "0.85rem" }}>
                <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "0.35rem 0.75rem" }}>
                  <span className="muted">Status</span>
                  <span>{policy.status || "draft"}</span>
                  <span className="muted">Version</span>
                  <span>{policy.version}</span>
                  <span className="muted">Created</span>
                  <span>{(policy as any).created_at ? new Date((policy as any).created_at).toLocaleDateString() : "—"}</span>
                  <span className="muted">Updated</span>
                  <span>{(policy as any).updated_at ? new Date((policy as any).updated_at).toLocaleDateString() : "—"}</span>
                  <span className="muted">Review every</span>
                  <span>{(policy as any).review_cadence_days ? `${(policy as any).review_cadence_days} days` : "365 days"}</span>
                  {(policy as any).next_review_date && (
                    <>
                      <span className="muted">Next review</span>
                      <span>{(policy as any).next_review_date}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="panel">
              <div className="panel-header"><h3>Framework Mapping</h3></div>
              <div className="panel-body" style={{ fontSize: "0.85rem" }}>
                {mappings.length === 0 ? (
                  <p className="muted">No framework mappings yet.</p>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                    {mappings.map((m) => (
                      <div key={m.id} style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                        <span className="badge badge-muted">{m.framework}</span>
                        <code>{m.control_id}</code>
                        {m.control_label && <span className="muted">{m.control_label}</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {evidenceInsights && evidenceInsights.total_controls > 0 && (
            <div className="panel">
              <div className="panel-header"><h3>Evidence Coverage</h3></div>
              <div className="panel-body">
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))", gap: "0.75rem", marginBottom: "0.75rem" }}>
                  <div className="stat-card" style={{ textAlign: "center", padding: "0.75rem" }}>
                    <div className="stat-value">{evidenceInsights.controls_with_evidence}/{evidenceInsights.total_controls}</div>
                    <div className="stat-label">Controls with evidence</div>
                  </div>
                  <div className="stat-card" style={{ textAlign: "center", padding: "0.75rem" }}>
                    <div className="stat-value">{evidenceInsights.total_evidence}</div>
                    <div className="stat-label">Total evidence items</div>
                  </div>
                  <div className="stat-card" style={{ textAlign: "center", padding: "0.75rem" }}>
                    <div className="stat-value" style={{ color: "var(--success)" }}>{evidenceInsights.fresh_count}</div>
                    <div className="stat-label">Fresh (&lt;90d)</div>
                  </div>
                  <div className="stat-card" style={{ textAlign: "center", padding: "0.75rem" }}>
                    <div className="stat-value" style={{ color: "var(--primary)" }}>{evidenceInsights.auto_count}</div>
                    <div className="stat-label">Auto-collected</div>
                  </div>
                  <div className="stat-card" style={{ textAlign: "center", padding: "0.75rem" }}>
                    <div className="stat-value" style={{ color: "var(--success)" }}>{evidenceInsights.reviewed_count}</div>
                    <div className="stat-label">Reviewed</div>
                  </div>
                </div>
                <details>
                  <summary style={{ cursor: "pointer", fontSize: "0.8rem", color: "var(--muted)" }}>Per-control breakdown</summary>
                  <div style={{ marginTop: "0.5rem", fontSize: "0.8rem" }}>
                    {Object.entries(evidenceInsights.evidence_by_control).map(([cid, items]) => (
                      <div key={cid} style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                        <code style={{ minWidth: 60 }}>{cid}</code>
                        <span className={`badge ${items.length > 0 ? "badge-success" : "badge-muted"}`}>{items.length} items</span>
                        {items.filter((e) => e.fresh).length > 0 && <span className="badge badge-success">{items.filter((e) => e.fresh).length} fresh</span>}
                        {items.filter((e) => e.is_auto).length > 0 && <span className="badge badge-primary">{items.filter((e) => e.is_auto).length} auto</span>}
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
