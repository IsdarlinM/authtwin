from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from sric.models import ClaimStatus

from .models import (
    ActorResourceBinding,
    AuthorizationMutationPlan,
    AuthorizationObservation,
    DifferentialInsight,
    Invariant,
    InvariantKind,
    MembershipEvent,
)

_ID_SEGMENT = re.compile(r"^(?:\d+|[0-9a-f]{8}-[0-9a-f-]{27,}|[A-Za-z0-9_-]{12,})$", re.I)
SENSITIVE_TERMS = {"email", "phone", "owner", "tenant", "role", "permission", "billing", "private", "secret", "token"}


def normalize_endpoint(value: str) -> dict[str, Any]:
    parsed=urlsplit(value if "://" in value else f"https://placeholder{value}")
    parts=[];identifiers=[]
    for idx,part in enumerate(parsed.path.split("/")):
        if not part: continue
        if _ID_SEGMENT.match(part):
            name=f"id{len(identifiers)+1}";parts.append("{"+name+"}");identifiers.append({"position":idx,"value":part,"parameter":name})
        else:parts.append(part)
    template="/"+"/".join(parts)
    return {"host":None if parsed.hostname=="placeholder" else parsed.hostname,"template":template or "/","identifiers":identifiers}


class AuthorizationIntelligence:
    def __init__(self, engine: Any) -> None:
        self.engine=engine

    def discovery_v2(self) -> dict[str, Any]:
        data=self.engine.store.load();families:dict[str,dict[str,Any]]={}
        for raw in data["observations"]:
            obs=AuthorizationObservation.model_validate(raw)
            raw_url=obs.metadata.get("url") or obs.metadata.get("url_template")
            if not isinstance(raw_url,str):
                resource=next((r for r in data["resources"] if r["resource_id"]==obs.resource_id),{})
                raw_url=resource.get("metadata",{}).get("url_template") if isinstance(resource.get("metadata"),dict) else None
            normalized=normalize_endpoint(raw_url) if isinstance(raw_url,str) else {"template":obs.resource_id,"identifiers":[],"host":None}
            key=f"{normalized['host'] or ''}{normalized['template']}"
            item=families.setdefault(key,{"template":normalized["template"],"host":normalized["host"],"operations":set(),"resource_ids":set(),"identifier_candidates":normalized["identifiers"],"status":"INFERRED"})
            item["operations"].add(obs.operation);item["resource_ids"].add(obs.resource_id)
        out=[]
        for item in families.values():
            item["operations"]=sorted(item["operations"]);item["resource_ids"]=sorted(item["resource_ids"]);out.append(item)
        return {"families":sorted(out,key=lambda x:str(x["template"])),"ownership_status":"INFERRED_OR_UNKNOWN","note":"Endpoint normalization never proves ownership or authorization."}

    def infer_actor_resource_bindings(self) -> list[ActorResourceBinding]:
        data=self.engine.store.load();bindings=[]
        for resource in data["resources"]:
            rid=str(resource["resource_id"]);owner=resource.get("owner_actor_id")
            obs=[AuthorizationObservation.model_validate(x) for x in data["observations"] if x["resource_id"]==rid]
            if owner:
                evidence=sorted({e for o in obs if o.actor_id==owner for e in o.evidence_ids});binding=ActorResourceBinding(binding_id=f"BIND-{hashlib.sha256((owner+rid).encode()).hexdigest()[:12]}",actor_id=str(owner),resource_id=rid,relationship="candidate_owner",confidence=.75 if evidence else .55,evidence_ids=evidence,rationale=["Explicit model owner_actor_id is present.","Creation/access evidence strengthens but does not alone prove ownership."])
                bindings.append(binding)
            for o in obs:
                if o.actor_id==owner:continue
                if o.metadata.get("created_resource") is True:
                    bindings.append(ActorResourceBinding(binding_id=f"BIND-{hashlib.sha256((o.actor_id+rid+'creator').encode()).hexdigest()[:12]}",actor_id=o.actor_id,resource_id=rid,relationship="candidate_creator",confidence=.45,evidence_ids=o.evidence_ids,rationale=["Actor was observed in a creation flow.","Creation alone does not establish current ownership."]))
        data["bindings"]=[x.model_dump(mode="json") for x in bindings];self.engine.store.save(data);return bindings

    def state_machine_v2(self) -> dict[str, Any]:
        base=self.engine.state_machine();data=self.engine.store.load();actors={}
        for actor in data["actors"]:actors[actor["actor_id"]]="SUSPENDED" if actor.get("suspended") else "ACTIVE"
        for event in data.get("session_events",[]):
            et=str(event.get("event_type","")).upper();aid=str(event.get("actor_id"))
            if et in {"SUSPEND","SUSPENDED"}:actors[aid]="SUSPENDED"
            elif et in {"REMOVE","REMOVED","MEMBERSHIP_REMOVED"}:actors[aid]="REMOVED"
            elif et in {"ROLE_CHANGE","ROLE_CHANGED"}:actors[aid]="ROLE_CHANGED"
        memberships=defaultdict(list)
        for raw in data.get("memberships",[]):
            e=MembershipEvent.model_validate(raw);memberships[e.actor_id].append(e.model_dump(mode="json"))
        return {"resource_transitions":base,"actor_states":actors,"membership_events":dict(memberships),"supported_resource_states":["CREATED","PRIVATE","SHARED","UNSHARED","ARCHIVED","DELETED","TRANSFERRED"],"supported_actor_states":["ACTIVE","SUSPENDED","REMOVED","ROLE_CHANGED"],"supported_membership_states":["INVITED","ACTIVE","REMOVED"]}

    def add_membership_event(self,event:MembershipEvent)->None:
        data=self.engine.store.load();data.setdefault("memberships",[]).append(event.model_dump(mode="json"));self.engine.store.save(data)

    def mutation_plans(self, source_observation_id: str | None=None) -> list[AuthorizationMutationPlan]:
        data=self.engine.store.load();actors=[x["actor_id"] for x in data["actors"]];resources=[x["resource_id"] for x in data["resources"]];plans=[]
        observations=[AuthorizationObservation.model_validate(x) for x in data["observations"] if source_observation_id is None or x["observation_id"]==source_observation_id]
        for obs in observations:
            alternatives=[a for a in actors if a!=obs.actor_id]
            if alternatives:
                plans.append(AuthorizationMutationPlan(plan_id=f"MUT-ACTOR-{obs.observation_id}",mutation_type="SAME_REQUEST_DIFFERENT_ACTOR",source_observation_id=obs.observation_id,actor_id=obs.actor_id,candidate_actor_id=alternatives[0],resource_id=obs.resource_id,operation=obs.operation,action_class="READ_ONLY_SENSITIVE" if obs.operation in {"READ","LIST"} else "MUTATING_REVERSIBLE",rationale=["Minimal actor substitution candidate.","Must preserve all other request semantics and execute through ReproSec safety gates."]))
            other_resources=[r for r in resources if r!=obs.resource_id]
            if other_resources:
                plans.append(AuthorizationMutationPlan(plan_id=f"MUT-RESOURCE-{obs.observation_id}",mutation_type="SAME_ACTOR_DIFFERENT_RESOURCE",source_observation_id=obs.observation_id,actor_id=obs.actor_id,resource_id=obs.resource_id,candidate_resource_id=other_resources[0],operation=obs.operation,action_class="READ_ONLY_SENSITIVE" if obs.operation in {"READ","LIST"} else "MUTATING_REVERSIBLE",rationale=["Minimal resource substitution candidate.","Resource relationship must be established from authorized synthetic/test data."]))
        data["mutation_plans"]=[x.model_dump(mode="json") for x in plans];self.engine.store.save(data);return plans

    def differential_response(self, observation_a: str, observation_b: str) -> DifferentialInsight:
        data=self.engine.store.load();by={x["observation_id"]:AuthorizationObservation.model_validate(x) for x in data["observations"]}
        if observation_a not in by or observation_b not in by:raise KeyError("observation not found")
        a,b=by[observation_a],by[observation_b];diff=[];sensitive=[]
        if a.status_code!=b.status_code:diff.append(f"status:{a.status_code}->{b.status_code}")
        ma,mb=a.metadata,b.metadata
        for key in sorted(set(ma)|set(mb)):
            if ma.get(key)!=mb.get(key):
                item=f"metadata.{key} changed";diff.append(item)
                if any(term in key.casefold() for term in SENSITIVE_TERMS):sensitive.append(item)
        fields_a=set(str(x) for x in ma.get("response_fields",[]) if isinstance(x,str));fields_b=set(str(x) for x in mb.get("response_fields",[]) if isinstance(x,str))
        for f in sorted(fields_a^fields_b):
            item=f"response field differs: {f}";diff.append(item)
            if any(term in f.casefold() for term in SENSITIVE_TERMS):sensitive.append(item)
        insight=DifferentialInsight(insight_id=f"DIFF-{hashlib.sha256((observation_a+observation_b).encode()).hexdigest()[:12]}",observation_a=observation_a,observation_b=observation_b,differences=diff,sensitive_differences=sensitive,evidence_ids=sorted(set(a.evidence_ids+b.evidence_ids)),limitations=["HTTP status alone does not determine authorization intent.","Differences remain HYPOTHESIS until deterministic validation."])
        data.setdefault("differential_insights",[]).append(insight.model_dump(mode="json"));self.engine.store.save(data);return insight

    def install_invariant_library(self) -> list[str]:
        library=[
            Invariant(invariant_id="LIB-OWNERSHIP",description="Non-owner mutation must be denied unless explicit relationship permits it",kind=InvariantKind.DENY_OTHER_OWNER_MUTATION,operations=["UPDATE","PATCH","DELETE","TRANSFER"]),
            Invariant(invariant_id="LIB-SUSPENSION",description="Suspended actors must not retain protected access",kind=InvariantKind.DENY_SUSPENDED,operations=["READ","CREATE","UPDATE","DELETE"]),
            Invariant(invariant_id="LIB-REVOCATION",description="Revoked sharing/membership must not retain protected access",kind=InvariantKind.DENY_REVOKED,operations=["READ","UPDATE","DELETE"]),
            Invariant(invariant_id="LIB-TENANT",description="Cross-tenant access requires explicit modeled relationship",kind=InvariantKind.CUSTOM,operations=["READ","CREATE","UPDATE","DELETE"],metadata={"library_rule":"tenant_isolation"}),
            Invariant(invariant_id="LIB-TRANSFER",description="Ownership transfer must revoke prior-owner-only privileges",kind=InvariantKind.CUSTOM,operations=["READ","UPDATE","DELETE"],metadata={"library_rule":"ownership_transfer"}),
            Invariant(invariant_id="LIB-INVITATION",description="Invitation and membership lifecycle must gate tenant resource access",kind=InvariantKind.CUSTOM,operations=["READ","CREATE","UPDATE"],metadata={"library_rule":"invitation_lifecycle"}),
        ]
        for inv in library:self.engine.add_invariant(inv)
        return [x.invariant_id for x in library]

    def websocket_surface(self) -> list[dict[str, Any]]:
        data=self.engine.store.load();out=[]
        for raw in data["observations"]:
            obs=AuthorizationObservation.model_validate(raw);sub=obs.metadata.get("websocket_subscription")
            if isinstance(sub,str):out.append({"observation_id":obs.observation_id,"actor_id":obs.actor_id,"subscription":sub,"decision":obs.decision.value,"membership_state":obs.metadata.get("membership_state","UNKNOWN"),"revocation_observed":bool(obs.metadata.get("revocation_observed")),"evidence_ids":obs.evidence_ids})
        return out
