"""Tests for the plan-centric API and the PRD failure scenarios (section 14.1)."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services import compliance_service, identity_service, scoring_service
from backend.app.services.plan_drafting_service import draft_plan_items
from backend.app.services.plan_service import plan_store


@pytest.fixture(autouse=True)
def _isolate_state():
    plan_store.reset()
    scoring_service.reset_scoring_rules()
    yield
    plan_store.reset()
    scoring_service.reset_scoring_rules()


client = TestClient(app)


def _create_plan(territory_id: str = "T001", user_id: str = "mgr-001") -> dict:
    response = client.post(
        "/v1/plans", json={"territory_id": territory_id, "user_id": user_id}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_health_endpoint_reports_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_correlation_id_header_is_returned():
    response = client.get("/health")
    assert response.headers.get("X-Correlation-ID")


def test_create_plan_has_cited_items_and_no_llm_math():
    plan = _create_plan("T001")
    assert plan["status"] == "PENDING_APPROVAL"
    assert plan["items"], "expected at least one plan item"
    for item in plan["items"]:
        assert item["citations"], "every item must cite evidence (FR-22)"
        assert item["facts"], "every item must expose its facts (FR-20)"
        for fact in item["facts"]:
            assert fact["source_id"]
    # Numeric ranking is produced deterministically (FR-10).
    ranks = [item["priority_rank"] for item in plan["items"]]
    scores = [item["priority_score"] for item in plan["items"]]
    assert ranks == list(range(1, len(ranks) + 1))
    assert scores == sorted(scores, reverse=True)


def test_unresolved_service_issue_changes_next_action():
    plan = _create_plan("T001")
    by_account = {item["account_id"]: item for item in plan["items"]}
    issue_item = by_account["ACC1002"]
    assert "Resolve the open service issue" in issue_item["recommended_action"]


def test_service_issue_account_is_not_blindly_top_ranked():
    """FR-13: high opportunity value alone must not guarantee top priority."""
    plan = _create_plan("T002", "mgr-002")
    by_account = {item["account_id"]: item for item in plan["items"]}
    # ACC2002 has a HIGH service issue and a lower score than the healthy account.
    assert by_account["ACC2002"]["priority_rank"] > by_account["ACC2001"]["priority_rank"]


def test_ownership_conflict_is_flagged_and_plan_validation_fails():
    plan = _create_plan("T002", "mgr-002")
    by_account = {item["account_id"]: item for item in plan["items"]}
    conflict = by_account["ACC2002"]
    assert conflict["compliance"]["status"] == "failed"
    assert "ownership" in conflict["recommended_action"].lower() or "ownership" in (
        conflict["reason"].lower()
    )
    assert plan["validation"]["status"] == "failed"  # FR-26/FR-28


def test_stale_record_is_flagged_not_guessed():
    plan = _create_plan("T001")
    by_account = {item["account_id"]: item for item in plan["items"]}
    assert by_account["ACC1002"]["stale"] is True
    assert by_account["ACC1002"]["stale_reason"]
    assert plan["stale_data"] is True


def test_unknown_territory_returns_404():
    response = client.post(
        "/v1/plans", json={"territory_id": "T999", "user_id": "mgr-001"}
    )
    assert response.status_code == 404


def test_unauthenticated_or_unauthorized_returns_403():
    # Unknown user cannot retrieve anything (FR-8/FR-24).
    assert (
        client.post(
            "/v1/plans", json={"territory_id": "T001", "user_id": "nobody"}
        ).status_code
        == 403
    )
    # Manager of T001 cannot request T002 accounts.
    assert (
        client.post(
            "/v1/plans", json={"territory_id": "T002", "user_id": "mgr-001"}
        ).status_code
        == 403
    )


def test_get_unknown_plan_returns_404():
    assert client.get("/v1/plans/plan-does-not-exist").status_code == 404


def test_edit_plan_bumps_version_and_is_blocked_after_approval():
    plan = _create_plan("T001")
    item = plan["items"][0]
    edited = client.patch(
        f"/v1/plans/{plan['plan_id']}",
        json={
            "user_id": "mgr-001",
            "items": [
                {
                    "item_id": item["item_id"],
                    "recommended_action": "Call the executive sponsor this week.",
                    "reason": "Manager judgement applied.",
                }
            ],
        },
    )
    assert edited.status_code == 200
    assert edited.json()["version"] == 2
    assert edited.json()["items"][0]["recommended_action"] == (
        "Call the executive sponsor this week."
    )

    approved = client.post(
        f"/v1/plans/{plan['plan_id']}/approve", json={"user_id": "mgr-001"}
    )
    assert approved.status_code == 200
    blocked = client.patch(
        f"/v1/plans/{plan['plan_id']}",
        json={"user_id": "mgr-001", "items": [{"item_id": item["item_id"], "reason": "x"}]},
    )
    assert blocked.status_code == 409


def test_only_a_manager_can_approve():
    plan = _create_plan("T001")
    response = client.post(
        f"/v1/plans/{plan['plan_id']}/approve", json={"user_id": "rep-042"}
    )
    assert response.status_code == 403


def test_approval_is_recorded_with_user_and_version():
    plan = _create_plan("T001")
    response = client.post(
        f"/v1/plans/{plan['plan_id']}/approve",
        json={"user_id": "mgr-001", "reason": "Looks good."},
    )
    body = response.json()
    assert body["status"] == "APPROVED"
    assert body["approval"]["approver_id"] == "mgr-001"
    assert body["approval"]["plan_version"] == plan["version"]
    assert body["approval"]["item_ids"]


def test_reject_marks_items_and_blocks_export():
    plan = _create_plan("T001")
    rejected = client.post(
        f"/v1/plans/{plan['plan_id']}/reject",
        json={"user_id": "mgr-001", "reason": "Not this quarter."},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "REJECTED"
    export = client.post(f"/v1/plans/{plan['plan_id']}/export?format=csv")
    assert export.status_code == 409  # nothing approved (FR-34 guard)


def test_export_requires_approval_then_is_idempotent():
    plan = _create_plan("T001")
    # Not approved yet -> cannot export.
    assert client.post(f"/v1/plans/{plan['plan_id']}/export?format=csv").status_code == 409

    client.post(f"/v1/plans/{plan['plan_id']}/approve", json={"user_id": "mgr-001"})

    first = client.post(
        f"/v1/plans/{plan['plan_id']}/export?format=csv",
        headers={"Idempotency-Key": "export-1"},
    )
    assert first.status_code == 200
    assert first.json()["format"] == "csv"
    assert first.json()["item_count"] == len(plan["items"])

    # Same idempotency key replays the original export exactly.
    replay = client.post(
        f"/v1/plans/{plan['plan_id']}/export?format=csv",
        headers={"Idempotency-Key": "export-1"},
    )
    assert replay.json()["export_id"] == first.json()["export_id"]

    # A different key with the same content is detected as a duplicate (FR-34).
    duplicate = client.post(f"/v1/plans/{plan['plan_id']}/export?format=csv")
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate"] is True
    assert duplicate.json()["export_id"] == first.json()["export_id"]


def test_audit_trail_records_lifecycle_events():
    plan = _create_plan("T001")
    client.post(f"/v1/plans/{plan['plan_id']}/approve", json={"user_id": "mgr-001"})
    client.post(f"/v1/plans/{plan['plan_id']}/export?format=json")
    trail = client.get(f"/v1/plans/{plan['plan_id']}/audit").json()
    event_types = [event["event_type"] for event in trail["events"]]
    assert event_types[0] == "PLAN_CREATED"
    assert "PLAN_APPROVED" in event_types
    assert "PLAN_EXPORTED" in event_types
    for event in trail["events"]:
        assert event["actor"]
        assert event["timestamp"]


def test_list_plans_returns_summaries():
    _create_plan("T001")
    _create_plan("T003", "mgr-003")
    summaries = client.get("/v1/plans").json()
    assert len(summaries) == 2
    assert {s["territory_id"] for s in summaries} == {"T001", "T003"}


def test_scoring_rules_are_configurable_without_code_changes():
    before = client.get("/v1/scoring-rules").json()
    assert "weights" in before
    updated = client.put(
        "/v1/scoring-rules",
        json={"thresholds": {"high": 60.0, "medium": 30.0}},
    )
    assert updated.status_code == 200
    assert updated.json()["thresholds"]["high"] == 60.0


# -- regression / failure-scenario unit tests --------------------------------


def test_permission_filtering_excludes_unauthorized_accounts():
    """FR-8: unauthorized records never reach the plan."""
    from backend.app.services.sales_data_service import get_account

    foreign_account = get_account("ACC2001")  # T002 account
    assert identity_service.can_access_account("rep-042", foreign_account) is False
    assert identity_service.can_access_account("mgr-001", foreign_account) is False
    assert identity_service.can_access_account("ops-001", foreign_account) is True


def test_missing_account_data_is_stated_not_invented():
    """Failure scenario: missing account record -> flagged, never fabricated."""
    broken_account = {
        "account_id": "ACC-FAKE",
        "territory_id": "T001",
        "name": None,
        "revenue": None,
        "product_adoption": None,
        "owner": "",
        "owner_id": "mgr-001",
        "permissions": {"allowed_roles": ["SALES_MANAGER"]},
    }
    items, _stale, _version = draft_plan_items([broken_account], "T001", "mgr-001")
    assert items
    item = items[0]
    assert item["account_name"] == "UNKNOWN"
    assert set(item["missing_data"]) >= {"name", "revenue", "product_adoption"}
    assert item["opportunity_summary"] == "No open opportunity on record."


def test_plan_validation_fails_when_no_items():
    result = compliance_service.evaluate_plan([])
    assert result.status == "failed"
