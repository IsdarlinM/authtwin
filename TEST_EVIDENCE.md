# Test Evidence — AuthTwin v0.5.0 Release Candidate

## Release-candidate review — 2026-08-08

The `agent/release-0.5.0` branch contains the AuthTwin 0.5 changes under review:

- SRIC/ReproSec 0.5 compatibility;
- coverage-guided authorization validation planning;
- explicit equivalence classes before different resources may share one representative experiment;
- safe-only planning by default while all unobserved cells remain `UNKNOWN`;
- deterministic cross-tool claim fingerprints;
- 0.5 regression tests and standardized release-evidence gate v2.

## Fresh execution status

**THE COMPLETE v0.5.0 RELEASE GATE HAS NOT BEEN EXECUTED SUCCESSFULLY FOR THIS BRANCH.**

The private repository cannot be materialized as a complete local checkout through this runtime. GitHub Actions currently terminates with `startup_failure` before any test job or check-run starts; this is recorded as an infrastructure blocker and not as a test PASS/FAIL.

## Required release evidence

Run from sibling 0.5 checkouts:

```bash
python sric-core/scripts/release-ecosystem.py --root .
```

The release train builds exact local SRIC/ReproSec candidate wheels before AuthTwin's isolated install smoke, runs the repository gate and then verifies the cross-product contract.

Do not merge/tag AuthTwin 0.5 until its exact-commit `release-gate.json` and the ecosystem `ecosystem-release-gate.json` both report `PASS`.

Previous 0.3.x evidence remains a historical regression baseline only.
