import json
from pathlib import Path

from typer.testing import CliRunner

from authtwin.cli_all import app

runner = CliRunner()


def test_validation_plan_cli(tmp_path: Path) -> None:
    path = tmp_path / "cells.json"
    path.write_text(
        json.dumps(
            [
                {
                    "cell_id": "c1",
                    "actor_id": "a1",
                    "resource_id": "r1",
                    "operation": "READ",
                    "validation_cost": "READ_ONLY_SAFE",
                }
            ]
        ),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["validation-plan", str(path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["planned_experiment_count"] == 1
    assert payload["plans"][0]["status"] == "UNKNOWN"
