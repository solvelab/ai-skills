# Reference — documentation templates

Skeletons for each document. Every section is optional except the lead: include only what the
project earns. Fenced blocks below are templates, not claims about any repo.

## README.md skeleton

Only the lead is mandatory — the title and the one-line description of what the software does. Every
other section below is included only if this project earns it.

The header block is for public/OSS-facing repos. For an internal service or a private tool, a plain
`# Title` plus the one-line description is the correct header — drop the div and the badges entirely.

Badges follow the signal-only rule from the skill: include the ones that can *fail* (CI status,
coverage, published version), skip the hardcoded ones that only restate the tech stack the Tech Stack
table already lists.

```markdown
<div align="center">
  <img src="logo.png" alt="Project Name" width="180" />

  # Project Name

  **One-line description of what the software does and why it exists.**

  [![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)](https://github.com/org/repo/actions/workflows/ci.yml)
  [![PyPI](https://img.shields.io/pypi/v/package.svg)](https://pypi.org/project/package/)
</div>

## Features

- **Feature Name**: Brief description of what it does
- **Another Feature**: Brief description

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.115+ |
| Database  | PostgreSQL 16 |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Using Docker Compose

\```bash
docker compose up
# API available at http://localhost:8000
\```

### Local Development

\```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
\```

## Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `LOG_LEVEL` | No | `INFO` | Log verbosity |

## API Endpoints (or Commands)

### Resource Name

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/items` | Yes | List items |
| POST | `/api/v1/items` | Yes | Create item |

## Architecture

\```
ASCII diagram showing component interactions
\```

## Folder Structure

\```
project/
├── app/
│   ├── api/          # Route handlers
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   └── main.py       # Entry point
├── tests/
├── Dockerfile
└── docker-compose.yml
\```

## Development

\```bash
# Run tests
pytest tests/ -v

# Lint
ruff check app/
\```

## Docker Commands

\```bash
docker compose up -d        # Start
docker compose logs -f       # Logs
docker compose down          # Stop
docker compose up -d --build # Rebuild
\```

## Troubleshooting

**Problem**: Description of common issue
**Solution**: How to fix it

## License

MIT
```

---

## docs/SETUP.md skeleton
The setup guide takes someone from zero to a running system. Follow this progression:

```markdown
# Setup Guide

Step-by-step guide to configure [Project Name] from scratch.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Configure Environment](#2-configure-environment)
3. [Deploy with Docker](#3-deploy-with-docker)
4. [Verify It Works](#4-verify-it-works)
5. [Troubleshooting](#5-troubleshooting)

## 1. Prerequisites

Before starting, make sure you have:

- Docker and Docker Compose installed
- [Dependency X] running and accessible

### Verify Dependencies

\```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy"}
\```

## 2. Configure Environment

\```bash
cp .env.example .env
# Edit .env with your settings
\```

### Environment Template

\```bash
# =============================================================================
# Database
# =============================================================================
DATABASE_URL=postgresql://user:pass@db:5432/mydb

# =============================================================================
# Authentication
# =============================================================================
JWT_SECRET_KEY=your-secret-here
\```

## 3. Deploy with Docker

\```bash
docker compose build
docker compose up -d
docker compose ps  # verify containers are running
\```

### Verify Logs

\```bash
docker compose logs -f api
# Expected: "Application started on port 8000"
\```

## 4. Verify It Works

\```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy"}
\```

## 5. Troubleshooting

**Problem**: Container exits immediately
**Solution**: Check logs with `docker compose logs api`. Common cause: missing env vars.

## Next Steps

- [ ] Configure production secrets
- [ ] Set up monitoring
- [ ] Review security checklist
```

---

### Setup guide conventions

- Numbered sections with a table of contents at the top, anchors matching the numbers.
- Prerequisites as `- [ ]` checkboxes so a reader can track them.
- **Verify after every step.** Each action is followed by the command that confirms it worked and the
  output it should print. A setup guide with no verification is a list of hopes.
- Group the environment template by feature area with comment dividers (`# ====`), matching the order
  of the config module so the two can be diffed.
- Troubleshooting covers the failures this project actually produces — take them from the exception
  messages and error paths in the code, not from a generic list, and add one whenever a reader hits a
  new one.
- End with a `- [ ]` Next Steps checklist for what comes after "it runs".

---

## docs/TECHNICAL.md skeleton
The technical reference is for deep understanding. This is where AI tools and new contributors go to understand *how* the system works.

```markdown
# Technical Documentation

Detailed architecture, components, and data flows for [Project Name].

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Components](#3-components)
4. [Data Flow](#4-data-flow)
5. [DTOs and Entities](#5-dtos-and-entities)
6. [HTTP Clients / External Integrations](#6-http-clients)
7. [Services](#7-services)
8. [Logging and Observability](#8-logging-and-observability)
9. [Testing](#9-testing)
10. [Extending the System](#10-extending-the-system)
```

---

### Technical doc conventions

- Table of contents with anchors, numbered to match the sections.
- Architecture diagram first — a text box diagram of how the components connect.
- Document the **data flows**: the path a request or event takes, step by step, naming the module at
  each hop so a reader can jump straight to the code.
- Show real method signatures with types for services and clients, not paraphrases.
- An **"Extending the system"** section: how to add a module, an integration, an endpoint. This is the
  section contributors and coding agents use most.
- This is the explanation tier — put the *why* here (trade-offs, constraints, rejected alternatives)
  and keep step-by-step commands in the setup guide, so the two decay at their own speeds.

---

## Formatting conventions
### Tables

Use tables for any structured, repeatable data:

```markdown
| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `DB_HOST` | Yes | - | Database hostname |
| `LOG_LEVEL` | No | `INFO` | Log verbosity |
```

- Center-align boolean/status columns (`:---:`)
- Use inline code for variable names, commands, values
- Group rows by category using bold header rows when the table is long

### ASCII Diagrams

Use text-based diagrams for architecture and flows:

```
┌─────────────┐     HTTP      ┌──────────────┐
│   Service A │ ─────────────>│  Service B   │
└─────────────┘               └──────────────┘
       │                             │
       │ Events                      │ SQL
       v                             v
┌─────────────┐               ┌──────────────┐
│  Message Q  │               │  PostgreSQL  │
└─────────────┘               └──────────────┘
```

Use box-drawing characters (`┌ ─ ┐ └ ┘ │ ├ ┤ ┬ ┴ ┼`) for clean diagrams. Reserve simple arrows (`→ ← ↓ ↑`) for inline flows.

### Code Blocks

- Always specify the language: ` ```bash `, ` ```python `, ` ```yaml `, ` ```json `
- Include comments explaining non-obvious commands
- Show expected output when the command produces meaningful results

### Directory Trees

```
project/
├── app/
│   ├── api/          # Route handlers
│   ├── models/       # Database entities
│   ├── services/     # Business logic
│   └── main.py       # Entry point
├── tests/
│   ├── test_*.py     # Unit tests
│   └── conftest.py   # Shared fixtures
└── docker-compose.yml
```

Always include inline comments (`# Purpose`) for each directory.

### Section Dividers

Use `---` (horizontal rule) between major sections for visual separation.

### Cross-References

Link between documentation files:

```markdown
See [Setup Guide](docs/SETUP.md) for first-time configuration.
See [Technical Documentation](docs/TECHNICAL.md) for architecture details.
```

---

---

## CHANGELOG.md format (generated by semantic-release — do not hand-write)
Use semantic-release format:

```markdown
## [v1.2.0](https://github.com/org/repo/compare/v1.1.0...v1.2.0) (2026-03-13)

### Features

* **auth**: add OAuth support for Google and GitHub ([abc1234](https://github.com/org/repo/commit/abc1234))

### Bug Fixes

* **orders**: fix fee calculation for products under R$8 ([def5678](https://github.com/org/repo/commit/def5678))
```

- Reverse chronological order (newest first)
- Group entries: Features, Bug Fixes, Breaking Changes
- Include commit hash links
- Prefix entries with scope in bold: `**module**:`

---
