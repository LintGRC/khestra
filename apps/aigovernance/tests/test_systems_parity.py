import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.main import app  # noqa: F401,E402 — app import exercised via conftest client fixture


def test_systems_support_parity_fields_and_filters(client):
    payload = {
        "name": "Widget Copilot",
        "description": "Customer support copilot",
        "risk_classification": "high",
        "owner": "Ops",
        "deployment_status": "production",
        "purpose": "Support automation",
        "version": "1.2.0",
        "review_date": "2026-07-15",
        "review_owner": "Compliance",
        "approval_status": "submitted",
        "evidence_links": [{"name": "Policy", "url": "https://example.com/policy"}],
        "tags": ["customer", "support"],
    }

    create_resp = client.post("/api/systems", json=payload)
    assert create_resp.status_code == 200
    sid = create_resp.json()["id"]

    fetch_resp = client.get(f"/api/systems/{sid}")
    assert fetch_resp.status_code == 200
    system = fetch_resp.json()["system"]
    assert system["version"] == "1.2.0"
    assert system["review_owner"] == "Compliance"
    assert system["approval_status"] == "submitted"
    assert system["evidence_links"][0]["name"] == "Policy"

    filtered_resp = client.get("/api/systems", params={"q": "Widget", "status": "production", "tier": "high", "tag": "customer"})
    assert filtered_resp.status_code == 200
    body = filtered_resp.json()
    assert body["total"] >= 1
    assert any(item["id"] == sid for item in body["systems"])
