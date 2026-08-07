import pytest

from authtwin.layers import (
    AuthorizationLayer,
    AuthorizationMismatch,
    LayerObservation,
    compare_authorization_layers,
)
from authtwin.models import Decision
from sric.models import ClaimStatus


def layer(
    observation_id: str,
    authorization_layer: AuthorizationLayer,
    decision: Decision,
    *,
    tenant: str = "tenant-a",
    resource: str = "resource-1",
    evidence: list[str] | None = None,
) -> LayerObservation:
    return LayerObservation(
        observation_id=observation_id,
        layer=authorization_layer,
        actor_id="actor-1",
        tenant_id=tenant,
        resource_id=resource,
        operation="read",
        decision=decision,
        source=f"source-{authorization_layer.lower()}",
        evidence_ids=evidence or [],
    )


def complete(
    intended: Decision, configured: Decision, observed: Decision
) -> list[LayerObservation]:
    return [
        layer("intended", AuthorizationLayer.INTENDED, intended, evidence=["E-I"]),
        layer("configured", AuthorizationLayer.CONFIGURED, configured, evidence=["E-C"]),
        layer("observed", AuthorizationLayer.OBSERVED, observed, evidence=["E-O"]),
    ]


def test_observed_layer_requires_evidence() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        layer("observed", AuthorizationLayer.OBSERVED, Decision.ALLOW)


def test_missing_layer_remains_unknown() -> None:
    result = compare_authorization_layers(
        [
            layer(
                "intended",
                AuthorizationLayer.INTENDED,
                Decision.DENY,
                evidence=["E-I"],
            ),
            layer(
                "observed",
                AuthorizationLayer.OBSERVED,
                Decision.ALLOW,
                evidence=["E-O"],
            ),
        ]
    )[0]

    assert result.status is ClaimStatus.UNKNOWN
    assert result.missing_layers == [AuthorizationLayer.CONFIGURED]
    assert result.skeptic_verdict == "UNKNOWN"
    assert result.confidence <= 0.49


def test_configuration_drift_is_hypothesis_not_vulnerability() -> None:
    result = compare_authorization_layers(
        complete(Decision.DENY, Decision.ALLOW, Decision.ALLOW)
    )[0]

    assert result.status is ClaimStatus.HYPOTHESIS
    assert AuthorizationMismatch.CONFIGURATION_DRIFT in result.mismatches
    assert result.confidence <= 0.79


def test_enforcement_drift_is_hypothesis() -> None:
    result = compare_authorization_layers(
        complete(Decision.DENY, Decision.DENY, Decision.ALLOW)
    )[0]

    assert result.status is ClaimStatus.HYPOTHESIS
    assert AuthorizationMismatch.ENFORCEMENT_DRIFT in result.mismatches
    assert AuthorizationMismatch.BEHAVIORAL_DRIFT in result.mismatches
    assert result.alternative_explanations


def test_consistent_sample_is_observed_with_limitation() -> None:
    result = compare_authorization_layers(
        complete(Decision.DENY, Decision.DENY, Decision.DENY)
    )[0]

    assert result.status is ClaimStatus.OBSERVED
    assert result.mismatches == [AuthorizationMismatch.CONSISTENT_SAMPLE]
    assert "does not prove universal enforcement" in result.limitations[0]


def test_tenants_and_resource_states_are_not_cross_compared() -> None:
    first = complete(Decision.DENY, Decision.DENY, Decision.DENY)
    second = [
        layer(
            "intended-b",
            AuthorizationLayer.INTENDED,
            Decision.ALLOW,
            tenant="tenant-b",
            resource="resource-2",
            evidence=["E-I-B"],
        ),
        layer(
            "configured-b",
            AuthorizationLayer.CONFIGURED,
            Decision.ALLOW,
            tenant="tenant-b",
            resource="resource-2",
            evidence=["E-C-B"],
        ),
        layer(
            "observed-b",
            AuthorizationLayer.OBSERVED,
            Decision.ALLOW,
            tenant="tenant-b",
            resource="resource-2",
            evidence=["E-O-B"],
        ),
    ]

    results = compare_authorization_layers([*first, *second])

    assert len(results) == 2
    assert {result.tenant_id for result in results} == {"tenant-a", "tenant-b"}


def test_contradictory_observed_decisions_become_unknown() -> None:
    observations = complete(Decision.DENY, Decision.DENY, Decision.DENY)
    observations.append(
        layer(
            "observed-conflict",
            AuthorizationLayer.OBSERVED,
            Decision.ALLOW,
            evidence=["E-CONFLICT"],
        )
    )

    result = compare_authorization_layers(observations)[0]

    assert result.status is ClaimStatus.UNKNOWN
    assert AuthorizationLayer.OBSERVED in result.missing_layers
