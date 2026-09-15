import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ControlTest, TestStats } from "../api";
import PageIntro from "../components/PageIntro";

export default function TestingPage() {
  const [tests, setTests] = useState<ControlTest[]>([]);
  const [stats, setStats] = useState<TestStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.listTests().catch(() => ({ tests: [] })),
      api.testStats().catch(() => null),
    ]).then(([t, s]) => {
      setTests(t.tests);
      setStats(s);
    }).finally(() => setLoading(false));
  }, []);

  const passRate = stats ? stats.pass_rate : 0;
  const total = tests.length;

  return (
    <>
      <PageIntro title="Tests of Controls" />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10, marginBottom: 16 }}>
        {[
          { label: "Total Tests", value: total, color: "var(--primary)" },
          { label: "Pass Rate", value: stats ? `${Math.round(passRate)}%` : "—", color: passRate >= 80 ? "var(--success)" : passRate >= 50 ? "var(--warning)" : "var(--danger)" },
          { label: "Not Tested", value: stats?.not_tested ?? 0, color: "var(--text-muted)" },
          { label: "Pass", value: stats?.pass ?? 0, color: "var(--success)" },
          { label: "Fail", value: stats?.fail ?? 0, color: "var(--danger)" },
          { label: "Needs Review", value: stats?.needs_review ?? 0, color: "var(--warning)" },
        ].map((s) => (
          <div key={s.label} className="stat-card" style={{ textAlign: "center", padding: "12px 8px" }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div className="muted" style={{ fontSize: 11 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {loading ? (
        <p className="muted">Loading tests…</p>
      ) : tests.length === 0 ? (
        <div className="panel" style={{ padding: 24, textAlign: "center" }}>
          <p className="muted">No test cases yet. Create tests from the criterion detail page.</p>
          <Link to="/criteria" className="btn btn-primary btn-sm" style={{ marginTop: 12 }}>Browse Criteria</Link>
        </div>
      ) : (
        <div className="panel">
          <div className="panel-header">
            <strong>All Test Cases</strong>
            <span className="muted">{total} total</span>
          </div>
          <div style={{ borderTop: "1px solid var(--border-subtle)" }}>
            {tests.map((t) => (
              <div key={t.id} style={{ padding: "12px 16px", borderBottom: "1px solid var(--border-subtle)", display: "flex", alignItems: "center", gap: 12, fontSize: 13 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", flexShrink: 0, background: t.status === "pass" ? "var(--success)" : t.status === "fail" ? "var(--danger)" : t.status === "needs_review" ? "var(--warning)" : "var(--text-muted)" }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Link to={`/criteria/${encodeURIComponent(t.control_id)}`} style={{ fontWeight: 600, color: "var(--text)", textDecoration: "none", fontFamily: "monospace" }}>{t.control_id}</Link>
                  <span className="muted" style={{ marginLeft: 8 }}>{t.test_procedure}</span>
                </div>
                <span style={{ fontSize: 11, color: "var(--muted)", flexShrink: 0 }}>{t.frequency}</span>
                <span style={{ fontSize: 11, flexShrink: 0, color: t.status === "pass" ? "var(--success)" : t.status === "fail" ? "var(--danger)" : "var(--muted)", fontWeight: 600 }}>{t.status.replace("_", " ")}</span>
                {t.last_tested && <span className="muted" style={{ fontSize: 11, flexShrink: 0 }}>{t.last_tested.slice(0, 10)}</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
