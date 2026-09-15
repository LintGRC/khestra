from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


FINDING_SOURCES = ["audit", "assessment", "pen_test", "scanner", "incident", "vendor", "internal", "external"]
FINDING_SEVERITIES = ["critical", "high", "medium", "low", "info"]
FINDING_STATUSES = ["open", "in_progress", "in_remediation", "resolved", "verified", "closed", "dismissed"]
ACTION_STATUSES = ["open", "in_progress", "completed", "verified", "closed"]


@dataclass
class FindingItem:
    id: str
    title: str
    description: str = ""
    remediation: str = ""
    source: str = ""
    source_id: str = ""
    severity: str = "medium"
    status: str = "open"
    owner: str = ""
    framework: str = ""
    control_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "FindingItem":
        return FindingItem(**d)


@dataclass
class CorrectiveAction:
    id: str
    finding_id: str
    title: str
    description: str = ""
    owner: str = ""
    target_date: str = ""
    status: str = "open"
    completed_at: str = ""
    evidence_id: str = ""
    notes: str = ""
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "CorrectiveAction":
        return CorrectiveAction(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
