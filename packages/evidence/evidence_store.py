"""Compatibility re-exports — replaces per-app evidence_store.py copies.

All functions now live in filestore.py. This module re-exports them so
existing imports like `from evidence_store import get_evidence_bytes` keep working
without updating every consumer across CMMC, SOC2, and AI Gov.
"""

from filestore import (  # noqa: F401
    answers_without_evidence_bytes,
    evidence_file_key,
    get_evidence_bytes,
    load_evidence_from_disk,
    persist_evidence_to_disk,
    read_evidence_file_from_disk,
    safe_evidence_filename,
    verify_evidence_hash,
)
