from fastapi.testclient import TestClient

from authtwin.api import create_app


def test_policy_import_api_is_configured_only() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/policy/import",
        json={
            "provider": "AWS_IAM",
            "source_id": "export-1",
            "evidence_ids": ["E-1"],
            "data": {
                "Version": "2012-10-17",
                "Statement": {
                    "Sid": "Read",
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::bucket/*",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["configured_only"] is True
    assert payload["errors"] == []
    assert "does not prove runtime" in payload["limitations"][0]


def test_unknown_coverage_api_has_no_risk_or_findings() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/coverage/prioritize",
        json={
            "cells": [
                {
                    "cell_id": "C-1",
                    "actor_id": "actor-a",
                    "tenant_id": "tenant-a",
                    "resource_id": "resource-1",
                    "operation": "READ",
                    "resource_sensitivity": "CONFIDENTIAL",
                    "crosses_tenant_boundary": True,
                    "validation_cost": "READ_ONLY_SENSITIVE",
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_score"] is None
    assert payload["findings_created"] == 0
    assert payload["priorities"][0]["status"] == "UNKNOWN"


def test_invalid_policy_shape_fails_closed_in_report() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/policy/import",
        json={
            "provider": "OPENFGA",
            "source_id": "invalid",
            "data": {"tuples": "not-a-list"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["errors"]
    assert payload["rules"] == []
