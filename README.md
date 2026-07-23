# AuthTwin

```text
AuthTwin
imr :: v0.3.0
```

Authorization Digital Twin for modeling **who can do what, to which resource, in which state**, while preserving `UNKNOWN` instead of inventing findings.

> **AI proposes. Evidence proves. Humans control.**

## What works in v0.3.0

- actors, roles, tenants, suspension state and resources/ownership/sharing;
- observed authorization decisions with evidence references and timestamps;
- Authorization Matrix with unobserved cells represented as `UNKNOWN`;
- configurable authorization invariants and candidate-finding generation;
- differential actor comparison and Skeptic-style alternative explanations;
- explicit validation gate: a finding cannot become `VALIDATED` without evidence;
- JSON import/export and conservative RCAP import/export through ReproSec;
- measurable authorization coverage, safe counterfactual validation plans and state/session lifecycle modeling;
- strict invariant DSL, GraphQL/batch authorization analysis and Skeptic reviews;
- authorization discovery v2 with endpoint/resource-family normalization and conservative actor-resource bindings;
- actor/resource/membership state machine v2, safe mutation plans, differential response intelligence and reusable invariant library;
- GraphQL/WebSocket authorization surfaces remain evidence-native and unobserved gaps remain `UNKNOWN`;
- shared SRIC 0.4 workspace namespaces, graph/jobs/SSE, evidence lineage, notebook/search and content-addressed evidence primitives;
- local FastAPI + responsive Web UI backed by real workspace APIs;
- offline synthetic demo, signed-update primitive through SRIC, scope checks, plugin inspection and AI-disabled mode.

## Five-minute start

```bash
authtwin doctor
authtwin demo --workspace demo
authtwin matrix demo
authtwin findings demo
authtwin web demo
```

## Evidence semantics

`ALLOW`, `DENY` and `UNKNOWN` describe observations/model gaps. A `HYPOTHESIS` is not a vulnerability. Only deterministic validation with explicit evidence can create a `VALIDATED` result.

## Safety and privacy

Use only on systems/data you own or are authorized to assess. Cloud AI, telemetry and external uploads are off by default. Non-loopback Web UI binding is refused until an authenticated TLS deployment mode exists.

## Documentation

See `docs/` for installation, CLI, Web UI, architecture, security/threat model, AI, plugins, formats, integrations, release and development guidance. `ROADMAP.md` lists functionality deliberately deferred beyond v0.3.0.

## License
Apache-2.0.
