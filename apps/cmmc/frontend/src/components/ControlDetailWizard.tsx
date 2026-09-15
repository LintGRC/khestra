import { FormEvent, ReactNode } from "react";

export type WizardStepDef = {
  id: string;
  title: string;
  caption: ReactNode;
};

type Props = {
  steps: WizardStepDef[];
  step: number;
  onStepChange: (n: number) => void;
  editorMode: "edit" | "ssp";
  onEditorModeChange: (mode: "edit" | "ssp") => void;
  saving: boolean;
  saved: boolean;
  canEdit: boolean;
  onSave: () => void;
  children: ReactNode;
};

export default function ControlDetailWizard({
  steps,
  step,
  onStepChange,
  editorMode,
  onEditorModeChange,
  saving,
  saved,
  canEdit,
  onSave,
  children,
}: Props) {
  const current = steps[step] ?? steps[0];
  const isLast = step >= steps.length - 1;
  const isEdit = editorMode === "edit";

  const onWizardSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSave();
    if (!isLast) onStepChange(step + 1);
  };

  return (
    <div className="panel control-wizard-shell">
      <div className="panel-header control-wizard-header">
        <div>
          <strong>
            Step {step + 1} of {steps.length}: {current.title}
          </strong>
          {saved && <span className="save-toast" style={{ marginLeft: 8 }}>Saved</span>}
        </div>
        <div className="control-editor-mode-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={isEdit}
            className={isEdit ? "active" : ""}
            onClick={() => onEditorModeChange("edit")}
          >
            Edit
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={!isEdit}
            className={!isEdit ? "active" : ""}
            onClick={() => onEditorModeChange("ssp")}
          >
            SSP preview
          </button>
        </div>
      </div>
      {isEdit ? (
        <div className="panel-body">
          <div className="step-caption">{typeof current.caption === "string" ? <span className="muted">{current.caption}</span> : current.caption}</div>
          <div className="wizard-step-tabs" role="tablist">
            {steps.map((s, i) => (
              <button
                key={s.id}
                type="button"
                role="tab"
                aria-selected={i === step}
                className={`wizard-step-tab${i === step ? " active" : ""}${i < step ? " done" : ""}`}
                onClick={() => onStepChange(i)}
              >
                {i + 1}. {s.title}
              </button>
            ))}
          </div>
          <form onSubmit={onWizardSubmit}>
            <div className="wizard-step-content">{children}</div>
            <div className="btn-row wizard-nav">
              <button
                type="button"
                className="btn btn-secondary"
                disabled={step === 0}
                onClick={() => onStepChange(step - 1)}
              >
                Back
              </button>
              {canEdit && (
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? "Saving…" : isLast ? "Save control" : "Save & continue"}
                </button>
              )}
              {!isLast && (
                <button type="button" className="btn-link" onClick={() => onStepChange(step + 1)}>
                  Skip for now
                </button>
              )}
            </div>
          </form>
        </div>
      ) : (
        <div className="panel-body">{children}</div>
      )}
    </div>
  );
}
