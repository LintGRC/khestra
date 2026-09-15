"""Shared responsibility / inheritance map for cloud and SaaS providers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from controls import CMMC_FRAMEWORK

# providers tag: m365, azure, aws, google
INHERITANCE_MAP: List[Dict[str, Any]] = [
    {
        "control_id": "IA.L2-3.5.3",
        "providers": ("m365",),
        "provider": "Microsoft Entra ID",
        "org_responsibility": "Enable MFA for all in-scope users; Conditional Access policies; exception tracking.",
        "provider_responsibility": "Identity platform uptime; authenticator services.",
        "citation": "Microsoft shared responsibility matrix; export Entra CA policies.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "IA.L2-3.5.7",
        "providers": ("m365",),
        "provider": "Microsoft Entra ID",
        "org_responsibility": "Assign password policy; disable legacy auth; monitor exceptions.",
        "provider_responsibility": "Enforce stored password hash protection.",
        "citation": "Entra password policy screenshot; disable basic auth report.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "IA.L2-3.5.3",
        "providers": ("google",),
        "provider": "Google Workspace",
        "org_responsibility": "Enforce 2-Step Verification; context-aware access for CUI drives.",
        "provider_responsibility": "Workspace authentication infrastructure.",
        "citation": "Google Admin 2SV report; context-aware access policy.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "AU.L2-3.3.1",
        "providers": ("m365",),
        "provider": "Microsoft 365",
        "org_responsibility": "Enable unified audit log; retention; review procedures.",
        "provider_responsibility": "Audit log generation for platform events.",
        "citation": "Purview audit retention export.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "SC.L2-3.13.8",
        "providers": ("m365", "azure", "aws", "google"),
        "provider": "Cloud platform",
        "org_responsibility": "Configure TLS versions; disable weak ciphers on org-managed endpoints.",
        "provider_responsibility": "Encryption in transit for managed PaaS/SaaS paths.",
        "citation": "Provider compliance artifact (SOC 2 / FedRAMP) + config export.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "SC.L2-3.13.11",
        "providers": ("m365", "azure"),
        "provider": "Microsoft cloud",
        "org_responsibility": "Select FIPS-validated modules where required; document gaps on endpoints.",
        "provider_responsibility": "Platform crypto module attestations.",
        "citation": "Microsoft compliance portal FIPS export.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "SC.L2-3.13.16",
        "providers": ("azure", "aws"),
        "provider": "IaaS/PaaS",
        "org_responsibility": "Customer-managed keys; bucket/disk encryption settings.",
        "provider_responsibility": "Underlying storage encryption services.",
        "citation": "KMS key policy; SSE configuration screenshot.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "CM.L2-3.4.1",
        "providers": ("azure", "aws"),
        "provider": "IaaS",
        "org_responsibility": "Guest OS baselines; AMI/golden image; patch cadence.",
        "provider_responsibility": "Hypervisor and physical infrastructure.",
        "citation": "AWS/Azure shared responsibility model diagram.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "CM.L2-3.4.2",
        "providers": ("aws",),
        "provider": "AWS",
        "org_responsibility": "Security groups, launch templates, Config rules for drift.",
        "provider_responsibility": "Managed service control planes.",
        "citation": "AWS Config conformance pack export.",
        "inheritance_level": "Org",
    },
    {
        "control_id": "SC.L2-3.13.8",
        "providers": ("aws",),
        "provider": "AWS",
        "org_responsibility": "Enforce TLS on ALB/CloudFront; S3 bucket policies.",
        "provider_responsibility": "AWS network backbone encryption.",
        "citation": "AWS shared responsibility whitepaper.",
        "inheritance_level": "Partial",
    },
    {
        "control_id": "SI.L2-3.14.6",
        "providers": ("aws",),
        "provider": "AWS GuardDuty / Defender",
        "org_responsibility": "Enable monitoring in all regions; tune alerts; response playbooks.",
        "provider_responsibility": "Threat intel feeds for managed detectors.",
        "citation": "GuardDuty enabled-regions report.",
        "inheritance_level": "Partial",
    },
]


def _active_provider_tags(env_scope: Dict[str, str]) -> set[str]:
    tags: set[str] = set()
    if env_scope.get("uses_m365") == "yes":
        tags.add("m365")
    cloud = env_scope.get("cloud_hosting", "")
    if cloud in ("azure", "both"):
        tags.add("azure")
    if cloud in ("aws", "both"):
        tags.add("aws")
    if env_scope.get("uses_m365") == "no" and cloud in ("", "on_prem_only"):
        pass
    if env_scope.get("uses_google") == "yes":
        tags.add("google")
    return tags


def inheritance_map_rows(
    env_scope: Dict[str, str],
    scoped_controls: List[str],
) -> List[Dict[str, Any]]:
    tags = _active_provider_tags(env_scope)
    if not tags:
        return []
    scoped = set(scoped_controls)
    rows: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for entry in INHERITANCE_MAP:
        cid = entry["control_id"]
        if cid not in scoped:
            continue
        if not tags.intersection(entry["providers"]):
            continue
        dedupe = f"{cid}|{entry['provider']}"
        if dedupe in seen:
            continue
        seen.add(dedupe)
        rows.append(
            {
                **entry,
                "providers": list(entry["providers"]),
                "control_name": CMMC_FRAMEWORK[cid]["name"][:70],
            }
        )
    return rows


def inheritance_detail_for_control(
    control_id: str,
    env_scope: Dict[str, str],
    scoped_controls: List[str],
) -> Optional[Dict[str, Any]]:
    for row in inheritance_map_rows(env_scope, scoped_controls):
        if row["control_id"] == control_id:
            return row
    return None
