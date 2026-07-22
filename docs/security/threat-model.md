# Threat model

Assets: evidence, workspaces, scopes, reports and imported data. Threats include poisoned imports, path traversal, prompt injection, secret leakage, cross-workspace leakage, unauthorized Web UI exposure and unsafe active validation. Mitigations include strict schemas, safe path handling, loopback-only Web UI by default, no shell execution, explicit scope/policy controls and redaction.
