# FiveM Fallback Skill

Resilience for FiveM Lua calling an external backend / config store / another resource: shared
SafeCall/WithFallback, hardcoded config defaults, clampNum, bounded retries, negative cache, NUI error signaling.

## When to use

A resource makes HTTP/export calls that can fail (timeout, 5xx, partial payload, dependency down), or
when adding config fetch, NUI callbacks that hit the backend, or retry logic.

## Instructions

@../../shared/skills/fivem-fallback/content.md
