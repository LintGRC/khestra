import { Link } from "react-router-dom";

export type ReviewFinding = {
  severity: string;
  title: string;
  detail: string;
  control_ids?: string[];
};

export type FindingSummary = {
  met_no_proof_ids: string[];
  met_no_proof_count: number;
  short_narrative_ids: string[];
  short_narrative_count: number;
  gap_no_poam_ids: string[];
  gap_no_poam_count: number;
  scope_checks: ReviewFinding[];
  narrative_checks: ReviewFinding[];
  other: ReviewFinding[];
};

function ControlIdList({ ids, limit = 24 }: { ids: string[]; limit?: number }) {
  if (!ids.length) return null;
  const shown = ids.slice(0, limit);
  const rest = ids.length - shown.length;
  return (
    <div className="priority-chips quality-finding-ids">
      {shown.map((cid) => (
        <Link key={cid} className="priority-chip" to={`/controls/${encodeURIComponent(cid)}`}>
          {cid}
        </Link>
      ))}
      {rest > 0 && <span className="muted quality-finding-more">+{rest} more</span>}
    </div>
  );
}

function FindingGroup({
  tone,
  title,
  detail,
  ids,
  defaultOpen,
}: {
  tone: "warn" | "info";
  title: string;
  detail: string;
  ids?: string[];
  defaultOpen?: boolean;
}) {
  return (
    <div className={`quality-finding quality-finding-${tone}`}>
      <strong>{title}</strong>
      <p className="muted">{detail}</p>
      {ids && ids.length > 0 && (
        <details className="quality-finding-details" open={defaultOpen}>
          <summary>Control IDs ({ids.length})</summary>
          <ControlIdList ids={ids} />
        </details>
      )}
    </div>
  );
}

export default function PackageQualityFindings({ summary }: { summary: FindingSummary }) {
  const hasGrouped =
    summary.met_no_proof_count > 0
    || summary.short_narrative_count > 0
    || summary.gap_no_poam_count > 0
    || summary.scope_checks.length > 0
    || summary.narrative_checks.length > 0
    || summary.other.length > 0;

  if (!hasGrouped) return null;

  return (
    <div className="quality-findings">
      {summary.met_no_proof_count > 0 && (
        <FindingGroup
          tone="warn"
          title={`${summary.met_no_proof_count} MET control${summary.met_no_proof_count === 1 ? "" : "s"} missing proof`}
          detail="Upload a file or add an Examine reference (policy/SOP name) on each control before audit."
          ids={summary.met_no_proof_ids}
          defaultOpen={summary.met_no_proof_count <= 6}
        />
      )}
      {summary.short_narrative_count > 0 && (
        <FindingGroup
          tone="info"
          title={`${summary.short_narrative_count} MET control${summary.short_narrative_count === 1 ? "" : "s"} with very short narrative`}
          detail="Expand implementation text (80+ characters) before SSP export."
          ids={summary.short_narrative_ids}
        />
      )}
      {summary.gap_no_poam_count > 0 && (
        <FindingGroup
          tone="info"
          title={`${summary.gap_no_poam_count} open gap${summary.gap_no_poam_count === 1 ? "" : "s"} without POA&M notes`}
          detail="Add assessor notes or a remediation plan for POA&M export."
          ids={summary.gap_no_poam_ids}
        />
      )}
      {summary.scope_checks.map((f) => (
        <FindingGroup key={f.title} tone="warn" title={f.title} detail={f.detail} />
      ))}
      {summary.narrative_checks.map((f) => (
        <FindingGroup key={f.title} tone="info" title={f.title} detail={f.detail} />
      ))}
      {summary.other.map((f) => (
        <FindingGroup
          key={f.title}
          tone={f.severity === "high" ? "warn" : "info"}
          title={f.title}
          detail={f.detail}
        />
      ))}
    </div>
  );
}
