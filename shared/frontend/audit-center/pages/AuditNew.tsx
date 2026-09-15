import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { auditApi } from "../api";
import { AUDIT_TYPES } from "../types";

type Props = {
  frameworkDefault?: string;
};

export default function AuditNew({ frameworkDefault }: Props) {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const prefillControlId = params.get("control_id") || "";
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: "",
    framework: frameworkDefault || "",
    audit_type: "",
    start_date: "",
    end_date: "",
    auditor_name: "",
    auditor_email: "",
    scope_notes: "",
    preparation_notes: "",
    control_id: prefillControlId,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const { audit } = await auditApi.create(form);
      navigate(`../${audit.id}`, { replace: true });
    } catch {
      setError("Failed to create audit. Try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>New Audit</h2>
        <p className="muted">Schedule an internal or external assessment.</p>
      </div>

      {error && <div className="banner error">{error}</div>}

      <form onSubmit={handleSubmit} className="panel">
        <div className="panel-body" style={{ display: "grid", gap: "1rem" }}>
          <label>
            Title *
            <input name="title" value={form.title} onChange={handleChange} placeholder="Q2 2026 Internal Audit" required />
          </label>

          <div style={{ display: "flex", gap: "1rem" }}>
            <label style={{ flex: 1 }}>
              Framework
              <input name="framework" value={form.framework} onChange={handleChange} placeholder="CMMC, SOC2, ISO 27001..." />
            </label>
            <label style={{ flex: 1 }}>
              Audit Type
              <select name="audit_type" value={form.audit_type} onChange={handleChange}>
                <option value="">Select type...</option>
                {AUDIT_TYPES.map((t) => (
                  <option key={t} value={t}>{t.replace("_", " ")}</option>
                ))}
              </select>
            </label>
          </div>

          <div style={{ display: "flex", gap: "1rem" }}>
            <label style={{ flex: 1 }}>
              Start Date
              <input type="date" name="start_date" value={form.start_date} onChange={handleChange} />
            </label>
            <label style={{ flex: 1 }}>
              End Date
              <input type="date" name="end_date" value={form.end_date} onChange={handleChange} />
            </label>
          </div>

          <label>
            Control ID
            <input name="control_id" value={form.control_id} onChange={handleChange} placeholder="SC.L2-3.13.1" />
          </label>

          <div style={{ display: "flex", gap: "1rem" }}>
            <label style={{ flex: 1 }}>
              Auditor Name
              <input name="auditor_name" value={form.auditor_name} onChange={handleChange} placeholder="Jane Smith or Firm Name" />
            </label>
            <label style={{ flex: 1 }}>
              Auditor Email
              <input type="email" name="auditor_email" value={form.auditor_email} onChange={handleChange} placeholder="jane@example.com" />
            </label>
          </div>

          <label>
            Scope Notes
            <textarea name="scope_notes" value={form.scope_notes} onChange={handleChange} placeholder="Controls, locations, systems, and boundaries in scope. e.g. CMMC Level 2, all 110 controls, Site A" rows={3} />
          </label>

          <label>
            Preparation Notes
            <textarea name="preparation_notes" value={form.preparation_notes} onChange={handleChange} placeholder="Pre-audit prep, checklist items, or stakeholder briefings. e.g. Notify stakeholders, gather evidence folders, schedule opening meeting" rows={3} />
          </label>
        </div>

        <div className="panel-footer" style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", padding: "1rem" }}>
          <button className="btn btn-ghost" type="button" onClick={() => navigate(-1)}>Cancel</button>
          <button className="btn btn-primary" type="submit" disabled={saving || !form.title.trim()}>
            {saving ? "Creating..." : "Create Audit"}
          </button>
        </div>
      </form>
    </div>
  );
}
