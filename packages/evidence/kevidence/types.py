"""Shared types for the evidence layer (open side)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional

CheckStatus = Literal["pass", "fail", "warn", "error"]


@dataclass
class CheckResult:
    check_id: str
    check_name: str
    status: CheckStatus
    evidence: str
    detail: str
    collected_at: str
    raw_response: Dict[str, Any] | None = None
    remediation: str = ""
    console_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CollectorRunResult:
    connector_id: str
    started_at: str
    completed_at: str
    checks: List[CheckResult]
    summary: str
    fixture: bool = False
    monitor_run_id: Optional[str] = None
    drift_events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "summary": self.summary,
            "fixture": self.fixture,
            "monitor_run_id": self.monitor_run_id,
            "drift_events": self.drift_events,
            "checks": [c.to_dict() for c in self.checks],
        }


@dataclass
class AttachResult:
    control_id: str
    filename: str
    sha256: str
    check_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunAndAttachResult:
    run: CollectorRunResult
    attached: List[AttachResult] = field(default_factory=list)
    monitor_run_id: Optional[str] = None
    drift_events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run": self.run.to_dict(),
            "attached": [a.to_dict() for a in self.attached],
            "monitor_run_id": self.monitor_run_id,
            "drift_events": self.drift_events,
        }
