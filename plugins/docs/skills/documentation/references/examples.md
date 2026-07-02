# Documentation Skill — Reference Examples

Real-world examples of good documentation output for each tier. Use these as reference when generating documentation.

---

## README.md Example Snippet

```markdown
# OrderFlow

Automated order processing pipeline that syncs e-commerce orders from Shopify to an internal ERP via event-driven microservices.

## Features

- **Real-time sync**: processes Shopify webhooks within 2 seconds of order creation
- **Retry with backoff**: failed ERP submissions retry 3 times with exponential backoff
- **Audit trail**: every order state transition is logged to PostgreSQL with timestamps

## Tech Stack

| Component | Technology |
|-----------|------------|
| API | FastAPI 0.115 |
| Queue | RabbitMQ 3.13 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Container | Docker + Compose |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Shopify Partner account (for webhook config)

### Run Locally

\```bash
git clone https://github.com/org/orderflow.git
cd orderflow
cp .env.example .env
docker compose up -d
# API available at http://localhost:8000
\```

## Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `RABBITMQ_URL` | Yes | — | RabbitMQ connection string |
| `SHOPIFY_WEBHOOK_SECRET` | Yes | — | HMAC secret for webhook verification |
| `LOG_LEVEL` | No | `INFO` | Log verbosity |

## Architecture

\```
┌──────────────┐    webhook    ┌──────────────┐    publish    ┌──────────────┐
│   Shopify    │ ────────────> │   FastAPI    │ ────────────> │  RabbitMQ    │
└──────────────┘               └──────────────┘               └──────────────┘
                                      │                              │
                                      │ write                       │ consume
                                      v                              v
                               ┌──────────────┐               ┌──────────────┐
                               │  PostgreSQL  │               │  ERP Worker  │
                               └──────────────┘               └──────────────┘
\```

## Folder Structure

\```
orderflow/
├── app/
│   ├── api/              # Route handlers (webhooks, health)
│   ├── models/           # SQLAlchemy models
│   ├── services/         # Business logic (order processing)
│   ├── workers/          # RabbitMQ consumers
│   └── main.py           # FastAPI entry point
├── tests/
│   ├── test_webhooks.py  # Webhook handler tests
│   └── conftest.py       # Shared fixtures
├── docker-compose.yml
└── .env.example
\```
```

---

## docs/SETUP.md Example Snippet

```markdown
# Setup Guide

Step-by-step guide to configure OrderFlow from scratch.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone and Configure](#2-clone-and-configure)
3. [Start Services](#3-start-services)
4. [Verify It Works](#4-verify-it-works)
5. [Configure Shopify Webhooks](#5-configure-shopify-webhooks)
6. [Troubleshooting](#6-troubleshooting)

## 1. Prerequisites

Before starting, make sure you have:

- [ ] Docker 24+ and Docker Compose 2.20+
- [ ] A Shopify Partner account
- [ ] `curl` installed (for verification steps)

### Verify Docker

\```bash
docker --version
# Expected: Docker version 24.x.x or higher

docker compose version
# Expected: Docker Compose version v2.20.x or higher
\```

## 2. Clone and Configure

\```bash
git clone https://github.com/org/orderflow.git
cd orderflow
cp .env.example .env
\```

Edit `.env` with your settings:

\```bash
# =============================================================================
# Database
# =============================================================================
DATABASE_URL=postgresql://orderflow:secret@db:5432/orderflow

# =============================================================================
# Message Queue
# =============================================================================
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# =============================================================================
# Shopify
# =============================================================================
SHOPIFY_WEBHOOK_SECRET=whsec_your_secret_here
\```

## 3. Start Services

\```bash
docker compose build
# Expected: Successfully built all images

docker compose up -d
# Expected: All containers start without errors

docker compose ps
# Expected: All services show "Up" status
\```

## 4. Verify It Works

\```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", "database": "connected", "rabbitmq": "connected"}
\```

## 5. Troubleshooting

**Problem**: Container `orderflow-api` exits immediately
**Solution**: Check logs with `docker compose logs api`. Common cause: `DATABASE_URL` not set or database not ready. Wait 10 seconds and retry — PostgreSQL may still be initializing.

**Problem**: Health check returns `{"rabbitmq": "disconnected"}`
**Solution**: Verify RabbitMQ is running: `docker compose ps rabbitmq`. If restarting, wait for the management UI at `http://localhost:15672`.

**Problem**: Webhook events not appearing in the database
**Solution**: Check the worker logs: `docker compose logs worker`. Verify `SHOPIFY_WEBHOOK_SECRET` matches your Shopify app configuration.

**Problem**: `docker compose build` fails with permission errors
**Solution**: Run `sudo chown -R $USER:$USER .` to fix file ownership, then rebuild.

**Problem**: Port 8000 already in use
**Solution**: Stop the conflicting process: `lsof -ti:8000 | xargs kill -9`, then restart with `docker compose up -d`.
```

---

## docs/TECHNICAL.md Example Snippet

```markdown
# Technical Documentation

Detailed architecture, components, and data flows for OrderFlow.

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Components](#3-components)
4. [Data Flow](#4-data-flow)
5. [Services](#5-services)
6. [Extending the System](#6-extending-the-system)

## 1. Overview

OrderFlow is an event-driven order processing system. Shopify sends webhook events to a FastAPI endpoint, which validates and publishes them to RabbitMQ. Worker processes consume events and sync order data to an external ERP system.

| Component | Technology | Purpose |
|-----------|------------|---------|
| API | FastAPI 0.115 | Receives webhooks, serves health checks |
| Queue | RabbitMQ 3.13 | Decouples webhook ingestion from ERP sync |
| Database | PostgreSQL 16 | Stores order state and audit trail |
| Worker | Python + pika | Consumes queue messages, calls ERP API |

## 2. Architecture

\```
                              ┌─────────────────────────────────────┐
                              │            OrderFlow                │
┌──────────┐    POST          │  ┌─────────┐      ┌─────────────┐  │
│ Shopify  │ ────────────────>│  │  API    │ ───> │  RabbitMQ   │  │
└──────────┘  /api/v1/webhook │  └────┬────┘      └──────┬──────┘  │
                              │       │                   │         │
                              │       │ write             │ consume │
                              │       v                   v         │
                              │  ┌─────────┐      ┌─────────────┐  │
                              │  │ Postgres│      │   Worker    │  │
                              │  └─────────┘      └──────┬──────┘  │
                              │                          │         │
                              └──────────────────────────┼─────────┘
                                                         │ HTTP
                                                         v
                                                   ┌──────────┐
                                                   │   ERP    │
                                                   └──────────┘
\```

## 4. Data Flow

### Order Creation Flow

1. Shopify sends `POST /api/v1/webhook` with order payload
2. API validates HMAC signature using `SHOPIFY_WEBHOOK_SECRET`
3. API writes order to PostgreSQL with status `received`
4. API publishes `order.created` event to RabbitMQ
5. Worker consumes event, transforms payload to ERP format
6. Worker calls ERP API to create order
7. Worker updates PostgreSQL status to `synced` (or `failed` on error)

### Retry Logic

Failed ERP submissions retry with exponential backoff:

| Attempt | Delay |
|---------|-------|
| 1 | 5 seconds |
| 2 | 25 seconds |
| 3 | 125 seconds |

After 3 failures, the order is marked as `failed` and an alert is sent.

## 5. Services

### OrderService

\```python
class OrderService:
    async def create_order(self, payload: ShopifyWebhook) -> Order:
        """Validates webhook, persists order, publishes event."""

    async def get_order(self, order_id: str) -> Order | None:
        """Retrieves order by Shopify order ID."""

    async def update_status(self, order_id: str, status: OrderStatus) -> Order:
        """Updates order sync status."""
\```

## 6. Extending the System

### Adding a New Webhook Event

1. Create a new handler in `app/api/webhooks.py`
2. Register the route in `app/api/__init__.py`
3. Add the event type to `app/models/events.py`
4. Create a worker consumer in `app/workers/`
5. Add tests in `tests/test_webhooks.py`
```
