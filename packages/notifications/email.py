"""SMTP email dispatch for notifications."""

from __future__ import annotations

import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any

from . import config


def _build_html(notification: Dict[str, Any]) -> str:
    title = notification.get("title", "")
    body = notification.get("body", "")
    link = notification.get("link", "")
    ntype = notification.get("type", "")

    html_parts = [
        "<html><body style='font-family: sans-serif; padding: 20px;'>",
        f"<h2>{_escape(title)}</h2>",
        f"<p>{_escape(body)}</p>",
    ]
    if link:
        html_parts.append(f'<p><a href="{_escape(link)}" style="background: #2563eb; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 6px;">View in Khestra</a></p>')
    html_parts.append(f"<p style='color: #888; font-size: 0.85em;'>Type: {_escape(ntype)}</p>")
    html_parts.append("</body></html>")
    return "\n".join(html_parts)


def _escape(val: str) -> str:
    return val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def send_email_notification(notification: Dict[str, Any]) -> None:
    if not config.is_email_configured():
        return

    to_addrs = config.admin_notification_emails()
    if not to_addrs:
        return

    subject = f"[Khestra] {notification.get('title', 'Notification')}"
    text_body = notification.get("body", "")
    link = notification.get("link", "")
    if link:
        text_body += f"\n\nView in Khestra: {link}"

    msg = MIMEMultipart("alternative")
    msg["From"] = config.smtp_from()
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(_build_html(notification), "html", "utf-8"))

    try:
        with smtplib.SMTP(config.smtp_host(), config.smtp_port(), timeout=15) as server:
            if config.smtp_use_tls():
                server.starttls()
            user = config.smtp_user()
            if user:
                server.login(user, config.smtp_password())
            server.sendmail(config.smtp_from(), to_addrs, msg.as_string())
    except Exception:
        print(f"Failed to send email notification: {sys.exc_info()[1]}", file=sys.stderr)
