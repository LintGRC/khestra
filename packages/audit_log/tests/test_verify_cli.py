"""Tests for the khestra verify --evidence CLI (scripts/verify_compliance.py)."""

import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_compliance import run_verification  # noqa: E402


def _make_evidence_db(path: str, items: list[tuple[str, str, str]]):
    """items: (id, name, uploaded_at, review_status)"""
    db = sqlite3.connect(path)
    db.executescript(
        "CREATE TABLE evidence (id TEXT PRIMARY KEY, name TEXT, uploaded_at TEXT, review_status TEXT)"
    )
    for i in items:
        db.execute("INSERT INTO evidence (id, name, uploaded_at, review_status) VALUES (?, ?, ?, ?)", i)
    db.commit()
    db.close()


def test_clean_fleet_passes(tmp_path, monkeypatch):
    db_path = str(tmp_path / "evidence.db")
    _make_evidence_db(db_path, [
        ("e1", "Policy", "2026-08-01T00:00:00Z", "approved"),
        ("e2", "Screenshot", "2026-07-01T00:00:00Z", "approved"),
    ])
    monkeypatch.setenv("EVIDENCE_DB_PATH", db_path)
    monkeypatch.setenv("AUDIT_LOG_DB_PATH", str(tmp_path / "audit.db"))
    report = run_verification(str(tmp_path))
    assert report["ok"] is True
    assert report["evidence_items"] == 2


def test_stale_evidence_fails(tmp_path, monkeypatch):
    db_path = str(tmp_path / "evidence.db")
    _make_evidence_db(db_path, [
        ("e1", "OldPolicy", "2020-01-01T00:00:00Z", "approved"),
    ])
    monkeypatch.setenv("EVIDENCE_DB_PATH", db_path)
    monkeypatch.setenv("AUDIT_LOG_DB_PATH", str(tmp_path / "audit.db"))
    report = run_verification(str(tmp_path), stale_days=90)
    assert report["ok"] is False
    assert any("stale" in f for f in report["findings"])


def test_unreviewed_evidence_fails(tmp_path, monkeypatch):
    db_path = str(tmp_path / "evidence.db")
    _make_evidence_db(db_path, [
        ("e1", "Pending", "2026-08-01T00:00:00Z", "pending"),
    ])
    monkeypatch.setenv("EVIDENCE_DB_PATH", db_path)
    monkeypatch.setenv("AUDIT_LOG_DB_PATH", str(tmp_path / "audit.db"))
    report = run_verification(str(tmp_path))
    assert report["ok"] is False
    assert any("not reviewed" in f for f in report["findings"])


def test_missing_evidence_store_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("EVIDENCE_DB_PATH", str(tmp_path / "missing.db"))
    monkeypatch.setenv("AUDIT_LOG_DB_PATH", str(tmp_path / "audit.db"))
    report = run_verification(str(tmp_path))
    assert report["ok"] is False
