from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from sric.capabilities import discover_capabilities

from .api_vnext import create_app as create_base_app


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)

    @app.get("/api/v1/capabilities", tags=["standalone"])
    async def capabilities() -> dict[str, object]:
        return discover_capabilities(current_product="authtwin").model_dump(mode="json")

    return app
