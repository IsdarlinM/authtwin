from pathlib import Path

from fastapi.testclient import TestClient
from sric.workspace import Workspace

from authtwin.api_all import create_app


def test_standalone_web_and_capability_api(tmp_path: Path) -> None:
    workspace = Workspace.create(tmp_path, "standalone")
    client = TestClient(create_app(workspace.root))
    root = client.get("/")
    assert root.status_code == 200
    assert "AuthTwin" in root.text
    report = client.get("/api/v1/capabilities")
    assert report.status_code == 200
    assert report.json()["current_product"] == "authtwin"
    assert report.json()["standalone_ready"] is True
