from fastapi.testclient import TestClient

from authtwin.api_all import create_app


def test_console_and_workbench_catalogs_are_http_json(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    assert client.get("/console").status_code == 200
    assert client.get("/console/styles.css").status_code == 200
    catalog = client.get("/api/v1/console/catalog")
    assert catalog.status_code == 200
    assert catalog.json()["commands"]
    assert client.get("/workbench").status_code == 200
    feature_catalog = client.get("/api/v1/workbench/catalog")
    assert feature_catalog.status_code == 200
    assert feature_catalog.json()["features"]
    coverage = client.get("/api/v1/workbench/coverage")
    assert coverage.status_code == 200
    assert coverage.json()["complete"] is True
