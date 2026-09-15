"""Extract per-control E/I/T assessment methods from NIST SP 800-171A (2018).

Reads the pdftotext output, parses each control's requirement, determination
statements, and Potential Assessment Methods and Objects (Examine/Interview/Test),
then writes NIST_EIT_REFERENCE dict to a companion Python file.
"""

import re
import sys
from pathlib import Path

NIST_FAMILIES: dict[int, str] = {
    1: "AC", 2: "AT", 3: "AU", 4: "CM",
    5: "IA", 6: "IR", 7: "MA", 8: "MP",
    9: "PS", 10: "PE", 11: "RA", 12: "CA",
    13: "SC", 14: "SI",
}

OUT_DIR = Path(__file__).resolve().parent
TEXT_PATH = Path("/tmp/nist800171a.txt")
OUT_PATH = OUT_DIR / "nist_eit_reference.py"


NOISE_RE = re.compile(
    r"^CHAPTER THREE$|^PAGE \d+$|^NIST SP 800-171A$|^ASSESSING SECURITY|"
    r"^This publication is available free|"
    r"^\_{2,}$"
)
CTRL_ID_RE = re.compile(r"^3\.(\d+)\.(\d+)$")
OBJ_LABEL_RE = re.compile(r"^3\.\d+\.\d+\[([a-z])\]$")
HEADER_RE = re.compile(r"^3\.(\d+) (.+)")


def strip_noise(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        s = line.strip()
        if s and not NOISE_RE.match(s):
            result.append(s)
    return result


def cmmc_id(fam: int, num: int) -> str:
    return f"{NIST_FAMILIES[fam]}.L2-3.{fam}.{num}"


def parse():
    if not TEXT_PATH.exists():
        print(f"ERROR: {TEXT_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    raw = TEXT_PATH.read_text()
    lines = strip_noise(raw.splitlines())

    result: dict[str, dict] = {}

    ctrl_id = ""
    requirement: list[str] = []
    objectives: dict[str, str] = {}
    curr_obj = ""
    objectives_state = False
    eit_text: list[str] = []
    collecting_eit = False
    started = False

    for line in lines:
        if not started:
            m = HEADER_RE.match(line)
            if m:
                started = True
            continue

        # --- Family headers ---
        m = HEADER_RE.match(line)
        if m or CTRL_ID_RE.match(line):
            if ctrl_id and objectives and eit_text:
                _flush(ctrl_id, requirement, objectives, eit_text, result)

            if m:
                pass
            elif CTRL_ID_RE.match(line):
                mm = CTRL_ID_RE.match(line)
                ctrl_id = cmmc_id(int(mm.group(1)), int(mm.group(2)))
                requirement = []
                objectives = {}
                curr_obj = ""
                objectives_state = False
                eit_text = []
                collecting_eit = False
            continue

        if not ctrl_id:
            continue

        # SECURITY REQUIREMENT
        if line == "SECURITY REQUIREMENT":
            requirement = []
            continue

        if line == "ASSESSMENT OBJECTIVE":
            objectives_state = True
            continue

        # Determine if: — lettered objectives follow
        if line == "Determine if:":
            objectives_state = True
            continue

        # Determine if <text> — single inline objective
        if line.startswith("Determine if"):
            text = line[len("Determine if"):].lstrip(": ").strip()
            if text and not text.endswith("."):
                text += "."
            objectives["a"] = text
            objectives_state = True
            continue

        # POTENTIAL ASSESSMENT METHODS — start EIT collection
        if "POTENTIAL ASSESSMENT" in line:
            if curr_obj and objectives_state:
                objectives[curr_obj] = objectives.get(curr_obj, "")
                curr_obj = ""
            objectives_state = False
            collecting_eit = True
            eit_text = []
            continue

        # Objective label: 3.1.1[a]
        m = OBJ_LABEL_RE.match(line)
        if m:
            if curr_obj and objectives_state:
                objectives[curr_obj] = objectives.get(curr_obj, "")
            curr_obj = m.group(1)
            objectives[curr_obj] = ""
            continue

        # Collect objective text
        if objectives_state and curr_obj:
            objectives[curr_obj] = (objectives[curr_obj] + " " + line).strip()
            continue

        # Collect EIT text
        if collecting_eit:
            eit_text.append(line)
            continue

        # Collect requirement text
        if not objectives_state and not collecting_eit:
            requirement.append(line)
            continue

    # Flush last control
    if ctrl_id and objectives:
        _flush(ctrl_id, requirement, objectives, eit_text, result)

    # Convert result to dict keyed by CMMC control ID
    write_output(result)


def _flush(ctrl_id, requirement, objectives, eit_text, result):
    eit_parsed = parse_eit(eit_text)
    result[ctrl_id] = {
        "requirement": " ".join(requirement).strip(),
        "objectives": dict(sorted(objectives.items())),
        "examine": eit_parsed.get("examine", ""),
        "interview": eit_parsed.get("interview", ""),
        "test": eit_parsed.get("test", ""),
    }


def parse_eit(lines: list[str]) -> dict[str, str]:
    """Parse EIT text into examine/interview/test sections."""
    result = {}
    current = ""
    current_label = ""
    for line in lines:
        if line.startswith("Examine:"):
            if current_label:
                result[current_label] = current.strip()
            current_label = "examine"
            current = line[len("Examine:"):].strip()
        elif line.startswith("Interview:"):
            if current_label:
                result[current_label] = current.strip()
            current_label = "interview"
            current = line[len("Interview:"):].strip()
        elif line.startswith("Test:"):
            if current_label:
                result[current_label] = current.strip()
            current_label = "test"
            current = line[len("Test:"):].strip()
        elif current_label and line:
            current += " " + line
    if current_label:
        result[current_label] = current.strip()
    return result


def write_output(result: dict):
    items = sorted(result.items())
    lines = [
        "# Auto-generated by extract_nist_eit.py — DO NOT EDIT BY HAND",
        f"# Total controls: {len(items)}",
        "",
        "NIST_EIT_REFERENCE: dict[str, dict] = {",
    ]
    for cid, data in items:
        lines.append(f'    {cid!r}: {{')
        lines.append(f'        "requirement": {data["requirement"]!r},')
        objectives_list = list(data["objectives"].items())
        if len(objectives_list) == 1 and list(data["objectives"].keys())[0] == "a":
            # Single objective Format B — keep compact
            pass
        lines.append(f'        "objectives": {{')
        for k, v in objectives_list:
            lines.append(f'            {k!r}: {v!r},')
        lines.append(f"        }},")
        for key in ("examine", "interview", "test"):
            lines.append(f'        {key!r}: {data.get(key, "")!r},')
        lines.append(f"    }},")
    lines.append("}")
    lines.append("")
    out = "\n".join(lines)
    OUT_PATH.write_text(out)
    print(f"Wrote {len(items)} controls to {OUT_PATH}")


if __name__ == "__main__":
    parse()
