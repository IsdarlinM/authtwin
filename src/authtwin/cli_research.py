from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli_vnext import app
from .coverage import UnknownAuthorizationCell
from .research import build_validation_plan


@app.command("validation-plan")
def validation_plan(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    maximum_experiments: int = typer.Option(25, "--max-experiments", min=1, max=1000),
    include_unsafe: bool = typer.Option(False, "--include-unsafe"),
) -> None:
    """Plan representative experiments for UNKNOWN authorization coverage cells."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        raw_cells = payload if isinstance(payload, list) else payload.get("cells", [])
        if not isinstance(raw_cells, list):
            raise ValueError("input must be a JSON list or an object containing a cells list")
        cells = [UnknownAuthorizationCell.model_validate(item) for item in raw_cells]
        plans = build_validation_plan(
            cells,
            max_experiments=maximum_experiments,
            safe_only=not include_unsafe,
        )
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        typer.echo(f"validation planning failed: {exc}", err=True)
        raise typer.Exit(2) from exc

    typer.echo(
        json.dumps(
            {
                "input_cell_count": len(cells),
                "planned_experiment_count": len(plans),
                "plans": [item.model_dump(mode="json") for item in plans],
                "validated_findings_created": 0,
            },
            indent=2,
        )
    )
