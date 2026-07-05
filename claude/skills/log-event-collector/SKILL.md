---
name: log-event-collector
description: >-
  Doctrine for building a log-tailing event collector — a sidecar that tails an application or game
  server's text logs, parses lines into normalized events, and ships them to a backend API.
  Distilled from a production collector for an Assetto Corsa server, but stack-agnostic. Use when
  building or reviewing a log tailer, log-to-event parser, file offset persistence, log rotation or
  truncation handling, multi-line event correlation, shutdown flush, or idempotency/dedup keys for
  shipped events. Do NOT use for configuring log aggregation stacks (Loki, Fluentd, Filebeat), for
  the API that receives the events (that is python-rest-api), or for metrics/APM instrumentation.
metadata:
  author: solvelab
  version: 1.0.0
  category: backend
license: MIT
compatibility: Works in Claude Code, Claude.ai, and any environment with filesystem access.
---

Read and follow all instructions in ~/ai-skills/skills/log-event-collector/SKILL.md
