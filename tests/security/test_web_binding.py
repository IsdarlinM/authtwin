from pathlib import Path
from typer.testing import CliRunner
from authtwin.cli import app


def test_non_loopback_web_binding_is_refused(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app, ["web", "missing", "--host", "0.0.0.0", "--root", str(tmp_path)]
    )
    assert result.exit_code != 0
    assert "Non-loopback binding disabled" in result.output
