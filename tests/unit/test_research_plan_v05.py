from __future__ import annotations

from authtwin.coverage import (
    ResourceSensitivity,
    UnknownAuthorizationCell,
    ValidationCost,
)
from authtwin.research import build_validation_plan
from sric.models import ClaimStatus


def _cell(cell_id: str, resource_id: str) -> UnknownAuthorizationCell:
    return UnknownAuthorizationCell(
        cell_id=cell_id,
        actor_id="actor-a",
        tenant_id="tenant-a",
        resource_id=resource_id,
        operation="READ",
        resource_sensitivity=ResourceSensitivity.CONFIDENTIAL,
        crosses_tenant_boundary=True,
        validation_cost=ValidationCost.READ_ONLY_SAFE,
    )


def test_equivalent_unknown_cells_are_compressed() -> None:
    plans = build_validation_plan([_cell("c1", "r1"), _cell("c2", "r2")])
    assert len(plans) == 1
    assert plans[0].covered_cell_ids == ["c1", "c2"]
    assert plans[0].status is ClaimStatus.UNKNOWN
    assert plans[0].finding_created is False


def test_unsafe_cells_are_excluded_by_default() -> None:
    cell = UnknownAuthorizationCell(
        cell_id="c3",
        actor_id="actor-a",
        resource_id="r3",
        operation="DELETE",
        validation_cost=ValidationCost.MUTATING_DESTRUCTIVE,
    )
    assert build_validation_plan([cell]) == []
