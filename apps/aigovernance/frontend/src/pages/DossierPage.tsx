import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Shield, ArrowLeft, Download } from "lucide-react";
import { NavLink } from "react-router-dom";
import { authFetch, postDownload } from "../api";

const API = "/api/ai-governance";

export function DossierPage() {
  const { id } = useParams<{ id: string }>();
  const [dossier, setDossier] = useState<any>(null);

  useEffect(() => {
    if (!id) return;
    authFetch(`${API}/systems/${id}/dossier`).then((r) => r.json()).then((d) => setDossier(d)).catch(() => {});
  }, [id]);

  if (!dossier) return <p className="muted" style={{ padding: 24 }}>Loading...</p>;

  const sys = dossier.system || {};
  const incidents = dossier.related_incidents || [];

  return (
    <>
      <NavLink to={`/aigov/systems/${id}`} style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "var(--muted)", textDecoration: "none", marginBottom: 12 }}>
        <ArrowLeft size={12} /> Back
      </NavLink>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 600, margin: 0 }}>Regulatory Dossier</h1>
          <p className="muted" style={{ margin: "4px 0 0", fontSize: 13 }}>{sys.name}</p>
        </div>
        <button
          className="btn btn-primary btn-sm"
          style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
          onClick={() => postDownload(`${API}/systems/${id}/dossier/export`, undefined, `regulatory-dossier-${id}.zip`).catch((e) => alert(`Export failed: ${String(e)}`))}
        >
          <Download size={14} /> Download pack
        </button>
      </div>

      <div className="panel" style={{ padding: 16 }}>
        <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><Shield size={14} /> System Summary</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
          {[
            { label: "System Name", value: sys.name },
            { label: "Risk Classification", value: sys.risk_classification },
            { label: "Approval Status", value: sys.approval_status },
            { label: "Owner", value: sys.owner },
            { label: "Purpose", value: sys.purpose },
            { label: "Created", value: sys.created_at?.slice(0, 10) },
            { label: "Last Updated", value: sys.updated_at?.slice(0, 10) },
            { label: "Dossier Exported", value: dossier.dossier_exported_at?.slice(0, 19).replace("T", " ") },
          ].map((e) => (
            <div key={e.label} style={{ fontSize: 12 }}>
              <div className="muted" style={{ fontSize: 11 }}>{e.label}</div>
              <div style={{ fontWeight: 500 }}>{e.value || "-"}</div>
            </div>
          ))}
        </div>
      </div>

      {sys.risk_assessment && Object.keys(sys.risk_assessment).length > 0 && (
        <div className="panel" style={{ padding: 16, marginTop: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Risk Assessment</strong></div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
            {Object.entries(sys.risk_assessment).map(([k, v]) => (
              <div key={k} style={{ fontSize: 12 }}>
                <div className="muted" style={{ fontSize: 11 }}>{k}</div>
                <div style={{ fontWeight: 500 }}>{String(v) || "-"}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {incidents.length > 0 && (
        <div className="panel" style={{ padding: 16, marginTop: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Related Incidents ({incidents.length})</strong></div>
          {incidents.map((inc: any) => (
            <NavLink key={inc.id} to={`/aigov/incidents/${inc.id}`} style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", color: "inherit", fontSize: 13 }}>
              <Shield size={14} style={{ color: "var(--primary)", flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <span style={{ fontWeight: 500 }}>{inc.title || inc.incident_type}</span>
                <span className="muted" style={{ marginLeft: 8 }}>{inc.severity} · {inc.created_at?.slice(0, 10)}</span>
              </div>
              <span className={`badge ${inc.status === "resolved" ? "met" : "neutral"}`}>{inc.status}</span>
            </NavLink>
          ))}
        </div>
      )}

      {sys.evidence?.length > 0 && (
        <div className="panel" style={{ padding: 16, marginTop: 16 }}>
          <div className="panel-header" style={{ margin: "-16px -16px 12px" }}><strong>Evidence ({sys.evidence.length})</strong></div>
          {sys.evidence.map((e: any, i: number) => (
            <div key={e.id || i} style={{ fontSize: 12, padding: "6px 0", borderBottom: "1px solid var(--border-subtle)" }}>
              <div style={{ fontWeight: 500 }}>{e.collector || e.check}</div>
              <div className="muted">{e.status || "collected"} · {e.timestamp?.slice(0, 19).replace("T", " ")}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
