"""AuthTwin authorization digital twin."""

from .coverage import (
    CoveragePriority,
    ResourceSensitivity,
    UnknownAuthorizationCell,
    ValidationCost,
    prioritize_unknown_cells,
)
from .layers import (
    AuthorizationLayer,
    AuthorizationLayerComparison,
    AuthorizationMismatch,
    LayerObservation,
    compare_authorization_layers,
)
from .policy_adapters import (
    NormalizedPolicyRule,
    PolicyEffect,
    PolicyImportReport,
    PolicyProvider,
    normalize_policy_export,
)

__all__ = [
    "AuthorizationLayer",
    "AuthorizationLayerComparison",
    "AuthorizationMismatch",
    "CoveragePriority",
    "LayerObservation",
    "NormalizedPolicyRule",
    "PolicyEffect",
    "PolicyImportReport",
    "PolicyProvider",
    "ResourceSensitivity",
    "UnknownAuthorizationCell",
    "ValidationCost",
    "compare_authorization_layers",
    "normalize_policy_export",
    "prioritize_unknown_cells",
]
__version__ = "0.3.1"
