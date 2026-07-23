from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Decision(StrEnum): ALLOW="ALLOW";DENY="DENY";UNKNOWN="UNKNOWN"
class Actor(BaseModel):
    model_config=ConfigDict(extra="forbid");actor_id:str;name:str;roles:list[str]=Field(default_factory=list);tenant:str|None=None;suspended:bool=False;metadata:dict[str,Any]=Field(default_factory=dict)
class Resource(BaseModel):
    model_config=ConfigDict(extra="forbid");resource_id:str;resource_type:str;owner_actor_id:str|None=None;tenant:str|None=None;state:str="active";shared_with:list[str]=Field(default_factory=list);metadata:dict[str,Any]=Field(default_factory=dict)
class AuthorizationObservation(BaseModel):
    model_config=ConfigDict(extra="forbid");observation_id:str;actor_id:str;resource_id:str;operation:str;decision:Decision;status_code:int|None=None;state:str|None=None;evidence_ids:list[str]=Field(default_factory=list);source:str="user_input";observed_at:datetime=Field(default_factory=utcnow);metadata:dict[str,Any]=Field(default_factory=dict)
class InvariantKind(StrEnum): DENY_OTHER_OWNER_MUTATION="DENY_OTHER_OWNER_MUTATION";DENY_SUSPENDED="DENY_SUSPENDED";DENY_REVOKED="DENY_REVOKED";CUSTOM="CUSTOM"
class Invariant(BaseModel):
    model_config=ConfigDict(extra="forbid");invariant_id:str;description:str;kind:InvariantKind;operations:list[str]=Field(default_factory=list);enabled:bool=True;metadata:dict[str,Any]=Field(default_factory=dict)
class CandidateFinding(BaseModel):
    model_config=ConfigDict(extra="forbid");finding_id:str;invariant_id:str;title:str;status:ClaimStatus=ClaimStatus.HYPOTHESIS;confidence:float=Field(ge=0,le=1);supporting_observation_ids:list[str];evidence_ids:list[str]=Field(default_factory=list);counter_evidence_ids:list[str]=Field(default_factory=list);alternative_explanations:list[str]=Field(default_factory=list);limitations:list[str]=Field(default_factory=list);validation_note:str|None=None
class SessionEvent(BaseModel):
    model_config=ConfigDict(extra="forbid");event_id:str;actor_id:str;event_type:str;observed_at:datetime=Field(default_factory=utcnow);session_id_hash:str|None=None;evidence_ids:list[str]=Field(default_factory=list);metadata:dict[str,Any]=Field(default_factory=dict)
class CounterfactualPlan(BaseModel):
    model_config=ConfigDict(extra="forbid");plan_id:str;source_observation_id:str;source_actor_id:str;candidate_actor_id:str;resource_id:str;operation:str;status:ClaimStatus=ClaimStatus.HYPOTHESIS;action_class:str;requires_approval:bool=True;evidence_ids:list[str]=Field(default_factory=list);rationale:list[str]=Field(default_factory=list)
class CoverageReport(BaseModel):
    model_config=ConfigDict(extra="forbid");actors:int;resource_operation_pairs:int;possible_cells:int;observed_cells:int;unknown_cells:int;coverage:float=Field(ge=0,le=1)
class SkepticAssessment(BaseModel):
    model_config=ConfigDict(extra="forbid");finding_id:str;alternative_explanations:list[str]=Field(default_factory=list);missing_evidence:list[str]=Field(default_factory=list);counter_tests:list[str]=Field(default_factory=list);recommended_status:str
class MembershipEvent(BaseModel):
    model_config=ConfigDict(extra="forbid");event_id:str;actor_id:str;tenant_id:str;state:str;observed_at:datetime=Field(default_factory=utcnow);evidence_ids:list[str]=Field(default_factory=list)
class ActorResourceBinding(BaseModel):
    model_config=ConfigDict(extra="forbid");binding_id:str;actor_id:str;resource_id:str;relationship:str;status:ClaimStatus=ClaimStatus.INFERRED;confidence:float=Field(ge=0,le=1);evidence_ids:list[str]=Field(default_factory=list);counter_evidence_ids:list[str]=Field(default_factory=list);rationale:list[str]=Field(default_factory=list)
class AuthorizationMutationPlan(BaseModel):
    model_config=ConfigDict(extra="forbid");plan_id:str;mutation_type:str;source_observation_id:str;actor_id:str;candidate_actor_id:str|None=None;resource_id:str;candidate_resource_id:str|None=None;operation:str;status:ClaimStatus=ClaimStatus.HYPOTHESIS;action_class:str;requires_scope:bool=True;requires_policy:bool=True;requires_rate_limit:bool=True;requires_approval:bool=True;executor:str="reprosec";rationale:list[str]=Field(default_factory=list)
class DifferentialInsight(BaseModel):
    model_config=ConfigDict(extra="forbid");insight_id:str;observation_a:str;observation_b:str;status:ClaimStatus=ClaimStatus.HYPOTHESIS;differences:list[str]=Field(default_factory=list);sensitive_differences:list[str]=Field(default_factory=list);evidence_ids:list[str]=Field(default_factory=list);limitations:list[str]=Field(default_factory=list)
