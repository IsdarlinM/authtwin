# GraphQL fields and subscription revocation

AuthTwin 0.3.1 records field-level GraphQL authorization observations in equivalent tenant, resource and state contexts.

Different actor decisions for the same field produce a `HYPOTHESIS`, not a vulnerability. A single actor, contradictory observations or missing deterministic decisions remain `UNKNOWN`. Resolver errors, field masking, ownership and intended policy remain explicit alternative explanations.

WebSocket/GraphQL subscription observations preserve event order, revocation time, reauthentication, reconnects and evidence. Payloads observed after a recorded revocation produce a hypothesis only when a pre-revocation control event exists. Missing revocation or control evidence remains `UNKNOWN`.

CLI:

```bash
authtwin graphql-fields field-observations.json
authtwin subscription-revocation subscription-events.json
```

Extended loopback API:

```bash
python -m uvicorn authtwin.api_vnext:create_app --factory --host 127.0.0.1 --port 8762
```

```text
POST /api/v1/surfaces/graphql-fields
POST /api/v1/surfaces/subscription-revocation
```
