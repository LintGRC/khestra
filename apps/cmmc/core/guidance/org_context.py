"""Stack- and org-aware snippets for SSP starter narratives (deterministic, no AI)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from env_scope import CLOUD_LABELS, MOBILE_CONTROLS, REMOTE_CONTROLS, WIRELESS_CONTROLS
from inheritance_map import inheritance_detail_for_control

OrgProfile = Dict[str, str]
EnvScope = Dict[str, str]

_INVALID_ORG_NAMES = frozenset({"", "your organization", "organization"})
_ORG_NAME_PLACEHOLDER = "[Organization name]"


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


def org_name_valid(org_profile: OrgProfile) -> bool:
    name = _clean(org_profile.get("org_name")).lower()
    return bool(name) and name not in _INVALID_ORG_NAMES


def org_display_name(org_profile: OrgProfile) -> str:
    org = _clean(org_profile.get("org_name"))
    if org and org.lower() not in _INVALID_ORG_NAMES:
        return org
    return _ORG_NAME_PLACEHOLDER


def stack_pattern_label(env_scope: EnvScope) -> Optional[str]:
    """Short label for the active deployment pattern."""
    m365 = env_scope.get("uses_m365") == "yes"
    google = env_scope.get("uses_google") == "yes"
    cloud = env_scope.get("cloud_hosting", "")
    remote = env_scope.get("remote_workforce") == "yes"
    wireless = env_scope.get("uses_wireless") == "yes"

    if not any((m365, google, cloud, remote, wireless, env_scope.get("processes_cui"))):
        return None

    parts: List[str] = []
    if m365:
        parts.append("M365/Entra")
    if google:
        parts.append("Google Workspace")
    if cloud == "azure":
        parts.append("Azure IaaS/PaaS")
    elif cloud == "aws":
        parts.append("AWS IaaS/PaaS")
    elif cloud == "both":
        parts.append("Azure + AWS")
    elif cloud == "on_prem_only":
        parts.append("on-premises")
    if remote:
        parts.append("remote workforce")
    if wireless:
        parts.append("wireless in scope")
    elif env_scope.get("uses_wireless") == "no":
        parts.append("no corporate Wi‑Fi to CUI")

    return ", ".join(parts) if parts else None


def has_org_context(org_profile: Optional[OrgProfile], env_scope: Optional[EnvScope]) -> bool:
    profile = org_profile or {}
    env = env_scope or {}
    if stack_pattern_label(env):
        return True
    for key in ("org_name", "system_name", "system_owner", "iso_name"):
        val = _clean(profile.get(key))
        if val and val.lower() not in ("your organization", "organization"):
            return True
    return False


def stack_context_lines(org_profile: OrgProfile, env_scope: EnvScope) -> List[str]:
    """Facts drawn only from profile and environment answers."""
    lines: List[str] = []
    org = _clean(org_profile.get("org_name"))
    system = _clean(org_profile.get("system_name"))
    if org_name_valid(org_profile):
        if system:
            lines.append(f"{org} — assessed system: {system}.")
        else:
            lines.append(f"{org}.")

    owner = _clean(org_profile.get("system_owner"))
    iso = _clean(org_profile.get("iso_name"))
    if owner:
        lines.append(f"System owner: {owner}.")
    if iso:
        lines.append(f"Information security officer: {iso}.")

    pattern = stack_pattern_label(env_scope)
    if pattern:
        lines.append(f"Environment profile: {pattern}.")

    if env_scope.get("processes_cui") == "yes":
        lines.append("Organization processes CUI within the defined system boundary.")
    elif env_scope.get("processes_cui") == "no":
        lines.append("Environment profile indicates CUI is not processed — confirm assessment scope.")

    cloud = env_scope.get("cloud_hosting", "")
    if cloud and cloud not in ("", "on_prem_only"):
        lines.append(f"Cloud hosting: {CLOUD_LABELS.get(cloud, cloud)}.")

    boundary = _clean(org_profile.get("boundary_description"))
    if boundary and len(boundary) > 20:
        excerpt = boundary if len(boundary) <= 220 else boundary[:217] + "…"
        lines.append(f"System boundary (excerpt): {excerpt}")

    return lines


def _m365_snippet(control_id: str, org_profile: OrgProfile) -> Optional[str]:
    org = org_display_name(org_profile)
    snippets = {
        "IA.L2-3.5.3": (
            f"{org} requires multifactor authentication for in-scope users via Microsoft Entra ID "
            "Conditional Access. Document named policies, included user/group scope, and any "
            "documented exceptions with compensating controls."
        ),
        "IA.L2-3.5.7": (
            f"{org} enforces password complexity and authentication policy through Microsoft Entra ID. "
            "Legacy authentication is disabled where feasible; password protection and lockout settings "
            "are reviewed periodically."
        ),
        "AU.L2-3.3.1": (
            f"{org} enables Microsoft 365 unified audit logging and Entra sign-in logs for in-scope "
            "services. Retention, review cadence, and alerting are defined in organizational procedures."
        ),
        "SC.L2-3.13.8": (
            f"{org} protects transmission of CUI using TLS for Microsoft 365 and org-managed endpoints. "
            "Weak cipher suites are disabled on systems under organizational control; provider compliance "
            "artifacts supplement shared-responsibility controls."
        ),
        "SC.L2-3.13.11": (
            f"{org} uses FIPS-validated cryptographic modules where required for Microsoft cloud services "
            "and org-managed endpoints. Gaps on user devices or custom applications are documented."
        ),
    }
    return snippets.get(control_id)


def _cloud_snippet(control_id: str, env_scope: EnvScope, org_profile: OrgProfile) -> Optional[str]:
    org = org_display_name(org_profile)
    cloud = env_scope.get("cloud_hosting", "")
    snippets: Dict[str, str] = {}

    if cloud in ("azure", "both"):
        snippets.update(
            {
                "SC.L2-3.13.16": (
                    f"{org} encrypts CUI at rest in Azure using platform and/or customer-managed keys. "
                    "Storage accounts, databases, and backups in scope are inventoried with encryption settings."
                ),
                "CM.L2-3.4.1": (
                    f"{org} maintains baseline configurations for Azure VMs and PaaS workloads in the CUI "
                    "boundary. Guest OS patching and application settings are owned by the organization."
                ),
            }
        )
    if cloud in ("aws", "both"):
        snippets.update(
            {
                "SC.L2-3.13.16": (
                    f"{org} encrypts CUI at rest in AWS using KMS and service-default encryption. "
                    "Buckets, volumes, and databases in scope are inventoried with encryption configuration."
                ),
                "CM.L2-3.4.1": (
                    f"{org} maintains golden AMIs and configuration baselines for EC2/ECS workloads processing CUI. "
                    "Patch cadence and drift detection are documented."
                ),
                "CM.L2-3.4.2": (
                    f"{org} tracks configuration changes in AWS using Security Groups, launch templates, "
                    "and AWS Config rules where deployed."
                ),
                "SI.L2-3.14.6": (
                    f"{org} monitors AWS environments with GuardDuty (or equivalent) in all in-scope regions; "
                    "alerts route to incident response procedures."
                ),
            }
        )
    if cloud == "aws":
        return snippets.get(control_id)
    if cloud in ("azure", "both") and control_id in snippets:
        return snippets.get(control_id)
    return snippets.get(control_id)


def _access_snippet(control_id: str, env_scope: EnvScope, org_profile: OrgProfile) -> Optional[str]:
    org = org_display_name(org_profile)

    if control_id in REMOTE_CONTROLS and env_scope.get("remote_workforce") == "yes":
        return (
            f"{org} controls remote access to CUI systems via VPN or zero-trust remote access. "
            "Session monitoring, encryption in transit, and termination of inactive sessions are enforced."
        )
    if control_id in REMOTE_CONTROLS and env_scope.get("remote_workforce") == "no":
        return (
            f"{org} does not routinely permit remote access to CUI. If this control is Not Applicable, "
            "document the on-site-only access model and any exception process."
        )
    if control_id in WIRELESS_CONTROLS and env_scope.get("uses_wireless") == "yes":
        return (
            f"{org} secures wireless access to CUI systems with WPA2-Enterprise or WPA3, network segmentation, "
            "and monitoring of wireless infrastructure."
        )
    if control_id in WIRELESS_CONTROLS and env_scope.get("uses_wireless") == "no":
        return (
            f"{org} does not use corporate wireless for CUI access. If Not Applicable, state that CUI "
            "systems are reachable only via wired or VPN paths."
        )
    if control_id in MOBILE_CONTROLS and env_scope.get("remote_workforce") == "yes":
        return (
            f"{org} manages laptops and mobile endpoints used for CUI via MDM/Intune (or equivalent), "
            "including encryption, patch status, and remote wipe capability."
        )
    return None


def _family_snippet(family: str, env_scope: EnvScope, org_profile: OrgProfile) -> Optional[str]:
    org = org_display_name(org_profile)
    if family == "IA" and env_scope.get("uses_m365") == "yes":
        return (
            f"{org} centralizes identity for in-scope users in Microsoft Entra ID with Conditional Access, "
            "group-based assignment, and periodic access reviews."
        )
    if family == "AC" and env_scope.get("remote_workforce") == "yes":
        return (
            f"{org} limits CUI access to authorized users; remote sessions require MFA and are logged."
        )
    if family == "SC" and env_scope.get("cloud_hosting") not in ("", "on_prem_only"):
        cloud_label = CLOUD_LABELS.get(env_scope.get("cloud_hosting", ""), "cloud services")
        return (
            f"{org} applies shared-responsibility controls for {cloud_label}; org-owned configuration "
            "and provider compliance artifacts are cited in evidence."
        )
    return None


def tailored_implementation(
    control_id: str,
    family: str,
    org_profile: OrgProfile,
    env_scope: EnvScope,
) -> Optional[str]:
    """Best matching implementation paragraph for this control and stack."""
    if env_scope.get("uses_m365") == "yes":
        text = _m365_snippet(control_id, org_profile)
        if text:
            return text
    text = _cloud_snippet(control_id, env_scope, org_profile)
    if text:
        return text
    text = _access_snippet(control_id, env_scope, org_profile)
    if text:
        return text
    return _family_snippet(family, env_scope, org_profile)


def inheritance_block(
    control_id: str,
    env_scope: EnvScope,
    scoped_controls: List[str],
) -> Optional[Tuple[str, str, str]]:
    """Returns (org_text, provider_text, citation) when inheritance map matches."""
    detail = inheritance_detail_for_control(control_id, env_scope, scoped_controls)
    if not detail:
        return None
    return (
        detail.get("org_responsibility", ""),
        detail.get("provider_responsibility", ""),
        detail.get("citation", ""),
    )


def context_evidence_hints(
    control_id: str,
    env_scope: EnvScope,
    scoped_controls: List[str],
) -> List[str]:
    hints: List[str] = []
    inherited = inheritance_block(control_id, env_scope, scoped_controls)
    if inherited:
        _, _, citation = inherited
        if citation:
            hints.append(citation)
    if env_scope.get("uses_m365") == "yes" and control_id.startswith("IA."):
        hints.append("Entra Conditional Access policy export; sign-in logs sample")
    if env_scope.get("remote_workforce") == "yes" and control_id in REMOTE_CONTROLS:
        hints.append("VPN configuration; remote session timeout settings")
    return hints
