from pathlib import Path
from fastapi.testclient import TestClient
from sric.workspace import Workspace
from authtwin.api import create_app


def test_api(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "w")
    c = TestClient(create_app(ws.root))
    root_response = c.get("/")
    assert root_response.status_code == 200
    assert "script-src 'self'" in root_response.headers["content-security-policy"]
    js_response = c.get("/assets/app.js")
    assert js_response.status_code == 200
    assert "fetch(" in js_response.text
    assert c.get("/api/summary").json()["actors"] == 0
