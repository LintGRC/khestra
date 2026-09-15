from .base import FrameworkConfig

SOC2 = FrameworkConfig(
    name="soc2",
    display_name="SOC 2",
    states=[
        "open", "approved", "rejected",
        "expired", "closed",
    ],
    transitions={
        "open": ["approved", "closed", "expired"],
        "approved": ["closed", "expired", "open"],
        "expired": ["open"],
        "rejected": [],
        "closed": [],
    },
)
