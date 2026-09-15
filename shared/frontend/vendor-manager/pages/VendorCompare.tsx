import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { vendorApi, vendorTerm } from "../api";
import type { VendorItem, VendorAssessment } from "../types";

function riskBadge(score: number | null) {
  if (score == null) return <>—</>;
  if (score >= 80) return <span className="badge badge-success">Low Risk ({score})</span>;
  if (score >= 50) return <span className="badge badge-warning">Medium ({score})</span>;
  return <span className="badge badge-danger">High Risk ({score})</span>;
}

function levelBadge(level: string) {
  const m: Record<string, string> = {
    low: "badge-success", medium: "badge-warning", high: "badge-danger", critical: "badge-danger",
  };
  return <span className={`badge ${m[level] || "badge-muted"}`}>{level}</span>;
}

export default function VendorCompare() {
  const [searchParams] = useSearchParams();
  const ids = (searchParams.get("ids") || "").split(",").filter(Boolean);
  const [vendors, setVendors] = useState<(VendorItem & { assessment?: VendorAssessment | null })[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ids.length) { setLoading(false); return; }
    Promise.all(
      ids.map(async (id) => {
        try {
          const [vd, ad] = await Promise.all([
            vendorApi.get(id),
            vendorApi.assessment(id).catch(() => ({ assessment: null })),
          ]);
          return { ...vd.vendor, assessment: ad.assessment };
        } catch { return null; }
      }),
    ).then((results) => {
      setVendors(results.filter(Boolean) as any);
    }).finally(() => setLoading(false));
  }, [ids.join(",")]);

  if (loading) return <div className="page-stack"><p className="muted">Loading...</p></div>;

  if (!ids.length || vendors.length === 0) {
    return (
      <div className="page-stack">
        <div className="page-header"><h2>{vendorTerm(2)} Comparison</h2></div>
        <p className="muted">Select {vendorTerm(2).toLowerCase()} from the dashboard to compare.</p>
        <Link to="/vendors" className="btn btn-primary btn-sm">Back to {vendorTerm(2)}</Link>
      </div>
    );
  }

  const rows: { label: string; render: (v: any) => any }[] = [
    { label: "Status", render: (v: any) => v.status },
    { label: "Risk Score", render: (v: any) => riskBadge(v.risk_score) },
    { label: "Risk Level", render: (v: any) => v.risk_level ? levelBadge(v.risk_level) : "—" },
    { label: "Category", render: (v: any) => v.category?.replace(/_/g, " ") || "—" },
    { label: "Tier", render: (v: any) => v.tier || "—" },
    { label: "Frameworks", render: (v: any) => (v.frameworks || []).join(", ") || "—" },
    { label: "AI Service", render: (v: any) => v.ai_service_type || "—" },
    { label: "Contact", render: (v: any) => v.contact_email || "—" },
    { label: "Data Residency", render: (v: any) => (v.data_residency || []).join(", ") || "—" },
    { label: "DPA", render: (v: any) => v.dpa_in_place ? "Yes" : "No" },
    { label: "Certs", render: (v: any) => (v.certificates || []).length ? `${v.certificates.length} uploaded` : "—" },
    { label: "Assessment Score", render: (v: any) => v.assessment ? `${v.assessment.overall_score}/100` : "—" },
    { label: "Assessment Level", render: (v: any) => v.assessment ? levelBadge(v.assessment.overall_level) : "—" },
    { label: "Findings", render: (v: any) => v.assessment ? (v.assessment.findings || []).length : "—" },
    { label: "Reminders", render: (v: any) => v.reminder_count || 0 },
    { label: "Created", render: (v: any) => v.created_at?.slice(0, 10) || "—" },
  ];

  return (
    <div className="page-stack">
      <div className="page-header">
        <h2>{vendorTerm(2)} Comparison</h2>
        <p className="muted">{vendors.length} {vendorTerm(vendors.length).toLowerCase()} selected</p>
        <Link to="/vendors" className="muted" style={{ fontSize: 13, textDecoration: "none" }}>← Back to {vendorTerm(2)}</Link>
      </div>

      <div className="panel">
        <div className="panel-body" style={{ padding: 0, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: "2px solid var(--border)" }}>
                <th style={{ padding: "10px 12px", textAlign: "left", fontWeight: 600, whiteSpace: "nowrap", position: "sticky", left: 0, background: "var(--panel-bg, #fff)" }}>Field</th>
                {vendors.map((v) => (
                  <th key={v.id} style={{ padding: "10px 12px", textAlign: "center", fontWeight: 600 }}>
                    <Link to={`/vendors/${v.id}`} style={{ textDecoration: "none", color: "var(--link)" }}>{v.name}</Link>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={row.label} style={{ borderBottom: "1px solid var(--border)", background: i % 2 === 0 ? "var(--surface-muted, rgba(0,0,0,0.02))" : "transparent" }}>
                  <td style={{ padding: "8px 12px", fontWeight: 600, whiteSpace: "nowrap", position: "sticky", left: 0, background: "var(--panel-bg, #fff)" }}>{row.label}</td>
                  {vendors.map((v) => (
                    <td key={v.id} style={{ padding: "8px 12px", textAlign: "center" }}>{row.render(v)}</td>
                  ))}
                </tr>
              ))}
              {vendors.some((v) => v.assessment?.category_scores?.length) && (
                <>
                  <tr style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "8px 12px", fontWeight: 700, position: "sticky", left: 0, background: "var(--panel-bg, #fff)" }}>Category Scores</td>
                    {vendors.map((v) => (
                      <td key={v.id} style={{ padding: "8px 12px", textAlign: "center" }}>
                        {v.assessment?.category_scores?.length ? (
                          <div style={{ fontSize: 12 }}>
                            {v.assessment.category_scores.map((cs: any) => (
                              <div key={cs.category} style={{ marginBottom: 2 }}>
                                <span className="muted">{cs.category.replace(/_/g, " ")}: </span>
                                <strong>{cs.score}</strong>
                              </div>
                            ))}
                          </div>
                        ) : "—"}
                      </td>
                    ))}
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
