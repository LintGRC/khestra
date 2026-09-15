import { Link, useLocation, useSearchParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, ControlSummary } from "../api";
import { useLayout } from "../Layout";
import PageIntro from "../components/PageIntro";
import { EmptyState, PageSkeleton } from "../components/ui/Skeleton";
import { FilterBar, FilterSearch, FilterSelect } from "@shared/filter-bar";

function statusClass(status: string): string {
  if (["MET", "NOT APPLICABLE", "INHERITED"].includes(status)) return "met";
  if (["NOT MET", "NOT STARTED"].includes(status)) return "gap";
  return "neutral";
}

function opStatusColor(os: string | undefined): string {
  if (os === "PASS") return "var(--success)";
  if (os === "FAIL") return "var(--danger)";
  if (os === "NEEDS REVIEW") return "var(--warning)";
  return "var(--text-muted)";
}

function freshnessLabel(freshness: string, lastDate: string | null): string {
  if (!lastDate) return "—";
  if (freshness === "fresh") return "Fresh";
  if (freshness === "stale") return "Stale";
  if (freshness === "expired") return "Expired";
  return "—";
}

function freshnessDot(freshness: string): string {
  if (freshness === "fresh") return "●";
  if (freshness === "stale") return "●";
  if (freshness === "expired") return "●";
  return "○";
}

function freshnessColor(freshness: string): string {
  if (freshness === "fresh") return "var(--success)";
  if (freshness === "stale") return "var(--warning)";
  if (freshness === "expired") return "var(--danger)";
  return "var(--text-muted)";
}

export default function CriteriaPage() {
  const { dashboard } = useLayout();
  const { pathname } = useLocation();
  const fwBase = pathname.match(/^\/(cmmc|soc2|aigov)/)?.[0] ?? "";
  const [searchParams] = useSearchParams();
  const [controls, setControls] = useState<ControlSummary[]>([]);
  const [categories, setCategories] = useState<{ id: string; label: string }[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState(() => searchParams.get("category") || "");
  const [coverageFilter, setCoverageFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.controls(category || undefined, search || undefined)
      .then((data) => {
        setControls(data.controls);
        setCategories(data.category_options);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [category, search]);

  if (loading) return <PageSkeleton variant="default" />;

  const coverageMap = new Map(
    (dashboard?.coverage || []).map((c) => [c.id, c])
  );

  let filtered = controls;
  if (coverageFilter === "covered") {
    filtered = filtered.filter((c) => coverageMap.get(c.id)?.has_evidence);
  } else if (coverageFilter === "missing") {
    filtered = filtered.filter((c) => !coverageMap.get(c.id)?.has_evidence);
  } else if (coverageFilter === "auto") {
    filtered = filtered.filter((c) => coverageMap.get(c.id)?.has_auto_evidence);
  } else if (coverageFilter === "stale") {
    filtered = filtered.filter((c) => {
      const cov = coverageMap.get(c.id);
      return cov && (cov.freshness === "stale" || cov.freshness === "expired");
    });
  }

  return (
    <>
      <PageIntro title={`Trust Services Criteria (${controls.length} in scope)`} summary="Track evidence coverage per criterion based on your selected TSC scope. Green = fresh evidence, yellow = stale, red = expired, gray = none." />

      <FilterBar>
        <FilterSearch value={search} onChange={setSearch} placeholder="Search criteria…" debounceMs={300} />
        <FilterSelect value={category} onChange={setCategory} options={categories.map((c) => ({ value: c.id, label: c.label }))} placeholder="All categories" />
        <FilterSelect value={coverageFilter} onChange={setCoverageFilter} options={[
          { value: "covered", label: "With evidence" },
          { value: "auto", label: "Auto-collected" },
          { value: "stale", label: "Stale / expired" },
          { value: "missing", label: "Missing evidence" },
        ]} placeholder="All coverage" />
      </FilterBar>

      {filtered.length === 0 ? (
        <EmptyState title="No criteria match" description="Try a different search or filter.">
          <button className="btn btn-secondary btn-sm" onClick={() => { setSearch(""); setCategory(""); setCoverageFilter("all"); }}>
            Clear filters
          </button>
        </EmptyState>
      ) : (
        <div className="criteria-list">
          {filtered.map((c) => {
            const cov = coverageMap.get(c.id);
            return (
              <Link
                key={c.id}
                to={`${fwBase}/criteria/${encodeURIComponent(c.id)}`}
                className={`criteria-card ${statusClass(c.status)}`}
              >
                <div className="criteria-card-header">
                  <span className="criteria-code">{c.id}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span title={`Operating: ${c.operating_status || "NOT TESTED"}`} style={{ width: 8, height: 8, borderRadius: "50%", background: opStatusColor(c.operating_status), display: "inline-block", flexShrink: 0 }} />
                    <span className={`status-badge status-${statusClass(c.status)}`}>{c.status}</span>
                  </div>
                </div>
                <h3 className="criteria-name">{c.name}</h3>
                <p className="muted criteria-desc">{c.description}</p>
                <div className="criteria-card-footer">
                  <span className="criteria-evidence-count">
                    {c.evidence_count} file{c.evidence_count !== 1 ? "s" : ""}
                    {c.auto_evidence_count > 0 && ` (${c.auto_evidence_count} auto)`}
                  </span>
                  {c.pof_total !== undefined && c.pof_total > 0 && (
                    <span className="criteria-pof-badge" style={{ fontSize: "0.7rem", color: (c.pof_coverage_pct ?? 0) >= 80 ? "var(--success)" : (c.pof_coverage_pct ?? 0) >= 50 ? "var(--warning)" : "var(--danger)" }}>
                      {c.pof_addressed}/{c.pof_total} PoFs
                    </span>
                  )}
                  <span className="criteria-freshness">
                    {cov && <span style={{ color: freshnessColor(cov.freshness) }}>{freshnessDot(cov.freshness)}</span>} {cov ? freshnessLabel(cov.freshness, cov.last_evidence_date) : "—"}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </>
  );
}
