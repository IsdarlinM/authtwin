from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field
from sric.cases import claim_fingerprint
from sric.models import ClaimStatus

from .coverage import CoveragePriority, UnknownAuthorizationCell, prioritize_unknown_cells


class AuthorizationValidationPlan(BaseModel):
    """A minimal representative experiment for one equivalence class of UNKNOWN cells."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str
    representative_cell_id: str
    covered_cell_ids: list[str]
    research_priority: int = Field(ge=0, le=100)
    safe_to_validate: bool
    action_class: str
    claim_fingerprint: str
    reasons: list[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.UNKNOWN
    finding_created: bool = False


def _equivalence_key(cell: UnknownAuthorizationCell) -> tuple[object, ...]:
    resource_equivalence = cell.equivalence_class or f"resource:{cell.resource_id}"
    return (
        cell.tenant_id,
        resource_equivalence,
        cell.resource_sensitivity,
        cell.operation.upper(),
        cell.crosses_tenant_boundary,
        cell.crosses_privilege_boundary,
        cell.validation_cost,
    )


def build_validation_plan(
    cells: Sequence[UnknownAuthorizationCell],
    *,
    max_experiments: int = 25,
    safe_only: bool = True,
) -> list[AuthorizationValidationPlan]:
    """Compress authorization coverage gaps into representative safe experiments.

    Cells are compressed across different resources only when the caller supplies an explicit
    `equivalence_class`. Without that evidence, resource IDs are treated independently. The
    planner never changes an UNKNOWN cell into a finding and never treats research priority as
    exploitability.
    """

    if max_experiments < 1:
        raise ValueError("max_experiments must be at least 1")

    priorities = {item.cell_id: item for item in prioritize_unknown_cells(cells)}
    grouped: dict[tuple[object, ...], list[UnknownAuthorizationCell]] = defaultdict(list)
    for cell in cells:
        priority = priorities[cell.cell_id]
        if safe_only and not priority.safe_to_validate:
            continue
        grouped[_equivalence_key(cell)].append(cell)

    ranked_groups: list[tuple[CoveragePriority, list[UnknownAuthorizationCell]]] = []
    for group in grouped.values():
        representative = sorted(
            group,
            key=lambda cell: (-priorities[cell.cell_id].research_priority, cell.cell_id),
        )[0]
        ranked_groups.append((priorities[representative.cell_id], group))

    ranked_groups.sort(key=lambda item: (-item[0].research_priority, item[0].cell_id))
    output: list[AuthorizationValidationPlan] = []
    for index, (priority, group) in enumerate(ranked_groups[:max_experiments], start=1):
        representative = next(cell for cell in group if cell.cell_id == priority.cell_id)
        fingerprint = claim_fingerprint(
            claim_type="authorization-coverage-gap",
            subject=representative.actor_id,
            predicate=representative.operation,
            object_value=representative.equivalence_class or representative.resource_id,
            context={
                "tenant_id": representative.tenant_id,
                "crosses_tenant_boundary": representative.crosses_tenant_boundary,
                "crosses_privilege_boundary": representative.crosses_privilege_boundary,
                "resource_sensitivity": representative.resource_sensitivity.value,
            },
        )
        output.append(
            AuthorizationValidationPlan(
                plan_id=f"ATP-{index:04d}",
                representative_cell_id=representative.cell_id,
                covered_cell_ids=sorted(cell.cell_id for cell in group),
                research_priority=priority.research_priority,
                safe_to_validate=priority.safe_to_validate,
                action_class=priority.recommended_action_class.value,
                claim_fingerprint=fingerprint,
                reasons=[
                    *priority.reasons,
                    f"Representative covers {len(group)} explicitly equivalent UNKNOWN matrix cell(s).",
                    "The plan is a research-coverage optimization, not a vulnerability claim.",
                ],
            )
        )
    return output
