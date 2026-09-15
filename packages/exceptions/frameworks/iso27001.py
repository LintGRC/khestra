from .base import FrameworkConfig

ISO27001 = FrameworkConfig(
    name="iso 27001",
    display_name="ISO 27001",
    states=[
        "draft", "open", "pending_approval", "approved",
        "rejected", "expired", "closed",
    ],
    transitions={
        "draft": ["open"],
        "open": ["pending_approval", "closed", "expired"],
        "pending_approval": ["approved", "rejected", "open"],
        "approved": ["closed", "expired", "open"],
        "expired": ["open"],
        "rejected": [],
        "closed": [],
    },
)

# Exceptions frontend sends the display spelling "ISO 27001"; the registry
# lowercases unaliased names, so map every variant to the builtin key.
ISO27001_ALIASES = {
    "ISO 27001": "iso 27001",
    "ISO27001": "iso 27001",
    "iso27001": "iso 27001",
    "iso 27001": "iso 27001",
    "ISO 27001:2022": "iso 27001",
}
