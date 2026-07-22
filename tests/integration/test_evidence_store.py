import json
from pathlib import Path
from typer.testing import CliRunner
from authtwin.cli import app


def test_evidence_uses_sric_content_addressed_store(tmp_path: Path) -> None:
    runner = CliRunner()
    created = runner.invoke(app, ["workspace", "create", "case", "--root", str(tmp_path)])
    assert created.exit_code == 0, created.output
    artifact = tmp_path / "note.txt"
    artifact.write_text("synthetic evidence", encoding="utf-8")
    result = runner.invoke(
        app,
        ["evidence", "case", str(artifact), "--media-type", "text/plain", "--root", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["evidence_id"].startswith("EVD-")
    assert len(payload["sha256"]) == 64
    assert (
        tmp_path / "case" / "evidence" / "metadata" / f"{payload['evidence_id']}.json"
    ).is_file()
