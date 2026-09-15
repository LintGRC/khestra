#!/usr/bin/env python3
"""Open-core leak check for the public Khestra tree.

Standalone (no closed packages required) and CI-safe. Fails on:
  1. collector check-id shaped tokens (connector prefix + slug)
  2. forbidden secret / demo-credential strings
  3. module-level imports of the closed `collectors` package
  4. catalog regressions (CMMC / SOC 2 / ISO 27001 control counts)

The closed 152-check inventory is intentionally NOT embedded here (that list
is itself closed). Exact-inventory parity is enforced in the private monorepo;
this check enforces the shape/prefix rule plus the other guardrails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {".git", "__pycache__", "node_modules", "dist", ".venv", "venv", "build"}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".xlsx", ".zip",
    ".woff", ".woff2", ".ttf", ".ico", ".svg", ".lock", ".drawio",
}
SKIP_FILES = {"leak_check.py"}

CHECK_ID_SHAPE = re.compile(
    r"\b(aws|azure|gcp|entra|intune|okta|duo|github|jira|linear|jumpcloud|"
    r"kandji|jamf|bamboo|cloudflare|crowdstrike|splunk|tenable|sentinel|google)"
    r"-[a-z0-9][a-z0-9-]+"
)
# Tokens that match the shape but are not collector check ids.
SHAPE_ALLOWLIST = {"crowdstrike-edge", "linear-gradient", "github-actions"}

SECRET_PATTERNS = [
    ("changeme", re.compile(r"changeme", re.I)),
    ("IStingEm", re.compile(r"IStingEm")),
    ("vibe-shield", re.compile(r"vibe-shield")),
    ("vibeshield", re.compile(r"vibeshield")),
    ("septr-python", re.compile(r"septr-python")),
    ("SecurePass789", re.compile(r"SecurePass789")),
    ("admin@localhost", re.compile(r"admin@localhost")),
    ("demo-token", re.compile(r"demo-token")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9]{16,}")),
]

CLOSED_IMPORT = re.compile(r"^(from\s+collectors[.\s]|import\s+collectors\b)")


def files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in SKIP_SUFFIXES or p.name in SKIP_FILES:
            continue
        yield p


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def main() -> int:
    shape_hits, secret_hits, import_hits = [], [], []
    for p in files():
        rel = p.relative_to(ROOT)
        text = read(p)
        for m in CHECK_ID_SHAPE.finditer(text):
            if m.group(0) not in SHAPE_ALLOWLIST:
                line = text[: m.start()].count("\n") + 1
                shape_hits.append(f"{rel}:{line}: {m.group(0)}")
        for name, pat in SECRET_PATTERNS:
            m = pat.search(text)
            if m:
                line = text[: m.start()].count("\n") + 1
                secret_hits.append(f"{rel}:{line}: {name}")
        if p.suffix == ".py":
            for i, line in enumerate(text.splitlines(), 1):
                if CLOSED_IMPORT.match(line):
                    import_hits.append(f"{rel}:{i}: {line.strip()[:80]}")

    # Catalog completeness
    counts = {}
    cmmc = ROOT / "apps/cmmc/core/controls.py"
    soc2 = ROOT / "apps/soc2/core/soc2_catalog.py"
    iso_candidates = [
        ROOT / "apps/iso27001/core/controls.py",
        ROOT / "apps/iso27001/core/iso_27001_official.py",
    ]
    if cmmc.exists():
        counts["CMMC"] = len(re.findall(r'"[A-Z]{2}\.L2-3\.\d+\.\d+"', read(cmmc)))
    if soc2.exists():
        counts["SOC2"] = len(re.findall(r'"(?:CC\d+\.\d+|[A-P]\d+\.\d+)"', read(soc2)))
    for iso in iso_candidates:
        if iso.exists():
            counts["ISO27001"] = len(re.findall(r'"A\.\d+\.\d+"', read(iso)))
            break

    ok = True
    print("=== open-core leak check ===")
    for label, hits in (
        ("check-id shape", shape_hits),
        ("secret strings", secret_hits),
        ("closed imports", import_hits),
    ):
        if hits:
            ok = False
            print(f"FAIL: {len(hits)} {label}")
            for h in hits[:10]:
                print(f"  {h}")
        else:
            print(f"PASS: zero {label} leaks")

    expected = {"CMMC": 110, "SOC2": 60, "ISO27001": 30}
    for fw, minimum in expected.items():
        n = counts.get(fw, 0)
        status = "PASS" if n >= minimum else "FAIL"
        if n < minimum:
            ok = False
        print(f"{status}: {fw} catalog = {n} (min {minimum})")

    print("ALL CHECKS PASSED" if ok else "LEAK CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
