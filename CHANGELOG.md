# Changelog

## 0.5.5 - 2026-08-08
- Made the official AuthTwin updater zero-config: `authtwin update`, `authtwin update --check`, and `authtwin update --force` no longer require user-supplied manifest/key configuration.
- Delegated official update trust and immutable GitHub signed-commit validation to SRIC Core 0.5.5 while preserving same-version force reinstall and downgrade rejection.
- Kept `--manifest` plus `--public-key` as an explicit advanced custom/private-channel override.
- Updated the SRIC Core floor/lock/pin and the optional ReproSec `rcap` compatibility range to 0.5.5.
- Added standalone regression coverage proving `authtwin update --force` selects the official channel with no manifest/key.

## 0.5.4 - 2026-08-08
- Added the SRIC Web Command Console at `/console`, exposing the complete installed `authtwin.cli_all` command tree without an operating-system shell.
- Added exact Web-catalog-to-CLI-tree regression coverage so future public CLI commands cannot silently disappear from the Web console.
- Preserved AuthTwin evidence semantics, authorization safety controls and human-controlled validation; missing evidence remains `UNKNOWN`.
- Added fixed-runner `shell=False` execution, explicit mutation approval, secret redaction, cancellable jobs and real-time SSE output through SRIC Core 0.5.4.
- Updated SRIC to 0.5.4 and the optional ReproSec `rcap` compatibility range to 0.5.4.

## 0.5.3 - 2026-08-08
- Added `authtwin update --force` for explicit same-version reinstall of a trusted signed release using pip `--force-reinstall`.
- Preserved Ed25519 manifest verification, SHA-256 wheel verification, state backup and rollback behavior.
- `--force` may install the same or a newer signed release, never an older release; SemVer prerelease precedence is enforced by SRIC Core.
- `--check` and `--force` are mutually exclusive.
- Updated the SRIC Core runtime floor, lock and exact first-party source pin to 0.5.3 while keeping ReproSec optional through the `rcap` extra.
- Added standalone regression coverage for the public `--force` CLI contract.

## 0.5.2 - 2026-08-08
- Added a subdued green interactive CLI banner ordered as `AuthTwin :: v0.5.2`, `Developer: IsdarlinM`, then the product description.
- Added colorized Typer/Rich command help plus global `--no-color` and `NO_COLOR` support.
- Kept banner output on interactive stderr so JSON, reports and automation stdout remain clean.
- Added CLI branding regression tests and documentation.
- Updated the SRIC Core runtime floor, lock and first-party source pin to 0.5.2 while preserving ReproSec as an optional `rcap` integration.

## 0.5.1 - 2026-08-08
- Fixed clean installation when `sric-core` is not published on PyPI.
- Added a first-party dependency manifest pinned to the exact SRIC Core 0.5.1 GitHub commit.
- Windows and Linux installers now bootstrap first-party dependencies before AuthTwin and its third-party runtime dependencies.
- Preserved ReproSec as an optional `rcap` extra and did not make sibling products mandatory.
- Updated the SRIC dependency floor/runtime lock to 0.5.1 and the optional ReproSec compatibility range to 0.5.1.
- Added standalone regression coverage for the installer dependency contract.

## 0.5.0 - 2026-08-08
- Added coverage-guided validation planning that compresses equivalent `UNKNOWN` authorization cells into representative experiments.
- Added deterministic cross-tool claim fingerprints for planned authorization coverage gaps.
- Added safe-only planning by default; destructive and other non-safe validation costs are excluded from automatic experiment selection.
- Preserved strict semantics: research priority is not exploitability, plans remain `UNKNOWN`, and no finding is created by the planner.
- Updated SRIC/ReproSec compatibility to the Sentinel Forge 0.5 release train.
- Made ReproSec an explicitly optional `rcap` integration rather than a standalone runtime requirement.
- Added capability discovery plus standalone CLI/API/Web contracts that operate with only AuthTwin and SRIC installed.
- Reworked Linux/Windows installation to resolve SRIC 0.5 automatically and removed silent sibling-checkout discovery.
- Added clean-install CI, optional-RCAP CI separation and data-preserving Linux uninstall behavior.
- Added regression tests for equivalence compression, safe validation selection and truth-state preservation.

## 0.3.1 - 2026-08-06
- Added explicit `INTENDED`, `CONFIGURED` and `OBSERVED` authorization evidence layers.
- Added conservative comparison of policy intent, deployed configuration and runtime enforcement.
- Configuration, enforcement and behavioral drift remain `HYPOTHESIS`; missing or contradictory layers remain `UNKNOWN`.
- Added tenant, resource state and actor state to comparison keys to prevent invalid cross-state comparisons.
- Added SRIC 0.4.1 confidence calibration and Skeptic review with alternative explanations and counter-evidence.
- Added tests for incomplete evidence, contradictory observations, tenant isolation, state separation and non-validation semantics.
- Replaced hosted GitHub Actions/Dependabot automation with a local reproducible release gate.

## 0.3.0 - 2026-07-22
- Added authorization discovery v2, endpoint/resource-family normalization and conservative actor-resource binding.
- Added actor/resource/membership state machine v2, safe mutation plans, differential response intelligence and reusable invariant library.
- Added WebSocket authorization lifecycle modeling and expanded GraphQL/differential workflows.
- Upgraded to shared SRIC 0.4 workspace namespaces and ReproSec 0.4 multi-actor evidence interoperability.

## 0.2.0 - 2026-07-21
- Added measurable authorization coverage, deterministic resource/operation discovery and safe counterfactual validation plans.
- Added observed state/session lifecycle modeling, strict Authorization Invariant DSL, GraphQL surface grouping and batch authorization analysis.
- Added Skeptic reviews with alternative explanations/missing evidence and retained `UNKNOWN` for unobserved matrix cells.
- Integrated SRIC 0.3 temporal graph, jobs, evidence lineage, notebook/query APIs and SSE job events.
- Added shared Evidence Store ingestion and RCAP import/export interoperability with ReproSec 0.3.

## 0.1.0 - 2026-07-21
- Initial evidence-native AuthTwin implementation.
- CLI, local API/UI, deterministic local storage, demo, tests, security controls and SRIC integration.
