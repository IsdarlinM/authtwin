# AuthTwin

```text
AuthTwin :: v0.5.12
Developer: IsdarlinM

Model authorization behavior, invariants, and differential evidence.
```

Authorization Digital Twin for modeling **who can do what, to which resource, in which state**, while preserving `UNKNOWN` instead of inventing findings.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

AuthTwin is independently installable and useful. It requires **SRIC Core >=0.5.12,<0.6** for shared evidence/workspace/policy/Web/runtime primitives, but no sibling Sentinel Forge product is required. ReproSec interoperability remains optional through the `rcap` extra.

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
- deterministic validation gate: no finding becomes `VALIDATED` without evidence;
- optional RCAP interoperability through ReproSec;
- measurable coverage, safe counterfactual plans and state/session lifecycle modeling;
- strict invariant DSL, GraphQL/batch analysis and WebSocket lifecycle modeling;
- coverage-guided validation planning with explicit equivalence classes;
- endpoint/resource-family normalization and conservative actor-resource bindings;
- SRIC graph, jobs/SSE, lineage, notebook/search and confidence primitives;
- local FastAPI API, responsive Web UI and offline synthetic demo;
- zero-config product update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC distribution/module compatibility checks in `doctor` and `/api/v1/runtime-compatibility`;
- full Web Feature Workbench with every public AuthTwin CLI command and argument represented as structured responsive controls;
- JSON-safe shared Web command catalog generation;
- structured redacted HTTP 503 catalog failure handling, bounded Web child reaping and SSE-safe retired-job retention through SRIC 0.5.12;
- shared operational exception containment and persisted Job Engine secret redaction;
- shared-route CSP that permits same-origin Console/Workbench CSS/JS while retaining restrictive object/base/frame policies;
- degraded Web mode that preserves the authorization dashboard and reports actionable 503 compatibility errors;
- advanced Web Command Console with fixed-runner execution, exact CLI-tree parity and real-time jobs;
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

The normal installer pins SRIC Core to immutable signed main commit `4dd0ad417e55fc76fb67d582ec50234bffff2876` and resolves that explicit first-party source in the same pip transaction as AuthTwin. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces, configuration and evidence. It validates host Python and any existing venv; a stale/incomplete/broken runtime rebuilds only `~/.authtwin/venv`. It bootstraps `pip`, `setuptools` and `wheel`, runs `pip check`, imports `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`, requires SRIC `>=0.5.12,<0.6`, and executes doctor/capabilities plus all root help aliases before success.

Installer-internal smokes use `SENTINEL_BANNER=never` and a temporary validation log. Successful installation therefore does not repeat the AuthTwin banner. Normal installation does not use `--force-reinstall`.

Termux prefers a writable `$PREFIX/bin` already present in `PATH`; standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper rather than `setx` and accepts any Python 3 interpreter satisfying `>=3.11`.

For optional RCAP interoperability:

```bash
python -m pip install 'authtwin[rcap]'
```

## CLI presentation and help contract

Interactive terminals display `AuthTwin :: v0.5.12`, `Developer: IsdarlinM`, then the purpose statement. Use `authtwin --no-color COMMAND`, `authtwin COMMAND --no-color`, or `NO_COLOR=1` for plain output.

Supported help forms are:

```text
authtwin --help
authtwin -h
authtwin help
authtwin COMMAND --help
authtwin COMMAND -h
authtwin COMMAND help
```

Unexpected operational exceptions are redacted/contained by SRIC. `SENTINEL_DEBUG=1` is an explicit developer-only opt-in for raw local exception propagation.

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

AuthTwin's native dashboard is the authorization-focused quick view for matrix, coverage, counterfactual plans, evidence detail, search and jobs. `/workbench` provides **All Features**: every public `authtwin.cli_all` command and every CLI parameter as a structured responsive Web form. `/console` remains the advanced argv-oriented console. `/api/v1/runtime-compatibility` exposes shared-runtime diagnostics.

Command metadata is normalized to deterministic JSON-safe primitives. If command-catalog construction itself fails, SRIC 0.5.12 returns a bounded/redacted HTTP 503 instead of an opaque HTTP 500. Shared Web modules are loaded lazily so an incompatible optional Web runtime does not turn into an unrelated global CLI import failure.

For `/console` and `/workbench`, AuthTwin uses a same-origin CSP policy permitting the required shared CSS/JS while retaining `object-src 'none'`, `base-uri 'none'` and `frame-ancestors 'none'`.

Execution is not an operating-system shell: the fixed SRIC runner uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, mutation/destructive approval gates and SSE output. Timed-out children use bounded terminate/kill/wait handling with background reaping when required. Recently pruned terminal jobs remain briefly available to active status/SSE readers. AuthTwin evidence semantics remain authoritative; a Web invocation cannot turn an unobserved gap into `VALIDATED`.

## Updates and shared runtime repair

```bash
authtwin update --check
authtwin update
authtwin update --force
```

Supported stale SRIC runtimes are advanced through fixed immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.12 floor. This avoids unsafe rollback-metadata jumps. A same-version corrupt 0.5.12 runtime is repaired from the fixed signed 0.5.12 snapshot. The normal product updater remains zero-config and does not fall back to blind `git pull`.

The SRIC official update channel may remain on the previous fully gated release while 0.5.12 exact-commit gates are blocked; AuthTwin's first-party pin/repair chain uses fixed verified commits rather than that moving channel.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.12 standalone compatibility regression walks every public AuthTwin CLI command, all supported help forms and exact ordered CLI/Web parameter parity. Existing suites cover Console/Workbench pages/assets/catalogs/coverage, native GET/POST API routes, actors/roles/tenants, matrix/invariants/differential behavior, lifecycle, GraphQL/batch/WebSocket surfaces, RCAP integration, fuzz/security properties and `UNKNOWN`/evidence semantics.

`TEST_EVIDENCE.md` is authoritative for what actually executed. The shared SRIC 0.5.12 focused runtime harness passed its four targeted regressions after first exposing and fixing a background-reaper return-code race. GitHub-hosted runners are currently blocked by an account billing lock, so zero-step workflows are not counted as PASS and do not prove AuthTwin's complete exact-commit release gate.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.authtwin/` are preserved.

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are OFF by default. Apache-2.0.
