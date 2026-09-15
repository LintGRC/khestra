from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


RISK_CATEGORIES = ["security", "privacy", "operational", "compliance", "reputational", "strategic", "financial", "third_party"]
RISK_STATUSES = ["identified", "assessed", "in_treatment", "mitigated", "accepted", "monitoring", "closed"]
RISK_TREATMENTS = ["mitigate", "accept", "transfer", "avoid"]


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class RiskComment:
    id: str
    author: str
    body: str
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "RiskComment":
        return RiskComment(**d)


@dataclass
class RiskItem:
    id: str
    title: str
    description: str = ""
    category: str = ""
    framework: str = ""
    control_ids: list[str] = field(default_factory=list)
    system_id: str = ""
    owner: str = ""
    status: str = "identified"
    likelihood: int = 0
    impact: int = 0
    inherent_score: int = 0
    residual_likelihood: int = 0
    residual_impact: int = 0
    residual_score: int = 0
    treatment: str = ""
    treatment_plan: str = ""
    mitigation_evidence: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    framework_metadata: dict = field(default_factory=dict)
    comments: list[RiskComment] = field(default_factory=list)
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["comments"] = [c.to_dict() for c in self.comments]
        return d

    @staticmethod
    def from_dict(d: dict) -> "RiskItem":
        comments = [RiskComment.from_dict(c) for c in d.pop("comments", [])]
        return RiskItem(**d, comments=comments)
