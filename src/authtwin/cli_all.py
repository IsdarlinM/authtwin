from __future__ import annotations

from . import cli_surfaces as _cli_surfaces  # noqa: F401
from .cli_vnext import app, run as _run

__all__ = ["app", "run"]


def run() -> None:
    _run()
