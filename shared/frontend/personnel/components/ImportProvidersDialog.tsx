import { useEffect, useState } from "react";
import { personnelApi } from "../api";
import ProviderConfigForm from "./ProviderConfigForm";

const PROVIDERS = [
  { key: "entra", label: "Microsoft Entra ID" },
  { key: "okta", label: "Okta" },
  { key: "scim", label: "SCIM 2.0" },
] as const;

export default function ImportProvidersDialog({ onClose }: { onClose: () => void }) {
  const [providerData, setProviderData] = useState<Record<string, { configured: boolean; label: string; schema: any; config: Record<string, string | boolean> } | null>>({});
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState<string | null>(null);
  const [importMsg, setImportMsg] = useState<{ ok: boolean; msg: string } | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const refresh = async () => {
    setLoading(true);
    const results: Record<string, any> = {};
    for (const p of PROVIDERS) {
      try {
        const r = await personnelApi.getProviderConfig(p.key);
        if (r.ok) {
          const configured = r.schema.fields.every((f: any) => {
            if (f.is_secret) return r.config[`has_${f.key}`] === true;
            return (r.config[f.key] as string || "").trim().length > 0;
          });
          results[p.key] = { configured, label: r.schema.label, schema: r.schema, config: r.config };
        } else {
          results[p.key] = { configured: false, label: p.label, schema: null, config: {} };
        }
      } catch {
        results[p.key] = { configured: false, label: p.label, schema: null, config: {} };
      }
    }
    setProviderData(results);
    setLoading(false);
  };

  useEffect(() => { refresh(); }, []);

  const handleImport = async (provider: string) => {
    setImporting(provider);
    setImportMsg(null);
    try {
      const result = await personnelApi.importFrom(provider);
      if (result.ok) {
        const parts = [`${result.count} imported`];
        if (result.updated > 0) parts.push(`${result.updated} updated`);
        if (result.deactivated && result.deactivated > 0) parts.push(`${result.deactivated} deactivated`);
        const errs = result.errors;
        let msg = `${providerData[provider]?.label || provider} sync: ${parts.join(", ")}.`;
        if (errs && errs.length > 0) {
          msg += ` ${errs.length} error(s): ${errs.slice(0, 3).join("; ")}${errs.length > 3 ? "..." : ""}`;
        }
        setImportMsg({ ok: true, msg });
        if (result.count > 0 || result.updated > 0) {
          setTimeout(onClose, 2000);
        }
      } else {
        setImportMsg({ ok: false, msg: result.error || "Import failed." });
      }
    } catch {
      setImportMsg({ ok: false, msg: "Import failed." });
    } finally {
      setImporting(null);
    }
  };

  const handleSaved = async (providerKey: string) => {
    setImportMsg(null);
    try {
      const r = await personnelApi.getProviderConfig(providerKey);
      if (r.ok) {
        const configured = r.schema.fields.every((f: any) => {
          if (f.is_secret) return r.config[`has_${f.key}`] === true;
          return (r.config[f.key] as string || "").trim().length > 0;
        });
        setProviderData((prev) => ({
          ...prev,
          [providerKey]: { configured, label: r.schema.label, schema: r.schema, config: r.config },
        }));
      }
    } catch { /* ignore */ }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel import-dialog-panel" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h3>Import Team Members</h3>
          <button className="btn btn-ghost btn-sm" onClick={onClose} style={{ fontSize: "1.1rem", lineHeight: 1 }}>&#x2715;</button>
        </header>

        <div className="modal-body" style={{ display: "flex", flexDirection: "column" }}>
          {loading ? (
            <p className="muted" style={{ textAlign: "center", padding: "2rem" }}>Loading...</p>
          ) : (
            PROVIDERS.map((p) => {
              const data = providerData[p.key];
              const configured = data?.configured ?? false;
              const isExpanded = expanded[p.key] ?? false;
              return (
                <div key={p.key}>
                  <div
                    className="import-provider-row"
                    onClick={(e) => { if ((e.target as HTMLElement).tagName !== "BUTTON") setExpanded(prev => ({ ...prev, [p.key]: !prev[p.key] })); }}
                  >
                    <span className="import-provider-chevron">
                      {isExpanded ? "\u25BE" : "\u25B8"}
                    </span>
                    <span className="import-provider-name">{data?.label || p.label}</span>
                    <span className="import-provider-status">
                      <span className="import-provider-dot" style={{ background: configured ? "var(--success)" : "var(--border)" }} />
                      {configured && <span style={{ color: "var(--success)" }}>Configured</span>}
                    </span>
                    {configured && (
                      <button className="btn btn-primary btn-sm" onClick={(e) => { e.stopPropagation(); handleImport(p.key); }} disabled={importing === p.key} style={{ minWidth: 70, flexShrink: 0 }}>
                        {importing === p.key ? "..." : "Import"}
                      </button>
                    )}
                  </div>
                  {isExpanded && (
                    <div className="import-provider-config">
                      {data?.schema ? (
                        <ProviderConfigForm
                          provider={p.key}
                          compact
                          onSaved={() => handleSaved(p.key)}
                          initialSchema={data.schema}
                          initialConfig={data.config}
                        />
                      ) : (
                        <p className="muted" style={{ fontSize: "0.78rem", margin: 0 }}>Could not load config form.</p>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}

          {importMsg && (
            <div className={`banner ${importMsg.ok ? "success" : "error"}`} style={{ marginTop: "0.75rem", marginBottom: 0 }}>
              {importMsg.ok ? "\u2713 " : "\u2717 "}{importMsg.msg}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
