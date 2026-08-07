from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Iterable

from pydantic import BaseModel, ConfigDict, Field


class PolicyProvider(StrEnum):
    AWS_IAM = "AWS_IAM"
    KUBERNETES_RBAC = "KUBERNETES_RBAC"
    OPENFGA = "OPENFGA"
    GENERIC = "GENERIC"


class PolicyEffect(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    UNKNOWN = "UNKNOWN"


class NormalizedPolicyRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    provider: PolicyProvider
    effect: PolicyEffect
    subjects: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    conditions: dict[str, Any] = Field(default_factory=dict)
    source_path: str
    evidence_ids: list[str] = Field(default_factory=list)


class PolicyImportReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: PolicyProvider
    source_id: str
    content_sha256: str
    configured_only: bool = True
    rules: list[NormalizedPolicyRule] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    unknown_fields: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _hash(data: dict[str, Any]) -> str:
    encoded = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _policy_effect(value: Any) -> PolicyEffect:
    try:
        return PolicyEffect(str(value).upper())
    except ValueError:
        return PolicyEffect.UNKNOWN


def _aws_rules(
    data: dict[str, Any], evidence_ids: list[str]
) -> tuple[list[NormalizedPolicyRule], list[str], list[str]]:
    allowed = {"Version", "Statement", "Id"}
    unknown = sorted(set(data) - allowed)
    errors: list[str] = []
    statements = data.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list):
        return [], unknown, ["AWS IAM Statement must be an object or list"]

    rules: list[NormalizedPolicyRule] = []
    for index, raw in enumerate(statements):
        if not isinstance(raw, dict):
            errors.append(f"Statement[{index}] is not an object")
            continue
        condition = raw.get("Condition", {})
        if not isinstance(condition, dict):
            condition = {}
        rules.append(
            NormalizedPolicyRule(
                rule_id=str(raw.get("Sid") or f"AWS-{index:04d}"),
                provider=PolicyProvider.AWS_IAM,
                effect=_policy_effect(raw.get("Effect", "UNKNOWN")),
                subjects=_list(raw.get("Principal") or raw.get("NotPrincipal")),
                actions=_list(raw.get("Action") or raw.get("NotAction")),
                resources=_list(raw.get("Resource") or raw.get("NotResource")),
                conditions=condition,
                source_path=f"Statement[{index}]",
                evidence_ids=evidence_ids,
            )
        )
    return rules, unknown, errors


def _kubernetes_rules(
    data: dict[str, Any], evidence_ids: list[str]
) -> tuple[list[NormalizedPolicyRule], list[str], list[str]]:
    allowed = {"apiVersion", "kind", "metadata", "rules", "subjects", "roleRef"}
    unknown = sorted(set(data) - allowed)
    errors: list[str] = []
    kind = str(data.get("kind", ""))
    supported = {"Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding"}
    if kind not in supported:
        errors.append("Unsupported Kubernetes RBAC kind")
        return [], unknown, errors

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    if kind in {"RoleBinding", "ClusterRoleBinding"}:
        raw_subjects = data.get("subjects", [])
        if not isinstance(raw_subjects, list):
            raw_subjects = []
            errors.append("Kubernetes subjects must be a list")
        subjects = [
            f"{item.get('kind', 'Unknown')}:{item.get('namespace', '')}:{item.get('name', '')}"
            for item in raw_subjects
            if isinstance(item, dict)
        ]
        role_ref = data.get("roleRef", {})
        if not isinstance(role_ref, dict):
            role_ref = {}
            errors.append("Kubernetes roleRef must be an object")
        return [
            NormalizedPolicyRule(
                rule_id=f"{kind}:{metadata.get('name', 'unnamed')}",
                provider=PolicyProvider.KUBERNETES_RBAC,
                effect=PolicyEffect.ALLOW,
                subjects=subjects,
                actions=["bind"],
                resources=[
                    f"{role_ref.get('kind', 'Role')}:{role_ref.get('name', '')}"
                ],
                source_path="roleRef",
                evidence_ids=evidence_ids,
            )
        ], unknown, errors

    rules: list[NormalizedPolicyRule] = []
    raw_rules = data.get("rules", [])
    if not isinstance(raw_rules, list):
        return [], unknown, ["Kubernetes rules must be a list"]
    for index, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            errors.append(f"rules[{index}] is not an object")
            continue
        resources = (
            _list(raw.get("resources"))
            + _list(raw.get("resourceNames"))
            + _list(raw.get("nonResourceURLs"))
        )
        rules.append(
            NormalizedPolicyRule(
                rule_id=f"{kind}-{index:04d}",
                provider=PolicyProvider.KUBERNETES_RBAC,
                effect=PolicyEffect.ALLOW,
                actions=_list(raw.get("verbs")),
                resources=resources,
                conditions={"apiGroups": _list(raw.get("apiGroups"))},
                source_path=f"rules[{index}]",
                evidence_ids=evidence_ids,
            )
        )
    return rules, unknown, errors


def _openfga_rules(
    data: dict[str, Any], evidence_ids: list[str]
) -> tuple[list[NormalizedPolicyRule], list[str], list[str]]:
    allowed = {"tuples", "authorization_model_id", "store_id"}
    unknown = sorted(set(data) - allowed)
    tuples = data.get("tuples", [])
    if not isinstance(tuples, list):
        return [], unknown, ["OpenFGA tuples must be a list"]

    rules: list[NormalizedPolicyRule] = []
    errors: list[str] = []
    for index, raw in enumerate(tuples):
        if not isinstance(raw, dict):
            errors.append(f"tuples[{index}] is not an object")
            continue
        user = str(raw.get("user", ""))
        relation = str(raw.get("relation", ""))
        object_id = str(raw.get("object", ""))
        if not all([user, relation, object_id]):
            errors.append(f"tuples[{index}] lacks user, relation or object")
            continue
        rules.append(
            NormalizedPolicyRule(
                rule_id=f"OPENFGA-{index:04d}",
                provider=PolicyProvider.OPENFGA,
                effect=PolicyEffect.ALLOW,
                subjects=[user],
                actions=[relation],
                resources=[object_id],
                source_path=f"tuples[{index}]",
                evidence_ids=evidence_ids,
            )
        )
    return rules, unknown, errors


def normalize_policy_export(
    *,
    provider: PolicyProvider,
    source_id: str,
    data: dict[str, Any],
    evidence_ids: Iterable[str] = (),
) -> PolicyImportReport:
    evidence = sorted(set(evidence_ids))
    if provider is PolicyProvider.AWS_IAM:
        rules, unknown, errors = _aws_rules(data, evidence)
    elif provider is PolicyProvider.KUBERNETES_RBAC:
        rules, unknown, errors = _kubernetes_rules(data, evidence)
    elif provider is PolicyProvider.OPENFGA:
        rules, unknown, errors = _openfga_rules(data, evidence)
    else:
        rules = []
        unknown = sorted(data)
        errors = ["Generic provider requires an explicit adapter"]

    warnings: list[str] = []
    if unknown:
        warnings.append(
            "Unknown top-level fields were preserved in the import report and not silently interpreted."
        )
    if not evidence:
        warnings.append("No evidence IDs were attached to the imported configuration.")
    return PolicyImportReport(
        provider=provider,
        source_id=source_id,
        content_sha256=_hash(data),
        rules=rules,
        warnings=warnings,
        errors=errors,
        unknown_fields=unknown,
        limitations=[
            "Imported policy describes configuration or intent; it does not prove runtime authorization enforcement.",
            "Unsupported semantics remain UNKNOWN and must not be converted into allow/deny observations.",
        ],
    )
