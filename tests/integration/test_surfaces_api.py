from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from authtwin.api_vnext import create_app


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_graphql_field_difference_is_hypothesis_not_finding() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/surfaces/graphql-fields",
        json={
            "observations": [
                {
                    "observation_id": "O-1",
                    "operation_name": "GetDocument",
                    "operation_kind": "QUERY",
                    "field_path": "document.owner.email",
                    "actor_id": "owner",
                    "tenant_id": "tenant-a",
                    "resource_id": "doc-1",
                    "resource_state": "ACTIVE",
                    "decision": "ALLOW",
                    "evidence_ids": ["E-1"],
                },
                {
                    "observation_id": "O-2",
                    "operation_name": "GetDocument",
                    "operation_kind": "QUERY",
                    "field_path": "document.owner.email",
                    "actor_id": "other",
                    "tenant_id": "tenant-a",
                    "resource_id": "doc-1",
                    "resource_state": "ACTIVE",
                    "decision": "DENY",
                    "evidence_ids": ["E-2"],
                },
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "HYPOTHESIS"
    assert payload["validated_findings_created"] == 0


def test_subscription_events_after_revocation_remain_hypothesis() -> None:
    client = TestClient(create_app())
    revocation = T0 + timedelta(minutes=5)
    response = client.post(
        "/api/v1/surfaces/subscription-revocation",
        json={
            "observations": [
                {
                    "observation_id": "before",
                    "subscription_id": "SUB-1",
                    "actor_id": "actor",
                    "topic": "document.updated",
                    "event_index": 0,
                    "received_at": T0.isoformat(),
                    "revocation_observed_at": revocation.isoformat(),
                    "evidence_ids": ["E-BEFORE"],
                },
                {
                    "observation_id": "after",
                    "subscription_id": "SUB-1",
                    "actor_id": "actor",
                    "topic": "document.updated",
                    "event_index": 1,
                    "received_at": (T0 + timedelta(minutes=6)).isoformat(),
                    "revocation_observed_at": revocation.isoformat(),
                    "evidence_ids": ["E-AFTER"],
                },
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "HYPOTHESIS"
    assert payload["validated_findings_created"] == 0
