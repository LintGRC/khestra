import { Link } from "react-router-dom";
import { useState } from "react";
import { api } from "../api";
import { useLayout } from "../Layout";

const DISMISS_KEY = "cmmc_onboarding_dismissed";

export default function GettingStartedBanner() {
  const { dashboard, canEditOrg } = useLayout();
  const [dismissed, setDismissed] = useState(() => localStorage.getItem(DISMISS_KEY) === "1");
  const [loadingDemo, setLoadingDemo] = useState(false);

  if (dismissed) return null;
  if (dashboard?.controls_assessed && dashboard.controls_assessed > 3) return null;

  const loadDemo = async () => {
    setLoadingDemo(true);
    try {
      await api.loadDemo("apex");
      window.location.href = "/controls";
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="banner welcome getting-started-banner">
      <strong>Getting started.</strong>{" "}
      Configure your organization profile, assess controls, then export SSP and POA&M — all stored locally.
      <div className="btn-row" style={{ marginTop: "0.5rem" }}>
        <Link className="btn btn-primary" to="/organization">Organization profile</Link>
        {canEditOrg && (
          <button type="button" className="btn btn-secondary" disabled={loadingDemo} onClick={loadDemo}>
            {loadingDemo ? "Loading…" : "Load sample data"}
          </button>
        )}
        <button
          type="button"
          className="btn-link"
          onClick={() => {
            localStorage.setItem(DISMISS_KEY, "1");
            setDismissed(true);
          }}
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
