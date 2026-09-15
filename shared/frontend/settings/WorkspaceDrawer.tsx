import { useEffect, useState } from "react";
import { applyBrand, applyTheme, getStoredTheme, getStoredBrand, type ThemeChoice, type BrandChoice } from "@cmmc/theme";
import { apiUrl } from "@shared/apiPrefix";
import { DEMO_CHOICES, DEMO_LIST } from "./demos";

type SettingsData = {
  current_role?: string;
  current_user_name?: string;
  auth_role_locked?: boolean;
  auth_user_email?: string;
  user_roles?: string[];
  team_members?: string[];
  clients?: { id: string; name: string }[];
  active_client_id?: string;
  msp_mode?: boolean;
};

type DemoStatusData = {
  is_demo?: boolean;
  label?: string;
  demo_id?: string;
};

type Props = {
  open: boolean;
  onClose: () => void;
  settings?: SettingsData | null;
  demoStatus?: DemoStatusData | null;
  demoLoading?: boolean;
  clearingDemo?: boolean;
  canExport?: boolean;
  canEdit?: boolean;
  canEditOrg?: boolean;
  showClients?: boolean;
  activeClientName?: string;
  onRoleChange?: (role: string) => void;
  onUserNameChange?: (name: string) => void;
  onMspToggle?: () => void;
  onClientSwitch?: (id: string) => void;
  onCreateClient?: () => void;
  onRenameClient?: () => void;
  onDeleteClient?: () => void;
  onLoadDemo?: (id: string) => void;
  onClearDemo?: () => void;
  onImportWorkspace?: (file: File) => Promise<any>;
  onResetControls?: () => Promise<any>;
  onResetWorkspace?: () => Promise<any>;
  showManageClient?: boolean;
  showNewClient?: boolean;
  newClientName?: string;
  renameClientName?: string;
  setShowManageClient?: (v: boolean) => void;
  setShowNewClient?: (v: boolean) => void;
  setNewClientName?: (v: string) => void;
  setRenameClientName?: (v: string) => void;
};

export default function WorkspaceDrawer(props: Props) {
  const {
    open, onClose, settings, demoStatus, demoLoading, clearingDemo,
    canExport, canEdit, canEditOrg, showClients, activeClientName = "Default",
    onRoleChange, onUserNameChange, onMspToggle, onClientSwitch,
    onCreateClient, onRenameClient, onDeleteClient,
    onLoadDemo, onClearDemo,
    onImportWorkspace, onResetControls, onResetWorkspace,
    showManageClient, showNewClient, newClientName, renameClientName,
    setShowManageClient, setShowNewClient, setNewClientName, setRenameClientName,
  } = props;

  const [theme, setTheme] = useState<ThemeChoice>(() => getStoredTheme());
  const [brand, setBrand] = useState<BrandChoice>(() => getStoredBrand());
  const [selectedDemo, setSelectedDemo] = useState("");

  useEffect(() => {
    if (demoStatus?.demo_id) {
      setSelectedDemo(demoStatus.demo_id);
    }
  }, [demoStatus?.demo_id]);

  const onThemeChange = (choice: ThemeChoice) => {
    setTheme(choice);
    applyTheme(choice);
  };

  const onBrandChange = (choice: BrandChoice) => {
    setBrand(choice);
    applyBrand(choice);
  };

  if (!open) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose} role="presentation">
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Workspace settings">
        <div className="drawer-header">
          <strong>Workspace &amp; settings</strong>
          <button type="button" className="btn-link" onClick={onClose}>Close</button>
        </div>

        <div className="drawer-body">
          <section className="drawer-section">
            <h4>Appearance</h4>
            <label className="drawer-field-label" htmlFor="shared-theme-select">Color mode</label>
            <select
              id="shared-theme-select"
              className="drawer-select"
              value={theme}
              onChange={(e) => onThemeChange(e.target.value as ThemeChoice)}
            >
              <option value="system">System</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
            <label className="drawer-field-label" htmlFor="shared-brand-select">Color style</label>
            <select
              id="shared-brand-select"
              className="drawer-select"
              value={brand}
              onChange={(e) => onBrandChange(e.target.value as BrandChoice)}
            >
              <option value="lintgrc">LintGRC (teal)</option>
              <option value="classic">Classic (slate)</option>
            </select>
            <p className="muted drawer-hint">
              LintGRC is the default and matches lintgrc.com. Classic uses the earlier slate palette.
            </p>
          </section>

          {(onRoleChange || settings?.auth_role_locked) && (
            <section className="drawer-section">
              <h4>Role view</h4>
              {settings?.auth_role_locked ? (
                <>
                  <p className="drawer-role-locked">
                    <strong>{settings.current_role}</strong>
                  </p>
                  <p className="muted drawer-hint">
                    Assigned for this organization
                    {settings.auth_user_email ? ` · signed in as ${settings.auth_user_email}` : ""}.
                  </p>
                </>
              ) : (
                <>
                  <select
                    className="drawer-select"
                    value={settings?.current_role ?? "Assessor"}
                    onChange={(e) => onRoleChange?.(e.target.value)}
                  >
                    {(settings?.user_roles ?? ["Assessor"]).map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                  {!canEdit && <p className="muted drawer-hint">Read-only controls for this role</p>}
                </>
              )}
            </section>
          )}

          {onUserNameChange && (
            <section className="drawer-section">
              <h4>Your name</h4>
              {settings?.auth_role_locked ? (
                <p className="drawer-role-locked">{settings.current_user_name || settings.auth_user_email || "—"}</p>
              ) : (
                <>
                  <p className="muted drawer-hint">
                    For <strong>My assignments</strong> on Controls. Type your name below.
                  </p>
                  <input
                    className="drawer-select"
                    defaultValue={settings?.current_user_name ?? ""}
                    placeholder="e.g. Jane Smith"
                    onBlur={(e) => onUserNameChange(e.target.value.trim())}
                  />
                </>
              )}
            </section>
          )}

          {canEditOrg && onLoadDemo && (
            <section className="drawer-section">
              <h4>Sample data</h4>
              <label className="drawer-field-label" htmlFor="shared-demo-select">Demo workspace</label>
              <select
                id="shared-demo-select"
                className="drawer-select"
                value={selectedDemo}
                disabled={demoLoading}
                onChange={(e) => setSelectedDemo(e.target.value)}
              >
                <option value="">Choose a sample…</option>
                {DEMO_LIST.map(({ id, label }) => (
                  <option key={id} value={id}>{label}</option>
                ))}
              </select>
              {selectedDemo && selectedDemo in DEMO_CHOICES && (
                <p className="muted drawer-hint">
                  {DEMO_CHOICES[selectedDemo as keyof typeof DEMO_CHOICES].description}
                </p>
              )}
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={demoLoading || !selectedDemo || selectedDemo === demoStatus?.demo_id}
                onClick={() => selectedDemo && onLoadDemo(selectedDemo)}
              >
                {demoLoading ? "Loading…" : selectedDemo === demoStatus?.demo_id ? "Currently loaded" : "Load sample"}
              </button>
              {demoStatus?.is_demo && (
                <>
                  <p className="muted drawer-hint">
                    <strong>{demoStatus.label}</strong> sample is active. Scores and exports are for training only.
                  </p>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    disabled={clearingDemo || demoLoading}
                    onClick={onClearDemo}
                  >
                    {clearingDemo ? "Exiting…" : "Exit demo"}
                  </button>
                </>
              )}
            </section>
          )}

          {(onMspToggle || (showClients && onClientSwitch)) && (
            <section className="drawer-section">
              <h4>Multi-client</h4>
              {onMspToggle && (
                <label className="drawer-check">
                  <input type="checkbox" checked={settings?.msp_mode ?? false} onChange={onMspToggle} />
                  MSP / consultant mode
                </label>
              )}
              {showClients && settings && onClientSwitch && (
                <>
                  <select
                    className="drawer-select"
                    value={settings.active_client_id}
                    onChange={(e) => onClientSwitch(e.target.value)}
                  >
                    {settings.clients?.map((c) => (
                      <option key={c.id} value={c.id}>{c.name || c.id}</option>
                    ))}
                  </select>
                  {onMspToggle && settings.msp_mode && (
                    <>
                      {setShowNewClient && setNewClientName && onCreateClient && (
                        showNewClient ? (
                          <div className="new-client-row">
                            <input value={newClientName} onChange={(e) => setNewClientName(e.target.value)} placeholder="Client name" />
                            <button type="button" className="btn-link" onClick={onCreateClient}>Add</button>
                          </div>
                        ) : (
                          <button type="button" className="btn-link" onClick={() => setShowNewClient(true)}>+ New client</button>
                        )
                      )}
                      {setShowManageClient && setRenameClientName && settings.clients && settings.clients.length > 1 && (
                        <>
                          <button type="button" className="btn-link" onClick={() => setShowManageClient(!showManageClient)}>
                            {showManageClient ? "Hide manage" : "Manage clients"}
                          </button>
                          {showManageClient && (
                            <div className="manage-client-panel">
                              <input value={renameClientName} onChange={(e) => setRenameClientName(e.target.value)} placeholder="Rename client" />
                              <button type="button" className="btn-link" onClick={onRenameClient}>Save name</button>
                              {settings.active_client_id !== "default" && (
                                <button type="button" className="btn-link danger-text" onClick={onDeleteClient}>Delete client</button>
                              )}
                            </div>
                          )}
                        </>
                      )}
                    </>
                  )}
                </>
              )}
            </section>
          )}

          {(onImportWorkspace || onResetControls || onResetWorkspace || canExport) && (
            <section className="drawer-section">
              <h4>Backup &amp; data</h4>
              {canExport && (
                <>
                  <a className="btn btn-secondary btn-sm" href={apiUrl("/api/export/workspace")}>Download backup (.zip)</a>
                  <a className="btn btn-secondary btn-sm" href={apiUrl("/api/export/oscal")}>OSCAL JSON</a>
                </>
              )}
              {onImportWorkspace && (
                <label className="btn btn-secondary btn-sm drawer-upload">
                  Restore from zip
                  <input
                    type="file"
                    accept=".zip"
                    hidden
                    onChange={async (e) => {
                      const f = e.target.files?.[0];
                      if (!f) return;
                      await onImportWorkspace(f);
                      window.location.reload();
                    }}
                  />
                </label>
              )}
              {onResetControls && (
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={async () => {
                    if (window.confirm("Reset control answers only? Organization profile stays.")) {
                      await onResetControls();
                      window.location.reload();
                    }
                  }}
                >
                  Reset control answers
                </button>
              )}
              {onResetWorkspace && (
                <button
                  type="button"
                  className="btn btn-secondary btn-sm danger-text"
                  onClick={async () => {
                    if (window.confirm("Reset entire workspace?")) {
                      await onResetWorkspace();
                      window.location.reload();
                    }
                  }}
                >
                  Reset workspace
                </button>
              )}
            </section>
          )}

          <p className="muted drawer-foot">Active: {activeClientName} · Data stays on this machine</p>
        </div>
      </div>
    </div>
  );
}
