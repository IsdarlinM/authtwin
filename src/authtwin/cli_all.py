from __future__ import annotations

import sys

from . import cli as _base_cli
from . import cli_research as _cli_research  # noqa: F401
from . import cli_surfaces as _cli_surfaces  # noqa: F401
from .api_all import create_app as create_complete_app
from .cli_vnext import app
from . import cli_capabilities as _cli_capabilities  # noqa: F401

_base_cli.create_app = create_complete_app

__all__ = ["app", "normalize_help_argv", "run"]


def normalize_help_argv(argv: list[str]) -> list[str]:
    """Normalize trailing `help` for root and nested AuthTwin commands."""
    normalized = list(argv)
    if len(normalized) >= 3 and normalized[-1] == "help" and normalized[1] != "help":
        normalized[-1] = "--help"
    return normalized


def run() -> None:
    """Console entrypoint including every public AuthTwin command and local Web/API."""
    sys.argv[:] = normalize_help_argv(sys.argv)
    app()
