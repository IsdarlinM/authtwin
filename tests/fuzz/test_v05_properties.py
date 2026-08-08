from __future__ import annotations

from hypothesis import given, strategies as st
from sric.models import ClaimStatus

from authtwin.coverage import UnknownAuthorizationCell, ValidationCost
from authtwin.research import build_validation_plan


_ids = st.from_regex(r"[a-z][a-z0-9-]{0,15}", fullmatch=True)


@given(st.lists(_ids, min_size=1, max_size=20, unique=True))
def test_generated_safe_plans_never_create_findings(resource_ids: list[str]) -> None:
    cells = [
        UnknownAuthorizationCell(
            cell_id=f"cell-{index}",
            actor_id="actor-a",
            tenant_id="tenant-a",
            resource_id=resource_id,
            operation="READ",
            validation_cost=ValidationCost.READ_ONLY_SAFE,
        )
        for index, resource_id in enumerate(resource_ids)
    ]
    plans = build_validation_plan(cells, max_experiments=100)
    assert len(plans) == len(resource_ids)
    assert all(plan.status is ClaimStatus.UNKNOWN for plan in plans)
    assert all(plan.finding_created is False for plan in plans)
    assert all(plan.safe_to_validate for plan in plans)


@given(st.integers(min_value=1, max_value=20))
def test_explicit_equivalence_is_required_for_cross_resource_compression(count: int) -> None:
    cells = [
        UnknownAuthorizationCell(
            cell_id=f"cell-{index}",
            actor_id="actor-a",
            resource_id=f"resource-{index}",
            operation="READ",
            validation_cost=ValidationCost.READ_ONLY_SAFE,
            equivalence_class="documents",
        )
        for index in range(count)
    ]
    plans = build_validation_plan(cells, max_experiments=100)
    assert len(plans) == 1
    assert plans[0].covered_cell_ids == sorted(cell.cell_id for cell in cells)
