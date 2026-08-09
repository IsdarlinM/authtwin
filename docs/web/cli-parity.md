# Web/CLI capability parity

AuthTwin 0.5.4 mounts the shared SRIC 0.5.4 Web Command Console at `/console`.

The console discovers `authtwin.cli_all` at runtime and exposes the same public command tree, including nested commands, through a responsive same-origin UI and `/api/v1/console/*` API. A standalone regression test requires the Web catalog and CLI catalog to be exactly equal.

This is not an operating-system shell. Execution uses the fixed `sric.web_console_runner`, `shell=False`, disabled stdin and an argv array. The browser cannot choose an executable. Mutating commands require explicit approval; destructive command names require an approval phrase. AuthTwin authorization-model, evidence and validation safety gates remain authoritative, and missing evidence remains `UNKNOWN`.

Arguments and retained output are redacted, output is rendered as untrusted text, console jobs are cancellable and output/status is streamed with SSE. Commands requiring interactive stdin must use their explicit CLI flags in the Web argument field.

See the shared SRIC document `docs/web/cli-parity.md` for the complete execution and security contract.
