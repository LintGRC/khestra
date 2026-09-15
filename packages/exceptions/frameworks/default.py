from .base import FrameworkConfig

DEFAULT = FrameworkConfig(
    name="default",
    display_name="Generic",
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
