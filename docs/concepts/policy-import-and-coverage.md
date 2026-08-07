# Policy imports and UNKNOWN coverage priority

AuthTwin imports policy exports as untrusted, configured-only evidence.

Supported initial adapters:

- AWS IAM policy documents;
- Kubernetes Role, ClusterRole, RoleBinding and ClusterRoleBinding objects;
- OpenFGA relationship tuples.

Unknown fields are reported and unsupported structures fail closed. Imported ALLOW/DENY rules describe intent or configuration; they never prove runtime enforcement and are not inserted as `OBSERVED` decisions.

## Coverage priority

`prioritize_unknown_cells` ranks unobserved matrix cells for research using resource sensitivity, operation type, tenant/privilege boundaries, coverage gaps, adjacent observed contrasts and validation cost.

The output is explicitly **research coverage priority**, not likelihood, severity or risk. Every item remains `UNKNOWN`, creates no finding and records whether the proposed validation class is safe, sensitive, mutating, destructive or prohibited.

CLI examples:

```bash
authtwin policy-import policy.json --provider aws_iam --source-id export-1 --evidence E-1
authtwin coverage-priority unknown-cells.json
authtwin layer-compare authorization-layers.json
```
