import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { apiUrl } from "@shared/apiPrefix";
import { authHeaders } from "@shared/accessToken";

type TestRun = {
  id: string;
  test_id: string;
  run_date: string;
  result: string;
  notes: string;
  evidence_hub_id: string;
  evidence_title: string;
  run_by: string;
  actual_rpo_minutes: number | null;
  actual_rto_minutes: number | null;
  verified_by: string;
  created_at: string;
  met_rpo?: boolean | null;
  met_rto?: boolean | null;
  has_evidence?: boolean;
};

type ControlTest = {
  id: string;
  title: string;
  control_id: string;
  framework: string;
  frequency: string;
  owner: string;
  active: boolean;
  target_rpo_minutes: number | null;
  target_rto_minutes: number | null;
  commitment: string;
  run_count: number;
  last_run: TestRun | null;
  next_due: string;
  overdue: boolean;
  expected_per_year: number;
  runs_without_evidence: number;
};

type EvidenceItem = { id: string; display_title?: string; name?: string; filename?: string };

const FREQUENCIES = ["monthly", "quarterly", "semi_annual", "annual"] as const;

const RESULT_BADGE: Record<string, string> = {
  passed: "badge-success",
  failed: "badge-danger",
  deferred: "badge-warning",
};

function cap(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

async function ctFetch(path: string, init?: RequestInit): Promise<any> {
  const headers = await authHeaders();
  const r = await fetch(apiUrl(path), {
    ...init,
    headers: { ...(init?.headers || {}), ...headers, "Content-Type": "application/json" },
  });
  if (!r.ok) throw new Error(String(r.status));
  return r.json();
}

export default function ControlTestsPage({ frameworkId = "" }: { frameworkId?: string }) {
  const [tests, setTests] = useState<ControlTest[]>([]);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", control_id: "", framework: frameworkId, frequency: "quarterly", owner: "", target_rpo_minutes: "", target_rto_minutes: "" });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [runsOpen, setRunsOpen] = useState<Record<string, TestRun[] | null>>({});
  const [runForm, setRunForm] = useState<{ test_id: string; run_date: string; result: string; notes: string; evidence_hub_id: string; actual_rpo_minutes: string; actual_rto_minutes: string; verified_by: string } | null>(null);
  const [runSaving, setRunSaving] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const fwBase = location.pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";

  const refresh = () =>
    ctFetch(`/api/control-tests${frameworkId ? `?framework=${encodeURIComponent(frameworkId)}` : ""}`)
      .then((d) => setTests(d.tests || []))
      .catch(() => setError("Unable to load control tests."))
      .finally(() => setLoading(false));

  useEffect(() => {
    refresh();
    ctFetch(`/api/evidence-hub?limit=100${frameworkId ? `&framework_id=${encodeURIComponent(frameworkId)}` : ""}`)
      .then((d) => setEvidence(d.evidence || []))
      .catch(() => setEvidence([]));
  }, [frameworkId]);

  if (loading) return <p className="muted">Loading control tests…</p>;
  if (error && tests.length === 0)
    return (
      <div className="panel">
        <div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>{error}</p></div>
      </div>
    );

  const overdue = tests.filter((t) => t.overdue);
  const upcoming = tests.filter((t) => !t.overdue && t.next_due);
  const today = new Date().toISOString().slice(0, 10);

  const submitTest = async () => {
    if (!form.title.trim()) { setFormError("Title is required"); return; }
    setFormError(null);
    setSaving(true);
    try {
      const payload = {
        ...form,
        target_rpo_minutes: form.target_rpo_minutes ? Number(form.target_rpo_minutes) : null,
        target_rto_minutes: form.target_rto_minutes ? Number(form.target_rto_minutes) : null,
      };
      if (editingId) {
        await ctFetch(`/api/control-tests/${editingId}`, { method: "PATCH", body: JSON.stringify(payload) });
      } else {
        await ctFetch("/api/control-tests", { method: "POST", body: JSON.stringify(payload) });
      }
      setShowForm(false);
      setEditingId(null);
      setForm({ title: "", control_id: "", framework: frameworkId, frequency: "quarterly", owner: "", target_rpo_minutes: "", target_rto_minutes: "" });
      await refresh();
    } catch {
      setFormError("Save failed.");
    } finally {
      setSaving(false);
    }
  };

  const submitRun = async () => {
    if (!runForm) return;
    setRunSaving(true);
    try {
      const item = evidence.find((e) => e.id === runForm.evidence_hub_id);
      await ctFetch(`/api/control-tests/${runForm.test_id}/runs`, {
        method: "POST",
        body: JSON.stringify({
          run_date: runForm.run_date || today,
          result: runForm.result,
          notes: runForm.notes,
          evidence_hub_id: runForm.evidence_hub_id,
          evidence_title: item ? String(item.display_title || item.name || item.filename || "") : "",
          run_by: "",
          actual_rpo_minutes: runForm.actual_rpo_minutes ? Number(runForm.actual_rpo_minutes) : null,
          actual_rto_minutes: runForm.actual_rto_minutes ? Number(runForm.actual_rto_minutes) : null,
          verified_by: runForm.verified_by,
        }),
      });
      setRunForm(null);
      await refresh();
    } catch {
      setRunForm(null);
    } finally {
      setRunSaving(false);
    }
  };

  const toggleRuns = async (t: ControlTest) => {
    const cur = runsOpen[t.id];
    if (cur === undefined || cur === null) {
      try {
        const d = await ctFetch(`/api/control-tests/${t.id}/runs`);
        setRunsOpen((m) => ({ ...m, [t.id]: d.runs || [] }));
      } catch {
        setRunsOpen((m) => ({ ...m, [t.id]: [] }));
      }
    } else {
      setRunsOpen((m) => ({ ...m, [t.id]: null }));
    }
  };

  const del = async (t: ControlTest) => {
    if (!window.confirm(`Delete "${t.title}" and its run history?`)) return;
    try {
      await ctFetch(`/api/control-tests/${t.id}`, { method: "DELETE" });
      await refresh();
    } catch {
      setError("Delete failed.");
    }
  };

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Control tests</h2>
        <p className="muted">Recurring evidence-producing activities (e.g. backup restore tests) with run logs — your policy says a frequency, this page proves the runs.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 20 }}>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{tests.length}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Tests</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--danger)" }}>{overdue.length}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Overdue</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--success)" }}>{upcoming.length}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>On schedule</div>
        </div>
        <div className="panel" style={{ padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{tests.reduce((n, t) => n + t.run_count, 0)}</div>
          <div className="muted" style={{ fontSize: "0.8rem" }}>Runs logged</div>
        </div>
      </div>

      {!showForm ? (
        <button className="btn btn-primary" onClick={() => { setEditingId(null); setShowForm(true); }}>
          New test
        </button>
      ) : (
        <div className="panel" style={{ marginBottom: 20 }}>
          <div className="panel-header">
            <strong>{editingId ? "Edit test" : "New test"}</strong>
            <button className="btn btn-sm btn-ghost" onClick={() => { setShowForm(false); setEditingId(null); }}>Cancel</button>
          </div>
          <div className="panel-body" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 10 }}>
            <input className="input" placeholder="Title (e.g. Restore test — production DB)" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <input className="input" placeholder="Control ID (e.g. 3.10.4 / A1.2)" value={form.control_id} onChange={(e) => setForm({ ...form, control_id: e.target.value })} />
            <input className="input" placeholder="Framework" value={form.framework} onChange={(e) => setForm({ ...form, framework: e.target.value })} />
            <select className="input" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
              {FREQUENCIES.map((f) => <option key={f} value={f}>{cap(f)}</option>)}
            </select>
            <input className="input" placeholder="Owner" value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} />
            <input className="input" type="number" min={1} placeholder="Target RPO (min) — optional" value={form.target_rpo_minutes} onChange={(e) => setForm({ ...form, target_rpo_minutes: e.target.value })} />
            <input className="input" type="number" min={1} placeholder="Target RTO (min) — optional" value={form.target_rto_minutes} onChange={(e) => setForm({ ...form, target_rto_minutes: e.target.value })} />
            <button className="btn btn-primary" disabled={saving} onClick={submitTest}>{saving ? "Saving…" : editingId ? "Save changes" : "Create test"}</button>
            {formError && <span style={{ color: "var(--danger)", fontSize: "0.8rem" }}>{formError}</span>}
          </div>
        </div>
      )}

      {tests.length === 0 ? (
        <div className="panel">
          <div className="panel-body"><p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No control tests recorded for this framework yet.</p></div>
        </div>
      ) : (
        tests.map((t) => {
          const runs = runsOpen[t.id];
          return (
            <div className="panel" key={t.id} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 220 }}>
                  <strong>{t.title}</strong>
                  <div className="muted" style={{ fontSize: "0.75rem", display: "flex", gap: 8, flexWrap: "wrap", marginTop: 2 }}>
                    {t.control_id && <span className={`badge badge-muted`}>{t.control_id}</span>}
                    {t.framework && <span className="badge badge-success">{t.framework}</span>}
                    <span>{cap(t.frequency)}</span>
                    {t.commitment && <span className="badge badge-info">{t.commitment}</span>}
                    {t.owner && <span>Owner: {t.owner}</span>}
                    <span>{t.run_count} run{t.run_count === 1 ? "" : "s"} logged · {t.expected_per_year}/yr expected</span>
                    {t.runs_without_evidence > 0 && (
                      <span style={{ color: "var(--warning, #b8860b)" }} title="Runs without linked evidence — auditors will ask why">
                        ⚠ {t.runs_without_evidence} run{t.runs_without_evidence === 1 ? "" : "s"} without evidence
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  {t.overdue ? (
                    <span style={{ color: "var(--danger)", fontSize: "0.85rem", fontWeight: 600 }}>
                      Overdue — was due {t.next_due}
                    </span>
                  ) : t.next_due ? (
                    <span className="muted" style={{ fontSize: "0.85rem" }}>Next due {t.next_due}</span>
                  ) : (
                    <span className="muted" style={{ fontSize: "0.85rem" }}>No due date</span>
                  )}
                  {t.last_run && (
                    <div style={{ fontSize: "0.75rem", marginTop: 2 }}>
                      Last: {t.last_run.run_date} <span className={`badge ${RESULT_BADGE[t.last_run.result] || "badge-muted"}`}>{t.last_run.result}</span>
                    </div>
                  )}
                </div>
              </div>
              <div style={{ display: "flex", gap: 6, padding: "0 14px 10px" }}>
                <button className="btn btn-sm btn-primary" onClick={() => setRunForm({ test_id: t.id, run_date: today, result: "passed", notes: "", evidence_hub_id: "", actual_rpo_minutes: "", actual_rto_minutes: "", verified_by: "" })}>Log run</button>
                <button className="btn btn-sm btn-ghost" onClick={() => toggleRuns(t)}>Runs ({t.run_count})</button>
                <button className="btn btn-sm btn-ghost" onClick={() => { setEditingId(t.id); setForm({ title: t.title, control_id: t.control_id, framework: t.framework, frequency: t.frequency, owner: t.owner, target_rpo_minutes: t.target_rpo_minutes != null ? String(t.target_rpo_minutes) : "", target_rto_minutes: t.target_rto_minutes != null ? String(t.target_rto_minutes) : "" }); setShowForm(true); }}>Edit</button>
                <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => del(t)}>Delete</button>
              </div>

              {runs != null && (
                <div style={{ borderTop: "1px solid var(--border-subtle)" }}>
                  {runs.length === 0 ? (
                    <p className="muted" style={{ padding: "10px 14px", fontSize: "0.8rem" }}>No runs logged yet.</p>
                  ) : (
                    runs.map((r) => (
                      <div key={r.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 14px", borderBottom: "1px solid var(--border-subtle)", fontSize: "0.85rem", flexWrap: "wrap" }}>
                        <span className={`badge ${RESULT_BADGE[r.result] || "badge-muted"}`}>{r.result}</span>
                        <span>{r.run_date}</span>
                        {r.actual_rto_minutes != null && (
                          r.met_rto == null ? (
                            <span className={`badge ${t.target_rto_minutes != null ? "badge-info" : "badge-muted"}`}>RTO {r.actual_rto_minutes}m</span>
                          ) : r.met_rto ? (
                            <span className="badge badge-success" title="Recovery within target">RTO {r.actual_rto_minutes}m ✓</span>
                          ) : (
                            <span className="badge badge-danger" title="Missed target — explain in notes">RTO {r.actual_rto_minutes}m ✗ (target {t.target_rto_minutes}m)</span>
                          )
                        )}
                        {r.actual_rpo_minutes != null && (
                          r.met_rpo == null ? (
                            <span className="badge badge-muted">RPO {r.actual_rpo_minutes}m</span>
                          ) : r.met_rpo ? (
                            <span className="badge badge-success" title="Data loss within target">RPO {r.actual_rpo_minutes}m ✓</span>
                          ) : (
                            <span className="badge badge-danger" title="Missed target — explain in notes">RPO {r.actual_rpo_minutes}m ✗ (target {t.target_rpo_minutes}m)</span>
                          )
                        )}
                        {r.notes && <span className="muted" style={{ flex: 1 }}>{r.notes}</span>}
                        {r.has_evidence ? (
                          <button className="btn-link" onClick={() => navigate(`${fwBase}/evidence`)} title={r.evidence_title || r.evidence_hub_id}>
                            Evidence ↗
                          </button>
                        ) : (
                          <span className="badge badge-warning" title="No evidence linked — JEngErik: artifacts ready at due date, not last minute">No evidence</span>
                        )}
                        {r.verified_by && <span className="muted" title="Business/verification sign-off">✓ {r.verified_by}</span>}
                        {r.run_by && <span className="muted">{r.run_by}</span>}
                      </div>
                    ))
                  )}
                </div>
              )}

              {runForm && runForm.test_id === t.id && (
                <div style={{ borderTop: "1px solid var(--border-subtle)", padding: 12, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
                  <input className="input" type="date" value={runForm.run_date} onChange={(e) => setRunForm({ ...runForm, run_date: e.target.value })} />
                  <select className="input" value={runForm.result} onChange={(e) => setRunForm({ ...runForm, result: e.target.value })}>
                    <option value="passed">Passed</option>
                    <option value="failed">Failed</option>
                    <option value="deferred">Deferred</option>
                  </select>
                  <input className="input" placeholder="Notes (e.g. restored 1.2 TB, checksums OK)" value={runForm.notes} onChange={(e) => setRunForm({ ...runForm, notes: e.target.value })} />
                  <input className="input" type="number" min={0} placeholder="Actual RTO (min)" value={runForm.actual_rto_minutes} onChange={(e) => setRunForm({ ...runForm, actual_rto_minutes: e.target.value })} />
                  <input className="input" type="number" min={0} placeholder="Actual RPO (min)" value={runForm.actual_rpo_minutes} onChange={(e) => setRunForm({ ...runForm, actual_rpo_minutes: e.target.value })} />
                  <input className="input" placeholder="Verified by (e.g. Finance sign-off)" value={runForm.verified_by} onChange={(e) => setRunForm({ ...runForm, verified_by: e.target.value })} />
                  {evidence.length > 0 ? (
                    <select className="input" value={runForm.evidence_hub_id} onChange={(e) => setRunForm({ ...runForm, evidence_hub_id: e.target.value })}>
                      <option value="">Link evidence (optional)</option>
                      {evidence.map((e) => (
                        <option key={e.id} value={e.id}>{String(e.display_title || e.name || e.filename || e.id).slice(0, 60)}</option>
                      ))}
                    </select>
                  ) : (
                    <input className="input" disabled placeholder="No evidence hub items to link" />
                  )}
                  <button className="btn btn-primary" disabled={runSaving} onClick={submitRun}>{runSaving ? "Logging…" : "Log run"}</button>
                  <button className="btn btn-sm btn-ghost" onClick={() => setRunForm(null)}>Cancel</button>
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
