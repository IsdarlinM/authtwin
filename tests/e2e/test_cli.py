from typer.testing import CliRunner
from authtwin.cli import app

runner = CliRunner()


def test_help_variants() -> None:
    assert runner.invoke(app, ["--help"]).exit_code == 0
    assert runner.invoke(app, ["-h"]).exit_code == 0
    assert runner.invoke(app, ["help"]).exit_code == 0
    assert runner.invoke(app, ["matrix", "--help"]).exit_code == 0
