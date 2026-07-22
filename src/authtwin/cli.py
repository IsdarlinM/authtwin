from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional
import typer
from sric.workspace import Workspace
from sric.evidence import EvidenceStore
from sric.models import Provenance, ProvenanceType
from sric.plugins import PluginRegistry
from sric.scope import ScopeEngine, ScopePolicy
from sric.updater import perform_update
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import NotebookEntry, ResearchNotebook
from . import __version__
from .api import create_app
from .core import AuthTwinEngine
from .models import Actor, AuthorizationObservation, Decision, Invariant, InvariantKind, Resource, SessionEvent

app = typer.Typer(
    name="authtwin",
    help="Authorization Digital Twin — evidence-native authorization modeling.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    rich_markup_mode=None,
)


def ws_path(name: str, root: Path) -> Path:
    return root / name


def root_default() -> Path:
    return Path.home() / ".authtwin" / "workspaces"


@app.command()
def version() -> None:
    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check runtime, SRIC integration, plugin registry and secure defaults."""
    import sric

    plugin_path = Path.home() / ".sric" / "plugins"
    plugins = PluginRegistry(plugin_path).list()
    checks: dict[str, dict[str, object]] = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {"ok": sric.__version__.startswith("0.3."), "version": sric.__version__},
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins), "path": str(plugin_path)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(item["ok"]) for item in checks.values())
    typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    if not ok:
        raise typer.Exit(1)


@app.command()
def init(name: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    root.mkdir(parents=True, exist_ok=True)
    ws = Workspace.create(root, name)
    AuthTwinEngine(ws.root)
    typer.echo(str(ws.root))


@app.command("workspace")
def workspace_command(
    action: str = typer.Argument("list", help="create|list|show|archive"),
    name: Optional[str] = typer.Argument(None),
    root: Path = typer.Option(root_default(), "--root"),
    confirm: bool = typer.Option(False, "--confirm", help="Required for archive."),
) -> None:
    """Manage isolated investigation workspaces."""
    root.mkdir(parents=True, exist_ok=True)
    action = action.lower()
    if action == "list":
        items = sorted(
            p.name for p in root.iterdir() if p.is_dir() and (p / "workspace.json").is_file()
        )
        typer.echo(json.dumps({"workspaces": items}, indent=2))
        return
    if not name:
        typer.echo(f"workspace {action} requires NAME", err=True)
        raise typer.Exit(2)
    target = ws_path(name, root)
    if action == "create":
        ws = Workspace.create(root, name)
        AuthTwinEngine(ws.root)
        typer.echo(str(ws.root))
        return
    if action == "show":
        ws = Workspace.open(target)
        meta = json.loads((ws.root / "workspace.json").read_text(encoding="utf-8"))
        typer.echo(json.dumps({"path": str(ws.root), "metadata": meta}, indent=2))
        return
    if action == "archive":
        if not confirm:
            typer.echo("workspace archive requires --confirm; no data was changed", err=True)
            raise typer.Exit(5)
        Workspace.open(target)
        archive_root = root / "archived"
        archive_root.mkdir(exist_ok=True)
        destination = archive_root / name
        if destination.exists():
            typer.echo("archive destination already exists; no data was changed", err=True)
            raise typer.Exit(2)
        target.rename(destination)
        typer.echo(str(destination))
        return
    typer.echo(f"Unknown workspace action: {action}", err=True)
    raise typer.Exit(2)


@app.command("config")
def config_command(
    action: str = typer.Argument("show", help="show|explain"),
    key: Optional[str] = typer.Argument(None),
    workspace: Optional[str] = typer.Option(None, "--workspace"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Inspect configuration and explain where a value comes from."""
    defaults: dict[str, object] = {"telemetry": False, "cloud_ai": False, "external_uploads": False}
    values = dict(defaults)
    sources = {k: "secure default" for k in values}
    if workspace:
        meta_path = ws_path(workspace, root) / "workspace.json"
        if not meta_path.is_file():
            typer.echo("workspace.json not found", err=True)
            raise typer.Exit(2)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for k in values:
            if k in meta:
                values[k] = meta[k]
                sources[k] = f"workspace config: {meta_path}"
    if action == "show":
        typer.echo(json.dumps({"values": values, "sources": sources}, indent=2))
        return
    if action == "explain":
        if not key or key not in values:
            typer.echo("config explain requires one of: " + ", ".join(sorted(values)), err=True)
            raise typer.Exit(2)
        typer.echo(json.dumps({"key": key, "value": values[key], "source": sources[key]}, indent=2))
        return
    typer.echo(f"Unknown config action: {action}", err=True)
    raise typer.Exit(2)


@app.command()
def actor(
    workspace: str,
    actor_id: str,
    name: str,
    role: list[str] = typer.Option([], "--role"),
    tenant: Optional[str] = None,
    suspended: bool = False,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    AuthTwinEngine(ws_path(workspace, root)).add_actor(
        Actor(actor_id=actor_id, name=name, roles=role, tenant=tenant, suspended=suspended)
    )
    typer.echo(actor_id)


@app.command()
def resource(
    workspace: str,
    resource_id: str,
    resource_type: str,
    owner: Optional[str] = None,
    tenant: Optional[str] = None,
    state: str = "active",
    shared_with: list[str] = typer.Option([], "--shared-with"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    AuthTwinEngine(ws_path(workspace, root)).add_resource(
        Resource(
            resource_id=resource_id,
            resource_type=resource_type,
            owner_actor_id=owner,
            tenant=tenant,
            state=state,
            shared_with=shared_with,
        )
    )
    typer.echo(resource_id)


@app.command()
def observe(
    workspace: str,
    observation_id: str,
    actor_id: str,
    resource_id: str,
    operation: str,
    decision: Decision,
    evidence: list[str] = typer.Option([], "--evidence"),
    status_code: Optional[int] = None,
    state: Optional[str] = None,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    AuthTwinEngine(ws_path(workspace, root)).observe(
        AuthorizationObservation(
            observation_id=observation_id,
            actor_id=actor_id,
            resource_id=resource_id,
            operation=operation.upper(),
            decision=decision,
            evidence_ids=evidence,
            status_code=status_code,
            state=state,
        )
    )
    typer.echo(observation_id)


@app.command("invariant")
def invariant_cmd(
    workspace: str,
    invariant_id: str,
    description: str,
    kind: InvariantKind,
    operation: list[str] = typer.Option([], "--operation"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    AuthTwinEngine(ws_path(workspace, root)).add_invariant(
        Invariant(
            invariant_id=invariant_id, description=description, kind=kind, operations=operation
        )
    )
    typer.echo(invariant_id)


@app.command("import")
def import_cmd(
    workspace: str,
    path: Path,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    engine = AuthTwinEngine(ws_path(workspace, root))
    try:
        counts = (
            engine.import_rcap(path) if path.suffix.lower() == ".rcap" else engine.import_json(path)
        )
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    typer.echo(json.dumps(counts, indent=2))


@app.command()
def model(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    data = AuthTwinEngine(ws_path(workspace, root)).store.load()
    typer.echo(json.dumps({k: len(v) for k, v in data.items() if isinstance(v, list)}, indent=2))


@app.command()
def matrix(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    typer.echo(json.dumps(AuthTwinEngine(ws_path(workspace, root)).matrix(), indent=2))


@app.command("state-machine")
def state_machine(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Show observed resource-state transitions; missing history remains UNKNOWN."""
    typer.echo(json.dumps(AuthTwinEngine(ws_path(workspace, root)).state_machine(), indent=2))


@app.command()
def compare(
    workspace: str, actor_a: str, actor_b: str, root: Path = typer.Option(root_default(), "--root")
) -> None:
    typer.echo(
        json.dumps(AuthTwinEngine(ws_path(workspace, root)).compare(actor_a, actor_b), indent=2)
    )


@app.command()
def findings(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    items = AuthTwinEngine(ws_path(workspace, root)).evaluate()
    typer.echo(json.dumps([x.model_dump(mode="json") for x in items], indent=2))


@app.command()
def validate(
    workspace: str,
    finding_id: str,
    evidence: list[str] = typer.Option(..., "--evidence"),
    note: str = typer.Option(..., "--note"),
    confirm: bool = typer.Option(False, "--confirm"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    if not confirm:
        typer.echo("Validation requires --confirm after human review.", err=True)
        raise typer.Exit(5)
    try:
        item = AuthTwinEngine(ws_path(workspace, root)).validate(finding_id, evidence, note)
    except KeyError:
        typer.echo("Finding not found", err=True)
        raise typer.Exit(2)
    typer.echo(item.model_dump_json(indent=2))




@app.command("coverage")
def coverage_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Measure observed authorization matrix coverage; UNKNOWN cells are not findings."""
    typer.echo(AuthTwinEngine(ws_path(workspace, root)).coverage().model_dump_json(indent=2))


@app.command("discover")
def discover_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Summarize deterministic resource/operation candidates from supplied observations."""
    typer.echo(json.dumps(AuthTwinEngine(ws_path(workspace, root)).discover_resources(), indent=2))


@app.command("counterfactual")
def counterfactual_command(
    workspace: str,
    observation_id: Optional[str] = typer.Option(None, "--observation"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Generate safe counterfactual test plans; never executes them automatically."""
    plans = AuthTwinEngine(ws_path(workspace, root)).counterfactuals(observation_id)
    typer.echo(json.dumps([p.model_dump(mode="json") for p in plans], indent=2))


@app.command("session")
def session_command(
    workspace: str,
    actor_id: str,
    event_id: Optional[str] = typer.Option(None, "--event-id"),
    event_type: Optional[str] = typer.Option(None, "--event-type"),
    evidence: list[str] = typer.Option([], "--evidence"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Append or inspect identity/session lifecycle events without storing raw session secrets."""
    engine = AuthTwinEngine(ws_path(workspace, root))
    if event_id or event_type:
        if not (event_id and event_type):
            typer.echo("--event-id and --event-type are required together", err=True)
            raise typer.Exit(2)
        engine.add_session_event(SessionEvent(event_id=event_id, actor_id=actor_id, event_type=event_type.upper(), evidence_ids=evidence))
    typer.echo(json.dumps(engine.session_lifecycle(actor_id), indent=2))


@app.command("invariant-dsl")
def invariant_dsl_command(
    workspace: str,
    file: Path = typer.Argument(..., exists=True, dir_okay=False),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Parse and install a small auditable authorization-invariant DSL."""
    engine = AuthTwinEngine(ws_path(workspace, root))
    invariant = engine.parse_invariant_dsl(file.read_text(encoding="utf-8"))
    engine.add_invariant(invariant)
    typer.echo(invariant.model_dump_json(indent=2))


@app.command("graphql")
def graphql_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Show authorization observations grouped by GraphQL operation/field metadata."""
    typer.echo(json.dumps(AuthTwinEngine(ws_path(workspace, root)).graphql_surface(), indent=2))


@app.command("batch")
def batch_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Analyze supplied batch-operation item decisions; no requests are generated."""
    typer.echo(json.dumps(AuthTwinEngine(ws_path(workspace, root)).batch_authorization(), indent=2))


@app.command("skeptic")
def skeptic_command(
    workspace: str,
    finding_id: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Generate alternative explanations, missing evidence and counter-tests for a candidate."""
    try:
        review = AuthTwinEngine(ws_path(workspace, root)).skeptic_review(finding_id)
    except KeyError:
        typer.echo("Finding not found", err=True)
        raise typer.Exit(2)
    typer.echo(review.model_dump_json(indent=2))

@app.command("export")
def export_cmd(
    workspace: str,
    output: Path,
    rcap: bool = typer.Option(
        False,
        "--rcap",
        help="Export a valid RCAP capsule containing the authorization model as evidence.",
    ),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    engine = AuthTwinEngine(ws_path(workspace, root))
    if rcap or output.suffix.lower() == ".rcap":
        try:
            engine.export_rcap(output)
        except RuntimeError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(2)
    else:
        output.write_text(json.dumps(engine.export_bridge(), indent=2), encoding="utf-8")
    typer.echo(str(output))


@app.command()
def report(
    workspace: str, output: Path, root: Path = typer.Option(root_default(), "--root")
) -> None:
    e = AuthTwinEngine(ws_path(workspace, root))
    data = e.store.load()
    m = e.matrix()
    text = f"# AuthTwin Report\n\n## Facts\nActors: {len(data['actors'])}\nResources: {len(data['resources'])}\nObservations: {len(data['observations'])}\n\n## Authorization Matrix\n```json\n{json.dumps(m, indent=2)}\n```\n\n## Candidate Findings\n```json\n{json.dumps(data['findings'], indent=2)}\n```\n\nAll candidates remain hypotheses unless explicitly VALIDATED with evidence.\n"
    output.write_text(text, encoding="utf-8")
    typer.echo(str(output))


@app.command()
def demo(workspace: str = "demo", root: Path = typer.Option(root_default(), "--root")) -> None:
    path = ws_path(workspace, root)
    if not path.exists():
        root.mkdir(parents=True, exist_ok=True)
        Workspace.create(root, workspace)
    e = AuthTwinEngine(path)
    e.add_actor(Actor(actor_id="alice", name="Alice", roles=["user"]))
    e.add_actor(Actor(actor_id="bob", name="Bob", roles=["user"]))
    e.add_resource(Resource(resource_id="doc-1", resource_type="document", owner_actor_id="alice"))
    e.observe(
        AuthorizationObservation(
            observation_id="obs-1",
            actor_id="alice",
            resource_id="doc-1",
            operation="READ",
            decision=Decision.ALLOW,
            evidence_ids=["EVD-1"],
        )
    )
    e.observe(
        AuthorizationObservation(
            observation_id="obs-2",
            actor_id="bob",
            resource_id="doc-1",
            operation="UPDATE",
            decision=Decision.ALLOW,
            evidence_ids=["EVD-2"],
        )
    )
    e.add_invariant(
        Invariant(
            invariant_id="INV-1",
            description="A user must not modify an exclusively owned resource of another user.",
            kind=InvariantKind.DENY_OTHER_OWNER_MUTATION,
            operations=["UPDATE", "DELETE"],
        )
    )
    e.evaluate()
    typer.echo(
        json.dumps(
            {"workspace": str(path), "matrix": e.matrix(), "findings": e.store.load()["findings"]},
            indent=2,
        )
    )


@app.command()
def web(
    workspace: str,
    host: str = "127.0.0.1",
    port: int = 8766,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        typer.echo(
            "Non-loopback binding disabled until authenticated TLS mode is configured.", err=True
        )
        raise typer.Exit(4)
    import uvicorn

    uvicorn.run(create_app(ws_path(workspace, root)), host=host, port=port)


@app.command("evidence")
def evidence_add(
    workspace: str,
    file: Path,
    source: str = typer.Option("user", "--source"),
    media_type: str = typer.Option("application/octet-stream", "--media-type"),
    redacted: bool = typer.Option(False, "--redacted"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Store a local evidence artifact in SRIC content-addressed storage."""
    if not file.is_file():
        typer.echo("evidence input must be a regular file", err=True)
        raise typer.Exit(2)
    workspace_path = ws_path(workspace, root)
    Workspace.open(workspace_path)
    store = EvidenceStore(workspace_path / "evidence")
    ref = store.put_bytes(
        file.read_bytes(),
        media_type=media_type,
        provenance=Provenance(
            provenance_type=ProvenanceType.USER_INPUT,
            source=source,
            method="cli_evidence_add",
            tool_version=__version__,
        ),
        redacted=redacted,
    )
    typer.echo(json.dumps(ref.model_dump(mode="json"), indent=2))


@app.command("ai")
def ai_status() -> None:
    """Show AI mode. Cloud AI remains disabled until explicitly configured."""
    typer.echo(
        json.dumps({"mode": "disabled", "provider": "disabled", "cloud_uploads": False}, indent=2)
    )


@app.command("plugins")
def plugins_list(path: Path = typer.Option(Path.home() / ".sric" / "plugins", "--path")) -> None:
    """List SRIC plugin manifests without auto-executing plugin code."""
    for manifest in PluginRegistry(path).list():
        typer.echo(f"{manifest.name}\t{manifest.version}\t{manifest.type}")


@app.command("scope")
def scope_check(
    target: str,
    method: str = typer.Option("GET", "--method"),
    allow: list[str] = typer.Option([], "--allow"),
    deny: list[str] = typer.Option([], "--deny"),
) -> None:
    """Evaluate a target using SRIC Scope Engine; no request is sent."""
    decision = ScopeEngine(
        ScopePolicy(allow_targets=allow, deny_targets=deny, allowed_methods={method.upper()})
    ).evaluate(target, method)
    typer.echo(
        json.dumps(
            {
                "allowed": decision.allowed,
                "reason": decision.reason,
                "matched_rule": decision.matched_rule,
            },
            indent=2,
        )
    )
    if not decision.allowed:
        raise typer.Exit(3)




@app.command("query")
def shared_query(
    workspace: str, query: str, limit: int = typer.Option(50, "--limit", min=1, max=500), root: Path = typer.Option(root_default(), "--root")
) -> None:
    """Search this workspace's shared SRIC graph."""
    typer.echo(json.dumps(TemporalGraph(ws_path(workspace, root)).search(query, limit), indent=2, default=str))


@app.command("notebook")
def notebook_command(
    workspace: str,
    entry_type: str | None = typer.Option(None, "--type"),
    title: str | None = typer.Option(None, "--title"),
    body: str | None = typer.Option(None, "--body"),
    status: str = typer.Option("OBSERVED", "--status"),
    save_query_name: str | None = typer.Option(None, "--save-query-name"),
    query: str | None = typer.Option(None, "--query"),
    list_queries: bool = typer.Option(False, "--list-queries"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """List/append research notes or manage saved investigation queries."""
    notebook = ResearchNotebook(wp(workspace, root))
    if save_query_name or query:
        if not (save_query_name and query):
            raise typer.BadParameter("--save-query-name and --query are required together")
        notebook.save_query(save_query_name, query)
        typer.echo(json.dumps({"saved": save_query_name, "query": query}, indent=2))
        return
    if list_queries:
        typer.echo(json.dumps(notebook.saved_queries(), indent=2))
        return
    if entry_type or title or body:
        if not (entry_type and title and body):
            raise typer.BadParameter("--type, --title and --body are required together")
        typer.echo(notebook.add(NotebookEntry(entry_type=entry_type, title=title, body=body, status=status)).model_dump_json(indent=2))
        return
    typer.echo(json.dumps([x.model_dump(mode="json") for x in notebook.list()], indent=2, default=str))


@app.command("evidence-lineage")
def evidence_lineage_command(
    workspace: str, artifact_id: str, root: Path = typer.Option(root_default(), "--root")
) -> None:
    """Explain evidence lineage and the reason a derived artifact is visible."""
    try:
        payload = EvidenceLineage(ws_path(workspace, root)).explain(artifact_id)
    except KeyError:
        typer.echo(f"Unknown lineage artifact: {artifact_id}", err=True)
        raise typer.Exit(2)
    typer.echo(json.dumps(payload, indent=2, default=str))


@app.command("jobs")
def jobs_command(
    workspace: str, job_id: Optional[str] = typer.Option(None, "--id"), cancel: bool = typer.Option(False, "--cancel"), root: Path = typer.Option(root_default(), "--root")
) -> None:
    """List/inspect/cancel persistent SRIC jobs for this workspace."""
    engine = JobEngine(ws_path(workspace, root))
    if job_id and cancel:
        typer.echo(engine.request_cancel(job_id).model_dump_json(indent=2))
        return
    if job_id:
        typer.echo(
            json.dumps(
                {
                    "job": engine.get(job_id).model_dump(mode="json"),
                    "events": [x.model_dump(mode="json") for x in engine.events(job_id)],
                },
                indent=2,
                default=str,
            )
        )
        return
    typer.echo(json.dumps([x.model_dump(mode="json") for x in engine.list()], indent=2, default=str))

@app.command("update")
def update(
    check: bool = typer.Option(False, "--check"),
    manifest: Optional[str] = typer.Option(None, "--manifest"),
    public_key: Optional[Path] = typer.Option(None, "--public-key"),
) -> None:
    """Check/install a signed wheel release. Never performs a blind git pull."""
    import os

    source = manifest or os.getenv("AUTHTWIN_RELEASE_MANIFEST_URL")
    key = public_key or (
        Path(os.environ["AUTHTWIN_RELEASE_PUBLIC_KEY"])
        if os.getenv("AUTHTWIN_RELEASE_PUBLIC_KEY")
        else None
    )
    if not source or key is None:
        typer.echo(
            "No trusted release channel configured. Provide --manifest and --public-key.", err=True
        )
        raise typer.Exit(2)
    try:
        status = perform_update(
            manifest_source=source,
            public_key_path=key,
            expected_product="authtwin",
            current_version=__version__,
            check_only=check,
        )
    except Exception as exc:
        typer.echo(f"Update verification failed; no update was installed: {exc}", err=True)
        raise typer.Exit(6)
    typer.echo(json.dumps(status.__dict__, indent=2))


@app.command("help", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def help_command(ctx: typer.Context, command: Optional[str] = typer.Argument(None)) -> None:
    if not command:
        typer.echo(ctx.parent.get_help() if ctx.parent else ctx.get_help())
        return
    root = ctx.parent.command if ctx.parent else app
    if hasattr(root, "commands") and command in root.commands:
        typer.echo(root.commands[command].get_help(ctx))
        return
    typer.echo(f"Unknown command: {command}", err=True)
    raise typer.Exit(2)


def run() -> None:
    if len(sys.argv) >= 3 and sys.argv[-1] == "help" and sys.argv[1] != "help":
        sys.argv[-1] = "--help"
    app()
