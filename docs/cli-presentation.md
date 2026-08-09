# CLI presentation

AuthTwin 0.5.9 uses the shared Sentinel Forge CLI presentation contract from SRIC Core.

Interactive console sessions show a subdued green ASCII banner ordered as `AuthTwin :: v0.5.9`, `Developer: IsdarlinM`, then the concise purpose statement. The banner is written to interactive stderr, keeping stdout suitable for JSON, reports, redirection, and automation.

Use `authtwin --no-color COMMAND` to disable ANSI/Rich colors. The installed console entrypoint also normalizes `authtwin COMMAND --no-color`. The standard `NO_COLOR` environment variable is honored.

The public help contract includes `authtwin --help`, `authtwin -h`, `authtwin help`, `authtwin COMMAND --help`, `authtwin COMMAND -h`, and `authtwin COMMAND help`. The release regression suite walks every public command and compares its ordered CLI parameters with the Web Feature Workbench schema.

Typer/Rich command and help presentation is colorized by default. `--no-color` changes presentation only; it does not alter authorization models, evidence, invariants, validation plans, update verification, Web Feature Workbench/Command Console behavior, or API responses.
