import { useState } from "react";
import { apiUrl } from "@shared/apiPrefix";

export default function ForgotPasswordPage({
  onBack,
  onResetToken,
}: {
  onBack: () => void;
  onResetToken: (token: string) => void;
}) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [resetToken, setResetToken] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.trim()) {
      setError("Email is required");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/auth/forgot-password"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      if (data.reset_token) {
        setResetToken(data.reset_token);
      }
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-gate">
      <div className="auth-gate-card panel" style={{ maxWidth: 400, margin: "0 auto" }}>
        <h1 style={{ textAlign: "center", marginBottom: 8 }}>Reset Password</h1>
        {!sent ? (
          <>
            <p className="muted" style={{ textAlign: "center", marginBottom: 20 }}>
              Enter your email to receive a reset link
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
              {error && <p className="banner error" style={{ margin: 0 }}>{error}</p>}
              <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%" }}>
                {loading ? "Sending…" : "Send reset link"}
              </button>
            </form>
          </>
        ) : (
          <>
            {resetToken ? (
              <div>
                <p className="muted" style={{ textAlign: "center", marginBottom: 12 }}>
                  A reset token has been generated. Click below to reset your password.
                </p>
                <button
                  className="btn btn-primary"
                  style={{ width: "100%" }}
                  onClick={() => onResetToken(resetToken)}
                >
                  Continue reset
                </button>
              </div>
            ) : (
              <p className="muted" style={{ textAlign: "center", marginBottom: 12 }}>
                If that email exists, a reset link has been sent.
              </p>
            )}
          </>
        )}
        <p style={{ textAlign: "center", marginTop: 16 }}>
          <button
            type="button"
            className="btn-ghost"
            onClick={onBack}
            style={{ cursor: "pointer", border: "none", background: "none", color: "var(--primary)", textDecoration: "underline", fontSize: "14px" }}
          >
            Back to sign in
          </button>
        </p>
      </div>
    </div>
  );
}