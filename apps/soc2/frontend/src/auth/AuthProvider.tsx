import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
  type FormEvent,
} from "react";
import { MsalProvider } from "@azure/msal-react";
import type { PublicClientApplication } from "@azure/msal-browser";
import { AuthContext } from "@shared/authContext";
import { setAccessTokenGetter } from "@shared/accessToken";
import { apiUrl } from "../api";
import { acquireApiToken, createMsalInstance } from "./msal";
import type { AuthConfig } from "./types";

export { useAuth } from "@shared/authContext";

async function fetchAuthConfig(): Promise<AuthConfig> {
  const res = await fetch(apiUrl("/api/auth/config"));
  if (!res.ok) {
    throw new Error("Failed to load auth config");
  }
  return res.json() as Promise<AuthConfig>;
}

function AuthEnabledProvider({
  config,
  instance,
  children,
}: {
  config: AuthConfig;
  instance: PublicClientApplication;
  children: ReactNode;
}) {
  const [ready, setReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");

  const syncAccount = useCallback(() => {
    const account = instance.getActiveAccount() ?? instance.getAllAccounts()[0];
    if (account) {
      if (!instance.getActiveAccount()) {
        instance.setActiveAccount(account);
      }
      setAuthenticated(true);
      setDisplayName(account.name || account.username || "");
      setEmail(account.username || "");
    } else {
      setAuthenticated(false);
      setDisplayName("");
      setEmail("");
    }
  }, [instance]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await instance.initialize();
      const response = await instance.handleRedirectPromise();
      if (cancelled) return;
      if (response?.account) {
        instance.setActiveAccount(response.account);
      }
      syncAccount();
      setReady(true);
    })().catch((err) => {
      console.error(err);
      if (!cancelled) setReady(true);
    });
    return () => {
      cancelled = true;
    };
  }, [instance, syncAccount]);

  useEffect(() => {
    setAccessTokenGetter(async () => {
      if (!authenticated) return null;
      return acquireApiToken(instance, config.scopes, config.login_hint);
    });
    return () => setAccessTokenGetter(null);
  }, [authenticated, config.login_hint, config.scopes, instance]);

  const login = useCallback(async () => {
    const result = await instance.loginPopup({
      scopes: config.scopes,
      loginHint: config.login_hint || undefined,
    });
    if (result.account) {
      instance.setActiveAccount(result.account);
    }
    syncAccount();
  }, [config.login_hint, config.scopes, instance, syncAccount]);

  const logout = useCallback(async () => {
    const account = instance.getActiveAccount() ?? instance.getAllAccounts()[0];
    await instance.logoutPopup({ account: account || undefined });
    syncAccount();
  }, [instance, syncAccount]);

  const value = useMemo(
    () => ({
      ready,
      enabled: true,
      authenticated,
      displayName,
      email,
      role: "",
      login,
      logout,
    }),
    [authenticated, displayName, email, login, logout, ready],
  );

  return (
    <MsalProvider instance={instance}>
      <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    </MsalProvider>
  );
}

function LocalAuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("soc2_token");
    if (saved) {
      try {
        const payload = JSON.parse(atob(saved.split(".")[1]));
        setAuthenticated(true);
        setDisplayName(payload.name || "");
        setEmail(payload.email || "");
      } catch {
        localStorage.removeItem("soc2_token");
      }
    }
    setReady(true);
    setAccessTokenGetter(async () => localStorage.getItem("soc2_token"));
    return () => setAccessTokenGetter(null);
  }, []);

  const login = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/auth/login"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      localStorage.setItem("soc2_token", data.token);
      setAuthenticated(true);
      setDisplayName(data.user?.name || "");
      setEmail(data.user?.email || "");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, [email, password]);

  const logout = useCallback(async () => {
    localStorage.removeItem("soc2_token");
    setAuthenticated(false);
    setDisplayName("");
    setEmail("");
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    login().catch(console.error);
  };

  const value = useMemo(
    () => ({ ready, enabled: true, authenticated, displayName, email, role: "", login, logout }),
    [ready, authenticated, displayName, email, login, logout],
  );

  if (!ready) {
    return <div className="auth-gate"><p className="muted">Loading…</p></div>;
  }

  if (!authenticated) {
    return (
      <div className="auth-gate">
        <div style={{ maxWidth: 360, margin: "2rem auto", padding: "2rem", border: "1px solid var(--border-color)", borderRadius: 8 }}>
          <h2 style={{ marginTop: 0 }}>Sign in</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Email
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
            </label>
            <label>
              Password
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </label>
            {error && <p style={{ color: "var(--danger)", fontSize: 12 }}>{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: "100%", marginTop: 8 }}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}


export default function AuthProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<AuthConfig | null>(null);
  const [instance, setInstance] = useState<PublicClientApplication | null>(null);

  useEffect(() => {
    fetchAuthConfig()
      .then((cfg) => {
        setConfig(cfg);
        if (cfg.enabled && cfg.mode !== "local") {
          setInstance(createMsalInstance(cfg));
        }
      })
      .catch((err) => console.error("Auth config load error:", err));
  }, []);


  if (!config) {
    return (
      <div className="auth-gate">
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (!config.enabled) {
    return (
      <AuthContext.Provider
        value={{
          ready: true,
          enabled: false,
          authenticated: true,
          displayName: "",
          email: "",
          role: "",
          login: async () => {},
          logout: async () => {},
        }}
      >
        {children}
      </AuthContext.Provider>
    );
  }

  if (config.mode === "local") {
    return <LocalAuthProvider>{children}</LocalAuthProvider>;
  }

  if (!instance) {
    return (
      <div className="auth-gate">
        <p className="muted">Starting sign-in…</p>
      </div>
    );
  }

  return (
    <AuthEnabledProvider config={config} instance={instance}>
      {children}
    </AuthEnabledProvider>
  );
}
