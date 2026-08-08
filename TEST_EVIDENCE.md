# Test Evidence — AuthTwin v0.5.0 Release Candidate

## Release-candidate review — 2026-08-08

The `agent/release-0.5.0` branch contains:

- SRIC 0.5 compatibility; ReproSec is optional through the `rcap` extra;
- coverage-guided authorization validation planning with explicit equivalence classes;
- safe-only automatic experiment selection while unobserved cells remain `UNKNOWN`;
- `authtwin capabilities` and `/api/v1/capabilities`;
- standalone CLI/API/Web tests and recursive help/parser contracts;
- Linux/Windows clean-install smoke definitions with no ReproSec requirement;
- a separate optional RCAP-integration CI job;
- Linux runtime uninstall that preserves workspaces/configuration/evidence;
- standardized standalone and release-evidence gates.

## Fresh execution status

**THE COMPLETE v0.5.0 TEST/RELEASE GATES HAVE NOT EXECUTED SUCCESSFULLY FOR THIS BRANCH.**

The repository cannot be materialized as a complete local checkout in this runtime. The latest observed GitHub Actions run concluded `startup_failure` and exposed zero jobs. No pytest, installer, static-analysis or wheel result from that run is counted as evidence.

## Required exact-commit evidence

```bash
python -m sric.standalone_gate --root authtwin
python sric-core/scripts/release-standalone-ecosystem.py --root .
python authtwin/scripts/release-gate.py
python sric-core/scripts/release-ecosystem.py --root .
```

Required results are PASS for AuthTwin's standalone gate, AuthTwin's release gate, the ecosystem standalone gate and the integrated ecosystem release gate. Previous 0.3.x evidence remains a historical baseline only.
