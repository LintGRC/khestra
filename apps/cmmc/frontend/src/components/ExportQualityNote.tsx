import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, ReadinessReviewSummary } from "../api";

export default function ExportQualityNote() {
  const [review, setReview] = useState<ReadinessReviewSummary | null>(null);

  useEffect(() => {
    api.readinessReview().then((r) => setReview(r as ReadinessReviewSummary)).catch(console.error);
  }, []);

  if (!review) return null;

  const ev = review.evidence;
  const metNoProof = review.finding_summary?.met_no_proof_count ?? 0;

  if (!ev.met_count) {
    return (
      <p className="muted export-quality-note">
        Audit package review: no MET controls yet — proof tracking starts when you mark controls MET.
      </p>
    );
  }

  if (metNoProof > 0) {
    return (
      <div className="banner warning export-quality-note">
        <strong>{metNoProof} of {ev.met_count} MET controls</strong> still need proof (upload a file or add an{" "}
        <strong>Examine</strong> reference on <Link to="/controls">Controls</Link>). Package quality:{" "}
        <strong>{review.review_score}%</strong> — not your SPRS score.
      </div>
    );
  }

  if (review.review_score < 100) {
    return (
      <div className="banner info export-quality-note">
        Package quality <strong>{review.review_score}%</strong> — {review.quality_explanation}{" "}
        Open <Link to="/readiness">Readiness</Link> for the full audit package review.
      </div>
    );
  }

  return (
    <div className="banner success export-quality-note">
      All <strong>{ev.met_count}</strong> MET controls have a file or Examine reference attached.{" "}
      <Link to="/readiness">Readiness</Link> has the full review; a report is included in the audit package zip.
    </div>
  );
}
