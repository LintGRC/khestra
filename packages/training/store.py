import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .models import (
    TrainingModule, TrainingAssignment,
    utcnow, TRAINING_STATUSES,
)


DB_PATH: str | None = None
PERSONNEL_STORE = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS training_modules (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '',
  description TEXT DEFAULT '',
  category TEXT DEFAULT '',
  is_required INTEGER DEFAULT 1,
  renewal_period_days INTEGER DEFAULT 365,
  control_ids TEXT DEFAULT '',
  created_by TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS training_assignments (
  id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL,
  person_id TEXT NOT NULL,
  status TEXT DEFAULT 'assigned',
  assigned_date TEXT DEFAULT '',
  completion_date TEXT DEFAULT '',
  expiry_date TEXT DEFAULT '',
  evidence_id TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  exemption_reason TEXT DEFAULT '',
  exempted_by TEXT DEFAULT '',
  exempted_date TEXT DEFAULT '',
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);
"""

_MODULE_COLS = [
    "id", "title", "description", "category", "is_required",
    "renewal_period_days", "control_ids", "content_md", "quiz_questions",
    "created_by", "created_at", "updated_at",
]
_ASSIGNMENT_COLS = [
    "id", "module_id", "person_id", "status", "assigned_date",
    "completion_date", "expiry_date", "evidence_id", "notes",
    "exemption_reason", "exempted_by", "exempted_date",
    "created_at", "updated_at",
]


def _get_db() -> sqlite3.Connection:
    global DB_PATH
    path = os.environ.get("TRAINING_DB_PATH") or DB_PATH or "/tmp/khestra-training.db"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.row_factory = sqlite3.Row
    _ensure_schema(db)
    return db


def _ensure_schema(db: sqlite3.Connection):
    db.executescript(_SCHEMA_SQL)
    for col, dtype in {"control_ids": "TEXT DEFAULT ''", "content_md": "TEXT DEFAULT ''", "quiz_questions": "TEXT DEFAULT '[]'"}.items():
        try:
            db.execute(f"ALTER TABLE training_modules ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


def _module_to_row(m: dict) -> list:
    row = [m.get(col, "") for col in _MODULE_COLS]
    row[_MODULE_COLS.index("is_required")] = 1 if m.get("is_required") else 0
    qq = m.get("quiz_questions", [])
    row[_MODULE_COLS.index("quiz_questions")] = json.dumps(qq) if isinstance(qq, (list, dict)) else qq
    return row


def _row_to_module(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["is_required"] = bool(d.get("is_required", 0))
    if isinstance(d.get("control_ids"), str):
        try:
            d["control_ids"] = json.loads(d["control_ids"])
        except (json.JSONDecodeError, TypeError):
            d["control_ids"] = []
    return d


def _assignment_to_row(a: dict) -> list:
    return [a.get(col, "") for col in _ASSIGNMENT_COLS]


def _row_to_assignment(row: sqlite3.Row) -> dict:
    return dict(row)


def _get_person_name(person_id: str) -> dict:
    try:
        from personnel.store import get_person
        p = get_person(person_id)
        if p:
            return {"person_name": p.get("name", ""), "person_email": p.get("email", "")}
    except Exception:
        pass
    return {"person_name": "", "person_email": ""}


def _enrich_assignments(assignments: list[dict]) -> list[dict]:
    for a in assignments:
        name_data = _get_person_name(a.get("person_id", ""))
        a.update(name_data)
    return assignments


def init_store(data_dir: str):
    global DB_PATH
    DB_PATH = str(Path(data_dir) / "training.db")
    db = _get_db()
    db.close()


# ─── Modules CRUD ────────────────────


def list_modules(control_id: str | None = None) -> list[dict]:
    db = _get_db()
    try:
        if control_id:
            rows = db.execute(
                "SELECT * FROM training_modules WHERE control_ids LIKE ? ORDER BY title ASC",
                (f'%"{control_id}"%',),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM training_modules ORDER BY title ASC").fetchall()
        return [_row_to_module(r) for r in rows]
    finally:
        db.close()


def get_module(module_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM training_modules WHERE id = ?", (module_id,)).fetchone()
        return _row_to_module(row) if row else None
    finally:
        db.close()


def create_module(
    title: str,
    description: str = "",
    category: str = "",
    is_required: bool = True,
    renewal_period_days: int = 365,
    control_ids: str = "",
    content_md: str = "",
    quiz_questions: list[dict] | None = None,
    created_by: str = "",
) -> dict:
    now = utcnow()
    m = TrainingModule(
        id=uuid4().hex[:12],
        title=title,
        description=description,
        category=category,
        is_required=is_required,
        renewal_period_days=renewal_period_days,
        control_ids=control_ids,
        content_md=content_md,
        quiz_questions=quiz_questions or [],
        created_by=created_by,
        created_at=now,
        updated_at=now,
    )
    d = m.to_dict()
    db = _get_db()
    try:
        placeholders = ", ".join(["?"] * len(_MODULE_COLS))
        cols = ", ".join(_MODULE_COLS)
        db.execute(f"INSERT INTO training_modules ({cols}) VALUES ({placeholders})", _module_to_row(d))
        db.commit()
    finally:
        db.close()
    return d


def update_module(
    module_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    category: str | None = None,
    is_required: bool | None = None,
    renewal_period_days: int | None = None,
    control_ids: str | None = None,
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM training_modules WHERE id = ?", (module_id,)).fetchone()
        if not row:
            return None
        m = _row_to_module(row)

        if title is not None:
            m["title"] = title
        if description is not None:
            m["description"] = description
        if category is not None:
            m["category"] = category
        if is_required is not None:
            m["is_required"] = is_required
        if renewal_period_days is not None:
            m["renewal_period_days"] = renewal_period_days
        if control_ids is not None:
            m["control_ids"] = control_ids

        m["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _MODULE_COLS[1:])
        db.execute(
            f"UPDATE training_modules SET {set_clause} WHERE id = ?",
            _module_to_row(m)[1:] + [m["id"]],
        )
        db.commit()
        return m
    finally:
        db.close()


def delete_module(module_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM training_modules WHERE id = ?", (module_id,))
        db.execute("DELETE FROM training_assignments WHERE module_id = ?", (module_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Assignments CRUD ────────────────


def list_assignments(
    module_id: str | None = None,
    status: str | None = None,
    person_id: str | None = None,
) -> list[dict]:
    db = _get_db()
    try:
        conditions: list[str] = []
        params: list[str] = []
        if module_id:
            conditions.append("module_id = ?")
            params.append(module_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if person_id:
            conditions.append("person_id = ?")
            params.append(person_id)
        sql = "SELECT * FROM training_assignments"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        rows = [dict(r) for r in db.execute(sql, params).fetchall()]
        return _enrich_assignments(rows)
    finally:
        db.close()


def get_assignment(assignment_id: str) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM training_assignments WHERE id = ?", (assignment_id,)).fetchone()
        if not row:
            return None
        a = dict(row)
        name_data = _get_person_name(a.get("person_id", ""))
        a.update(name_data)
        return a
    finally:
        db.close()


def create_assignment(
    module_id: str,
    person_id: str,
    assigned_date: str = "",
) -> dict:
    now = utcnow()
    a = TrainingAssignment(
        id=uuid4().hex[:12],
        module_id=module_id,
        person_id=person_id,
        status="assigned",
        assigned_date=assigned_date or now[:10],
        created_at=now,
        updated_at=now,
    )
    d = a.to_dict()
    db = _get_db()
    try:
        placeholders = ", ".join(["?"] * len(_ASSIGNMENT_COLS))
        cols = ", ".join(_ASSIGNMENT_COLS)
        db.execute(f"INSERT INTO training_assignments ({cols}) VALUES ({placeholders})", _assignment_to_row(d))
        db.commit()
    finally:
        db.close()
    name_data = _get_person_name(person_id)
    d.update(name_data)
    return d


def create_bulk_assignments(
    module_id: str,
    person_ids: list[str],
    assigned_date: str = "",
) -> list[dict]:
    results = []
    for pid in person_ids:
        try:
            results.append(create_assignment(module_id, pid, assigned_date))
        except Exception:
            pass
    return results


def update_assignment(
    assignment_id: str,
    *,
    status: str | None = None,
    completion_date: str | None = None,
    expiry_date: str | None = None,
    evidence_id: str | None = None,
    notes: str | None = None,
    exemption_reason: str | None = None,
    exempted_by: str | None = None,
    exempted_date: str | None = None,
) -> dict | None:
    db = _get_db()
    try:
        row = db.execute("SELECT * FROM training_assignments WHERE id = ?", (assignment_id,)).fetchone()
        if not row:
            return None
        a = dict(row)

        if status is not None:
            a["status"] = status
        if completion_date is not None:
            a["completion_date"] = completion_date
        if expiry_date is not None:
            a["expiry_date"] = expiry_date
        if evidence_id is not None:
            a["evidence_id"] = evidence_id
        if notes is not None:
            a["notes"] = notes
        if exemption_reason is not None:
            a["exemption_reason"] = exemption_reason
        if exempted_by is not None:
            a["exempted_by"] = exempted_by
        if exempted_date is not None:
            a["exempted_date"] = exempted_date

        a["updated_at"] = utcnow()
        set_clause = ", ".join(f"{c} = ?" for c in _ASSIGNMENT_COLS[1:])
        db.execute(
            f"UPDATE training_assignments SET {set_clause} WHERE id = ?",
            _assignment_to_row(a)[1:] + [a["id"]],
        )
        db.commit()
        name_data = _get_person_name(a.get("person_id", ""))
        a.update(name_data)
        return a
    finally:
        db.close()


def bulk_complete_assignments(assignment_ids: list[str], completion_date: str) -> int:
    db = _get_db()
    try:
        now = utcnow()
        updated = 0
        for aid in assignment_ids:
            row = db.execute("SELECT * FROM training_assignments WHERE id = ?", (aid,)).fetchone()
            if not row:
                continue
            a = dict(row)
            a["status"] = "completed"
            a["completion_date"] = completion_date
            a["updated_at"] = now

            m = db.execute("SELECT renewal_period_days FROM training_modules WHERE id = ?", (a.get("module_id", ""),)).fetchone()
            if m:
                try:
                    from datetime import datetime, timedelta
                    cd = datetime.strptime(completion_date[:10], "%Y-%m-%d")
                    expiry = cd + timedelta(days=m["renewal_period_days"])
                    a["expiry_date"] = expiry.strftime("%Y-%m-%d")
                except ValueError:
                    pass

            set_clause = ", ".join(f"{c} = ?" for c in _ASSIGNMENT_COLS[1:])
            db.execute(
                f"UPDATE training_assignments SET {set_clause} WHERE id = ?",
                _assignment_to_row(a)[1:] + [a["id"]],
            )
            updated += 1
        db.commit()
        return updated
    finally:
        db.close()


def delete_assignment(assignment_id: str) -> bool:
    db = _get_db()
    try:
        cur = db.execute("DELETE FROM training_assignments WHERE id = ?", (assignment_id,))
        db.commit()
        return cur.rowcount > 0
    finally:
        db.close()


# ─── Stats ────────────────────────────


def get_stats() -> dict:
    db = _get_db()
    try:
        modules = [dict(r) for r in db.execute("SELECT * FROM training_modules").fetchall()]
        assignments = [dict(r) for r in db.execute("SELECT * FROM training_assignments").fetchall()]
    finally:
        db.close()

    total_modules = len(modules)
    total_assignments = len(assignments)

    per_module: dict[str, dict] = {}
    for a in assignments:
        mid = a.get("module_id", "")
        if mid not in per_module:
            per_module[mid] = {"module_id": mid, "total": 0, "completed": 0, "overdue": 0, "exempt": 0}
        per_module[mid]["total"] += 1
        s = a.get("status", "")
        if s == "completed":
            per_module[mid]["completed"] += 1
        elif s == "overdue":
            per_module[mid]["overdue"] += 1
        elif s == "exempt":
            per_module[mid]["exempt"] += 1

    for m_data in per_module.values():
        t = m_data["total"]
        m_data["rate"] = round(m_data["completed"] / t, 2) if t else 0.0

    completed = sum(1 for a in assignments if a.get("status") == "completed")
    overdue = sum(1 for a in assignments if a.get("status") == "overdue")
    exempt = sum(1 for a in assignments if a.get("status") == "exempt")
    completion_rate = round(completed / total_assignments, 2) if total_assignments else 0.0

    # Per-person stats
    person_stats: dict[str, dict] = {}
    for a in assignments:
        pid = a.get("person_id", "")
        if pid not in person_stats:
            person_stats[pid] = {"person_id": pid, "total": 0, "completed": 0, "overdue": 0}
        person_stats[pid]["total"] += 1
        s = a.get("status", "")
        if s == "completed":
            person_stats[pid]["completed"] += 1
        elif s == "overdue":
            person_stats[pid]["overdue"] += 1
    for p_data in person_stats.values():
        t = p_data["total"]
        p_data["rate"] = round(p_data["completed"] / t, 2) if t else 0.0
        name_data = _get_person_name(p_data["person_id"])
        p_data.update(name_data)

    return {
        "total_modules": total_modules,
        "total_assignments": total_assignments,
        "completed": completed,
        "overdue": overdue,
        "exempt": exempt,
        "completion_rate": completion_rate,
        "per_module": list(per_module.values()),
        "per_person": list(person_stats.values()),
    }


# ─── Auto-assign ─────────────────────


def auto_assign_for_person(person_id: str) -> int:
    db = _get_db()
    try:
        modules = [dict(r) for r in db.execute("SELECT * FROM training_modules WHERE is_required = 1").fetchall()]
        created = 0
        now = utcnow()
        for m in modules:
            existing = db.execute(
                "SELECT id FROM training_assignments WHERE module_id = ? AND person_id = ?",
                (m["id"], person_id),
            ).fetchone()
            if existing:
                continue
            a = TrainingAssignment(
                id=uuid4().hex[:12],
                module_id=m["id"],
                person_id=person_id,
                status="assigned",
                assigned_date=now[:10],
                created_at=now,
                updated_at=now,
            )
            d = a.to_dict()
            placeholders = ", ".join(["?"] * len(_ASSIGNMENT_COLS))
            cols = ", ".join(_ASSIGNMENT_COLS)
            db.execute(f"INSERT INTO training_assignments ({cols}) VALUES ({placeholders})", _assignment_to_row(d))
            created += 1
        db.commit()
        return created
    finally:
        db.close()


def auto_assign_all() -> dict:
    created = 0
    skipped = 0
    try:
        from personnel.store import list_personnel
        all_people = list_personnel(status="active") or []
    except Exception:
        return {"created": 0, "skipped": 0, "error": "Cannot access personnel store"}

    for p in all_people:
        try:
            c = auto_assign_for_person(p["id"])
            created += c
        except Exception:
            skipped += 1
    return {"created": created, "skipped": skipped}


# ─── Alerts ──────────────────────────


def get_alerts() -> dict:
    from datetime import datetime, timedelta
    today = datetime.utcnow().strftime("%Y-%m-%d")
    soon = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

    db = _get_db()
    try:
        rows = [dict(r) for r in db.execute(
            "SELECT * FROM training_assignments WHERE status != 'exempt' AND expiry_date != ''"
        ).fetchall()]
    finally:
        db.close()

    overdue: list[dict] = []
    expiring_soon: list[dict] = []
    for a in rows:
        exp = a.get("expiry_date", "")
        if not exp or exp[:10] > soon:
            continue
        name_data = _get_person_name(a.get("person_id", ""))
        a.update(name_data)
        m = get_module(a.get("module_id", ""))
        a["module_title"] = m["title"] if m else "Unknown"

        if exp[:10] < today:
            overdue.append(a)
        elif exp[:10] >= today and exp[:10] <= soon:
            expiring_soon.append(a)

    overdue.sort(key=lambda x: x.get("expiry_date", ""))
    expiring_soon.sort(key=lambda x: x.get("expiry_date", ""))

    return {
        "overdue_count": len(overdue),
        "overdue": overdue[:10],
        "expiring_soon_count": len(expiring_soon),
        "expiring_soon": expiring_soon[:10],
    }
