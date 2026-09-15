"""Shared remediation item data model — framework-agnostic task definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_remediation_id() -> str:
    return uuid4().hex[:12]


RemediationType = str
# Standard types shared across frameworks
REMEDIATION_TYPES: List[RemediationType] = [
    "gap",
    "finding",
    "exception",
    "risk",
    "corrective_action",
    "vendor_remediation",
    "poam_entry",
    "milestone",
]


def framework_labels(framework_id: str) -> Dict[str, str]:
    """Maps standard remediation types to framework-specific labels for the UI."""
    labels: Dict[str, Dict[str, str]] = {
        "cmmc": {
            "gap": "Open Gap",
            "poam_entry": "POA&M Entry",
            "milestone": "Milestone",
            "finding": "Assessment Finding",
            "exception": "Exception",
        },
        "soc2": {
            "finding": "Audit Finding",
            "exception": "Policy Exception",
            "risk": "Risk Register Item",
            "gap": "Control Gap",
        },
        "aigovernance": {
            "corrective_action": "Corrective Action",
            "exception": "AI Policy Waiver",
            "vendor_remediation": "Vendor Remediation",
            "gap": "Coverage Gap",
        },
    }
    return labels.get(framework_id, {})


def framework_types(framework_id: str) -> List[str]:
    return list(framework_labels(framework_id).keys())


@dataclass
class RemediationItem:
    """A single remediation item, adaptable to any framework's view."""

    id: str = field(default_factory=new_remediation_id)
    framework: str = ""  # cmmc | soc2 | aigovernance
    type: str = "gap"  # see REMEDIATION_TYPES
    title: str = ""
    description: str = ""
    status: str = "open"  # open | in_progress | closed | pending_approval | rejected
    priority: str = "medium"  # low | medium | high | critical
    severity: str = "medium"
    owner: str = ""
    source_id: str = ""  # ID of the original record in the source app
    control_id: str = ""  # Mapped control ID
    framework_ref: str = ""  # Framework-specific control reference (e.g., "AC.L2-3.1.1")
    target_date: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "framework": self.framework,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "severity": self.severity,
            "owner": self.owner,
            "source_id": self.source_id,
            "control_id": self.control_id,
            "framework_ref": self.framework_ref,
            "target_date": self.target_date,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemediationItem":
        return cls(
            id=data.get("id", new_remediation_id()),
            framework=data.get("framework", ""),
            type=data.get("type", "gap"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=data.get("status", "open"),
            priority=data.get("priority", "medium"),
            severity=data.get("severity", "medium"),
            owner=data.get("owner", ""),
            source_id=data.get("source_id", ""),
            control_id=data.get("control_id", ""),
            framework_ref=data.get("framework_ref", ""),
            target_date=data.get("target_date"),
            completed_at=data.get("completed_at"),
            created_at=data.get("created_at", _now()),
            updated_at=data.get("updated_at", _now()),
            metadata=data.get("metadata", {}),
        )
