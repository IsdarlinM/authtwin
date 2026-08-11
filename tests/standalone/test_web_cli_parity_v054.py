from __future__ import annotations

from fastapi.testclient import TestClient

from authtwin.api_all import create_app
from sric.web_console import build_command_catalog


def test_web_console_catalog_exactly_matches_public_cli_tree(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.get("/api/v1/console/catalog")
    assert response.status_code == 200
    web_paths = {item["path"] for item in response.json()["commands"]}
    cli_paths = {item["path"] for item in build_command_catalog("authtwin.cli_all")}
    assert web_paths == cli_paths
    assert web_paths


def test_web_console_page_and_safety_contract_are_mounted(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    page = client.get("/console")
    assert page.status_code == 200
    assert "AuthTwin Security Console" in page.text
    assert 'href="/workbench"' in page.text
    catalog = client.get("/api/v1/console/catalog").json()
    assert catalog["execution"]["shell"] is False
    assert catalog["execution"]["arbitrary_executable"] is False
    commands = {item["path"]: item for item in catalog["commands"]}
    assert commands["web"]["context_only"] is True
    assert commands["web"]["executable"] is False
