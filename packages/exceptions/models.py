from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone


EXCEPTION_STATUSES = [
    "open", "pending_approval", "approved", "rejected", "expired", "closed"
]

RISK_LEVELS = ["low", "medium", "high", "critical"]

FRAMEWORKS = ["CMMC", "SOC2", "AI Gov", "NIST 800-171", "ISO 27001",
              "EU AI Act", "NIST AI RMF", "ISO 42001", "GDPR", "HIPAA", "PCI-DSS"]


@dataclass
class Attachment:
    id: str
    filename: str
    stored_as: str
    uploaded_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Attachment":
        return Attachment(**d)


@dataclass
class ExceptionComment:
    id: str
    author: str
    body: str
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "ExceptionComment":
        return ExceptionComment(**d)


@dataclass
class ExceptionHistoryEntry:
    id: str = ""
    timestamp: str = ""
    action: str = ""
    notes: str = ""
    detail: str = ""
    performed_by: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "ExceptionHistoryEntry":
        return ExceptionHistoryEntry(**d)


@dataclass
class ExceptionItem:
    id: str
    title: str
    description: str
    org_id: str = ""
    workspace_id: str = ""
    framework: str = ""
    control_id: str = ""
    control_reference: str = ""
    status: str = "open"
    risk_level: str = "medium"
    likelihood: int = 0
    impact: int = 0
    compensating_controls: str = ""
    risk_acceptance: str = ""
    owner: str = ""
    created_by: str = ""
    approved_by: str = ""
    expiry_date: str = ""
    expiry_days: int = 0
    approval_notes: str = ""
    notes: str = ""
    model_id: str = ""
    risk_assessment: dict | None = None
    extension_log: list[dict] = field(default_factory=list)
    relationships: dict = field(default_factory=dict)
    comments: list[ExceptionComment] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)
    history: list[ExceptionHistoryEntry] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["comments"] = [c.to_dict() for c in self.comments]
        d["attachments"] = [a.to_dict() for a in self.attachments]
        d["history"] = [h.to_dict() for h in self.history]
        return d

    @staticmethod
    def from_dict(d: dict) -> "ExceptionItem":
        comments = [ExceptionComment.from_dict(c) for c in d.pop("comments", [])]
        attachments = [Attachment.from_dict(a) for a in d.pop("attachments", [])]
        history = [ExceptionHistoryEntry.from_dict(h) for h in d.pop("history", [])]
        return ExceptionItem(**d, comments=comments, attachments=attachments, history=history)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_risk_score(likelihood: int, impact: int) -> int:
    return likelihood * impact


def compute_risk_level(score: int) -> str:
    if score >= 15: return "critical"
    if score >= 10: return "high"
    if score >= 5: return "medium"
    return "low"


def compute_risk_color(level: str) -> str:
    return {"critical": "#b91c1c", "high": "#dc2626", "medium": "#a16207", "low": "#15803d"}.get(level, "#64748b")


def compute_score_from_assessment(ra: dict) -> dict:
    method = ra.get("method", "likelihood_impact")
    if method == "likelihood_impact":
        likelihood = ra.get("likelihood", ra.get("score", 1))
        impact = ra.get("impact", 1)
        score_val = likelihood * impact
    else:
        score_val = ra.get("score", 1)
        likelihood = ra.get("likelihood", 1)
        impact = ra.get("impact", 1)
    level = compute_risk_level(score_val)
    return {
        "score": score_val,
        "likelihood": likelihood,
        "impact": impact,
        "level": level,
        "color": compute_risk_color(level),
        "residual": ra.get("residual", ""),
        "rationale": ra.get("rationale", ""),
        "method": method,
    }


def build_enriched(exc: dict) -> dict:
    ra = exc.get("risk_assessment")
    if ra:
        score_data = compute_score_from_assessment(ra)
        score = score_data["score"]
        level = score_data["level"]
    else:
        likelihood = exc.get("likelihood", 1)
        impact = exc.get("impact", 1)
        score = compute_risk_score(likelihood, impact)
        level = compute_risk_level(score)
    expires = None
    days_left = 0
    is_expired = False
    if exc.get("created_at") and exc.get("expiry_days"):
        try:
            from datetime import timedelta
            created = datetime.fromisoformat(exc["created_at"].replace("Z", "+00:00"))
            expires = (created + timedelta(days=int(exc["expiry_days"]))).isoformat()
            now = datetime.now(timezone.utc)
            expiry_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
            days_left = max(0, (expiry_dt - now).days)
            is_expired = expiry_dt < now
        except (ValueError, TypeError):
            pass
    elif exc.get("expiry_date") and exc.get("created_at"):
        try:
            from datetime import timedelta
            created = datetime.fromisoformat(exc["created_at"].replace("Z", "+00:00"))
            expiry_dt = datetime.fromisoformat(exc["expiry_date"].replace("Z", "+00:00"))
            expiry_days = (expiry_dt - created).days
            exc["expiry_days"] = max(1, expiry_days)
            expires = exc["expiry_date"]
            now = datetime.now(timezone.utc)
            days_left = max(0, (expiry_dt - now).days)
            is_expired = expiry_dt < now
        except (ValueError, TypeError):
            pass
    return {
        **exc,
        "risk_score": score,
        "risk_level": level,
        "risk_color": compute_risk_color(level),
        "expires_at": expires,
        "days_left": days_left,
        "is_expired": is_expired,
    }
