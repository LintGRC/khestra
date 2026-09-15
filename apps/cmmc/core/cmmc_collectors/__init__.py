"""CMMC-specific collector helpers (mapping, attach, narratives, freshness).

The closed `khestra-collectors` package is optional (`docs/OPEN_CORE_SPLIT.md`
§4.3): when it is absent this module degrades to an empty mapping so the app
boots in manual mode.
"""

from __future__ import annotations

from kevidence.availability import collectors_available

if collectors_available():
    from collectors.attach_registry import register_control_mapper
    from collectors.posture import register_posture_source
    from cmmc_collectors.mapping import controls_for_check

    register_control_mapper(controls_for_check)

    def _cmmc_attested_map():
        """Attested control statuses from the CMMC workspace answers (one load)."""
        try:
            from workspace_service import load_workspace

            ws = load_workspace()
            return {
                cid: (ans.get("status") or None)
                for cid, ans in (ws.get("answers") or {}).items()
            }
        except Exception:
            return {}

    def _cmmc_control_names():
        try:
            from controls import CMMC_FRAMEWORK

            return {cid: (entry.get("name") or None) for cid, entry in CMMC_FRAMEWORK.items()}
        except Exception:
            return {}

    register_posture_source("cmmc", _cmmc_attested_map, name_map_fn=_cmmc_control_names)

else:

    def controls_for_check(check_id: str):
        """No-op mapping when the collectors package is not installed."""
        return []


__all__ = ["controls_for_check"]
