import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { exceptionApi } from "../api";
import { EXCEPTION_TEMPLATES } from "../templates";

export default function ExceptionCreate({
  title = "Exception",
  basePath = "/exceptions",
  initialForm: externalInitial,
}: {
  title?: string;
  basePath?: string;
  initialForm?: Partial<{
    title: string;
    description: string;
    framework: string;
    control_id: string;
    control_reference: string;
    owner: string;
    likelihood: number;
    impact: number;
  }>;
}) {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: externalInitial?.title ?? "",
    description: externalInitial?.description ?? "",
    framework: externalInitial?.framework ?? "SOC2",
    control_id: externalInitial?.control_id ?? "",
    control_reference: externalInitial?.control_reference ?? "",
    likelihood: externalInitial?.likelihood ?? 1,
    impact: externalInitial?.impact ?? 1,
    compensating_controls: "",
    owner: externalInitial?.owner ?? "",
    expiry_days: 90,
  });

  const riskScore = form.likelihood * form.impact;
  const riskLevel =
    riskScore >= 15 ? "critical" : riskScore >= 10 ? "high" : riskScore >= 5 ? "medium" : "low";
  const riskColor =
    riskLevel === "critical"
      ? "var(--danger)"
      : riskLevel === "high"
        ? "var(--danger)"
        : riskLevel === "medium"
          ? "var(--warning)"
          : "var(--success)";

  const selectTemplate = (id: string) => {
    const t = EXCEPTION_TEMPLATES.find((t) => t.id === id);
    if (t) {
      setForm({
        title: t.title,
        description: t.description,
        framework: t.framework,
        control_id: t.control_reference,
        control_reference: t.control_reference,
        likelihood: t.likelihood,
        impact: t.impact,
        compensating_controls: t.compensating_controls,
        owner: "",
        expiry_days: t.expiry_days,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      setError("Title and description are required");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const res = await exceptionApi.create({
        title: form.title,
        description: form.description,
        framework: form.framework,
        control_id: form.control_id,
        control_reference: form.control_reference,
        likelihood: form.likelihood,
        impact: form.impact,
        compensating_controls: form.compensating_controls,
        owner: form.owner,
        expiry_days: form.expiry_days,
      });
      navigate(`${basePath}/${res.exception.id}`);
    } catch (err) {
      console.error(err);
      setError(`Failed to create ${title.toLowerCase()}. Check the backend.`);
    } finally {
      setSaving(false);
    }
  };

  const update = (field: string, value: string | number) =>
    setForm((f) => ({ ...f, [field]: value }));

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>New {title}</h2>
        <button className="btn btn-sm btn-ghost" onClick={() => navigate(-1)}>
          Cancel
        </button>
      </div>

      {error && <div className="banner error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="panel">
          <div className="panel-header"><h3>Start from Template</h3></div>
          <div className="panel-body">
            <select
              value=""
              onChange={(e) => selectTemplate(e.target.value)}
              style={{ width: "100%" }}
            >
              <option value="">— Blank —</option>
              {EXCEPTION_TEMPLATES.map((t) => (
                <option key={t.id} value={t.id}>{t.label} ({t.control_reference})</option>
              ))}
            </select>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><h3>{title} Details</h3></div>
          <div className="panel-body panel-form">
            <label>
              Title <span style={{ color: "var(--danger)" }}>*</span>
              <input
                value={form.title}
                onChange={(e) => update("title", e.target.value)}
                placeholder="e.g., MFA not supported on legacy payroll server"
                required
              />
            </label>
            <label>
              Description <span style={{ color: "var(--danger)" }}>*</span>
              <textarea
                rows={4}
                value={form.description}
                onChange={(e) => update("description", e.target.value)}
                placeholder="Describe the exception, why it exists, and what remediation is planned"
                required
              />
            </label>
            <div className="form-row">
              <label>
                Framework
                <select value={form.framework} onChange={(e) => update("framework", e.target.value)}>
                  {["SOC2", "CMMC", "AI Gov", "NIST 800-171", "ISO 27001", "HIPAA", "PCI-DSS"].map(
                    (f) => (
                      <option key={f} value={f}>{f}</option>
                    ),
                  )}
                </select>
              </label>
              <label>
                Control Reference
                <input
                  value={form.control_reference}
                  onChange={(e) => update("control_reference", e.target.value)}
                  placeholder="e.g., CC6.1"
                />
              </label>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><h3>Risk Assessment</h3></div>
          <div className="panel-body panel-form">
            <div className="form-row">
              <label>
                Likelihood
                <select value={form.likelihood} onChange={(e) => update("likelihood", Number(e.target.value))}>
                  {[
                    [1, "Very Unlikely"],
                    [2, "Unlikely"],
                    [3, "Possible"],
                    [4, "Likely"],
                    [5, "Very Likely"],
                  ].map(([v, l]) => (
                    <option key={v} value={v}>{v} — {l}</option>
                  ))}
                </select>
              </label>
              <label>
                Impact
                <select value={form.impact} onChange={(e) => update("impact", Number(e.target.value))}>
                  {[
                    [1, "Negligible"],
                    [2, "Minor"],
                    [3, "Moderate"],
                    [4, "Major"],
                    [5, "Severe"],
                  ].map(([v, l]) => (
                    <option key={v} value={v}>{v} — {l}</option>
                  ))}
                </select>
              </label>
            </div>
            <div style={{
              marginTop: "0.75rem",
              padding: "0.75rem",
              borderRadius: "6px",
              background: "var(--surface-subtle, rgba(128,128,128,0.05))",
              textAlign: "center",
              fontWeight: 700,
              fontSize: "1.1rem",
              color: riskColor,
            }}>
              Risk Score: {riskScore}/25 — {riskLevel.toUpperCase()}
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><h3>Ownership & Expiry</h3></div>
          <div className="panel-body panel-form">
            <div className="form-row">
              <label>
                Owner
                <input
                  value={form.owner}
                  onChange={(e) => update("owner", e.target.value)}
                  placeholder="email or username"
                />
              </label>
              <label>
                Expiry
                <select value={form.expiry_days} onChange={(e) => update("expiry_days", Number(e.target.value))}>
                  {[30, 60, 90, 120, 180, 365].map((d) => (
                    <option key={d} value={d}>{d} days</option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              Compensating Controls
              <textarea
                rows={3}
                value={form.compensating_controls}
                onChange={(e) => update("compensating_controls", e.target.value)}
                placeholder="Describe compensating controls that mitigate this exception"
              />
            </label>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
          <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Creating..." : `Create ${title}`}
          </button>
        </div>
      </form>
    </div>
  );
}
