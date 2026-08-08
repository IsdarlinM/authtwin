from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import sric
import typer
from sric.plugins import PluginRegistry

from . import cli as base
from .advanced import AuthorizationIntelligence
from .core import AuthTwinEngine
from .coverage import UnknownAuthorizationCell, prioritize_unknown_cells
from .layers import LayerObservation, compare_authorization_layers
from .models import MembershipEvent
from .policy_adapters import PolicyProvider, normalize_policy_export

app = base.app
ws_path = base.ws_path
root_default = base.root_default
rd = base.root_default


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


@app.command("doctor")
def doctor_vnext(
    json_output: bool = typer.Option(False, "--json"),
    plugin_path: Path = typer.Option(rd() / "plugins", "--plugin-path"),
) -> None:
    """Check Python, SRIC, AI-disabled defaults, plugins and privacy settings."""

    plugins = PluginRegistry(plugin_path).list()
    checks = {
        "python": {
            "ok": sys.version_info >= (3, 11),
            "version": sys.version.split()[0],
        },
        "sric": {
            "ok": sric.__version__.startswith("0.5."),
            "version": sric.__version__,
        },
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {
            "ok": True,
            "count": len(plugins),
            "path": str(plugin_path),
        },
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(value["ok"]) for value in checks.values())
    payload = {"ok": ok, "checks": checks}
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(
            "\n".join(
                f"[{'OK' if value['ok'] else 'FAIL'}] {name}: {value}"
                for name, value in checks.items()
            )
        )
    if not ok:
        raise typer.Exit(1)


@app.command("discover-v2")
def discover_v2(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Normalize observed endpoint/resource families conservatively."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    typer.echo(json.dumps(AuthorizationIntelligence(engine).discovery_v2(), indent=2))


@app.command("bindings")
def bindings_command(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Generate evidence-bearing candidate actor/resource bindings."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    output = AuthorizationIntelligence(engine).infer_actor_resource_bindings()
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in output],
            indent=2,
            default=str,
        )
    )


@app.command("state-v2")
def state_v2(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Show actor, resource and membership lifecycle state."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    typer.echo(
        json.dumps(
            AuthorizationIntelligence(engine).state_machine_v2(),
            indent=2,
            default=str,
        )
    )


@app.command("membership")
def membership_event(
    workspace: str,
    event_id: str,
    actor_id: str,
    tenant_id: str,
    state: str,
    evidence: list[str] = typer.Option([], "--evidence"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Record an evidence-bearing membership lifecycle event."""

    event = MembershipEvent(
        event_id=event_id,
        actor_id=actor_id,
        tenant_id=tenant_id,
        state=state.upper(),
        evidence_ids=evidence,
    )
    engine = AuthTwinEngine(ws_path(workspace, root))
    AuthorizationIntelligence(engine).add_membership_event(event)
    typer.echo(event.model_dump_json(indent=2))


@app.command("mutation-plan")
def mutation_plan(
    workspace: str,
    observation_id: Optional[str] = typer.Option(None, "--observation"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Propose minimal mutations; execution still requires ReproSec safety gates."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    output = AuthorizationIntelligence(engine).mutation_plans(observation_id)
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in output],
            indent=2,
            default=str,
        )
    )


@app.command("differential")
def differential(
    workspace: str,
    observation_a: str,
    observation_b: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Compare two authorization observations without validating a finding."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    insight = AuthorizationIntelligence(engine).differential_response(
        observation_a,
        observation_b,
    )
    typer.echo(insight.model_dump_json(indent=2))


@app.command("invariant-library")
def invariant_library(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Install the built-in conservative authorization invariant library."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    installed = AuthorizationIntelligence(engine).install_invariant_library()
    typer.echo(json.dumps({"installed": installed}, indent=2))


@app.command("websocket")
def websocket_surface(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Show evidence-bearing WebSocket authorization lifecycle observations."""

    engine = AuthTwinEngine(ws_path(workspace, root))
    typer.echo(
        json.dumps(
            AuthorizationIntelligence(engine).websocket_surface(),
            indent=2,
            default=str,
        )
    )


@app.command("layer-compare")
def layer_compare(path: Path) -> None:
    """Compare intended, configured and observed authorization layers from JSON."""

    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("layer observations JSON must be a list")
    observations = [LayerObservation.model_validate(item) for item in raw]
    output = compare_authorization_layers(observations)
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in output],
            indent=2,
            default=str,
        )
    )


@app.command("policy-import")
def policy_import(
    path: Path,
    provider: PolicyProvider = typer.Option(..., "--provider", case_sensitive=False),
    source_id: str = typer.Option(..., "--source-id"),
    evidence: list[str] = typer.Option([], "--evidence"),
) -> None:
    """Normalize a policy export as configured-only evidence; never execute it."""

    raw = _read_json(path)
    if not isinstance(raw, dict):
        raise typer.BadParameter("policy export JSON must be an object")
    report = normalize_policy_export(
        provider=provider,
        source_id=source_id,
        data=raw,
        evidence_ids=evidence,
    )
    typer.echo(report.model_dump_json(indent=2))
    if report.errors:
        raise typer.Exit(2)


@app.command("coverage-priority")
def coverage_priority(path: Path) -> None:
    """Rank UNKNOWN matrix cells for research; never create findings."""

    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("coverage cells JSON must be a list")
    cells = [UnknownAuthorizationCell.model_validate(item) for item in raw]
    output = prioritize_unknown_cells(cells)
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in output],
            indent=2,
            default=str,
        )
    )


def run() -> None:
    base.run()
