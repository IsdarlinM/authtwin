# Coverage-Guided Validation in AuthTwin 0.5

AuthTwin 0.5 can transform authorization matrix coverage gaps into a smaller set of representative research experiments.

Every input cell remains `UNKNOWN`. Planning changes research order only; it does not estimate exploitability, severity or vulnerability likelihood and cannot create a finding.

## Explicit equivalence

Different resources are never assumed equivalent merely because they share an actor, tenant, operation or sensitivity. Cross-resource compression occurs only when the caller supplies the same explicit `equivalence_class`, backed by prior modeling/evidence.

Without an equivalence class, the resource ID is part of the planning key and receives an independent experiment.

## Safety

`safe_only=True` is the default. Passive and read-only validation costs may be planned automatically; mutating or prohibited classes are excluded from automatic experiment selection and remain subject to SRIC Scope/Policy/Approval gates.

## Cross-tool correlation

Each plan gets a deterministic SRIC claim fingerprint so equivalent research claims can be deduplicated across tools while their evidence and provenance stay separate.
