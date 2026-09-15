import { useState } from "react";
import { api } from "../api";

type Props = {
  onCreated: () => Promise<void>;
};

export default function OrganizationOnboarding({ onCreated }: Props) {
  const [name, setName] = useState("");
  const [loadDemo, setLoadDemo] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Enter an organization name.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api.createOrganization(trimmed, loadDemo);
      await onCreated();
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-gate">
      <form className="auth-gate-card panel org-onboarding" onSubmit={onSubmit}>
        <h1>Create your organization</h1>
        <p className="muted">
          This sandbox gives you a private workspace. Connectors run in <strong>demo mode</strong>{" "}
          (bundled fixtures) — no live cloud credentials required.
        </p>
        <label className="org-onboarding-field" htmlFor="org-name">
          Organization name
        </label>
        <input
          id="org-name"
          className="drawer-select"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Apex Defense Demo"
          autoFocus
        />
        <label className="collector-schedule-toggle org-onboarding-demo">
          <input
            type="checkbox"
            checked={loadDemo}
            onChange={(e) => setLoadDemo(e.target.checked)}
          />
          Start with sample assessment data (recommended for demos)
        </label>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? "Creating…" : "Create organization"}
        </button>
        {error && <p className="verify-fail">{error}</p>}
      </form>
    </div>
  );
}
