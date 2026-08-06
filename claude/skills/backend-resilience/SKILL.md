---
name: backend-resilience
description: >-
  Resilience and fallback patterns for any service calling an unreliable dependency — external API,
  config store (Consul/KV), database, message broker, or another internal service. Use when adding or
  reviewing code that makes network calls that can time out, return 5xx, return partial payloads, or
  hit a dependency that is down — or when adding config fetch, retry logic, caching of failures, or
  degraded-mode behavior. Enforces explicit timeouts and a wall-clock deadline, retries only on
  idempotent operations with exponential backoff + jitter, safe defaults, one shared fallback helper,
  response-shape validation, clamping of remote values, negative caching with single-flight, and
  observable degradation. Examples in Python; the doctrine is language-agnostic. For the FiveM/Lua
  adaptation use fivem-fallback instead.
metadata:
  author: solvelab
  version: 2.0.0
  category: backend
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/backend-resilience/SKILL.md

Reference files are in ~/ai-skills/skills/backend-resilience/references/ — read them when the skill instructions point to them.
