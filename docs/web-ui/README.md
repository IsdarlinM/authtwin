# Web UI

The local Web UI reads the same workspace model as the CLI/API. It does not expose synthetic actions or bypass policy. Non-loopback deployment must be protected by authentication before production use; v0.1 is intended for local-first operation. The UI uses same-origin API calls and a restrictive CSP.
