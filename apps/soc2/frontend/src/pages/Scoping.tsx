import { useEffect, useState } from "react";
import { api, TscScopeResponse } from "../api";
import PageIntro from "../components/PageIntro";
import { PageSkeleton } from "../components/ui/Skeleton";

export default function ScopingPage() {
  const [data, setData] = useState<TscScopeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [scope, setScope] = useState<Record<string, boolean>>({});
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [confirmDowngrade, setConfirmDowngrade] = useState<string | null>(null);

  useEffect(() => {
    api.getScope()
      .then((res) => {
        setData(res);
        setScope(res.scope);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleToggle = (key: string) => {
    if (key === "Security") return;
    const newScope = { ...scope, [key]: !scope[key] };
    setScope(newScope);
  };

  const handleSave = async () => {
    if (!data) return;
    const deselecting = Object.keys(data.categories).filter((k) => !scope[k] && data.scope[k]);
    if (deselecting.length > 0 && !confirmDowngrade) {
      setConfirmDowngrade(deselecting.join(", "));
      return;
    }
    setSaving(true);
    setMessage(null);
    try {
      const res = await api.patchScope(scope);
      setData({ ...data, scope: res.scope, summary: res.summary, scoping_completed: true });
      setScope(res.scope);
      setMessage({ type: "success", text: "Scope saved. Only in-scope criteria will be shown." });
      setConfirmDowngrade(null);
    } catch (err: any) {
      setMessage({ type: "error", text: err?.message || "Failed to save scope" });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <PageSkeleton variant="default" />;
  if (!data) return <div className="page-stack"><p className="muted">Could not load scoping data.</p></div>;

  const selectedCount = Object.values(scope).filter(Boolean).length;
  const inScopeCriterionCount = Object.entries(data.categories)
    .filter(([k]) => scope[k])
    .reduce((sum, [, v]) => sum + v.criteria_count, 0);

  return (
    <div className="page-stack">
      <PageIntro
        title="Trust Services Criteria — Scoping"
        summary="Select which SOC 2 categories apply to your organization. Security (Common Criteria) is always required. Only in-scope criteria will appear throughout the app."
      />

      <div className="panel" style={{ textAlign: "center", padding: "16px" }}>
        <span style={{ fontSize: "1.2rem", fontWeight: 600 }}>
          {selectedCount} of {data.summary.total_categories} categories selected
        </span>
        <span className="muted" style={{ marginLeft: 8 }}>
          · {inScopeCriterionCount} of {data.summary.total_criteria} criteria in scope
        </span>
      </div>

      {message && (
        <div className={`banner ${message.type === "success" ? "success" : "error"}`}>
          {message.text}
        </div>
      )}

      <div className="scoping-cards" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {Object.entries(data.categories).map(([key, cat]) => {
          const isOn = scope[key];
          const isLocked = cat.mandatory;
          return (
            <div
              key={key}
              className="panel"
              style={{
                opacity: isOn ? 1 : 0.6,
                borderLeft: isLocked ? "3px solid var(--primary)" : isOn ? "3px solid var(--success)" : "3px solid transparent",
                transition: "opacity 0.2s",
              }}
            >
              <div className="panel-body">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <h3 style={{ margin: 0, fontSize: "1rem" }}>{cat.label}</h3>
                      <span className="badge badge-muted" style={{ fontSize: "0.7rem" }}>
                        {cat.criteria_count} criteria
                      </span>
                    </div>
                    <p className="muted" style={{ margin: "4px 0", fontSize: "0.85rem" }}>
                      {cat.description}
                    </p>
                    {cat.guidance_question && (
                      <p style={{ fontSize: "0.8rem", margin: "6px 0 0 0", fontStyle: "italic", color: "var(--text-muted)" }}>
                        {isOn ? "✅" : "❓"} {cat.guidance_question}
                      </p>
                    )}
                    {cat.example_commitment && (
                      <p style={{ fontSize: "0.75rem", margin: "2px 0 0 0", color: "var(--muted)" }}>
                        Example: {cat.example_commitment}
                      </p>
                    )}
                  </div>
                  <div style={{ flexShrink: 0 }}>
                    {isLocked ? (
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 4,
                          padding: "4px 12px",
                          borderRadius: 4,
                          background: "var(--primary-soft)",
                          color: "var(--primary)",
                          fontSize: "0.8rem",
                          fontWeight: 500,
                          cursor: "not-allowed",
                        }}
                      >
                        🔒 Required
                      </span>
                    ) : (
                      <button
                        type="button"
                        className={`btn btn-sm ${isOn ? "btn-primary" : "btn-secondary"}`}
                        onClick={() => handleToggle(key)}
                        style={{ minWidth: 80 }}
                      >
                        {isOn ? "ON" : "OFF"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirmation modal for scope reduction */}
      {confirmDowngrade && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          }}
          onClick={() => setConfirmDowngrade(null)}
        >
          <div
            className="panel"
            style={{ maxWidth: 480, margin: 16 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="panel-body">
              <h3>Reduce scope?</h3>
              <p>
                You are removing: <strong>{confirmDowngrade}</strong>. Controls for these
                categories will be hidden from all views. No data will be lost — you can
                re-enable them later and your evidence, narratives, and PoF statuses will
                still be there.
              </p>
              <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                <button
                  className="btn btn-primary"
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? "Saving…" : "Yes, reduce scope"}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => setConfirmDowngrade(null)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 8 }}>
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving || JSON.stringify(scope) === JSON.stringify(data.scope)}
        >
          {saving ? "Saving…" : "Save scope"}
        </button>
      </div>
    </div>
  );
}
