import { FormEvent, useEffect, useState } from "react";
import { api, authFetch, authenticatedDownload, apiUrl, CmmcAssessmentStatus, CmmcScope, ContractRecord, Organization } from "../api";
import InventoryTable from "../components/InventoryTable";
import ScopeCoveragePanel from "../components/ScopeCoveragePanel";
import InheritancePanel from "../components/InheritancePanel";
import OrgSetupChecklist from "../components/OrgSetupChecklist";
import PageIntro from "../components/PageIntro";
import { useLayout } from "../Layout";
import { PageSkeleton } from "../components/ui/Skeleton";

const PROFILE_FIELDS: [string, string, string?][] = [
  ["org_name", "Organization name"],
  ["system_name", "System name"],
  ["header_short_name", "Short name (header)", "optional"],
  ["system_unique_id", "System unique ID", "optional"],
  ["cage_code", "CAGE code", "optional"],
  ["uei", "UEI (Unique Entity ID)", "optional"],
  ["system_owner", "System owner"],
  ["system_owner_title", "System owner title", "optional"],
  ["iso_name", "Information security officer"],
  ["iso_title", "ISO / SSO title", "optional"],
  ["sysadmin_name", "System administrator"],
  ["network_admin_name", "Network administrator"],
  ["auditor_name", "Assessor / auditor"],
  ["org_address", "Address"],
  ["org_phone", "Phone"],
  ["gov_poc_name", "Government POC name", "optional"],
  ["gov_poc_title", "Government POC title", "optional"],
  ["gov_poc_address", "Government POC office address", "optional"],
  ["gov_poc_phone", "Government POC phone", "optional"],
  ["gov_poc_email", "Government POC email", "optional"],
  ["system_description", "System description", "textarea"],
  ["architecture_summary", "Architecture summary", "textarea"],
  ["boundary_description", "System boundary", "textarea"],
];

type DocumentItem = {
  key: string;
  name: string;
  category: string;
  controls: string[];
  evidence_type: string;
  status: string;
  evidence_count: number;
  last_uploaded: string | null;
};

const ENV_FIELDS: [string, string][] = [
  ["wireless", "Wireless in scope? (yes/no)"],
  ["remote_access", "Remote access in scope? (yes/no)"],
  ["mobile_devices", "Mobile devices in scope? (yes/no)"],
  ["cloud_provider", "Cloud (on_prem_only/azure/aws/both/other)"],
  ["m365_cui", "Microsoft 365 for CUI? (yes/no)"],
];

function EnvScopeFields({
  org,
  envScope,
  onChange,
  disabled,
}: {
  org: Organization;
  envScope: Record<string, string>;
  onChange: (next: Record<string, string>) => void;
  disabled?: boolean;
}) {
  const labels = org.env_scope_labels ?? { yes_no: { "": "Not answered", yes: "Yes", no: "No" }, cloud: {} };
  const fields = org.env_scope_fields ?? [];

  if (!fields.length) {
    return (
      <div className="form-grid">
        {ENV_FIELDS.map(([key, label]) => (
          <div key={key}>
            <label htmlFor={`env-${key}`}>{label}</label>
            <input
              id={`env-${key}`}
              value={envScope[key] || ""}
              disabled={disabled}
              onChange={(e) => onChange({ ...envScope, [key]: e.target.value })}
            />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="form-grid">
      {fields.map((f) => (
        <div key={f.key} className={f.type === "cloud" ? "span-2" : undefined}>
          <label htmlFor={`env-${f.key}`}>{f.label}</label>
          <select
            id={`env-${f.key}`}
            value={envScope[f.key] || ""}
            disabled={disabled}
            onChange={(e) => onChange({ ...envScope, [f.key]: e.target.value })}
          >
            {Object.entries(f.type === "cloud" ? labels.cloud : labels.yes_no).map(([val, lab]) => (
              <option key={val} value={val}>{lab}</option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
}

export default function OrganizationPage() {
  const { canEditOrg, canExport, settings } = useLayout();
  const [org, setOrg] = useState<Organization | null>(null);
  const [profile, setProfile] = useState<Record<string, string>>({});
  const [assetScope, setAssetScope] = useState<Record<string, number>>({});
  const [envScope, setEnvScope] = useState<Record<string, string>>({});
  const [inventory, setInventory] = useState<Record<string, string>[]>([]);
  const [systemScope, setSystemScope] = useState<Record<string, string>>({});
  const [appendixLabel, setAppendixLabel] = useState("");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({
    systemScope: true,
    topology: true,
  });
  const toggleSection = (key: string) => setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));

  const load = () =>
    api.organization().then((data) => {
      setOrg(data);
      setProfile(data.org_profile);
      setAssetScope(data.asset_scope);
      setEnvScope(data.env_scope);
      setInventory(data.org_inventory.assets || []);
      setSystemScope(data.system_scope || {});
    });

  useEffect(() => {
    load().catch(console.error);
  }, []);

  useEffect(() => {
    authFetch("/api/documents")
      .then((r) => r.json())
      .then((data) => setDocuments(data.documents || []))
      .catch(() => {});
  }, []);

  const saveAll = async () => {
    await api.patchOrgProfile(profile);
    if (Object.keys(assetScope).length) await api.patchAssetScope(assetScope);
    await api.patchEnvScope(envScope);
    await api.patchInventory(inventory.filter((r) => Object.values(r).some((v) => v?.trim())));
    if (Object.keys(systemScope).length) await api.patchSystemScope(systemScope);
  };

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMsg("");
    try {
      await saveAll();
      setMsg("Saved.");
      await load();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setSaving(false);
    }
  };

  const onInventoryImport = async (file: File) => {
    const result = await api.importInventory(file);
    setMsg(`Imported ${result.imported} asset(s).`);
    await load();
  };

  if (!org) return <PageSkeleton />;

  return (
    <>
      <PageIntro view="Organization" title="System profile" />
      {msg && <div className="banner info">{msg}</div>}
      {!canEditOrg && (
        <div className="banner warning">
          Read-only for {settings?.current_role ?? "this role"} — switch to Assessor or Compliance Manager to edit organization data.
        </div>
      )}

      <OrgSetupChecklist org={org} />
      <form className="panel-stack org-profile-form" onSubmit={saveProfile}>
      <div className="panel">
            <div className="panel-header">
              <strong>System profile</strong>
            </div>
            <div className="panel-body form-grid">
              {PROFILE_FIELDS.map(([key, label, kind]) => (
                <div key={key} className={kind === "textarea" ? "span-2" : undefined}>
                  <label htmlFor={key}>{label}</label>
                  {kind === "textarea" ? (
                    <textarea
                      id={key}
                      value={profile[key] || ""}
                      disabled={!canEditOrg}
                      onChange={(e) => setProfile({ ...profile, [key]: e.target.value })}
                      rows={3}
                    />
                  ) : (
                    <input
                      id={key}
                      value={profile[key] || ""}
                      disabled={!canEditOrg}
                      onChange={(e) => setProfile({ ...profile, [key]: e.target.value })}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header"><strong>Assessment team</strong></div>
            <div className="panel-body form-grid">
              <div className="span-2">
                <label htmlFor="team_roster">Additional team members</label>
                <textarea
                  id="team_roster"
                  value={profile.team_roster || ""}
                  disabled={!canEditOrg}
                  onChange={(e) => setProfile({ ...profile, team_roster: e.target.value })}
                  rows={4}
                  placeholder={"One name per line — used for control assignments.\nKey roles above are included automatically."}
                />
                {(org.team_members?.length ?? 0) > 0 && (
                  <p className="muted field-hint">
                    Roster: {org.team_members?.join(", ")}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="panel" id="org-scope">
            <div className="panel-header"><strong>Assessment scope</strong>
              <span className="muted">{org.scoped_controls_count} controls in scope</span>
            </div>
            <div className="panel-body form-grid">
              {Object.entries(org.asset_types).map(([asset, desc]) => (
                <div key={asset}>
                  <label htmlFor={`scope-${asset}`}>{asset} (%)</label>
                  <input
                    id={`scope-${asset}`}
                    type="number"
                    min={0}
                    max={100}
                    step={5}
                    disabled={!canEditOrg}
                    value={assetScope[asset] ?? 0}
                    onChange={(e) =>
                      setAssetScope({ ...assetScope, [asset]: Number(e.target.value) })
                    }
                  />
                  <p className="muted field-hint">{desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="panel" id="org-env">
            <div className="panel-header"><strong>Environment scope</strong></div>
            <div className="panel-body">
              <p className="panel-intro">
                Answer each question below, then save. This unlocks N/A suggestions on Controls,
                inheritance hints, and export contradiction checks.
              </p>
              <EnvScopeFields org={org} envScope={envScope} onChange={setEnvScope} disabled={!canEditOrg} />
            </div>
          </div>

          <InheritancePanel
            envScopeComplete={Boolean(org.env_scope_complete)}
            envScopeSummary={org.env_scope_summary || ""}
            hints={org.inheritance_hints || []}
            mapRows={org.inheritance_map || []}
            suggestions={org.scoping_suggestions || []}
          />

          <div className="panel" id="org-env">
            <button
              type="button"
              className="panel-header inheritance-map-toggle"
              aria-expanded={!collapsed.systemScope}
              onClick={() => toggleSection("systemScope")}
            >
              <strong>System scope</strong>
            </button>
            {!collapsed.systemScope && (
            <div className="panel-body form-grid">
              <div className="span-2">
                <label htmlFor="sco-cui-types">CUI types handled by this system</label>
                <textarea
                  id="sco-cui-types"
                  rows={2}
                  disabled={!canEditOrg}
                  value={systemScope.cui_types || ""}
                  onChange={(e) => setSystemScope({ ...systemScope, cui_types: e.target.value })}
                  placeholder="e.g. Export Controlled, ITAR, Proprietary, PII, FOUO"
                />
              </div>
              <div className="span-2">
                <label htmlFor="sco-connections">External connections / interconnections</label>
                <textarea
                  id="sco-connections"
                  rows={3}
                  disabled={!canEditOrg}
                  value={systemScope.external_connections || ""}
                  onChange={(e) => setSystemScope({ ...systemScope, external_connections: e.target.value })}
                  placeholder="One per line — system name, organization, purpose, protocol, encrypted (yes/no)"
                />
                <p className="muted field-hint">
                  List API pipes, VPNs, federated tenants, partner networks authorized to connect to this system.
                </p>
              </div>
              <div>
                <label htmlFor="sco-review">Last scope review</label>
                <input
                  id="sco-review"
                  type="text"
                  disabled={!canEditOrg}
                  value={systemScope.last_review || ""}
                  onChange={(e) => setSystemScope({ ...systemScope, last_review: e.target.value })}
                  placeholder="YYYY-MM-DD"
                />
              </div>
            </div>
            )}
          </div>

          <div className="panel" id="org-topology-section">
            <button
              type="button"
              className="panel-header inheritance-map-toggle"
              aria-expanded={!collapsed.topology}
              onClick={() => toggleSection("topology")}
            >
              <strong>Topology &amp; assets</strong>
            </button>
            {!collapsed.topology && (
            <div className="panel-body" style={{ padding: 0 }}>
              <div style={{ padding: "1rem", borderBottom: "1px solid var(--border)" }}>
                <strong style={{ fontSize: "0.875rem" }}>System environment (SSP text)</strong>
                <div className="form-grid" style={{ marginTop: "0.75rem" }}>
                  <div className="span-2">
                    <label htmlFor="hardware_inventory">Hardware inventory</label>
                    <textarea
                      id="hardware_inventory"
                      value={profile.hardware_inventory || ""}
                      disabled={!canEditOrg}
                      placeholder="Servers, firewalls, endpoints, cloud tenants\u2026 or \u201cSee attached inventory.xlsx\u201d"
                      rows={4}
                      onChange={(e) => setProfile({ ...profile, hardware_inventory: e.target.value })}
                    />
                  </div>
                  <div className="span-2">
                    <label htmlFor="software_inventory">Software inventory</label>
                    <textarea
                      id="software_inventory"
                      value={profile.software_inventory || ""}
                      disabled={!canEditOrg}
                      placeholder="OS versions, M365, Azure services, AV/EDR, etc."
                      rows={4}
                      onChange={(e) => setProfile({ ...profile, software_inventory: e.target.value })}
                    />
                  </div>
                  <div className="span-2">
                    <label htmlFor="hw_sw_org_owned">Hardware/software maintained and owned by org?</label>
                    <input
                      id="hw_sw_org_owned"
                      value={profile.hw_sw_org_owned || "Yes"}
                      disabled={!canEditOrg}
                      placeholder="Yes, or \u201cNo \u2014 explain\u201d for leased/managed services"
                      onChange={(e) => setProfile({ ...profile, hw_sw_org_owned: e.target.value })}
                    />
                  </div>
                </div>
              </div>
              <div style={{ padding: "1rem", borderBottom: "1px solid var(--border)" }}>
                <strong style={{ fontSize: "0.875rem" }}>Topology &amp; appendices</strong>
                <p className="muted">
                  Topology PNG/JPG embeds in SSP export. Appendix files are indexed in the SSP appendix.
                </p>
                {org.org_assets.topology_filename ? (
                  <p>
                    Topology: <strong>{org.org_assets.topology_filename}</strong>{" "}
                    {canEditOrg && (
                      <button type="button" className="btn-link" onClick={() => api.deleteTopology().then(load)}>
                        Remove
                      </button>
                    )}
                  </p>
                ) : (
                  canEditOrg && (
                  <input
                    type="file"
                    accept=".png,.jpg,.jpeg"
                    onChange={(e) => e.target.files?.[0] && api.uploadTopology(e.target.files[0]).then(load)}
                  />
                  )
                )}
                <div style={{ marginTop: "1rem" }}>
                  <label>Appendix documents</label>
                  {(org.org_assets.appendix_files || []).map((f) => (
                    <div key={f.filename} className="appendix-row">
                      {f.label || f.filename}{" "}
                      {canEditOrg && (
                      <button
                        type="button"
                        className="btn-link"
                        onClick={() => api.deleteAppendix(f.filename).then(load)}
                      >
                        Remove
                      </button>
                      )}
                    </div>
                  ))}
                  {canEditOrg && (
                  <>
                  <input
                    type="text"
                    placeholder="Document title (shown in SSP)"
                    value={appendixLabel}
                    onChange={(e) => setAppendixLabel(e.target.value)}
                  />
                  <input
                    type="file"
                    onChange={(e) =>
                      e.target.files?.[0] &&
                      api.uploadAppendix(e.target.files[0], appendixLabel).then(load)
                    }
                  />
                  </>
                  )}
                </div>
              </div>
              <div style={{ padding: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <strong style={{ fontSize: "0.875rem" }}>Asset inventory</strong>
                  {canExport && <a className="btn-link" href="#" onClick={(e) => { e.preventDefault(); authenticatedDownload(apiUrl("/api/export/appendix-pack"), "appendix-pack.zip"); }}>Appendix pack</a>}
                </div>
                {canEditOrg && (
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => e.target.files?.[0] && onInventoryImport(e.target.files[0])}
                />
                )}
                <InventoryTable
                  rows={inventory}
                  onChange={setInventory}
                  disabled={!canEditOrg}
                  updatedAt={org.org_inventory.updated_at}
                />
              </div>
            </div>
            )}
          </div>

          <div className="panel">
            <div className="panel-header">
              <strong>Required documents</strong>
              <span className="muted">
                {documents.filter((d) => d.status === "ok").length}/{documents.length} complete
              </span>
            </div>
            <div className="panel-body panel-body--flush">
              <table>
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Last updated</th>
                    <th>Files</th>
                    <th>Controls</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.key}>
                      <td>{doc.name}</td>
                      <td>
                        <span className="muted table-cell-sm">{doc.evidence_type}</span>
                      </td>
                      <td>
                        {doc.status === "ok" ? <span style={{ color: "var(--success)" }}>✓</span> : <span className="muted">—</span>}
                      </td>
                      <td>
                        <span className="muted">{doc.last_uploaded ? doc.last_uploaded.slice(0, 10) : "—"}</span>
                      </td>
                      <td>{doc.evidence_count || "0"}</td>
                      <td>
                        <span className="table-cell-small">
                          {doc.controls.slice(0, 4).join(", ")}{doc.controls.length > 4 ? ` +${doc.controls.length - 4}` : ""}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <ScopeCoveragePanel coverage={org.scope_coverage} />

          {canEditOrg && (
          <div className="btn-row">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Save organization"}
            </button>
          </div>
          )}
        </form>

        <AssessmentStatusPanel canEdit={canEditOrg} />
        <AssessmentScopePanel canEdit={canEditOrg} />
        <ContractFlowdownPanel canEdit={canEditOrg} />
    </>
  );
}

function ContractFlowdownPanel({ canEdit }: { canEdit: boolean }) {
  const [contracts, setContracts] = useState<ContractRecord[]>([]);
  const [form, setForm] = useState<ContractRecord>({
    name: "",
    contract_number: "",
    clause: "252.204-7020",
    required_status: "",
    flowdown_required: true,
    notes: "",
  });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = () => api.contracts().then((d) => setContracts(d.contracts)).catch(() => {});
  useEffect(() => {
    load();
  }, []);

  const add = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name) return;
    setBusy(true);
    setMsg("");
    try {
      await api.createContract(form);
      setForm({ ...form, name: "", contract_number: "", notes: "" });
      await load();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id: string) => {
    await api.deleteContract(id);
    await load();
  };

  const mismatchCount = contracts.filter((c) => c.mismatch).length;

  return (
    <div className="panel">
      <div className="panel-header">
        <strong>Contracts &amp; CMMC flowdown (32 CFR 170.23 / DFARS 252.204-7020-7021)</strong>
      </div>
      <div className="panel-body">
        {msg && <div className="banner info">{msg}</div>}
        {mismatchCount > 0 && (
          <div className="banner warning">
            {mismatchCount} contract{mismatchCount === 1 ? "" : "s"} require a CMMC status you do not currently hold —
            set your assessment status on the panel above.
          </div>
        )}
        {contracts.length === 0 && <p className="muted">No contracts recorded.</p>}
        {contracts.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Contract</th>
                <th>Number</th>
                <th>Clause</th>
                <th>Required status</th>
                <th>Held status</th>
                <th>Flowdown</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {contracts.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.contract_number || "—"}</td>
                  <td>{c.clause || "—"}</td>
                  <td>{c.required_status || "—"}</td>
                  <td>
                    {c.held_status || "None"}{" "}
                    {c.mismatch && <span className="badge badge-danger">mismatch</span>}
                  </td>
                  <td>{c.flowdown_required ? "Yes" : "No"}</td>
                  <td>
                    {canEdit && (
                      <button type="button" className="btn-link" onClick={() => c.id && remove(c.id)}>
                        Remove
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {canEdit && (
          <form className="form-grid" onSubmit={add} style={{ marginTop: "1rem" }}>
            <div>
              <label htmlFor="ct-name">Contract name</label>
              <input id="ct-name" type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label htmlFor="ct-number">Contract number</label>
              <input id="ct-number" type="text" value={form.contract_number} onChange={(e) => setForm({ ...form, contract_number: e.target.value })} />
            </div>
            <div>
              <label htmlFor="ct-clause">DFARS clause</label>
              <select id="ct-clause" value={form.clause} onChange={(e) => setForm({ ...form, clause: e.target.value })}>
                <option value="252.204-7020">252.204-7020 (NIST SP 800-171 DoD Assessment)</option>
                <option value="252.204-7021">252.204-7021 (CMMC)</option>
              </select>
            </div>
            <div>
              <label htmlFor="ct-status">Required CMMC status</label>
              <select id="ct-status" value={form.required_status} onChange={(e) => setForm({ ...form, required_status: e.target.value })}>
                <option value="">— select —</option>
                <option value="level1_self">Level 1 (Self)</option>
                <option value="level2_self">Level 2 (Self)</option>
                <option value="level2_c3pao">Level 2 (C3PAO)</option>
              </select>
            </div>
            <div>
              <label htmlFor="ct-flow">Flowdown to subcontractors</label>
              <select id="ct-flow" value={form.flowdown_required ? "yes" : "no"} onChange={(e) => setForm({ ...form, flowdown_required: e.target.value === "yes" })}>
                <option value="yes">Required</option>
                <option value="no">Not required</option>
              </select>
            </div>
            <div className="span-2">
              <label htmlFor="ct-notes">Notes</label>
              <input id="ct-notes" type="text" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
            <div className="btn-row" style={{ gridColumn: "1 / -1" }}>
              <button type="submit" className="btn-primary" disabled={busy}>
                {busy ? "Adding…" : "Add contract"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

function AssessmentScopePanel({ canEdit }: { canEdit: boolean }) {
  const [scope, setScope] = useState<CmmcScope>({
    esp: "",
    esp_name: "",
    esp_facilities: "",
    facilities: "",
    scope_statement: "",
    assets_in_scope: "",
  });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.assessmentScope().then((d) => setScope(d.scope)).catch(() => {});
  }, []);

  const save = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    try {
      const res = await api.putAssessmentScope(scope);
      setScope(res.scope);
      setMsg("Assessment scope saved — included in the SPRS entry summary.");
    } catch (err) {
      setMsg(String(err));
    } finally {
      setBusy(false);
    }
  };

  const set = (k: keyof CmmcScope) => (e: { target: { value: string } }) =>
    setScope({ ...scope, [k]: e.target.value });

  return (
    <div className="panel">
      <div className="panel-header">
        <strong>CMMC assessment scope (32 CFR Part 170.19)</strong>
      </div>
      <div className="panel-body">
        {msg && <div className="banner info">{msg}</div>}
        <form onSubmit={save}>
          <div className="form-grid">
            <div>
              <label htmlFor="scope-esp">External Service Provider (ESP) in scope</label>
              <select id="scope-esp" value={scope.esp} disabled={!canEdit || busy} onChange={set("esp")}>
                <option value="">— select —</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div>
              <label htmlFor="scope-esp-name">ESP name</label>
              <input id="scope-esp-name" type="text" value={scope.esp_name} disabled={!canEdit || busy} onChange={set("esp_name")} />
            </div>
            <div>
              <label htmlFor="scope-esp-fac">ESP facilities</label>
              <input id="scope-esp-fac" type="text" value={scope.esp_facilities} disabled={!canEdit || busy} onChange={set("esp_facilities")} />
            </div>
            <div>
              <label htmlFor="scope-fac">Contractor facilities</label>
              <input id="scope-fac" type="text" value={scope.facilities} disabled={!canEdit || busy} onChange={set("facilities")} />
            </div>
            <div className="span-2">
              <label htmlFor="scope-statement">Scope statement</label>
              <textarea
                id="scope-statement"
                value={scope.scope_statement}
                disabled={!canEdit || busy}
                onChange={set("scope_statement")}
                placeholder="Describe the assessment scope: systems, boundaries, and CUI handling in scope…"
              />
            </div>
            <div className="span-2">
              <label htmlFor="scope-assets">Assets in scope (summary)</label>
              <textarea
                id="scope-assets"
                value={scope.assets_in_scope}
                disabled={!canEdit || busy}
                onChange={set("assets_in_scope")}
              />
            </div>
          </div>
          {canEdit && (
            <div className="btn-row" style={{ marginTop: "1rem" }}>
              <button type="submit" className="btn-primary" disabled={busy}>
                {busy ? "Saving…" : "Save assessment scope"}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

const ASSESSMENT_TYPE_OPTIONS = [
  ["", "— not declared —"],
  ["level1_self", "Level 1 (Self) — FAR 52.204-21"],
  ["level2_self", "Level 2 (Self)"],
  ["level2_c3pao", "Level 2 (C3PAO)"],
];

function AssessmentStatusPanel({ canEdit }: { canEdit: boolean }) {
  const [status, setStatus] = useState<CmmcAssessmentStatus | null>(null);
  const [form, setForm] = useState({ assessment_type: "", status: "", status_date: "", affirming_official: "" });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = () =>
    api.assessmentStatus().then((s) => {
      setStatus(s);
      setForm({
        assessment_type: s.assessment_type,
        status: s.status,
        status_date: s.status_date || "",
        affirming_official: s.affirming_official,
      });
    });

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const save = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    try {
      setStatus(await api.putAssessmentStatus(form));
      setForm((f) => ({ ...f, status_date: status?.status_date || f.status_date }));
      setMsg("Assessment status saved.");
      await load();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setBusy(false);
    }
  };

  const days = (n: number | null | undefined) => (n === null || n === undefined ? "—" : `${n} days`);

  return (
    <div className="panel">
      <div className="panel-header">
        <strong>CMMC assessment status (32 CFR Part 170)</strong>
      </div>
      <div className="panel-body">
        {msg && <div className="banner info">{msg}</div>}
        <form onSubmit={save}>
          <div className="form-grid">
            <div>
              <label htmlFor="assessment_type">Assessment type</label>
              <select
                id="assessment_type"
                value={form.assessment_type}
                disabled={!canEdit || busy}
                onChange={(e) => setForm({ ...form, assessment_type: e.target.value })}
              >
                {ASSESSMENT_TYPE_OPTIONS.map(([val, lab]) => (
                  <option key={val} value={val}>{lab}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="assessment_status">CMMC status</label>
              <select
                id="assessment_status"
                value={form.status}
                disabled={!canEdit || busy}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                <option value="">— none —</option>
                <option value="conditional">Conditional (POA&amp;M)</option>
                <option value="final">Final</option>
              </select>
            </div>
            <div>
              <label htmlFor="status_date">CMMC Status Date</label>
              <input
                id="status_date"
                type="date"
                value={form.status_date}
                disabled={!canEdit || busy}
                onChange={(e) => setForm({ ...form, status_date: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="affirming_official">Affirming Official (§ 170.22)</label>
              <input
                id="affirming_official"
                type="text"
                value={form.affirming_official}
                placeholder="Name / title"
                disabled={!canEdit || busy}
                onChange={(e) => setForm({ ...form, affirming_official: e.target.value })}
              />
            </div>
          </div>
          {canEdit && (
            <div className="btn-row" style={{ marginTop: "1rem" }}>
              <button type="submit" className="btn-primary" disabled={busy}>
                {busy ? "Saving…" : "Save assessment status"}
              </button>
            </div>
          )}
        </form>

        {status && status.status && (
          <div className="assessment-clocks" style={{ marginTop: "1rem" }}>
            <table className="table">
              <thead>
                <tr><th>Program clock</th><th>Due</th><th>Remaining</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td>POA&amp;M closeout (180 days)</td>
                  <td>{status.closeout_due || "—"}</td>
                  <td>{status.closeout_due ? (status.closeout_expired ? "EXPIRED" : days(status.closeout_days_left)) : "—"}</td>
                </tr>
                <tr>
                  <td>Reassessment (3 years)</td>
                  <td>{status.reassessment_due || "—"}</td>
                  <td>{status.reassessment_due ? (status.reassessment_expired ? "EXPIRED" : days(status.reassessment_days_left)) : "—"}</td>
                </tr>
                <tr>
                  <td>Annual affirmation</td>
                  <td>{status.affirmation_due || "—"}</td>
                  <td>{status.affirmation_due ? (status.affirmation_expired ? "EXPIRED" : days(status.affirmation_days_left)) : "—"}</td>
                </tr>
              </tbody>
            </table>
            {status.status === "conditional" && status.gap_count > 0 && (
              <div className="banner warning">
                {status.gap_count} NOT MET requirement(s) open — remediate them, then complete the closeout on the
                Readiness page before {status.closeout_due}.
              </div>
            )}
            {status.status === "conditional" && status.gap_count === 0 && (
              <div className="banner success">
                All requirements remediated — run the POA&amp;M closeout on the Readiness page to promote to Final.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
