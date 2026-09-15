"""Family-level progress badges for the Assessment view."""

from typing import Any, Dict, List

import html

from controls import CMMC_FRAMEWORK

# Same statuses that count as SPRS gaps (see sprs_engine.py).
_OPEN_GAP_STATUSES = frozenset(
    {"NOT MET", "NOT STARTED", "PLANNED", "IN PROGRESS", "PARTIALLY MET"}
)


def _family_rows(answers: Dict[str, Any], scoped_controls: List[str]) -> List[dict]:
    families: Dict[str, dict] = {}
    for cid in scoped_controls:
        fam = CMMC_FRAMEWORK[cid]["family"]
        row = families.setdefault(
            fam,
            {"family": fam, "total": 0, "met": 0, "reviewed": 0, "open_gaps": 0},
        )
        row["total"] += 1
        status = answers.get(cid, {}).get("status", "NOT STARTED")
        if status == "MET":
            row["met"] += 1
        if status != "NOT STARTED":
            row["reviewed"] += 1
        if status in _OPEN_GAP_STATUSES:
            row["open_gaps"] += 1
    out = []
    for row in families.values():
        row["pct"] = round(100 * row["met"] / row["total"]) if row["total"] else 0
        row["complete"] = row["open_gaps"] == 0 and row["total"] > 0
        out.append(row)
    return sorted(out, key=lambda r: r["family"])


def _short_family_label(family: str) -> str:
    label = family.replace(" and ", " & ")
    if len(label) > 28:
        return label[:26] + "…"
    return label


def _chip_html(row: dict) -> str:
    label = _short_family_label(row["family"])
    meta = f'{row["met"]}/{row["total"]} MET · {row["reviewed"]} reviewed'
    open_label = f'{row["open_gaps"]} open'
    return (
        f'<div class="family-progress-chip attention">'
        f'<span class="fp-label">{html.escape(label)}</span>'
        f'<span class="fp-open">{open_label}</span>'
        f'<span class="fp-meta">{html.escape(meta)}</span></div>'
    )


def _render_chip_grid(chips: List[str]) -> None:
    import streamlit as st

    st.markdown(
        '<div class="family-progress-grid">'
        f'{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def render_family_badges(answers: Dict[str, Any], scoped_controls: List[str]) -> None:
    import streamlit as st

    rows = _family_rows(answers, scoped_controls)
    if not rows:
        return

    needs_attention = sorted(
        (r for r in rows if r["open_gaps"] > 0),
        key=lambda r: (-r["open_gaps"], r["family"]),
    )
    complete = [r for r in rows if r["open_gaps"] == 0]

    if needs_attention:
        st.markdown("**By family**")
        _render_chip_grid([_chip_html(r) for r in needs_attention])
        if complete:
            n = len(complete)
            word = "family is" if n == 1 else "families are"
            st.caption(f"{n} other control {word} complete — listed in the table below.")
    else:
        st.success("All control families are complete — no open SPRS gaps.")


def render_family_progress_table(answers: Dict[str, Any], scoped_controls: List[str]) -> None:
    """Full family list for SPRS details — includes complete and in-progress families."""
    import streamlit as st

    rows = _family_rows(answers, scoped_controls)
    if not rows:
        return

    table_rows = []
    for row in sorted(rows, key=lambda r: (-r["open_gaps"], r["family"])):
        if row["open_gaps"] == 0:
            status = "Complete"
        elif row["open_gaps"] == 1:
            status = "1 open gap"
        else:
            status = f'{row["open_gaps"]} open gaps'
        table_rows.append(
            {
                "Family": row["family"],
                "MET": row["met"],
                "Total": row["total"],
                "Open gaps": row["open_gaps"],
                "Status": status,
            }
        )

    st.markdown("**All families**")
    st.caption("Full checklist — MET totals and open-gap count per family.")
    st.dataframe(table_rows, use_container_width=True, hide_index=True)


# Legacy import path — app.render_family_progress delegates here.
