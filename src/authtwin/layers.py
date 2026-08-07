from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.calibration import ConfidenceSignal, score_confidence, skeptic_review
from sric.models import ClaimStatus

from .models import Decision


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuthorizationLayer(StrEnum):
    INTENDED = "INTENDED"
    CONFIGURED = "CONFIGURED"
    OBSERVED = "OBSERVED"


class AuthorizationMismatch(StrEnum):
    CONFIGURATION_DRIFT = "CONFIGURATION_DRIFT"
    ENFORCEMENT_DRIFT = "ENFORCEMENT_DRIFT"
    BEHAVIORAL_DRIFT = "BEHAVIORAL_DRIFT"
    CONSISTENT_SAMPLE = "CONSISTENT_SAMPLE"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"


class LayerObservation(BaseModel):
    """One authorization decision from a specific evidence layer.

    Intended policy, deployed/configured policy and observed enforcement are kept
    separate. Importing configuration never proves runtime enforcement.
    """

    model_config = ConfigDict(extra="forbid")

    observation_id: str
    layer: AuthorizationLayer
    actor_id: str
    resource_id: str
    operation: str
    decision: Decision
    tenant_id: str | None = None
    resource_state: str = "active"
    actor_state: str = "active"
    session_id_hash: str | None = None
    source: str
    source_group: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def evidence_requirements(self) -> "LayerObservation":
        if self.layer is AuthorizationLayer.OBSERVED and not self.evidence_ids:
            raise ValueError("OBSERVED authorization decisions require evidence_ids")
        return self

    def comparison_key(self) -> tuple[str, str | None, str, str, str, str]:
        return (
            self.actor_id,
            self.tenant_id,
            self.resource_id,
            self.operation,
            self.resource_state,
            self.actor_state,
        )


class AuthorizationLayerComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparison_id: str
    actor_id: str
    tenant_id: str | None
    resource_id: str
    operation: str
    resource_state: str
    actor_state: str
    intended: Decision = Decision.UNKNOWN
    configured: Decision = Decision.UNKNOWN
    observed: Decision = Decision.UNKNOWN
    status: ClaimStatus
    mismatches: list[AuthorizationMismatch] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    missing_layers: list[AuthorizationLayer] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    skeptic_verdict: str
    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def _select_layer_decision(
    observations: Sequence[LayerObservation], layer: AuthorizationLayer
) -> Decision:
    values = {item.decision for item in observations if item.layer is layer}
    if len(values) != 1:
        return Decision.UNKNOWN
    return next(iter(values))


def compare_authorization_layers(
    observations: Sequence[LayerObservation],
) -> list[AuthorizationLayerComparison]:
    """Compare intended, configured and observed authorization conservatively.

    A mismatch is a candidate hypothesis only. Missing or contradictory layer
    data produces UNKNOWN. This function never validates an authorization flaw.
    """

    grouped: dict[
        tuple[str, str | None, str, str, str, str], list[LayerObservation]
    ] = defaultdict(list)
    for item in observations:
        grouped[item.comparison_key()].append(item)

    results: list[AuthorizationLayerComparison] = []
    for index, (key, items) in enumerate(sorted(grouped.items(), key=lambda value: str(value[0]))):
        actor_id, tenant_id, resource_id, operation, resource_state, actor_state = key
        intended = _select_layer_decision(items, AuthorizationLayer.INTENDED)
        configured = _select_layer_decision(items, AuthorizationLayer.CONFIGURED)
        observed = _select_layer_decision(items, AuthorizationLayer.OBSERVED)
        decisions = {
            AuthorizationLayer.INTENDED: intended,
            AuthorizationLayer.CONFIGURED: configured,
            AuthorizationLayer.OBSERVED: observed,
        }
        missing = [layer for layer, decision in decisions.items() if decision is Decision.UNKNOWN]
        mismatches: list[AuthorizationMismatch] = []
        alternatives: list[str] = []
        limitations: list[str] = []

        if missing:
            mismatches.append(AuthorizationMismatch.INCOMPLETE_EVIDENCE)
            status = ClaimStatus.UNKNOWN
            limitations.append(
                "Missing or contradictory layers prevent a complete authorization comparison."
            )
        else:
            if intended is not configured:
                mismatches.append(AuthorizationMismatch.CONFIGURATION_DRIFT)
                alternatives.append(
                    "The deployed configuration may intentionally override the documented policy."
                )
            if configured is not observed:
                mismatches.append(AuthorizationMismatch.ENFORCEMENT_DRIFT)
                alternatives.extend(
                    [
                        "The observation may have used a stale or differently scoped session.",
                        "Caching, eventual consistency or a resource-state difference may explain the result.",
                    ]
                )
            if intended is not observed:
                mismatches.append(AuthorizationMismatch.BEHAVIORAL_DRIFT)
            if mismatches:
                status = ClaimStatus.HYPOTHESIS
            else:
                mismatches.append(AuthorizationMismatch.CONSISTENT_SAMPLE)
                status = ClaimStatus.OBSERVED
                limitations.append(
                    "Consistency for this sampled actor/resource/state does not prove universal enforcement."
                )

        evidence_ids = sorted({evidence for item in items for evidence in item.evidence_ids})
        counter_ids = sorted(
            {evidence for item in items for evidence in item.counter_evidence_ids}
        )
        signals = [
            ConfidenceSignal(
                signal=f"{item.layer.lower()}:{item.decision.lower()}",
                contribution=0.18 if item.layer is AuthorizationLayer.OBSERVED else 0.1,
                reason=f"{item.layer} authorization decision is available",
                source_id=item.source,
                source_group=item.source_group,
                evidence_ids=item.evidence_ids,
                observed_at=item.observed_at,
                direct_observation=item.layer is AuthorizationLayer.OBSERVED,
                source_quality=0.9 if item.layer is AuthorizationLayer.OBSERVED else 0.7,
                specificity=0.9,
                temporal_half_life_days=30 if item.layer is AuthorizationLayer.OBSERVED else 180,
            )
            for item in items
            if item.evidence_ids or item.layer is not AuthorizationLayer.OBSERVED
        ]
        required = evidence_ids if observed is not Decision.UNKNOWN else ["observed-runtime-evidence"]
        breakdown = score_confidence(
            signals,
            base_confidence=0.05,
            required_evidence=required,
            maximum=0.79,
        )
        review = skeptic_review(
            breakdown,
            alternative_explanations=alternatives,
            counter_evidence_ids=counter_ids,
            missing_required_evidence=[layer.value for layer in missing],
        )
        if status is ClaimStatus.UNKNOWN:
            confidence = min(review.adjusted_confidence, 0.49)
        elif status is ClaimStatus.HYPOTHESIS:
            confidence = min(review.adjusted_confidence, 0.79)
        else:
            confidence = min(review.adjusted_confidence, 0.69)

        results.append(
            AuthorizationLayerComparison(
                comparison_id=f"AUTH-LAYER-{index + 1:04d}",
                actor_id=actor_id,
                tenant_id=tenant_id,
                resource_id=resource_id,
                operation=operation,
                resource_state=resource_state,
                actor_state=actor_state,
                intended=intended,
                configured=configured,
                observed=observed,
                status=status,
                mismatches=mismatches,
                observation_ids=sorted(item.observation_id for item in items),
                evidence_ids=evidence_ids,
                counter_evidence_ids=counter_ids,
                missing_layers=missing,
                confidence=round(confidence, 6),
                skeptic_verdict=review.verdict.value,
                alternative_explanations=alternatives,
                limitations=limitations,
            )
        )
    return results
