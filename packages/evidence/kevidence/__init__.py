"""Open evidence-layer modules (open-core split §3.2).

This package is the OPEN side of the evidence layer. It must never import the
closed collectors package at module level (`docs/OPEN_CORE_CONTRACT.md` §D).
The closed package re-exports these modules for backward compatibility.
"""

from __future__ import annotations

OPEN_CORE_VERSION = "0.1.0"
