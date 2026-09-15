import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { riskApi } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import type { RiskItem } from "../types";
import { LEVELS, CATEGORIES, TREATMENTS } from "../types";
import { detectFrameworkId } from "@shared/vendor-manager/api";
import { FilterSearch } from "@shared/filter-bar";
import "../risk-register.css";

const FRAMEWORK_PATH: Record<string, string> = {
  "CMMC Rev 2": "/cmmc/controls",
  "SOC 2": "/soc2/criteria",
  "AI Gov": "/aigov/readiness",
  "AIGov": "/aigov/readiness",
  "ISO 27001": "/iso27001/soa",
};

const CONTROL_LEAF: Record<string, string> = {
  CMMC: "controls",
  SOC2: "criteria",
  AIGov: "readiness",
  ISO27001: "soa",
};

function levelColor(level: string): string {
  const m: Record<string, string> = {
    low: "#16a34a",
    medium: "#eab308",
    high: "#ea580c",
    critical: "#dc2626",
  };
  return m[level] || "#16a34a";
}

function cap(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

const EMPTY_FORM = {
  title: "",
  description: "",
  category: "operational",
  inherent_likelihood: "medium",
  inherent_impact: "medium",
  residual_likelihood: "low",
  residual_impact: "low",
  treatment: "mitigate",
  controls: "",
  owner: "",
  control_owner: "",
  framework: "",
  control_id: "",
  system_id: "",
  status: "identified",
  review_date: "",
  acceptance_expires: "",
};

type FilterKey = "active" | "critical" | "high" | "in_treatment" | "poam" | "accepted" | "closed";

export default function RiskDashboard() {
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [frameworks, setFrameworks] = useState<string[]>([]);
  const [controls, setControls] = useState<{ id: string; title: string; clause: string; framework: string }[]>([]);
  const [filter, setFilter] = useState<FilterKey>("active");
  const isCmmc = detectFrameworkId() === "CMMC";
  const navigate = useNavigate();
  const fwBase = typeof window !== "undefined" ? (window.location.pathname.match(/^\/(cmmc|soc2|aigov|iso27001)/)?.[0] ?? "") : "";
  const controlDetailPath = CONTROL_LEAF[detectFrameworkId() || ""] || "controls";
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [sortField, setSortField] = useState("title");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [frameworkFilter, setFrameworkFilter] = useState<string>("");
  const [selectedCell, setSelectedCell] = useState<string | null>(null);
  const [legendFilter, setLegendFilter] = useState<string | null>(null);
  const [heatView, setHeatView] = useState<"inherent" | "residual">("residual");
  const [showFilterMenu, setShowFilterMenu] = useState(false);
  const [uncovered, setUncovered] = useState<{ id: string; title: string; clause: string; framework: string }[]>([]);
  const [uncoveredLoading, setUncoveredLoading] = useState(true);

  const load = async () => {
    try {
      const data = await riskApi.list();
      setRisks(data.risks || []);
    } catch (e) {
      console.error(e);
      setError("Failed to load risks. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    riskApi.stats().then(setStats).catch(() => {});
    riskApi.listFrameworks().then((d) => setFrameworks(d.frameworks)).catch(() => {});
    riskApi.listControls().then((d) => setControls(d.controls)).catch(() => {});
  }, []);

  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    if (searchParams.get("action") !== "new") return;
    const controlId = searchParams.get("control_id") || "";
    setForm((prev) => ({ ...prev, control_id: controlId }));
    setShowForm(true);
    setSearchParams({}, { replace: true });
  }, [searchParams, setSearchParams]);

  const loadUncovered = () => {
    setUncoveredLoading(true);
    riskApi
      .uncoveredControls(frameworkFilter || undefined)
      .then((d) => setUncovered(d.controls || []))
      .catch(() => setUncovered([]))
      .finally(() => setUncoveredLoading(false));
  };

  useEffect(() => {
    loadUncovered();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [frameworkFilter]);

  useEffect(() => {
    const path = window.location.pathname;
    const match = path.match(/^\/(cmmc|soc2|aigov|iso27001)/);
    if (match && frameworks.length > 0) {
      const map: Record<string, string> = { cmmc: "CMMC Rev 2", soc2: "SOC 2", aigov: "AI Gov", iso27001: "ISO 27001" };
      const fw = map[match[1]];
      if (fw && frameworks.includes(fw)) {
        setFrameworkFilter(fw);
      }
    }
  }, [frameworks]);

  useEffect(() => {
    if (!showFilterMenu) return;
    const handle = (e: MouseEvent) => {
      if (!(e.target as HTMLElement).closest(".filter-dropdown")) setShowFilterMenu(false);
    };
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, [showFilterMenu]);

  const filtered = risks.filter((r) => {
    if (frameworkFilter && r.framework !== frameworkFilter) return false;
    if (selectedCell) {
      const [lh, imp] = selectedCell.split(":");
      if (r.residual_likelihood !== lh || r.residual_impact !== imp) return false;
    }
    if (legendFilter && r.residual_level !== legendFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!r.title.toLowerCase().includes(q) && !r.description.toLowerCase().includes(q) && !r.owner.toLowerCase().includes(q)) return false;
    }
    if (filter === "active") return r.status !== "closed";
    if (filter === "critical")
      return r.residual_level === "critical" && r.status !== "closed";
    if (filter === "high")
      return (
        (r.residual_level === "high" || r.residual_level === "critical") &&
        r.status !== "closed"
      );
    if (filter === "poam")
      return (r.status === "identified" || r.status === "in_treatment") && !!r.review_date;
    return r.status === filter;
  });

  const active = risks.filter((r) => r.status !== "closed");

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  const sortIcon = (field: string) => {
    if (sortField !== field) return "";
    return sortDir === "asc" ? " ↑" : " ↓";
  };

  const sorted = [...filtered].sort((a, b) => {
    let cmp = 0;
    if (sortField === "title") cmp = a.title.localeCompare(b.title);
    else if (sortField === "inherent") cmp = (a.inherent_score ?? 0) - (b.inherent_score ?? 0);
    else if (sortField === "residual") cmp = (a.residual_score ?? 0) - (b.residual_score ?? 0);
    else if (sortField === "status") cmp = (a.status ?? "").localeCompare(b.status ?? "");
    return sortDir === "asc" ? cmp : -cmp;
  });
  const heatmap: Record<string, Record<string, RiskItem[]>> = {};
  for (const lh of LEVELS) {
    heatmap[lh] = {};
    for (const imp of LEVELS) {
      heatmap[lh][imp] = active.filter(
        (r) =>
          (heatView === "inherent" ? r.inherent_likelihood : r.residual_likelihood) === lh &&
          (heatView === "inherent" ? r.inherent_impact : r.residual_impact) === imp,
      );
    }
  }

  const filterOptions: { key: FilterKey; label: string }[] = [
    { key: "active", label: "Active" },
    { key: "in_treatment", label: "In Treatment" },
    ...(isCmmc ? [{ key: "poam" as const, label: "POA&M" }] : []),
    { key: "accepted", label: "Accepted" },
    { key: "closed", label: "Closed" },
  ];
  const currentFilterLabel = filterOptions.find((o) => o.key === filter)?.label || "Active";
  const filterCount = (key: FilterKey) =>
    risks.filter((r) => {
      if (key === "active") return r.status !== "closed";
      if (key === "critical") return r.residual_level === "critical" && r.status !== "closed";
      if (key === "high")
        return (r.residual_level === "high" || r.residual_level === "critical") && r.status !== "closed";
      if (key === "poam")
        return (r.status === "identified" || r.status === "in_treatment") && !!r.review_date;
      return r.status === key;
    }).length;

  const score = (lh: string, imp: string) => {
    const s: Record<string, number> = { low: 1, medium: 2, high: 3, critical: 4 };
    return (s[lh] || 1) * (s[imp] || 1);
  };

  const matrixClass = (s: number): string => {
    if (s >= 12) return "heat-cell-critical";
    if (s >= 9) return "heat-cell-high";
    if (s >= 6) return "heat-cell-medium";
    return "heat-cell-low";
  };

  // Value labels with numeric suffix
  const LEVEL_VALUES: Record<string, string> = { low: "LOW 1", medium: "MEDIUM 2", high: "HIGH 3", critical: "CRITICAL 4" };

  const update = (field: string, value: string) =>
    setForm((f) => ({ ...f, [field]: value }));

  const handleCreate = async () => {
    if (!form.title.trim()) { setFormError("Title is required"); return; }
    setFormError(null);
    setSaving(true);
    try {
      const path = window.location.pathname;
      const match = path.match(/^\/(cmmc|soc2|aigov|iso27001)/);
      const fwMap: Record<string, string> = { cmmc: "CMMC Rev 2", soc2: "SOC 2", aigov: "AI Gov" };
      const detectedFw = match ? (fwMap[match[1]] || "") : "";
      await riskApi.create({
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        framework: detectedFw || form.framework,
        inherent_likelihood: form.inherent_likelihood,
        inherent_impact: form.inherent_impact,
        residual_likelihood: form.residual_likelihood,
        residual_impact: form.residual_impact,
        treatment: form.treatment,
        controls: form.controls.trim(),
        owner: form.owner.trim(),
        control_owner: form.control_owner.trim(),
        control_id: form.control_id.trim(),
        system_id: form.system_id.trim(),
        status: form.status,
        review_date: form.review_date,
        acceptance_expires: form.acceptance_expires,
      });
      setShowForm(false);
      setForm(EMPTY_FORM);
      await load();
      loadUncovered();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create risk");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (risk: RiskItem) => {
    setEditingId(risk.id);
    const matched = controls.find((c) => c.id === risk.control_id);
    setEditForm({
      title: risk.title || "",
      description: risk.description || "",
      category: risk.category || "operational",
      inherent_likelihood: risk.inherent_likelihood || "medium",
      inherent_impact: risk.inherent_impact || "medium",
      residual_likelihood: risk.residual_likelihood || "low",
      residual_impact: risk.residual_impact || "low",
      treatment: risk.treatment || "mitigate",
      controls: risk.controls || "",
      owner: risk.owner || "",
      control_owner: risk.control_owner || "",
      framework: matched?.framework || "",
      control_id: risk.control_id || "",
      system_id: risk.system_id || "",
      status: risk.status || "identified",
      review_date: risk.review_date || "",
      acceptance_expires: risk.acceptance_expires || "",
    });
  };

  const handleUpdate = async (id: string) => {
    setEditError(null);
    setSaving(true);
    try {
      await riskApi.update(id, {
        title: editForm.title.trim(),
        description: editForm.description.trim(),
        category: editForm.category,
        inherent_likelihood: editForm.inherent_likelihood,
        inherent_impact: editForm.inherent_impact,
        residual_likelihood: editForm.residual_likelihood,
        residual_impact: editForm.residual_impact,
        treatment: editForm.treatment,
        controls: editForm.controls.trim(),
        owner: editForm.owner.trim(),
        control_owner: editForm.control_owner.trim(),
        control_id: editForm.control_id.trim(),
        system_id: editForm.system_id.trim(),
        status: editForm.status,
        review_date: editForm.review_date,
        acceptance_expires: editForm.acceptance_expires,
      });
      setEditingId(null);
      await load();
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Failed to update risk");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this risk permanently?")) return;
    try {
      await riskApi.delete(id);
      await load();
    } catch (err) {
      console.error(err);
    }
  };

  const handleReSign = async (risk: RiskItem) => {
    const who = window.prompt("Who is re-signing this acceptance?", risk.owner || "");
    if (who === null) return;
    try {
      await riskApi.reSign(risk.id, who.trim() || risk.owner || "admin");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Re-sign failed");
      console.error(err);
    }
  };

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

  return (
    <div className="page-stack">
      {stats && (
        <div style={{ display: "flex", gap: 12, marginBottom: 8 }}>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700 }}>{stats.total || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>Total</div>
          </div>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700, color: "var(--danger)" }}>{(stats.by_status?.identified || 0) + (stats.by_status?.assessed || 0)}</div>
            <div className="muted" style={{ fontSize: 11 }}>Open</div>
          </div>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700, color: "var(--warning)" }}>{stats.by_status?.in_treatment || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>In Treatment</div>
          </div>
          <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
            <div style={{ fontWeight: 700, color: "var(--success)" }}>{stats.by_status?.closed || 0}</div>
            <div className="muted" style={{ fontSize: 11 }}>Closed</div>
          </div>
          {isCmmc && (
            <div className="panel" style={{ flex: 1, padding: "8px 12px", textAlign: "center" }}>
              <div style={{ fontWeight: 700, color: "var(--danger)" }}>{(stats.by_status?.identified || 0) + (stats.by_status?.in_treatment || 0)}</div>
              <div className="muted" style={{ fontSize: 11 }}>Open POA&M</div>
            </div>
          )}
        </div>
      )}

      <div
        className="page-header"
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
      >
        <div>
          <h2>Risk Register</h2>
          <p className="muted">
            {active.length} active · {risks.filter((r) => r.status === "closed").length} closed ·{" "}
            {active.filter((r) => r.residual_level === "critical").length} critical
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => window.open(apiUrl("/api/risks/export/csv"), "_blank")}>CSV</button>
          <button
            className="btn btn-primary"
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setFormError(null);
              if (!showForm) {
                const path = window.location.pathname;
                const match = path.match(/^\/(cmmc|soc2|aigov|iso27001)/);
                const fwMap: Record<string, string> = { cmmc: "CMMC Rev 2", soc2: "SOC 2", aigov: "AI Gov" };
                const fw = match ? (fwMap[match[1]] || "") : "";
                setForm((f) => ({ ...f, framework: fw }));
              }
            }}
          >
            {showForm ? "Cancel" : "+ New Risk"}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="panel">
          <div className="panel-header">
            <h3>New Risk</h3>
          </div>
          <div className="panel-body panel-form">
            <label>
              Title <span style={{ color: "var(--danger)" }}>*</span>
              <input
                value={form.title}
                onChange={(e) => update("title", e.target.value)}
                placeholder="e.g., Unpatched vulnerability in customer-facing API"
              />
            </label>
            <label>
              Description
              <textarea
                rows={2}
                value={form.description}
                onChange={(e) => update("description", e.target.value)}
                placeholder="Describe the risk, affected systems, and potential impact"
              />
            </label>
            <div className="form-row">
              <label>
                Category
                <select value={form.category} onChange={(e) => update("category", e.target.value)}>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {cap(c)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Framework
                <select value={form.framework} onChange={(e) => { update("framework", e.target.value); update("control_id", ""); }}>
                  <option value="">-- Select --</option>
                  {frameworks.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-row">
              <label>
                Control
                <select value={form.control_id} onChange={(e) => update("control_id", e.target.value)}>
                  <option value="">-- Select --</option>
                  {controls.map((c) => (
                    <option key={c.id} value={c.id}>{c.clause} — {c.title}</option>
                  ))}
                </select>
              </label>
              <label>
                Inherent Likelihood
                <select
                  value={form.inherent_likelihood}
                  onChange={(e) => update("inherent_likelihood", e.target.value)}
                >
                  {LEVELS.map((l) => (
                    <option key={l} value={l}>
                      {cap(l)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Inherent Impact
                <select
                  value={form.inherent_impact}
                  onChange={(e) => update("inherent_impact", e.target.value)}
                >
                  {LEVELS.map((l) => (
                    <option key={l} value={l}>
                      {cap(l)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-row">
              <label>
                Residual Likelihood
                <select
                  value={form.residual_likelihood}
                  onChange={(e) => update("residual_likelihood", e.target.value)}
                >
                  {LEVELS.map((l) => (
                    <option key={l} value={l}>
                      {cap(l)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Residual Impact
                <select
                  value={form.residual_impact}
                  onChange={(e) => update("residual_impact", e.target.value)}
                >
                  {LEVELS.map((l) => (
                    <option key={l} value={l}>
                      {cap(l)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-row">
              <label>
                Treatment
                <select
                  value={form.treatment}
                  onChange={(e) => update("treatment", e.target.value)}
                >
                  {TREATMENTS.map((t) => (
                    <option key={t} value={t}>
                      {cap(t)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Status
                <select value={form.status} onChange={(e) => update("status", e.target.value)}>
                  {["identified", "in_treatment", "accepted", "closed"].map((s) => (
                    <option key={s} value={s}>
                      {cap(s)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              Controls
              <textarea
                rows={2}
                value={form.controls}
                onChange={(e) => update("controls", e.target.value)}
                placeholder="Describe existing or planned controls"
              />
            </label>
            <label>
              System ID
              <input
                value={form.system_id}
                onChange={(e) => update("system_id", e.target.value)}
                placeholder="Link to an AI system ID"
              />
            </label>
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
                Control Owner
                <input
                  value={form.control_owner}
                  onChange={(e) => update("control_owner", e.target.value)}
                  placeholder="who runs the mitigating control"
                />
              </label>
            </div>
            <div className="form-row">
              <label>
                Review Date
                <input
                  type="date"
                  value={form.review_date}
                  onChange={(e) => update("review_date", e.target.value)}
                />
              </label>
              <label>
                Acceptance Expires (accepted risks)
                <input
                  type="date"
                  value={form.acceptance_expires}
                  onChange={(e) => update("acceptance_expires", e.target.value)}
                />
              </label>
            </div>
            {formError && (
              <p style={{ color: "var(--danger)", fontSize: "0.8125rem", margin: "0.5rem 0 0" }}>{formError}</p>
            )}
            <button className="btn btn-primary" onClick={handleCreate} disabled={saving}>
              {saving ? "Creating..." : "Create Risk"}
            </button>
          </div>
        </div>
      )}

      {/* Framework filter */}
      <div className="risk-toolbar">
        <span className="risk-sort-label">Framework:</span>
        <button
          className={`btn btn-sm ${!frameworkFilter ? "btn-primary" : "btn-ghost"}`}
          onClick={() => setFrameworkFilter("")}
        >
          All
        </button>
        {frameworks.map((f) => (
          <button
            key={f}
            className={`btn btn-sm ${frameworkFilter === f ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setFrameworkFilter(frameworkFilter === f ? "" : f)}
          >
            {cap(f)}
          </button>
        ))}
      </div>

      {/* Heatmap */}
      <div className="panel">
        <div className="panel-header">
          <h3>
            Risk Heatmap — {heatView === "inherent" ? "Inherent" : "Residual"} Risk (Active)
          </h3>
          <span className="muted" style={{ fontSize: "0.75rem", display: "flex", alignItems: "center", gap: 8 }}>
            {active.length} risks shown
            <button
              className={`btn btn-sm ${heatView === "inherent" ? "btn-primary" : "btn-ghost"}`}
              onClick={() => {
                if (heatView !== "inherent") {
                  setHeatView("inherent");
                  setSelectedCell(null);
                  setLegendFilter(null);
                }
              }}
            >
              Inherent
            </button>
            <button
              className={`btn btn-sm ${heatView === "residual" ? "btn-primary" : "btn-ghost"}`}
              onClick={() => {
                if (heatView !== "residual") {
                  setHeatView("residual");
                  setSelectedCell(null);
                  setLegendFilter(null);
                }
              }}
            >
              Residual
            </button>
          </span>
        </div>
        <div className="panel-body">
          <div className="overflow-x-auto" style={{ overflowX: "auto" }}>
            <div className="heat-grid">
              {/* Y-axis label */}
              <div className="heat-axis-y">LIKELIHOOD</div>

              {/* X-axis label */}
              <div className="heat-axis-x">IMPACT</div>

              {/* Column headers */}
              {LEVELS.map((imp, ci) => (
                <div
                  key={imp}
                  className="heat-col-value"
                  style={{ gridColumn: 3 + ci, gridRow: 2 }}
                >
                  {LEVEL_VALUES[imp]}
                </div>
              ))}

              {/* Data rows */}
              {[...LEVELS].reverse().map((lh, ri) => (
                <div key={lh} style={{ display: "contents" }}>
                  {/* Row header */}
                  <div
                    className="heat-row-value"
                    style={{ gridColumn: 2, gridRow: 3 + ri }}
                  >
                    {LEVEL_VALUES[lh]}
                  </div>

                  {/* Cells */}
                  {LEVELS.map((imp, ci) => {
                    const cellRisks = heatmap[lh]?.[imp] || [];
                    const count = cellRisks.length;
                    const s = score(lh, imp);
                    const cls = matrixClass(s);
                    return (
                      <div
                        key={imp}
                        className={`heat-cell ${cls}${count === 0 ? " heat-cell-empty" : ""}${selectedCell === `${lh}:${imp}` && count > 0 ? " heat-cell-active" : ""}`}
                        style={{ gridColumn: 3 + ci, gridRow: 3 + ri }}
                        title={count > 0 ? cellRisks.map((r) => r.title).join("\n") : "No risks"}
                        onClick={() => {
                          if (count > 0) {
                            const key = `${lh}:${imp}`;
                            if (selectedCell === key) {
                              setSelectedCell(null);
                            } else {
                              setSelectedCell(key);
                              setLegendFilter(null);
                              document.getElementById("risk-list")?.scrollIntoView({ behavior: "smooth", block: "start" });
                            }
                          }
                        }}
                      >
                        {count > 0 && (
                          <span className={`heat-cell-badge ${count === 1 ? "dot" : "pill"}`}>
                            {count > 1 && count}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
          <div className="heat-legend">
            {(LEVELS as string[]).map((level, i) => {
              const labels = ["Low (1-5)", "Medium (6-8)", "High (9-11)", "Critical (12-16)"];
              return (
                <span
                  key={level}
                  className="heat-legend-item"
                  onClick={() => {
                    setLegendFilter((prev) => prev === level ? null : level);
                    setSelectedCell(null);
                  }}
                >
                  <span className={`heat-swatch heat-swatch-${level}`} /> {labels[i]}
                </span>
              );
            })}
          </div>
        </div>
      </div>

      {/* Risk list */}
      <div id="risk-list" className="panel">
        <div className="panel-header">
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", width: "100%" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <FilterSearch value={search} onChange={setSearch} placeholder="Search risks..." maxWidth={500} />
              {selectedCell && (
                <button
                  className="btn btn-xs btn-ghost"
                  style={{ fontSize: "0.7rem" }}
                  onClick={() => { setSelectedCell(null); setLegendFilter(null); }}
                >
                  {selectedCell.replace(":", " × ").replace(/\b\w/g, (c) => c.toUpperCase())}
                </button>
              )}
              <div className="filter-dropdown" style={{ marginLeft: "auto" }}>
                <button
                  className={`btn btn-sm ${filter !== "active" ? "btn-primary" : "btn-ghost"}`}
                  onClick={() => setShowFilterMenu(!showFilterMenu)}
                >
                  {currentFilterLabel} ({filterCount(filter)}) ▾
                </button>
                {showFilterMenu && (
                  <div className="filter-menu">
                    {filterOptions.map((opt) => (
                      <button
                        key={opt.key}
                        className={`filter-menu-item ${filter === opt.key ? "filter-menu-item-active" : ""}`}
                        onMouseDown={(e) => { e.preventDefault(); setFilter(opt.key); setShowFilterMenu(false); }}
                      >
                        {opt.label} ({filterCount(opt.key)})
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", flexWrap: "wrap" }}>
                <span className="risk-sort-label" style={{ fontSize: "0.7rem", color: "var(--muted)", marginRight: "0.15rem" }}>Sort:</span>
                {["title", "inherent", "residual", "status"].map((f) => {
                  const sortHint: Record<string, string> = {
                    title: "Sort alphabetically by title",
                    inherent: "Sort by inherent risk score (likelihood × impact)",
                    residual: "Sort by residual risk score (likelihood × impact)",
                    status: "Sort by risk status",
                  };
                  return (
                    <button
                      key={f}
                      className={`btn btn-sm ${sortField === f ? "btn-primary" : "btn-ghost"}`}
                      onClick={() => handleSort(f)}
                      title={sortHint[f]}
                    >
                      {f.charAt(0).toUpperCase() + f.slice(1)}{sortIcon(f)}
                    </button>
                  );
                })}
              </div>
          </div>
        </div>
        <div className="panel-body">
          {(() => {
            if (sorted.length === 0) {
              return <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No risks match this filter.</p>;
            }
            return sorted.map((risk) => {
              const isEditing = editingId === risk.id;
              return (
                <div
                  key={risk.id}
                  style={{
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    padding: "1rem",
                    marginBottom: "0.5rem",
                    borderLeft: `4px solid ${levelColor(risk.residual_level)}`,
                  }}
                >
                  {isEditing ? (
                    <div className="panel-form">
                      <label>
                        Title
                        <input
                          value={editForm.title}
                          onChange={(e) =>
                            setEditForm((f) => ({ ...f, title: e.target.value }))
                          }
                        />
                      </label>
                      <label>
                        Description
                        <textarea
                          rows={2}
                          value={editForm.description}
                          onChange={(e) =>
                            setEditForm((f) => ({
                              ...f,
                              description: e.target.value,
                            }))
                          }
                        />
                      </label>
                      <div className="form-row">
                        <label>
                          Category
                          <select
                            value={editForm.category}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                category: e.target.value,
                              }))
                            }
                          >
                            {CATEGORIES.map((c) => (
                              <option key={c} value={c}>
                                {cap(c)}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Framework
                          <select
                            value={editForm.framework}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                framework: e.target.value,
                                control_id: "",
                              }))
                            }
                          >
                            <option value="">-- Select --</option>
                            {frameworks.map((f) => (
                              <option key={f} value={f}>{f}</option>
                            ))}
                          </select>
                        </label>
                      </div>
                      <div className="form-row">
                        <label>
                          Control
                            <select
                              value={editForm.control_id}
                              onChange={(e) =>
                                setEditForm((f) => ({
                                  ...f,
                                  control_id: e.target.value,
                                }))
                              }
                            >
                              <option value="">-- Select --</option>
                              {controls.map((c) => (
                                <option key={c.id} value={c.id}>{c.clause} — {c.title}</option>
                              ))}
                            </select>
                        </label>
                        <label>
                          Inherent Likelihood
                          <select
                            value={editForm.inherent_likelihood}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                inherent_likelihood: e.target.value,
                              }))
                            }
                          >
                            {LEVELS.map((l) => (
                              <option key={l} value={l}>
                                {cap(l)}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Inherent Impact
                          <select
                            value={editForm.inherent_impact}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                inherent_impact: e.target.value,
                              }))
                            }
                          >
                            {LEVELS.map((l) => (
                              <option key={l} value={l}>
                                {cap(l)}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                      <div className="form-row">
                        <label>
                          Residual Likelihood
                          <select
                            value={editForm.residual_likelihood}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                residual_likelihood: e.target.value,
                              }))
                            }
                          >
                            {LEVELS.map((l) => (
                              <option key={l} value={l}>
                                {cap(l)}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Residual Impact
                          <select
                            value={editForm.residual_impact}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                residual_impact: e.target.value,
                              }))
                            }
                          >
                            {LEVELS.map((l) => (
                              <option key={l} value={l}>
                                {cap(l)}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                      <div className="form-row">
                        <label>
                          Treatment
                          <select
                            value={editForm.treatment}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                treatment: e.target.value,
                              }))
                            }
                          >
                            {TREATMENTS.map((t) => (
                              <option key={t} value={t}>
                                {cap(t)}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Status
                          <select
                            value={editForm.status}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                status: e.target.value,
                              }))
                            }
                          >
                            {["identified", "in_treatment", "accepted", "closed"].map(
                              (s) => (
                                <option key={s} value={s}>
                                  {cap(s)}
                                </option>
                              ),
                            )}
                          </select>
                        </label>
                      </div>
                      <label>
                        Controls
                        <textarea
                          rows={2}
                          value={editForm.controls}
                          onChange={(e) =>
                            setEditForm((f) => ({
                              ...f,
                              controls: e.target.value,
                            }))
                          }
                        />
                      </label>
                      <div className="form-row">
                        <label>
                          System ID
                          <input
                            value={editForm.system_id}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                system_id: e.target.value,
                              }))
                            }
                          />
                        </label>
                        <label>
                          Owner
                          <input
                            value={editForm.owner}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                owner: e.target.value,
                              }))
                            }
                          />
                        </label>
                        <label>
                          Control Owner
                          <input
                            value={editForm.control_owner}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                control_owner: e.target.value,
                              }))
                            }
                          />
                        </label>
                        <label>
                          Review Date
                          <input
                            type="date"
                            value={editForm.review_date}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                review_date: e.target.value,
                              }))
                            }
                          />
                        </label>
                        <label>
                          Acceptance Expires
                          <input
                            type="date"
                            value={editForm.acceptance_expires}
                            onChange={(e) =>
                              setEditForm((f) => ({
                                ...f,
                                acceptance_expires: e.target.value,
                              }))
                            }
                          />
                        </label>
                      </div>
                      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                        {editError && (
                          <p style={{ color: "var(--danger)", fontSize: "0.8rem", flex: "1 1 100%", margin: 0 }}>{editError}</p>
                        )}
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleUpdate(risk.id)}
                          disabled={saving}
                        >
                          {saving ? "Saving..." : "Save"}
                        </button>
                        <button
                          className="btn btn-sm btn-ghost"
                          onClick={() => {
                            setEditingId(null);
                            setEditError(null);
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "flex-start",
                          flexWrap: "wrap",
                          gap: "0.5rem",
                          marginBottom: "0.5rem",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            gap: "0.5rem",
                            flexWrap: "wrap",
                            alignItems: "center",
                          }}
                        >
                          <span
                            className={`badge ${risk.residual_level === "critical" || risk.residual_level === "high" ? "badge-danger" : "badge-warning"}`}
                          >
                            Residual: {risk.residual_level} ({risk.residual_score})
                          </span>
                          <span className="badge badge-muted">
                            Inherent: {risk.inherent_level} ({risk.inherent_score})
                          </span>
                          <span className="badge badge-muted">{risk.treatment}</span>
                          <span className="badge badge-muted">
                            {risk.status.replace(/_/g, " ")}
                          </span>
                        </div>
                        <div style={{ display: "flex", gap: "0.35rem" }}>
                          <button
                            className="btn btn-sm btn-ghost"
                            onClick={() => startEdit(risk)}
                          >
                            Edit
                          </button>
                          <button
                            className="btn btn-sm btn-ghost"
                            style={{ color: "var(--danger)" }}
                            onClick={() => handleDelete(risk.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      <p style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
                        {risk.title}
                      </p>
                      <p style={{ fontSize: "0.9rem", marginBottom: "0.25rem" }}>
                        {risk.description}
                      </p>
                      {risk.control_ids && risk.control_ids.length > 0 && (
                        <p style={{ fontSize: "0.85rem", marginBottom: "0.25rem" }}>
                          <strong>Control IDs:</strong>{" "}
                          {risk.control_ids.map((cid, i) => (
                            <span key={cid}>
                              {i > 0 && ", "}
                              <a
                                href="#"
                                style={{ textDecoration: "underline", cursor: "pointer" }}
                                onClick={(e) => {
                                  e.preventDefault();
                                  const path = fwBase
                                    ? `${fwBase}/${controlDetailPath}/${encodeURIComponent(cid)}`
                                    : `${FRAMEWORK_PATH[risk.framework] || "/cmmc/controls"}/${encodeURIComponent(cid)}`;
                                  navigate(path);
                                }}
                              >
                                {cid}
                              </a>
                            </span>
                          ))}
                        </p>
                      )}
                      {risk.controls && (
                        <p style={{ fontSize: "0.85rem" }}>
                          <strong>Controls:</strong> {risk.controls}
                        </p>
                      )}
                      <div
                        style={{
                          fontSize: "0.75rem",
                          color: "var(--muted)",
                          marginTop: "0.5rem",
                        }}
                      >
                        Owner: {risk.owner} · {risk.created_at?.slice(0, 10)}
                        {risk.control_owner && ` · Control owner: ${risk.control_owner}`}
                        {risk.review_date && ` · Review: ${risk.review_date}`}
                      </div>
                      {risk.status === "accepted" && risk.acceptance_expires && (
                        <div
                          style={{
                            fontSize: "0.78rem",
                            marginTop: "0.5rem",
                            padding: "6px 8px",
                            borderRadius: 6,
                            background: risk.acceptance_overdue
                              ? "var(--danger-soft)"
                              : risk.acceptance_days_left != null && risk.acceptance_days_left <= 30
                                ? "var(--warning-soft)"
                                : "var(--border-subtle)",
                            color: risk.acceptance_overdue
                              ? "var(--danger)"
                              : risk.acceptance_days_left != null && risk.acceptance_days_left <= 30
                                ? "var(--warning)"
                                : "var(--muted)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: 8,
                            flexWrap: "wrap",
                          }}
                        >
                          <span>
                            {risk.acceptance_overdue
                              ? `⚠ Acceptance expired ${risk.acceptance_expires} — re-sign required`
                              : `Acceptance expires ${risk.acceptance_expires}`}
                          </span>
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => handleReSign(risk)}
                          >
                            Re-sign
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              );
            });
          })()}
          </div>
        </div>

        <div className="panel" style={{ marginTop: 20 }}>
          <div className="panel-header">
            <strong>
              Uncovered controls ({uncoveredLoading ? "…" : uncovered.length})
            </strong>
            <span className="muted" style={{ fontSize: "0.8rem" }}>
              Controls with no linked risk — document assessment by creating a risk.
            </span>
          </div>
          <div className="panel-body" style={{ padding: 0 }}>
            {uncoveredLoading ? (
              <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>Loading uncovered controls…</p>
            ) : uncovered.length === 0 ? (
              <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>
                {frameworkFilter ? `Every ${frameworkFilter} control has a linked risk. Nice.` : "No uncovered controls."}
              </p>
            ) : (
              <div style={{ maxHeight: 320, overflowY: "auto" }}>
                {uncovered.map((c) => (
                  <div
                    key={c.id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "8px 14px",
                      borderBottom: "1px solid var(--border-subtle)",
                      fontSize: "0.85rem",
                    }}
                  >
                    <code style={{ flexShrink: 0, fontWeight: 600 }}>{c.id}</code>
                    <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {c.clause ? `${c.clause} — ` : ""}{c.title}
                    </span>
                    <span className="muted" style={{ fontSize: "0.75rem", flexShrink: 0 }}>{c.framework}</span>
                    <button
                      className="btn btn-primary btn-sm"
                      style={{ flexShrink: 0 }}
                      onClick={() => {
                        setForm({ ...EMPTY_FORM, framework: c.framework, control_id: c.id });
                        setShowForm(true);
                        setEditingId(null);
                        setFormError(null);
                        window.scrollTo({ top: 0, behavior: "smooth" });
                      }}
                    >
                      Create risk
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
    </div>
  );
}
