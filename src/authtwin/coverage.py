from __future__ import annotations

from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus


class ResourceSensitivity(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class ValidationCost(StrEnum):
    PASSIVE = "PASSIVE"
    READ_ONLY_SAFE = "READ_ONLY_SAFE"
    READ_ONLY_SENSITIVE = "READ_ONLY_SENSITIVE"
    MUTATING_REVERSIBLE = "MUTATING_REVERSIBLE"
    MUTATING_DESTRUCTIVE = "MUTATING_DESTRUCTIVE"
    PROHIBITED = "PROHIBITED"


class UnknownAuthorizationCell(BaseModel):
    """An unobserved matrix cell to prioritize for research, never a finding."""

    model_config = ConfigDict(extra="forbid")

    cell_id: str
    actor_id: str
    tenant_id: str | None = None
    resource_id: str
    operation: str
    resource_sensitivity: ResourceSensitivity = ResourceSensitivity.UNKNOWN
    crosses_tenant_boundary: bool = False
    crosses_privilege_boundary: bool = False
    coverage_gap_count: int = Field(default=1, ge=1)
    adjacent_observed_denies: int = Field(default=0, ge=0)
    adjacent_observed_allows: int = Field(default=0, ge=0)
    validation_cost: ValidationCost = ValidationCost.READ_ONLY_SENSITIVE
    evidence_ids: list[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.UNKNOWN

    @model_validator(mode="after")
    def unknown_only(self) -> "UnknownAuthorizationCell":
        if self.status is not ClaimStatus.UNKNOWN:
            raise ValueError("coverage-priority cells must remain UNKNOWN")
        return self


class CoveragePriority(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cell_id: str
    research_priority: int = Field(ge=0, le=100)
    safe_to_validate: bool
    recommended_action_class: ValidationCost
    reasons: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.UNKNOWN
    finding_created: bool = False


_SENSITIVITY_WEIGHT = {
    ResourceSensitivity.PUBLIC: 0,
    ResourceSensitivity.INTERNAL: 10,
    ResourceSensitivity.CONFIDENTIAL: 20,
    ResourceSensitivity.RESTRICTED: 30,
    ResourceSensitivity.UNKNOWN: 5,
}

_OPERATION_WEIGHT = {
    "READ": 8,
    "LIST": 5,
    "CREATE": 12,
    "UPDATE": 15,
    "PATCH": 15,
    "DELETE": 20,
    "TRANSFER": 25,
    "SHARE": 18,
    "ADMIN": 25,
}

_COST_PENALTY = {
    ValidationCost.PASSIVE: 0,
    ValidationCost.READ_ONLY_SAFE: 0,
    ValidationCost.READ_ONLY_SENSITIVE: 5,
    ValidationCost.MUTATING_REVERSIBLE: 20,
    ValidationCost.MUTATING_DESTRUCTIVE: 60,
    ValidationCost.PROHIBITED: 100,
}


def prioritize_unknown_cells(
    cells: Sequence[UnknownAuthorizationCell],
) -> list[CoveragePriority]:
    """Rank research coverage gaps without treating them as risk or findings."""

    output: list[CoveragePriority] = []
    for cell in cells:
        reasons: list[str] = []
        score = _SENSITIVITY_WEIGHT[cell.resource_sensitivity]
        if cell.resource_sensitivity in {
            ResourceSensitivity.CONFIDENTIAL,
            ResourceSensitivity.RESTRICTED,
        }:
            reasons.append("Sensitive resource coverage is incomplete.")

        operation_weight = _OPERATION_WEIGHT.get(cell.operation.upper(), 6)
        score += operation_weight
        reasons.append(f"Operation coverage weight: {operation_weight}.")

        if cell.crosses_tenant_boundary:
            score += 20
            reasons.append("The unobserved cell crosses a tenant boundary.")
        if cell.crosses_privilege_boundary:
            score += 15
            reasons.append("The unobserved cell crosses a privilege boundary.")

        score += min(15, cell.coverage_gap_count * 3)
        if cell.adjacent_observed_denies and cell.adjacent_observed_allows:
            score += 8
            reasons.append("Adjacent observed decisions differ and deserve controlled comparison.")

        score -= _COST_PENALTY[cell.validation_cost]
        safe = cell.validation_cost in {
            ValidationCost.PASSIVE,
            ValidationCost.READ_ONLY_SAFE,
            ValidationCost.READ_ONLY_SENSITIVE,
        }
        if not safe:
            reasons.append("Active validation requires stronger policy gates or is prohibited.")

        output.append(
            CoveragePriority(
                cell_id=cell.cell_id,
                research_priority=max(0, min(100, score)),
                safe_to_validate=safe,
                recommended_action_class=cell.validation_cost,
                reasons=reasons,
                limitations=[
                    "Research priority measures coverage value, not vulnerability likelihood, severity or exploitability.",
                    "The matrix cell remains UNKNOWN until evidence-bearing observation and safe validation occur.",
                ],
            )
        )
    return sorted(output, key=lambda item: (-item.research_priority, item.cell_id))
