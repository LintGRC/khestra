from __future__ import annotations

from .store import get_db


def get_setting(key: str) -> str | None:
    db = get_db()
    try:
        row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None
    finally:
        db.close()


def set_setting(key: str, value: str) -> None:
    db = get_db()
    try:
        db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        db.commit()
    finally:
        db.close()


def delete_setting(key: str) -> None:
    db = get_db()
    try:
        db.execute("DELETE FROM settings WHERE key = ?", (key,))
        db.commit()
    finally:
        db.close()


def get_all_settings() -> dict[str, str]:
    db = get_db()
    try:
        rows = db.execute("SELECT key, value FROM settings").fetchall()
        return {row["key"]: row["value"] for row in rows}
    finally:
        db.close()
