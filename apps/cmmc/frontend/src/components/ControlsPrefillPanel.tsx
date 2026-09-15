import { useState } from "react";
import { api } from "../api";

type Scope = "missing_met" | "all_empty" | "all";

type Props = {
  canEdit: boolean;
  onApplied: () => void;
};

const SCOPE_LABELS: Record<Scope, string> = {
  missing_met: "MET / N/A / Inherited without narrative",
  all_empty: "All controls missing a narrative",
  all: "All controls (overwrites existing narratives)",
};

export default function ControlsPrefillPanel({ canEdit, onApplied }: Props) {
  const [scope, setScope] = useState<Scope>("missing_met");
  const [open, setOpen] = useState(false);
  const [applying, setApplying] = useState(false);
  const [useAi, setUseAi] = useState(false);
  const [force, setForce] = useState(false);
  const [msg, setMsg] = useState("");

  const onGenerate = async () => {
    setApplying(true);
    setMsg("");
    try {
      const r = await api.generateAllNarratives(scope, useAi, force);
      setMsg(`Generated narratives for ${r.generated} control(s) (${r.skipped} skipped). Review and edit before export.`);
      onApplied();
    } catch (err) {
      setMsg(String(err));
    } finally {
      setApplying(false);
    }
  };

  if (!canEdit) return null;

  return (
    <details className="controls-prefill-panel" open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary>
        <strong>Generate SSP narratives</strong>
        <span className="muted">Bulk generate from org profile and evidence</span>
      </summary>
      <div className="controls-prefill-body">
        <p className="muted">
          Generates narratives using org profile, evidence collectors, and optional AI polish.
          Edit each control before treating as final.
        </p>
        <label>
          Apply to
          <select value={scope} onChange={(e) => setScope(e.target.value as Scope)}>
            {(Object.keys(SCOPE_LABELS) as Scope[]).map((s) => (
              <option key={s} value={s}>{SCOPE_LABELS[s]}</option>
            ))}
          </select>
        </label>
        <label style={{ marginLeft: 12 }}>
          <input type="checkbox" checked={useAi} onChange={(e) => setUseAi(e.target.checked)} />
          {" "}Use AI polish
        </label>
        <label style={{ marginLeft: 12 }}>
          <input type="checkbox" checked={force} onChange={(e) => setForce(e.target.checked)} />
          {" "}Force overwrite (regenerate even human-edited narratives)
        </label>
        <div className="btn-row">
          <button type="button" className="btn btn-secondary" disabled={applying} onClick={onGenerate}>
            {applying ? "Generating…" : "Generate narratives"}
          </button>
        </div>
        {msg && <p className="muted">{msg}</p>}
      </div>
    </details>
  );
}
