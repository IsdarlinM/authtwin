# Test Evidence — AuthTwin v0.3.1

## QA pass — 2026-08-07

Freshly executed in the current local runtime:

- Sentinel Forge cross-product high-risk regression matrix including AuthTwin GraphQL field comparison and subscription-revocation controls: **7/7 matrix tests passed**;
- Python `compileall` over the reconstructed corrected modules: **PASS**;
- branch comparison against `main`: branch is ahead and **0 commits behind** at the time of this audit.

Current-source review and new regression coverage include:

- `INTENDED` / `CONFIGURED` / `OBSERVED` separation;
- field-level GraphQL comparison without automatic bypass findings;
- pre-revocation payload control requirements;
- conflicting revocation timestamps remaining `UNKNOWN`;
- timezone-aware observation validation;
- policy-import and coverage APIs through the final workspace-bound vNext app;
- complete CLI entrypoint registration for GraphQL/subscription commands;
- recursive help-path coverage and controlled CLI validation errors;
- `authtwin web` serving the same vNext API used by integration tests;
- Web root/CSP smoke and public Python exports for surface analysis.

## Current release-gate status

**FULL CURRENT REPOSITORY GATE NOT EXECUTABLE IN THIS RUNTIME.**

The private repository cannot be materialized as a complete local checkout from the connector, and Ruff, mypy, `build` and `pip-audit` are unavailable from the runtime/index. No GitHub Actions, Codespaces or paid/hosted GitHub execution was used.

Before treating v0.3.1 as a fully validated release, run the exact commit from a local sibling checkout:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

## Previous validated baseline

The previous v0.3.0 state was recorded on 2026-07-22 with **21 pytest tests passed**, compileall/security scan/CLI help/synthetic smoke/build/isolated wheel smoke PASS. Those results are a historical baseline only.
