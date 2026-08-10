from __future__ import annotations

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from authtwin.api_all import create_app
from authtwin.cli_all import app
from sric.web_console import build_command_catalog
from sric.web_workbench import build_feature_catalog

runner = CliRunner()

ALLOWED_CONTROLS = {
    "text", "path", "number", "flag", "tri-state", "count", "multi-text",
    "multi-value", "select", "multi-select",
}


def test_every_public_cli_command_and_argument_is_represented_in_workbench() -> None:
    cli = {item["path"]: item for item in build_command_catalog("authtwin.cli_all")}
    web = {item["path"]: item for item in build_feature_catalog("authtwin.cli_all")}
    assert set(cli) == set(web)
    assert cli
    for path, command in cli.items():
        assert [item["name"] for item in command["params"]] == [
            item["name"] for item in web[path]["params"]
        ]
        assert web[path]["classification"] == command["classification"]
        assert web[path]["approval_required"] == command["approval_required"]
        for param in web[path]["params"]:
            assert param["control"] in ALLOWED_CONTROLS


def test_every_public_cli_command_help_exposes_options_and_required_arguments() -> None:
    catalog = build_command_catalog("authtwin.cli_all")
    assert runner.invoke(app, ["--help"]).exit_code == 0
    for command in catalog:
        result = runner.invoke(app, command["path"].split() + ["--help"])
        assert result.exit_code == 0, f"{command['path']}\n{result.output}"
        normalized = result.output.lower().replace("_", "-")
        for param in command["params"]:
            if param["kind"] == "option":
                for opt in param["opts"]:
                    assert opt in result.output
            elif param["required"]:
                assert param["name"].lower().replace("_", "-") in normalized


def test_workbench_mount_and_guided_contract(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    page = client.get("/workbench")
    assert page.status_code == 200
    assert "No command syntax is required" in page.text
    assert "Advanced argv" not in page.text
    assert "Additional arguments" not in page.text

    payload = client.get("/api/v1/workbench/catalog").json()
    assert payload["schema_version"] == 2
    assert payload["contract"]["complete"] is True
    assert payload["execution"]["shell"] is False
    assert payload["execution"]["arbitrary_executable"] is False
    assert payload["execution"]["user_supplied_argv"] is False
    assert {item["path"] for item in payload["features"]} == {
        item["path"] for item in build_command_catalog("authtwin.cli_all")
    }


def test_native_auth_features_remain_available_with_guided_console(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    page = client.get("/")
    assert page.status_code == 200
    assert "Security Console" in page.text
    assert 'href=\'/workbench\'' in page.text
    assert "Advanced Console" not in page.text
    assert 'href=\'/console\'' not in page.text
    for route in ("/api/summary", "/api/matrix", "/api/coverage", "/api/counterfactuals", "/api/graphql", "/api/batch"):
        response = client.get(route)
        assert response.status_code == 200, route
