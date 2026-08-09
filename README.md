# AuthTwin

```text
AuthTwin :: v0.5.7
Developer: IsdarlinM

Model authorization behavior, invariants, and differential evidence.
```

Authorization Digital Twin for modeling **who can do what, to which resource, in which state**, while preserving `UNKNOWN` instead of inventing findings.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

AuthTwin is independently installable and independently useful. It requires SRIC Core 0.5.x for shared evidence/workspace/policy primitives, but no other Sentinel Forge product is required. ReproSec interoperability is optional through the `rcap` extra; its absence never prevents AuthTwin from starting, modeling authorization, using CLI/Web/API or generating reports.

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
- zero-config official update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC version/module compatibility checks in `doctor` and `/api/v1/runtime-compatibility`;
- full Web Feature Workbench with every public AuthTwin CLI command and argument represented as structured responsive controls;
- degraded Web mode that preserves the authorization dashboard and reports an actionable 503 if a shared Workbench module is unavailable;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Authorization evidence layers

AuthTwin separates `INTENDED`, `CONFIGURED` and `OBSERVED`. A mismatch is not automatically an authorization bypass. Missing or contradictory evidence remains `UNKNOWN`; deterministic evidence is required before validation.

## Standalone install and repair

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

The installer resolves SRIC automatically. `SRIC_CORE_SOURCE` exists only as an explicit development/release-validation override. Installers are repair-capable: they force-reinstall the pinned first-party runtime and AuthTwin, run `pip check`, verify `sric.web_console` and `sric.web_workbench`, and execute doctor/capability/help smokes without deleting workspaces or evidence.

For optional RCAP interoperability in a package environment:

```bash
python -m pip install 'authtwin[rcap]'
```

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `AuthTwin :: v0.5.7`, `Developer: IsdarlinM`, then the authorization-modeling purpose statement. Use `authtwin --no-color COMMAND`, `authtwin COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean.

The help contract covers `authtwin --help`, `authtwin -h`, `authtwin help`, `authtwin COMMAND --help`, `authtwin COMMAND -h` and `authtwin COMMAND help`.

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

AuthTwin's native dashboard remains the authorization-focused quick view for matrix, coverage, counterfactual plans, evidence detail, search and jobs. `/workbench` provides **All Features**: every public `authtwin.cli_all` command and every CLI parameter as a structured responsive Web form. `/console` remains the advanced argv-oriented console, and `/api/v1/runtime-compatibility` exposes the shared-runtime diagnostic.

Shared Web modules are loaded lazily. A stale/corrupt SRIC therefore no longer turns an optional UI import into a global CLI failure; the native application remains reachable and the missing Workbench reports `RUNTIME_INCOMPATIBLE` with repair instructions. The Workbench remains generated from the installed CLI tree and the release gate fails if a command or parameter disappears from Web representation.

Execution is not an operating-system shell: the fixed SRIC runner uses `shell=False`, disabled stdin, CSRF protection, redaction, bounded/cancellable jobs and SSE output. AuthTwin evidence semantics and human-controlled validation remain authoritative; a Web invocation cannot turn an unobserved gap into `VALIDATED`.

## Updates

```bash
authtwin update --check
authtwin update
authtwin update --force
```

Before an official product update, AuthTwin checks the SRIC version and required shared modules. Supported stale 0.5.x cores are advanced through immutable GitHub-signature-verified historical snapshots to the compatible floor; a compatible-version core missing required modules is force-reinstalled through the official channel. Custom/private `--manifest` plus `--public-key` updates remain explicit and do not silently replace their core channel.

Official updates accept only fixed Sentinel Forge repositories, validate immutable signed commits and source metadata, back up state, install without a shell and verify the installed distribution. `--force` may reinstall the current official release or move forward, never downgrade. No blind `git pull` fallback is used.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.7 runtime/interface suite reproduces stale/missing Workbench states, validates signed transitions and same-version repair, verifies degraded Web behavior, walks every public AuthTwin command with all supported help forms and compares every ordered CLI parameter with the Workbench schema. Existing unit/integration/E2E/security suites continue to cover actors, roles, tenants, authorization matrix, invariants, differential behavior, lifecycle, GraphQL/batch/WebSocket surfaces and `UNKNOWN`/evidence semantics. Destructive operations are gate-tested rather than executed solely for coverage.

Standalone and full release evidence are written below `build/release-evidence/`. A release is complete only when evidence for the exact commit is PASS.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.authtwin/` are preserved.

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are OFF by default. Apache-2.0.
