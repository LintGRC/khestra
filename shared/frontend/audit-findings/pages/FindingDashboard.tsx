import { useEffect, useState } from "react";
import { findingApi } from "../api";
import type { FindingItem } from "../types";
import { FilterBar, FilterButtons, FilterCount, FilterSearch } from "@shared/filter-bar";
import FindingCard from "../components/FindingCard";
import "../findings.css";

type Props = {
  frameworkFilter?: string;
  onControlClick?: (controlId: string) => void;
  onCreatePoam?: (finding: FindingItem) => void;
};

export default function FindingDashboard({ frameworkFilter, onControlClick, onCreatePoam }: Props) {
  const [findings, setFindings] = useState<FindingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("open");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: "",
    description: "",
    remediation: "",
    control_ids: "",
    severity: "medium",
    source: "audit",
    owner: "",
  });

  const load = async () => {
    try {
      const data = await findingApi.list(
        frameworkFilter ? { framework: frameworkFilter } : undefined,
      );
      setFindings(data.findings || []);
    } catch (e) {
      console.error(e);
      setError("Failed to load findings. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [frameworkFilter]);

  const filtered = findings.filter((f) => {
    if (filter === "open") return f.status === "open";
    if (filter === "in_remediation")
      return f.status === "in_remediation" || f.status === "in_progress";
    if (filter === "material")
      return f.severity === "critical" || f.severity === "high";
    return f.status === filter;
  });

  const searched = search
    ? filtered.filter((f) => {
        const q = search.toLowerCase();
        return (
          f.title.toLowerCase().includes(q) ||
          f.description.toLowerCase().includes(q) ||
          f.owner.toLowerCase().includes(q) ||
          f.control_ids?.some((cid) => cid.toLowerCase().includes(q))
        );
      })
    : filtered;

  const filterCounts = {
    open: findings.filter((f) => f.status === "open").length,
    in_remediation: findings.filter((f) => f.status === "in_remediation" || f.status === "in_progress").length,
    material: findings.filter((f) => f.severity === "critical" || f.severity === "high").length,
    closed: findings.filter((f) => f.status === "closed").length,
  };

  const handleCreate = async () => {
    if (!form.title.trim()) return;
    setActionError(null);
    setSaving(true);
    try {
      await findingApi.create({
        title: form.title.trim(),
        description: form.description.trim(),
        remediation: form.remediation.trim(),
        control_ids: form.control_ids
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        severity: form.severity,
        source: form.source,
        owner: form.owner.trim(),
        framework: frameworkFilter || "",
      });
      setShowForm(false);
      setForm({
        title: "",
        description: "",
        remediation: "",
        control_ids: "",
        severity: "medium",
        source: "audit",
        owner: "",
      });
      await load();
    } catch (err) {
      console.error(err);
      setActionError("Failed to create finding.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this finding and all its corrective actions permanently?")) return;
    setActionError(null);
    try {
      await findingApi.delete(id);
      await load();
    } catch (err) {
      console.error(err);
      setActionError("Failed to delete finding.");
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
      <div
        className="page-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h2>Audit Findings</h2>
          <p className="muted">
            {findings.length} total ·{" "}
            {findings.filter((f) => f.status === "open").length} open ·{" "}
            {findings.filter(
              (f) => f.severity === "critical" || f.severity === "high",
            ).length}{" "}
            critical/high
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? "Cancel" : "+ New Finding"}
        </button>
      </div>

      {actionError && (
        <div className="banner error">{actionError}</div>
      )}

      {showForm && (
        <div className="panel">
          <div className="panel-header">
            <h3>New Finding</h3>
          </div>
          <div className="panel-body panel-form">
            <label>
              Title <span style={{ color: "var(--danger)" }}>*</span>
              <input
                value={form.title}
                onChange={(e) =>
                  setForm((f) => ({ ...f, title: e.target.value }))
                }
                placeholder="e.g., Incomplete access review for production systems"
              />
            </label>
            <label>
              Description
              <textarea
                rows={2}
                value={form.description}
                onChange={(e) =>
                  setForm((f) => ({ ...f, description: e.target.value }))
                }
              />
            </label>
            <label>
              Remediation
              <textarea
                rows={2}
                value={form.remediation}
                onChange={(e) =>
                  setForm((f) => ({ ...f, remediation: e.target.value }))
                }
                placeholder="e.g., Run: aws iam enable-mfa-device --user-name <user> ..."
              />
            </label>
            <div className="form-row">
              <label>
                Control IDs
                <input
                  value={form.control_ids}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, control_ids: e.target.value }))
                  }
                  placeholder="CC6.1, CC7.2"
                />
              </label>
              <label>
                Severity
                <select
                  value={form.severity}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, severity: e.target.value }))
                  }
                >
                  {["critical", "high", "medium", "low", "info"].map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-row">
              <label>
                Source
                <select
                  value={form.source}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, source: e.target.value }))
                  }
                >
                  {[
                    "audit",
                    "assessment",
                    "pen_test",
                    "scanner",
                    "incident",
                    "internal",
                  ].map((s) => (
                    <option key={s} value={s}>
                      {s.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Owner
                <input
                  value={form.owner}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, owner: e.target.value }))
                  }
                  placeholder="email or username"
                />
              </label>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleCreate}
              disabled={saving}
            >
              {saving ? "Creating..." : "Create Finding"}
            </button>
          </div>
        </div>
      )}

      <FilterBar>
        <FilterButtons
          items={[
            { key: "open", label: "Open", count: filterCounts.open },
            { key: "in_remediation", label: "In Remediation", count: filterCounts.in_remediation },
            { key: "material", label: "Critical/High", count: filterCounts.material },
            { key: "closed", label: "Closed", count: filterCounts.closed },
          ]}
          active={filter}
          onChange={setFilter}
        />
        <FilterSearch
          value={search}
          onChange={setSearch}
          placeholder="Search findings..."
          debounceMs={200}
          maxWidth={240}
        />
        <FilterCount value={searched.length} />
      </FilterBar>

      {searched.length === 0 ? (
        <div className="panel">
          <div className="panel-body">
            <p
              className="muted"
              style={{ textAlign: "center", padding: "2rem" }}
            >
              {search ? "No findings match your search." : "No findings match this filter."}
            </p>
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {searched.map((f) => (
            <FindingCard
              key={f.id}
              finding={f}
              onDelete={handleDelete}
              onControlClick={onControlClick}
              onCreatePoam={onCreatePoam}
            />
          ))}
        </div>
      )}
    </div>
  );
}
