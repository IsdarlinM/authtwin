from typer.testing import CliRunner
from sric.workspace import Workspace

from authtwin.cli_all import app


runner = CliRunner()


def test_notebook_command_resolves_workspace_without_name_error(tmp_path) -> None:
    Workspace.create(tmp_path, "case")
    result = runner.invoke(app, ["notebook", "case", "--root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "[]" in result.output
