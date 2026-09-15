"""Local security helpers for evidence and workspace import."""

import zipfile
from io import BytesIO
from typing import BinaryIO

MAX_ZIP_MEMBERS = 500
MAX_ZIP_UNCOMPRESSED_MB = 100
MAX_EVIDENCE_FILENAME_LEN = 200
ALLOWED_EVIDENCE_EXTENSIONS = frozenset(
    {".pdf", ".png", ".jpg", ".jpeg", ".json", ".conf", ".txt", ".csv", ".docx", ".xlsx"}
)


def safe_evidence_filename(name: str) -> str:
    base = (name or "file").replace("\\", "/").split("/")[-1]
    base = "".join(c for c in base if c.isalnum() or c in "._- ")
    return base[:MAX_EVIDENCE_FILENAME_LEN] or "evidence_file"


def validate_workspace_zip(uploaded_file) -> tuple[bool, str]:
    """Reject zip bombs and unexpected archive structure."""
    try:
        raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
        uploaded_file.seek(0) if hasattr(uploaded_file, "seek") else None
        total_uncompressed = 0
        with zipfile.ZipFile(BytesIO(raw)) as zf:
            if "state.json" not in zf.namelist():
                return False, "Missing state.json in workspace archive."
            if len(zf.namelist()) > MAX_ZIP_MEMBERS:
                return False, f"Archive has too many files (max {MAX_ZIP_MEMBERS})."
            for info in zf.infolist():
                total_uncompressed += info.file_size
                if total_uncompressed > MAX_ZIP_UNCOMPRESSED_MB * 1024 * 1024:
                    return False, f"Archive exceeds {MAX_ZIP_UNCOMPRESSED_MB}MB uncompressed limit."
                if ".." in info.filename or info.filename.startswith("/"):
                    return False, "Invalid path in archive."
        return True, ""
    except zipfile.BadZipFile:
        return False, "File is not a valid ZIP archive."
    except Exception as exc:
        return False, str(exc)
