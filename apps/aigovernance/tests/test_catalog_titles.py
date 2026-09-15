"""Regression tests for AI Governance catalog title accuracy.

These tests verify that control titles match their official source documents:
- EU AI Act Regulation 2024/1689
- NIST AI RMF 1.0 (AI 100-1) Table 1
- ISO/IEC 42001:2023
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.ai_controls_catalog import AI_GOV_FRAMEWORK


# ═══════════════════════════════════════════════════════════════
# NIST AI RMF 1.0 — subcategory integrity (source: docs/NIST_AI_RMF_100-1.pdf
# via core/nist_ai_rmf_official.py)
# ═══════════════════════════════════════════════════════════════


def test_nist_subcategories_match_official():
    """NIST AI RMF catalog entries must be exactly the 72 official subcategories,
    each carrying the official statement as `official_title`."""
    from core.nist_ai_rmf_official import NIST_AI_RMF_SUBCATEGORIES

    nist = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "NIST AI RMF"}
    expected = {f"NIST-{key.replace(' ', '-')}": stmt for key, stmt in NIST_AI_RMF_SUBCATEGORIES.items()}
    assert len(expected) == 72
    assert set(nist) == set(expected), (
        f"mismatch: extra={set(nist) - set(expected)}, missing={set(expected) - set(nist)}"
    )
    for cid, stmt in expected.items():
        assert nist[cid].get("official_title") == stmt, cid
        assert nist[cid].get("clause") == cid[len("NIST-"):].replace("-", " "), cid


def test_nist_subcategory_guidance_derived():
    """Every NIST subcategory must have examine/interview/test guidance."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    nist = {k for k in AI_GOV_FRAMEWORK if k.startswith("NIST-")}
    for cid in nist:
        guidance = AI_GENERATED_CONTROL_OBJECTIVES.get(cid, [])
        assert len(guidance) == 3, f"{cid}: expected 3 guidance items, got {len(guidance)}"
        assert guidance[0].startswith("Examine:"), cid
        assert guidance[1].startswith("Interview:"), cid
        assert guidance[2].startswith("Test:"), cid


# ═══════════════════════════════════════════════════════════════
# ISO 42001:2023 — Clause 8 and 10 titles
# Source: docs/ISO-IEC-42001-2023.pdf TOC
# ═══════════════════════════════════════════════════════════════

ISO_CLAUSE_TITLES = {
    "ISO-8.2": "AI Risk Assessment",
    "ISO-8.3": "AI Risk Treatment",
    "ISO-8.4": "AI System Impact Assessment",
    "ISO-10.1": "Continual Improvement",
    "ISO-10.2": "Nonconformity & Corrective Action",
}


def test_iso_clause_titles_match_official():
    """ISO clause 8.x and 10.x titles must match the official standard."""
    for control_id, expected_title in ISO_CLAUSE_TITLES.items():
        actual = AI_GOV_FRAMEWORK[control_id]["title"]
        assert actual == expected_title, (
            f"{control_id}: expected {expected_title!r}, got {actual!r}"
        )


# ═══════════════════════════════════════════════════════════════
# ISO 42001:2023 — Annex A objectives
# Source: Konfirmity/WiCyS/riskprofs (all quoting the standard)
# Real: A.2–A.10, 9 objectives, 38 controls
# ═══════════════════════════════════════════════════════════════

ISO_ANNEX_A_TITLES = {
    "ISO-A.2":  "Policies related to AI",
    "ISO-A.3":  "Internal organization",
    "ISO-A.4":  "Resources for AI systems",
    "ISO-A.5":  "Assessing impacts of AI systems",
    "ISO-A.6":  "AI system life cycle",
    "ISO-A.7":  "Data for AI systems",
    "ISO-A.8":  "Information for interested parties of AI systems",
    "ISO-A.9":  "Use of AI systems",
    "ISO-A.10": "Third-party and customer relationships",
}


def test_iso_annex_a_titles_match_official():
    """ISO Annex A titles must match A.2–A.10 from the standard."""
    for control_id, expected_title in ISO_ANNEX_A_TITLES.items():
        actual = AI_GOV_FRAMEWORK[control_id]["title"]
        assert actual == expected_title, (
            f"{control_id}: expected {expected_title!r}, got {actual!r}"
        )


def test_iso_annex_a_count():
    """ISO Annex A should have exactly 9 objectives (A.2–A.10)."""
    annex_a = {k: v for k, v in AI_GOV_FRAMEWORK.items()
               if v["framework"] == "ISO 42001" and re.fullmatch(r"ISO-A\.\d+", k)}
    assert len(annex_a) == 9, f"Expected 9 Annex A objectives, got {len(annex_a)}"


def test_no_invented_annex_a_ids():
    """Annex A objectives must be exactly A.2–A.10; controls must be the 38 official ones."""
    from core.iso_42001_official import ANNEX_A_CONTROL_TOPICS

    expected_objectives = {f"ISO-A.{i}" for i in range(2, 11)}
    expected_controls = {f"ISO-{ref}" for topics in ANNEX_A_CONTROL_TOPICS.values() for ref in topics}
    iso_ids = {k for k in AI_GOV_FRAMEWORK if k.startswith("ISO-A.")}
    objectives = {k for k in iso_ids if re.fullmatch(r"ISO-A\.\d+", k)}
    controls = iso_ids - objectives
    assert objectives == expected_objectives, (
        f"Annex A objective mismatch: unexpected={objectives - expected_objectives}, "
        f"missing={expected_objectives - objectives}"
    )
    assert controls == expected_controls, (
        f"Annex A control mismatch: unexpected={controls - expected_controls}, "
        f"missing={expected_controls - controls}"
    )


def test_iso_total_count():
    """ISO 42001 should have 70 total entries (23 clauses + 9 Annex A objectives + 38 controls)."""
    iso = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "ISO 42001"}
    assert len(iso) == 70, f"Expected 70 ISO entries, got {len(iso)}"


def test_iso_official_titles_match_standard():
    """Every ISO catalog entry must carry the official wording from the standard
    (docs/ISO-IEC-42001-2023.pdf) in `official_title`."""
    from core.iso_42001_official import (
        ANNEX_A_CONTROL_TOPICS,
        OFFICIAL_ISO_42001_ANNEX_A,
        OFFICIAL_ISO_42001_CLAUSES,
    )

    iso = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "ISO 42001"}
    expected = {}
    for clause, title in OFFICIAL_ISO_42001_CLAUSES.items():
        expected[f"ISO-{clause}"] = title
    for annex, title in OFFICIAL_ISO_42001_ANNEX_A.items():
        if annex != "A.1":
            expected[f"ISO-{annex}"] = title
    for topics in ANNEX_A_CONTROL_TOPICS.values():
        for ref, topic in topics.items():
            expected[f"ISO-{ref}"] = topic

    for cid, official_title in expected.items():
        assert cid in iso, f"{cid} missing from catalog"
        assert iso[cid].get("official_title") == official_title, (
            f"{cid}: official_title {iso[cid].get('official_title')!r} != {official_title!r}"
        )
    # No ISO entry may carry an official_title we don't recognize
    for cid, entry in iso.items():
        assert cid in expected, f"{cid} has no official title in the standard data"


def test_iso_annex_a_control_guidance_derived():
    """Every Annex A control must have examine/interview/test guidance."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    controls = {k for k in AI_GOV_FRAMEWORK if k.startswith("ISO-A.") and len(k) > len("ISO-A.x")}
    for cid in controls:
        guidance = AI_GENERATED_CONTROL_OBJECTIVES.get(cid, [])
        assert len(guidance) == 3, f"{cid}: expected 3 guidance items, got {len(guidance)}"
        assert guidance[0].startswith("Examine:"), cid
        assert guidance[1].startswith("Interview:"), cid
        assert guidance[2].startswith("Test:"), cid


def test_eu_official_titles_match_regulation():
    """Every EU AI Act catalog entry must carry the official article title
    (from apps/aigovernance/docs/EU_AI_Act_Regulation_2024_1689.pdf) in `official_title`."""
    from core.eu_ai_act_official import EU_AI_ACT_ARTICLE_TITLES

    eu = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "EU AI Act"}
    expected = {f"EU-{art}": title for art, title in EU_AI_ACT_ARTICLE_TITLES.items()}
    assert len(expected) == 40
    for cid, official_title in expected.items():
        assert cid in eu, f"{cid} missing from catalog"
        assert eu[cid].get("official_title") == official_title, (
            f"{cid}: official_title {eu[cid].get('official_title')!r} != {official_title!r}"
        )
    for cid, entry in eu.items():
        assert cid in expected, f"{cid} has no official title in the regulation data"


def test_eu_new_articles_have_guidance():
    """The five catalog articles added from conformity (8, 46, 47, 57, 60) must have guidance."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    for cid in ("EU-8", "EU-46", "EU-47", "EU-57", "EU-60"):
        guidance = AI_GENERATED_CONTROL_OBJECTIVES.get(cid, [])
        assert len(guidance) == 3, f"{cid}: expected 3 guidance items, got {len(guidance)}"


def test_owasp_titles_match_official():
    """OWASP Agentic catalog entries must be exactly ASI01-ASI10 with official titles."""
    from core.agentic_ai_official import OWASP_AGENTIC_TOP_10_DESCRIPTIONS, OWASP_AGENTIC_TOP_10_TITLES

    owasp = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "OWASP Agentic"}
    assert len(owasp) == 10
    for i in range(1, 11):
        ref = f"ASI{i:02d}"
        cid = f"OWASP-{i}"
        entry = owasp[cid]
        assert entry["official_title"] == OWASP_AGENTIC_TOP_10_TITLES[ref], cid
        assert entry["clause"] == ref, cid
        assert entry["title"] == OWASP_AGENTIC_TOP_10_TITLES[ref], cid
        assert ref in OWASP_AGENTIC_TOP_10_DESCRIPTIONS


def test_owasp_guidance_derived():
    """Every OWASP risk must have examine/interview/test guidance."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    for i in range(1, 11):
        cid = f"OWASP-{i}"
        guidance = AI_GENERATED_CONTROL_OBJECTIVES.get(cid, [])
        assert len(guidance) == 3, f"{cid}: expected 3 guidance items, got {len(guidance)}"
        assert guidance[0].startswith("Examine:"), cid
        assert guidance[1].startswith("Interview:"), cid
        assert guidance[2].startswith("Test:"), cid


def test_owasp_llm_titles_match_official():
    """OWASP LLM Top 10 catalog entries must be exactly LLM01-LLM10:2025 with official titles."""
    from core.llm_top_10_official import LLM_TOP_10_DESCRIPTIONS, LLM_TOP_10_TITLES

    llm = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "OWASP LLM Top 10"}
    assert len(llm) == 10
    for i in range(1, 11):
        ref = f"LLM{i:02d}"
        cid = f"OWASP-LLM-{i}"
        entry = llm[cid]
        assert entry["official_title"] == LLM_TOP_10_TITLES[ref], cid
        assert entry["clause"] == f"{ref}:2025", cid
        assert entry["title"] == LLM_TOP_10_TITLES[ref], cid
        assert ref in LLM_TOP_10_DESCRIPTIONS


def test_owasp_llm_guidance_derived():
    """Every OWASP LLM risk must have examine/interview/test guidance."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    for i in range(1, 11):
        cid = f"OWASP-LLM-{i}"
        guidance = AI_GENERATED_CONTROL_OBJECTIVES.get(cid, [])
        assert len(guidance) == 3, f"{cid}: expected 3 guidance items, got {len(guidance)}"
        assert guidance[0].startswith("Examine:"), cid
        assert guidance[1].startswith("Interview:"), cid
        assert guidance[2].startswith("Test:"), cid


def test_ui_framework_lists_are_in_sync():
    """The frontend framework registries must all include the same frameworks.

    Guards against a framework being added to the catalog but silently missing
    from the UI context (which previously hid frameworks from every tab).
    """
    app_root = Path(__file__).resolve().parents[1]

    frameworks_ts = (app_root / "frontend/src/pages/aiGovFrameworks.ts").read_text()
    keys = set(re.findall(r'key: "([a-z0-9_]+)"', frameworks_ts))
    assert keys, "no framework keys parsed from aiGovFrameworks.ts"

    context_ts = (app_root / "frontend/src/pages/AiGovFrameworkContext.tsx").read_text()
    context_keys = set(re.findall(r'"(eu_ai_act|nist_ai_rmf|iso_42001|owasp_agentic|owasp_llm|iso27001|soc2|cmmc)"', context_ts))
    assert context_keys, "no framework keys parsed from AiGovFrameworkContext.tsx"
    assert keys == context_keys, (
        f"framework drift: aiGovFrameworks={sorted(keys)} vs context={sorted(context_keys)}"
    )

    checklist_ts = (app_root / "frontend/src/pages/EvidenceRequirementsChecklist.tsx").read_text()
    artifact_keys = set(re.findall(r'^  ([a-z0-9_]+): \[', checklist_ts, re.M))
    assert keys == artifact_keys, (
        f"framework drift: aiGovFrameworks={sorted(keys)} vs checklist artifacts={sorted(artifact_keys)}"
    )

    platform_ts = (app_root.parent.parent / "apps/platform/frontend/src/framework/frameworks.ts").read_text()
    assert "aigovernance" in platform_ts, "platform framework registry missing aigovernance"


def test_iso_annex_a_official_objectives():
    """Annex A objective titles must match the official wording (incl. A.8)."""
    from core.iso_42001_official import OFFICIAL_ISO_42001_ANNEX_A

    iso = {k: v for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "ISO 42001"}
    for annex in ("A.2", "A.3", "A.4", "A.5", "A.6", "A.7", "A.8", "A.9", "A.10"):
        assert iso[f"ISO-{annex}"]["title"] == OFFICIAL_ISO_42001_ANNEX_A[annex], annex


# ═══════════════════════════════════════════════════════════════
# ISO 42001 — guidance data and consumer reference integrity
# ═══════════════════════════════════════════════════════════════

# Keyword that each control's examine/interview/test guidance must cover.
ISO_GUIDANCE_KEYWORDS = {
    "ISO-8.2": "risk assessment",
    "ISO-8.3": "risk treatment",
    "ISO-8.4": "impact assessment",
    "ISO-A.2": "policy",
    "ISO-A.5": "impact",
    "ISO-A.6": "lifecycle",
    "ISO-A.7": "data",
    "ISO-A.8": "interested parties",
    "ISO-A.9": "oversight",
    "ISO-A.10": "third-party",
}

# Files that reference ISO 42001 clause/Annex A IDs, relative to the app root.
# Each file is scanned for the patterns that must never appear (invented IDs).
ISO_REF_CONSUMER_FILES = {
    "core/guidance/objectives_data.py": [r"ISO-A\.1[1-9]\b", r"ISO-A\.2[0-9]\b"],
    "core/competence_requirements.py": [r"ISO-A\.1[1-9]\b", r"ISO-A\.2[0-9]\b"],
    "server/tabletop/scenarios.py": [r"ISO 42001 8\.[56]\b", r"ISO 42001 A\.1[1-9]\b"],
    "server/contract_templates.py": [r"ISO-A\.1[1-9]\b", r"Annex A\.1[1-9]\b"],
    "frontend/src/pages/EvidenceRequirementsChecklist.tsx": [r"\bA\.1[1-9]\b", r"\bA\.2[0-9]\b"],
    "artifacts.md": [r"\bA\.1[1-9]\b", r"\bA\.2[0-9]\b"],
    "../../packages/policies/templates.py": [r"ISO-A\.1[1-9]\b", r"ISO-A\.2[0-9]\b"],
    "../../shared/frontend/gap-analysis/types.ts": [
        r"ISO 42001 8\.[56]\b",
        r"ISO 42001 A\.1[1-9]\b",
        r"GOVERN 1\.7\b",
        r"MEASURE 3\.[5-9]\b",
    ],
}


def test_iso_guidance_keys_match_catalog():
    """Every ISO control must have guidance and every guidance key must exist."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    iso_catalog = {k for k, v in AI_GOV_FRAMEWORK.items() if v["framework"] == "ISO 42001"}
    iso_guidance = {k for k in AI_GENERATED_CONTROL_OBJECTIVES if k.startswith("ISO-")}
    assert iso_guidance == iso_catalog, (
        f"guidance/catalog mismatch: extra={iso_guidance - iso_catalog}, "
        f"missing={iso_catalog - iso_guidance}"
    )


def test_iso_guidance_content_matches_control():
    """Guidance content must align with each control's official subject (no shifted mappings)."""
    from core.guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES

    for control_id, keyword in ISO_GUIDANCE_KEYWORDS.items():
        text = " ".join(AI_GENERATED_CONTROL_OBJECTIVES[control_id]).lower()
        assert keyword in text, f"{control_id}: guidance content does not cover {keyword!r}"


def test_no_invented_iso_refs_in_consumers():
    """Consumers must not reference invented ISO 42001 clause/Annex A IDs."""
    app_root = Path(__file__).resolve().parents[1]
    for rel_path, patterns in ISO_REF_CONSUMER_FILES.items():
        target = (app_root / rel_path).resolve()
        if not target.exists():
            continue
        text = target.read_text()
        for pattern in patterns:
            match = re.search(pattern, text)
            assert match is None, (
                f"{rel_path}: invalid ISO 42001 ref pattern {pattern!r} found: {match.group(0)!r}"
            )


def test_shared_catalog_titles_match_aigov_catalog():
    """Overlapping IDs in packages/control_catalog must have identical titles to the
    verified aigov catalog (single source of truth for EU AI Act / NIST AI RMF / ISO 42001)."""
    packages_path = Path(__file__).resolve().parents[3] / "packages"
    if str(packages_path) not in sys.path:
        sys.path.insert(0, str(packages_path))
    from control_catalog.catalog import CONTROLS_CATALOG

    shared = {c["id"]: c for c in CONTROLS_CATALOG}
    mismatches = []
    for cid, aigov_entry in AI_GOV_FRAMEWORK.items():
        if cid not in shared:
            continue
        if shared[cid]["title"] != aigov_entry["title"]:
            mismatches.append(f"{cid}: shared={shared[cid]['title']!r} aigov={aigov_entry['title']!r}")
        if shared[cid].get("clause") != aigov_entry.get("clause"):
            mismatches.append(f"{cid}: shared clause={shared[cid].get('clause')!r} aigov clause={aigov_entry.get('clause')!r}")
    assert not mismatches, "Shared catalog diverges from aigov catalog:\n" + "\n".join(mismatches[:10])


def test_shared_catalog_covers_all_aigov_controls():
    """The shared catalog must contain every aigov catalog control (canonical coverage)."""
    packages_path = Path(__file__).resolve().parents[3] / "packages"
    if str(packages_path) not in sys.path:
        sys.path.insert(0, str(packages_path))
    from control_catalog.catalog import CONTROLS_CATALOG

    shared_ids = {c["id"] for c in CONTROLS_CATALOG}
    missing = sorted(set(AI_GOV_FRAMEWORK) - shared_ids)
    assert not missing, f"Shared catalog missing aigov controls: {missing[:10]}"
