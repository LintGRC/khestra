import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import type { AiGovFrameworkKey } from "./aiGovFrameworks";

export const ALL_FRAMEWORKS: AiGovFrameworkKey[] = ["eu_ai_act", "nist_ai_rmf", "iso_42001", "owasp_agentic", "owasp_llm"];

const STORAGE_KEY = "aigov_active_frameworks";

function loadStored(): AiGovFrameworkKey[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed.filter((k: string) => ALL_FRAMEWORKS.includes(k as AiGovFrameworkKey)) as AiGovFrameworkKey[];
      }
    }
  } catch {}
  return [...ALL_FRAMEWORKS];
}

type AiGovFrameworkContextType = {
  activeFrameworks: AiGovFrameworkKey[];
  setActiveFrameworks: (keys: AiGovFrameworkKey[]) => void;
  toggleFramework: (key: AiGovFrameworkKey) => void;
};

const AiGovFrameworkContext = createContext<AiGovFrameworkContextType>({
  activeFrameworks: [...ALL_FRAMEWORKS],
  setActiveFrameworks: () => {},
  toggleFramework: () => {},
});

export function AiGovFrameworkProvider({ children }: { children: ReactNode }) {
  const [activeFrameworks, setActiveFrameworksState] = useState<AiGovFrameworkKey[]>(loadStored);

  const setActiveFrameworks = useCallback((keys: AiGovFrameworkKey[]) => {
    setActiveFrameworksState(keys);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
  }, []);

  const toggleFramework = useCallback((key: AiGovFrameworkKey) => {
    setActiveFrameworksState(prev => {
      const next = prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key];
      if (next.length === 0) return prev; // never uncheck all
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  return (
    <AiGovFrameworkContext.Provider value={{ activeFrameworks, setActiveFrameworks, toggleFramework }}>
      {children}
    </AiGovFrameworkContext.Provider>
  );
}

export function useActiveFrameworks() {
  return useContext(AiGovFrameworkContext);
}
