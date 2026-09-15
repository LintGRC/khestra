"""Tests for policy approval workflow state machine."""

import os
import sys
from pathlib import Path

import pytest

PACKAGES = Path(__file__).resolve().parents[2]
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))

from policies.store import (
    init_store,
    create_document,
    update_document,
    get_document,
    delete_document,
    submit_for_review,
    approve_document,
    publish_document,
    reject_document,
    create_attestation,
    list_attestations,
    list_documents,
)


@pytest.fixture(autouse=True)
def _db():
    tmp = f"/tmp/test_policies_{os.urandom(4).hex()}.db"
    os.environ["POLICIES_DB_PATH"] = tmp
    init_store("/tmp")
    yield
    try:
        os.remove(tmp)
    except OSError:
        pass


def _create_doc(**kw) -> dict:
    return create_document(
        title=kw.get("title", "Test Policy"),
        description=kw.get("description", "test"),
        content=kw.get("content", "# Test"),
        owner=kw.get("owner", "admin"),
    )


class TestDocumentCRUD:
    def test_create_document(self):
        doc = _create_doc(title="Access Control Policy")
        assert doc["title"] == "Access Control Policy"
        assert doc["status"] == "draft"
        assert doc["version"] == 1
        assert doc["id"]

    def test_get_document_returns_none_for_missing(self):
        assert get_document("nonexistent") is None

    def test_get_document_returns_doc(self):
        doc = _create_doc()
        fetched = get_document(doc["id"])
        assert fetched is not None
        assert fetched["id"] == doc["id"]

    def test_update_document_title(self):
        doc = _create_doc()
        updated = update_document(doc["id"], title="Updated Title")
        assert updated
        assert updated["title"] == "Updated Title"
        assert updated["version"] == 2

    def test_delete_document_removes_it(self):
        doc = _create_doc()
        assert delete_document(doc["id"]) is True
        assert get_document(doc["id"]) is None

    def test_delete_nonexistent_returns_false(self):
        assert delete_document("nope") is False

    def test_list_documents_includes_new_doc(self):
        doc = _create_doc()
        docs = list_documents()
        assert any(d["id"] == doc["id"] for d in docs)


class TestApprovalWorkflow:
    def test_draft_to_under_review(self):
        doc = _create_doc()
        result = submit_for_review(doc["id"], submitted_by="assessor")
        assert result
        assert result["status"] == "under_review"

    def test_draft_to_under_review_missing_doc(self):
        assert submit_for_review("nope") is None

    def test_under_review_to_approved(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        result = approve_document(doc["id"], approved_by="manager")
        assert result
        assert result["status"] == "approved"
        assert result["approved_by"] == "manager"
        assert result["approved_at"]
        assert result["next_review_date"]

    def test_approved_to_published(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        approve_document(doc["id"])
        result = publish_document(doc["id"])
        assert result
        assert result["status"] == "published"

    def test_under_review_to_draft_on_rejection(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        result = reject_document(doc["id"], rejection_notes="Needs revision", rejected_by="manager")
        assert result
        assert result["status"] == "draft"
        assert result["rejection_notes"] == "Needs revision"

    def test_rejected_doc_can_be_resubmitted(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        reject_document(doc["id"])
        result = submit_for_review(doc["id"])
        assert result
        assert result["status"] == "under_review"

    def test_full_cycle_draft_to_published(self):
        doc = _create_doc()
        assert doc["status"] == "draft"
        doc = submit_for_review(doc["id"])
        assert doc["status"] == "under_review"
        doc = approve_document(doc["id"])
        assert doc["status"] == "approved"
        doc = publish_document(doc["id"])
        assert doc["status"] == "published"


class TestInvalidTransitions:
    def test_cannot_submit_already_submitted(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        with pytest.raises(ValueError, match="must be 'draft'"):
            submit_for_review(doc["id"])

    def test_cannot_approve_draft(self):
        doc = _create_doc()
        with pytest.raises(ValueError, match="must be 'under_review'"):
            approve_document(doc["id"])

    def test_cannot_approve_published(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        approve_document(doc["id"])
        publish_document(doc["id"])
        with pytest.raises(ValueError, match="must be 'under_review'"):
            approve_document(doc["id"])

    def test_cannot_publish_draft(self):
        doc = _create_doc()
        with pytest.raises(ValueError, match="must be 'approved'"):
            publish_document(doc["id"])

    def test_cannot_publish_under_review(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        with pytest.raises(ValueError, match="must be 'approved'"):
            publish_document(doc["id"])

    def test_cannot_reject_draft(self):
        doc = _create_doc()
        with pytest.raises(ValueError, match="must be 'under_review'"):
            reject_document(doc["id"])

    def test_cannot_reject_approved(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        approve_document(doc["id"])
        with pytest.raises(ValueError, match="must be 'under_review'"):
            reject_document(doc["id"])

    def test_cannot_reject_published(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        approve_document(doc["id"])
        publish_document(doc["id"])
        with pytest.raises(ValueError, match="must be 'under_review'"):
            reject_document(doc["id"])

    def test_cannot_approve_nonexistent(self):
        doc = create_document("Temp")
        delete_document(doc["id"])
        assert approve_document(doc["id"]) is None

    def test_cannot_submit_already_published(self):
        doc = _create_doc()
        submit_for_review(doc["id"])
        approve_document(doc["id"])
        publish_document(doc["id"])
        with pytest.raises(ValueError, match="must be 'draft'"):
            submit_for_review(doc["id"])


class TestAttestations:
    def test_create_attestation(self):
        doc = _create_doc()
        att = create_attestation(doc["id"], user_name="Alice", user_id="user1", notes="Acknowledged")
        assert att
        assert att["user_name"] == "Alice"
        assert att["policy_id"] == doc["id"]

    def test_attestation_nonexistent_policy(self):
        assert create_attestation("nope", "Alice") is None

    def test_duplicate_attestation_prevention(self):
        doc = _create_doc()
        att1 = create_attestation(doc["id"], user_name="Alice", user_id="user1")
        assert att1
        assert att1.get("duplicate") is None or not att1.get("duplicate")
        att2 = create_attestation(doc["id"], user_name="Alice", user_id="user1")
        assert att2
        assert att2.get("duplicate") is True

    def test_list_attestations_by_policy(self):
        doc = _create_doc()
        create_attestation(doc["id"], user_name="Alice", user_id="user1")
        create_attestation(doc["id"], user_name="Bob", user_id="user2")
        atts = list_attestations(policy_id=doc["id"])
        assert len(atts) == 2

    def test_list_all_attestations(self):
        doc = _create_doc()
        create_attestation(doc["id"], user_name="Alice", user_id="user1")
        atts = list_attestations()
        assert len(atts) >= 1
