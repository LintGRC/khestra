"""Guard: no live secrets may ever be committed to the repo.

Scans tracked source files for obvious live-key patterns. Placeholders like
"sk-your-key-here" in .env.example are fine (they don't match the patterns).
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "cmmc_data",
    "data",
    "demo_data",
    "fixtures",
    "samples",
    "khestra",
    "control_mappings",
    "control_mappings_enriched",
    "reference",
}

EXCLUDE_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".xlsx", ".zip", ".woff", ".woff2", ".ttf", ".svg", ".ico", ".lock"}

# Patterns are assembled from parts so this test file itself contains no
# live-looking key literal that a naive grep would flag.
LIVE_KEY_PATTERNS = [
    re.compile(r"sk-" + r"[A-Za-z0-9]" + r"{16,}"),
    re.compile(r"AKIA" + r"[0-9A-Z]" + r"{16}"),
    re.compile(r"-----BEGIN " + r"(RSA |EC |OPENSSH |ENCRYPTED )?" + r"PRIVATE KEY-----"),
    re.compile(r"ghp_" + r"[A-Za-z0-9]" + r"{30,}"),
    re.compile(r"xox[baprs]-" + r"[A-Za-z0-9-]{10,}"),
]


def _candidate_files():
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.suffix in EXCLUDE_SUFFIXES:
            continue
        if "site-packages" in path.parts:
            continue
        yield path


def test_no_live_secret_patterns_in_repo():
    violations = []
    for path in _candidate_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in LIVE_KEY_PATTERNS:
            match = pattern.search(text)
            if match:
                violations.append(f"{path.relative_to(REPO)}: {pattern.pattern} matched")
    assert not violations, (
        "Possible live secrets in tracked files:\n" + "\n".join(violations[:10])
    )


def test_example_env_placeholder_is_safe():
    example = REPO / "apps" / "cmmc" / ".env.example"
    text = example.read_text(encoding="utf-8")
    assert "sk-your-key-here" in text
    for pattern in LIVE_KEY_PATTERNS:
        assert pattern.search(text) is None, pattern.pattern
