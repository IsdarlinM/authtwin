# Web/CLI feature parity

AuthTwin 0.5.6 mounts the shared SRIC Web Feature Workbench at `/workbench` and retains `/console` as an advanced argv-oriented surface.

The Workbench derives its catalog from `authtwin.cli_all`. Every public command and every ordered CLI parameter is represented as a structured responsive Web control. `/api/v1/workbench/coverage` fails the contract when a command or parameter is missing.

Execution remains outside an operating-system shell: structured fields become argv for the fixed `sric.web_console_runner` with `shell=False`, disabled stdin, CSRF protection, redaction, bounded/cancellable jobs and SSE output. Mutating/destructive approval is preserved.

AuthTwin evidence semantics remain authoritative. Missing authorization evidence stays `UNKNOWN`, and Web execution cannot manufacture `VALIDATED` findings.

The release tests invoke help for every public command, verify all options/required arguments, compare the complete ordered CLI parameter tree against the Workbench schema and smoke-test native authorization Web/API routes. Destructive actions are gate-tested instead of being executed merely for coverage.
