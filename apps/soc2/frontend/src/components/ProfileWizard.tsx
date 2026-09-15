import { useState } from "react";
import type { Organization, OrgProfile, EnvScope } from "../api";

type Props = {
  org: Organization;
  profile: OrgProfile;
  envScope: EnvScope;
  disabled?: boolean;
  onProfileChange: (patch: Partial<OrgProfile>) => void;
  onEnvChange: (patch: Partial<EnvScope>) => void;
  onComplete: () => void;
};

export default function ProfileWizard({
  org,
  profile,
  envScope,
  disabled,
  onProfileChange,
  onEnvChange,
  onComplete,
}: Props) {
  const [step, setStep] = useState(0);
  const steps = org.wizard_steps || [];
  const current = steps[step];
  if (!current) return null;

  const total = steps.length;
  const progress = ((step + 1) / total) * 100;
  const isEnv = current.key === "environment";
  const isLast = step === total - 1;

  const next = () => {
    if (isLast) {
      onComplete();
    } else {
      setStep(step + 1);
    }
  };

  const prev = () => {
    if (step > 0) setStep(step - 1);
  };

  const yesNoOptions = [
    { value: "", label: "Not answered" },
    { value: "yes", label: "Yes" },
    { value: "no", label: "No" },
  ];

  const cloudOptions = [
    { value: "", label: "Not answered" },
    { value: "on_prem_only", label: "On-premises only" },
    { value: "aws", label: "Amazon Web Services" },
    { value: "azure", label: "Microsoft Azure" },
    { value: "gcp", label: "Google Cloud Platform" },
    { value: "other", label: "Other" },
  ];

  const envFields = [
    { key: "uses_cloud", label: "Do you use cloud services?", type: "yes_no" },
    { key: "cloud_provider", label: "Primary cloud provider", type: "cloud" },
    { key: "uses_saas", label: "Do you use third-party SaaS?", type: "yes_no" },
    { key: "remote_workforce", label: "Do you have a remote workforce?", type: "yes_no" },
    { key: "uses_wireless", label: "Do you use wireless networks?", type: "yes_no" },
    { key: "processes_pii", label: "Do you process PII/personal data?", type: "yes_no" },
  ];

  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header">
        <h3 style={{ margin: 0 }}>
          Step {step + 1} of {total}: {current.label}
        </h3>
      </div>
      <div className="panel-body">
        <div className="progress-bar" style={{ marginBottom: 16 }}>
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>

        {isEnv ? (
          <div className="form-grid">
            {envFields.map((f) => (
              <div className="form-row" key={f.key}>
                <label>{f.label}</label>
                <select
                  value={envScope[f.key] || ""}
                  onChange={(e) => onEnvChange({ [f.key]: e.target.value })}
                  disabled={disabled}
                >
                  {(f.type === "cloud" ? cloudOptions : yesNoOptions).map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        ) : (
          <div className="form-grid">
            {current.fields.map((field) => (
              <div className="form-row" key={field}>
                <label>{org.field_labels[field] || field}</label>
                {field.includes("description") || field.includes("inventory") || field === "team_roster" ? (
                  <textarea
                    value={profile[field] || ""}
                    onChange={(e) => onProfileChange({ [field]: e.target.value })}
                    disabled={disabled}
                    placeholder={org.field_placeholders[field] || ""}
                    rows={3}
                  />
                ) : (
                  <input
                    type="text"
                    value={profile[field] || ""}
                    onChange={(e) => onProfileChange({ [field]: e.target.value })}
                    disabled={disabled}
                    placeholder={org.field_placeholders[field] || ""}
                  />
                )}
              </div>
            ))}
          </div>
        )}

        <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "flex-end" }}>
          {step > 0 && (
            <button type="button" className="btn btn-secondary" onClick={prev} disabled={disabled}>
              Back
            </button>
          )}
          <button type="button" className="btn btn-primary" onClick={next} disabled={disabled}>
            {isLast ? "Finish setup" : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
}
