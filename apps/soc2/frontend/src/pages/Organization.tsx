import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, apiUrl, type Organization, type OrgProfile, type EnvScope, type InventoryAsset } from "../api";
import { useLayout } from "../Layout";
import PageIntro from "../components/PageIntro";
import OrgSetupChecklist from "../components/OrgSetupChecklist";
import ProfileWizard from "../components/ProfileWizard";
import InventoryTable from "../components/InventoryTable";

export default function OrganizationPage() {
  const { settings, refreshDashboard, canEdit } = useLayout();
  const [org, setOrg] = useState<Organization | null>(null);
  const [profile, setProfile] = useState<OrgProfile>({});
  const [envScope, setEnvScope] = useState<EnvScope>({});
  const [inventory, setInventory] = useState<InventoryAsset[]>([]);
  const [useWizard, setUseWizard] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ type: "ok" | "err"; text: string } | null>(null);
  const [documents, setDocuments] = useState<any[]>([]);

  useEffect(() => {
    api.organization().then((data) => {
      setOrg(data);
      setProfile(data.org_profile);
      setEnvScope(data.env_scope);
      setInventory(data.org_inventory?.assets || []);
      setUseWizard(data.needs_wizard);
    }).catch(console.error);
    fetch(apiUrl("/api/documents"))
      .then((r) => r.json())
      .then((d) => setDocuments(d.documents || []))
      .catch(() => {});
  }, []);

  const saveAll = useCallback(async () => {
    if (!org) return;
    setSaving(true);
    setMsg(null);
    try {
      await Promise.all([
        api.patchOrgProfile(profile),
        api.patchEnvScope(envScope),
        api.patchInventory(inventory),
      ]);
      const refreshed = await api.organization();
      setOrg(refreshed);
      await refreshDashboard();
      setMsg({ type: "ok", text: "Saved" });
    } catch (err) {
      setMsg({ type: "err", text: String(err) });
    } finally {
      setSaving(false);
      setTimeout(() => setMsg(null), 3000);
    }
  }, [org, profile, envScope, inventory, refreshDashboard]);

  if (!org) return null;

  const envFields = [
    { key: "uses_cloud", label: "Do you use cloud services?", type: "yes_no" },
    { key: "cloud_provider", label: "Primary cloud provider", type: "cloud" },
    { key: "uses_saas", label: "Do you use third-party SaaS?", type: "yes_no" },
    { key: "remote_workforce", label: "Do you have a remote workforce?", type: "yes_no" },
    { key: "uses_wireless", label: "Do you use wireless networks?", type: "yes_no" },
    { key: "processes_pii", label: "Do you process PII/personal data?", type: "yes_no" },
  ];

  const yesNoLabels = org.env_scope_labels?.yes_no || { "": "Not answered", yes: "Yes", no: "No" };
  const cloudLabels = org.env_scope_labels?.cloud || { "": "Not answered" };

  const renderEnvSelect = (field: { key: string; label: string; type: string }) => {
    const labels = field.type === "cloud" ? cloudLabels : yesNoLabels;
    return (
      <div className="form-row" key={field.key} id={`org-env-${field.key}`}>
        <label>{field.label}</label>
        <select
          value={envScope[field.key] || ""}
          onChange={(e) => setEnvScope({ ...envScope, [field.key]: e.target.value })}
          disabled={!canEdit}
        >
          {Object.entries(labels).map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>
      </div>
    );
  };

  const renderProfileField = (field: string) => {
    const label = org.field_labels[field] || field;
    const placeholder = org.field_placeholders[field] || "";
    const isTextarea = ["system_description", "architecture_summary", "boundary_description",
      "hardware_inventory", "software_inventory", "team_roster",
      "subservice_organizations", "user_entity_controls"].includes(field);

    return (
      <div className="form-row" key={field} id={`org-${field}`}>
        <label>{label}</label>
        {isTextarea ? (
          <textarea
            value={profile[field] || ""}
            onChange={(e) => setProfile({ ...profile, [field]: e.target.value })}
            disabled={!canEdit}
            placeholder={placeholder}
            rows={3}
          />
        ) : (
          <input
            type="text"
            value={profile[field] || ""}
            onChange={(e) => setProfile({ ...profile, [field]: e.target.value })}
            disabled={!canEdit}
            placeholder={placeholder}
          />
        )}
      </div>
    );
  };

  return (
    <div className="page-stack">
      <PageIntro title="Organization" />

      {msg && (
        <div className={`banner ${msg.type === "ok" ? "success" : "error"}`}>{msg.text}</div>
      )}

      {settings?.workspace_locked && (
        <div className="banner info">Workspace is locked — organization profile is read-only.</div>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
        <button
          type="button"
          className={`btn ${useWizard ? "btn-primary" : "btn-secondary"} btn-sm`}
          onClick={() => setUseWizard(true)}
          disabled={!canEdit}
        >
          Guided setup
        </button>
        <button
          type="button"
          className={`btn ${!useWizard ? "btn-primary" : "btn-secondary"} btn-sm`}
          onClick={() => setUseWizard(false)}
          disabled={!canEdit}
        >
          Full form
        </button>
      </div>

      {!useWizard && <OrgSetupChecklist org={org} />}

      {useWizard ? (
        <ProfileWizard
          org={org}
          profile={profile}
          envScope={envScope}
          disabled={!canEdit}
          onProfileChange={(patch: Partial<OrgProfile>) => setProfile({ ...profile, ...patch } as OrgProfile)}
          onEnvChange={(patch: Partial<EnvScope>) => setEnvScope({ ...envScope, ...patch } as EnvScope)}
          onComplete={saveAll}
        />
      ) : (
        <>
          <section className="panel" id="org-identity" style={{ marginBottom: 16 }}>
            <div className="panel-header"><h3>Organization & System</h3></div>
            <div className="panel-body">
              <div className="form-grid">
                {renderProfileField("org_name")}
                {renderProfileField("system_name")}
                {renderProfileField("system_description")}
                {renderProfileField("architecture_summary")}
                {renderProfileField("boundary_description")}
              </div>
            </div>
          </section>

          <section className="panel" id="org-roles" style={{ marginBottom: 16 }}>
            <div className="panel-header"><h3>Team & Roles</h3></div>
            <div className="panel-body">
              <div className="form-grid">
                {renderProfileField("system_owner")}
                {renderProfileField("compliance_officer")}
                {renderProfileField("it_admin")}
                {renderProfileField("auditor_name")}
                {renderProfileField("team_roster")}
              </div>
            </div>
          </section>

          <section className="panel" id="org-env" style={{ marginBottom: 16 }}>
            <div className="panel-header"><h3>Environment Scope</h3></div>
            <div className="panel-body">
              <div className="form-grid">
                {envFields.map(renderEnvSelect)}
              </div>
              {org.env_scope_summary && (
                <pre style={{ fontSize: 12, marginTop: 12, whiteSpace: "pre-wrap" }}>{org.env_scope_summary}</pre>
              )}
              {org.scoping_suggestions && org.scoping_suggestions.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <strong>Scoping suggestions:</strong>
                  <ul style={{ marginTop: 4 }}>
                    {org.scoping_suggestions.map((s, i) => (
                      <li key={i}>
                        <a href={`/criteria/${s.control_id}`} className="btn-link">{s.control_id}</a> — {s.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>

          <section className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-header"><h3>Trust Services Criteria Scope</h3></div>
            <div className="panel-body">
              <p className="muted" style={{ fontSize: 13 }}>
                Select which TSC categories apply to your organization. Only in-scope criteria will appear in the app.
                Security (Common Criteria) is always required.
              </p>
              <Link to="/scoping" className="btn btn-primary btn-sm">
                {org.scoping_completed ? "Edit scope" : "Set scope →"}
              </Link>
            </div>
          </section>

            <section className="panel" id="org-cuec" style={{ marginBottom: 16 }}>
              <div className="panel-header"><h3>Complementary Controls (CUEC / CSOC)</h3></div>
              <div className="panel-body">
                <p className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
                  The AICPA SOC 2 framework requires disclosure of controls at subservice organizations and user entities.
                </p>
                <div className="form-grid">
                  {renderProfileField("subservice_organizations")}
                  {renderProfileField("reporting_method")}
                  {renderProfileField("user_entity_controls")}
                </div>
              </div>
            </section>

            <section className="panel" id="org-inventory" style={{ marginBottom: 16 }}>
              <div className="panel-header"><h3>Asset Inventory</h3></div>
              <div className="panel-body">
                <InventoryTable
                  assets={inventory}
                  disabled={!canEdit}
                  onChange={setInventory}
                />
                {org.org_inventory?.updated_at && (
                  <p className="muted" style={{ marginTop: 8, fontSize: 12 }}>
                    Last updated: {org.org_inventory.updated_at}
                  </p>
                )}
              </div>
            </section>

            {documents.length > 0 && (
              <section className="panel" id="org-documents" style={{ marginBottom: 16 }}>
                <div className="panel-header">
                  <h3>Required documents</h3>
                  <span className="muted">
                    {documents.filter((d: any) => d.status === "ok").length}/{documents.length} complete
                  </span>
                </div>
                <div className="panel-body" style={{ padding: 0 }}>
                  <table className="data-table" style={{ width: "100%" }}>
                    <thead>
                      <tr>
                        <th>Document</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Evidence</th>
                        <th>Controls</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map((doc: any) => (
                        <tr key={doc.key}>
                          <td>{doc.name}</td>
                          <td><span className="muted" style={{ fontSize: "0.75rem" }}>{doc.evidence_type}</span></td>
                          <td>
                            {doc.status === "ok"
                              ? <span className="badge badge-success">OK</span>
                              : <span className="badge badge-danger">Needs document</span>
                            }
                          </td>
                          <td><span className="muted">{doc.evidence_count || 0}</span></td>
                          <td>
                            <span style={{ fontSize: "0.75rem", wordBreak: "break-all" }}>
                              {doc.controls.slice(0, 4).join(", ")}{doc.controls.length > 4 ? ` +${doc.controls.length - 4}` : ""}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

        </>
      )}

      {!useWizard && canEdit && (
        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <button type="button" className="btn btn-primary" onClick={saveAll} disabled={saving}>
            {saving ? "Saving…" : "Save all"}
          </button>
          {msg && <span className="muted" style={{ alignSelf: "center" }}>{msg.text}</span>}
        </div>
      )}

      {org.audit_log && org.audit_log.length > 0 && (
        <section className="panel" style={{ marginTop: 16 }}>
          <div className="panel-header"><h3>Recent changes</h3></div>
          <div className="panel-body">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Event</th>
                  <th>User</th>
                </tr>
              </thead>
              <tbody>
                {org.audit_log.slice(-10).reverse().map((entry, i) => (
                  <tr key={i}>
                    <td>{entry.timestamp}</td>
                    <td>{entry.event}</td>
                    <td>{String(entry.user || "")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
