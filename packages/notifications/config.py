"""SMTP and email notification configuration from env vars."""

from __future__ import annotations

import os
from typing import List


def smtp_host() -> str:
    return os.environ.get("SMTP_HOST", "").strip()


def smtp_port() -> int:
    try:
        return int(os.environ.get("SMTP_PORT", "587"))
    except (ValueError, TypeError):
        return 587


def smtp_user() -> str:
    return os.environ.get("SMTP_USER", "").strip()


def smtp_password() -> str:
    return os.environ.get("SMTP_PASS", "").strip()


def smtp_from() -> str:
    return os.environ.get("SMTP_FROM", "noreply@khestra.local").strip()


def smtp_use_tls() -> bool:
    val = os.environ.get("SMTP_USE_TLS", "1").strip().lower()
    return val in ("1", "true", "yes")


def admin_notification_emails() -> List[str]:
    raw = os.environ.get("ADMIN_NOTIFICATION_EMAILS", "").strip()
    if not raw:
        return []
    return [e.strip() for e in raw.split(",") if e.strip()]


def is_email_configured() -> bool:
    return bool(smtp_host() and admin_notification_emails())
