# AuthTwin

```text
AuthTwin
imr :: v0.3.1
```

Authorization Digital Twin for modeling **who can do what, to which resource, in which state**, while preserving `UNKNOWN` instead of inventing findings.

> **AI proposes. Evidence proves. Humans control.**

## Implemented

- actors, roles, tenants, suspension state and resources/ownership/sharing;
- observed authorization decisions with evidence references and timestamps;
- Authorization Matrix with unobserved cells represented as `UNKNOWN`;
- configurable authorization invariants and candidate-finding generation;
- differential actor comparison and Skeptic-style alternative explanations;
- explicit validation gate: a finding cannot become `VALIDATED` without deterministic evidence;
- JSON import/export and conservative RCAP interoperability through ReproSec;
- measurable coverage, safe counterfactual plans and state/session lifecycle modeling;
- strict invariant DSL, GraphQL/batch analysis and WebSocket lifecycle modeling;
- endpoint/resource-family normalization and conservative actor-resource bindings;
- shared SRIC 0.4.1 workspace, graph, jobs/SSE, lineage, notebook/search and confidence calibration;
- local FastAPI API, responsive Web UI and offline synthetic demo.

## Authorization evidence layers in v0.3.1

AuthTwin now separates:

- `INTENDED`: documented or declared policy;
- `CONFIGURED`: deployed authorization configuration;
- `OBSERVED`: runtime behavior backed by direct evidence.

A mismatch between layers is not automatically an authorization bypass. Configuration drift, enforcement drift and behavioral drift remain `HYPOTHESIS`. Missing or contradictory layer evidence produces `UNKNOWN`. Comparisons include tenant, actor state and resource state so observations from different contexts are not combined incorrectly.

## Five-minute start

```bash
authtwin doctor
authtwin demo --workspace demo
authtwin matrix demo
authtwin findings demo
authtwin web demo
```

## Local release gate

AuthTwin does not require hosted CI:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The release gate writes machine-readable evidence to `build/release-evidence/release-gate.json`. No release is complete without a full `PASS` report for the exact commit.

## Evidence semantics

`ALLOW`, `DENY` and `UNKNOWN` describe observations or model gaps. A `HYPOTHESIS` is not a vulnerability. Only deterministic validation with explicit evidence can create a `VALIDATED` result.

## Safety and privacy

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are off by default. Non-loopback Web UI binding is refused until authenticated TLS deployment exists.

See `docs/` and `ROADMAP.md` for architecture, security, CLI, formats, integrations and deferred work. Apache-2.0.
