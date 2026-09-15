from .base import FrameworkConfig

CMMC = FrameworkConfig(
    name="cmmc",
    display_name="CMMC",
    states=[
        "draft", "open", "in_progress", "completed",
        "expired", "closed",
    ],
    transitions={
        "draft": ["open"],
        "open": ["in_progress", "expired"],
        "in_progress": ["completed", "open", "expired"],
        "completed": ["closed"],
        "expired": ["open"],
        "closed": [],
    },
)
