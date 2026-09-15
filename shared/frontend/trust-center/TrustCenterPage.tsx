import { useEffect, useState } from "react";

type Certification = {
  framework: string;
  status: string;
  last_audit: string;
  scope: string;
};

type Security = Record<string, string>;

type Subprocessor = {
  name: string;
  service: string;
  location: string;
  soc2: boolean;
};

type Policy = {
  id: string;
  title: string;
  description: string;
  version: number;
  updated_at: string;
};

type Summary = {
  org_name: string;
  certification_count: number;
  certifications: { framework: string; status: string }[];
  last_audit_date: string;
  security_count: number;
  subprocessor_count: number;
};

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "active" ? "badge badge--success" :
    status === "in_progress" ? "badge badge--warning" :
    "badge badge--default";
  return <span className={cls}>{status.replace("_", " ")}</span>;
}

export default function TrustCenterPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [certs, setCerts] = useState<Certification[]>([]);
  const [security, setSecurity] = useState<Security>({});
  const [subprocessors, setSubprocessors] = useState<Subprocessor[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [evidenceTotal, setEvidenceTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const BASE = "/api/trust-center";
    Promise.all([
      fetch(`${BASE}/summary`).then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); }).catch(() => null),
      fetch(`${BASE}/compliance`).then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); }).catch(() => []),
      fetch(`${BASE}/security`).then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); }).catch(() => ({})),
      fetch(`${BASE}/subprocessors`).then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); }).catch(() => []),
      fetch(`${BASE}/policies`).then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); }).catch(() => []),
      fetch(`${BASE}/evidence-summary`).then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); }).catch(() => ({total_evidence: 0})),
    ]).then(([s, c, sec, sub, pol, ev]) => {
      setSummary(s);
      setCerts(c as Certification[]);
      setSecurity(sec as Security);
      setSubprocessors(sub as Subprocessor[]);
      setPolicies(pol as Policy[]);
      setEvidenceTotal((ev as {total_evidence: number}).total_evidence || 0);
      setError(null);
    }).catch(() => {
      setError("Could not load Trust Center data.");
    });
  }, []);

  return (
    <div className="trust-center">
      <header className="trust-center-header">
        <h1>Trust Center</h1>
        {summary && <p className="muted">{summary.org_name}</p>}
      </header>

      {error && <div className="banner error">{error}</div>}

      <div className="trust-center-grid">
        {/* Certifications */}
        <section className="panel">
          <div className="panel-header">
            <strong>Compliance Certifications</strong>
            <span className="badge">{certs.length}</span>
          </div>
          <div className="panel-body">
            {certs.length === 0 && <p className="muted">No certifications configured.</p>}
            {certs.map((c, i) => (
              <div key={i} className="trust-center-cert-row">
                <div className="trust-center-cert-info">
                  <strong>{c.framework}</strong>
                  <p className="muted">{c.scope}</p>
                </div>
                <StatusBadge status={c.status} />
              </div>
            ))}
          </div>
        </section>

        {/* Security */}
        <section className="panel">
          <div className="panel-header">
            <strong>Security Posture</strong>
          </div>
          <div className="panel-body">
            {Object.keys(security).length === 0 && <p className="muted">No security info configured.</p>}
            {Object.entries(security).map(([key, val]) => (
              <div key={key} className="trust-center-kv">
                <span className="trust-center-kv-key">{key.replace(/_/g, " ")}</span>
                <span className="trust-center-kv-value">{val}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Subprocessors */}
        <section className="panel">
          <div className="panel-header">
            <strong>Subprocessors</strong>
            <span className="badge">{subprocessors.length}</span>
          </div>
          <div className="panel-body">
            {subprocessors.length === 0 && <p className="muted">No subprocessors configured.</p>}
            {subprocessors.map((sp, i) => (
              <div key={i} className="trust-center-sub-row">
                <div className="trust-center-sub-info">
                  <strong>{sp.name}</strong>
                  <p className="muted">{sp.service} — {sp.location}</p>
                </div>
                {sp.soc2 && <span className="badge badge--success">SOC 2</span>}
              </div>
            ))}
          </div>
        </section>

        {/* Published Policies */}
        <section className="panel">
          <div className="panel-header">
            <strong>Published Policies</strong>
            <span className="badge">{policies.length}</span>
          </div>
          <div className="panel-body">
            {policies.length === 0 && <p className="muted">No published policies yet.</p>}
            {policies.map(p => (
              <div key={p.id} className="trust-center-policy-row">
                <a
                  className="trust-center-policy-link"
                  href={`/api/policies/${p.id}/export`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {p.title}
                </a>
                <span className="muted">v{p.version}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Evidence Summary */}
        <section className="panel">
          <div className="panel-header">
            <strong>Evidence Collection</strong>
          </div>
          <div className="panel-body">
            <div className="trust-center-stat">{evidenceTotal}</div>
            <p className="muted">total evidence artifacts collected</p>
          </div>
        </section>
      </div>

      <style>{`
        .trust-center { padding: 2rem; max-width: 1200px; margin: 0 auto; }
        .trust-center-header { margin-bottom: 2rem; }
        .trust-center-header h1 { margin: 0 0 0.25rem; font-size: 1.75rem; }
        .trust-center-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        @media (max-width: 768px) { .trust-center-grid { grid-template-columns: 1fr; } }
        .trust-center-cert-row, .trust-center-sub-row, .trust-center-policy-row { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border, #e5e7eb); }
        .trust-center-cert-row:last-child, .trust-center-sub-row:last-child, .trust-center-policy-row:last-child { border-bottom: none; }
        .trust-center-cert-info p, .trust-center-sub-info p { margin: 0; font-size: 0.8rem; }
        .trust-center-kv { padding: 0.25rem 0; }
        .trust-center-kv-key { font-weight: 600; display: block; font-size: 0.8rem; text-transform: capitalize; }
        .trust-center-kv-value { font-size: 0.9rem; }
        .trust-center-policy-link { font-weight: 500; }
        .trust-center-stat { font-size: 2rem; font-weight: 700; color: var(--primary, #1f4e79); }
        .badge { display: inline-block; padding: 0.125rem 0.5rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
        .badge--success { background: #d1fae5; color: #065f46; }
        .badge--warning { background: #fef3c7; color: #92400e; }
        .badge--default { background: #e5e7eb; color: #374151; }
      `}</style>
    </div>
  );
}
