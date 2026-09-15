from dataclasses import dataclass, asdict
from datetime import datetime, timezone


AUDIT_ACTIONS = [
    "created", "updated", "deleted", "approved", "rejected",
    "submitted", "reviewed", "commented", "exported", "imported",
    "evidence_uploaded", "evidence_deleted", "evidence_reviewed",
    "control_updated", "status_changed", "attested",
    "deployed", "classified", "notified", "frozen",
]

AUDIT_RESOURCE_TYPES = [
    "control", "policy", "exception", "vendor", "system", "incident",
    "evidence", "finding", "risk", "remediation", "fria",
    "assessment", "audit_period", "change_request", "organization",
    "user", "membership", "setting",
]


@dataclass
class AuditEntry:
    id: str
    action: str
    resource_type: str
    resource_id: str
    resource_name: str
    user: str
    timestamp: str
    details: str
    framework: str
    source: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "AuditEntry":
        return AuditEntry(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
