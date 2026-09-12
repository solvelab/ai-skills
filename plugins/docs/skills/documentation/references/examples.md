# Reference — worked examples

One worked example per canonical document, from the same fictional project, with the same section
list the skeleton in [`templates.md`](templates.md) prescribes. Read a skeleton to know which
sections a document has; read the example beside it to know what belongs inside them.

The project: **OrderFlow**, a service that receives Shopify order webhooks and syncs them to an ERP
through a queue. Every number, path and payload below is internally consistent, so the examples can
be read as one repository rather than six fragments.

## Contents

- [README.md](#readmemd)
- [docs/en/REQUIREMENTS.md](#docsenrequirementsmd)
- [docs/en/SETUP.md](#docsensetupmd)
- [docs/en/ARCHITECTURE.md](#docsenarchitecturemd)
- [docs/en/OPERATIONS.md](#docsenoperationsmd)
- [docs/en/API.md](#docsenapimd)
- [docs/en/adr/0001-queue-between-api-and-erp.md](#docsenadr0001-queue-between-api-and-erpmd)
- [docs/reports/2026-04-17-erp-cutover.md](#docsreports2026-04-17-erp-cutovermd)
- [The mirror, side by side](#the-mirror-side-by-side)
- [What the layout looks like when it is right](#what-the-layout-looks-like-when-it-is-right)

## README.md

```markdown
# OrderFlow

**Syncs Shopify orders into the ERP within seconds, and loses none of them when the ERP is down.**

[![CI](https://github.com/org/orderflow/actions/workflows/ci.yml/badge.svg)](https://github.com/org/orderflow/actions/workflows/ci.yml)

## Documentation

| Document | What it answers |
|---|---|
| [Requirements](docs/en/REQUIREMENTS.md) | what this is for, who uses it, what it must do |
| [Setup](docs/en/SETUP.md) | how to get it running the first time |
| [Architecture](docs/en/ARCHITECTURE.md) | how it is built and why |
| [Operations](docs/en/OPERATIONS.md) | how it is deployed, and what to do when it breaks |
| [API](docs/en/API.md) | what each endpoint takes and returns |
| Security | not applicable: no public traffic, one service token, no stored card data |

Portuguese: [LEIA-ME](README.pt-BR.md) · [docs/pt-BR/](docs/pt-BR/)

## Quick Start

\```bash
git clone https://github.com/org/orderflow.git
cd orderflow
cp .env.example .env
docker compose up -d
curl -s localhost:8000/api/v1/health
\```

First-time setup with prerequisites and verification: [docs/en/SETUP.md](docs/en/SETUP.md).

## Development

| Command | What it does |
|---|---|
| `pytest tests/ -v` | runs the suite, 84 tests |
| `ruff check app/` | lints |
| `docker compose logs -f worker` | follows the consumer |

## License

MIT
```

The README says what it is, shows the map, and stops. The environment table is not here: it belongs
to the setup guide, and a copy of it here would be the second copy that drifts.

## docs/en/REQUIREMENTS.md

```markdown
# Requirements

What OrderFlow is for, who uses it, and what it must do.

## Table of Contents

1. [Purpose](#1-purpose)
2. [Users and their goals](#2-users-and-their-goals)
3. [Functional requirements](#3-functional-requirements)
4. [Non-functional requirements](#4-non-functional-requirements)
5. [Out of scope](#5-out-of-scope)
6. [Glossary](#6-glossary)

## 1. Purpose

Orders placed in Shopify used to be typed into the ERP by hand, twice a day. Typing them cost about
40 minutes a day and produced 3 to 5 wrong quantities a week. OrderFlow receives the order the
moment it is placed and submits it to the ERP, so the warehouse picks from the ERP and nobody types.

## 2. Users and their goals

| User | Goal | Enters through |
|---|---|---|
| Warehouse operator | see today's orders in the ERP without waiting for a batch | the ERP itself |
| Support agent | tell a customer whether an order reached the ERP | `GET /api/v1/orders/{id}` |
| Shopify | deliver an order event and get a fast answer | `POST /api/v1/webhook` |

## 3. Functional requirements

- **FR-1** An order webhook is persisted before the endpoint answers `200`.
- **FR-2** A webhook whose HMAC signature does not verify is answered `401` and not persisted.
- **FR-3** A failed ERP submission is retried 3 times, 5s, 25s and 125s apart, before the order is
  marked `failed`.
- **FR-4** An order already received is not created twice, however many times Shopify redelivers it.

## 4. Non-functional requirements

- **NFR-1** The webhook endpoint answers in under 500 ms at the 95th percentile.
- **NFR-2** No order is lost while the ERP is unavailable for up to 24 hours.

## 5. Out of scope

- Editing or cancelling an order after it reached the ERP; that stays a human action in the ERP.
- Any product, price or stock synchronisation. Orders only.

## 6. Glossary

| Term | Means | Written in code as |
|---|---|---|
| order | one purchase by one customer, with one or more items | `Order` |
| submission | one attempt to create that order in the ERP | `Submission` |
| nota fiscal | the Brazilian tax document the ERP issues afterwards | `nota_fiscal` |
```

`nota fiscal` keeps its name because it is a legal document with no faithful translation; the
glossary is where that decision is recorded, and `code-locale` is the rule that allows it.

## docs/en/SETUP.md

```markdown
# Setup

Step-by-step guide to run OrderFlow from scratch.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Configure](#2-configure)
3. [Run](#3-run)
4. [Verify](#4-verify)
5. [Troubleshooting](#5-troubleshooting)

## 1. Prerequisites

- [ ] Docker 24+ and Docker Compose 2.20+
- [ ] 2 GB of free memory (Postgres, RabbitMQ and two application containers)
- [ ] Outbound access to `erp.internal:8443` — the sync fails silently without it

\```bash
docker compose version
# Passes at: Docker Compose version v2.20.0 or higher
\```

## 2. Configure

\```bash
cp .env.example .env
\```

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | URL | — | yes | PostgreSQL connection string |
| `RABBITMQ_URL` | URL | — | yes | AMQP connection string |
| `SHOPIFY_WEBHOOK_SECRET` | secret | — | yes | HMAC secret; absent fails the boot |
| `ERP_BASE_URL` | URL | — | yes | ERP endpoint, reached over TLS |
| `LOG_LEVEL` | enum | `INFO` | no | one of `DEBUG`, `INFO`, `WARNING` |

Read from [app/config.py](../../app/config.py). A variable the code never reads does not belong here.

## 3. Run

\```bash
docker compose up -d
docker compose ps
# Passes at: api, worker, db and rabbitmq all show "Up"
\```

## 4. Verify

\```bash
curl -s localhost:8000/api/v1/health
# Passes at: {"status":"healthy","database":"connected","queue":"connected"}
\```

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `api` exits immediately | `SHOPIFY_WEBHOOK_SECRET` unset | set it in `.env`, then restart |
| health says `"queue":"disconnected"` | RabbitMQ still starting | wait 10 s, retry; it boots slower than the API |
| orders stay `received` forever | worker cannot reach the ERP | open `erp.internal:8443`, then restart the worker |
| `000` after the full `--max-time` | egress dropped silently | open the path; a firewall is discarding, not refusing |
```

Each prerequisite states the value that passes. "Docker installed" is not a prerequisite: the reader
cannot fail it, so it verifies nothing.

## docs/en/ARCHITECTURE.md

```markdown
# Architecture

How OrderFlow is built, and the constraints that shaped it.

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
                          │ Postgres │             │  Worker  │ ──> ERP
                          └──────────┘             └──────────┘
\```

## 2. Components

| Component | Lives in | Responsibility |
|---|---|---|
| API | [app/api/](../../app/api/) | verifies the signature, persists, publishes |
| Worker | [app/workers/](../../app/workers/) | consumes, transforms, submits, retries |
| Models | [app/models/](../../app/models/) | `Order` and `Submission`, with their states |

## 3. Data flow

1. Shopify posts to `/api/v1/webhook` — the contract is in [API.md](API.md).
2. The API verifies the HMAC signature and answers `401` when it fails — **FR-2**.
3. The order is written with status `received` before the response — **FR-1**.
4. The API publishes `order.created` and answers `200`.
5. The worker consumes, maps the payload to the ERP shape and submits.
6. Three failures, 5s/25s/125s apart, mark the order `failed` — **FR-3**.

## 5. Trade-offs

**A queue instead of a direct call.** The ERP goes down for hours during its nightly window, and an
order submitted into that window would be lost — **NFR-2** forbids it. The cost is that the order is
not in the ERP when the API answers, so `synced` is a state support has to read rather than assume,
and the queue is one more thing to operate.

**Idempotency by Shopify order id, not by payload hash.** Shopify redelivers the same order with a
changed `updated_at`, so a payload hash would see two different orders — **FR-4** would fail exactly
when it matters, on a redelivery storm.

## 6. Decisions

| ADR | Decision |
|---|---|
| [0001](adr/0001-queue-between-api-and-erp.md) | a queue sits between the API and the ERP |

## 7. Extending the system

Adding a webhook event: a handler in [app/api/webhooks.py](../../app/api/webhooks.py), the event
type in [app/models/events.py](../../app/models/events.py), a consumer in
[app/workers/](../../app/workers/), and a case in [tests/test_webhooks.py](../../tests/test_webhooks.py).
```

The trade-off section names the constraint that forced the choice and cites the requirement by its
identifier. It does not restate what the requirement says.

## docs/en/OPERATIONS.md

```markdown
# Operations

How OrderFlow is deployed, what it consumes, and what to do when it fails.

## Table of Contents

1. [Environments](#1-environments)
2. [Resources](#2-resources)
3. [Deploy](#3-deploy)
4. [Rollback](#4-rollback)
5. [Runbook](#5-runbook)

## 2. Resources

| Resource | Value | Source |
|---|---|---|
| API CPU request / limit | `250m` / `1` | [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml) |
| API memory request / limit | `256Mi` / `512Mi` | [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml) |
| Inbound port | `8000` | [k8s/api-service.yaml](../../k8s/api-service.yaml) |
| Outbound | `erp.internal:8443` | [app/clients/erp.py](../../app/clients/erp.py) |
| Outbound | `rabbitmq.svc:5672` | [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml) |
| Runs as | uid `10001`, read-only root filesystem | [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml) |
| Volume | `2Gi`, class `local-path` | [k8s/pvc.yaml](../../k8s/pvc.yaml) |

## 5. Runbook

### The queue is growing and nothing is consumed

1. `kubectl logs deploy/orderflow-worker --tail=50`.
2. Repeated `ConnectionRefused` on `erp.internal:8443` means the ERP is down. Nothing to do: the
   retry is doing its job, and **NFR-2** covers up to 24 hours.
3. Silent logs mean the consumer died. `kubectl rollout restart deploy/orderflow-worker`.
4. Queue still growing 5 minutes after the restart: page the ERP team; the backlog drains at about
   400 orders a minute, so a 3-hour outage takes roughly 12 minutes to clear.
```

The outbound rows are the ones the sources leave out and the ones that fail quietest. Each row names
the file it was read from.

## docs/en/API.md

```markdown
# API

Base URL: `https://orderflow.internal/api/v1` · Auth: bearer token in `Authorization`.

## Table of Contents

1. [Orders](#1-orders)
2. [Webhook](#2-webhook)
3. [Errors](#3-errors)

## 1. Orders

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/orders` | yes | lists orders, newest first, 50 per page |
| `GET` | `/orders/{id}` | yes | one order, with its submission attempts |
| `GET` | `/health` | no | liveness, plus database and queue state |

### GET /orders/{id}

\```json
{
  "id": "ord_5512",
  "shopify_id": "4412887",
  "status": "synced",
  "total_cents": 4780,
  "submissions": [{"attempt": 1, "at": "2026-03-13T10:02:11Z", "result": "ok"}]
}
\```

## 3. Errors

| Status | Means |
|---|---|
| `401` | the HMAC signature did not verify — **FR-2** |
| `404` | no order with that id |
| `422` | the payload parsed but a field is invalid |
```

Where the service publishes an OpenAPI document, this whole file is one link to it. A hand-written
copy of a generated contract drifts, and nothing signals when it does.

## docs/en/adr/0001-queue-between-api-and-erp.md

```markdown
# 0001 — A queue sits between the API and the ERP

- **Status**: accepted
- **Date**: 2026-03-13
- **Deciders**: the backend team

## Context

The ERP is unavailable for 2 to 4 hours every night during its batch window, and intermittently
during the day. An order submitted into that window is lost, and a lost order is a lost sale.
**NFR-2** requires no order to be lost for up to 24 hours of ERP downtime.

## Decision

The API persists the order and publishes `order.created` to RabbitMQ. A worker consumes the event
and submits to the ERP, retrying 3 times with exponential backoff before marking the order `failed`.

## Consequences

- An order is durable the moment the API answers, before the ERP ever sees it.
- `synced` becomes a state support reads instead of assuming; the customer-facing answer changes
  from "it is in the ERP" to "it is queued, and here is the attempt log".
- RabbitMQ joins the resource table and the runbook, and a growing queue becomes a signal worth
  alerting on.

## Alternatives considered

- **Direct synchronous call.** One component fewer, and every order submitted during the nightly
  window is lost. Rejected against **NFR-2**.
- **Cron re-submission from the database.** No new component, and turns a 2-second sync into a
  15-minute one. Rejected because the warehouse picks continuously and cannot wait on a batch.
```

## docs/reports/2026-04-17-erp-cutover.md

```markdown
# 2026-04-17 — ERP cutover rehearsal

- **Ran by**: the backend team
- **Against**: staging, commit `a1b2c3d`

## What was exercised

1. 500 orders replayed through the webhook, ERP reachable — all 500 reached `synced`.
2. ERP blocked at the firewall for 40 minutes, 120 orders replayed — all 120 stayed `received`,
   none lost, and all 120 reached `synced` 6 minutes after the block was lifted.
3. Duplicate delivery of 50 orders — 50 created, 0 duplicated, which is **FR-4** holding.

## What it means

**NFR-2** holds at 40 minutes; the 24-hour claim is still an extrapolation and is not proven here.
The drain rate measured 420 orders a minute, which is the number the runbook now quotes.
```

The report is dated, signed, and never edited afterwards. The drain rate it measured moved into the
runbook, where it is a permanent fact; the report keeps the date it was true.

## The mirror, side by side

The same section, in the two trees. Prose is translated; the table's data, the code block and the
identifiers are not.

```markdown
<!-- docs/en/SETUP.md -->
## 2. Configure

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `LOG_LEVEL` | enum | `INFO` | no | one of `DEBUG`, `INFO`, `WARNING` |

\```bash
cp .env.example .env
\```
```

```markdown
<!-- docs/pt-BR/SETUP.md -->
## 2. Configurar

| Variável | Tipo | Padrão | Obrigatória | Descrição |
|---|---|---|---|---|
| `LOG_LEVEL` | enum | `INFO` | não | um de `DEBUG`, `INFO`, `WARNING` |

\```bash
cp .env.example .env
\```
```

Same number, same position, same code block. The header row is the translated pair the checker knows,
so the table is still recognized as the setup guide's property in either tree.

## What the layout looks like when it is right

```
orderflow/
├── README.md                 # what it is, the map, quick start, dev commands
├── README.pt-BR.md           # the same, in Portuguese
├── AGENTS.md                 # three commands and a link to the map
├── CHANGELOG.md              # generated
└── docs/
    ├── en/
    │   ├── REQUIREMENTS.md
    │   ├── SETUP.md
    │   ├── ARCHITECTURE.md
    │   ├── OPERATIONS.md
    │   ├── API.md
    │   └── adr/0001-queue-between-api-and-erp.md
    ├── pt-BR/                # the same file names, mirrored
    └── reports/
        └── 2026-04-17-erp-cutover.md
```

Nine documents, no duplicates, and every fact with one address. Run
`check-doc-layout.py .` against it and it says `findings: 0`.
