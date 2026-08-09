from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typer.testing import CliRunner

import authtwin.sric_bootstrap as bootstrap
from authtwin.api_all import _mount_degraded_workbench
from authtwin.cli_all import app, normalize_help_argv
from sric.web_console import build_command_catalog
from sric.web_workbench import build_feature_catalog, feature_contract


def _runtime(version: str, *, compatible: bool, missing: tuple[str, ...] = ()) -> bootstrap.SRICRuntimeStatus:
    return bootstrap.SRICRuntimeStatus(version, compatible, missing, (() if compatible else ("incompatible",)))


def test_stale_core_and_missing_workbench_are_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap.importlib.metadata, "version", lambda _name: "0.5.5")
    monkeypatch.setattr(bootstrap, "_find_module", lambda _name: False)
    result = bootstrap.status()
    assert result.compatible is False
    assert "sric.web_workbench" in result.missing_modules
    assert any("older than required 0.5.7" in reason for reason in result.reasons)


def test_bridge_and_same_version_repair_semantics(monkeypatch: pytest.MonkeyPatch) -> None:
    states = iter([_runtime("0.5.5", compatible=False), _runtime("0.5.7", compatible=True)])
    bridged: list[bool] = []
    updates: list[dict[str, object]] = []
    fake = SimpleNamespace(perform_product_update=lambda **kwargs: updates.append(kwargs))
    monkeypatch.setattr(bootstrap, "status", lambda: next(states))
    monkeypatch.setattr(bootstrap, "_upgrade_055_to_056", lambda: bridged.append(True))
    monkeypatch.setattr(bootstrap, "_updater", lambda: fake)
    monkeypatch.setattr(bootstrap, "_require_updater_api", lambda *_args: None)
    monkeypatch.setattr(bootstrap.importlib, "invalidate_caches", lambda: None)
    assert bootstrap.ensure_for_official_update().compatible is True
    assert bridged == [True]
    assert updates[0] == {"expected_product": "sric-core", "current_version": "0.5.6", "check_only": False, "force": False}

    states = iter([_runtime("0.5.7", compatible=False, missing=("sric.web_workbench",)), _runtime("0.5.7", compatible=True)])
    updates.clear()
    monkeypatch.setattr(bootstrap, "status", lambda: next(states))
    bootstrap.ensure_for_official_update()
    assert updates[0]["force"] is True


def test_degraded_workbench_is_actionable_503() -> None:
    degraded = FastAPI()
    _mount_degraded_workbench(degraded, "missing sric.web_workbench")
    client = TestClient(degraded)
    assert client.get("/workbench").status_code == 503
    payload = client.get("/api/v1/workbench/coverage").json()
    assert payload["complete"] is False
    assert payload["status"] == "RUNTIME_INCOMPATIBLE"


def test_every_auth_cli_command_param_has_web_representation_and_help() -> None:
    cli = build_command_catalog("authtwin.cli_all")
    web = build_feature_catalog("authtwin.cli_all")
    assert feature_contract("authtwin.cli_all")["complete"] is True
    cli_by_path = {item["path"]: item for item in cli}
    web_by_path = {item["path"]: item for item in web}
    assert set(cli_by_path) == set(web_by_path)
    runner = CliRunner()
    for args in (["--help"], ["-h"], ["help"]):
        assert runner.invoke(app, args).exit_code == 0
    for path, command in cli_by_path.items():
        args = path.split()
        assert runner.invoke(app, [*args, "--help"]).exit_code == 0, path
        assert runner.invoke(app, [*args, "-h"]).exit_code == 0, path
        assert normalize_help_argv(["authtwin", *args, "help"])[-1] == "--help"
        assert [p["name"] for p in command["params"]] == [p["name"] for p in web_by_path[path]["params"]]
