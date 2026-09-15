import { useState } from "react";

const DISMISS_KEY = "cmmc_demo_banner_dismissed";

type Props = {
  label: string;
  demoId?: string;
  onClear: () => void;
  clearing?: boolean;
};

export default function DemoBanner({ label, demoId, onClear, clearing }: Props) {
  const dismissKey = demoId ? `${DISMISS_KEY}_${demoId}` : DISMISS_KEY;
  const [dismissed, setDismissed] = useState(() => localStorage.getItem(dismissKey) === "1");

  if (dismissed) return null;

  return (
    <div className="banner demo-banner">
      <div>
        <strong>Sample workspace</strong>
        <p className="muted">
          Viewing <strong>{label}</strong> demo data. Scores and exports are for training — not your organization.
          Loading a demo replaces the current workspace on this device.
        </p>
      </div>
      <div className="demo-banner-actions">
        <button type="button" className="btn btn-primary btn-sm" disabled={clearing} onClick={onClear}>
          {clearing ? "Exiting…" : "Exit demo"}
        </button>
        <button
          type="button"
          className="btn-link"
          onClick={() => {
            localStorage.setItem(dismissKey, "1");
            setDismissed(true);
          }}
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
