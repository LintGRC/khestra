import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.main import app  # noqa: F401,E402 — app import exercised via conftest client fixture


def test_vendor_intake_supports_rich_metadata_and_filters(client):
    payload = {
        "name": "Northwind AI",
        "contactName": "Aisha",
        "contactEmail": "aisha@northwind.ai",
        "category": "NLP",
        "aiServiceType": "LLM",
        "tier": "2",
        "status": "pending",
        "riskLevel": "medium",
        "tags": ["critical", "ai"],
        "dataResidency": ["EU"],
        "transferMechanism": "SCCs",
        "dpaInPlace": True,
        "certificates": ["SOC 2"],
        "reviewDate": "2026-07-20",
        "reviewOwner": "Compliance",
        "approvalStatus": "submitted",
    }

    create_resp = client.post("/api/vendor-intake/vendors", json=payload)
    assert create_resp.status_code == 200

    vendor = create_resp.json()["vendor"]
    vid = vendor["id"]

    fetch_resp = client.get(f"/api/vendor-intake/vendors/{vid}")
    assert fetch_resp.status_code == 200
    fetched = fetch_resp.json()["vendor"]
    assert fetched["category"] == "NLP"
    assert fetched["aiServiceType"] == "LLM"
    assert fetched["reviewOwner"] == "Compliance"
    assert fetched["approvalStatus"] == "submitted"
    assert fetched["certificates"] == ["SOC 2"]

    filtered_resp = client.get(
        "/api/vendor-intake/vendors",
        params={"q": "Northwind", "status": "pending", "tier": "2", "tag": "critical"},
    )
    assert filtered_resp.status_code == 200
    body = filtered_resp.json()
    assert body["total"] >= 1
    assert any(item["id"] == vid for item in body["vendors"])
