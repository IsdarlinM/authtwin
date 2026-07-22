# AuthTwin

```text
AuthTwin
imr :: v0.2.0
```

Authorization Digital Twin for modeling **who can do what, to which resource, in which state**, while preserving `UNKNOWN` instead of inventing findings.

> **AI proposes. Evidence proves. Humans control.**

## What works in v0.2.0

- actors, roles, tenants, suspension state and resources/ownership/sharing;
- observed authorization decisions with evidence references and timestamps;
- Authorization Matrix with unobserved cells represented as `UNKNOWN`;
- configurable authorization invariants and candidate-finding generation;
- differential actor comparison and Skeptic-style alternative explanations;
- explicit validation gate: a finding cannot become `VALIDATED` without evidence;
- JSON import/export and conservative RCAP import;
- valid RCAP export through ReproSec; HTTP status alone is never interpreted as authorization intent;
- local FastAPI + responsive Web UI backed by real workspace APIs;
- offline synthetic demo, signed-update primitive through SRIC, scope checks, plugin inspection and AI-disabled mode.

- measurable authorization coverage and deterministic resource/operation discovery;
- safe counterfactual validation plans that remain `HYPOTHESIS`/`UNKNOWN` until executed through evidence-producing validation;
- observed state/session lifecycle modeling, strict invariant DSL, GraphQL surface grouping and batch authorization analysis;
- Skeptic reviews that enumerate alternative explanations and missing evidence before elevation;
- SRIC 0.3 temporal graph, jobs/SSE, evidence lineage, notebook/search and content-addressed evidence primitives;

## Five-minute start

```bash
authtwin doctor
authtwin demo --workspace demo
authtwin matrix demo
authtwin findings demo
authtwin web demo
```

Import the offline lab:

```bash
authtwin init lab
authtwin import lab examples/lab/authorization-model.json
authtwin matrix lab
```

## Evidence semantics

`ALLOW`, `DENY` and `UNKNOWN` describe observations/model gaps. A `HYPOTHESIS` is not a vulnerability. Only deterministic validation with explicit evidence can create a `VALIDATED` result.

## Safety and privacy

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are off by default. Non-loopback Web UI binding is refused until an authenticated TLS deployment mode exists.

## Documentation

See `docs/` for installation, CLI, Web UI, architecture, security/threat model, AI, plugins, formats, integrations, release and development guidance. `ROADMAP.md` lists functionality deliberately deferred beyond v0.2.0.

## License

Apache-2.0.
