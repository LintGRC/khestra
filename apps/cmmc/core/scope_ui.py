"""Assessment scope (CUI %) — belongs on Organization, not buried in Tools."""

from typing import Callable, Dict, List

from controls import CMMC_FRAMEWORK


def default_asset_scope(asset_types: Dict[str, str]) -> Dict[str, int]:
    """Most users handle CUI — default full Level 2 scope; they still click Apply scope to confirm."""
    return {name: (100 if name == "CUI Assets" else 0) for name in asset_types}


def apply_scope_from_assets(asset_scope: Dict[str, int]) -> List[str]:
    cui = asset_scope.get("CUI Assets", 0)
    if cui == 0:
        return [c for c in CMMC_FRAMEWORK if "CUI" not in CMMC_FRAMEWORK[c]["name"]]
    return list(CMMC_FRAMEWORK.keys())


def render_assessment_scope(
    asset_scope: Dict[str, int],
    asset_types: Dict[str, str],
    scoped_controls: List[str],
    on_save: Callable[[], None],
) -> None:
    import streamlit as st

    st.markdown("### Assessment scope")
    st.caption(
        "Each field is **percent of your in-scope environment** (0–100), not a count. "
        "Most subcontractors set **CUI Assets** to **100%**, then click **Apply scope** for all 110 controls."
    )

    changed = False
    cols = st.columns(2)
    items = list(asset_types.items())
    for i, (asset, desc) in enumerate(items):
        with cols[i % 2]:
            val = asset_scope.get(asset, 0)
            new_val = st.number_input(
                f"{asset} (%)",
                min_value=0,
                max_value=100,
                value=val,
                step=5,
                key=f"org_scope_{asset}",
                help=f"{desc}. Enter 0–100 (percent), not a headcount.",
            )
            if new_val != val:
                asset_scope[asset] = new_val
                changed = True

    if st.button("Apply scope", key="org_apply_scope", type="primary"):
        st.session_state.scoped_controls = apply_scope_from_assets(st.session_state.asset_scope)
        st.session_state.scope_confirmed = True
        on_save()
        st.rerun()
    elif changed:
        st.caption("Adjust percentages, then click **Apply scope**.")

    st.info(f"**{len(scoped_controls)}** of {len(CMMC_FRAMEWORK)} controls in scope for this assessment.")
