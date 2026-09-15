"""Workspace service for AI Governance — wraps evidence_store for the AI controls framework."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from evidence_store import (
    evidence_file_key,
    persist_evidence_to_disk,
    load_evidence_from_disk,
    verify_evidence_hash,
)
from client_workspaces import (
    client_evidence_dir,
    client_session_path,
    resolve_client_dir,
    DEFAULT_CLIENT_ID,
)
from ai_controls_catalog import AI_GOV_FRAMEWORK
from guidance.objectives_data import AI_GENERATED_CONTROL_OBJECTIVES


def default_workspace() -> Dict[str, Any]:
    return {
        "answers": {cid: _default_answer(cid) for cid in AI_GOV_FRAMEWORK},
        "org_profile": {"org_name": "Default Organization", "plan": "trial"},
    }


def _default_answer(cid: str) -> Dict[str, Any]:
    ans = {"status": "NOT_MET", "implementation_narrative": "", "evidence": []}
    objs = AI_GENERATED_CONTROL_OBJECTIVES.get(cid, [])
    if objs:
        ans["examine"] = objs[0] if len(objs) > 0 else ""
        ans["interview"] = objs[1] if len(objs) > 1 else ""
        ans["test"] = objs[2] if len(objs) > 2 else ""
        ans["obj_examine_done"] = False
        ans["obj_interview_done"] = False
        ans["obj_test_done"] = False
    return ans


def load_workspace(client_id: Optional[str] = None) -> Dict[str, Any]:
    cid = client_id or DEFAULT_CLIENT_ID
    path = client_session_path(cid)
    if not path.exists():
        ws = default_workspace()
        save_workspace(ws, cid)
        return ws
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Ensure all controls have entries and objectives
        for cid_key in AI_GOV_FRAMEWORK:
            ans = data.setdefault("answers", {}).setdefault(cid_key, _default_answer(cid_key))
            if "examine" not in ans:
                objs = AI_GENERATED_CONTROL_OBJECTIVES.get(cid_key, [])
                ans["examine"] = objs[0] if len(objs) > 0 else ""
                ans["interview"] = objs[1] if len(objs) > 1 else ""
                ans["test"] = objs[2] if len(objs) > 2 else ""
                ans["obj_examine_done"] = ans.get("obj_examine_done", False)
                ans["obj_interview_done"] = ans.get("obj_interview_done", False)
                ans["obj_test_done"] = ans.get("obj_test_done", False)
        return data
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Corrupt workspace file {path}, resetting to default workspace", file=sys.stderr)
        ws = default_workspace()
        save_workspace(ws, cid)
        return ws


def save_workspace(ws: Dict[str, Any], client_id: Optional[str] = None) -> None:
    cid = client_id or DEFAULT_CLIENT_ID
    path = client_session_path(cid)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Persist evidence to disk, then save session without bytes
    evd_dir = client_evidence_dir(cid)
    restored = load_evidence_from_disk(evd_dir)
    persist_evidence_to_disk(ws.get("answers", {}), evd_dir, restored_evidence=restored)
    # Save workspace without evidence bytes
    clean = _without_evidence_bytes(ws)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def attach_evidence(
    ws: Dict[str, Any],
    control_id: str,
    filename: str,
    data: bytes,
    sha256: str,
    upload_date: str,
) -> Dict[str, Any]:
    answers = ws.setdefault("answers", {})
    if control_id not in answers:
        answers[control_id] = {"status": "NOT_MET", "implementation_narrative": "", "evidence": []}
    answers[control_id].setdefault("evidence", []).append({
        "filename": filename,
        "upload_date": upload_date,
        "sha256": sha256,
        "data_bytes": data,
    })
    return ws


def _without_evidence_bytes(ws: Dict[str, Any]) -> Dict[str, Any]:
    clean: Dict[str, Any] = {}
    for cid, ans in ws.get("answers", {}).items():
        row = dict(ans)
        evs = []
        for ev in ans.get("evidence") or []:
            evs.append({k: v for k, v in ev.items() if k != "data_bytes"})
        row["evidence"] = evs
        clean[cid] = row
    return {"answers": clean, **{k: v for k, v in ws.items() if k != "answers"}}
