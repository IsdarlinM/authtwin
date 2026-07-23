from __future__ import annotations
import json,sys
from pathlib import Path
from typing import Optional
import typer,sric
from sric.plugins import PluginRegistry
from . import cli as base
from .advanced import AuthorizationIntelligence
from .core import AuthTwinEngine
from .models import MembershipEvent
app=base.app;ws_path=base.ws_path;root_default=base.root_default;rd=base.root_default
@app.command("doctor")
def doctor_vnext(json_output:bool=typer.Option(False,"--json"),plugin_path:Path=typer.Option(rd()/"plugins","--plugin-path"))->None:
    plugins=PluginRegistry(plugin_path).list();checks={"python":{"ok":sys.version_info>=(3,11),"version":sys.version.split()[0]},"sric":{"ok":sric.__version__.startswith("0.4."),"version":sric.__version__},"ai":{"ok":True,"mode":"disabled","cloud_uploads":False},"plugins":{"ok":True,"count":len(plugins),"path":str(plugin_path)},"privacy":{"ok":True,"telemetry":False}};ok=all(bool(v["ok"]) for v in checks.values());payload={"ok":ok,"checks":checks};typer.echo(json.dumps(payload,indent=2) if json_output else "\n".join(f"[{'OK' if v['ok'] else 'FAIL'}] {k}: {v}" for k,v in checks.items()));
    if not ok:raise typer.Exit(1)
@app.command("discover-v2")
def discover_v2(workspace:str,root:Path=typer.Option(root_default(),"--root"))->None:typer.echo(json.dumps(AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).discovery_v2(),indent=2))
@app.command("bindings")
def bindings_command(workspace:str,root:Path=typer.Option(root_default(),"--root"))->None:
    out=AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).infer_actor_resource_bindings();typer.echo(json.dumps([x.model_dump(mode="json") for x in out],indent=2,default=str))
@app.command("state-v2")
def state_v2(workspace:str,root:Path=typer.Option(root_default(),"--root"))->None:typer.echo(json.dumps(AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).state_machine_v2(),indent=2,default=str))
@app.command("membership")
def membership_event(workspace:str,event_id:str,actor_id:str,tenant_id:str,state:str,evidence:list[str]=typer.Option([],"--evidence"),root:Path=typer.Option(root_default(),"--root"))->None:
    event=MembershipEvent(event_id=event_id,actor_id=actor_id,tenant_id=tenant_id,state=state.upper(),evidence_ids=evidence);AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).add_membership_event(event);typer.echo(event.model_dump_json(indent=2))
@app.command("mutation-plan")
def mutation_plan(workspace:str,observation_id:Optional[str]=typer.Option(None,"--observation"),root:Path=typer.Option(root_default(),"--root"))->None:
    out=AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).mutation_plans(observation_id);typer.echo(json.dumps([x.model_dump(mode="json") for x in out],indent=2,default=str))
@app.command("differential")
def differential(workspace:str,observation_a:str,observation_b:str,root:Path=typer.Option(root_default(),"--root"))->None:typer.echo(AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).differential_response(observation_a,observation_b).model_dump_json(indent=2))
@app.command("invariant-library")
def invariant_library(workspace:str,root:Path=typer.Option(root_default(),"--root"))->None:typer.echo(json.dumps({"installed":AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).install_invariant_library()},indent=2))
@app.command("websocket")
def websocket_surface(workspace:str,root:Path=typer.Option(root_default(),"--root"))->None:typer.echo(json.dumps(AuthorizationIntelligence(AuthTwinEngine(ws_path(workspace,root))).websocket_surface(),indent=2,default=str))
def run()->None:base.run()
