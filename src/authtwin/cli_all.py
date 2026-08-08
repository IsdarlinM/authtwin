from __future__ import annotations

import typer
from sric.cli_style import CLIBrand, configure_cli_context, no_color_option, run_branded_cli

from . import __version__
from . import cli as _base_cli
from . import cli_research as _cli_research  # noqa: F401
from . import cli_surfaces as _cli_surfaces  # noqa: F401
from .api_all import create_app as create_complete_app
from .cli_vnext import app
from . import cli_capabilities as _cli_capabilities  # noqa: F401

_base_cli.create_app = create_complete_app

__all__ = ["BRAND", "app", "normalize_help_argv", "run"]

BRAND = CLIBrand(
    product="AuthTwin",
    description="Model authorization behavior, invariants, and differential evidence.",
    version=__version__,
)
app.rich_markup_mode = "rich"


@app.callback()
def branded_main(
    ctx: typer.Context,
    no_color: bool = no_color_option(),
) -> None:
    """AuthTwin CLI presentation controls."""

    configure_cli_context(ctx, no_color=no_color)


def normalize_help_argv(argv: list[str]) -> list[str]:
    """Normalize trailing `help` for root and nested AuthTwin commands."""
    normalized = list(argv)
    if len(normalized) >= 3 and normalized[-1] == "help" and normalized[1] != "help":
        normalized[-1] = "--help"
    return normalized


def run() -> None:
    """Console entrypoint including the branded CLI and local Web/API."""

    run_branded_cli(app, BRAND, argv_normalizer=normalize_help_argv)
