---
name: python-rest-api
description: >-
  Conventions for Python REST APIs (FastAPI + pydantic v2), distilled from real solvelab production
  services. Use when creating or reviewing a Python API service — project layout, response envelope
  with centralized response codes, exception-handler registry (input errors are never raw 500),
  Field-constraint validation, tenant-isolation lookups, session-per-request DB access,
  pydantic-settings config, two-tier health endpoints, and the testing stack (SQLite unit fixtures,
  testcontainers integration marker, adversarial test naming, OpenAPI golden snapshot, Schemathesis
  fuzz gate). Also machine-to-machine service auth (named token catalog), domain-state idempotency
  with partial unique indexes, JSONB dialect variants, and out-of-process ingestion workers (UDP).
  The baseline that api-resilience-testing and bug-hunter assume.
metadata:
  author: solvelab
  version: 1.2.0
  category: backend
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/python-rest-api/SKILL.md

Reference files are in ~/ai-skills/skills/python-rest-api/references/ — read them when the skill instructions point to them.
