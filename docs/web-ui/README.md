# Web UI

The local Web UI reads the same shared workspace model as the CLI/API and exposes only implemented, evidence-backed capabilities, including coverage, authorization matrix, counterfactuals and v0.3 discovery/state/mutation surfaces. It does not bypass Scope/Policy controls or invent synthetic actions. Non-loopback deployment requires authenticated TLS; v0.3 remains local-first by default. Same-origin API calls and a restrictive CSP are required.
