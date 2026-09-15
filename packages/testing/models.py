from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


CONTROL_TEST_STATUSES = ["not_tested", "pass", "fail", "needs_review"]
TEST_FREQUENCIES = ["once", "daily", "weekly", "monthly", "quarterly", "annual", "continuous"]
TEST_RESULTS = ["pass", "fail", "needs_review"]


@dataclass
class ControlTest:
    id: str
    control_id: str
    framework: str
    test_procedure: str
    frequency: str = ""
    sample_size: int = 0
    sampling_methodology: str = ""
    population_size: int = 0
    confidence_level: float = 0.0
    margin_of_error: float = 0.0
    last_tested: str = ""
    next_test_due: str = ""
    status: str = "not_tested"
    tested_by: str = ""
    evidence_id: str = ""
    notes: str = ""
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "ControlTest":
        return ControlTest(**d)


@dataclass
class TestResult:
    id: str
    test_id: str
    result: str
    tested_by: str
    tested_at: str
    evidence_id: str = ""
    notes: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "TestResult":
        return TestResult(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
