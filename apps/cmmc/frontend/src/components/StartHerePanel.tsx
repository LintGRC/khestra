const STEPS = [
  ["Explore (optional)", "Workspace & settings → Sample data — pick Apex or Bridgeport from the dropdown."],
  ["Organization", "Company name, CUI scope, environment flags — or Guided setup."],
  ["Controls", "Set status and write implementation narratives; attach evidence."],
  ["Fix big gaps first", "Use priority controls — 5-point items hurt SPRS most."],
  ["Export", "Download SSP and POA&M when export readiness looks good."],
  ["Readiness", "SPRS entry text and audit package before a C3PAO discussion."],
] as const;

export default function StartHerePanel() {
  return (
    <details className="start-here-panel">
      <summary className="sidebar-section-label start-here-summary">Start here</summary>
      <ol className="start-here-steps">
        {STEPS.map(([title, detail]) => (
          <li key={title}>
            <strong>{title}</strong> — {detail}
          </li>
        ))}
      </ol>
      <p className="muted sidebar-hint">Data stays on this computer. Exports are drafts.</p>
    </details>
  );
}
