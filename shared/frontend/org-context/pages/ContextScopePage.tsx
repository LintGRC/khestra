import { useCallback, useEffect, useState } from "react";
import { orgContextApi } from "../api";
import type { ContextRecord, InterestedParty } from "../types";

const EMPTY: ContextRecord = {
  id: "",
  label: "",
  internal_issues: [],
  external_issues: [],
  interested_parties: [],
  climate_relevant: false,
  climate_note: "",
  climate_status: "not_assessed",
  scope_statement: "",
  boundaries: "",
  interfaces_dependencies: [],
  created_at: "",
  updated_at: "",
};

function sectionCard(title: string, subtitle: string, children: React.ReactNode) {
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-body">
        <h4 style={{ margin: "0 0 4px" }}>{title}</h4>
        <p className="muted" style={{ fontSize: 12, marginTop: 0 }}>{subtitle}</p>
        {children}
      </div>
    </div>
  );
}

function IssueList({
  items,
  editable,
  onChange,
  placeholder,
}: {
  items: string[];
  editable: boolean;
  onChange: (items: string[]) => void;
  placeholder: string;
}) {
  const update = (i: number, v: string) => {
    const next = [...items];
    next[i] = v;
    onChange(next);
  };
  if (!editable) {
    if (items.length === 0) return <p className="muted" style={{ fontSize: 13 }}>None recorded.</p>;
    return (
      <ul style={{ margin: "8px 0", paddingLeft: 18 }}>
        {items.filter(Boolean).map((it, i) => (
          <li key={i} style={{ fontSize: 13 }}>{it}</li>
        ))}
      </ul>
    );
  }
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {items.map((it, i) => (
        <div key={i} style={{ display: "flex", gap: 6 }}>
          <input
            value={it}
            onChange={(e) => update(i, e.target.value)}
            placeholder={placeholder}
            style={{ flex: 1 }}
          />
          <button
            className="btn btn-sm btn-ghost"
            style={{ color: "var(--danger)" }}
            onClick={() => onChange(items.filter((_, j) => j !== i))}
          >
            ✕
          </button>
        </div>
      ))}
      <button
        className="btn btn-sm btn-ghost"
        onClick={() => onChange([...items, ""])}
      >
        + Add issue
      </button>
    </div>
  );
}

export default function ContextScopePage() {
  const [records, setRecords] = useState<ContextRecord[]>([]);
  const [record, setRecord] = useState<ContextRecord | null>(null);
  const [stats, setStats] = useState<{ total: number; climate_relevant: number } | null>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<ContextRecord>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(() => {
    orgContextApi.list().then((d) => {
      setRecords(d.records || []);
      setRecord(d.latest || null);
    }).catch(() => setError("Failed to load organizational context."));
    orgContextApi.stats().then(setStats).catch(() => undefined);
  }, []);

  useEffect(() => { load(); }, [load]);

  const startEdit = () => {
    setDraft(record ? JSON.parse(JSON.stringify(record)) : { ...EMPTY });
    setEditing(true);
  };

  const save = async () => {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const body = {
        label: draft.label,
        internal_issues: draft.internal_issues,
        external_issues: draft.external_issues,
        interested_parties: draft.interested_parties,
        climate_relevant: draft.climate_relevant,
        climate_note: draft.climate_note,
        climate_status: draft.climate_status,
        scope_statement: draft.scope_statement,
        boundaries: draft.boundaries,
        interfaces_dependencies: draft.interfaces_dependencies,
      };
      if (record) await orgContextApi.update(record.id, body);
      else await orgContextApi.create(body);
      setNotice("Context & scope saved.");
      setEditing(false);
      load();
    } catch {
      setError("Save failed. Check the fields and try again.");
    } finally {
      setSaving(false);
    }
  };

  const addParty = () =>
    setDraft({ ...draft, interested_parties: [...draft.interested_parties, { name: "", requirements: [], addressed_via_isms: true, notes: "" }] });

  const updateParty = (i: number, patch: Partial<InterestedParty>) => {
    const next = [...draft.interested_parties];
    next[i] = { ...next[i], ...patch };
    setDraft({ ...draft, interested_parties: next });
  };

  const updatePartyRequirements = (i: number, v: string) => {
    updateParty(i, { requirements: v.split("\n").map((s) => s.trim()).filter(Boolean) });
  };

  const removeParty = (i: number) =>
    setDraft({ ...draft, interested_parties: draft.interested_parties.filter((_, j) => j !== i) });

  return (
    <div className="page-stack">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Context & Scope</h2>
          <p className="muted">
            ISO/IEC 27001 clauses 4.1–4.3 · {stats ? `${stats.total} record(s), ${stats.climate_relevant} climate-relevant` : ""}
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => (editing ? setEditing(false) : startEdit())}>
          {editing ? "Cancel" : record ? "Edit" : "+ Record Context"}
        </button>
      </div>

      {draft.climate_relevant && (
        <div className="banner info" style={{ marginBottom: 12 }}>
          Amendment 1 (2024): climate change is recorded as a relevant issue — it must be considered in the Clause 6.1 risk assessment.
        </div>
      )}
      {error && <div className="banner danger" style={{ marginBottom: 12 }}>{error}</div>}
      {notice && <div className="banner success" style={{ marginBottom: 12 }}>{notice}</div>}

      {!record && !editing && (
        <div className="panel">
          <div className="panel-body">
            <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>
              No context &amp; scope record yet. Record the organization's context, interested parties and ISMS scope to satisfy clauses 4.1–4.3.
            </p>
          </div>
        </div>
      )}

      {(record || editing) && (() => {
        const rec = record as ContextRecord;
        return (
        <>
          {sectionCard(
            "Organization & ISMS Context",
            "Clause 4.1 — determine external and internal issues relevant to the ISMS",
            editing ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <input
                  value={draft.label}
                  onChange={(e) => setDraft({ ...draft, label: e.target.value })}
                  placeholder="Record label, e.g. Context analysis 2026"
                />
                <div className="form-grid">
                  <div>
                    <label className="muted" style={{ fontSize: 11 }}>Internal issues</label>
                    <IssueList
                      items={draft.internal_issues}
                      editable
                      onChange={(items) => setDraft({ ...draft, internal_issues: items })}
                      placeholder="e.g. rapid cloud adoption, staff turnover"
                    />
                  </div>
                  <div>
                    <label className="muted" style={{ fontSize: 11 }}>External issues</label>
                    <IssueList
                      items={draft.external_issues}
                      editable
                      onChange={(items) => setDraft({ ...draft, external_issues: items })}
                      placeholder="e.g. regulatory changes, supply chain risk"
                    />
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                  <label style={{ fontSize: 13 }}>Amd 1:2024 — climate-change relevance:</label>
                  <select
                    value={draft.climate_status}
                    onChange={(e) => {
                      const s = e.target.value as ContextRecord["climate_status"];
                      setDraft({ ...draft, climate_status: s, climate_relevant: s === "relevant" });
                    }}
                    style={{ fontSize: 13 }}
                  >
                    <option value="not_assessed">Not assessed</option>
                    <option value="not_relevant">Determined not relevant</option>
                    <option value="relevant">Relevant</option>
                  </select>
                </div>
                {draft.climate_status === "relevant" && (
                  <input
                    value={draft.climate_note}
                    onChange={(e) => setDraft({ ...draft, climate_note: e.target.value })}
                    placeholder="Climate note — how climate change affects the ISMS (clause 4.1 / 4.2)"
                  />
                )}
              </div>
            ) : (
              <div>
                <p style={{ fontSize: 13 }}><strong>{rec.label || "Context record"}</strong> · updated {rec.updated_at?.slice(0, 10) || "—"}</p>
                <div className="form-grid">
                  <div>
                    <label className="muted" style={{ fontSize: 11 }}>Internal issues</label>
                    <IssueList items={rec.internal_issues} editable={false} onChange={() => undefined} placeholder="" />
                  </div>
                  <div>
                    <label className="muted" style={{ fontSize: 11 }}>External issues</label>
                    <IssueList items={rec.external_issues} editable={false} onChange={() => undefined} placeholder="" />
                  </div>
                </div>
                {(rec.climate_status ?? (rec.climate_relevant ? "relevant" : "not_assessed")) !== "not_assessed" && (
                  <p style={{ fontSize: 13, marginTop: 8 }}>
                    <span className={`badge ${rec.climate_status === "relevant" ? "badge-warning" : "badge-success"}`}>
                      Climate change: {rec.climate_status === "relevant" ? "relevant" : rec.climate_status === "not_relevant" ? "not relevant" : "not assessed"}
                    </span>{" "}
                    {rec.climate_note && <span className="muted">{rec.climate_note}</span>}
                  </p>
                )}
              </div>
            )
          )}

          {sectionCard(
            "Interested Parties",
            "Clause 4.2 — determine relevant interested parties and their information security requirements",
            editing ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {draft.interested_parties.map((p, i) => (
                  <div key={i} style={{ border: "1px solid var(--border-subtle)", borderRadius: 8, padding: 10 }}>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <input
                        value={p.name}
                        onChange={(e) => updateParty(i, { name: e.target.value })}
                        placeholder="Party name, e.g. Customers, Regulators"
                        style={{ flex: 1 }}
                      />
                      <label style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <input
                          type="checkbox"
                          checked={p.addressed_via_isms}
                          onChange={(e) => updateParty(i, { addressed_via_isms: e.target.checked })}
                        />
                        addressed via ISMS
                      </label>
                      <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => removeParty(i)}>✕</button>
                    </div>
                    <textarea
                      value={(p.requirements || []).join("\n")}
                      onChange={(e) => updatePartyRequirements(i, e.target.value)}
                      placeholder="Requirements (one per line)"
                      style={{ width: "100%", minHeight: 48, marginTop: 6 }}
                    />
                  </div>
                ))}
                <button className="btn btn-sm btn-ghost" onClick={addParty}>+ Add interested party</button>
              </div>
            ) : rec.interested_parties.length === 0 ? (
              <p className="muted" style={{ fontSize: 13 }}>None recorded.</p>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left" }}>
                    <th style={{ padding: "0.5rem" }}>Party</th>
                    <th style={{ padding: "0.5rem" }}>Requirements</th>
                    <th style={{ padding: "0.5rem" }}>Addressed via ISMS</th>
                  </tr>
                </thead>
                <tbody>
                  {rec.interested_parties.map((p, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                      <td style={{ padding: "0.5rem", fontWeight: 500 }}>{p.name}</td>
                      <td style={{ padding: "0.5rem", fontSize: 12 }}>
                        {(p.requirements || []).join(" · ") || "—"}
                        {p.notes ? <span className="muted"> ({p.notes})</span> : null}
                      </td>
                      <td style={{ padding: "0.5rem" }}>
                        {p.addressed_via_isms ? <span className="badge badge-success">Yes</span> : <span className="badge badge-muted">No</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}

          {sectionCard(
            "ISMS Scope",
            "Clause 4.3 — boundaries and applicability of the ISMS",
            editing ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <textarea
                  value={draft.scope_statement}
                  onChange={(e) => setDraft({ ...draft, scope_statement: e.target.value })}
                  placeholder="Scope statement — what the ISMS covers"
                  style={{ width: "100%", minHeight: 64 }}
                />
                <textarea
                  value={draft.boundaries}
                  onChange={(e) => setDraft({ ...draft, boundaries: e.target.value })}
                  placeholder="Boundaries — locations, systems, processes in/out of scope"
                  style={{ width: "100%", minHeight: 48 }}
                />
                <IssueList
                  items={draft.interfaces_dependencies}
                  editable
                  onChange={(items) => setDraft({ ...draft, interfaces_dependencies: items })}
                  placeholder="Interfaces and dependencies with other processes/systems"
                />
              </div>
            ) : (
              <div>
                {rec.scope_statement && <p style={{ fontSize: 13 }}><strong>Scope:</strong> {rec.scope_statement}</p>}
                {rec.boundaries && <p style={{ fontSize: 13 }}><strong>Boundaries:</strong> {rec.boundaries}</p>}
                {rec.interfaces_dependencies.length > 0 && (
                  <p style={{ fontSize: 13 }}>
                    <strong>Interfaces/dependencies:</strong> {rec.interfaces_dependencies.join(" · ")}
                  </p>
                )}
                {!rec.scope_statement && !rec.boundaries && rec.interfaces_dependencies.length === 0 && (
                  <p className="muted" style={{ fontSize: 13 }}>None recorded.</p>
                )}
              </div>
            )
          )}

          {editing && (
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-primary" onClick={save} disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
              <button className="btn btn-ghost" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          )}

          {records.length > 1 && (
            <p className="muted" style={{ fontSize: 12, marginTop: 12 }}>
              {records.length} context records — the latest is shown. Older records are kept for audit history.
            </p>
          )}
        </>
        );
      })()}
    </div>
  );
}
