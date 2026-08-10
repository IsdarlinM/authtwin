from fastapi.testclient import TestClient

from authtwin.api_all import create_app


def test_shared_web_routes_allow_same_origin_styles(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    for path in ("/console", "/workbench"):
        response = client.get(path)
        assert response.status_code == 200
        csp = response.headers["content-security-policy"]
        assert "style-src 'self' 'unsafe-inline'" in csp
        assert "script-src 'self'" in csp
        assert "object-src 'none'" in csp
    assert client.get("/console/styles.css").status_code == 200
