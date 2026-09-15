"""AI Governance collector integration — maps checks to AI framework controls.

Degrades to an empty mapping when the closed `khestra-collectors` package is
absent (`docs/OPEN_CORE_SPLIT.md` §4.3).
"""

from __future__ import annotations

from kevidence.availability import collectors_available

if collectors_available():
    from collectors.attach_registry import register_control_mapper
    from collectors.posture import register_posture_source
    from .mapping import ai_controls_for_check

    register_control_mapper(ai_controls_for_check)

    def _aigov_attested_map():
        """Attested control statuses from the AI Governance workspace (one load)."""
        try:
            from workspace_service import load_workspace

            ws = load_workspace()
            return {
                cid: (ans.get("status") or None)
                for cid, ans in (ws.get("answers") or {}).items()
            }
        except Exception:
            return {}

    def _aigov_control_names():
        try:
            from ai_controls_catalog import AI_GOV_FRAMEWORK

            return {cid: (entry.get("title") or None) for cid, entry in AI_GOV_FRAMEWORK.items()}
        except Exception:
            return {}

    register_posture_source("aigov", _aigov_attested_map, name_map_fn=_aigov_control_names)

else:

    def ai_controls_for_check(check_id: str):
        """No-op mapping when the collectors package is not installed."""
        return []


__all__ = ["ai_controls_for_check"]
