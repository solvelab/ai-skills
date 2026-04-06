## CRITICAL: Always Analyze Before Documenting

Before writing any documentation, read the codebase and decide which documents are needed based on what the project actually is.

### Step 1 — Analyze the project

Run these before writing anything:
- `find . -type f | head -60` — understand the file structure
- Read the main entry point, config files, and existing docs
- Identify: language, framework, architecture style, deployment method, integrations

### Step 2 — Decide which documents to create

Use this decision table:

| Condition | Document to create |
|---|---|
| Any project | `README.md` — always |
| Setup requires more than 5 commands | `docs/SETUP.md` |
| Non-trivial architecture (services, flows, integrations) | `docs/TECHNICAL.md` |
| REST or GraphQL API exists | `docs/API.md` |
| Project accepts contributions | `CONTRIBUTING.md` |
| Multiple environments (dev, staging, prod) | `docs/DEPLOYMENT.md` |
| Kubernetes or complex infra | `k8s/README.md` or `docs/INFRASTRUCTURE.md` |
| Version history exists or releases are planned | `CHANGELOG.md` |
| Background workers or scheduled jobs | `docs/WORKERS.md` |
| Webhooks or event-driven architecture | `docs/EVENTS.md` |
| Machine learning models or data pipelines | `docs/MODEL.md` or `docs/PIPELINE.md` |
| CLI tool or scripts | `docs/CLI.md` |
| SDK or library for developers | `docs/SDK.md` |
| Security-sensitive configuration | `docs/SECURITY.md` |

### Step 3 — Create all relevant documents

Do NOT stop after README.md.
Do NOT create documents that don't apply to this project.
Read the codebase first. Only document what actually exists in the code.

Before writing README.md:
- Check for logo/icon files in the repo root (`logo.png`, `logo.svg`, `icon.png`, `favicon.ico`). Include in the header if found.
- Always include shields/badges relevant to the tech stack detected in the codebase (language, framework, license, Docker, database).

---

# Documentation Skill

You are a documentation writer. When asked to create or update project documentation, follow the patterns and principles below. These are derived from real, battle-tested documentation across production codebases.

---

## Core Principles

1. **Purpose first** — the very first lines must explain what the software does and why it exists. A reader (human or AI) should understand the project's value in under 10 seconds.
2. **Simple and human** — write so any developer can understand the solution quickly. Use plain language. Avoid jargon unless it's the project's domain vocabulary.
3. **Vibe coding friendly** — make documentation context-rich enough for AI tools to understand the codebase and assist effectively. Include architecture diagrams, module trees, data flows, and configuration references.
4. **Knowledge transfer** — someone new should be able to onboard just by reading the docs. No tribal knowledge required.
5. **Detail when needed** — simple overview by default, deep-dive sections when complexity demands it. Use a three-tier depth model (see below).
6. **Living documentation** — structure docs so they're easy to update as the software evolves. Prefer tables and lists over prose paragraphs for things that change frequently (env vars, endpoints, commands).

---

## Three-Tier Documentation Model

Organize documentation in three layers of increasing depth:

| Tier | File | Purpose | Audience |
|------|------|---------|----------|
| **1. Overview** | `README.md` | What it does, quick start, feature map, architecture at a glance | Everyone — first thing anyone reads |
| **2. Walkthrough** | `docs/SETUP.md` | Step-by-step first-time setup from zero to running | New developers, DevOps |
| **3. Deep Reference** | `docs/TECHNICAL.md` | Architecture details, data flows, DTOs, extension points | Contributors, maintainers, AI assistants |

Additional docs as needed:
- `CHANGELOG.md` — version history (semantic-release format)
- `ARCHITECTURE.md` — standalone architecture reference (if too large for README)
- `k8s/README.md` — Kubernetes deployment guide
- `docs/<feature>.md` — feature-specific deep dives

---

## README.md Structure

Follow this skeleton. Every section is optional except the first three — include only what's relevant to the project:

```markdown
<div align="center">
  <img src="logo.png" alt="Project Name" width="180" />

  # Project Name

  **One-line description of what the software does and why it exists.**

  [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)]()
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

### README Rules

- **Visual header**: Always start README.md with a centered header block containing: project logo (if one exists in the repo — look for `logo.png`, `logo.svg`, `icon.png`), project title in H1, one-line description in bold, and shields/badges relevant to the project (language, framework, license). Use this structure:
  ```markdown
  <div align="center">
    <img src="logo.png" alt="Project Logo" width="180" />

    # Project Name

    **One-line description**

    [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
    [![Framework](https://img.shields.io/badge/framework-version-blue.svg)](https://framework-url)
    [![License](https://img.shields.io/badge/license-MIT-green.svg)]()
  </div>
  ```
- **Badges to include** (only when relevant to the project):
  - Language + version: Python, Node.js, Go, etc.
  - Main framework + version: FastAPI, Express, Discord.py, etc.
  - License: MIT, Apache, Proprietary
  - Docker: if `docker-compose.yml` exists
  - Database: if a database is configured
- **Logo detection**: Before writing README.md, search for image files in the repo root (`logo.png`, `logo.svg`, `icon.png`, `favicon.ico`). If found, include it in the header. If not found, skip the `<img>` tag.
- **No logo, no problem**: If no logo exists, keep the centered div with just the title, description, and badges.
- **Lead with purpose**: the first line after the header div must be a one-sentence description if not already in the header. No badges or logos outside the centered header div.
- **Quick Start must be quick**: 3-5 commands maximum. If it takes more, link to `docs/SETUP.md`.
- **Features as a scannable list**: use bold feature names with concise descriptions. Use emoji sparingly (only if the project already does).
- **Tables for structured data**: env vars, endpoints, commands, tech stack — always tables, never prose.
- **ASCII diagrams over images**: text-based diagrams are grep-able, git-diff-friendly, and readable by AI tools.
- **Folder structure with annotations**: show the directory tree with inline comments explaining each directory's purpose.
- **Copy-paste ready commands**: every code block should work if pasted directly into a terminal. Include comments for context.

---

## docs/SETUP.md Structure

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

### Setup Guide Rules

- **Table of contents at the top**: numbered sections with anchor links.
- **Checkboxes for prerequisites**: `- [ ]` format so readers can mentally check them off.
- **Verify at every step**: after each major action, show how to confirm it worked. Include expected output.
- **Environment template with section headers**: group env vars by feature area using comment dividers (`# ====`).
- **Troubleshooting is mandatory**: at least 5 common problems with solutions.
- **End with Next Steps**: checklist of follow-up tasks using `- [ ]` format.
- **Commands include expected output**: show what success looks like so the reader knows they did it right.

---

## docs/TECHNICAL.md Structure

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

### Technical Doc Rules

- **Table of contents with anchor links**: always at the top, numbered to match sections.
- **Architecture diagram first**: ASCII box diagram showing how components connect.
- **Document data flows**: show the path data takes through the system, step by step.
- **Include code signatures**: for services and clients, show method signatures with types and return values.
- **DTOs and entities section**: show dataclass/model definitions with field descriptions.
- **"Extending the System" section**: explain how to add new modules, integrations, or features. This is critical for AI-assisted development.
- **Tech stack table**: component → technology mapping at the top of the overview.

---

## Formatting Conventions

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

## CHANGELOG.md Format

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

## Writing Style Guide

1. **Be direct**: use imperative mood for instructions ("Run the command", "Edit the file"). No hedging.
2. **Show, don't explain**: a code example is worth a paragraph of prose. When in doubt, add a code block.
3. **Keep prose minimal**: use sentences for context, tables for data, code blocks for commands.
4. **Use consistent terminology**: pick one term for each concept and stick with it throughout all docs.
5. **Document the "why" alongside the "what"**: for non-obvious decisions, add a brief explanation (e.g., "We use Camoufox because standard Playwright gets detected by anti-bot systems").
6. **Include real examples**: use realistic values, not `foo`/`bar`. Show actual API payloads, real config values, concrete use cases.
7. **Warn about footguns**: use bold + warning indicator for dangerous operations (e.g., `**Warning**: This deletes all data`).

---

## When Creating Documentation

1. **Read the codebase first**: understand the project structure, entry points, configuration, and dependencies before writing anything.
2. **Start with README.md**: if it doesn't exist, create it. If it exists, update it to match the skeleton above.
3. **Create docs/SETUP.md** when the project requires more than 5 commands to set up.
4. **Create docs/TECHNICAL.md** when the project has non-trivial architecture (multiple services, complex data flows, extension points).
5. **Update CHANGELOG.md** when making significant changes — follow the semantic-release format.
6. **Never invent features**: only document what actually exists in the code. Read before you write.

## When Updating Documentation

1. **Keep existing structure**: don't reorganize docs unless asked. Add to the existing skeleton.
2. **Update, don't duplicate**: if information exists in one place, update it there. Don't create parallel docs.
3. **Reflect code changes**: when code changes (new endpoints, new env vars, new modules), update the corresponding doc sections.
4. **Preserve the project's voice**: if docs are in Portuguese, keep them in Portuguese. If English, keep English. Match the existing tone.

---

## Troubleshooting

**Problem**: Only README.md was updated, SETUP.md and TECHNICAL.md were not created.
**Solution**: This skill always creates all three tiers. Re-run with: "Document this project following the documentation skill — create README.md, docs/SETUP.md, and docs/TECHNICAL.md."

**Problem**: Documentation describes features that don't exist in the code.
**Solution**: Always read the codebase before writing. Run `find . -type f` and read key files before starting.

**Problem**: Setup guide is missing expected output for commands.
**Solution**: Every command block must show what success looks like with a comment like `# Expected: ...`

---

## How to Use

### Prompt

Open your project in Claude Code and paste this prompt:

```
Document this project following the documentation skill.
Analyze the codebase and create all documentation files this project needs.
```

---

## Trigger Test Cases

Should trigger on:
- "Document this project"
- "Write the docs for this codebase"
- "Update the README"
- "Create setup and technical documentation"
- "Help someone understand this project"
- "Document this for AI tools"

Should NOT trigger on:
- "Write a blog post"
- "Create a presentation"
- "Fix this bug"
- "Review my code"
