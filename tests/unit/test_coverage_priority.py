import pytest

from authtwin.coverage import (
    ResourceSensitivity,
    UnknownAuthorizationCell,
    ValidationCost,
    prioritize_unknown_cells,
)
from sric.models import ClaimStatus


def cell(
    cell_id: str,
    *,
    sensitivity: ResourceSensitivity = ResourceSensitivity.INTERNAL,
    operation: str = "READ",
    tenant: bool = False,
    privilege: bool = False,
    cost: ValidationCost = ValidationCost.READ_ONLY_SENSITIVE,
) -> UnknownAuthorizationCell:
    return UnknownAuthorizationCell(
        cell_id=cell_id,
        actor_id="actor",
        tenant_id="tenant-a",
        resource_id="resource",
        operation=operation,
        resource_sensitivity=sensitivity,
        crosses_tenant_boundary=tenant,
        crosses_privilege_boundary=privilege,
        validation_cost=cost,
    )


def test_priority_is_not_a_finding_or_risk_score() -> None:
    result = prioritize_unknown_cells([cell("C-1")])[0]

    assert result.status is ClaimStatus.UNKNOWN
    assert result.finding_created is False
    assert "not vulnerability likelihood" in result.limitations[0]


def test_sensitive_cross_tenant_gap_is_prioritized() -> None:
    ordinary = cell("ordinary")
    sensitive = cell(
        "sensitive",
        sensitivity=ResourceSensitivity.RESTRICTED,
        operation="TRANSFER",
        tenant=True,
        privilege=True,
    )

    results = prioritize_unknown_cells([ordinary, sensitive])

    assert results[0].cell_id == "sensitive"
    assert results[0].research_priority > results[1].research_priority


def test_destructive_validation_is_not_marked_safe() -> None:
    result = prioritize_unknown_cells(
        [cell("delete", operation="DELETE", cost=ValidationCost.MUTATING_DESTRUCTIVE)]
    )[0]

    assert result.safe_to_validate is False
    assert result.research_priority >= 0


def test_prohibited_action_has_zero_or_low_priority_and_never_safe() -> None:
    result = prioritize_unknown_cells(
        [
            cell(
                "prohibited",
                sensitivity=ResourceSensitivity.RESTRICTED,
                operation="ADMIN",
                tenant=True,
                privilege=True,
                cost=ValidationCost.PROHIBITED,
            )
        ]
    )[0]

    assert result.safe_to_validate is False
    assert result.research_priority == 0


def test_adjacent_decision_difference_increases_research_value() -> None:
    base = cell("base")
    contrasted = cell("contrast")
    contrasted.adjacent_observed_allows = 1
    contrasted.adjacent_observed_denies = 1

    results = {item.cell_id: item for item in prioritize_unknown_cells([base, contrasted])}

    assert results["contrast"].research_priority > results["base"].research_priority


def test_input_cell_cannot_claim_non_unknown_status() -> None:
    with pytest.raises(ValueError, match="must remain UNKNOWN"):
        UnknownAuthorizationCell(
            cell_id="invalid",
            actor_id="actor",
            resource_id="resource",
            operation="READ",
            status=ClaimStatus.HYPOTHESIS,
        )
