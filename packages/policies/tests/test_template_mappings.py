"""Policy template mapping integrity — every mapped control ID must resolve.

Guards against the legacy `mapped_controls_aigov` / `AI_*` IDs that existed
nowhere (removed) and against any other invented mapped-control IDs.
"""

import re
import sys
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[2]
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))

from control_catalog.catalog import CONTROLS_CATALOG  # noqa: E402
from policies.templates import BUILTIN_TEMPLATES  # noqa: E402

CATALOG_IDS = {c["id"] for c in CONTROLS_CATALOG}

MAPPING_FIELDS = [
    "mapped_controls_soc2",
    "mapped_controls_cmmc",
    "mapped_controls_eu_ai_act",
    "mapped_controls_nist_ai_rmf",
    "mapped_controls_iso_42001",
    "mapped_controls_iso27001",
]

LEGACY_AI_ID = re.compile(r"^AI_[A-Z]+\.\d+$")


def test_no_legacy_aigov_mapping_field():
    for tpl in BUILTIN_TEMPLATES:
        assert "mapped_controls_aigov" not in tpl, tpl["key"]


def test_no_legacy_ai_ids_anywhere():
    for tpl in BUILTIN_TEMPLATES:
        for field in MAPPING_FIELDS:
            for cid in tpl.get(field, []):
                assert not LEGACY_AI_ID.match(cid), f"{tpl['key']}.{field}: {cid}"


def test_mapped_control_ids_resolve_in_catalog():
    unresolved = []
    for tpl in BUILTIN_TEMPLATES:
        for field in MAPPING_FIELDS:
            for cid in tpl.get(field, []):
                if cid not in CATALOG_IDS:
                    unresolved.append(f"{tpl['key']}.{field}: {cid}")
    assert not unresolved, "Unresolvable mapped control IDs:\n" + "\n".join(unresolved[:15])
