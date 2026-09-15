"""Load synthetic demo orgs into workspace (no Streamlit)."""

from __future__ import annotations

from typing import Any, Dict

from demo_data import get_demo_session_payload
from demo_data_b import get_demo_b_session_payload
from demo_data_trident import get_demo_trident_session_payload
from evidence_store import persist_evidence_to_disk
from workspace_service import _evidence_path, save_workspace

DEMO_CHOICES = {
    "apex": get_demo_session_payload,
    "bridgeport": get_demo_b_session_payload,
    "trident": get_demo_trident_session_payload,
}


def payload_to_workspace(payload: dict, client_id: str, org_name: str | None = None) -> Dict[str, Any]:
    return {
        "client_id": client_id,
        "version": payload.get("version"),
        "org_name": org_name or payload["org_name"],
        "org_profile": {**payload["org_profile"], "org_name": org_name or payload["org_name"]},
        "answers": payload["answers"],
        "audit_log": [],
        "asset_scope": payload["asset_scope"],
        "scoped_controls": payload["scoped_controls"],
        "current_role": "Assessor",
        "sprs_history": [],
        "org_assets": payload.get("org_assets", {}),
        "org_asset_bytes": payload.get("org_asset_bytes", {}),
        "org_inventory": payload.get("org_inventory", {"assets": [], "updated_at": ""}),
        "live_asset_snapshots": payload.get("live_asset_snapshots", {}),
        "scope_confirmed": True,
        "last_export_at": None,
        "assessment_fingerprint_at_export": None,
        "env_scope": payload.get("env_scope", {}),
        "restored_evidence": payload.get("restored_evidence", {}),
    }


def load_demo(demo_id: str = "trident", client_id: str | None = None, org_name: str | None = None) -> Dict[str, Any]:
    from client_workspaces import active_client_id

    fn = DEMO_CHOICES.get(demo_id) or DEMO_CHOICES["apex"]
    payload = fn()
    cid = client_id or active_client_id()
    ws = payload_to_workspace(payload, cid, org_name=org_name)
    if demo_id in ("apex", "trident"):
        from collectors.engine import run_collector
        from scope_coverage import apply_live_asset_snapshot

        intune_run = run_collector("intune", use_fixture=True)
        ws = apply_live_asset_snapshot(
            ws, "intune", intune_run.checks, synced_at=intune_run.completed_at
        )
    if ws.get("restored_evidence"):
        all_entries = []
        for ans in ws["answers"].values():
            all_entries.extend(ans.get("evidence") or [])
        persist_evidence_to_disk(
            _evidence_path(cid),
            all_entries,
            cid,
            ws["restored_evidence"],
        )
    save_workspace(ws)
    if demo_id == "trident":
        _seed_trident_control_tests()
    return ws


def _seed_trident_control_tests() -> None:
    """Demo control tests with run history for the Trident workspace.

    One quarterly restore test on cadence (upcoming), one that missed its
    slot (overdue — drives the compliance calendar + sweep), and one fresh
    monthly test that has never run. Idempotent: only seeds when the store
    has no tests for the CMMC framework.
    """
    try:
        from control_tests.store import add_run, create_test, list_tests
        from evidence_hub.store import list_evidence

        if any(t.get("framework") == "CMMC Rev 2" for t in list_tests()):
            return
        owner = "admin@tridentdefense.com"
        evidence = []
        try:
            evidence = [e for e in list_evidence() if e.get("id")][:3]
        except Exception:
            evidence = []

        on_cadence = create_test(
            title="Restore test — production database cluster",
            control_id="3.10.4",
            framework="CMMC Rev 2",
            frequency="quarterly",
            owner=owner,
            target_rpo_minutes=240,
            target_rto_minutes=120,
        )
        for day, result, notes, rto, rpo, verified in [
            ("2025-11-20", "passed", "Full restore to staging; data verified", 95, 180, "Jane Weaver — IT Ops"),
            ("2026-02-20", "passed", "Point-in-time restore within RTO", 88, 240, "Jane Weaver — IT Ops"),
            ("2026-05-20", "passed", "Restored 1.2 TB; integrity checksum OK", 100, 210, "M. Okonkwo — Finance"),
        ]:
            add_run(
                on_cadence["id"], run_date=day, result=result, notes=notes, run_by=owner,
                actual_rto_minutes=rto, actual_rpo_minutes=rpo, verified_by=verified,
            )

        missed = create_test(
            title="Failover test — DR site",
            control_id="3.10.5",
            framework="CMMC Rev 2",
            frequency="quarterly",
            owner=owner,
            target_rpo_minutes=60,
            target_rto_minutes=30,
        )
        for day, result, notes, rto, rpo, verified in [
            ("2025-08-10", "passed", "Failover completed in 40 minutes", 40, 60, "Jane Weaver — IT Ops"),
            ("2025-11-10", "passed", "Failover completed; no data loss", 28, 45, "Jane Weaver — IT Ops"),
            ("2026-02-10", "failed", "Failover took 55 minutes; tape restore stalled", 55, 60, ""),
        ]:
            add_run(
                missed["id"], run_date=day, result=result, notes=notes, run_by=owner,
                actual_rto_minutes=rto, actual_rpo_minutes=rpo, verified_by=verified,
            )

        fresh = create_test(
            title="Backup verification — document shares",
            control_id="3.10.4",
            framework="CMMC Rev 2",
            frequency="monthly",
            owner=owner,
            target_rto_minutes=720,
        )
        if evidence:
            add_run(
                fresh["id"],
                run_date="2026-07-15",
                result="passed",
                notes="Share-level restore test with checksum verification",
                evidence_hub_id=evidence[0]["id"],
                evidence_title=str(evidence[0].get("display_title") or evidence[0].get("name") or ""),
                run_by=owner,
                actual_rto_minutes=120,
                verified_by="Jane Weaver — IT Ops",
            )
    except Exception:
        pass
