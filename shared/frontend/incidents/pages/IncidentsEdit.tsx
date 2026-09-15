import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api";
import type { FailureMode } from "../types";
import { FAILURE_MODE_LABELS } from "../types";

export default function IncidentsEdit({ basePath = "/incidents" }: { basePath?: string }) {
  const { iid } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "", description: "", failure_mode: "", severity: "medium",
    reporter_name: "", model_name: "", control_id: "", impact_description: "",
    affected_inference_pct: 0, total_users_exposed: 0, downstream_applications: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!iid) return;
    api.get(iid).then((d) => {
      const inc = d.incident;
      setForm({
        title: inc.title || "",
        description: inc.description || "",
        failure_mode: inc.failure_mode || "",
        severity: inc.severity || "medium",
        reporter_name: inc.reporter_name || "",
        model_name: inc.model_name || "",
        control_id: inc.control_id || "",
        impact_description: inc.impact?.description || "",
        affected_inference_pct: inc.impact?.affected_inference_pct || 0,
        total_users_exposed: inc.impact?.total_users_exposed || 0,
        downstream_applications: (inc.impact?.downstream_applications || []).join(", "),
      });
    }).catch(() => setError("Failed to load incident")).finally(() => setLoading(false));
  }, [iid]);

  const handleSubmit = async () => {
    if (!form.title.trim() || !iid) return;
    setSaving(true);
    try {
      await api.update(iid, form as unknown as Parameters<typeof api.update>[1]);
      navigate(`${basePath}/${iid}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="muted">Loading...</p>;
  if (error) return <div className="page-stack"><div className="banner error">{error}</div></div>;

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Edit Incident</h2>
        <Link to={`${basePath}/${iid}`} className="muted" style={{ fontSize: 13, textDecoration: "none" }}>← Back to incident</Link>
      </div>

      <div className="panel">
        <div className="panel-header"><strong>Incident Details</strong></div>
        <div className="panel-body">
          <div className="form-grid">
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Title *</label><input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Failure Mode</label><select value={form.failure_mode} onChange={(e) => setForm({ ...form, failure_mode: e.target.value })}><option value="">Select...</option>{(Object.entries(FAILURE_MODE_LABELS) as [FailureMode, string][]).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Severity</label><select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Description</label><textarea rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Reporter Name</label><input value={form.reporter_name} onChange={(e) => setForm({ ...form, reporter_name: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Model Name</label><input value={form.model_name} onChange={(e) => setForm({ ...form, model_name: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Control ID</label><input value={form.control_id} onChange={(e) => setForm({ ...form, control_id: e.target.value })} placeholder="SC.L2-3.13.1" /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Impact Description</label><textarea rows={2} value={form.impact_description} onChange={(e) => setForm({ ...form, impact_description: e.target.value })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>% Calls Affected</label><input type="number" min={0} max={100} value={form.affected_inference_pct} onChange={(e) => setForm({ ...form, affected_inference_pct: Number(e.target.value) })} /></div>
            <div><label className="muted" style={{ fontSize: 11 }}>Users Exposed</label><input type="number" min={0} value={form.total_users_exposed} onChange={(e) => setForm({ ...form, total_users_exposed: Number(e.target.value) })} /></div>
            <div className="span-2"><label className="muted" style={{ fontSize: 11 }}>Downstream Applications</label><input value={form.downstream_applications} onChange={(e) => setForm({ ...form, downstream_applications: e.target.value })} /></div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={!form.title.trim() || saving}>{saving ? "Saving..." : "Save Changes"}</button>
            <button className="btn btn-secondary" onClick={() => navigate(`${basePath}/${iid}`)}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  );
}
