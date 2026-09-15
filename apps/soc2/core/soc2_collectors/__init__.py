"""Register SOC 2 control mapping with shared evidence package.

Degrades to an empty mapping when the closed `khestra-collectors` package is
absent (`docs/OPEN_CORE_SPLIT.md` §4.3).
"""

from __future__ import annotations

from kevidence.availability import collectors_available

if collectors_available():
    from collectors.attach_registry import register_control_mapper
    from collectors.posture import register_posture_source
    from soc2_collectors.mapping import criteria_for_check

    register_control_mapper(criteria_for_check)

    def _soc2_attested_map():
        """Attested criterion statuses from the SOC 2 workspace answers (one load)."""
        try:
            from workspace_service import load_workspace

            ws = load_workspace()
            return {
                cid: (ans.get("status") or None)
                for cid, ans in (ws.get("answers") or {}).items()
            }
        except Exception:
            return {}

    def _soc2_control_names():
        try:
            from soc2_catalog import SOC2_CONTROLS

            return {cid: (entry.get("title") or None) for cid, entry in SOC2_CONTROLS.items()}
        except Exception:
            return {}

    register_posture_source("soc2", _soc2_attested_map, name_map_fn=_soc2_control_names)

else:

    def criteria_for_check(check_id: str):
        """No-op mapping when the collectors package is not installed."""
        return []


__all__ = ["criteria_for_check"]
