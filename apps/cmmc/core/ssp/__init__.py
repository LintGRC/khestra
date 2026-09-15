"""Modular System Security Plan (SSP) generation for CMMC / NIST SP 800-171."""

from ssp.assembler import assemble_ssp, assemble_ssp_family
from ssp.constants import FAMILY_ORDER

__all__ = ["assemble_ssp", "assemble_ssp_family", "generate_ssp", "FAMILY_ORDER"]


def generate_ssp(
    answers,
    audit_log=None,
    asset_scope=None,
    org_name: str = "Your Organization",
    template_path=None,
    scoped_controls=None,
    org_profile=None,
    org_assets=None,
    org_asset_bytes=None,
    org_inventory=None,
):
    """
    Backward-compatible entry point.

    Uses python-docx with the official CUI SSP template when present.

    Returns:
        bytes: .docx file content
    """
    profile = org_profile or {"org_name": org_name}
    return assemble_ssp(
        answers=answers,
        asset_scope=asset_scope or {},
        org_name=org_name,
        scoped_controls=scoped_controls,
        template_path=template_path,
        org_profile=profile,
        org_assets=org_assets,
        org_asset_bytes=org_asset_bytes,
        audit_log=audit_log,
        org_inventory=org_inventory,
    )
