from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .api import create_app as create_base_app
from .coverage import UnknownAuthorizationCell
from .coverage import prioritize_unknown_cells
from .policy_adapters import PolicyProvider, normalize_policy_export
from .research import build_validation_plan
from .surfaces import (
    GraphQLFieldObservation,
    SubscriptionEventObservation,
    assess_subscription_revocation,
    compare_graphql_fields,
)


class GraphQLFieldRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observations: list[GraphQLFieldObservation]


class SubscriptionRevocationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observations: list[SubscriptionEventObservation]


class ValidationPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cells: list[UnknownAuthorizationCell]
    maximum_experiments: int = Field(default=25, ge=1, le=1000)
    safe_only: bool = True


class PolicyImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: PolicyProvider
    source_id: str
    data: dict[str, object]
    evidence_ids: list[str] = Field(default_factory=list)


class CoveragePriorityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cells: list[UnknownAuthorizationCell]


router = APIRouter(prefix="/api/v1/surfaces", tags=["authorization-surfaces"])
research_router = APIRouter(prefix="/api/v1/research", tags=["authorization-research"])
policy_router = APIRouter(prefix="/api/v1/policy", tags=["authorization-policy"])
coverage_router = APIRouter(prefix="/api/v1/coverage", tags=["authorization-coverage"])


@policy_router.post("/import")
async def policy_import(request: PolicyImportRequest) -> dict[str, object]:
    report = normalize_policy_export(
        provider=request.provider,
        source_id=request.source_id,
        data=request.data,
        evidence_ids=request.evidence_ids,
    )
    return report.model_dump(mode="json")


@coverage_router.post("/prioritize")
async def coverage_prioritize(request: CoveragePriorityRequest) -> dict[str, object]:
    priorities = prioritize_unknown_cells(request.cells)
    return {
        "priorities": [item.model_dump(mode="json") for item in priorities],
        "risk_score": None,
        "findings_created": 0,
    }


@router.post("/graphql-fields")
async def graphql_fields(request: GraphQLFieldRequest) -> dict[str, object]:
    reports = compare_graphql_fields(request.observations)
    return {
        "reports": [item.model_dump(mode="json") for item in reports],
        "validated_findings_created": 0,
    }


@router.post("/subscription-revocation")
async def subscription_revocation(
    request: SubscriptionRevocationRequest,
) -> dict[str, object]:
    reports = assess_subscription_revocation(request.observations)
    return {
        "reports": [item.model_dump(mode="json") for item in reports],
        "validated_findings_created": 0,
    }


@research_router.post("/validation-plan")
async def validation_plan(request: ValidationPlanRequest) -> dict[str, object]:
    plans = build_validation_plan(
        request.cells,
        max_experiments=request.maximum_experiments,
        safe_only=request.safe_only,
    )
    return {
        "plans": [item.model_dump(mode="json") for item in plans],
        "input_cell_count": len(request.cells),
        "planned_experiment_count": len(plans),
        "validated_findings_created": 0,
    }


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)
    app.include_router(router)
    app.include_router(research_router)
    app.include_router(policy_router)
    app.include_router(coverage_router)
    return app
