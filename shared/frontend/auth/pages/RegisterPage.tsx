import { useState } from "react";
import { apiUrl } from "@shared/apiPrefix";

export default function RegisterPage({
  onLogin,
  onBack,
}: {
  onLogin: (token: string, user: { id: string; name: string; email: string; role: string }) => void;
  onBack: () => void;
}) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.trim() || !password || !orgName.trim()) {
      setError("Email, password, and organization name are required");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/auth/register"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), name: name.trim() || email.trim(), password, org_name: orgName.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
      onLogin(data.token, data.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-gate">
      <div className="auth-gate-card panel" style={{ maxWidth: 400, margin: "0 auto" }}>
        <h1 style={{ textAlign: "center", marginBottom: 8 }}>Create Account</h1>
        <p className="muted" style={{ textAlign: "center", marginBottom: 20 }}>
          Set up your organization and admin account
        </p>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input
            type="text"
            placeholder="Organization name"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            autoFocus
            required
            disabled={loading}
          />
          <input
            type="text"
            placeholder="Your name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={loading}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
          <input
            type="password"
            placeholder="Password (min 8 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
          <input
            type="password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            disabled={loading}
          />
          {error && <p className="banner error" style={{ margin: 0 }}>{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p style={{ textAlign: "center", marginTop: 16 }}>
          <button type="button" className="btn-ghost" onClick={onBack} style={{ cursor: "pointer", border: "none", background: "none", color: "var(--primary)", textDecoration: "underline", fontSize: "14px" }}>
            Back to sign in
          </button>
        </p>
      </div>
    </div>
  );
}