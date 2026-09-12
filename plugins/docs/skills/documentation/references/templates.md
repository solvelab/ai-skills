# Reference — documentation templates

One skeleton per canonical document of the map. The section list of each skeleton is fixed: a reader
who learned one project finds the same sections, in the same order, in the next one. What varies is
which documents a project has, never what is inside them.

Fenced blocks below are templates, not claims about any repository. Every table whose header row is
written in **bold** below is an *owned* shape: the checker recognizes that exact header row and
reports it when it appears outside the document that owns it.

## Contents

- [README.md skeleton](#readmemd-skeleton)
- [docs/en/REQUIREMENTS.md skeleton](#docsenrequirementsmd-skeleton)
- [docs/en/SETUP.md skeleton](#docsensetupmd-skeleton)
- [docs/en/ARCHITECTURE.md skeleton](#docsenarchitecturemd-skeleton)
- [docs/en/OPERATIONS.md skeleton](#docsenoperationsmd-skeleton)
- [docs/en/API.md skeleton](#docsenapimd-skeleton)
- [docs/en/adr/NNNN-slug.md skeleton](#docsenadrnnnn-slugmd-skeleton)
- [docs/reports/ skeleton](#docsreports-skeleton)
- [The mirror](#the-mirror)
- [Prerequisite categories](#prerequisite-categories)
- [Formatting conventions](#formatting-conventions)
- [CHANGELOG.md format](#changelogmd-format)

## README.md skeleton

Only the lead is mandatory — the title and the one-line description — plus `## Documentation`, which
is the map of this repository and the one section no project skips.

The header block is for public repositories. For an internal service a plain `# Title` and the
one-line description is the correct header: drop the div and the badges.

```markdown
# Project Name

**One-line description of what the software does and why it exists.**

[![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)](https://github.com/org/repo/actions/workflows/ci.yml)

## Documentation

| Document | What it answers |
|---|---|
| [Requirements](docs/en/REQUIREMENTS.md) | what this is for, who uses it, what it must do |
| [Setup](docs/en/SETUP.md) | how to get it running the first time |
| [Architecture](docs/en/ARCHITECTURE.md) | how it is built and why |
| [API](docs/en/API.md) | what each endpoint takes and returns |
| Operations | not applicable: one environment, started by one command |
| Security | not applicable: no auth, no secrets, no inbound traffic |

Portuguese: [LEIA-ME](README.pt-BR.md) · [docs/pt-BR/](docs/pt-BR/)

## Quick Start

\```bash
git clone https://github.com/org/repo.git
cd repo
cp .env.example .env
docker compose up -d
\```

Full first-time setup, with prerequisites and verification: [docs/en/SETUP.md](docs/en/SETUP.md).

## Development

| Command | What it does |
|---|---|
| `pytest tests/ -v` | runs the test suite |
| `ruff check app/` | lints |
| `docker compose up -d --build` | rebuilds and restarts locally |

## License

MIT
```

The `| Command | What it does |` table is **owned by the README**. Environment variables, endpoints
and operational resources are not: the README links their documents instead of repeating them. The
one deliberate repetition is the quick start, up to 5 commands that also appear in the setup guide.

## docs/en/REQUIREMENTS.md skeleton

The document every project has, whether or not it runs a spec-driven workflow. It answers what the
software is for, who uses it, what it must do, and what every other document means by its terms.

```markdown
# Requirements

What this system is for, who uses it, and what it must do.

## Table of Contents

1. [Purpose](#1-purpose)
2. [Users and their goals](#2-users-and-their-goals)
3. [Functional requirements](#3-functional-requirements)
4. [Non-functional requirements](#4-non-functional-requirements)
5. [Out of scope](#5-out-of-scope)
6. [Glossary](#6-glossary)

## 1. Purpose

Two or three sentences: the problem, who has it, and what changes once this exists.

## 2. Users and their goals

| User | Goal | Enters through |
|---|---|---|
| Warehouse operator | confirm a shipment in under 10 seconds | the web UI |
| Billing service | read an order's final price | `GET /api/v1/orders/{id}` |

## 3. Functional requirements

Numbered, one behaviour each, stated so a test can fail against it.

- **FR-1** The system accepts an order webhook and persists it before answering `200`.
- **FR-2** A webhook whose HMAC signature does not verify is rejected with `401` and not persisted.
- **FR-3** A failed downstream submission is retried 3 times before the order is marked `failed`.

## 4. Non-functional requirements

- **NFR-1** A webhook is answered in under 500 ms at the 95th percentile.
- **NFR-2** No order is lost when the downstream system is unavailable for up to 24 hours.

## 5. Out of scope

- Editing an order after it has been submitted downstream.

## 6. Glossary

| Term | Means | Written in code as |
|---|---|---|
| order | one purchase, one customer, many items | `Order` |
| shipment | one physical box leaving the warehouse | `Shipment` |
```

**Where the project runs a spec-driven workflow**, sections 3 and 4 become an index instead of a
list, and the specifications stay the single source:

```markdown
## 3. Functional requirements

Requirements live in the specifications; this table is their index.

| Capability | Specification | Covers |
|---|---|---|
| order-intake | [openspec/specs/order-intake/spec.md](../../openspec/specs/order-intake/spec.md) | webhook, validation, persistence |
| erp-sync | [openspec/specs/erp-sync/spec.md](../../openspec/specs/erp-sync/spec.md) | retry, backoff, failure state |
```

Never copy a requirement out of a specification into this document: two copies of one rule is one
rule and one lie, and nothing tells the reader which is which.

## docs/en/SETUP.md skeleton

The tutorial: zero to running, one happy path, no options. It owns environment variables and
troubleshooting.

```markdown
# Setup

Step-by-step guide to run Project Name from scratch.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Configure](#2-configure)
3. [Run](#3-run)
4. [Verify](#4-verify)
5. [Troubleshooting](#5-troubleshooting)

## 1. Prerequisites

- [ ] Docker 24+ and Docker Compose 2.20+
- [ ] PostgreSQL 16 reachable, or the bundled compose service
- [ ] Outbound access to `api.stripe.com:443`

\```bash
docker --version
# Passes at: Docker version 24.0.0 or higher
\```

## 2. Configure

\```bash
cp .env.example .env
\```

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | URL | — | yes | PostgreSQL connection string |
| `LOG_LEVEL` | enum | `INFO` | no | one of `DEBUG`, `INFO`, `WARNING` |
| `STRIPE_KEY` | secret | — | yes | read at boot; absent fails the start |

Every row is read from the config module. A variable the code never reads does not belong here.

## 3. Run

\```bash
docker compose up -d
docker compose ps
# Passes at: every service shows "Up"; a line showing "Exited" names the container that failed
\```

## 4. Verify

\```bash
curl -s http://localhost:8000/api/v1/health
# Passes at: {"status":"healthy","database":"connected"}
\```

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| container exits at once | `DATABASE_URL` unset | set it in `.env`, then `docker compose up -d` |
| `000` after the full timeout | egress blocked silently | open `api.stripe.com:443` |
| `000` immediately | port closed, host up | start the service |
```

The `| Variable | Type | Default | Required | Description |` and `| Symptom | Cause | Fix |` tables
are **owned by the setup guide**. A prerequisite states the value that *passes*, never only the
command that probes it.

## docs/en/ARCHITECTURE.md skeleton

The explanation tier: how it is built, and why it is built that way. It owns components, flows and
trade-offs. It never lists environment variables or endpoints — it links their owners.

```markdown
# Architecture

How Project Name is built, and the constraints that shaped it.

## Table of Contents

1. [Overview](#1-overview)
2. [Components](#2-components)
3. [Data flow](#3-data-flow)
4. [Integrations](#4-integrations)
5. [Trade-offs](#5-trade-offs)
6. [Decisions](#6-decisions)
7. [Extending the system](#7-extending-the-system)

## 1. Overview

\```
┌──────────┐   webhook    ┌──────────┐   publish   ┌──────────┐
│ Shopify  │ ───────────> │   API    │ ──────────> │ RabbitMQ │
└──────────┘              └────┬─────┘             └────┬─────┘
                               │ write                  │ consume
                               v                        v
                          ┌──────────┐             ┌──────────┐
                          │ Postgres │             │  Worker  │
                          └──────────┘             └──────────┘
\```

## 2. Components

| Component | Lives in | Responsibility |
|---|---|---|
| API | [app/api/](../../app/api/) | receives webhooks, answers health |
| Worker | [app/workers/](../../app/workers/) | consumes the queue, calls the ERP |

## 3. Data flow

1. Shopify posts to `/api/v1/webhook` (contract: [API.md](API.md)).
2. The API verifies the HMAC signature — **FR-2**.
3. The order is persisted with status `received` before the response — **FR-1**.
4. The worker consumes, transforms and submits; three retries — **FR-3**.

## 5. Trade-offs

**Queue instead of a direct call.** The ERP is down for hours at a time and loses nothing while
queued — **NFR-2**. The cost is that an order is not in the ERP the instant the API answers, so
"synced" is a state the UI must show rather than assume.

## 6. Decisions

| ADR | Decision |
|---|---|
| [0001](adr/0001-queue-between-api-and-erp.md) | a queue sits between the API and the ERP |
| [0002](adr/0002-hmac-verified-before-persist.md) | the signature is verified before anything is written |
```

Requirements are cited by their identifier (`FR-2`), never restated. The document that defines them
is `REQUIREMENTS.md`.

## docs/en/OPERATIONS.md skeleton

Running it in production: how it goes out, what it needs, what it must reach, and what to do when it
breaks. It owns the resource table.

```markdown
# Operations

How Project Name is deployed, what it consumes, and what to do when it fails.

## Table of Contents

1. [Environments](#1-environments)
2. [Resources](#2-resources)
3. [Deploy](#3-deploy)
4. [Rollback](#4-rollback)
5. [Runbook](#5-runbook)

## 2. Resources

| Resource | Value | Source |
|---|---|---|
| CPU request / limit | `250m` / `1` | [k8s/deployment.yaml](../../k8s/deployment.yaml) |
| Memory request / limit | `256Mi` / `512Mi` | [k8s/deployment.yaml](../../k8s/deployment.yaml) |
| Inbound port | `8000` | [k8s/service.yaml](../../k8s/service.yaml) |
| Outbound | `api.stripe.com:443` | [app/clients/stripe.py](../../app/clients/stripe.py) |
| Runs as | uid `10001`, read-only root | [k8s/deployment.yaml](../../k8s/deployment.yaml) |

Every row names the file it was read from. A resource nobody can trace is a resource nobody updates.

## 5. Runbook

### The queue is growing and nothing is being consumed

1. `kubectl logs deploy/worker --tail=50` — a repeated `ConnectionRefused` means the ERP is down.
2. If the ERP is down: nothing to do, the retry is doing its job — **NFR-2**.
3. If the logs are silent: the consumer died. `kubectl rollout restart deploy/worker`.
```

The `| Resource | Value | Source |` table is **owned by this document**. The setup guide links it
rather than repeating it, because a local run and a production deployment are two different readers.

## docs/en/API.md skeleton

The reference tier. Where a generated specification exists, this document is one link to it and
nothing else — a hand-written copy of a generated contract drifts in silence.

```markdown
# API

Base URL: `https://api.example.com/api/v1` · Auth: bearer token in `Authorization`.

## Table of Contents

1. [Orders](#1-orders)
2. [Errors](#2-errors)

## 1. Orders

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/orders` | yes | lists orders, newest first |
| `POST` | `/orders` | yes | creates an order |
| `GET` | `/orders/{id}` | yes | one order by id |

### POST /orders

\```json
{"customer_id": "cus_8821", "items": [{"sku": "ABC-1", "quantity": 2}]}
\```

\```json
{"id": "ord_5512", "status": "received", "total_cents": 4780}
\```

## 2. Errors

| Status | Means |
|---|---|
| `401` | the signature or token did not verify |
| `422` | the payload parsed but a field is invalid |
```

## docs/en/adr/NNNN-slug.md skeleton

One decision per file, numbered sequentially, never renumbered. The format is MADR.

```markdown
# 0001 — A queue sits between the API and the ERP

- **Status**: accepted
- **Date**: 2026-03-13
- **Deciders**: the backend team

## Context

The ERP is unavailable for hours at a time, and an order lost during that window is a
sale lost. Requirement **NFR-2** says no order is lost for up to 24 hours of downtime.

## Decision

The API persists the order and publishes an event. A worker consumes the event and calls the ERP,
retrying with exponential backoff.

## Consequences

- An order is durable the moment the API answers, before the ERP ever sees it.
- "Synced" becomes a visible state instead of an assumption — the UI has to show it.
- One more moving part to operate: the queue is now in the resource table and the runbook.

## Alternatives considered

- **Direct synchronous call.** Simpler, and loses every order submitted while the ERP is down.
- **Cron re-submission from the database.** No new component, and turns a 2-second sync into a
  15-minute one, which the warehouse workflow cannot absorb.
```

A decision worth a paragraph of "why" inside another document is worth an ADR instead: that is how
the explanation tier stops growing a second changelog inside itself.

## docs/reports/ skeleton

A record of one moment: a homologation run, a diagnosis, a migration log. It is dated in its name,
it is never edited afterwards, and it is the only document allowed to go stale on purpose.

```markdown
# 2026-04-17 — Dashboard v2 homologation

- **Ran by**: the platform team
- **Against**: staging, commit `a1b2c3d`

## What was exercised

1. Filter by owner, 12 cases — all passed.
2. Export to CSV, 3 cases — one failed: accented names came back as `?`.

## What it means

The encoding defect is real and is now issue #412. Everything else is ready to go out.
```

A report never becomes documentation. When something in it turns out to be permanent, it is written
into the document that owns that fact, and the report keeps the date it was true.

## The mirror

Every document above exists twice: `docs/en/X.md` and `docs/<tag>/X.md`, same file name, same
sections, same numbering, and the same fenced blocks byte for byte. Only the prose is translated.

```markdown
| Variable | Type | Default | Required | Description |   <!-- docs/en/SETUP.md -->
| Variável | Tipo | Padrão | Obrigatória | Descrição |   <!-- docs/pt-BR/SETUP.md -->
```

The header row is translated; the variable names, defaults and code blocks under it are not. The
same holds for `| Method | Path | Auth | Description |`, `| Resource | Value | Source |`,
`| Command | What it does |` and `| Symptom | Cause | Fix |` — the checker knows both spellings of
each, and knows which document owns it in either language.

`docs/reports/`, `AGENTS.md` and `CHANGELOG.md` have no mirror.

## Prerequisite categories

Walk this list and keep the rows this project earns — a category that does not apply is dropped, not
filled with "N/A". Every value is read from the project's own manifests, never carried over from the
sources that name the category.

| Category | Covers |
|---|---|
| Compute | CPU, memory, and the disk the install needs |
| Platform | architecture and operating systems supported |
| Versions | the supported range of the platform and of every dependency |
| Dependencies | packages, runtimes and CLIs the steps invoke |
| Inbound network | the ports and hostnames that must be free and reachable |
| **Outbound network** | the hostnames and ports the software must *reach* |
| Storage | persistent volumes, and the provisioner or class they need |
| Identity and permissions | uid/gid, filesystem modes, RBAC, accounts, tokens, licences |
| Client | browser and client-side requirements, when the product ships a web UI |
| Operator knowledge | the skills the steps assume the reader already has |

Where each category is documented as a prerequisite, and by whom:

- **Compute** — [K3s](https://docs.k3s.io/installation/requirements) (2 cores / 2 GB server,
  1 core / 512 MB agent); [Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/)
  (1 core, 512 MB, 10-50 GB).
- **Platform** — K3s (x86_64, armhf, arm64); Grafana (five OS families).
- **Versions** — [The Good Docs Project](https://www.thegooddocsproject.dev/template/installation-guide)
  ("Required version for your system"); Grafana (SQLite 3, MySQL 8.0+, PostgreSQL 12+).
- **Dependencies** — The Good Docs Project ("Necessary dependencies or packages").
- **Inbound network** — K3s (6443, 8472/UDP, 51820-51821).
- **Outbound network** — not named by any of these sources; add it anyway, see below.
- **Storage** — [Portainer](https://docs.portainer.io/start/install-ce/server/kubernetes/baremetal),
  [Kubernetes StorageClass](https://kubernetes.io/docs/concepts/storage/storage-classes/).
- **Identity and permissions** —
  [Elastic ECK](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/required-rbac-permissions).
- **Client** — Grafana (Chrome, Firefox, Safari, Edge; "JavaScript must be enabled").
- **Operator knowledge** — The Good Docs Project ("Specialist knowledge or skills").

**Outbound network is the row the sources leave out, and the one that fails quietest.** None of the
five above names it. Its absence was measured on a production watchdog: the guide never said the
cluster had to reach the alerting provider, and blocked egress there produces a healthy process, a
green board, and no alert — the exact state the product existed to distinguish from health.

### Diagnostic tables, when one result has opposite remedies

An "expected output" line can only describe success. When the same command's failures need different
fixes, map every observable result — that is what the `| Symptom | Cause | Fix |` table is for, and
it is why the fix column is not optional.

## Formatting conventions

### Tables

- Center-align boolean or status columns (`:---:`).
- Inline code for variable names, commands and values.
- A cell stops at 120 characters; past that the row is a section (rule R2).
- Past 25 options, the table becomes an index plus one section per option (rule R3).

### Text diagrams

Box-drawing characters (`┌ ─ ┐ └ ┘ │ ├ ┤ ┬ ┴ ┼`) for architecture; simple arrows for inline flows.
Text diagrams are greppable, diff-able and readable by agents, which images are not.

### Code blocks

- Always tag the language: ` ```bash `, ` ```python `, ` ```yaml `, ` ```json `.
- Show what passes, not only what to run.
- A block is copied into the mirror unchanged, comments included.

### Directory trees

Include one only when the layout is genuinely non-obvious, root it where the reader actually stands,
cap it at the directories that carry meaning, and annotate each. Never paste a full `tree` dump: a
tree duplicates the filesystem and is the highest-rot artifact a document can carry.

### Cross-references

```markdown
First-time setup: [docs/en/SETUP.md](docs/en/SETUP.md).
Why it is built this way: [docs/en/ARCHITECTURE.md](docs/en/ARCHITECTURE.md).
```

## CHANGELOG.md format

Generated by semantic-release from the commit history — do not hand-write it, and do not mirror it.

```markdown
## [v1.2.0](https://github.com/org/repo/compare/v1.1.0...v1.2.0) (2026-03-13)

### Features

* **auth**: add OAuth support for Google and GitHub ([abc1234](https://github.com/org/repo/commit/abc1234))

### Bug Fixes

* **orders**: fix fee calculation for products under R$8 ([def5678](https://github.com/org/repo/commit/def5678))
```

- Reverse chronological order, newest first.
- Grouped: Features, Bug Fixes, Breaking Changes.
- Commit hash links, scope in bold.

The commit format that produces it is `conventional-commit`.
