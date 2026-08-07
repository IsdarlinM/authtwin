# Local release validation

AuthTwin does not depend on GitHub Actions or another hosted CI service.

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The full local gate runs compilation, Ruff, strict mypy, all pytest suites, project security/evaluation scripts when present, `pip-audit`, SBOM generation when available, package build, isolated wheel installation and root CLI `--help`/`-h` checks. Machine-readable evidence is written to `build/release-evidence/release-gate.json` with SHA-256 hashes for generated artifacts.

`python scripts/release-gate.py --quick` is a development-only check. A release must not be announced without a complete `PASS` report for the exact source commit.
