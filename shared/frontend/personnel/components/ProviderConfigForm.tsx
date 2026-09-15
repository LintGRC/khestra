import { useEffect, useState } from "react";
import { personnelApi } from "../api";

interface SchemaField {
  key: string;
  label: string;
  is_secret: boolean;
  placeholder?: string;
}

interface Schema {
  label: string;
  fields: SchemaField[];
}

interface Props {
  provider: string;
  onSaved: () => void;
  onBack?: () => void;
  compact?: boolean;
  initialSchema?: Schema | null;
  initialConfig?: Record<string, string | boolean>;
}

export default function ProviderConfigForm({ provider, onSaved, onBack, compact, initialSchema, initialConfig }: Props) {
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [secretVisibility, setSecretVisibility] = useState<Record<string, boolean>>({});
  const [hasSecrets, setHasSecrets] = useState<Record<string, boolean>>({});
  const [schema, setSchema] = useState<Schema | null>(initialSchema ?? null);
  const [fetchErr, setFetchErr] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (initialSchema && initialConfig) {
      setSchema(initialSchema);
      const initial: Record<string, string> = {};
      const secrets: Record<string, boolean> = {};
      for (const field of initialSchema.fields) {
        initial[field.key] = (initialConfig[field.key] as string) || "";
        if (field.is_secret) {
          secrets[field.key] = initialConfig[`has_${field.key}`] === true;
        }
      }
      setFieldValues(initial);
      setHasSecrets(secrets);
      return;
    }
    setTestResult(null);
    setFetchErr(false);
    personnelApi.getProviderConfig(provider).then((r) => {
      if (r.ok) {
        setSchema(r.schema);
        const initial: Record<string, string> = {};
        const secrets: Record<string, boolean> = {};
        for (const field of r.schema.fields) {
          initial[field.key] = (r.config[field.key] as string) || "";
          if (field.is_secret) {
            secrets[field.key] = r.config[`has_${field.key}`] === true as boolean;
          }
        }
        setFieldValues(initial);
        setHasSecrets(secrets);
      } else {
        setFetchErr(true);
      }
    }).catch(() => setFetchErr(true));
  }, [provider]);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const r = await personnelApi.testProviderConfig(provider);
      setTestResult(r.ok ? { ok: true, msg: "Connection successful" } : { ok: false, msg: r.error || "Connection failed" });
    } catch {
      setTestResult({ ok: false, msg: "Connection failed" });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    const allFilled = schema?.fields.every((f) => {
      if (f.is_secret && hasSecrets[f.key] && !fieldValues[f.key]) return true;
      return (fieldValues[f.key] || "").trim().length > 0;
    });
    if (!allFilled) {
      setTestResult({ ok: false, msg: "All fields are required." });
      return;
    }
    setTestResult(null);
    setSaving(true);
    try {
      await personnelApi.saveProviderConfig(provider, fieldValues);
      await onSaved();
    } catch {
      setTestResult({ ok: false, msg: "Save failed" });
    } finally {
      setSaving(false);
    }
  };

  if (fetchErr) {
    return <p className="muted" style={{ fontSize: "0.78rem", margin: 0 }}>Could not load config form.</p>;
  }

  if (compact) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {schema?.fields.map((field) => (
          <div key={field.key}>
            <label className="import-provider-label">{field.label}</label>
            {field.is_secret ? (
              <div style={{ display: "flex", gap: 4 }}>
                <input
                  type={secretVisibility[field.key] ? "text" : "password"}
                  value={fieldValues[field.key] || ""}
                  onChange={(e) => setFieldValues({ ...fieldValues, [field.key]: e.target.value })}
                  placeholder={hasSecrets[field.key] ? "Leave blank to keep current" : (field.placeholder || "Enter value")}
                  style={{ flex: 1 }}
                />
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setSecretVisibility({ ...secretVisibility, [field.key]: !secretVisibility[field.key] })}>Show</button>
              </div>
            ) : (
              <input value={fieldValues[field.key] || ""} onChange={(e) => setFieldValues({ ...fieldValues, [field.key]: e.target.value })} placeholder={field.placeholder} />
            )}
          </div>
        ))}

        {testResult && (
          <div className={`banner ${testResult.ok ? "success" : "error"}`} style={{ margin: 0 }}>
            {testResult.ok ? "\u2713 " : "\u2717 "}{testResult.msg}
          </div>
        )}

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button className="btn btn-ghost btn-sm" onClick={handleTest} disabled={testing}>
            {testing ? "Testing..." : "Test Connection"}
          </button>
          <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {onBack && <button type="button" className="btn btn-ghost btn-sm" onClick={onBack} style={{ fontSize: "0.85rem" }}>&larr; Back</button>}
          <h3 style={{ margin: 0, fontSize: "1rem" }}>Configure {schema?.label || provider}</h3>
        </div>
      </div>

      <div style={{ padding: "1.25rem 1.5rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {schema?.fields.map((field) => (
          <div key={field.key}>
            <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: 4 }}>{field.label}</label>
            {field.is_secret ? (
              <div style={{ display: "flex", gap: 4 }}>
                <input
                  type={secretVisibility[field.key] ? "text" : "password"}
                  value={fieldValues[field.key] || ""}
                  onChange={(e) => setFieldValues({ ...fieldValues, [field.key]: e.target.value })}
                  placeholder={hasSecrets[field.key] ? "Leave blank to keep current" : (field.placeholder || "Enter value")}
                  style={{ flex: 1 }}
                />
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setSecretVisibility({ ...secretVisibility, [field.key]: !secretVisibility[field.key] })} style={{ flexShrink: 0 }}>
                  {secretVisibility[field.key] ? "Hide" : "Show"}
                </button>
              </div>
            ) : (
              <input
                value={fieldValues[field.key] || ""}
                onChange={(e) => setFieldValues({ ...fieldValues, [field.key]: e.target.value })}
                placeholder={field.placeholder}
              />
            )}
          </div>
        ))}

        {testResult && (
          <div className={`banner ${testResult.ok ? "success" : "error"}`} style={{ margin: 0 }}>
            {testResult.ok ? "\u2713 " : "\u2717 "}{testResult.msg}
          </div>
        )}
      </div>

      <div style={{ padding: "1rem 1.5rem", borderTop: "1px solid var(--border)", display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
        {onBack && <button className="btn btn-ghost btn-sm" onClick={onBack}>Cancel</button>}
        <button className="btn btn-ghost btn-sm" onClick={handleTest} disabled={testing}>
          {testing ? "Testing..." : "Test Connection"}
        </button>
        <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
    </>
  );
}
