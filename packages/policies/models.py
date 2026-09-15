from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone


@dataclass
class PolicySection:
    id: str
    title: str
    content: str
    framework_tags: list[str] = field(default_factory=list)
    mapped_controls: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "PolicySection":
        return PolicySection(**d)


@dataclass
class PolicyDocument:
    id: str
    title: str
    description: str
    content: str
    version: int
    status: str  # draft, under_review, approved, published, archived
    owner: str
    framework_tags: list[str] = field(default_factory=list)
    mapped_controls: dict[str, list[str]] = field(default_factory=dict)
    sections: list[PolicySection] = field(default_factory=list)
    change_notes: str = ""
    workspace_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    approved_by: str = ""
    approved_at: str = ""
    rejection_notes: str = ""
    review_cadence_days: int = 365
    next_review_date: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["sections"] = [s.to_dict() for s in self.sections]
        return d

    @staticmethod
    def from_dict(d: dict) -> "PolicyDocument":
        sections = [PolicySection.from_dict(s) for s in d.pop("sections", [])]
        return PolicyDocument(**d, sections=sections)


@dataclass
class PolicyVersion:
    id: str
    policy_id: str
    version: int
    content: str
    title: str
    description: str
    change_notes: str
    created_by: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "PolicyVersion":
        return PolicyVersion(**d)


@dataclass
class PolicyAttestation:
    id: str
    policy_id: str
    user_name: str
    acknowledged: bool
    date: str
    notes: str = ""
    user_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "PolicyAttestation":
        return PolicyAttestation(**d)


@dataclass
class PolicyMapping:
    id: str
    policy_id: str
    framework: str
    control_id: str
    control_label: str = ""
    mapped_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "PolicyMapping":
        return PolicyMapping(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
