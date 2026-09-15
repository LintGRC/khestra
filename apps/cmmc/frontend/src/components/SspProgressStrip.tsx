import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, SspProgress } from "../api";

type Props = {
  onShowMissing?: () => void;
  missingFilterActive?: boolean;
};

export default function SspProgressStrip({ onShowMissing, missingFilterActive }: Props) {
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "/cmmc";
  const navigate = useNavigate();
  const [progress, setProgress] = useState<SspProgress | null>(null);

  useEffect(() => {
    api.sspProgress().then(setProgress).catch(console.error);
  }, []);

  if (!progress || progress.scoped_count === 0) return null;

  const pct = progress.documented_pct;
  const tone = pct >= 70 ? "good" : pct >= 40 ? "warn" : "bad";

  return (
    <div className={`panel ssp-progress-strip ssp-progress-${tone}`}>
      <div className="panel-body ssp-progress-body">
        <div className="ssp-progress-main">
          <strong>SSP descriptions</strong>
          <span className="ssp-progress-count">
            {progress.documented_count} / {progress.scoped_count} controls
          </span>
          <span className="muted">{pct}% with SSP text</span>
        </div>
        <div className="ssp-progress-actions">
          {progress.empty_count > 0 && onShowMissing && (
            <button
              type="button"
              className={`btn btn-secondary btn-sm${missingFilterActive ? " active" : ""}`}
              onClick={onShowMissing}
            >
              {missingFilterActive ? "Show all controls" : `Show missing (${progress.empty_count})`}
            </button>
          )}
          <button type="button" className="btn-link" onClick={() => navigate(`${fwBase}/export`)}>
            Export readiness →
          </button>
        </div>
      </div>
      <div className="ssp-progress-track" aria-hidden>
        <div className="ssp-progress-fill" style={{ width: `${pct}%` }} />
      </div>
      {progress.families.length > 0 && (
        <details className="ssp-progress-families">
          <summary className="muted">By family</summary>
          <ul className="ssp-progress-family-list">
            {progress.families.map((f) => (
              <li key={f.family}>
                <span>{f.family}</span>
                <span className="muted">
                  {f.documented_count}/{f.scoped_count}
                </span>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
