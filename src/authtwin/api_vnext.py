from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .api import create_app as create_base_app
from .coverage import UnknownAuthorizationCell
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


router = APIRouter(prefix="/api/v1/surfaces", tags=["authorization-surfaces"])
research_router = APIRouter(prefix="/api/v1/research", tags=["authorization-research"])


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
    return app
