import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

type SidebarCtx = { open: boolean; toggle: () => void; close: () => void };
const SidebarContext = createContext<SidebarCtx>({ open: false, toggle: () => {}, close: () => {} });

export function SidebarProvider({ active, children }: { active?: boolean; children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    try {
      const saved = localStorage.getItem("sidebar_open");
      if (saved !== null) return saved === "true";
    } catch { /* localStorage unavailable */ }
    return active ?? false;
  });
  const toggle = useCallback(() => {
    setSidebarOpen((v) => {
      const next = !v;
      try { localStorage.setItem("sidebar_open", String(next)); } catch {}
      return next;
    });
  }, []);
  const close = useCallback(() => {
    setSidebarOpen(false);
    try { localStorage.setItem("sidebar_open", "false"); } catch {}
  }, []);

  return (
    <SidebarContext.Provider value={{ open: sidebarOpen, toggle, close }}>
      {children}
    </SidebarContext.Provider>
  );
}

export function SidebarToggle() {
  const { open, toggle } = useContext(SidebarContext);
  return (
    <button type="button" className="sidebar-toggle" onClick={toggle} aria-label="Toggle sidebar">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ transform: open ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}
      >
        <polyline points="15 18 9 12 15 6" />
      </svg>
    </button>
  );
}

export function SidebarClose({ className }: { className?: string }) {
  const { open, toggle } = useContext(SidebarContext);
  return (
    <button type="button" className={className ?? "sidebar-close"} onClick={toggle} title="Close sidebar">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ transform: open ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}
      >
        <polyline points="15 18 9 12 15 6" />
      </svg>
    </button>
  );
}

export default function SidebarShell({
  frameworkSwitcher,
  frameworkLabel,
  sidebarClassName,
  children,
}: {
  frameworkSwitcher?: ReactNode;
  frameworkLabel: string;
  sidebarClassName?: string;
  children: ReactNode;
}) {
  const { open: sidebarOpen, close } = useContext(SidebarContext);

  useEffect(() => {
    if (!sidebarOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") close(); };
    globalThis.addEventListener("keydown", onKey);
    return () => globalThis.removeEventListener("keydown", onKey);
  }, [sidebarOpen]);

  return (
    <>
      <div className={`sidebar-backdrop${sidebarOpen ? " visible" : ""}`} onClick={() => close()} />
      <aside className={`sidebar${sidebarClassName ? ` ${sidebarClassName}` : ""}${sidebarOpen ? " open" : ""}`}>
        <div className="sidebar-brand">
          <a href="/" className="brand-wordmark" aria-label="Khestra">
            <span className="brand-name">Khestra</span>
          </a>
          <SidebarClose />
        </div>
        {frameworkSwitcher ? <div className="sidebar-label">{frameworkSwitcher}</div> : <p className="sidebar-label">{frameworkLabel}</p>}
        {children}
      </aside>
    </>
  );
}
