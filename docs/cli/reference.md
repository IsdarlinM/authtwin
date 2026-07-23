# CLI Reference — authtwin

Generated from the registered runtime command tree. Every public command below supports `--help` and `-h`; top-level `COMMAND help` is normalized to the same help path.

## Commands

- `authtwin actor`
- `authtwin ai` — Show AI mode. Cloud AI remains disabled until explicitly configured.
- `authtwin batch` — Analyze supplied batch-operation item decisions; no requests are generated.
- `authtwin bindings` — Infer candidate actor-resource relationships with evidence and explicit INFERRED state.
- `authtwin compare`
- `authtwin config` — Inspect configuration and explain where a value comes from.
- `authtwin counterfactual` — Generate safe counterfactual test plans; never executes them automatically.
- `authtwin coverage` — Measure observed authorization matrix coverage; UNKNOWN cells are not findings.
- `authtwin demo`
- `authtwin differential` — Compare response semantics/metadata rather than relying only on HTTP status.
- `authtwin discover` — Summarize deterministic resource/operation candidates from supplied observations.
- `authtwin discover-v2` — Normalize endpoint/resource families without proving ownership.
- `authtwin doctor` — Check runtime, SRIC integration, plugin registry and secure defaults.
- `authtwin evidence` — Store a local evidence artifact in SRIC content-addressed storage.
- `authtwin evidence-lineage` — Explain evidence lineage and the reason a derived artifact is visible.
- `authtwin export`
- `authtwin findings`
- `authtwin graphql` — Show authorization observations grouped by GraphQL operation/field metadata.
- `authtwin help`
- `authtwin import`
- `authtwin init`
- `authtwin invariant`
- `authtwin invariant-dsl` — Parse and install a small auditable authorization-invariant DSL.
- `authtwin invariant-library` — Install reusable ownership/tenant/revocation/suspension/transfer/invitation invariants.
- `authtwin jobs` — List/inspect/cancel persistent SRIC jobs for this workspace.
- `authtwin matrix`
- `authtwin membership` — Record an observed invitation/membership lifecycle event.
- `authtwin model`
- `authtwin mutation-plan` — Generate minimal differential plans; execution still requires Scope/Policy/RateLimit/Approval/ReproSec.
- `authtwin notebook` — List/append research notes or manage saved investigation queries.
- `authtwin observe`
- `authtwin plugins` — List SRIC plugin manifests without auto-executing plugin code.
- `authtwin query` — Search this workspace's shared SRIC graph.
- `authtwin report`
- `authtwin resource`
- `authtwin scope` — Evaluate a target using SRIC Scope Engine; no request is sent.
- `authtwin session` — Append or inspect identity/session lifecycle events without storing raw session secrets.
- `authtwin skeptic` — Generate alternative explanations, missing evidence and counter-tests for a candidate.
- `authtwin state-machine` — Show observed resource-state transitions; missing history remains UNKNOWN.
- `authtwin state-v2` — Show actor/resource/membership authorization lifecycle state.
- `authtwin update` — Check/install a signed wheel release. Never performs a blind git pull.
- `authtwin validate`
- `authtwin version`
- `authtwin web`
- `authtwin websocket` — Inspect observed WebSocket subscription authorization/revocation lifecycle.
- `authtwin workspace` — Manage isolated investigation workspaces.

## Help contract

```text
authtwin --help
authtwin -h
authtwin help
authtwin COMMAND --help
authtwin COMMAND -h
authtwin COMMAND help
```

Use command-specific help for authoritative arguments, options and defaults.
