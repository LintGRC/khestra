import { useEffect, useLayoutEffect, useRef } from "react";
import { useLocation, useNavigationType } from "react-router-dom";

const s = new Map<string, number>();

export function useScrollRestoration() {
  const { key } = useLocation();
  const action = useNavigationType();
  const keyRef = useRef(key);
  keyRef.current = key;

  useEffect(() => {
    const onScroll = () => s.set(keyRef.current, window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration = "manual";
    }
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useLayoutEffect(() => {
    if (action === "POP") {
      const saved = s.get(key);
      if (saved === undefined) return;
      const attempt = () => {
        if (document.body.scrollHeight >= saved) {
          window.scrollTo(0, saved);
          return;
        }
        requestAnimationFrame(attempt);
      };
      attempt();
    } else {
      window.scrollTo(0, 0);
    }
  }, [key, action]);
}
