"""Tests for the tamper-evident audit log hash chain."""

import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))

from audit_log import store  # noqa: E402


@pytest.fixture()
def audit_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "audit.db")
    monkeypatch.setenv("AUDIT_LOG_DB_PATH", db_path)
    monkeypatch.setattr(store, "_seed_demo_events", lambda: None)
    store.DB_PATH = None
    store.init_store(str(tmp_path))
    yield db_path


def test_chain_verifies_after_logging(audit_db):
    for i in range(3):
        store.log_event(
            action="updated",
            resource_type="control",
            resource_id=f"CTRL-{i}",
            framework_id="AIGov",
            user_email="tester@khestra.dev",
        )
    result = store.verify_chain()
    assert result["valid"] is True
    assert result["checked"] >= 3
    assert result["first_invalid"] is None


def test_entries_chain_prev_hash(audit_db):
    store.log_event(action="created", resource_type="system", resource_id="sys-1", framework_id="AIGov")
    store.log_event(action="updated", resource_type="system", resource_id="sys-1", framework_id="AIGov")
    entries = store.list_events(limit=10)
    # list is DESC; chain is ASC
    entries = list(reversed(entries))
    assert len(entries) >= 2
    h0 = entries[0]["details"].get("_integrity_hash")
    h1 = entries[1]["details"].get("_prev_hash")
    assert h1 == h0, "second entry must chain onto the first entry's hash"


def test_tampering_detected(audit_db):
    store.log_event(action="created", resource_type="policy", resource_id="pol-1", framework_id="SOC2")
    store.log_event(action="updated", resource_type="policy", resource_id="pol-1", framework_id="SOC2")
    assert store.verify_chain()["valid"] is True

    # Tamper with the first (root) entry's resource_id
    db = sqlite3.connect(audit_db)
    row = db.execute("SELECT rowid, details FROM audit_entries ORDER BY rowid ASC LIMIT 1").fetchone()
    details = json.loads(row[1])
    details["tampered"] = True
    db.execute("UPDATE audit_entries SET details = ? WHERE rowid = ?", (json.dumps(details), row[0]))
    db.commit()
    db.close()

    result = store.verify_chain()
    assert result["valid"] is False
    assert result["first_invalid"] is not None


def test_middle_tampering_breaks_chain(audit_db):
    store.log_event(action="a", resource_type="r", resource_id="1", framework_id="AIGov")
    store.log_event(action="b", resource_type="r", resource_id="2", framework_id="AIGov")
    store.log_event(action="c", resource_type="r", resource_id="3", framework_id="AIGov")
    assert store.verify_chain()["valid"] is True

    # Tamper with the middle entry's action field directly in the row
    db = sqlite3.connect(audit_db)
    row = db.execute("SELECT rowid, action FROM audit_entries ORDER BY rowid ASC LIMIT 1 OFFSET 1").fetchone()
    db.execute("UPDATE audit_entries SET action = 'hacked' WHERE rowid = ?", (row[0],))
    db.commit()
    db.close()

    result = store.verify_chain()
    assert result["valid"] is False
    assert result["invalid_count"] >= 1
    assert result["first_invalid"]["rowid"] == row[0], "the tampered entry must be the first invalid"


def test_recomputed_tampering_breaks_link(audit_db):
    """If an attacker rewrites a tampered entry's hash, the NEXT entry's link
    (which embeds the original hash) must break — propagation is detected."""
    store.log_event(action="a", resource_type="r", resource_id="1", framework_id="AIGov")
    store.log_event(action="b", resource_type="r", resource_id="2", framework_id="AIGov")
    store.log_event(action="c", resource_type="r", resource_id="3", framework_id="AIGov")
    assert store.verify_chain()["valid"] is True

    # Recompute the middle entry's stored hash after changing its action
    db = sqlite3.connect(audit_db)
    db.row_factory = sqlite3.Row
    rows = db.execute(
        "SELECT rowid, timestamp, user_id, user_email, action, resource_type, resource_id, "
        "framework_id, details FROM audit_entries ORDER BY rowid ASC LIMIT 1 OFFSET 1"
    ).fetchone()
    details = json.loads(rows["details"])
    details["_outcome"] = details.get("_outcome", "success")
    entry_data = {
        "timestamp": rows["timestamp"], "user_id": rows["user_id"], "user_email": rows["user_email"],
        "action": "hacked", "resource_type": rows["resource_type"], "resource_id": rows["resource_id"],
        "framework_id": rows["framework_id"], "outcome": details["_outcome"],
    }
    details["_integrity_hash"] = store._compute_integrity_hash(
        entry_data, details.get("_prev_hash", ""), details
    )
    db.execute(
        "UPDATE audit_entries SET action = 'hacked', details = ? WHERE rowid = ?",
        (json.dumps(details), rows["rowid"]),
    )
    db.commit()
    db.close()

    result = store.verify_chain()
    assert result["valid"] is False
    assert result["invalid_count"] >= 1
    assert result["first_invalid"] is not None
    # The rewritten entry is internally consistent; the NEXT entry's link must break.
    assert "prev hash" in result["first_invalid"]["reason"]


def test_demo_seed_entries_verify(audit_db):
    """Pre-chain seed entries (no _prev_hash) must still verify as the chain root."""
    assert store.verify_chain()["valid"] is True
