from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from authtwin.api_vnext import create_app

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(tmp_path))


def test_graphql_field_difference_is_hypothesis_not_finding(tmp_path: Path) -> None:
    response = client(tmp_path).post(
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


def test_subscription_events_after_revocation_remain_hypothesis(tmp_path: Path) -> None:
    revocation = T0 + timedelta(minutes=5)
    response = client(tmp_path).post(
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


def test_subscription_without_payload_precontrol_is_unknown(tmp_path: Path) -> None:
    revocation = T0 + timedelta(minutes=5)
    response = client(tmp_path).post(
        "/api/v1/surfaces/subscription-revocation",
        json={
            "observations": [
                {
                    "observation_id": "before-empty",
                    "subscription_id": "SUB-1",
                    "actor_id": "actor",
                    "topic": "document.updated",
                    "event_index": 0,
                    "received_at": T0.isoformat(),
                    "revocation_observed_at": revocation.isoformat(),
                    "received_payload": False,
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
    assert response.json()["reports"][0]["status"] == "UNKNOWN"


def test_naive_surface_timestamp_is_validation_error_not_500(tmp_path: Path) -> None:
    response = client(tmp_path).post(
        "/api/v1/surfaces/graphql-fields",
        json={
            "observations": [
                {
                    "observation_id": "O-X",
                    "operation_name": "Get",
                    "operation_kind": "QUERY",
                    "field_path": "user.email",
                    "actor_id": "actor",
                    "decision": "UNKNOWN",
                    "observed_at": "2026-01-01T00:00:00",
                }
            ]
        },
    )
    assert response.status_code == 422
