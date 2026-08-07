# Authorization analysis API

The normal local AuthTwin API now exposes:

```text
POST /api/v1/layers/compare
POST /api/v1/policy/import
POST /api/v1/coverage/prioritize
```

Layer comparison returns evidence-bearing drift candidates and never creates a validated finding. Policy imports are configured-only, parse untrusted data and never execute it. Coverage priority is a research-coverage metric, not a risk or vulnerability score; every input cell remains `UNKNOWN`.
