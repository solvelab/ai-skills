---
name: fivem-fallback
description: Resilience and fallback patterns for FiveM Lua calling an external backend, config store (Consul/KV), or another resource. Use when a resource makes HTTP/export calls that can time out, return 5xx, return partial payloads, or hit a dependency that is down — or when adding config fetch, NUI callbacks that call the backend, or retry logic. Enforces a shared SafeCall/WithFallback helper, hardcoded config defaults, clampNum on remote values, bounded retries, negative cache, and NUI error signaling. Do NOT use for non-FiveM resilience.
metadata:
  author: your-org
  version: 1.0.0
  category: fivem
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/fivem-fallback/SKILL.md
