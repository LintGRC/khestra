"""ISO 27001 collector integration — maps shared collector checks to ISO 27001:2022 controls.

Degrades to an empty mapping when the closed `khestra-collectors` package is
absent (`docs/OPEN_CORE_SPLIT.md` §4.3).
"""

from __future__ import annotations

from kevidence.availability import collectors_available

if collectors_available():
    from collectors.attach_registry import register_control_mapper
    from collectors.posture import register_posture_source
    from .mapping import iso27001_controls_for_check

    register_control_mapper(iso27001_controls_for_check)

    def _iso_attested_map():
        """Attested statuses from the Statement of Applicability store (one load)."""
        try:
            from soa import list_soa

            return {row["control_id"]: (row.get("status") or None) for row in list_soa()}
        except Exception:
            return {}

    def _iso_control_names():
        try:
            from controls import ALL_CONTROLS

            return {c["id"]: (c.get("title") or None) for c in ALL_CONTROLS}
        except Exception:
            return {}

    register_posture_source("iso27001", _iso_attested_map, name_map_fn=_iso_control_names)

else:

    def iso27001_controls_for_check(check_id: str):
        """No-op mapping when the collectors package is not installed."""
        return []


__all__ = ["iso27001_controls_for_check"]
