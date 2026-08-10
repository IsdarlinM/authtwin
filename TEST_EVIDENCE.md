# Test Evidence — AuthTwin v0.5.12 Candidate

## Candidate review — 2026-08-10

AuthTwin 0.5.12 aligns the product to SRIC Core 0.5.12 and closes the first-party runtime drift identified by the Sentinel Forge cross-ecosystem audit.

Candidate controls include:

- package metadata, runtime lock, bootstrap, `doctor`, Linux/Termux installer and Windows installer all require SRIC `>=0.5.12,<0.6`;
- clean/repair installation pins signed SRIC main commit `4dd0ad417e55fc76fb67d582ec50234bffff2876`;
- runtime integrity requires `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`;
- supported stale SRIC releases advance through fixed signed snapshots one release at a time from 0.5.5 through 0.5.12;
- same-version corrupt 0.5.12 repairs from the fixed signed snapshot;
- installers remain atomic/idempotent, run `pip check`, preserve user workspaces/evidence and suppress internal banners;
- runtime regressions verify the exact pin, lock, transition chain, same-version repair and degraded Workbench 503 behavior;
- the exhaustive standalone interface contract walks every public AuthTwin command, root/subcommand `--help`, `-h`, trailing `help`, and exact ordered CLI/Web parameter parity;
- existing integration/standalone tests cover native GET/POST authorization APIs, Console/Workbench catalogs and coverage, CSP/assets, actors/roles/tenants, matrix/invariants, GraphQL/batch/WebSocket surfaces, RCAP interoperability, fuzz/security properties and `UNKNOWN` semantics.

## Executed focused evidence relevant to this candidate

The shared SRIC Core 0.5.12 runtime used by AuthTwin was exercised in a focused local harness. Its first run exposed a real background-reaper return-code race (`3 passed, 1 failed`); after correction the harness completed:

```text
4 passed in 0.19s
```

Covered shared behaviors were catalog-503 redaction, retained terminal-job/SSE safety, final-wait background reaping and Job Engine persistence redaction.

This is shared-runtime evidence only and is **not** represented as a full AuthTwin repository/platform/browser PASS.

## AuthTwin exact-commit hosted CI status

**THE COMPLETE v0.5.12 AUTHTWIN TEST/RELEASE GATES HAVE NOT EXECUTED.**

GitHub-hosted jobs cannot allocate runners because the account is locked due to a billing issue. The observed pattern is `runner_id=0`, `steps=[]`; zero-step jobs are infrastructure failure rather than test evidence.

The maintenance execution container also cannot resolve `github.com`, so the complete repository cannot be cloned there as a substitute for the unavailable hosted runners. Static GitHub review and updated test definitions do not equal executed test evidence.

## Required exact-commit evidence before declaring the release complete

```bash
python -m sric.standalone_gate --root authtwin
python sric-core/scripts/release-standalone-ecosystem.py --root .
python authtwin/scripts/release-gate.py
python sric-core/scripts/release-ecosystem.py --root .
```

The Definition of Done still requires successful execution of:

- unit, integration, E2E, security and fuzz suites;
- every public CLI command/help form and exact CLI/Web parameter parity;
- Web Console/Workbench pages, assets, form controls/buttons, catalogs, coverage, submission, cancellation, approval and SSE behavior;
- every documented GET/POST API resource with valid and invalid inputs;
- clean Linux/Termux and Windows install/repair, PATH and quiet-banner behavior;
- signed update/rollback preserving workspaces/config/evidence;
- responsive browser/UI checks and browser-console review;
- dependency/secret/SAST/SBOM/build gates;
- optional RCAP integration separately from standalone operation;
- ecosystem execution against exact final commits.

The project owner explicitly requested integration of the corrected candidate to `main`. Such integration must not be described as proof that the externally blocked full release gates passed.
