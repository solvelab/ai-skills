---
name: observability
description: >-
  Correlation, metrics and tracing for a backend service — the request id bound to every log line and
  propagated outward, RED metrics per endpoint and per dependency, the registry the fallback counter
  lives in, and when OpenTelemetry earns its cost. Use when adding logging, metrics, tracing, a
  /metrics endpoint, a request-id or correlation-id middleware, health/readiness that reports degraded
  mode, or when asked why an outage was invisible. Enforces one id per request bound to the logger,
  route templates as labels (never raw paths or user ids), and a counter behind every fallback. Do NOT
  use for a log-shipping sidecar's own instrumentation (that is log-event-collector), for configuring
  an aggregation stack (Loki, Fluentd, Filebeat), or for choosing a vendor.
metadata:
  author: solvelab
  version: 1.0.0
  category: backend
license: MIT
compatibility: Works in any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/observability/SKILL.md
