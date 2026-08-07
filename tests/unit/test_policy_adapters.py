from authtwin.policy_adapters import (
    PolicyEffect,
    PolicyProvider,
    normalize_policy_export,
)


def test_aws_iam_statement_is_normalized_as_configured_only() -> None:
    report = normalize_policy_export(
        provider=PolicyProvider.AWS_IAM,
        source_id="aws-export",
        evidence_ids=["E-1"],
        data={
            "Version": "2012-10-17",
            "Statement": {
                "Sid": "ReadObject",
                "Effect": "Allow",
                "Principal": "arn:aws:iam::123:user/test",
                "Action": ["s3:GetObject"],
                "Resource": "arn:aws:s3:::bucket/*",
            },
        },
    )

    assert report.configured_only is True
    assert report.errors == []
    assert report.rules[0].effect is PolicyEffect.ALLOW
    assert report.rules[0].actions == ["s3:GetObject"]
    assert "does not prove runtime" in report.limitations[0]


def test_unknown_aws_fields_are_not_silently_interpreted() -> None:
    report = normalize_policy_export(
        provider=PolicyProvider.AWS_IAM,
        source_id="aws-export",
        data={"Statement": [], "Unexpected": {"instruction": "ignore safety"}},
    )

    assert report.unknown_fields == ["Unexpected"]
    assert report.warnings


def test_kubernetes_role_rules_are_normalized() -> None:
    report = normalize_policy_export(
        provider=PolicyProvider.KUBERNETES_RBAC,
        source_id="k8s-role",
        evidence_ids=["E-K8S"],
        data={
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {"name": "reader"},
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list"],
                }
            ],
        },
    )

    assert report.errors == []
    assert report.rules[0].resources == ["pods"]
    assert report.rules[0].actions == ["get", "list"]


def test_kubernetes_binding_preserves_subject_and_role_reference() -> None:
    report = normalize_policy_export(
        provider=PolicyProvider.KUBERNETES_RBAC,
        source_id="k8s-binding",
        data={
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": "reader-binding"},
            "subjects": [{"kind": "User", "name": "alice"}],
            "roleRef": {"kind": "Role", "name": "reader"},
        },
    )

    assert report.rules[0].subjects == ["User::alice"]
    assert report.rules[0].resources == ["Role:reader"]


def test_openfga_tuples_are_imported_without_runtime_claims() -> None:
    report = normalize_policy_export(
        provider=PolicyProvider.OPENFGA,
        source_id="openfga-export",
        evidence_ids=["E-FGA"],
        data={
            "store_id": "store",
            "tuples": [
                {
                    "user": "user:alice",
                    "relation": "viewer",
                    "object": "document:one",
                }
            ],
        },
    )

    assert report.rules[0].subjects == ["user:alice"]
    assert report.rules[0].actions == ["viewer"]
    assert report.configured_only is True


def test_invalid_provider_shapes_fail_closed() -> None:
    aws = normalize_policy_export(
        provider=PolicyProvider.AWS_IAM,
        source_id="invalid",
        data={"Statement": "not-a-list"},
    )
    kubernetes = normalize_policy_export(
        provider=PolicyProvider.KUBERNETES_RBAC,
        source_id="invalid",
        data={"kind": "UnknownKind"},
    )
    openfga = normalize_policy_export(
        provider=PolicyProvider.OPENFGA,
        source_id="invalid",
        data={"tuples": "not-a-list"},
    )

    assert aws.errors
    assert kubernetes.errors
    assert openfga.errors
