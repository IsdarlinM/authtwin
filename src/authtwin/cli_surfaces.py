from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli_vnext import app
from .surfaces import (
    GraphQLFieldObservation,
    SubscriptionEventObservation,
    assess_subscription_revocation,
    compare_graphql_fields,
)


def _read_list(path: Path) -> list[object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise typer.BadParameter("input JSON must be a list")
    return raw


@app.command("graphql-fields")
def graphql_fields(path: Path) -> None:
    """Compare field-level GraphQL decisions in equivalent contexts."""
    try:
        observations = [
            GraphQLFieldObservation.model_validate(item) for item in _read_list(path)
        ]
        reports = compare_graphql_fields(observations)
    except (ValidationError, ValueError) as exc:
        typer.echo(f"invalid GraphQL authorization input: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in reports],
            indent=2,
            default=str,
        )
    )


@app.command("subscription-revocation")
def subscription_revocation(path: Path) -> None:
    """Assess evidence before/after WebSocket subscription revocation."""
    try:
        observations = [
            SubscriptionEventObservation.model_validate(item) for item in _read_list(path)
        ]
        reports = assess_subscription_revocation(observations)
    except (ValidationError, ValueError) as exc:
        typer.echo(f"invalid subscription observation: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in reports],
            indent=2,
            default=str,
        )
    )
