# AuthTwin

```text
AuthTwin :: v0.5.2
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

Interactive terminals display a compact subdued-green banner ordered as `AuthTwin :: v0.5.2`, `Developer: IsdarlinM`, then the authorization-modeling purpose statement. Use `authtwin --no-color COMMAND`, `authtwin COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean. See `docs/cli-presentation.md`.

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

AuthTwin's local Web UI exposes the authorization matrix, coverage, counterfactual plans, evidence detail, search and real-time job state. It is a structured application UI, **not an operating-system web shell**.

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
