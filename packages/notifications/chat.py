"""Slack and Microsoft Teams incoming-webhook dispatch for notifications.

Mirrors the email adapter: reads webhook URLs from env vars, POSTs a simple
payload, and swallows failures (notifications are best-effort). A notification
goes to every configured channel — users mute what they don't want.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from typing import Any, Dict


def slack_webhook_url() -> str:
    import os
    return os.environ.get("SLACK_WEBHOOK_URL", "").strip()


def teams_webhook_url() -> str:
    import os
    return os.environ.get("TEAMS_WEBHOOK_URL", "").strip()


def is_chat_configured() -> bool:
    return bool(slack_webhook_url() or teams_webhook_url())


def _format_text(notification: Dict[str, Any]) -> str:
    parts = [notification.get("title", "Khestra notification")]
    body = notification.get("body", "")
    if body:
        parts.append(body)
    link = notification.get("link", "")
    if link:
        parts.append(f"View in Khestra: {link}")
    return "\n".join(parts)


def _post(webhook_url: str, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()


def send_slack(webhook_url: str, notification: Dict[str, Any]) -> None:
    """Slack incoming webhook: {"text": "..."}."""
    _post(webhook_url, {"text": _format_text(notification)})


def send_teams(webhook_url: str, notification: Dict[str, Any]) -> None:
    """Teams incoming webhook: {"title": "...", "text": "..."}."""
    _post(
        webhook_url,
        {
            "title": notification.get("title", "Khestra notification"),
            "text": _format_text(notification),
        },
    )


def send_chat_notification(notification: Dict[str, Any]) -> None:
    """Fan out to every configured chat channel (best-effort)."""
    slack_url = slack_webhook_url()
    if slack_url:
        try:
            send_slack(slack_url, notification)
        except Exception:
            print(f"Failed to send Slack notification: {sys.exc_info()[1]}", file=sys.stderr)
    teams_url = teams_webhook_url()
    if teams_url:
        try:
            send_teams(teams_url, notification)
        except Exception:
            print(f"Failed to send Teams notification: {sys.exc_info()[1]}", file=sys.stderr)
