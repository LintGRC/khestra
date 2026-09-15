import { useState } from "react";
import { apiUrl } from "@shared/apiPrefix";

export default function LoginPage({
  onLogin,
  onRegister,
  onForgotPassword,
}: {
  onLogin: (token: string, user: { id: string; name: string; email: string; role: string }) => void;
  onRegister: () => void;
  onForgotPassword: () => void;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.trim() || !password) {
      setError("Email and password required");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/auth/login"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      onLogin(data.token, data.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-gate">
      <div className="auth-gate-card panel" style={{ maxWidth: 400, margin: "0 auto" }}>
        <h1 style={{ textAlign: "center", marginBottom: 8 }}>Sign in</h1>
        <p className="muted" style={{ textAlign: "center", marginBottom: 20 }}>
          Enter your credentials to access the platform
        </p>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoFocus
            required
            disabled={loading}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
          {error && <p className="banner error" style={{ margin: 0 }}>{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p style={{ textAlign: "center", marginTop: 14, fontSize: "14px" }}>
          <button
            type="button"
            onClick={onRegister}
            style={{ cursor: "pointer", border: "none", background: "none", color: "var(--primary)", textDecoration: "underline" }}
          >
            Create account
          </button>
          <span style={{ margin: "0 8px", color: "var(--muted)" }}>|</span>
          <button
            type="button"
            onClick={onForgotPassword}
            style={{ cursor: "pointer", border: "none", background: "none", color: "var(--primary)", textDecoration: "underline" }}
          >
            Forgot password?
          </button>
        </p>
      </div>
    </div>
  );
}
