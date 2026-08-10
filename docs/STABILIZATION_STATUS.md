# AuthTwin 0.5.13 stabilization status

Date: 2026-08-10

AuthTwin 0.5.13 is under Sentinel Forge P0/P1 stabilization and is not considered a fully gated stable release until the exact release commit passes the coordinated Windows/Linux and Python 3.11-3.13 gates.

This stabilization branch fixes the notebook workspace NameError path, adds a data-preserving Windows uninstaller, removes CI dependence on private core tokens/branch-name coupling and adds regression coverage. Authorization gaps continue to remain UNKNOWN unless deterministic evidence validates them.

The official update channel remains unchanged until hosted CI can execute and release evidence, SBOM/provenance and dependency review are complete.
