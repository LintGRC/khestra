from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


ASSET_TYPES = [
    "server", "cloud_instance", "application", "endpoint",
    "ai_model", "dataset", "api_service", "vendor_system",
    "database", "network_device", "container", "user", "other",
]

ASSET_STATUSES = ["active", "inactive", "retired", "deprecated"]


@dataclass
class AssetItem:
    id: str
    name: str
    asset_type: str = "other"
    framework_tags: list[str] = field(default_factory=list)
    owner: str = ""
    description: str = ""
    location: str = ""
    ip_address: str = ""
    hostname: str = ""
    status: str = "active"
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "AssetItem":
        return AssetItem(**d)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
