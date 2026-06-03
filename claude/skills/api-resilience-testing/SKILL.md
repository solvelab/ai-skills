---
name: api-resilience-testing
description: Tests REST/HTTP APIs beyond the happy path — negative, fuzz, contract, and security testing — to find critical failures before production. Use this skill whenever the work involves a REST API: adding or changing an endpoint, reviewing an API PR or diff, writing API tests, designing request/response schemas, or when the user says "test/harden/break/audit/review the API", "negative testing", "fuzz", "API robustness", "API security", "validate payloads", or asks about invalid inputs, status codes, error handling, auth/authz, or OpenAPI/Swagger contract validation. Produces an endpoint map, positive + negative scenarios, suggested automated tests, and a resilience checklist. Do NOT use for non-API or pure happy-path unit testing.
metadata:
  author: solvelab
  version: 1.0.0
  category: testing
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/shared/skills/api-resilience-testing/content.md

Concrete negative-test examples are in ~/ai-skills/shared/skills/api-resilience-testing/references/negative-test-catalog.md — read them when generating test scenarios.
