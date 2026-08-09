# AuthTwin

```text
AuthTwin :: v0.5.5
Developer: IsdarlinM

Model authorization behavior, invariants, and differential evidence.
```

Authorization Digital Twin for modeling **who can do what, to which resource, in which state**, while preserving `UNKNOWN` instead of inventing findings.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

AuthTwin is independently installable and independently useful. It requires SRIC Core 0.5.x for shared evidence/workspace/policy primitives, but no other Sentinel Forge product is required.

ReproSec interoperability is optional through the `rcap` extra. Its absence must never prevent AuthTwin from starting, modeling authorization, using the CLI, serving the Web UI or generating reports.

```bash
authtwin doctor --json
authtwin capabilities
```

## Implemented

- actors, roles, tenants, suspension state and resources/ownership/sharing;
- observed authorization decisions with evidence references and timestamps;
- Authorization Matrix with unobserved cells represented as `UNKNOWN`;
- configurable authorization invariants and candidate-finding generation;
- differential actor comparison and Skeptic-style alternative explanations;
- explicit validation gate: a finding cannot become `VALIDATED` without deterministic evidence;
- optional RCAP interoperability through ReproSec;
- measurable coverage, safe counterfactual plans and state/session lifecycle modeling;
- strict invariant DSL, GraphQL/batch analysis and WebSocket lifecycle modeling;
- coverage-guided validation planning with explicit equivalence classes;
- endpoint/resource-family normalization and conservative actor-resource bindings;
- SRIC 0.5.x graph, jobs/SSE, lineage, notebook/search and confidence primitives;
- local FastAPI API, responsive Web UI and offline synthetic demo;
- zero-config official update flow with safe same-version `update --force` reinstall support;
- Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Authorization evidence layers

AuthTwin separates `INTENDED`, `CONFIGURED` and `OBSERVED`. A mismatch is not automatically an authorization bypass. Missing or contradictory evidence remains `UNKNOWN`; deterministic evidence is required before validation.

## Standalone install

Linux:

```bash
./scripts/install-linux.sh
authtwin doctor --json
authtwin capabilities
```

Windows:

```cmd
scripts\install-windows.cmd
authtwin doctor --json
authtwin capabilities
```

The installer resolves SRIC automatically. `SRIC_CORE_SOURCE` exists only as an explicit development/release-validation override.

For optional RCAP interoperability in a package environment:

```bash
python -m pip install 'authtwin[rcap]'
```

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `AuthTwin :: v0.5.5`, `Developer: IsdarlinM`, then the authorization-modeling purpose statement. Use `authtwin --no-color COMMAND`, `authtwin COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean. See `docs/cli-presentation.md`.

## Five-minute start

```bash
authtwin doctor --json
authtwin capabilities
authtwin demo --workspace demo
authtwin matrix demo
authtwin findings demo
authtwin web demo
```

## Web and API

AuthTwin's local Web UI exposes the authorization matrix, coverage, counterfactual plans, evidence detail, search and real-time job state. `/console` adds the Web Command Console, whose catalog is generated from `authtwin.cli_all`; a standalone test requires the Web and CLI command-path sets to be exactly equal.

The console is **not an operating-system web shell**. It invokes only the fixed SRIC runner with `shell=False`, disabled stdin and a structured argv array. Mutating commands require explicit approval, while AuthTwin's evidence and validation semantics remain authoritative. See `docs/web/cli-parity.md`.

## Updates

The official update path is zero-config:

```bash
authtwin update --check
authtwin update
authtwin update --force
```

Normal users do **not** provide a manifest or public key. SRIC resolves only the fixed official `IsdarlinM/authtwin` channel, requires the selected immutable release commit to be reported by GitHub as signature-verified, validates the exact source snapshot and package metadata, backs up state, installs without a shell, and verifies the installed distribution version.

`--force` reinstalls the official release even when that exact version is already installed. It may install a newer official release but never downgrades; `--check` and `--force` cannot be combined. Normal upgrades require rollback metadata; same-version forced reinstalls use the verified target snapshot as the recovery package.

`--manifest` and `--public-key` remain available together only as an advanced custom/private-channel override. Custom channels retain Ed25519 manifest and SHA-256 wheel verification. No blind `git pull` fallback is used. See `docs/release/update.md`.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

Standalone and full release evidence are written below `build/release-evidence/`. A release is complete only when evidence for the exact commit is PASS.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.authtwin/` are preserved.

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are OFF by default. Apache-2.0.
