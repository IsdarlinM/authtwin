# AuthTwin

```text
AuthTwin :: v0.5.11
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
- JSON-safe shared Web command catalog generation from SRIC 0.5.11;
- shared-route CSP that permits same-origin Console/Workbench CSS/JS while retaining restrictive object/base/frame policies;
- degraded Web mode that preserves the authorization dashboard and reports an actionable 503 if a shared Workbench module is unavailable;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Authorization evidence layers

AuthTwin separates `INTENDED`, `CONFIGURED` and `OBSERVED`. A mismatch is not automatically an authorization bypass. Missing or contradictory evidence remains `UNKNOWN`; deterministic evidence is required before validation.

## Standalone install and repair

Linux / Termux:

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

The normal installer pins SRIC Core to an immutable GitHub commit and resolves that explicit first-party source **in the same pip transaction as AuthTwin**. Because `sric-core` is intentionally not discovered from PyPI, the installer does not perform a later product-only reinstall that could trigger `ResolutionImpossible`. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces and evidence. It validates both host Python and the existing runtime interpreter; a stale, incomplete or broken environment rebuilds only `~/.authtwin/venv`. It bootstraps `pip`, `setuptools` and `wheel`, resolves constrained AuthTwin plus the explicit SRIC source, runs `pip check`, imports `sric.web_console`, `sric.web_workbench` and `sric.web_catalog`, requires SRIC `>=0.5.11,<0.6`, and runs doctor/capability plus `--help`, `-h` and `help` smokes.

Installer-internal smokes use `SENTINEL_BANNER=never` and a temporary validation log. Successful installation no longer repeats the AuthTwin banner; failure output is retained and emitted when a check fails. Normal installation does not use `--force-reinstall`.

On Termux, a writable `$PREFIX/bin` already present in `PATH` is preferred so `authtwin` becomes immediately reachable. Standard Linux falls back to `~/.local/bin` and persists the canonical profile entry only when necessary. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`; any Python 3 interpreter satisfying `>=3.11` is accepted.

For optional RCAP interoperability in a package environment:

```bash
python -m pip install 'authtwin[rcap]'
```

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `AuthTwin :: v0.5.11`, `Developer: IsdarlinM`, then the authorization-modeling purpose statement. Use `authtwin --no-color COMMAND`, `authtwin COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean.

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

SRIC 0.5.11 normalizes command metadata to deterministic JSON-safe primitives before FastAPI serialization, preventing unusual CLI defaults or Typer metadata from surfacing as an opaque catalog HTTP 500. Shared Web modules are loaded lazily; a stale/corrupt SRIC therefore no longer turns an optional UI import into a global CLI failure.

For `/console` and `/workbench`, AuthTwin overrides the native dashboard CSP with a shared-route policy that explicitly allows `style-src 'self' 'unsafe-inline'` and `script-src 'self'`; this permits the same-origin SRIC stylesheet and script while preserving `object-src 'none'`, `base-uri 'none'` and `frame-ancestors 'none'`.

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

The 0.5.11 Web regression verifies that both shared Web pages return a CSP allowing same-origin styles/scripts and that `/console/styles.css` is reachable. The 0.5.10 installer/catalog regressions remain in force for atomic first-party resolution, signed SRIC 0.5.11 pin/lock, venv-only repair, Termux `$PREFIX/bin`, safe Windows PATH handling, quiet installer smokes, HTTP-200 Console/Workbench catalogs and complete CLI/Web coverage. Existing unit/integration/E2E/security suites continue to cover actors, roles, tenants, authorization matrix, invariants, differential behavior, lifecycle, GraphQL/batch/WebSocket surfaces and `UNKNOWN`/evidence semantics.

Standalone and full release evidence are written below `build/release-evidence/`. A release is complete only when evidence for the exact commit is PASS.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.authtwin/` are preserved.

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are OFF by default. Apache-2.0.
