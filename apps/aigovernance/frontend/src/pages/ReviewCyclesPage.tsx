import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { TabbedPage } from "@shared/tabbed-page";
import { RefreshCw, Plus, CheckCircle, Calendar, X, Trash2, Swords } from "lucide-react";

const API = "/api/ai-governance";

const STATUS_COLORS: Record<string, { bg: string; color: string }> = {
  completed: { bg: "#dcfce7", color: "#166534" },
  in_progress: { bg: "#dbeafe", color: "#1e40af" },
  scheduled: { bg: "#f3f4f6", color: "#6b7280" },
};

type ReviewCycle = {
  id: string;
  label: string;
  status: string;
  start: string;
  end: string;
  models_reviewed: number;
  frameworks: string[];
  created_at: string;
};

function CyclesTab() {
  const [cycles, setCycles] = useState<ReviewCycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ label: "", start: "", end: "" });
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      const r = await fetch(`${API}/review-cycles`);
      const d = await r.json();
      setCycles(d.cycles || []);
    } catch { /* */ } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!form.label.trim()) return;
    setSaving(true);
    try {
      await fetch(`${API}/review-cycles`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setShowForm(false);
      setForm({ label: "", start: "", end: "" });
      await load();
    } catch { /* */ } finally { setSaving(false); }
  };

  const handleStatus = async (id: string, status: string) => {
    await fetch(`${API}/review-cycles/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
    await load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this review cycle?")) return;
    await fetch(`${API}/review-cycles/${id}`, { method: "DELETE" });
    await load();
  };

  if (loading) return <p className="muted">Loading...</p>;

  return (
    <div>
      <div className="page-header" style={{ padding: 0, marginBottom: 16 }}>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}><Plus size={14} /> New Review Cycle</button>
      </div>

      {showForm && (
        <div className="panel" style={{ padding: 16, marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <strong>New Review Cycle</strong>
            <button className="btn btn-sm btn-ghost" onClick={() => setShowForm(false)}><X size={14} /></button>
          </div>
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Label</label><input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} placeholder="e.g., Q3 2025 AI Risk Review" /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Start</label><input type="date" value={form.start} onChange={(e) => setForm({ ...form, start: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>End</label><input type="date" value={form.end} onChange={(e) => setForm({ ...form, end: e.target.value })} /></div>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleCreate} disabled={saving || !form.label.trim()}>{saving ? "Creating..." : "Create Cycle"}</button>
        </div>
      )}

      {cycles.length === 0 ? (
        <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No review cycles yet.</p>
      ) : (
        <div className="panel-stack" style={{ gap: 12 }}>
          {cycles.map((c) => {
            const sc = STATUS_COLORS[c.status] || STATUS_COLORS.scheduled;
            return (
              <div key={c.id} className="panel" style={{ padding: 16, borderLeft: `3px solid ${sc.color}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <RefreshCw size={16} style={{ color: "var(--primary)" }} />
                      <strong style={{ fontSize: 15 }}>{c.label}</strong>
                      <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: sc.bg, color: sc.color }}>{c.status.replace(/_/g, " ")}</span>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 4 }}>
                    {c.status === "scheduled" && <button className="btn btn-sm btn-primary" onClick={() => handleStatus(c.id, "in_progress")}>Start</button>}
                    {c.status === "in_progress" && <button className="btn btn-sm btn-primary" onClick={() => handleStatus(c.id, "completed")}>Complete</button>}
                    <button className="btn btn-sm btn-ghost" style={{ color: "var(--danger)" }} onClick={() => handleDelete(c.id)}><Trash2 size={12} /></button>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 20, fontSize: 12, color: "var(--muted)" }}>
                  {c.start && <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Calendar size={12} /> {c.start}{c.end ? ` – ${c.end}` : ""}</span>}
                  {c.models_reviewed > 0 && <span style={{ display: "flex", alignItems: "center", gap: 4 }}><CheckCircle size={12} /> {c.models_reviewed} models reviewed</span>}
                </div>
                <div style={{ display: "flex", gap: 4, marginTop: 8 }}>
                  {(c.frameworks || []).map((fw) => (
                    <span key={fw} style={{ fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: "var(--radius)", background: "var(--info-soft, #dbeafe)", color: "var(--info, #1d4ed8)" }}>{fw}</span>
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

function TabletopTab() {
  const [exercises, setExercises] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/tabletop/exercises`)
      .then((r) => r.json())
      .then((d) => setExercises(d.exercises || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading...</p>;

  return (
    <div>
      <Link to="/aigov/tabletop" className="btn btn-primary btn-sm" style={{ marginBottom: 16, display: "inline-flex", alignItems: "center", gap: 6, textDecoration: "none" }}>
        <Swords size={14} /> New Tabletop Exercise
      </Link>
      {exercises.length === 0 ? (
        <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>No tabletop exercises yet. Run a drill to test your AI incident response.</p>
      ) : (
        <div className="panel" style={{ padding: 0 }}>
          {exercises.map((e: any, i: number) => (
            <div key={e.id || i} style={{ display: "flex", gap: 8, padding: "10px 12px", borderBottom: "1px solid var(--border-subtle)", alignItems: "center" }}>
              <Swords size={14} style={{ color: "var(--primary)" }} />
              <span style={{ flex: 1 }}><strong>{e.title || e.name || `Exercise ${e.id}`}</strong></span>
              <span className={`badge ${e.status === "completed" ? "badge-success" : e.status === "in_progress" ? "badge-warning" : "badge-muted"}`}>{e.status || "draft"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ReviewCyclesPage() {
  return (
    <TabbedPage
      title="Review Cycles"
      tabs={[
        { id: "cycles", label: "Review Cycles", content: <CyclesTab /> },
        { id: "tabletop", label: "Tabletop Exercises", content: <TabletopTab /> },
      ]}
    />
  );
}
