import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { vendorApi, vendorTerm, detectFrameworkId } from "../api";

export default function VendorNew() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const isCmmc = detectFrameworkId() === "CMMC";
  const isSoc2 = detectFrameworkId() === "SOC2";
  const [form, setForm] = useState({
    name: "",
    category: "",
    ai_service_type: "",
    tier: "",
    contact_name: "",
    contact_email: "",
    contact_phone: "",
    website: "",
    product_service: "",
    data_residency: "",
    transfer_mechanism: "",
    dpa_in_place: false,
    handles_cui: false,
    cmmc_level: "",
    sprs_score: "",
    flow_down_clause_signed: "",
    cui_categories: "",
    last_assessment_date: "",
    soc_report_date: "",
    review_date: "",
    data_types: "",
  });

  async function handleSubmit() {
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      const { vendor } = await vendorApi.create({
        ...form,
        data_residency: form.data_residency.split(",").map((s) => s.trim()).filter(Boolean),
        data_types: form.data_types.split(",").map((s) => s.trim()).filter(Boolean),
        sprs_score: form.sprs_score ? parseInt(form.sprs_score) : null,
        cui_categories: form.cui_categories.split(",").map((s) => s.trim()).filter(Boolean),
      });
      navigate(`/vendors/${vendor.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ maxWidth: 500, margin: "0 auto" }}>
      <NavLink
        to="/vendors"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 4,
          fontSize: 12,
          color: "var(--muted)",
          textDecoration: "none",
          marginBottom: 12,
        }}
      >
        ← Back
      </NavLink>
      <div className="page-header">
        <h2>New {vendorTerm()}</h2>
      </div>
      <div className="panel" style={{ padding: 16 }}>
        <div className="form-grid">
          <div className="span-2">
            <label className="muted" style={{ fontSize: 11 }}>
              Name <span style={{ color: "var(--danger)" }}>*</span>
            </label>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g., Acme AI Solutions"
            />
          </div>
          <div>
            <label className="muted" style={{ fontSize: 11 }}>Category</label>
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            >
              <option value="">— Select —</option>
              <option value="ai_platform">AI Platform</option>
              <option value="cloud_provider">Cloud Provider</option>
              <option value="data_processor">Data Processor</option>
              <option value="consulting">Consulting</option>
              <option value="saas">SaaS</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="muted" style={{ fontSize: 11 }}>AI Service Type</label>
            <input
              value={form.ai_service_type}
              onChange={(e) => setForm({ ...form, ai_service_type: e.target.value })}
              placeholder="e.g., LLM API, vision model"
            />
          </div>
          <div>
            <label className="muted" style={{ fontSize: 11 }}>Tier</label>
            <select
              value={form.tier}
              onChange={(e) => setForm({ ...form, tier: e.target.value })}
            >
              <option value="">Select</option>
              <option value="1">Tier 1</option>
              <option value="2">Tier 2</option>
              <option value="3">Tier 3</option>
            </select>
          </div>
          <div>
            <label className="muted" style={{ fontSize: 11 }}>Contact Email</label>
            <input
              value={form.contact_email}
              onChange={(e) => setForm({ ...form, contact_email: e.target.value })}
              placeholder="vendor@example.com"
            />
          </div>
          <div className="span-2">
            <label className="muted" style={{ fontSize: 11 }}>Data Residency (comma-separated)</label>
            <input
              value={form.data_residency}
              onChange={(e) => setForm({ ...form, data_residency: e.target.value })}
              placeholder="EU, US, APAC"
            />
          </div>
          <div className="span-2">
            <label className="muted" style={{ fontSize: 11 }}>Transfer Mechanism</label>
            <input
              value={form.transfer_mechanism}
              onChange={(e) => setForm({ ...form, transfer_mechanism: e.target.value })}
              placeholder="e.g., SCC, BCR"
            />
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={form.dpa_in_place}
              onChange={(e) => setForm({ ...form, dpa_in_place: e.target.checked })}
              style={{ width: "auto" }}
            />
            DPA in place
          </label>
        </div>

        {isCmmc && (
          <div className="panel" style={{ padding: 16, marginTop: 16 }}>
            <div className="panel-header"><strong>CMMC / NIST 800-171 Fields</strong></div>
            <div className="panel-body">
              <div className="form-grid">
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, cursor: "pointer" }}>
                  <input type="checkbox" checked={form.handles_cui} onChange={(e) => setForm({ ...form, handles_cui: e.target.checked })} style={{ width: "auto" }} />
                  Handles CUI?
                </label>
                <div>
                  <label className="muted" style={{ fontSize: 11 }}>CMMC Level Required</label>
                  <select value={form.cmmc_level} onChange={(e) => setForm({ ...form, cmmc_level: e.target.value })}>
                    <option value="">Select</option>
                    <option value="1">Level 1</option>
                    <option value="2">Level 2</option>
                    <option value="3">Level 3</option>
                  </select>
                </div>
                <div>
                  <label className="muted" style={{ fontSize: 11 }}>SPRS Score</label>
                  <input type="number" min={0} max={110} value={form.sprs_score} onChange={(e) => setForm({ ...form, sprs_score: e.target.value })} placeholder="e.g. 78" />
                </div>
                <div>
                  <label className="muted" style={{ fontSize: 11 }}>Flow-down Clause</label>
                  <select value={form.flow_down_clause_signed} onChange={(e) => setForm({ ...form, flow_down_clause_signed: e.target.value })}>
                    <option value="">Select</option>
                    <option value="Yes">Signed</option>
                    <option value="Pending">Pending</option>
                    <option value="No">Not Signed</option>
                  </select>
                </div>
                <div className="span-2">
                  <label className="muted" style={{ fontSize: 11 }}>CUI Categories (comma-separated)</label>
                  <input value={form.cui_categories} onChange={(e) => setForm({ ...form, cui_categories: e.target.value })} placeholder="e.g. CUI-Controlled, CUI-Export Controlled" />
                </div>
                <div>
                  <label className="muted" style={{ fontSize: 11 }}>Last Assessment Date</label>
                  <input type="date" value={form.last_assessment_date} onChange={(e) => setForm({ ...form, last_assessment_date: e.target.value })} />
                </div>
              </div>
            </div>
          </div>
        )}
        {isSoc2 && (
          <div className="panel" style={{ padding: 16, marginTop: 16 }}>
            <div className="panel-header"><strong>SOC 2 Vendor Fields</strong></div>
            <div className="panel-body">
              <div className="form-grid">
                <div>
                  <label className="muted" style={{ fontSize: 11 }}>SOC Report Date</label>
                  <input type="date" value={form.soc_report_date} onChange={(e) => setForm({ ...form, soc_report_date: e.target.value })} />
                </div>
                <div>
                  <label className="muted" style={{ fontSize: 11 }}>Next Review Date</label>
                  <input type="date" value={form.review_date} onChange={(e) => setForm({ ...form, review_date: e.target.value })} />
                </div>
                <div className="span-2">
                  <label className="muted" style={{ fontSize: 11 }}>Data Types Handled (comma-separated)</label>
                  <input value={form.data_types} onChange={(e) => setForm({ ...form, data_types: e.target.value })} placeholder="e.g. PII, PHI, PCI, Credentials" />
                </div>
              </div>
            </div>
          </div>
        )}
        <button
          onClick={handleSubmit}
          className="btn btn-primary"
          style={{ marginTop: 12 }}
          disabled={saving}
        >
          {saving ? "Creating..." : `Create ${vendorTerm()}`}
        </button>
      </div>
    </div>
  );
}
