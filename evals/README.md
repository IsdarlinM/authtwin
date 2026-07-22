# AI / reasoning evals

AI remains optional and disabled by default. This product consumes SRIC's provider-neutral agent/runtime contracts; external content is untrusted data and model output cannot validate findings.

Product-specific deterministic reasoning/false-positive behavior is regression-tested under `tests/`. Any future product-specific model prompt or provider behavior must add versioned synthetic/anonymous datasets here and run alongside SRIC's `evals/` safety suite.
