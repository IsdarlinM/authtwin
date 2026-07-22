from pathlib import Path
from sric.workspace import Workspace
from authtwin.core import AuthTwinEngine
from authtwin.models import (
    Actor,
    Resource,
    AuthorizationObservation,
    Decision,
    Invariant,
    InvariantKind,
)


def make(tmp_path: Path) -> AuthTwinEngine:
    ws = Workspace.create(tmp_path, "w")
    return AuthTwinEngine(ws.root)


def test_matrix_unknown_and_candidate(tmp_path: Path) -> None:
    e = make(tmp_path)
    e.add_actor(Actor(actor_id="a", name="A"))
    e.add_actor(Actor(actor_id="b", name="B"))
    e.add_resource(Resource(resource_id="r", resource_type="doc", owner_actor_id="a"))
    e.observe(
        AuthorizationObservation(
            observation_id="o",
            actor_id="b",
            resource_id="r",
            operation="UPDATE",
            decision=Decision.ALLOW,
            evidence_ids=["E1"],
        )
    )
    e.add_invariant(
        Invariant(
            invariant_id="i",
            description="deny cross-owner mutation",
            kind=InvariantKind.DENY_OTHER_OWNER_MUTATION,
            operations=["UPDATE"],
        )
    )
    m = e.matrix()
    assert m["rows"][0]["decisions"]["a"] == "UNKNOWN"
    findings = e.evaluate()
    assert len(findings) == 1
    assert findings[0].status.value == "HYPOTHESIS"


def test_validated_requires_evidence(tmp_path: Path) -> None:
    e = make(tmp_path)
    e.add_actor(Actor(actor_id="a", name="A"))
    e.add_actor(Actor(actor_id="b", name="B"))
    e.add_resource(Resource(resource_id="r", resource_type="doc", owner_actor_id="a"))
    e.observe(
        AuthorizationObservation(
            observation_id="o",
            actor_id="b",
            resource_id="r",
            operation="DELETE",
            decision=Decision.ALLOW,
        )
    )
    e.add_invariant(
        Invariant(
            invariant_id="i",
            description="deny",
            kind=InvariantKind.DENY_OTHER_OWNER_MUTATION,
            operations=["DELETE"],
        )
    )
    f = e.evaluate()[0]
    try:
        e.validate(f.finding_id, [], "x")
        assert False
    except ValueError:
        pass


def test_state_machine_preserves_unknown_history(tmp_path: Path) -> None:
    e = make(tmp_path)
    e.add_actor(Actor(actor_id="a", name="A"))
    e.add_resource(
        Resource(resource_id="r", resource_type="doc", owner_actor_id="a", state="active")
    )
    e.observe(
        AuthorizationObservation(
            observation_id="o1",
            actor_id="a",
            resource_id="r",
            operation="READ",
            decision=Decision.ALLOW,
            state="shared",
            evidence_ids=["E1"],
        )
    )
    e.observe(
        AuthorizationObservation(
            observation_id="o2",
            actor_id="a",
            resource_id="r",
            operation="READ",
            decision=Decision.DENY,
            state="unshared",
            evidence_ids=["E2"],
        )
    )
    machine = e.state_machine()["r"]
    assert machine[0]["from"] == "UNKNOWN"
    assert machine[0]["to"] == "shared"
    assert machine[1]["from"] == "shared"
    assert machine[1]["to"] == "unshared"
