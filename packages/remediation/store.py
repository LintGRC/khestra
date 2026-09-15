"""SQLite-backed store for remediation items — shared across all frameworks."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import RemediationItem


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS remediation_items (
  id TEXT PRIMARY KEY,
  framework TEXT DEFAULT '',
  type TEXT DEFAULT 'gap',
  title TEXT DEFAULT '',
  description TEXT DEFAULT '',
  status TEXT DEFAULT 'open',
  priority TEXT DEFAULT 'medium',
  severity TEXT DEFAULT 'medium',
  owner TEXT DEFAULT '',
  source_id TEXT DEFAULT '',
  control_id TEXT DEFAULT '',
  framework_ref TEXT DEFAULT '',
  target_date TEXT DEFAULT '',
  completed_at TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT '',
  metadata TEXT DEFAULT '{}'
);
"""

_COLS = [
    "id", "framework", "type", "title", "description",
    "status", "priority", "severity", "owner",
    "source_id", "control_id", "framework_ref",
    "target_date", "completed_at", "created_at", "updated_at",
    "metadata",
]


class RemediationStore:
    """SQLite-backed repository for remediation items.

    Each app provides a data directory; items are stored under data/remediation/remediation.db.
    """

    def __init__(self, data_dir: Path):
        self._db_path = data_dir / "remediation" / "remediation.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        old_json = data_dir / "remediation" / "items.json"
        if not self._db_path.is_file() and old_json.is_file():
            self._migrate_from_json(old_json)
        else:
            self._get_db().close()

    def _get_db(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self._db_path), timeout=10)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA busy_timeout=5000")
        db.row_factory = sqlite3.Row
        db.executescript(_SCHEMA_SQL)
        return db

    def _migrate_from_json(self, json_path: Path):
        try:
            items = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            items = {}
        if not items:
            json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))
            return

        db = self._get_db()
        try:
            placeholders = ", ".join(["?"] * len(_COLS))
            cols_str = ", ".join(_COLS)
            for data in items.values():
                metadata = json.dumps(data.get("metadata", {}), default=str)
                vals = [data.get(col, "") for col in _COLS[:-1]] + [metadata]
                db.execute(f"INSERT INTO remediation_items ({cols_str}) VALUES ({placeholders})", vals)
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            placeholders = ", ".join(["?"] * len(_COLS))
            cols_str = ", ".join(_COLS)
            for data in items.values():
                try:
                    metadata = json.dumps(data.get("metadata", {}), default=str)
                    vals = [data.get(col, "") for col in _COLS[:-1]] + [metadata]
                    db.execute(f"INSERT INTO remediation_items ({cols_str}) VALUES ({placeholders})", vals)
                except sqlite3.IntegrityError:
                    pass
            db.commit()
        finally:
            db.close()
        json_path.rename(json_path.with_suffix(json_path.suffix + ".migrated"))

    def _row_to_item(self, row: sqlite3.Row) -> RemediationItem:
        d = dict(row)
        try:
            d["metadata"] = json.loads(d.get("metadata", "{}"))
        except (json.JSONDecodeError, TypeError):
            d["metadata"] = {}
        return RemediationItem.from_dict(d)

    def list(
        self,
        framework: Optional[str] = None,
        type_filter: Optional[str] = None,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[RemediationItem]:
        db = self._get_db()
        try:
            conditions: list[str] = []
            params: list[str] = []
            if framework:
                conditions.append("framework = ?")
                params.append(framework)
            if type_filter:
                conditions.append("type = ?")
                params.append(type_filter)
            if status:
                conditions.append("status = ?")
                params.append(status)
            if owner:
                conditions.append("owner = ?")
                params.append(owner)

            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(
                f"SELECT * FROM remediation_items{where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset],
            ).fetchall()
            return [self._row_to_item(r) for r in rows]
        finally:
            db.close()

    def get(self, item_id: str) -> Optional[RemediationItem]:
        db = self._get_db()
        try:
            row = db.execute("SELECT * FROM remediation_items WHERE id = ?", (item_id,)).fetchone()
            return self._row_to_item(row) if row else None
        finally:
            db.close()

    def upsert(self, item: RemediationItem) -> RemediationItem:
        import datetime as _dt

        now = _dt.datetime.now(_dt.timezone.utc).isoformat()
        item.updated_at = now

        db = self._get_db()
        try:
            data = item.to_dict()
            metadata = json.dumps(data.get("metadata", {}), default=str)
            vals = [data.get(col, "") for col in _COLS[:-1]] + [metadata]

            cols_str = ", ".join(_COLS)
            placeholders = ", ".join(["?"] * len(_COLS))
            update_str = ", ".join(f"{c} = excluded.{c}" for c in _COLS)

            db.execute(
                f"INSERT INTO remediation_items ({cols_str}) VALUES ({placeholders}) "
                f"ON CONFLICT(id) DO UPDATE SET {update_str}",
                vals,
            )
            db.commit()
        finally:
            db.close()
        return item

    def delete(self, item_id: str) -> bool:
        db = self._get_db()
        try:
            cur = db.execute("DELETE FROM remediation_items WHERE id = ?", (item_id,))
            db.commit()
            return cur.rowcount > 0
        finally:
            db.close()

    def count(
        self,
        framework: Optional[str] = None,
        type_filter: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        db = self._get_db()
        try:
            conditions: list[str] = []
            params: list[str] = []
            if framework:
                conditions.append("framework = ?")
                params.append(framework)
            if type_filter:
                conditions.append("type = ?")
                params.append(type_filter)
            if status:
                conditions.append("status = ?")
                params.append(status)

            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            row = db.execute(f"SELECT COUNT(*) as c FROM remediation_items{where}", params).fetchone()
            return row["c"]
        finally:
            db.close()

    def stats(self, framework: Optional[str] = None) -> Dict[str, Any]:
        db = self._get_db()
        try:
            params: list[str] = []
            fw_filter = " WHERE framework = ?" if framework else ""
            if framework:
                params.append(framework)

            total_row = db.execute(f"SELECT COUNT(*) as c FROM remediation_items{fw_filter}", params).fetchone()
            total = total_row["c"]

            by_status = {
                r["status"]: r["c"]
                for r in db.execute(
                    f"SELECT status, COUNT(*) as c FROM remediation_items{fw_filter} GROUP BY status",
                    params,
                ).fetchall()
            }
            by_priority = {
                r["priority"]: r["c"]
                for r in db.execute(
                    f"SELECT priority, COUNT(*) as c FROM remediation_items{fw_filter} GROUP BY priority",
                    params,
                ).fetchall()
            }

            return {
                "total": total,
                "by_status": by_status,
                "by_priority": by_priority,
                "open": by_status.get("open", 0) + by_status.get("in_progress", 0),
            }
        finally:
            db.close()
