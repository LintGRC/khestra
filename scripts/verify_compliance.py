"""khestra verify --evidence

CI-friendly compliance verification for the Khestra fleet (pattern: AGT's
`agt verify --evidence`). Checks:

  1. Evidence freshness   — evidence items older than the staleness window
  2. Evidence review state — pending / rejected evidence
  3. Audit log integrity   — tamper-evident hash chain verifies

Exit codes: 0 = clean, 1 = findings, 2 = error.

Usage:
    python scripts/verify_compliance.py [--data-dir DIR] [--stale-days 90]
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def _age_days(timestamp: str) -> float | None:
    if not timestamp:
        return None
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - ts).total_seconds() / 86400


def run_verification(data_dir: str, stale_days: int = 90) -> dict:
    findings = []

    # 1. Evidence freshness + review state
    evidence_db = os.environ.get("EVIDENCE_DB_PATH") or str(Path(data_dir) / "evidence.db")
    try:
        db = sqlite3.connect(evidence_db)
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT id, name, uploaded_at, review_status FROM evidence").fetchall()
        db.close()
        total = len(rows)
        stale = [r for r in rows if (a := _age_days(r["uploaded_at"] or "")) is not None and a > stale_days]
        unreviewed = [r for r in rows if r["review_status"] not in ("approved", "rejected")]
        if stale:
            findings.append(f"{len(stale)} stale evidence items (>{stale_days} days)")
        if unreviewed:
            findings.append(f"{len(unreviewed)} evidence items not reviewed (status not approved/rejected)")
    except (sqlite3.Error, OSError) as exc:
        findings.append(f"evidence store unavailable: {exc}")
        total = 0

    # 2. Audit log chain integrity
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages"))
        from audit_log.store import verify_chain

        audit = verify_chain()
        if not audit["valid"]:
            findings.append(
                f"audit chain invalid: {audit.get('invalid_count', '?')} entries "
                f"(first: {audit.get('first_invalid', {}).get('id', '?')})"
            )
    except sqlite3.OperationalError as exc:
        if "no such table" not in str(exc):
            findings.append(f"audit chain unavailable: {exc}")
    except Exception as exc:  # noqa: BLE001 — CLI should degrade gracefully
        findings.append(f"audit chain unavailable: {exc}")

    return {
        "ok": not findings,
        "evidence_items": total,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Khestra compliance verification")
    parser.add_argument("--data-dir", default=os.environ.get("DATA_DIR", "."))
    parser.add_argument("--stale-days", type=int, default=90)
    args = parser.parse_args()

    report = run_verification(args.data_dir, args.stale_days)
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        for f in report["findings"]:
            print(f"FAIL: {f}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
