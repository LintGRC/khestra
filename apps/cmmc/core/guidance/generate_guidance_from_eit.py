"""Generate per-objective guidance entries from NIST EIT reference data.

Usage:
    cd apps/cmmc/core/guidance
    python3 generate_guidance_from_eit.py > /tmp/entries.txt

Then manually review and append to objective_guidance.py.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps/cmmc/core"))

import importlib.util

def _load_mod(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

ref_mod = _load_mod(str(ROOT / "apps/cmmc/core/guidance/nist_eit_reference.py"))
REF = ref_mod.NIST_EIT_REFERENCE

existing_mod = _load_mod(str(ROOT / "apps/cmmc/core/guidance/objective_guidance.py"))
EXISTING = existing_mod.OBJECTIVE_DELIVERABLE_GUIDANCE

# Verb → kind mapping based on the MAIN verb after "are/is"
VERB_KIND = {
    "defined": "policy",
    "identified": "policy",
    "specified": "policy",
    "established": "policy",
    "described": "policy",
    "documented": "policy",
    "developed": "policy",
    "implemented": "config",
    "enforced": "config",
    "employed": "config",
    "limited": "config",
    "restricted": "config",
    "prevented": "config",
    "controlled": "config",
    "disabled": "config",
    "protected": "config",
    "safeguarded": "config",
    "monitored": "evidence",
    "reviewed": "evidence",
    "assessed": "evidence",
    "tested": "evidence",
    "scanned": "evidence",
    "created": "evidence",
    "generated": "evidence",
    "logged": "evidence",
    "tracked": "evidence",
    "recorded": "evidence",
    "performed": "evidence",
    "conducted": "evidence",
    "remediated": "evidence",
    "corrected": "evidence",
    "screened": "evidence",
    "terminated": "evidence",
    "notified": "evidence",
    "trained": "evidence",
    "made": "evidence",
    "updated": "evidence",
    "carried": "evidence",
}

def main_verb(obj_text: str) -> str | None:
    """Extract the main verb after 'are' or 'is'."""
    m = re.search(r"\b(?:are|is)\s+(\w+)", obj_text, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return None

def detect_kind(text: str) -> str:
    verb = main_verb(text)
    if verb and verb in VERB_KIND:
        return VERB_KIND[verb]
    return "evidence"

def make_deliverable(obj_text: str, kind: str) -> str:
    # Clean parentheticals and normalize
    t = re.sub(r"\([^)]*\)", "", obj_text).strip()
    
    # Extract core subject: everything before the "are/is" verb
    m = re.match(r"^(the\s+|a\s+|an\s+)?(.+?)\s+(?:are|is)\s+", t, re.IGNORECASE)
    subjects = []
    if m:
        raw = m.group(2).strip()
        # Clean up common artifacts
        raw = re.sub(r"\s+", " ", raw).strip()
        subjects.append(raw)
    
    subject = subjects[0] if subjects else t
    
    # Truncate long subjects
    if len(subject) > 60:
        subject = subject[:60].rsplit(" ", 1)[0]
    
    if kind == "policy":
        if subject.lower().endswith(("policy", "plan", "procedure")):
            return subject
        return f"Written {subject} policy"
    elif kind == "config":
        return f"{subject} configuration proof"
    else:
        return f"{subject} records"

def select_eit(control_data: dict, kind: str) -> str:
    parts = []
    for method in ("examine", "test"):
        text = control_data.get(method, "").strip()
        if text:
            parts.append(f"{method.capitalize()}: {text}")
    return " ".join(parts)


def generate():
    entries = {}
    for cid in sorted(REF):
        if cid in EXISTING:
            continue
        data = REF[cid]
        objectives = data.get("objectives", {})
        obj_entries = {}
        for letter, obj_text in sorted(objectives.items()):
            kind = detect_kind(obj_text)
            deliverable = make_deliverable(obj_text, kind)
            how = select_eit(data, kind)
            obj_entries[letter] = {
                "deliverable": deliverable,
                "how": how,
                "kind": kind,
            }
        if obj_entries:
            entries[cid] = obj_entries
    
    print("# Auto-generated — review before using")
    print(f"# {len(entries)} controls, {sum(len(v) for v in entries.values())} objectives")
    print()
    for cid in sorted(entries):
        objs = entries[cid]
        print(f'    "{cid}": {{')
        for letter in sorted(objs):
            e = objs[letter]
            print(f'        "{letter}": {{')
            print(f'            "deliverable": {e["deliverable"]!r},')
            print(f'            "how": {e["how"]!r},')
            print(f'            "kind": {e["kind"]!r},')
            print(f"        }},")
        print(f"    }},")

if __name__ == "__main__":
    generate()
