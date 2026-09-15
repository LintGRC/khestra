import { useCallback, useEffect, useRef, useState } from "react";
import { useEditor, EditorContent, type Editor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import { Variable } from "./VariableExtension";
import "./PolicyEditor.css";

export type VariableMap = Record<string, string>;

export type PolicyEditorHandle = {
  getJSON: () => Record<string, unknown>;
  setJSON: (json: Record<string, unknown>) => void;
  reset: () => void;
};

function Toolbar({ editor, variables, policyId }: { editor: Editor; variables: VariableMap; policyId?: string }) {
  const varKeys = Object.keys(variables);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  const addVariable = useCallback(
    (name: string) => {
      editor.chain().focus().insertVariable(name).run();
    },
    [editor],
  );

  const handleAiGenerate = useCallback(async () => {
    if (!policyId || !aiPrompt.trim()) return;
    setAiLoading(true);
    try {
      const res = await fetch(`/api/policies/${policyId}/generate-ai`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ template: aiPrompt }),
      });
      if (!res.ok) throw new Error((await res.text()) || "Generation failed");
      const data = await res.json();
      if (data.tiptap_json) {
        editor.commands.setContent(data.tiptap_json);
      }
      setAiPrompt("");
    } catch (e) {
      console.error(e);
      alert(`AI generation failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setAiLoading(false);
    }
  }, [policyId, aiPrompt, editor]);

  return (
    <div className="policy-editor-toolbar">
      <div className="toolbar-row">
        <button type="button" className="toolbar-btn" onClick={() => editor.chain().focus().toggleBold().run()} data-active={editor.isActive("bold") ? "" : undefined} title="Bold">
          <strong>B</strong>
        </button>
        <button type="button" className="toolbar-btn" onClick={() => editor.chain().focus().toggleItalic().run()} data-active={editor.isActive("italic") ? "" : undefined} title="Italic">
          <em>I</em>
        </button>
        <span className="toolbar-sep" />
        <button type="button" className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} data-active={editor.isActive("heading", { level: 2 }) ? "" : undefined} title="Heading 2">
          H2
        </button>
        <button type="button" className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()} data-active={editor.isActive("heading", { level: 3 }) ? "" : undefined} title="Heading 3">
          H3
        </button>
        <span className="toolbar-sep" />
        <button type="button" className="toolbar-btn" onClick={() => editor.chain().focus().toggleBulletList().run()} data-active={editor.isActive("bulletList") ? "" : undefined} title="Bullet list">
          • list
        </button>
        <button type="button" className="toolbar-btn" onClick={() => editor.chain().focus().toggleOrderedList().run()} data-active={editor.isActive("orderedList") ? "" : undefined} title="Numbered list">
          1. list
        </button>
        <span className="toolbar-sep" />
        <select
          className="toolbar-select"
          value=""
          onChange={(e) => {
            if (e.target.value) addVariable(e.target.value);
            e.target.value = "";
          }}
          title="Insert merge variable"
        >
          <option value="">+ Variable</option>
          {varKeys.map((k) => (
            <option key={k} value={k}>
              {k}
            </option>
          ))}
        </select>
      </div>
      <div className="toolbar-row toolbar-row-ai" title="Describe the policy section you want written (e.g. &quot;Write the Scope section covering all systems and employees&quot;)">
        <textarea
          className="toolbar-ai-input"
          value={aiPrompt}
          onChange={(e) => {
            setAiPrompt(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = e.target.scrollHeight + "px";
          }}
          placeholder="Describe what to generate…"
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAiGenerate(); } }}
          disabled={aiLoading}
          rows={1}
        />
        <button type="button" className="toolbar-btn toolbar-btn-ai" onClick={handleAiGenerate} disabled={aiLoading || !aiPrompt.trim()} title="Generate with AI">
          {aiLoading ? "..." : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

export type PolicyEditorProps = {
  initialContent?: Record<string, unknown>;
  variables?: VariableMap;
  placeholder?: string;
  editable?: boolean;
  policyId?: string;
  onChange?: (json: Record<string, unknown>) => void;
  ref?: React.Ref<PolicyEditorHandle>;
};

export default function PolicyEditor({
  initialContent,
  variables = {},
  placeholder = "Start writing…",
  editable = true,
  policyId,
  onChange,
  ref,
}: PolicyEditorProps) {
  const editorRef = useRef<Editor | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        codeBlock: false,
        blockquote: false,
        horizontalRule: false,
      }),
      Placeholder.configure({ placeholder }),
      Variable,
    ],
    content: initialContent ?? {
      type: "doc",
      content: [{ type: "paragraph" }],
    },
    editable,
    onUpdate: ({ editor: ed }) => {
      editorRef.current = ed;
      onChange?.(ed.getJSON() as Record<string, unknown>);
    },
  });

  useEffect(() => {
    editor?.setEditable(editable);
  }, [editor, editable]);

  if (ref && "current" in ref) {
    (ref as React.MutableRefObject<PolicyEditorHandle | null>).current = {
      getJSON: () => {
        return (editor?.getJSON() ?? { type: "doc", content: [] }) as Record<string, unknown>;
      },
      setJSON: (json: Record<string, unknown>) => {
        editor?.commands.setContent(json);
      },
      reset: () => {
        editor?.commands.setContent({ type: "doc", content: [{ type: "paragraph" }] });
      },
    };
  }

  if (!editor) return null;

  return (
    <div className="policy-editor">
      {editable && <Toolbar editor={editor} variables={variables} policyId={policyId} />}
      <EditorContent editor={editor} className="policy-editor-content" />
    </div>
  );
}
