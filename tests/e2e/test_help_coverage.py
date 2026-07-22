from typer.main import get_command
from typer.testing import CliRunner
from authtwin.cli import app


def test_all_registered_commands_have_help() -> None:
    runner = CliRunner()
    group = get_command(app)
    assert hasattr(group, "commands")
    commands = group.commands  # type: ignore[attr-defined]
    assert commands
    for name in commands:
        assert runner.invoke(app, [name, "--help"]).exit_code == 0, name
        assert runner.invoke(app, [name, "-h"]).exit_code == 0, name
