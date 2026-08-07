from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AccessDecision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    UNKNOWN = "UNKNOWN"


class GraphQLFieldObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str
    operation_name: str
    operation_kind: str
    field_path: str
    actor_id: str
    tenant_id: str | None = None
    resource_id: str | None = None
    resource_state: str = "UNKNOWN"
    actor_state: str = "ACTIVE"
    decision: AccessDecision
    response_shape_hash: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def observed_decisions_require_evidence(self) -> "GraphQLFieldObservation":
        if self.decision is not AccessDecision.UNKNOWN and not self.evidence_ids:
            raise ValueError("ALLOW/DENY field observations require evidence_ids")
        return self


class GraphQLFieldComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparison_id: str
    operation_name: str
    field_path: str
    tenant_id: str | None = None
    resource_id: str | None = None
    resource_state: str
    actor_decisions: dict[str, AccessDecision]
    status: ClaimStatus
    hypothesis: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def compare_graphql_fields(
    observations: Sequence[GraphQLFieldObservation],
) -> list[GraphQLFieldComparison]:
    grouped: dict[
        tuple[str, str, str | None, str | None, str],
        list[GraphQLFieldObservation],
    ] = defaultdict(list)
    for item in observations:
        key = (
            item.operation_name,
            item.field_path,
            item.tenant_id,
            item.resource_id,
            item.resource_state,
        )
        grouped[key].append(item)

    output: list[GraphQLFieldComparison] = []
    for key in sorted(grouped, key=lambda item: tuple("" if value is None else value for value in item)):
        values = grouped[key]
        actor_decisions: dict[str, AccessDecision] = {}
        conflicting_actors: list[str] = []
        for actor_id in sorted({item.actor_id for item in values}):
            decisions = {item.decision for item in values if item.actor_id == actor_id}
            if len(decisions) == 1:
                actor_decisions[actor_id] = next(iter(decisions))
            else:
                actor_decisions[actor_id] = AccessDecision.UNKNOWN
                conflicting_actors.append(actor_id)

        missing: list[str] = []
        if len(actor_decisions) < 2:
            missing.append("second actor observation in equivalent context")
        if any(value is AccessDecision.UNKNOWN for value in actor_decisions.values()):
            missing.append("deterministic field decision for every actor")
        decisions = set(actor_decisions.values()) - {AccessDecision.UNKNOWN}
        hypothesis: str | None = None
        if missing:
            status = ClaimStatus.UNKNOWN
        elif len(decisions) > 1:
            status = ClaimStatus.HYPOTHESIS
            hypothesis = (
                "Equivalent-context actors received different field-level authorization decisions."
            )
        else:
            status = ClaimStatus.OBSERVED

        operation, field_path, tenant_id, resource_id, resource_state = key
        output.append(
            GraphQLFieldComparison(
                comparison_id=(
                    f"graphql:{operation}:{field_path}:{tenant_id or '-'}:"
                    f"{resource_id or '-'}:{resource_state}"
                ),
                operation_name=operation,
                field_path=field_path,
                tenant_id=tenant_id,
                resource_id=resource_id,
                resource_state=resource_state,
                actor_decisions=actor_decisions,
                status=status,
                hypothesis=hypothesis,
                evidence_ids=sorted(
                    {evidence for item in values for evidence in item.evidence_ids}
                ),
                missing_evidence=sorted(set(missing)),
                limitations=[
                    "Different field decisions are not proof of improper authorization; roles, ownership and policy intent must be evaluated.",
                    "Response-shape differences, resolver errors and masking behavior require deterministic controls."
                ],
            )
        )
    return output


class SubscriptionEventObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str
    subscription_id: str
    actor_id: str
    tenant_id: str | None = None
    topic: str
    event_index: int = Field(ge=0)
    received_at: datetime = Field(default_factory=utcnow)
    revocation_observed_at: datetime | None = None
    session_reauthenticated: bool = False
    connection_reestablished: bool = False
    received_payload: bool = True
    payload_shape_hash: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def received_events_require_evidence(self) -> "SubscriptionEventObservation":
        if self.received_payload and not self.evidence_ids:
            raise ValueError("received subscription events require evidence_ids")
        return self


class SubscriptionRevocationAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subscription_id: str
    status: ClaimStatus
    events_before_revocation: int
    events_after_revocation: int
    post_revocation_event_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    hypothesis: str | None = None


def assess_subscription_revocation(
    events: Sequence[SubscriptionEventObservation],
) -> list[SubscriptionRevocationAssessment]:
    grouped: dict[str, list[SubscriptionEventObservation]] = defaultdict(list)
    for event in events:
        grouped[event.subscription_id].append(event)

    output: list[SubscriptionRevocationAssessment] = []
    for subscription_id in sorted(grouped):
        values = sorted(
            grouped[subscription_id],
            key=lambda item: (item.received_at, item.event_index, item.observation_id),
        )
        revocations = [
            item.revocation_observed_at
            for item in values
            if item.revocation_observed_at is not None
        ]
        missing: list[str] = []
        if not revocations:
            missing.append("evidence-bearing revocation timestamp")
            revocation = None
        else:
            revocation = min(revocations)

        before = [
            item for item in values if revocation is not None and item.received_at < revocation
        ]
        after = [
            item
            for item in values
            if revocation is not None
            and item.received_at >= revocation
            and item.received_payload
        ]
        alternatives: list[str] = []
        if any(item.session_reauthenticated for item in after):
            alternatives.append("The session may have been reauthenticated after revocation.")
        if any(item.connection_reestablished for item in after):
            alternatives.append("The connection may have been reestablished under new authorization state.")
        if after and not before:
            missing.append("pre-revocation control event")

        if missing:
            status = ClaimStatus.UNKNOWN
            hypothesis = None
        elif after:
            status = ClaimStatus.HYPOTHESIS
            hypothesis = "Subscription payloads were observed after the recorded revocation instant."
        else:
            status = ClaimStatus.OBSERVED
            hypothesis = None

        output.append(
            SubscriptionRevocationAssessment(
                subscription_id=subscription_id,
                status=status,
                events_before_revocation=len(before),
                events_after_revocation=len(after),
                post_revocation_event_ids=[item.observation_id for item in after],
                evidence_ids=sorted(
                    {evidence for item in values for evidence in item.evidence_ids}
                ),
                counter_evidence_ids=sorted(
                    {
                        evidence
                        for item in values
                        for evidence in item.counter_evidence_ids
                    }
                ),
                missing_evidence=sorted(set(missing)),
                alternative_explanations=sorted(set(alternatives)),
                hypothesis=hypothesis,
            )
        )
    return output
