import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { MsalProvider } from "@azure/msal-react";
import type { PublicClientApplication } from "@azure/msal-browser";
import { AuthContext } from "@shared/authContext";
import { setAccessTokenGetter } from "@shared/accessToken";
import { apiUrl } from "../api";
import { acquireApiToken, createMsalInstance } from "./msal";
import type { AuthConfig } from "./types";
import LoginPage from "@shared/auth/pages/LoginPage";
import RegisterPage from "@shared/auth/pages/RegisterPage";
import ForgotPasswordPage from "@shared/auth/pages/ForgotPasswordPage";
import ResetPasswordPage from "@shared/auth/pages/ResetPasswordPage";

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
  const [role, setRole] = useState("");
  const [showRegister, setShowRegister] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetToken, setResetToken] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("khestra_auth_token");
    if (stored) {
      setAccessTokenGetter(async () => stored);
      fetch(apiUrl("/api/auth/me"), {
        headers: { Authorization: `Bearer ${stored}` },
      })
        .then((r) => r.json().then((data) => {
          if (r.ok) {
            setAuthenticated(true);
            setDisplayName(data.name || "");
            setEmail(data.email || "");
            setRole(data.role || "");
          } else {
            localStorage.removeItem("khestra_auth_token");
            setAccessTokenGetter(null);
          }
        }))
        .catch(() => {
          localStorage.removeItem("khestra_auth_token");
          setAccessTokenGetter(null);
        })
        .finally(() => setReady(true));
    } else {
      setReady(true);
    }
  }, []);

  const login = useCallback(async (email?: string, password?: string) => {
    const res = await fetch(apiUrl("/api/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");
    localStorage.setItem("khestra_auth_token", data.token);
    setAccessTokenGetter(async () => data.token);
    setAuthenticated(true);
    setDisplayName(data.user.name || "");
    setEmail(data.user.email || "");
    setRole(data.user.role || "");
  }, []);

  const logout = useCallback(async () => {
    localStorage.removeItem("khestra_auth_token");
    setAccessTokenGetter(null);
    setAuthenticated(false);
    setDisplayName("");
    setEmail("");
    setRole("");
  }, []);

  const value = useMemo(
    () => ({
      ready,
      enabled: true,
      authenticated,
      displayName,
      email,
      role,
      login,
      logout,
    }),
    [authenticated, displayName, email, login, logout, ready, role],
  );

  if (!ready) {
    return (
      <div className="auth-gate">
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (!authenticated) {
    const PUBLIC_PATHS = ["/questionnaire/"];
    if (PUBLIC_PATHS.some((p) => window.location.pathname.startsWith(p))) {
      return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
    }
    const onLogin = (token: string, user: { id: string; name: string; email: string; role: string }) => {
      localStorage.setItem("khestra_auth_token", token);
      setAccessTokenGetter(async () => token);
      setAuthenticated(true);
      setDisplayName(user.name || "");
      setEmail(user.email || "");
      setRole(user.role || "");
    };
    const goBack = () => {
      setShowRegister(false);
      setShowForgotPassword(false);
      setResetToken("");
    };
    if (resetToken) {
      return (
        <AuthContext.Provider value={value}>
          <ResetPasswordPage token={resetToken} onDone={goBack} />
        </AuthContext.Provider>
      );
    }
    if (showForgotPassword) {
      return (
        <AuthContext.Provider value={value}>
          <ForgotPasswordPage onBack={goBack} onResetToken={(t) => setResetToken(t)} />
        </AuthContext.Provider>
      );
    }
    return (
      <AuthContext.Provider value={value}>
        {showRegister ? (
          <RegisterPage onLogin={onLogin} onBack={goBack} />
        ) : (
          <>
            <LoginPage
              onLogin={onLogin}
              onRegister={() => setShowRegister(true)}
              onForgotPassword={() => setShowForgotPassword(true)}
            />
          </>
        )}
      </AuthContext.Provider>
    );
  }

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<AuthConfig | null>(null);
  const [instance, setInstance] = useState<PublicClientApplication | null>(null);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    fetchAuthConfig()
      .then((cfg) => {
        setConfig(cfg);
        if (cfg.mode === "entra") {
          setInstance(createMsalInstance(cfg));
        }
      })
      .catch((err) => setLoadError(String(err)));
  }, []);

  if (loadError) {
    return (
      <div className="auth-gate">
        <p className="verify-fail">Auth configuration error: {loadError}</p>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="auth-gate">
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (config.mode === "local") {
    return <LocalAuthProvider>{children}</LocalAuthProvider>;
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
