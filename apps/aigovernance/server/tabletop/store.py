import json, os
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

DATA_DIR: str | None = None
_store: list[dict] | None = None


def init_store(data_dir: str):
    global DATA_DIR, _store
    DATA_DIR = data_dir
    _store = None
    _load()


def _path() -> Path:
    return Path(DATA_DIR) / "tabletop_exercises.json"


def _load() -> list[dict]:
    global _store
    if _store is not None:
        return _store
    p = _path()
    if p.exists():
        _store = json.loads(p.read_text())
    else:
        _store = []
    return _store


def _save():
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(_store, indent=2, default=str))
    os.replace(tmp, p)


def _id() -> str:
    return uuid4().hex[:12]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def list_exercises() -> list[dict]:
    return _load()


def get_exercise(eid: str) -> dict | None:
    for e in _load():
        if e["id"] == eid:
            return e
    return None


def create_exercise(scenario: dict, responses: list[dict], participants: list[str]) -> dict:
    s = _load()
    eid = _id()
    scores = []
    for step in scenario["steps"]:
        resp = next((r for r in responses if r["step"] == step["step"]), None)
        answer = (resp or {}).get("answer", "")
        from .scoring import score_step
        scores.append(score_step(step, answer))

    from .scoring import calculate_overall, generate_recommendations
    overall_pct = calculate_overall(scores)
    recommendations = generate_recommendations(scores)

    now = _now()
    exercise = {
        "id": eid,
        "scenarioId": scenario["id"],
        "scenarioTitle": scenario["title"],
        "scenarioType": scenario["type"],
        "status": "completed",
        "participants": participants,
        "responses": responses,
        "scores": scores,
        "overallScore": round(overall_pct * len(scores) / 100) if scores else 0,
        "overallPercentage": overall_pct,
        "recommendations": recommendations,
        "startedAt": now,
        "completedAt": now,
    }
    s.append(exercise)
    _save()
    return exercise


def delete_exercise(eid: str) -> bool:
    s = _load()
    for i, e in enumerate(s):
        if e["id"] == eid:
            s.pop(i)
            _save()
            return True
    return False
