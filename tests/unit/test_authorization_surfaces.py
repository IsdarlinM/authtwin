from datetime import datetime, timedelta, timezone

import pytest

from authtwin.surfaces import (
    AccessDecision,
    GraphQLFieldObservation,
    SubscriptionEventObservation,
    assess_subscription_revocation,
    compare_graphql_fields,
)
from sric.models import ClaimStatus


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def field(
    observation_id: str,
    actor: str,
    decision: AccessDecision,
) -> GraphQLFieldObservation:
    return GraphQLFieldObservation(
        observation_id=observation_id,
        operation_name="GetDocument",
        operation_kind="QUERY",
        field_path="document.owner.email",
        actor_id=actor,
        tenant_id="tenant-a",
        resource_id="doc-1",
        resource_state="ACTIVE",
        decision=decision,
        evidence_ids=[f"E-{observation_id}"] if decision is not AccessDecision.UNKNOWN else [],
    )


def test_equivalent_actor_field_difference_is_hypothesis_only() -> None:
    report = compare_graphql_fields(
        [field("owner", "owner", AccessDecision.ALLOW), field("other", "other", AccessDecision.DENY)]
    )[0]

    assert report.status is ClaimStatus.HYPOTHESIS
    assert report.hypothesis
    assert "not proof" in report.limitations[0]


def test_single_actor_field_observation_remains_unknown() -> None:
    report = compare_graphql_fields([field("owner", "owner", AccessDecision.ALLOW)])[0]

    assert report.status is ClaimStatus.UNKNOWN
    assert report.missing_evidence


def test_conflicting_same_actor_decisions_remain_unknown() -> None:
    observations = [
        field("one", "owner", AccessDecision.ALLOW),
        field("two", "owner", AccessDecision.DENY),
        field("three", "other", AccessDecision.DENY),
    ]

    report = compare_graphql_fields(observations)[0]

    assert report.actor_decisions["owner"] is AccessDecision.UNKNOWN
    assert report.status is ClaimStatus.UNKNOWN


def test_observed_field_decision_requires_evidence() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        GraphQLFieldObservation(
            observation_id="invalid",
            operation_name="Get",
            operation_kind="QUERY",
            field_path="user.email",
            actor_id="actor",
            decision=AccessDecision.ALLOW,
        )


def event(
    observation_id: str,
    index: int,
    received_at: datetime,
    *,
    revocation: datetime | None,
    reauthenticated: bool = False,
) -> SubscriptionEventObservation:
    return SubscriptionEventObservation(
        observation_id=observation_id,
        subscription_id="SUB-1",
        actor_id="actor",
        tenant_id="tenant-a",
        topic="document.updated",
        event_index=index,
        received_at=received_at,
        revocation_observed_at=revocation,
        session_reauthenticated=reauthenticated,
        evidence_ids=[f"E-{observation_id}"],
    )


def test_post_revocation_payload_is_hypothesis_with_control() -> None:
    revocation = T0 + timedelta(minutes=5)
    report = assess_subscription_revocation(
        [
            event("before", 0, T0, revocation=revocation),
            event("after", 1, T0 + timedelta(minutes=6), revocation=revocation),
        ]
    )[0]

    assert report.status is ClaimStatus.HYPOTHESIS
    assert report.events_after_revocation == 1


def test_missing_revocation_or_precontrol_remains_unknown() -> None:
    no_revocation = assess_subscription_revocation(
        [event("event", 0, T0, revocation=None)]
    )[0]
    revocation = T0
    no_precontrol = assess_subscription_revocation(
        [event("after", 0, T0 + timedelta(seconds=1), revocation=revocation)]
    )[0]

    assert no_revocation.status is ClaimStatus.UNKNOWN
    assert no_precontrol.status is ClaimStatus.UNKNOWN


def test_reauthentication_is_recorded_as_alternative_explanation() -> None:
    revocation = T0 + timedelta(minutes=1)
    report = assess_subscription_revocation(
        [
            event("before", 0, T0, revocation=revocation),
            event(
                "after",
                1,
                T0 + timedelta(minutes=2),
                revocation=revocation,
                reauthenticated=True,
            ),
        ]
    )[0]

    assert any("reauthenticated" in item for item in report.alternative_explanations)
