import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FRAMEWORK_ORDER, FRAMEWORKS } from "./frameworks";
import type { FrameworkId } from "./frameworks";
import { rememberFramework } from "@shared/apiPrefix";

function frameworkFromUrl(): FrameworkId | null {
  const match = location.pathname.match(/^\/(cmmc|soc2|aigov|iso27001)(?:\/|$)/);
  if (!match) return null;
  const raw = match[1];
  return raw === "aigov" ? "aigovernance" : (raw as FrameworkId);
}

export default function FrameworkSwitcher({ placeholder }: { placeholder?: string }) {
  const navigate = useNavigate();
  const detected = frameworkFromUrl();
  const framework = detected ?? "cmmc";
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.parentElement?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpen((v) => !v);
    }
  }, []);

  const meta = detected ? FRAMEWORKS[framework] : null;

  const ID_URL: Record<FrameworkId, string> = {
    cmmc: "cmmc",
    soc2: "soc2",
    aigovernance: "aigov",
    iso27001: "iso27001",
  };

  const switchTo = (id: FrameworkId) => {
    rememberFramework(id);
    navigate(`/${ID_URL[id]}/`);
    setOpen(false);
  };

  const switchToPlatform = () => {
    navigate("/");
    setOpen(false);
  };

  return (
    <div
      className="framework-switcher"
      ref={rootRef}
      role="button"
      tabIndex={0}
      aria-haspopup="listbox"
      aria-expanded={open}
      onClick={() => setOpen((v) => !v)}
      onKeyDown={handleKeyDown}
    >
      <span className="framework-switcher-trigger">
        {meta ? meta.shortLabel : (placeholder ?? "CMMC")}
      </span>
      <span className="framework-switcher-chevron" aria-hidden>▾</span>
      {open && (
        <ul className="framework-switcher-menu" role="listbox">
          <li>
            <button
              type="button"
              role="option"
              aria-selected={detected === null}
              className={`framework-switcher-option framework-switcher-option--platform${detected === null ? " active" : ""}`}
              onClick={(e) => {
                e.stopPropagation();
                switchToPlatform();
              }}
            >
              <span>{placeholder ?? "Platform"} Overview</span>
            </button>
          </li>
          <li className="framework-switcher-separator" role="separator" />
          {FRAMEWORK_ORDER.map((id) => {
            const item = FRAMEWORKS[id];
            const active = detected !== null && id === framework;
            return (
              <li key={id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={active}
                  className={`framework-switcher-option${active ? " active" : ""}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    switchTo(id);
                  }}
                >
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
