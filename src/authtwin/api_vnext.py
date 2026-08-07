from __future__ import annotations

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict

from .api import create_app as create_base_app
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


router = APIRouter(prefix="/api/v1/surfaces", tags=["authorization-surfaces"])


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


def create_app() -> FastAPI:
    app = create_base_app()
    app.include_router(router)
    return app
