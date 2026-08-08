# Changelog

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
