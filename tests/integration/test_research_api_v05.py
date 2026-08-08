from pathlib import Path

from fastapi.testclient import TestClient

from authtwin.api_vnext import create_app


def test_validation_plan_api_preserves_unknown_semantics(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.post(
        "/api/v1/research/validation-plan",
        json={
            "cells": [
                {
                    "cell_id": "c1",
                    "actor_id": "a1",
                    "tenant_id": "t1",
                    "resource_id": "r1",
                    "operation": "READ",
                    "resource_sensitivity": "CONFIDENTIAL",
                    "crosses_tenant_boundary": True,
                    "validation_cost": "READ_ONLY_SAFE",
                    "equivalence_class": "documents",
                },
                {
                    "cell_id": "c2",
                    "actor_id": "a1",
                    "tenant_id": "t1",
                    "resource_id": "r2",
                    "operation": "READ",
                    "resource_sensitivity": "CONFIDENTIAL",
                    "crosses_tenant_boundary": True,
                    "validation_cost": "READ_ONLY_SAFE",
                    "equivalence_class": "documents",
                },
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["planned_experiment_count"] == 1
    assert payload["plans"][0]["status"] == "UNKNOWN"
    assert payload["validated_findings_created"] == 0
