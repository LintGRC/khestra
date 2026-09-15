from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


RACI_ROLES = ["Responsible", "Accountable", "Consulted", "Informed"]

RACI_WEIGHTS = {
    "Responsible": "R — does the work",
    "Accountable": "A — owns the outcome",
    "Consulted": "C — provides input",
    "Informed": "I — kept up to date",
}


@dataclass
class RaciAssignment:
    id: str
    org_id: str
    framework: str  # CMMC, SOC2, AI Gov
    ref_type: str  # control, process, system, policy
    ref_id: str  # e.g. "AC.1.001", "CC6.1", or a UUID
    user_id: str  # ID from orgs package
    user_name: str  # denormalized for convenience
    responsibility: str  # R, A, C, I
    notes: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "RaciAssignment":
        return RaciAssignment(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
