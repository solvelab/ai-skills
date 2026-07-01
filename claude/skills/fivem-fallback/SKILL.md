---
name: fivem-fallback
description: >-
  FiveM/Lua adaptation of the backend-resilience doctrine: safe defaults, SafeCall/clampNum helpers,
  boot-time config retry, negative cache and NUI error signaling for FiveM resources calling an external
  backend, config store (Consul/KV), or another resource. Use when a FiveM resource makes HTTP/export
  calls that can time out, return 5xx, return partial payloads, or hit a dependency that is down — or
  when adding config fetch, NUI callbacks that call the backend, or retry logic in Lua. For non-FiveM
  services use backend-resilience instead.
metadata:
  author: solvelab
  version: 1.1.0
  category: fivem
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/fivem-fallback/SKILL.md
