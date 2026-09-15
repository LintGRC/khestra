"""Tests for the shared assets store."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGES))

from assets.store import (
    init_store,
    list_assets,
    get_asset,
    get_asset_by_name,
    create_asset,
    update_asset,
    delete_asset,
    import_csv,
    export_csv,
)

# Store auto-seeds 5 demo assets on init_store.
SEED_COUNT = 5


@pytest.fixture(autouse=True)
def _env(tmp_path):
    uid = uuid.uuid4().hex[:8]
    db = tmp_path / f"assets_{uid}.db"
    os.environ["ASSETS_DB_PATH"] = str(db)
    init_store(str(tmp_path))
    yield
    os.environ.pop("ASSETS_DB_PATH", None)
    try:
        os.remove(str(db))
    except OSError:
        pass


class TestAssetCRUD:
    def test_create_asset(self):
        a = create_asset(name="Web App", type="application", owner="alice")
        assert a["id"]
        assert a["name"] == "Web App"
        assert a["handles_cui"] is False

    def test_create_handles_cui(self):
        a = create_asset(name="CUI Server", handles_cui=True)
        assert a["handles_cui"] is True

    def test_get_asset(self):
        a = create_asset(name="Lookup")
        got = get_asset(a["id"])
        assert got["name"] == "Lookup"

    def test_get_asset_by_name(self):
        a = create_asset(name="Unique Name")
        got = get_asset_by_name("Unique Name")
        assert got["id"] == a["id"]

    def test_get_missing(self):
        assert get_asset("nope") is None

    def test_list_includes_seeded(self):
        assert len(list_assets()) >= SEED_COUNT

    def test_update_asset(self):
        a = create_asset(name="Old")
        updated = update_asset(a["id"], name="New")
        assert updated["name"] == "New"

    def test_delete_asset(self):
        a = create_asset(name="Doomed")
        assert delete_asset(a["id"]) is True
        assert get_asset(a["id"]) is None

    def test_framework_tags_roundtrip(self):
        a = create_asset(name="Tagged", framework_tags=["CMMC", "SOC 2"])
        got = get_asset(a["id"])
        assert set(got["framework_tags"]) == {"CMMC", "SOC 2"}


class TestCSVImportExport:
    def test_import_csv(self):
        csv_bytes = b"name,type,owner\nDB Server,database,bob\nCache,infrastructure,alice\n"
        count = import_csv(csv_bytes)
        assert count == 2
        # New assets appear alongside seeded ones
        all_assets = list_assets()
        names = {a["name"] for a in all_assets}
        assert "DB Server" in names
        assert "Cache" in names

    def test_import_csv_empty(self):
        count = import_csv(b"")
        assert count == 0

    def test_export_csv(self):
        a = create_asset(name="Export Me", type="service")
        csv = export_csv([a])
        assert "Export Me" in csv
        assert "name" in csv
