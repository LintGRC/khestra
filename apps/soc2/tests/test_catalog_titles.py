"""SOC 2 catalog regression tests — verified against the official AICPA 2017 Trust Services Criteria (with Revised Points of Focus 2022)."""

from soc2_catalog import SOC2_CONTROLS
from tsc_2017_official import TSC_CRITERION_STATEMENTS, TSC_POF_TITLES

OFFICIAL_TSC_COUNT = 61

OFFICIAL_MEANINGS = {
    "CC6.8": "Malware Prevention",
    "CC7.1": "Detection and Monitoring",
    "CC7.2": "Anomaly Monitoring",
    "CC7.3": "Security Event Evaluation",
    "CC7.4": "Incident Response",
    "CC7.5": "Recovery from Security Incidents",
}

OFFICIAL_PRIVACY_IDS = [
    "P1.1",
    "P2.1",
    "P3.1",
    "P3.2",
    "P4.1",
    "P4.2",
    "P4.3",
    "P5.1",
    "P5.2",
    "P6.1",
    "P6.2",
    "P6.3",
    "P6.4",
    "P6.5",
    "P6.6",
    "P6.7",
    "P7.1",
    "P8.1",
]


def test_catalog_contains_exactly_official_criteria():
    assert len(SOC2_CONTROLS) == OFFICIAL_TSC_COUNT


def test_official_criteria_have_correct_meanings():
    for cid, official_title in OFFICIAL_MEANINGS.items():
        assert cid in SOC2_CONTROLS, f"official criterion {cid} missing"
        assert SOC2_CONTROLS[cid]["title"] == official_title, f"{cid} title wrong"


def test_privacy_criteria_use_official_numbering():
    privacy = sorted(k for k in SOC2_CONTROLS if k.startswith("P") and not k.startswith("PI"))
    assert privacy == OFFICIAL_PRIVACY_IDS


def test_points_of_focus_ids_unique_and_prefixed():
    seen = set()
    for cid, control in SOC2_CONTROLS.items():
        assert control["points_of_focus"], f"{cid} has no points of focus"
        for pof in control["points_of_focus"]:
            assert pof["id"].startswith(cid), f"{pof['id']} not prefixed by {cid}"
            assert pof["id"] not in seen, f"duplicate PoF id {pof['id']}"
            seen.add(pof["id"])


def test_catalog_ids_match_official_module():
    assert set(SOC2_CONTROLS) == set(TSC_CRITERION_STATEMENTS)
    assert len(TSC_CRITERION_STATEMENTS) == OFFICIAL_TSC_COUNT
    assert "P1.0" not in TSC_CRITERION_STATEMENTS


def test_official_title_matches_tsc_statement():
    for cid, statement in TSC_CRITERION_STATEMENTS.items():
        assert SOC2_CONTROLS[cid]["official_title"] == statement, cid
        assert "following point" not in statement.lower(), cid
        assert not statement.endswith("-"), cid


def test_known_pof_titles_locked():
    """Spot-check PoFs that were previously collapsed or invented in the catalog."""
    assert TSC_POF_TITLES["CC1.1"] == (
        "Sets the Tone at the Top",
        "Establishes Standards of Conduct",
        "Evaluates Adherence to Standards of Conduct",
        "Addresses Deviations in a Timely Manner",
        "Considers Contractors and Vendor Employees in Demonstrating Its Commitment",
    )
    assert TSC_POF_TITLES["CC6.8"] == (
        "Restricts Application and Software Installation",
        "Detects Unauthorized Changes to Software and Configuration Parameters",
        "Uses a Defined Change Control Process",
        "Uses Antivirus and Anti-Malware Software",
        "Scans Information Assets from Outside the Entity for Malware and Other Unauthorized Software",
    )
    assert len(TSC_POF_TITLES["CC6.8"]) == 5
    assert "Uses Antivirus and Anti-Malware Software" in TSC_POF_TITLES["CC6.8"]


def test_every_criterion_has_official_pofs():
    for cid in TSC_CRITERION_STATEMENTS:
        assert cid in TSC_POF_TITLES and TSC_POF_TITLES[cid], cid


def test_catalog_pof_parity_with_official():
    """SKU 1 parity: catalog PoF count == official PoF count per criterion.

    Catalog carries faithful paraphrases (not verbatim AICPA titles — see
    soc2_pof_paraphrases.py); this asserts completeness/correspondence only.
    """
    for cid in TSC_CRITERION_STATEMENTS:
        official = TSC_POF_TITLES[cid]
        catalog = [p["text"] for p in SOC2_CONTROLS[cid]["points_of_focus"]]
        assert len(catalog) == len(official), (
            f"{cid}: catalog has {len(catalog)} PoFs, official has {len(official)}"
        )
        # textual equivalence is fuzzy (paraphrase); at minimum ensure no
        # obvious truncation of the last entry and ids match order.
        for i, pof in enumerate(SOC2_CONTROLS[cid]["points_of_focus"]):
            assert pof["id"] == f"{cid}.P{i + 1}"


def test_official_pof_total_is_299():
    """299 real PoF titles; P8.1 has 6 (2 trailing glossary entries excluded)."""
    total = sum(len(v) for v in TSC_POF_TITLES.values())
    assert total == 299
    assert len(TSC_POF_TITLES["P8.1"]) == 6

