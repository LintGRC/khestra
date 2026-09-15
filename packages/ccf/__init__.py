"""Common Control Framework — cross-framework control mapping for Khestra GRC."""

from .ccf import (
    CCFTopic,
    frameworks,
    get_ccf_topics,
    get_framework_controls,
    get_mapped_controls,
    list_frameworks,
    map_control_to_ccf,
)

__all__ = [
    "CCFTopic",
    "frameworks",
    "get_ccf_topics",
    "get_framework_controls",
    "get_mapped_controls",
    "list_frameworks",
    "map_control_to_ccf",
]
