"""SSP Appendix Starter Pack — zip download for the app."""

from __future__ import annotations

from pathlib import Path

from appendix_pack_builder import OUT_DIR, build_appendix_pack_zip, generate_all

PACK_DIR = OUT_DIR


def get_appendix_pack_zip() -> bytes:
    """Return zip of all four appendix shells + README."""
    if not (PACK_DIR / "IR_Plan_Outline.docx").exists():
        generate_all(PACK_DIR)
    return build_appendix_pack_zip(PACK_DIR)
