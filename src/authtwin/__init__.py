"""AuthTwin authorization digital twin."""

from .coverage import CoveragePriority, ResourceSensitivity, UnknownAuthorizationCell, ValidationCost, prioritize_unknown_cells
from .layers import AuthorizationLayer, AuthorizationLayerComparison, AuthorizationMismatch, LayerObservation, compare_authorization_layers
from .policy_adapters import NormalizedPolicyRule, PolicyEffect, PolicyImportReport, PolicyProvider, normalize_policy_export
from .research import AuthorizationValidationPlan, build_validation_plan
from .surfaces import AccessDecision, GraphQLFieldComparison, GraphQLFieldObservation, SubscriptionEventObservation, SubscriptionRevocationAssessment, assess_subscription_revocation, compare_graphql_fields

__all__ = [
    "AccessDecision", "AuthorizationLayer", "AuthorizationLayerComparison", "AuthorizationMismatch",
    "AuthorizationValidationPlan", "CoveragePriority", "GraphQLFieldComparison", "GraphQLFieldObservation",
    "LayerObservation", "NormalizedPolicyRule", "PolicyEffect", "PolicyImportReport", "PolicyProvider",
    "ResourceSensitivity", "SubscriptionEventObservation", "SubscriptionRevocationAssessment",
    "UnknownAuthorizationCell", "ValidationCost", "assess_subscription_revocation", "build_validation_plan",
    "compare_authorization_layers", "compare_graphql_fields", "normalize_policy_export", "prioritize_unknown_cells",
]
__version__ = "0.5.7"
