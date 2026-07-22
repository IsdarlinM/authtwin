from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
from .models import (
    Actor,
    AuthorizationObservation,
    CandidateFinding,
    Decision,
    Invariant,
    InvariantKind,
    Resource,
    SessionEvent,
    CounterfactualPlan,
    CoverageReport,
    SkepticAssessment,
)
from .store import JsonStore
from sric.models import ClaimStatus
from sric.graph import GraphEdge, GraphNode, TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage, LineageRecord

MUTATING = {"CREATE", "UPDATE", "PATCH", "DELETE", "SHARE", "UNSHARE", "TRANSFER", "EXPORT"}


MAX_IMPORT_BYTES = 10 * 1024 * 1024


def _load_json_file(path: Path) -> Any:
    if not path.is_file() or path.is_symlink():
        raise ValueError("import path must be a regular non-symlink file")
    size = path.stat().st_size
    if size > MAX_IMPORT_BYTES:
        raise ValueError(f"import exceeds {MAX_IMPORT_BYTES} byte limit")
    return __import__("json").loads(path.read_text(encoding="utf-8"))


def _upsert(items: list[dict[str, Any]], key: str, value: dict[str, Any]) -> None:
    for i, item in enumerate(items):
        if item.get(key) == value.get(key):
            items[i] = value
            return
    items.append(value)


class AuthTwinEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.store = JsonStore(workspace)
        self.graph = TemporalGraph(workspace)
        self.jobs = JobEngine(workspace)
        self.lineage = EvidenceLineage(workspace)

    def add_actor(self, actor: Actor) -> None:
        data = self.store.load()
        _upsert(data["actors"], "actor_id", actor.model_dump(mode="json"))
        self.store.save(data)
        self.graph.upsert_node(GraphNode(node_id=f"actor:{actor.actor_id}", node_type="actor", label=actor.name, source="authtwin", metadata={"roles": actor.roles, "tenant": actor.tenant, "suspended": actor.suspended}))
        self._lineage_once(LineageRecord(artifact_id=f"actor:{actor.actor_id}", artifact_type="actor", status="OBSERVED", source="authtwin", method="user_or_import"))

    def add_resource(self, resource: Resource) -> None:
        data = self.store.load()
        _upsert(data["resources"], "resource_id", resource.model_dump(mode="json"))
        self.store.save(data)
        self.graph.upsert_node(GraphNode(node_id=f"resource:{resource.resource_id}", node_type="resource", label=resource.resource_id, source="authtwin", metadata={"resource_type": resource.resource_type, "owner_actor_id": resource.owner_actor_id, "tenant": resource.tenant, "state": resource.state}))
        self._lineage_once(LineageRecord(artifact_id=f"resource:{resource.resource_id}", artifact_type="resource", status="OBSERVED", source="authtwin", method="user_or_import"))
        if resource.owner_actor_id:
            try:
                self.graph.upsert_edge(GraphEdge(edge_id=f"owns:{resource.owner_actor_id}:{resource.resource_id}", source_node_id=f"actor:{resource.owner_actor_id}", target_node_id=f"resource:{resource.resource_id}", edge_type="owns", discovery_method="explicit_model", evidence_ids=[]))
            except ValueError:
                pass

    def observe(self, observation: AuthorizationObservation) -> None:
        data = self.store.load()
        actor_ids = {x["actor_id"] for x in data["actors"]}
        resource_ids = {x["resource_id"] for x in data["resources"]}
        if observation.actor_id not in actor_ids:
            raise ValueError(f"unknown actor: {observation.actor_id}")
        if observation.resource_id not in resource_ids:
            raise ValueError(f"unknown resource: {observation.resource_id}")
        _upsert(data["observations"], "observation_id", observation.model_dump(mode="json"))
        self.store.save(data)
        obs_node = GraphNode(node_id=f"observation:{observation.observation_id}", node_type="authorization_observation", label=f"{observation.operation} {observation.resource_id}", source=observation.source, evidence_ids=observation.evidence_ids, metadata={"decision": observation.decision.value, "actor_id": observation.actor_id, "resource_id": observation.resource_id, "state": observation.state})
        self.graph.upsert_node(obs_node)
        for target, edge_type in ((f"actor:{observation.actor_id}", "performed_by"), (f"resource:{observation.resource_id}", "targets")):
            self.graph.upsert_edge(GraphEdge(source_node_id=obs_node.node_id, target_node_id=target, edge_type=edge_type, discovery_method="authorization_observation", evidence_ids=observation.evidence_ids))
        self._lineage_once(LineageRecord(artifact_id=f"observation:{observation.observation_id}", artifact_type="authorization_observation", status="OBSERVED", source=observation.source, method="observe", evidence_ids=observation.evidence_ids, parent_ids=[f"actor:{observation.actor_id}", f"resource:{observation.resource_id}"]))

    def add_invariant(self, invariant: Invariant) -> None:
        data = self.store.load()
        _upsert(data["invariants"], "invariant_id", invariant.model_dump(mode="json"))
        self.store.save(data)

    def matrix(self) -> dict[str, Any]:
        data = self.store.load()
        actors = [x["actor_id"] for x in data["actors"]]
        rows: dict[tuple[str, str], dict[str, str]] = defaultdict(
            lambda: {a: Decision.UNKNOWN.value for a in actors}
        )
        for obs in data["observations"]:
            rows[(obs["resource_id"], obs["operation"].upper())][obs["actor_id"]] = obs["decision"]
        return {
            "actors": actors,
            "rows": [
                {"resource_id": r, "operation": o, "decisions": d}
                for (r, o), d in sorted(rows.items())
            ],
        }

    def state_machine(self) -> dict[str, list[dict[str, Any]]]:
        """Derive observed resource-state transitions without inventing missing states."""
        data = self.store.load()
        resources = {x["resource_id"]: Resource.model_validate(x) for x in data["resources"]}
        by_resource: dict[str, list[AuthorizationObservation]] = defaultdict(list)
        for raw in data["observations"]:
            obs = AuthorizationObservation.model_validate(raw)
            by_resource[obs.resource_id].append(obs)
        result: dict[str, list[dict[str, Any]]] = {}
        for resource_id, resource in resources.items():
            events = sorted(by_resource.get(resource_id, []), key=lambda x: x.observed_at)
            transitions: list[dict[str, Any]] = []
            previous: str | None = None
            for obs in events:
                if not obs.state:
                    continue
                if previous is None:
                    transitions.append(
                        {
                            "from": "UNKNOWN",
                            "to": obs.state,
                            "observation_id": obs.observation_id,
                            "evidence_ids": obs.evidence_ids,
                            "observed_at": obs.observed_at.isoformat(),
                        }
                    )
                elif previous != obs.state:
                    transitions.append(
                        {
                            "from": previous,
                            "to": obs.state,
                            "observation_id": obs.observation_id,
                            "evidence_ids": obs.evidence_ids,
                            "observed_at": obs.observed_at.isoformat(),
                        }
                    )
                previous = obs.state
            if not transitions and resource.state:
                transitions.append(
                    {
                        "from": "UNKNOWN",
                        "to": resource.state,
                        "observation_id": None,
                        "evidence_ids": [],
                        "observed_at": None,
                        "note": "Current modeled state only; transition history is UNKNOWN.",
                    }
                )
            result[resource_id] = transitions
        return result

    def compare(self, actor_a: str, actor_b: str) -> list[dict[str, Any]]:
        matrix = self.matrix()
        out = []
        for row in matrix["rows"]:
            a = row["decisions"].get(actor_a, Decision.UNKNOWN.value)
            b = row["decisions"].get(actor_b, Decision.UNKNOWN.value)
            if a != b:
                out.append(
                    {
                        "resource_id": row["resource_id"],
                        "operation": row["operation"],
                        actor_a: a,
                        actor_b: b,
                    }
                )
        return out

    def evaluate(self) -> list[CandidateFinding]:
        data = self.store.load()
        actors = {x["actor_id"]: Actor.model_validate(x) for x in data["actors"]}
        resources = {x["resource_id"]: Resource.model_validate(x) for x in data["resources"]}
        invariants = [
            Invariant.model_validate(x) for x in data["invariants"] if x.get("enabled", True)
        ]
        findings: list[CandidateFinding] = []
        for obs_raw in data["observations"]:
            obs = AuthorizationObservation.model_validate(obs_raw)
            actor = actors[obs.actor_id]
            resource = resources[obs.resource_id]
            if obs.decision != Decision.ALLOW:
                continue
            for inv in invariants:
                violation = False
                alternatives = []
                if inv.kind == InvariantKind.DENY_OTHER_OWNER_MUTATION:
                    ops = {x.upper() for x in (inv.operations or list(MUTATING))}
                    violation = obs.operation.upper() in ops and resource.owner_actor_id not in {
                        None,
                        obs.actor_id,
                    }
                    if obs.actor_id in resource.shared_with:
                        alternatives.append(
                            "Actor is listed in resource.shared_with; sharing may legitimately grant this operation."
                        )
                    if actor.tenant and resource.tenant and actor.tenant == resource.tenant:
                        alternatives.append(
                            "Actor and resource share a tenant; tenant policy may legitimately grant access."
                        )
                elif inv.kind == InvariantKind.DENY_SUSPENDED:
                    violation = actor.suspended
                elif inv.kind == InvariantKind.DENY_REVOKED:
                    violation = resource.state.lower() in {"revoked", "unshared"} or obs.state in {
                        "revoked",
                        "unshared",
                    }
                if violation:
                    base = 0.82 if obs.evidence_ids else 0.58
                    if alternatives:
                        base -= min(0.25, 0.1 * len(alternatives))
                    findings.append(
                        CandidateFinding(
                            finding_id=f"FND-{len(findings) + 1:04d}",
                            invariant_id=inv.invariant_id,
                            title=f"Candidate invariant violation: {inv.description}",
                            confidence=max(0.1, base),
                            supporting_observation_ids=[obs.observation_id],
                            evidence_ids=obs.evidence_ids,
                            alternative_explanations=alternatives,
                            limitations=[
                                "Authorization intent is not inferred from status code alone.",
                                "Candidate remains HYPOTHESIS until deterministic validation and evidence review.",
                            ],
                        )
                    )
        data["findings"] = [f.model_dump(mode="json") for f in findings]
        self.store.save(data)
        return findings

    def validate(self, finding_id: str, evidence_ids: list[str], note: str) -> CandidateFinding:
        if not evidence_ids:
            raise ValueError("VALIDATED findings require evidence")
        data = self.store.load()
        for i, item in enumerate(data["findings"]):
            if item["finding_id"] == finding_id:
                f = CandidateFinding.model_validate(item)
                f.status = ClaimStatus.VALIDATED
                f.evidence_ids = sorted(set(f.evidence_ids + evidence_ids))
                f.validation_note = note
                data["findings"][i] = f.model_dump(mode="json")
                self.store.save(data)
                return f
        raise KeyError(finding_id)

    def _lineage_once(self, record: LineageRecord) -> None:
        try:
            self.lineage.explain(record.artifact_id)
        except KeyError:
            self.lineage.append(record)

    def coverage(self) -> CoverageReport:
        matrix = self.matrix()
        actors = len(matrix["actors"])
        pairs = len(matrix["rows"])
        possible = actors * pairs
        observed = sum(1 for row in matrix["rows"] for value in row["decisions"].values() if value != Decision.UNKNOWN.value)
        unknown = max(0, possible - observed)
        return CoverageReport(actors=actors, resource_operation_pairs=pairs, possible_cells=possible, observed_cells=observed, unknown_cells=unknown, coverage=(observed / possible if possible else 0.0))

    def discover_resources(self) -> dict[str, int]:
        """Derive resource/operation candidates only from supplied observations and endpoint metadata."""
        data = self.store.load()
        operations: dict[str, set[str]] = defaultdict(set)
        identifiers: set[str] = set()
        for raw in data["observations"]:
            obs = AuthorizationObservation.model_validate(raw)
            operations[obs.resource_id].add(obs.operation.upper())
            for key in ("object_id", "resource_identifier", "graphql_field"):
                value = obs.metadata.get(key)
                if isinstance(value, str) and value:
                    identifiers.add(value)
        return {"resource_types": len({r["resource_type"] for r in data["resources"]}), "resources": len(data["resources"]), "operations": sum(len(v) for v in operations.values()), "candidate_identifiers": len(identifiers)}

    def counterfactuals(self, source_observation_id: str | None = None) -> list[CounterfactualPlan]:
        data = self.store.load()
        actors = [Actor.model_validate(x) for x in data["actors"]]
        observations = [AuthorizationObservation.model_validate(x) for x in data["observations"]]
        plans: list[CounterfactualPlan] = []
        for obs in observations:
            if source_observation_id and obs.observation_id != source_observation_id:
                continue
            for actor in actors:
                if actor.actor_id == obs.actor_id:
                    continue
                action_class = "READ_ONLY_SENSITIVE" if obs.operation.upper() in {"READ", "LIST", "GET"} else "MUTATING_REVERSIBLE"
                plans.append(CounterfactualPlan(plan_id=f"CF-{len(plans)+1:04d}", source_observation_id=obs.observation_id, source_actor_id=obs.actor_id, candidate_actor_id=actor.actor_id, resource_id=obs.resource_id, operation=obs.operation, action_class=action_class, evidence_ids=obs.evidence_ids, rationale=["Plan mirrors an observed operation with a different test actor.", "Execution is not automatic and requires scope/policy/approval."]))
        data["counterfactual_plans"] = [p.model_dump(mode="json") for p in plans]
        self.store.save(data)
        return plans

    def add_session_event(self, event: SessionEvent) -> None:
        data = self.store.load()
        if event.actor_id not in {x["actor_id"] for x in data["actors"]}:
            raise ValueError(f"unknown actor: {event.actor_id}")
        _upsert(data["session_events"], "event_id", event.model_dump(mode="json"))
        self.store.save(data)
        self._lineage_once(LineageRecord(artifact_id=f"session:{event.event_id}", artifact_type="session_event", status="OBSERVED", source="authtwin", method=event.event_type, evidence_ids=event.evidence_ids, parent_ids=[f"actor:{event.actor_id}"]))

    def session_lifecycle(self, actor_id: str) -> list[dict[str, Any]]:
        data = self.store.load()
        events = [SessionEvent.model_validate(x) for x in data["session_events"] if x["actor_id"] == actor_id]
        return [x.model_dump(mode="json") for x in sorted(events, key=lambda e: e.observed_at)]

    def parse_invariant_dsl(self, text: str) -> Invariant:
        """Parse a deliberately small auditable DSL; unsupported semantics fail closed."""
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
        values: dict[str, str] = {}
        for line in lines:
            if ":" not in line:
                raise ValueError(f"invalid invariant DSL line: {line}")
            key, value = line.split(":", 1)
            values[key.strip().lower()] = value.strip()
        required = {"id", "description", "kind"}
        missing = required - values.keys()
        if missing:
            raise ValueError(f"missing invariant DSL keys: {', '.join(sorted(missing))}")
        try:
            kind = InvariantKind(values["kind"].upper())
        except ValueError as exc:
            raise ValueError("unsupported invariant kind") from exc
        operations = [x.strip().upper() for x in values.get("operations", "").split(",") if x.strip()]
        return Invariant(invariant_id=values["id"], description=values["description"], kind=kind, operations=operations)

    def graphql_surface(self) -> list[dict[str, Any]]:
        data = self.store.load()
        surface: dict[tuple[str, str], dict[str, Any]] = {}
        for raw in data["observations"]:
            obs = AuthorizationObservation.model_validate(raw)
            operation_name = obs.metadata.get("graphql_operation")
            field = obs.metadata.get("graphql_field")
            if not isinstance(operation_name, str) and not isinstance(field, str):
                continue
            key = (str(operation_name or "anonymous"), str(field or "unknown"))
            item = surface.setdefault(key, {"operation": key[0], "field": key[1], "actors": {}, "evidence_ids": []})
            item["actors"][obs.actor_id] = obs.decision.value
            item["evidence_ids"] = sorted(set(item["evidence_ids"] + obs.evidence_ids))
        return list(surface.values())

    def batch_authorization(self) -> list[dict[str, Any]]:
        data = self.store.load()
        results: list[dict[str, Any]] = []
        for raw in data["observations"]:
            obs = AuthorizationObservation.model_validate(raw)
            items = obs.metadata.get("batch_items")
            if not isinstance(items, list):
                continue
            normalized = [x for x in items if isinstance(x, dict)]
            decisions = {str(x.get("decision", "UNKNOWN")) for x in normalized}
            results.append({"observation_id": obs.observation_id, "resource_id": obs.resource_id, "item_count": len(normalized), "mixed_decisions": len(decisions) > 1, "decisions": sorted(decisions), "evidence_ids": obs.evidence_ids})
        return results

    def skeptic_review(self, finding_id: str) -> SkepticAssessment:
        data = self.store.load()
        raw = next((x for x in data["findings"] if x["finding_id"] == finding_id), None)
        if raw is None:
            raise KeyError(finding_id)
        finding = CandidateFinding.model_validate(raw)
        alternatives = list(finding.alternative_explanations)
        common = ["Resource may be public by design.", "Actor may have an unmodeled legitimate relationship or inherited tenant role.", "Observed response may be cache/metadata rather than protected object access.", "Authorization may be enforced at a different layer not represented in the current evidence."]
        for item in common:
            if item not in alternatives:
                alternatives.append(item)
        missing = [] if finding.evidence_ids else ["No evidence references are attached to the candidate."]
        tests = ["Confirm resource ownership/visibility using authoritative test data.", "Repeat the same operation with a control actor lacking the suspected relationship.", "Compare response semantics, not status code alone.", "Re-test after relevant state transition (share/revoke/role change) when authorized."]
        status = "VALIDATION_READY" if finding.evidence_ids and not missing else "NEEDS_EVIDENCE"
        return SkepticAssessment(finding_id=finding_id, alternative_explanations=alternatives, missing_evidence=missing, counter_tests=tests, recommended_status=status)

    def import_rcap(self, path: Path) -> dict[str, int]:
        """Import an RCAP as observations without inferring authorization from HTTP status alone."""
        import hashlib
        import json
        import tempfile
        from urllib.parse import urlsplit

        try:
            from reprosec.capsule import safe_extract
        except ImportError as exc:
            raise RuntimeError("RCAP import requires a compatible ReproSec 0.3.x release") from exc
        counts = {"actors": 0, "resources": 0, "observations": 0}
        with tempfile.TemporaryDirectory() as td:
            root = safe_extract(path, Path(td) / "capsule")
            request_map: dict[str, dict[str, Any]] = {}
            for req_path in sorted((root / "requests").glob("*.json")):
                req = json.loads(req_path.read_text(encoding="utf-8"))
                request_map[str(req["request_id"])] = req
            response_by_request: dict[str, dict[str, Any]] = {}
            for res_path in sorted((root / "responses").glob("*.json")):
                res = json.loads(res_path.read_text(encoding="utf-8"))
                response_by_request[str(res["request_id"])] = res
            for step_path in sorted((root / "workflow").glob("*.json")):
                step = json.loads(step_path.read_text(encoding="utf-8"))
                actor_id = str(step.get("actor") or "unknown-actor")
                self.add_actor(Actor(actor_id=actor_id, name=actor_id, metadata={"source": "rcap"}))
                counts["actors"] += 1
                req = request_map.get(str(step.get("request_id")))
                if req is None:
                    continue
                parsed = urlsplit(str(req.get("url", "")))
                resource_value = f"{parsed.hostname or 'unknown'}{parsed.path or '/'}"
                resource_id = "http-" + hashlib.sha256(resource_value.encode()).hexdigest()[:12]
                self.add_resource(
                    Resource(
                        resource_id=resource_id,
                        resource_type="http_endpoint",
                        metadata={"url_template": resource_value, "source": "rcap"},
                    )
                )
                counts["resources"] += 1
                method = str(req.get("method", "GET")).upper()
                operation = {
                    "GET": "READ",
                    "HEAD": "READ",
                    "POST": "CREATE",
                    "PUT": "UPDATE",
                    "PATCH": "UPDATE",
                    "DELETE": "DELETE",
                }.get(method, method)
                res = response_by_request.get(str(req.get("request_id")))
                evidence = [str(req.get("request_id"))]
                status_code = None
                metadata: dict[str, Any] = {
                    "http_method": method,
                    "source": "rcap",
                    "authorization_interpretation": "UNKNOWN",
                }
                if res is not None:
                    evidence.append(str(res.get("response_id")))
                    status_code = int(res["status_code"])
                    metadata["http_status_code"] = status_code
                self.observe(
                    AuthorizationObservation(
                        observation_id=f"OBS-RCAP-{step.get('step_id', counts['observations'] + 1)}",
                        actor_id=actor_id,
                        resource_id=resource_id,
                        operation=operation,
                        decision=Decision.UNKNOWN,
                        status_code=status_code,
                        evidence_ids=evidence,
                        source="imported",
                        metadata=metadata,
                    )
                )
                counts["observations"] += 1
        return counts

    def import_json(self, path: Path) -> dict[str, int]:

        payload = _load_json_file(path)
        counts = {"actors": 0, "resources": 0, "observations": 0, "invariants": 0}
        for item in payload.get("actors", []):
            self.add_actor(Actor.model_validate(item))
            counts["actors"] += 1
        for item in payload.get("resources", []):
            self.add_resource(Resource.model_validate(item))
            counts["resources"] += 1
        for item in payload.get("observations", []):
            self.observe(AuthorizationObservation.model_validate(item))
            counts["observations"] += 1
        for item in payload.get("invariants", []):
            self.add_invariant(Invariant.model_validate(item))
            counts["invariants"] += 1
        return counts

    def export_rcap(self, output: Path) -> Path:
        """Export the authorization model as evidence inside a valid RCAP capsule."""
        import tempfile

        try:
            from reprosec.capsule import initialize_directory, pack
        except ImportError as exc:
            raise RuntimeError(
                "RCAP export requires a compatible ReproSec 0.3.x release; install authtwin[rcap] or a trusted ReproSec release"
            ) from exc
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "authtwin-rcap"
            initialize_directory(root, "AuthTwin authorization model")
            evidence = root / "evidence" / "authtwin-model.json"
            evidence.write_text(
                __import__("json").dumps(self.export_bridge(), indent=2, default=str) + "\n",
                encoding="utf-8",
            )
            provenance = root / "provenance" / "authtwin.json"
            provenance.write_text(
                __import__("json").dumps(
                    {
                        "source": "authtwin",
                        "status_rule": "Only explicit human validation with evidence may produce VALIDATED findings.",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            return pack(root, output)

    def export_bridge(self) -> dict[str, Any]:
        data = self.store.load()
        return {
            "format": "sric.authorization-model",
            "version": "0.1",
            "actors": data["actors"],
            "resources": data["resources"],
            "observations": data["observations"],
            "invariants": data["invariants"],
            "findings": data["findings"],
        }
