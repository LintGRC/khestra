from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone


AUDIT_STATUSES = ["planned", "in_progress", "frozen", "completed", "cancelled"]
AUDIT_TYPES = ["internal", "external", "readiness", "certification", "surveillance"]
REQUEST_STATUSES = ["open", "submitted", "approved", "rejected", "waived"]


@dataclass
class Audit:
    id: str
    title: str
    framework: str = ""
    audit_type: str = ""
    start_date: str = ""
    end_date: str = ""
    status: str = "planned"
    auditor_name: str = ""
    auditor_email: str = ""
    scope_notes: str = ""
    preparation_notes: str = ""
    control_id: str = ""
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Audit":
        return Audit(**d)


@dataclass
class EvidenceRequest:
    id: str
    audit_id: str
    title: str
    control_id: str = ""
    description: str = ""
    requested_by: str = ""
    assigned_to: str = ""
    status: str = "open"
    evidence_id: str = ""
    evidence_notes: str = ""
    due_date: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "EvidenceRequest":
        return EvidenceRequest(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
