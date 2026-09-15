import { useEffect, useState } from "react";
import { policyApi } from "../api";
import type { PolicyMapping } from "../types";
import { KNOWN_FRAMEWORKS, LIVE_FRAMEWORKS } from "../types";

type Props = {
  policyId: string;
};

const FRAMEWORK_COLORS: Record<string, string> = {
  soc2: "var(--green, #2ecc71)",
  cmmc: "var(--blue, #3498db)",
  aigovernance: "var(--orange, #e67e22)",
  iso42001: "var(--purple, #9b59b6)",
  iso27001: "var(--purple, #9b59b6)",
  eu_ai_act: "var(--orange, #e67e22)",
  nist_ai_rmf: "var(--blue, #3498db)",
};

export default function CrossFrameworkMappingPanel({ policyId }: Props) {
  const [mappings, setMappings] = useState<PolicyMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [framework, setFramework] = useState("soc2");
  const [controlId, setControlId] = useState("");
  const [controlLabel, setControlLabel] = useState("");

  const load = async () => {
    const res = await policyApi.listMappings(policyId);
    setMappings(res.mappings ?? []);
  };

  useEffect(() => {
    load()
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [policyId]);

  async function handleAdd() {
    if (!controlId.trim()) return;
    try {
      await policyApi.createMapping(policyId, {
        framework,
        control_id: controlId.trim(),
        control_label: controlLabel.trim(),
      });
      setControlId("");
      setControlLabel("");
      setShowForm(false);
      await load();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleRemove(mappingId: string) {
    try {
      await policyApi.deleteMapping(policyId, mappingId);
      await load();
    } catch (err) {
      console.error(err);
    }
  }

  function frameworkMeta(fwId: string) {
    return KNOWN_FRAMEWORKS.find((f) => f.id === fwId) ?? { id: fwId, label: fwId, shortLabel: fwId };
  }

  function isLive(fwId: string) {
    return KNOWN_FRAMEWORKS.some((f) => f.id === fwId && f.live);
  }

  const grouped: Record<string, PolicyMapping[]> = {};
  for (const m of mappings) {
    if (!grouped[m.framework]) grouped[m.framework] = [];
    grouped[m.framework].push(m);
  }

  return (
    <div
      style={{
        marginTop: "1rem",
        border: "1px solid var(--border)",
        borderRadius: "8px",
        padding: "1rem",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "0.75rem",
        }}
      >
        <strong>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ verticalAlign: "middle", marginRight: "0.4rem" }}>
            <circle cx="12" cy="12" r="10" />
            <path d="M2 12h20" />
            <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
          </svg>
          Cross-Framework Mappings
        </strong>
        <button className="btn btn-sm btn-ghost" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Add Mapping"}
        </button>
      </div>

      {showForm && (
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            flexWrap: "wrap",
            marginBottom: "0.75rem",
            padding: "0.75rem",
            background: "var(--surface-subtle, rgba(128,128,128,0.06))",
            borderRadius: "6px",
            alignItems: "end",
          }}
        >
          <label style={{ flex: "0 0 130px" }}>
            Framework
            <select
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              style={{ marginTop: "0.2rem" }}
            >
              {LIVE_FRAMEWORKS.map((fw) => (
                <option key={fw.id} value={fw.id}>
                  {fw.shortLabel}
                </option>
              ))}
            </select>
          </label>
          <label style={{ flex: "1 1 140px", minWidth: "100px" }}>
            Control ID
            <input
              value={controlId}
              onChange={(e) => setControlId(e.target.value)}
              placeholder="e.g. CC6.1"
              style={{ marginTop: "0.2rem" }}
            />
          </label>
          <label style={{ flex: "1 1 160px", minWidth: "120px" }}>
            Label
            <input
              value={controlLabel}
              onChange={(e) => setControlLabel(e.target.value)}
              placeholder="e.g. Access Controls"
              style={{ marginTop: "0.2rem" }}
            />
          </label>
          <button className="btn btn-sm btn-primary" onClick={handleAdd}>
            Add
          </button>
        </div>
      )}

      {loading ? (
        <p className="muted" style={{ fontSize: "0.85rem" }}>Loading mappings...</p>
      ) : mappings.length === 0 ? (
        <p className="muted" style={{ fontSize: "0.85rem" }}>
          No cross-framework mappings. Add a mapping to show which controls this policy satisfies.
        </p>
      ) : (
        <div>
          {Object.entries(grouped).map(([fwId, fwMappings]) => {
            const meta = frameworkMeta(fwId);
            const color = FRAMEWORK_COLORS[fwId] || "var(--muted)";
            return (
              <div key={fwId} style={{ marginBottom: "0.5rem" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    marginBottom: "0.25rem",
                  }}
                >
                  <span
                    style={{
                      display: "inline-block",
                      width: "10px",
                      height: "10px",
                      borderRadius: "50%",
                      backgroundColor: color,
                      flexShrink: 0,
                    }}
                  />
                  <strong style={{ fontSize: "0.85rem", color }}>
                    {meta.shortLabel}
                  </strong>
                  {!isLive(fwId) && (
                    <span
                      className="badge"
                      style={{
                        fontSize: "0.65rem",
                        padding: "0.05rem 0.4rem",
                        borderColor: "var(--muted)",
                        color: "var(--muted)",
                      }}
                    >
                      coming soon
                    </span>
                  )}
                  <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
                    ({fwMappings.length} control{fwMappings.length !== 1 ? "s" : ""})
                  </span>
                </div>
                <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", paddingLeft: "1.25rem" }}>
                  {fwMappings.map((m) => (
                    <span
                      key={m.id}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.3rem",
                        padding: "0.2rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.8rem",
                        border: "1px solid var(--border)",
                        background: "var(--surface-subtle, rgba(128,128,128,0.04))",
                      }}
                    >
                      <span>
                        {m.control_id}
                        {m.control_label ? ` (${m.control_label})` : ""}
                      </span>
                      <button
                        onClick={() => handleRemove(m.id)}
                        style={{
                          border: "none",
                          background: "none",
                          cursor: "pointer",
                          padding: 0,
                          fontSize: "0.85rem",
                          color: "var(--muted)",
                          lineHeight: 1,
                        }}
                        title="Remove mapping"
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}