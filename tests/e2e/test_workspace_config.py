from pathlib import Path
from typer.testing import CliRunner
from authtwin.cli import app


def test_workspace_and_config(tmp_path: Path) -> None:
    runner = CliRunner()
    created = runner.invoke(app, ["workspace", "create", "case", "--root", str(tmp_path)])
    assert created.exit_code == 0, created.output
    listed = runner.invoke(app, ["workspace", "list", "--root", str(tmp_path)])
    assert listed.exit_code == 0
    assert "case" in listed.output
    explained = runner.invoke(
        app, ["config", "explain", "telemetry", "--workspace", "case", "--root", str(tmp_path)]
    )
    assert explained.exit_code == 0
    assert '"value": false' in explained.output.lower()
    refused = runner.invoke(app, ["workspace", "archive", "case", "--root", str(tmp_path)])
    assert refused.exit_code != 0
    assert (tmp_path / "case").exists()
