import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { policyApi } from "../api";
import { apiUrl } from "@shared/apiPrefix";
import type { TemplateItem } from "../types";
import { KNOWN_FRAMEWORKS } from "../types";
import PolicyEditor, { type PolicyEditorHandle, type VariableMap } from "../components/PolicyEditor";

function deriveBasePath(frameworkFilter?: string) {
  if (!frameworkFilter) return "/policies";
  return `/${frameworkFilter}/policies`;
}

export default function PolicyCreate({ frameworkFilter }: { frameworkFilter?: string }) {
  const navigate = useNavigate();
  const basePath = deriveBasePath(frameworkFilter);
  const editorRef = useRef<PolicyEditorHandle | null>(null);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [policyId, setPolicyId] = useState<string | null>(null);
  const [variables, setVariables] = useState<VariableMap>({});
  const [step, setStep] = useState<"template" | "editor" | "saving">("template");
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [frameworkTags, setFrameworkTags] = useState<string[]>(
    frameworkFilter ? [frameworkFilter] : []
  );

  const visibleTemplates = useMemo(() => {
    if (!frameworkFilter) return templates;
    return templates.filter((t) => t.framework_tags?.some(
      (tag) => tag.toLowerCase() === frameworkFilter || tag.toLowerCase().includes(frameworkFilter)
    ));
  }, [templates, frameworkFilter]);

  useEffect(() => {
    Promise.all([
      policyApi.templates().catch(() => ({ templates: [] })),
      fetch(apiUrl("/api/settings/policy-variables"))
        .then((r) => (r.ok ? r.json() : {}))
        .catch(() => ({})),
    ])
      .then(([t, v]) => {
        let tList = t.templates || [];
        if (frameworkFilter) {
          try {
            tList = tList.filter((t) => t.framework_tags?.some(
              (tag) => tag.toLowerCase() === frameworkFilter || tag.toLowerCase().includes(frameworkFilter)
            ));
          } catch {
            console.warn("Failed to filter templates by framework, showing all");
          }
        }
        setTemplates(tList);
        setVariables(v);
      })
      .catch(() => setError("Failed to load templates"));
  }, [frameworkFilter]);

  const handleCreate = useCallback(async () => {
    if (!title.trim()) return;
    setError(null);
    try {
      const tmpl = selectedTemplate ? templates.find((t) => t.key === selectedTemplate) : null;
      const mc = tmpl?.mapped_controls || [];

      const created = await policyApi.create({
        name: title.trim(),
        version: "1.0",
        description: description.trim(),
        mapped_controls: mc,
        framework_tags: frameworkTags,
      });
      const newId = ((created as any).policy || created).id;
      setPolicyId(newId);
      setStep("editor");

      if (selectedTemplate && tmpl) {
        const gen = await policyApi.generate(newId, selectedTemplate);
        const tiptapJson = (gen as any).tiptap_json;
        if (tiptapJson && editorRef.current) {
          editorRef.current.setJSON(tiptapJson);
        }
      }
    } catch (e) {
      console.error(e);
      setError("Failed to create policy");
    }
  }, [selectedTemplate, templates, title, description]);

  const handleSave = useCallback(async () => {
    if (!policyId || !editorRef.current) return;
    setStep("saving");
    setError(null);
    try {
      const json = editorRef.current.getJSON();

      // Save the TipTap JSON as the policy content
      await policyApi.update(policyId, {
        name: title,
        description,
        content: JSON.stringify(json),
      });
      navigate(`${basePath}/${policyId}`);
    } catch (e) {
      console.error(e);
      setError("Failed to save policy");
      setStep("editor");
    }
  }, [policyId, title, description, navigate]);

  const handleCancel = useCallback(async () => {
    if (policyId) {
      try { await policyApi.delete(policyId); } catch { /* best effort */ }
    }
    navigate(basePath);
  }, [policyId, navigate, basePath]);

  if (step === "template") {
    return (
      <div className="page-stack">
        <div className="page-header">
          <h2>Create Policy</h2>
          <p className="muted">Select a template to start from, or create a blank policy.</p>
        </div>

        {error && <div className="banner error">{error}</div>}

        <div className="panel">
          <div className="panel-body">
            <div style={{ display: "grid", gap: "0.75rem" }}>
              <label>
                Policy Title
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Access Control Policy"
                  style={{ width: "100%" }}
                />
              </label>
              <label>
                Description
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of this policy"
                  rows={2}
                  style={{ width: "100%" }}
                />
              </label>
              <label>
                Template <span className="muted">(optional — select to pre-fill content)</span>
                <select value={selectedTemplate} onChange={(e) => setSelectedTemplate(e.target.value)} style={{ width: "100%" }}>
                  <option value="">— Start from scratch —</option>
                  {visibleTemplates.map((t) => (
                    <option key={t.key} value={t.key}>
                      {t.name} ({t.short_name})
                    </option>
                  ))}
                </select>
              </label>
              <div>
                <div style={{ marginBottom: "0.25rem" }}>
                  Framework tags <span className="muted">(which frameworks may use this policy)</span>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {KNOWN_FRAMEWORKS.map((fw) => {
                    const checked = frameworkTags.includes(fw.id);
                    return (
                      <label
                        key={fw.id}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.35rem",
                          padding: "0.3rem 0.6rem",
                          borderRadius: "6px",
                          border: `1px solid ${checked ? "var(--primary)" : "var(--border)"}`,
                          background: checked ? "var(--primary-soft, rgba(37,99,235,0.08))" : "transparent",
                          cursor: "pointer",
                          fontSize: "0.85rem",
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() =>
                            setFrameworkTags((prev) =>
                              checked ? prev.filter((t) => t !== fw.id) : [...prev, fw.id]
                            )
                          }
                          style={{ margin: 0 }}
                        />
                        {fw.shortLabel}
                        {!fw.live && <span className="muted" style={{ fontSize: "0.75rem" }}>(coming soon)</span>}
                      </label>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
          <div className="panel-footer" style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end", padding: "1rem" }}>
              <button className="btn btn-ghost" onClick={handleCancel}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={!title.trim()}>
                Create & Edit
              </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>Editing: {title}</h2>
        <p className="muted">{description}</p>
      </div>

      {error && <div className="banner error">{error}</div>}

      <div className="panel">
        <div className="panel-body" style={{ padding: 0 }}>
          <PolicyEditor
            ref={editorRef}
            variables={variables}
            policyId={policyId || undefined}
            placeholder="Write your policy content here…"
          />
        </div>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
          <button className="btn btn-ghost" onClick={handleCancel}>
            Cancel
          </button>
        <button className="btn btn-primary" onClick={handleSave} disabled={step === "saving"}>
          {step === "saving" ? "Saving..." : "Save Policy"}
        </button>
      </div>
    </div>
  );
}
