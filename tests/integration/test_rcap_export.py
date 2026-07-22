from pathlib import Path

import pytest

from sric.workspace import Workspace
from authtwin.core import AuthTwinEngine
from authtwin.models import Actor, Decision, AuthorizationObservation, Resource

reprosec = pytest.importorskip("reprosec")
from reprosec.capsule import verify_archive  # noqa: E402


def test_rcap_export_is_valid(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "w")
    engine = AuthTwinEngine(ws.root)
    engine.add_actor(Actor(actor_id="alice", name="Alice"))
    engine.add_resource(
        Resource(resource_id="doc", resource_type="document", owner_actor_id="alice")
    )
    engine.observe(
        AuthorizationObservation(
            observation_id="obs",
            actor_id="alice",
            resource_id="doc",
            operation="READ",
            decision=Decision.ALLOW,
            evidence_ids=["EVD-1"],
        )
    )
    output = tmp_path / "auth.rcap"
    engine.export_rcap(output)
    assert output.is_file()
    assert verify_archive(output) == []


def test_rcap_import_stays_unknown(tmp_path: Path) -> None:
    from reprosec.capsule import (
        add_request,
        add_response,
        add_workflow_step,
        initialize_directory,
        pack,
    )
    from reprosec.models import RequestRecord, ResponseRecord, WorkflowStep

    capsule_dir = tmp_path / "capsule"
    initialize_directory(capsule_dir, "Auth import")
    req = RequestRecord(method="GET", url="https://example.test/doc/1")
    add_request(capsule_dir, req)
    add_response(capsule_dir, ResponseRecord(request_id=req.request_id, status_code=200))
    add_workflow_step(capsule_dir, WorkflowStep(actor="bob", request_id=req.request_id))
    archive = pack(capsule_dir, tmp_path / "import.rcap")

    ws = Workspace.create(tmp_path, "imported")
    engine = AuthTwinEngine(ws.root)
    counts = engine.import_rcap(archive)
    assert counts["observations"] == 1
    observation = engine.store.load()["observations"][0]
    assert observation["decision"] == "UNKNOWN"
    assert observation["metadata"]["authorization_interpretation"] == "UNKNOWN"
