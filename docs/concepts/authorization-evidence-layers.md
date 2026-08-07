# Authorization evidence layers

AuthTwin keeps policy intent, deployed configuration and observed enforcement separate.

## INTENDED

Represents documentation, design requirements or policy-as-code intent. It can describe what should happen, but it does not prove that the deployed system contains or enforces that policy.

## CONFIGURED

Represents configuration imported from an authorization system, cloud/IAM export, gateway, application configuration or other deployed artifact. Configuration is evidence of deployment state, not runtime enforcement.

## OBSERVED

Represents a direct authorization decision captured from an authorized test, deterministic replay or other evidence-bearing observation. `OBSERVED` layer records require evidence IDs.

## Comparison semantics

- Intended differs from configured: `CONFIGURATION_DRIFT` hypothesis.
- Configured differs from observed: `ENFORCEMENT_DRIFT` hypothesis.
- Intended differs from observed: `BEHAVIORAL_DRIFT` hypothesis.
- A missing or contradictory layer: `UNKNOWN`.
- All three agree: a consistent sampled observation, not proof of universal enforcement.

Comparisons are scoped by actor, tenant, resource, operation, actor state and resource state. Sessions, caching, eventual consistency, experiment flags and resource transitions are retained as possible alternative explanations.

No layer comparison can create a `VALIDATED` finding. Validation still requires a deterministic plan, controls and evidence through the normal Claim-Evidence workflow.
