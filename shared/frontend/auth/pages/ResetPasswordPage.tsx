import { useState } from "react";
import { apiUrl } from "@shared/apiPrefix";

export default function ResetPasswordPage({
  token,
  onDone,
}: {
  token: string;
  onDone: () => void;
}) {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!password || password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/auth/reset-password"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Reset failed");
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-gate">
      <div className="auth-gate-card panel" style={{ maxWidth: 400, margin: "0 auto" }}>
        <h1 style={{ textAlign: "center", marginBottom: 8 }}>Set New Password</h1>
        {!success ? (
          <>
            <p className="muted" style={{ textAlign: "center", marginBottom: 20 }}>
              Enter your new password
            </p>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <input
                type="password"
                placeholder="New password (min 8 characters)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
                required
                disabled={loading}
              />
              <input
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={loading}
              />
              {error && <p className="banner error" style={{ margin: 0 }}>{error}</p>}
              <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%" }}>
                {loading ? "Resetting…" : "Reset password"}
              </button>
            </form>
          </>
        ) : (
          <div>
            <p className="muted" style={{ textAlign: "center", marginBottom: 12 }}>
              Password reset successfully. You can now sign in with your new password.
            </p>
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={onDone}>
              Back to sign in
            </button>
          </div>
        )}
      </div>
    </div>
  );
}