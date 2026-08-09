from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from sric.capabilities import discover_capabilities

from . import __version__
from .api_vnext import create_app as create_base_app
from .sric_bootstrap import status as sric_runtime_status


def _mount_degraded_workbench(app: FastAPI, reason: str) -> None:
    @app.get("/workbench", include_in_schema=False)
    async def workbench_unavailable() -> HTMLResponse:
        return HTMLResponse(
            "<h1>Sentinel Forge runtime repair required</h1>"
            "<p>The native AuthTwin dashboard remains available, but the shared Web Feature "
            "Workbench cannot start because SRIC Core is incompatible.</p>"
            f"<pre>{reason}</pre><p>Run <code>authtwin doctor</code> and "
            "<code>authtwin update</code>, or rerun the installer.</p>",
            status_code=503,
        )

    @app.get("/api/v1/workbench/coverage", include_in_schema=False)
    async def workbench_coverage_unavailable() -> JSONResponse:
        return JSONResponse(
            {"complete": False, "status": "RUNTIME_INCOMPATIBLE", "reason": reason, "repair": "authtwin update or rerun installer"},
            status_code=503,
        )


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)

    @app.get("/api/v1/capabilities", tags=["standalone"])
    async def capabilities() -> dict[str, object]:
        return discover_capabilities(current_product="authtwin").model_dump(mode="json")

    @app.get("/api/v1/runtime-compatibility", tags=["standalone"])
    async def runtime_compatibility() -> dict[str, object]:
        runtime = sric_runtime_status()
        return {"compatible": runtime.compatible, "sric_version": runtime.version, "missing_modules": list(runtime.missing_modules), "reasons": list(runtime.reasons)}

    try:
        from sric.web_console import WebConsoleConfig, mount_web_console
    except ModuleNotFoundError as exc:
        _mount_degraded_workbench(app, f"missing shared Web console module: {exc.name or exc}")
        return app

    config = WebConsoleConfig(product="authtwin", display_name="AuthTwin", cli_module="authtwin.cli_all", version=__version__)
    manager = mount_web_console(app, config)
    try:
        from sric.web_workbench import mount_feature_workbench
    except ModuleNotFoundError as exc:
        _mount_degraded_workbench(app, f"missing shared Workbench module: {exc.name or exc}")
    else:
        mount_feature_workbench(app, config, manager)
    return app
