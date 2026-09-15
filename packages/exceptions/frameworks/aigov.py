from .base import FrameworkConfig

AI_GOV = FrameworkConfig(
    name="aigov",
    display_name="AI Governance",
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

# Alias for display
AI_GOV_ALIASES = {
    "AI Gov": "aigov",
    "AI Governance": "aigov",
    "EU AI Act": "aigov",
    "eu_ai_act": "aigov",
    "NIST AI RMF": "aigov",
    "nist_ai_rmf": "aigov",
    "ISO 42001": "aigov",
    "iso_42001": "aigov",
}
