"""Regression tests for the unified control catalog.

Locks the unified catalog to the official framework inventories:
  - CMMC Rev 2: 15 (L1) + 110 (L2) + 24 (L3) practices per DoD Model Overview
    v2.13 / 32 CFR Part 170 (L1 = FAR 52.204-21(b)(1)(i)-(xv) format).
  - SOC 2: 61 Trust Services Criteria points.
  - Every control ID referenced by control_mappings/*.json and CCF topics
    must resolve to a catalog entry.
"""

import json
import re
import sys
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))
REPO = Path(__file__).resolve().parents[3]

from control_catalog.catalog import CONTROLS_CATALOG, list_controls  # noqa: E402

OFFICIAL_CMMC = {
    "AC.L1-b.1.i", "AC.L1-b.1.ii", "AC.L1-b.1.iii", "AC.L1-b.1.iv",
    "IA.L1-b.1.v", "IA.L1-b.1.vi", "MP.L1-b.1.vii", "PE.L1-b.1.viii",
    "PE.L1-b.1.ix", "SC.L1-b.1.x", "SC.L1-b.1.xi", "SI.L1-b.1.xii",
    "SI.L1-b.1.xiii", "SI.L1-b.1.xiv", "SI.L1-b.1.xv",
}


def test_catalog_totals():
    assert len(CONTROLS_CATALOG) == 536
    assert len(list_controls("CMMC Rev 2")) == 149
    assert len(list_controls("SOC 2")) == 61
    assert len(list_controls("EU AI Act")) == 40
    assert len(list_controls("NIST AI RMF")) == 72
    assert len(list_controls("ISO 42001")) == 70
    assert len(list_controls("OWASP Agentic")) == 10
    assert len(list_controls("OWASP LLM Top 10")) == 10
    assert len(list_controls("ISO 27001")) == 124


def test_cmmc_level_counts():
    cmmc = list_controls("CMMC Rev 2")
    by_level = {1: 0, 2: 0, 3: 0}
    for c in cmmc:
        by_level[c["level"]] = by_level.get(c["level"], 0) + 1
    assert by_level == {1: 15, 2: 110, 3: 24}


def test_cmmc_l1_ids_match_far_clause_format():
    l1 = {c["id"] for c in list_controls("CMMC Rev 2") if c["level"] == 1}
    assert l1 == OFFICIAL_CMMC
    for cid in OFFICIAL_CMMC:
        assert cid.split(".L1-")[1].startswith("b.1.")


def test_cmmc_l2_ids_are_sp800_171_style():
    l2 = [c["id"] for c in list_controls("CMMC Rev 2") if c["level"] == 2]
    assert len(l2) == 110
    assert all(".L2-3." in cid for cid in l2)


def test_cmmc_l3_ids_are_sp800_172_style():
    l3 = [c["id"] for c in list_controls("CMMC Rev 2") if c["level"] == 3]
    assert len(l3) == 24
    assert all(".L3-3." in cid and cid.endswith("e") for cid in l3)


def test_all_ids_unique():
    ids = [c["id"] for c in CONTROLS_CATALOG]
    assert len(ids) == len(set(ids))


def test_no_deprecated_cmmc_1_02_or_20_ids():
    stale = [c["id"] for c in list_controls("CMMC Rev 2") if ".L1-3." in c["id"]]
    assert stale == []
    for cid in ("AC.2.005", "AC.3.024", "SC.L1-3.13.2"):
        assert cid not in {c["id"] for c in CONTROLS_CATALOG}


def test_control_mappings_reference_catalog_ids():
    ids = {c["id"] for c in CONTROLS_CATALOG}
    missing = set()
    for f in (REPO / "control_mappings").glob("*.json"):
        data = json.loads(f.read_text())
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if "control_id" in node and node["control_id"]:
                    if node["control_id"] not in ids:
                        missing.add(node["control_id"])
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    assert missing == set()


def test_ccf_cmmc_topics_reference_catalog_ids():
    from ccf import ccf  # noqa: PLC0415

    ids = {c["id"] for c in CONTROLS_CATALOG}
    missing = {
        cid for topic in ccf.get_ccf_topics() for cid in topic.cmmc if cid not in ids
    }
    assert missing == set()


def test_risk_seed_data_has_no_deprecated_cmmc_ids():
    from risks import store  # noqa: PLC0415

    src = Path(store.__file__).read_text()
    stale = re.findall(r'"((?:AC|SC)\.L1-3\.\d+\.\d+)"', src)
    assert stale == []
    assert "SC.L1-3.13.2" not in src
    assert "AC.L1-3.1.20" not in src
