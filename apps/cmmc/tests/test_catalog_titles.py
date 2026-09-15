"""Regression tests for CMMC catalog title accuracy.

Verifies that all 110 CMMC / NIST SP 800-171 Rev 2 control names
match the official requirement text from the in-repo CSV source.
"""

import csv
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.controls import CMMC_FRAMEWORK

CSV_PATH = Path(__file__).resolve().parents[2].parent / "reference" / "sp800-171r2-security-reqs.csv"


def _load_official_requirements():
    """Load official requirement text from the in-repo CSV."""
    reqs = {}
    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) >= 5:
                ident = row[2].strip()
                req_text = row[4].strip()
                # Strip trailing period and footnote markers
                req_text = re.sub(r"\.\[\d+\]$", "", req_text)
                if req_text.endswith("."):
                    req_text = req_text[:-1]
                reqs[ident] = req_text
    return reqs


def _extract_ident(key):
    """Extract the NIST requirement number from catalog key (e.g. AC.L2-3.1.1 -> 3.1.1)."""
    m = re.search(r"-(\d+\.\d+\.\d+)$", key)
    return m.group(1) if m else None


def test_catalog_count():
    """CMMC Level 2 should have exactly 110 controls."""
    assert len(CMMC_FRAMEWORK) == 110, f"Expected 110 controls, got {len(CMMC_FRAMEWORK)}"


def test_all_names_match_official_csv():
    """Every control name must match the official requirement text from the CSV."""
    official = _load_official_requirements()
    assert len(official) == 110, f"CSV has {len(official)} requirements, expected 110"

    mismatches = []
    for key, entry in CMMC_FRAMEWORK.items():
        ident = _extract_ident(key)
        if ident is None:
            mismatches.append((key, "N/A", "Could not extract identifier", ""))
            continue
        if ident not in official:
            mismatches.append((key, ident, "Not in CSV", ""))
            continue
        actual = entry["name"]
        expected = official[ident]
        if actual != expected:
            mismatches.append((key, ident, expected, actual))

    assert not mismatches, (
        f"{len(mismatches)} name mismatches:\n"
        + "\n".join(
            f"  {k} ({i}): expected {e!r}\n                  got      {a!r}"
            for k, i, e, a in mismatches[:10]
        )
    )


def test_families_match_csv():
    """Each control's family must match the CSV family."""
    official = _load_official_requirements()

    family_map = {
        "Access Control": "AC",
        "Awareness and Training": "AT",
        "Audit and Accountability": "AU",
        "Security Assessment": "CA",
        "Configuration Management": "CM",
        "Identification and Authentication": "IA",
        "Incident Response": "IR",
        "Maintenance": "MA",
        "Media Protection": "MP",
        "Physical Protection": "PE",
        "Personnel Security": "PS",
        "Risk Assessment": "RA",
        "System and Communications Protection": "SC",
        "System and Information Integrity": "SI",
    }

    # Build CSV family lookup from identifier
    csv_families = {}
    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 3:
                ident = row[2].strip()
                family = row[0].strip()
                csv_families[ident] = family

    mismatches = []
    for key, entry in CMMC_FRAMEWORK.items():
        ident = _extract_ident(key)
        if ident and ident in csv_families:
            expected_family = csv_families[ident]
            actual_family = entry["family"]
            if actual_family.lower() != expected_family.lower():
                mismatches.append((key, expected_family, actual_family))

    assert not mismatches, (
        f"{len(mismatches)} family mismatches: "
        + ", ".join(f"{k}: expected {e}, got {a}" for k, e, a in mismatches[:5])
    )


def test_no_duplicate_si_names():
    """SI family controls must not share the same name (the old shuffle bug)."""
    si_controls = {k: v for k, v in CMMC_FRAMEWORK.items() if k.startswith("SI.")}
    names = [v["name"] for v in si_controls.values()]
    assert len(names) == len(set(names)), (
        f"Duplicate SI names: {[n for n in names if names.count(n) > 1]}"
    )
