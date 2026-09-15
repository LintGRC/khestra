from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import json


TRAINING_STATUSES = ["assigned", "in_progress", "completed", "overdue", "exempt"]


@dataclass
class TrainingModule:
    id: str
    title: str
    description: str = ""
    category: str = ""
    is_required: bool = True
    renewal_period_days: int = 365
    control_ids: str = ""
    content_md: str = ""
    quiz_questions: list[dict] = field(default_factory=list)
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "TrainingModule":
        d2 = dict(d)
        d2["is_required"] = bool(d2.get("is_required", True))
        if isinstance(d2.get("quiz_questions"), str):
            try:
                d2["quiz_questions"] = json.loads(d2["quiz_questions"])
            except (json.JSONDecodeError, TypeError):
                d2["quiz_questions"] = []
        return TrainingModule(**d2)


@dataclass
class TrainingAssignment:
    id: str
    module_id: str
    person_id: str
    status: str = "assigned"
    assigned_date: str = ""
    completion_date: str = ""
    expiry_date: str = ""
    evidence_id: str = ""
    notes: str = ""
    exemption_reason: str = ""
    exempted_by: str = ""
    exempted_date: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "TrainingAssignment":
        return TrainingAssignment(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
