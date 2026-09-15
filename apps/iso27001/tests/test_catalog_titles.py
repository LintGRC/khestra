"""ISO 27001 catalog titles locked to docs/iso-iec-27001-2022.pdf."""

from controls import ALL_CONTROLS
from iso_27001_official import ISO_27001_TITLES


def test_official_module_has_116_titles():
    assert len(ISO_27001_TITLES) == 116
    clauses = [k for k in ISO_27001_TITLES if not k.startswith("A.")]
    annex = [k for k in ISO_27001_TITLES if k.startswith("A.")]
    assert len(clauses) == 23
    assert len(annex) == 93


def test_catalog_ids_and_titles_match_official():
    catalog = {c["id"]: c for c in ALL_CONTROLS}
    assert set(catalog) == set(ISO_27001_TITLES)
    for cid, title in ISO_27001_TITLES.items():
        assert catalog[cid]["title"] == title, cid
        assert catalog[cid]["official_title"] == title, cid


def test_table_a1_titles_use_official_wording():
    assert ISO_27001_TITLES["A.5.1"] == "Policies for information security"
    assert ISO_27001_TITLES["A.5.21"] == (
        "Managing information security in the information and communication "
        "technology (ICT) supply chain"
    )
    assert ISO_27001_TITLES["A.5.34"] == (
        "Privacy and protection of personal identifiable information (PII)"
    )
    assert ISO_27001_TITLES["A.8.20"] == "Networks security"
    assert ISO_27001_TITLES["4.1"] == "Understanding the organization and its context"
    assert ISO_27001_TITLES["9.3"] == "Management review"
