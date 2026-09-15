import { FormEvent, useEffect, useState } from "react";
import { api, AuditPeriod, EvidenceManifest, PeriodCoverage, Soc2Engagement, apiUrl } from "../api";
import { useLayout } from "../Layout";
import PageIntro from "../components/PageIntro";
import { PageSkeleton, EmptyState } from "../components/ui/Skeleton";

export default function AuditPage() {
  const { canEdit } = useLayout();
  const [periods, setPeriods] = useState<AuditPeriod[]>([]);
  const [manifest, setManifest] = useState<EvidenceManifest | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", start_date: "", end_date: "" });
  const [saving, setSaving] = useState(false);
  const [freezing, setFreezing] = useState<string | null>(null);
  const [coverage, setCoverage] = useState<PeriodCoverage | null>(null);
  const [engagement, setEngagement] = useState<Soc2Engagement>({
    type: "",
    firm: "",
    cpa_contact: "",
    engagement_start: "",
    engagement_end: "",
    status: "",
  });
  const [engSaved, setEngSaved] = useState(false);

  const reload = async () => {
    const [pData, mData, cov, eng] = await Promise.all([
      api.auditPeriods(),
      api.manifest(),
      api.evidenceCoverage().catch(() => null),
      api.auditEngagement().catch(() => ({ engagement: null })),
    ]);
    setPeriods(pData.periods);
    setManifest(mData);
    setCoverage(cov);
    if (eng?.engagement) setEngagement(eng.engagement);
  };

  useEffect(() => {
    reload().catch(console.error).finally(() => setLoading(false));
  }, []);

  const onSaveEngagement = async (e: FormEvent) => {
    e.preventDefault();
    setEngSaved(false);
    try {
      const res = await api.putAuditEngagement(engagement);
      setEngagement(res.engagement);
      setEngSaved(true);
    } catch {
      /* surface via banner below */
    }
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.start_date || !form.end_date) return;
    setSaving(true);
    try {
      await api.createAuditPeriod(form);
      setForm({ name: "", start_date: "", end_date: "" });
      setShowForm(false);
      await reload();
    } finally {
      setSaving(false);
    }
  };

  const onFreeze = async (periodId: string) => {
    if (!window.confirm("Freeze evidence? No further edits will be allowed for this period.")) return;
    setFreezing(periodId);
    try {
      await api.freezeAuditPeriod(periodId);
      await reload();
    } finally {
      setFreezing(null);
    }
  };

  if (loading) return <PageSkeleton variant="default" />;

  return (
    <div className="page-stack">
      <PageIntro title="Audit Periods" summary="Define Type II audit windows, freeze evidence at period end, and generate the evidence manifest for your auditor." />

      <div className="panel">
        <div className="panel-header">
          <strong>Engagement (SOC 2 report)</strong>
        </div>
        <div className="panel-body">
          {engSaved && <div className="banner success">Engagement saved — reflected in the System Description report.</div>}
          <form className="form-grid" onSubmit={onSaveEngagement}>
            <div>
              <label htmlFor="eng-type">Report type</label>
              <select
                id="eng-type"
                value={engagement.type}
                disabled={!canEdit}
                onChange={(e) => setEngagement({ ...engagement, type: e.target.value })}
              >
                <option value="">— select —</option>
                <option value="type1">Type I</option>
                <option value="type2">Type II</option>
              </select>
              <p className="muted" style={{ fontSize: 12, marginTop: 6 }}>
                Type I is design at a point in time. Type II requires an engagement window and
                operating-effectiveness PASS on MET controls before readiness.
              </p>
            </div>
            <div>
              <label htmlFor="eng-firm">CPA firm</label>
              <input
                id="eng-firm"
                type="text"
                value={engagement.firm}
                disabled={!canEdit}
                onChange={(e) => setEngagement({ ...engagement, firm: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="eng-contact">CPA contact</label>
              <input
                id="eng-contact"
                type="text"
                value={engagement.cpa_contact}
                disabled={!canEdit}
                onChange={(e) => setEngagement({ ...engagement, cpa_contact: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="eng-start">Engagement start</label>
              <input
                id="eng-start"
                type="date"
                value={engagement.engagement_start}
                disabled={!canEdit}
                onChange={(e) => setEngagement({ ...engagement, engagement_start: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="eng-end">Engagement end</label>
              <input
                id="eng-end"
                type="date"
                value={engagement.engagement_end}
                disabled={!canEdit}
                onChange={(e) => setEngagement({ ...engagement, engagement_end: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="eng-status">Engagement status</label>
              <select
                id="eng-status"
                value={engagement.status}
                disabled={!canEdit}
                onChange={(e) => setEngagement({ ...engagement, status: e.target.value })}
              >
                <option value="">— select —</option>
                <option value="planning">Planning</option>
                <option value="fieldwork">Fieldwork</option>
                <option value="report">Report in progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            {canEdit && (
              <div className="btn-row" style={{ gridColumn: "1 / -1" }}>
                <button type="submit" className="btn-primary">Save engagement</button>
              </div>
            )}
          </form>
        </div>
      </div>

      <div className="stats stats-compact">
        <div className="stat-card">
          <div className="stat-label">Total evidence</div>
          <div className="stat-value">{manifest?.total_evidence ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Controls covered (all)</div>
          <div className="stat-value">{manifest?.controls_covered ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Period coverage</div>
          <div className="stat-value" style={{ color: (coverage?.coverage_pct ?? 0) >= 80 ? "var(--success)" : (coverage?.coverage_pct ?? 0) >= 30 ? "var(--warning)" : "var(--danger)" }}>
            {coverage ? `${coverage.coverage_pct}%` : "—"}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active periods</div>
          <div className="stat-value">{periods.filter((p) => !p.frozen).length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Frozen periods</div>
          <div className="stat-value">{periods.filter((p) => p.frozen).length}</div>
        </div>
      </div>

      {coverage && (
        <div className="panel" style={{ borderLeft: "3px solid var(--primary)" }}>
          <div className="panel-header">
            <strong>Evidence coverage — {coverage.period_name}</strong>
            <span className="muted">{coverage.coverage_pct}% ({coverage.controls_covered}/{coverage.total_controls} controls)</span>
          </div>
          <div className="panel-body">
            <div style={{ width: "100%", background: "var(--border)", borderRadius: 6, height: 10, overflow: "hidden", marginBottom: 12 }}>
              <div style={{ width: `${coverage.coverage_pct}%`, height: "100%", borderRadius: 6, background: coverage.coverage_pct >= 80 ? "var(--success)" : coverage.coverage_pct >= 30 ? "var(--warning)" : "var(--danger)", transition: "width 0.5s" }} />
            </div>
            <p className="muted" style={{ fontSize: 12 }}>
              Controls with evidence whose validity range overlaps the audit period. Add valid_from/valid_to dates when uploading evidence to improve accuracy.
            </p>
          </div>
        </div>
      )}

      {canEdit && (
        <div className="controls-toolbar">
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "New period"}
          </button>
        </div>
      )}

      {showForm && (
        <form className="panel panel-form" onSubmit={onSubmit}>
          <div className="panel-body">
          <label>
            Period name
            <input
              required
              placeholder="e.g. FY 2026 Type II"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </label>
          <div className="form-row">
            <label>
              Start date
              <input
                type="date"
                required
                value={form.start_date}
                onChange={(e) => setForm((f) => ({ ...f, start_date: e.target.value }))}
              />
            </label>
            <label>
              End date
              <input
                type="date"
                required
                value={form.end_date}
                onChange={(e) => setForm((f) => ({ ...f, end_date: e.target.value }))}
              />
            </label>
          </div>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Creating…" : "Create period"}
          </button>
          </div>
        </form>
      )}

      {periods.length === 0 ? (
        <EmptyState
          title="No audit periods"
          description="Create your first Type II audit period to track evidence collection against a date range."
        />
      ) : (
        <div className="panel-stack">
          {periods.map((p) => (
            <div key={p.id} className={`panel ${p.frozen ? "panel-frozen" : "panel-active"}`}>
              <div className="panel-header">
                <strong>{p.name}</strong>
                {p.frozen ? (
                  <span className="badge badge-success">Frozen</span>
                ) : (
                  <span className="badge badge-info">Active</span>
                )}
              </div>
              <div className="panel-body">
                <div className="request-meta">
                  <span>{p.start_date} → {p.end_date}</span>
                  {p.frozen_at && <span className="muted">Frozen: {p.frozen_at}</span>}
                  <span className="muted">Created: {p.created_at}</span>
                </div>
                {!p.frozen && canEdit && (
                  <div className="request-actions">
                    <button
                      className="btn btn-primary btn-sm"
                      disabled={freezing === p.id}
                      onClick={() => onFreeze(p.id)}
                    >
                      {freezing === p.id ? "Freezing…" : "Freeze evidence"}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {manifest && manifest.total_evidence > 0 && (
        <div className="panel section-spaced">
          <div className="panel-header">
            <strong>Evidence manifest</strong>
            <span className="muted">SHA-256: {manifest.manifest_hash.slice(0, 16)}…</span>
          </div>
          <div className="panel-body">
            <p className="muted">
              Generated {manifest.generated_at}. {manifest.total_evidence} files across {manifest.controls_covered} criteria.
            </p>
            <div className="request-actions">
              <a className="btn btn-secondary btn-sm" href={apiUrl("/api/reports/evidence-index")}>Download CSV</a>
              <a className="btn btn-secondary btn-sm" href={apiUrl("/api/reports/audit-package")}>Download ZIP package</a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
