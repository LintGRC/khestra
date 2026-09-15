from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


VENDOR_STATUSES = ["pending", "sent", "assessed", "approved", "rejected"]
RISK_LEVELS = ["low", "medium", "high", "critical"]


@dataclass
class VendorCertificate:
    id: str
    type: str = ""
    filename: str = ""
    uploaded_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "VendorCertificate":
        return VendorCertificate(**d)


FRAMEWORKS = ["SOC2", "AIGov", "CMMC"]


@dataclass
class Vendor:
    id: str
    name: str
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    website: str = ""
    product_service: str = ""
    category: str = ""
    ai_service_type: str = ""
    tier: str = ""
    status: str = "pending"
    risk_score: int | None = None
    risk_level: str | None = None
    access_token: str = ""
    tags: list[str] = field(default_factory=list)
    org_id: str = ""
    workspace_id: str = ""
    frameworks: list[str] = field(default_factory=list)
    data_residency: list[str] = field(default_factory=list)
    transfer_mechanism: str = ""
    dpa_in_place: bool = False
    certificates: list[VendorCertificate | dict] = field(default_factory=list)
    soc_report_type: str = ""
    soc_report_opinion: str = ""
    soc_report_coverage_start: str = ""
    soc_report_coverage_end: str = ""
    next_review_due: str = ""
    review_date: str = ""
    data_types: list[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["certificates"] = [
            c.to_dict() if isinstance(c, VendorCertificate) else c
            for c in self.certificates
        ]
        return d

    @staticmethod
    def from_dict(d: dict) -> "Vendor":
        certs = d.pop("certificates", [])
        v = Vendor(**d)
        v.certificates = [VendorCertificate.from_dict(c) if isinstance(c, dict) else c for c in certs]
        return v


@dataclass
class VendorResponse:
    id: str
    vendor_id: str
    questionnaire_id: str = "default"
    status: str = "draft"  # draft / submitted
    answers: list[dict] = field(default_factory=list)
    created_at: str = ""
    submitted_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "VendorResponse":
        return VendorResponse(**d)


@dataclass
class VendorAssessment:
    id: str
    vendor_id: str
    response_id: str
    overall_score: int = 0
    overall_level: str = "medium"
    category_scores: dict[str, float] = field(default_factory=dict)
    findings: list[dict] = field(default_factory=list)
    summary: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "VendorAssessment":
        return VendorAssessment(**d)


@dataclass
class VendorRemediation:
    id: str
    vendor_id: str
    assessment_id: str
    description: str = ""
    priority: str = "medium"
    status: str = "open"
    owner: str = ""
    due_date: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "VendorRemediation":
        return VendorRemediation(**d)


@dataclass
class VendorActivity:
    id: str
    vendor_id: str
    action: str = ""
    detail: str = ""
    performed_by: str = ""
    notes: str = ""
    timestamp: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "VendorActivity":
        return VendorActivity(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
