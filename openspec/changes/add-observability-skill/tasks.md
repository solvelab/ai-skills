## 1. Probe before prescribing

- [x] 1.1 Install and version-check the stack (fastapi 0.141.1, prometheus-client 0.26.0,
      structlog 26.1.0, opentelemetry-api 1.44.0, instrumentation-fastapi 0.65b0)
- [x] 1.2 Run the middleware end to end: id generated, client id preserved, id on every log line
- [x] 1.3 Verify the cardinality guard: route template labelled, raw path absent from `/metrics`
- [x] 1.4 Verify counter, latency histogram and `fallback_used_total` are exposed

## 2. The skill (1.0.0)

- [x] 2.1 Correlation section with `clear_contextvars()` first and the leak it prevents
- [x] 2.2 RED metrics with the cardinality rule in both framings, carrying the probed evidence
- [x] 2.3 The fallback counter's definition, label rules and rate alert
- [x] 2.4 Health's third state (degraded) as a body field and a metric
- [x] 2.5 Tracing: when it earns its cost, one id not two, honest ceiling
- [x] 2.6 What not to instrument
- [x] 2.7 What to test, handed to `bug-hunter`'s Observable degradation class
- [x] 2.8 Version pin block with everything probed

## 3. Wire it into the family

- [x] 3.1 `backend-resilience` → 2.0.1: links here for the counter's definition
- [x] 3.2 `python-rest-api` → 1.4.1: links here for correlation and the degraded state
- [x] 3.3 README row in the backend section
- [x] 3.4 `./generate.sh` — wrappers and the `plugins/backend` copy produced

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform: name == directory, folded description, solvelab, semver, `backend`,
      MIT, compatibility
- [x] Q.2 Content in English (catalog locale)
- [x] Q.3 Description carries triggers and a `Do NOT use for` clause routing to `log-event-collector`
- [x] Q.4 No duplicated doctrine: the counter is prescribed in `backend-resilience`, defined here;
      neither restates the other
- [x] Q.5 Every quantified claim carries its measured number and conditions
- [x] Q.6 Description states no policy the body contradicts
- [x] Q.7 README updated

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-observability-skill --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync
- [x] V.4 `scripts/validate-skills.py` 0 findings across 32 skills
- [x] V.5 `scripts/selftest-validate-skills.py` 12/12
- [ ] V.6 `openspec archive add-observability-skill --yes` after review
