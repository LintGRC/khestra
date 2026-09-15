import { useCallback, useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api, type ControlEvidenceItem, type EvidenceGuidance, type SoaRow, type Sufficiency } from "../api";

const STATUSES = ["implemented", "partially implemented", "not implemented", "excluded"];
const STATUS_CLASSES: Record<string, string> = {
  implemented: "em-implemented",
  "partially implemented": "em-partial",
  "not implemented": "em-not-implemented",
  excluded: "em-excluded",
};

function sufficiencyClass(level?: string) {
  const m: Record<string, string> = {
    comprehensive: "badge-success",
    adequate: "badge-info",
    minimal: "badge-warning",
    insufficient: "badge-danger",
  };
  return m[level || ""] || "badge-muted";
}

export default function SoaDetail() {
  const { id } = useParams();
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(iso27001)/)?.[0] ?? "";
  const [row, setRow] = useState<SoaRow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [guidance, setGuidance] = useState<EvidenceGuidance | null>(null);
  const [evidence, setEvidence] = useState<ControlEvidenceItem[]>([]);
  const [sufficiency, setSufficiency] = useState<Sufficiency | null>(null);
  const [findings, setFindings] = useState<Array<{ id: string; title: string; severity: string; status: string }>>([]);

  const load = useCallback(() => {
    setError(null);
    setSaveError(null);
    if (!id) {
      setError("Control not found");
      return;
    }
    api.getSoa(id)
      .then(setRow)
      .catch((e) => setError(String(e)));
    api.evidenceGuidance(id).then(setGuidance).catch(() => setGuidance(null));
    api.controlEvidence(id).then(setEvidence).catch(() => setEvidence([]));
    api.controlSufficiency(id).then(setSufficiency).catch(() => setSufficiency(null));
    api
      .findingsForControl(id)
      .then((rows) => setFindings(rows))
      .catch(() => setFindings([]));
  }, [id]);

  useEffect(load, [load]);

  const patch = async (fields: Record<string, unknown>) => {
    if (!row) return;
    setSaving(true);
    setSavedAt(null);
    setSaveError(null);
    try {
      const updated = await api.updateSoa(row.control_id, fields);
      setRow(updated);
      setSavedAt(updated.updated_at);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  if (error) {
    return (
      <div className="page-stack">
        <div className="banner error">{error}</div>
        <p>
          <Link to={`${fwBase}/soa`}>← Back to SoA</Link>
        </p>
      </div>
    );
  }
  if (!row) return <div>Loading…</div>;

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <div className="muted" style={{ fontSize: 13, marginBottom: 4 }}>
            <Link to={`${fwBase}/soa`}>SoA</Link> / {row.section}
          </div>
          <h2>{row.control_id} — {row.title}</h2>
          <p>{row.summary}</p>
        </div>
        <span className={`pill ${STATUS_CLASSES[row.status] ?? ""}`}>{row.status}</span>
      </section>

      {savedAt && <div className="banner success">Saved at {savedAt}</div>}
      {saveError && (
        <div className="banner error">
          Save failed: {saveError}{" "}
          <button type="button" className="btn-link" onClick={() => setSaveError(null)}>
            Dismiss
          </button>
        </div>
      )}

      <section className="card">
        <h3 style={{ marginTop: 0 }}>Implementation status</h3>
        <div className="button-row">
          {STATUSES.map((s) => (
            <button
              key={s}
              type="button"
              className={`btn btn-sm ${row.status === s ? "btn-primary" : "btn-secondary"}`}
              onClick={() => {
                if (s === "excluded" && !row.justification.trim()) {
                  setSaveError("Exclusion requires a justification (ISO 27001 clause 6.1.3).");
                  return;
                }
                const fields: Record<string, unknown> = { status: s };
                if (s === "excluded") fields.applicable = false;
                patch(fields);
              }}
              disabled={saving}
            >
              {s}
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <label className="label" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            checked={row.applicable}
            onChange={(e) => {
              if (!e.target.checked && !row.justification.trim()) {
                setSaveError("Exclusion requires a justification (ISO 27001 clause 6.1.3).");
                return;
              }
              patch({ applicable: e.target.checked });
            }}
            disabled={saving}
          />
          Applicable to the organization
        </label>
      </section>

      <section className="card">
        <h3 style={{ marginTop: 0 }}>Justification / notes</h3>
        <textarea
          className="textarea"
          rows={5}
          value={row.justification}
          placeholder={
            row.applicable
              ? "Describe how this control is implemented, or why it is not yet applied."
              : "Explain why this control is not applicable / is excluded."
          }
          onBlur={(e) => {
            if (e.target.value !== row.justification) {
              patch({ justification: e.target.value }).catch(() => {});
            }
          }}
        />
        <p className="muted" style={{ fontSize: 12 }}>
          Changes are saved when the field loses focus. If the save fails, a banner will appear above.
        </p>
      </section>

      {row.doc_link && (
        <p className="muted" style={{ fontSize: 12 }}>
          Guidance: {row.doc_link}
        </p>
      )}

      {row.attributes && (() => {
        const labels: Record<string, string> = {
          control_type: "Control type",
          properties: "Information security properties",
          concepts: "Cybersecurity concepts",
          capabilities: "Operational capabilities",
          domains: "Security domains",
        };
        const groups = Object.entries(labels).filter(([k]) => (row.attributes?.[k]?.length ?? 0) > 0);
        if (groups.length === 0) return null;
        return (
          <section className="card">
            <h3 style={{ marginTop: 0 }}>Attributes (ISO/IEC 27002:2022)</h3>
            {groups.map(([k, label]) => (
              <div key={k} style={{ marginBottom: 8 }}>
                <span className="muted" style={{ fontSize: 12, marginRight: 8 }}>{label}:</span>
                {(row.attributes?.[k] ?? []).map((v) => (
                  <span key={v} className="badge badge-muted" style={{ marginRight: 4 }}>
                    {v.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            ))}
          </section>
        );
      })()}
      {(guidance || evidence.length > 0 || sufficiency) && (
        <section className="card">
          <h3 style={{ marginTop: 0 }}>
            Evidence &amp; Guidance{" "}
            {sufficiency && (
              <span className={`badge ${sufficiencyClass(sufficiency.level)}`} style={{ marginLeft: 8 }}>
                sufficiency {sufficiency.score}/100 · {sufficiency.level}
              </span>
            )}
          </h3>

          {evidence.length > 0 && (
            <>
              <p className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
                {evidence.length} linked evidence item{evidence.length !== 1 ? "s" : ""} (Evidence Hub)
              </p>
              <ul style={{ margin: "0 0 12px", paddingLeft: 18, fontSize: 13 }}>
                {evidence.map((e) => (
                  <li key={e.id} style={{ marginBottom: 4 }}>
                    <Link to={`${fwBase}/evidence`}>{e.display_title || e.name}</Link>{" "}
                    <span className={`badge ${e.review_status === "approved" ? "badge-success" : e.review_status === "pending" ? "badge-warning" : "badge-muted"}`}>
                      {e.review_status}
                    </span>
                    {e.period_covered && <span className="muted" style={{ fontSize: 11 }}> · {e.period_covered}</span>}
                  </li>
                ))}
              </ul>
            </>
          )}

          {guidance && guidance.items.length > 0 && (
            <>
              <p className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
                Suggested evidence to gather for this control
              </p>
              <ul style={{ margin: "0 0 12px", paddingLeft: 18, fontSize: 13 }}>
                {guidance.items.map((it, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>{it}</li>
                ))}
              </ul>
            </>
          )}

          {guidance && (guidance.collectors.length > 0 || guidance.tests.length > 0) && (
            <div style={{ fontSize: 12, marginTop: 4 }}>
              {guidance.collectors.length > 0 && (
                <p className="muted" style={{ margin: "4px 0" }}>
                  Automated collectors:{" "}
                  {guidance.collectors.map((c) => (
                    <span key={c} className="badge badge-muted" style={{ marginRight: 4 }}>{c}</span>
                  ))}
                </p>
              )}
              {guidance.tests.length > 0 && (
                <p className="muted" style={{ margin: "4px 0" }}>
                  Control tests:{" "}
                  {guidance.tests.map((t) => (
                    <span key={t} className="badge badge-info" style={{ marginRight: 4 }}>{t}</span>
                  ))}
                </p>
              )}
              {guidance.modules.length > 0 && (
                <p className="muted" style={{ margin: "4px 0" }}>
                  Where it lives: {guidance.modules.join(" · ")}
                </p>
              )}
            </div>
          )}
        </section>
      )}

      {(row.linked_risks || []).length > 0 && (
        <section className="panel">
          <div className="panel-body">
            <h3 style={{ marginBottom: 8 }}>Risks that selected this control</h3>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
              {row.linked_risks!.map((r) => (
                <li key={r.id} style={{ marginBottom: 4 }}>
                  <Link to={`${fwBase}/risks`}>{r.title || r.id}</Link>{" "}
                  <span className="badge badge-muted">{r.status}</span>
                  {r.treatment ? <span className="badge badge-info" style={{ marginLeft: 4 }}>{r.treatment}</span> : null}
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {findings.length > 0 && (
        <section className="panel">
          <div className="panel-body">
            <h3 style={{ marginBottom: 8 }}>Open findings for this control</h3>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
              {findings.map((f) => (
                <li key={f.id} style={{ marginBottom: 4 }}>
                  <Link to={`${fwBase}/findings`}>{f.title}</Link>{" "}
                  <span className={`badge ${
                    f.severity === "high" ? "badge-danger" : f.severity === "medium" ? "badge-warning" : "badge-info"
                  }`}>
                    {f.severity}
                  </span>{" "}
                  <span className="badge badge-muted">{f.status}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </div>
  );
}