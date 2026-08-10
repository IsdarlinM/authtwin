from fastapi.testclient import TestClient
from sric.workspace import Workspace

from authtwin.api_all import create_app


def test_authtwin_mounts_shared_security_workspace_v3(tmp_path) -> None:
    workspace = Workspace.create(tmp_path / "workspaces", "smoke").root
    client = TestClient(create_app(workspace))

    page = client.get("/workbench")
    assert page.status_code == 200
    assert "Security Workspace" in page.text
    assert 'class="global-rail"' in page.text
    assert 'class="panel jobs activity-panel"' in page.text

    catalog = client.get("/api/v1/workbench/catalog")
    assert catalog.status_code == 200
    payload = catalog.json()
    assert payload["ui_version"] == 3
    assert payload["product"] == "authtwin"
    assert payload["contract"]["complete"] is True
    assert payload["execution"]["shell"] is False
    assert payload["execution"]["user_supplied_argv"] is False
