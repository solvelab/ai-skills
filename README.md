<div align="center">

  # 🧠 AI Skills

  **Personal collection of reusable AI skills and conventions for coding assistants.**

  [![Claude Code](https://img.shields.io/badge/Claude_Code-supported-8A2BE2?logo=anthropic&logoColor=white)](https://claude.ai)
  [![OpenAI Codex](https://img.shields.io/badge/OpenAI_Codex-supported-412991?logo=openai&logoColor=white)](https://openai.com)
  [![Cursor](https://img.shields.io/badge/Cursor-supported-000000?logo=cursor&logoColor=white)](https://cursor.com)
  [![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-supported-24292e?logo=github&logoColor=white)](https://github.com/features/copilot)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)]()
  [![Version](https://img.shields.io/github/v/tag/solvelab/ai-skills?label=version&color=blue)](CHANGELOG.md)
  [![Install](https://img.shields.io/badge/install-npx%20skills-brightgreen?logo=npm&logoColor=white)](#-install)

</div>

Each skill is an instruction file that teaches an AI tool how to perform a specific type of task — like writing documentation, creating commits, or following code conventions.

Supports **Claude Code**, **OpenAI Codex**, **Cursor**, and **GitHub Copilot** from a single source of truth — no duplication.

---

## 🚀 Install

Skills follow the open [Agent Skills](https://github.com/vercel-labs/skills) standard (`skills/<name>/SKILL.md`), so every mainstream install path works.

### Option A — `npx skills` (recommended, works with 70+ agents)

```bash
# Interactive: pick skills and agents
npx skills add solvelab/ai-skills

# Everything, for every detected agent
npx skills add solvelab/ai-skills --all

# Specific skills / specific agents
npx skills add solvelab/ai-skills --skill documentation -a claude-code -a cursor

# Global (user-wide) instead of per-project
npx skills add solvelab/ai-skills --all -g

# Just look at what's available
npx skills add solvelab/ai-skills --list
```

The CLI detects your installed agents (Claude Code, Codex, Cursor, Copilot, and many more) and routes each skill to the right directory.

### Option B — Claude Code plugin marketplace

The marketplace ships **per-domain plugins** so a project enables only coherent sets —
`ai-skills-workflow` (commits + OpenSpec), `ai-skills-backend`, `ai-skills-testing`,
`ai-skills-fivem`, `ai-skills-nui` (NUI React/CEF), `ai-skills-frontend` (SPA API client),
`ai-skills-game` (R3F + AssettoServer), `ai-skills-devops`, `ai-skills-docs`,
`ai-skills-tooling` (Claude Code status line) — plus the full
`ai-skills` bundle for whoever really wants all 28.

**B1 — manual**, inside Claude Code:

```
/plugin marketplace add solvelab/ai-skills
/plugin install ai-skills-backend@ai-skills     # or ai-skills-fivem, ai-skills-game, ...
```

**B2 — project auto-install (team distribution)** — commit a `.claude/settings.json` in your
project; anyone opening the repo gets prompted to install the plugin automatically (trust dialog →
one accept, zero manual steps):

```json
{
  "extraKnownMarketplaces": {
    "ai-skills": { "source": { "source": "github", "repo": "solvelab/ai-skills" } }
  },
  "enabledPlugins": {
    "ai-skills-workflow@ai-skills": true,
    "ai-skills-backend@ai-skills": true,
    "ai-skills-testing@ai-skills": true
  }
}
```

Pick the groups that match the project (a FiveM repo takes `ai-skills-fivem`, an R3F game takes
`ai-skills-game`, ...) — dumping all 29 skills into every project is noise, not help.

**B3 — user-level (whole machine)** — same snippet in `~/.claude/settings.json` enables the plugin
for every project on the machine.

Plugin updates are **version-pinned**: you only receive changes when a new release is tagged (see
[Releases & Versioning](#-releases--versioning)).

> **Pick ONE method per machine.** Plugin skills are namespaced (`ai-skills:fivem-lua`) and don't
> conflict with the symlink install (Option C) — but running both duplicates every skill in
> discovery. On a machine using symlinks, disable a project's auto-install locally with
> `.claude/settings.local.json` setting the same plugin keys to `false`.

### Option C — One-line terminal install

```bash
# Claude Code (default) — symlinks skills into ~/.claude/skills/
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash

# OpenAI Codex
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash -s -- --tool codex

# All tools
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash -s -- --tool all
```

This clones the repo into `~/ai-skills` and, for Claude Code, symlinks each skill into `~/.claude/skills/` (native discovery — no config edits). Use `--legacy` for the old `~/.claude/CLAUDE.md` block instead.

### Option D — Manual install

```bash
# 1. Clone the repository
git clone https://github.com/solvelab/ai-skills.git ~/ai-skills

# 2. Configure your tool (choose one):

# Claude Code — symlink skills for native discovery
mkdir -p ~/.claude/skills
for s in ~/ai-skills/skills/*/; do ln -sfn "${s%/}" ~/.claude/skills/"$(basename "$s")"; done

# OpenAI Codex — add to ~/.codex/AGENTS.md
echo '
# AI Skills

Skills are located at ~/ai-skills/codex/skills/.
Each skill has an AGENTS.md file with instructions for specific tasks.
' >> ~/.codex/AGENTS.md

# Cursor — copy inline rules into your project
cp ~/ai-skills/cursor/rules/*.mdc /path/to/project/.cursor/rules/

# GitHub Copilot — copy instruction files
cp ~/ai-skills/copilot/instructions/*.instructions.md /path/to/project/.github/instructions/
```

---

## ♻️ Update

Pull the latest skills/rules into `~/ai-skills` and regenerate the Cursor wrappers:

```bash
# One-line (no clone needed)
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/update.sh | bash

# Or, if already cloned
cd ~/ai-skills && ./update.sh

# Force-sync, discarding any local changes in ~/ai-skills
cd ~/ai-skills && ./update.sh --force
```

`install.sh` also pulls on re-run, but `update.sh` is the dedicated path: fast-forward sync (or `--force` hard-reset), then regenerates all tool wrappers from `skills/`. Claude Code symlinks point into the repo, so a pull is all it takes.

Installed via the **Claude Code plugin**? Update with `/plugin marketplace update ai-skills` — you'll receive changes when a new version is released. Installed via **npx skills**? Re-run `npx skills add solvelab/ai-skills`.

> Global rules (`~/.claude/CLAUDE.md` `@`-includes) load at **session start** — restart your AI tool after updating to apply new rules.

---

## 🔖 Releases & Versioning

Releases are **fully automated** by [semantic-release](https://github.com/semantic-release/semantic-release): every push to `master` runs `.github/workflows/ci.yml`, which analyzes the [Conventional Commits](https://www.conventionalcommits.org) since the last tag and, when warranted, cuts a release — no manual steps.

| Commit type | Release |
|-------------|---------|
| `feat:`, `skill:` | minor |
| `fix:`, `refactor:` | patch |
| `BREAKING CHANGE:` footer or `!` | major |
| `docs:`, `chore:` | none |

Each release automatically: bumps `VERSION`, propagates it to `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (via `scripts/set-version.sh`), regenerates all wrappers, updates `CHANGELOG.md` from the commit messages, commits (`chore(release): vX.Y.Z [skip ci]`), tags `vX.Y.Z`, and publishes a GitHub Release with the notes.

| Channel | What you get |
|---------|--------------|
| Claude Code plugin | **Version-pinned** — updates only when `plugin.json` version is bumped by a release |
| `npx skills` / `install.sh` / `update.sh` | Latest `master` |

Each skill also carries its own `metadata.version` in its `SKILL.md` frontmatter — bump it when that skill's behavior changes. Repo version = the collection; skill version = the individual contract. The CI/CD pipeline (`.github/workflows/ci.yml`) validates every push/PR (wrapper sync, version coherence, frontmatter) and cuts releases on `master`.

---

## 🔧 Global Personal Rules (optional, Claude Code only)

Beyond skills — which trigger per task — Claude Code also loads a **global rules file** (`~/.claude/CLAUDE.md`) that applies to every conversation. This repo ships an example at `claude/global/personal-rules.md` showing how to keep those rules portable across machines.

> **Note:** `personal-rules.md` contains the **repo maintainer's personal config** (collaboration style, commit conventions). Fork and edit to match your own preferences — do not adopt the defaults blindly.

### How it works

1. Rules live in `claude/global/personal-rules.md` (versioned in this repo).
2. On each machine, `~/.claude/CLAUDE.md` references the file with the `@` directive instead of duplicating its contents:

   ```markdown
   # Global Rules

   @~/ai-skills/claude/global/personal-rules.md
   ```

3. Edit once → `git push` → `git pull` on every other machine. Rules propagate.

### Setup on a new machine

```bash
# 1. Clone this repo (if not already)
git clone https://github.com/solvelab/ai-skills.git ~/ai-skills

# 2. Reference the rules file from your global Claude Code config
mkdir -p ~/.claude
cat >> ~/.claude/CLAUDE.md <<'EOF'
@~/ai-skills/claude/global/personal-rules.md
EOF
```

To customize: edit `~/ai-skills/claude/global/personal-rules.md` (or fork the repo).

---

## 📁 Repository Structure

```
ai-skills/
├── skills/                                   # ★ Canonical skills (single source of truth)
│   ├── api-resilience-testing/
│   │   ├── SKILL.md                          # Frontmatter + full instructions (self-contained)
│   │   └── references/
│   │       └── negative-test-catalog.md      # Concrete negative-test examples
│   ├── documentation/
│   │   ├── SKILL.md
│   │   └── references/examples.md
│   ├── helm-migration/
│   │   ├── SKILL.md
│   │   └── references/examples.md
│   ├── bug-hunter/SKILL.md
│   ├── fivem-lua/SKILL.md
│   ├── fivem-fallback/SKILL.md
│   └── r3f-*/SKILL.md                        # React Three Fiber skills (10 topics)
├── .claude-plugin/
│   ├── plugin.json                           # Claude Code plugin manifest (version-pinned)
│   └── marketplace.json                      # Claude Code marketplace catalog
├── claude/
│   ├── global/personal-rules.md              # Maintainer's portable Claude Code rules (example)
│   └── skills/                               # Generated: thin wrappers for legacy CLAUDE.md installs
├── codex/
│   ├── AGENTS.md                             # Codex global index
│   └── skills/                               # Generated: @-include wrappers
├── cursor/rules/                             # Generated: .mdc rules with content inlined
├── copilot/instructions/                     # Generated: .instructions.md link wrappers
├── shared/conventions/                       # Cross-tool coding standards
├── VERSION                                   # Single source of truth for the collection version
├── CHANGELOG.md                              # Keep a Changelog format
├── generate.sh                               # Regenerates all tool wrappers from skills/
├── install.sh                                # One-line installer with --tool flag
├── update.sh                                 # Sync + regenerate
├── scripts/set-version.sh                    # Version propagation (called by semantic-release)
├── .releaserc.json                           # semantic-release config (auto-versioning from commits)
└── README.md
```

| Folder | Purpose |
|--------|---------|
| `skills/` | **Canonical skills** — self-contained `SKILL.md` per skill, open Agent Skills standard. Edit here. |
| `.claude-plugin/` | Claude Code plugin + marketplace manifests |
| `claude/global/` | Portable global rules for Claude Code, `@`-included from `~/.claude/CLAUDE.md` |
| `claude/skills/` | Generated wrappers for legacy `~/.claude/CLAUDE.md` installs |
| `codex/skills/` | Generated OpenAI Codex wrappers using `@./path` file includes |
| `cursor/rules/` | Generated Cursor .mdc rules with content inlined |
| `copilot/instructions/` | Generated GitHub Copilot wrappers with markdown link references |
| `shared/conventions/` | Coding standards shared across all tools |

---

## 🔀 Multi-Tool Architecture

The canonical skill lives in `skills/<name>/SKILL.md` — a **self-contained** file following the open [Agent Skills](https://github.com/vercel-labs/skills) standard (YAML frontmatter + full instructions + optional `references/`). Because it's self-contained, `npx skills`, the Claude Code plugin, and plain directory copies all work without this repo being present at a fixed path.

`generate.sh` derives all tool-specific wrappers from it:

```
skills/documentation/SKILL.md    ← ★ Single source of truth (self-contained)
        │
        ├── (used directly)  npx skills add · Claude Code plugin · ~/.claude/skills/ symlinks
        ├── claude/skills/documentation/SKILL.md        ← generated: frontmatter + "Read skills/…"
        ├── codex/skills/documentation/AGENTS.md         ← generated: @../../skills/…/SKILL.md
        ├── cursor/rules/documentation.mdc               ← generated: content inlined
        └── copilot/instructions/documentation.instructions.md  ← generated: markdown link
```

| Tool | Consumes | Mechanism |
|------|----------|-----------|
| **Any of 70+ agents** | `skills/<name>/` | `npx skills add solvelab/ai-skills` |
| **Claude Code** | `skills/<name>/` | Plugin marketplace, or symlinks in `~/.claude/skills/` |
| **OpenAI Codex** | `codex/skills/<name>/AGENTS.md` | `@./path` native include |
| **Cursor** | `cursor/rules/<name>.mdc` | Content inlined (no include support) |
| **GitHub Copilot** | `copilot/instructions/<name>.instructions.md` | Markdown link reference |

---

## 🧩 How Skills Work

### What is a skill?

A skill is a markdown instruction file that an AI reads before performing a task. It contains patterns, rules, and examples that guide the AI to produce consistent, high-quality output.

Think of skills as reusable expertise — instead of explaining your documentation style every time, you write it once and every AI tool follows it automatically.

### How each tool discovers skills

| Tool | Discovery mechanism |
|------|-------------------|
| **Claude Code** | Natively discovers `SKILL.md` folders in `~/.claude/skills/`, `.claude/skills/`, and installed plugins. Matches skills to tasks using the YAML `description` field. |
| **OpenAI Codex** | Reads `AGENTS.md` files from configured paths and walks the directory tree. Follows `@./path` includes automatically. |
| **Cursor** | Reads `.mdc` files from `.cursor/rules/` in the project directory. Applies rules based on YAML `globs` or `alwaysApply` settings. |
| **GitHub Copilot** | Reads `.instructions.md` files from `.github/instructions/`. Follows markdown link references to external files. |

---

## 📦 Skills Available

### Backend & testing

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **python-rest-api** | creating/reviewing a Python API, FastAPI service, response envelope, project layout | Production conventions distilled from real solvelab services — layering, error envelope + code registry, never-raw-500 handlers, tenant isolation, service-token catalog, domain-state idempotency, testing stack (golden OpenAPI, fuzz gate) |
| **backend-resilience** | external call, timeout, 5xx, dependency down, config fetch, retry, fallback, negative cache | Stack-agnostic resilience doctrine — safe defaults, shared fallback helper, response-shape validation, clamping, bounded retries, negative caching, in-flight dedupe (Python examples) |
| **api-resilience-testing** | "test/harden/break/audit/review the API", "negative testing", "fuzz", "API robustness", "API security", invalid payloads, status codes, auth, OpenAPI | Tests REST APIs beyond the happy path (negative/fuzz/contract/security); produces an endpoint map, scenarios, suggested tests and a resilience checklist |
| **bug-hunter** | "bug hunt", "adversarial test", break it, anti-forge, edge cases of a change | Per-change adversarial testing rite — universal checklist + opt-in stack tracks (Python/pytest, FiveM/Lua, .NET plugin) |
| **log-event-collector** | log tailer, log-to-event parser, file offset, log rotation, event dedup/idempotency, shutdown flush | Doctrine for a log-tailing collector sidecar — byte-offset persistence with rotation guard, atomic state, deterministic event keys, multi-line correlation, exactly-once shutdown flush, golden log fixture |

### FiveM

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **fivem-lua** | RegisterNetEvent, RegisterNUICallback, fxmanifest, exports, NUI, CreateThread, StateBags, natives | CitizenFX Lua conventions — client-never-trusted boundary, explicit fxmanifest order, no busy loops, module-per-global, NUI focus/cleanup |
| **fivem-fallback** | FiveM resource calling backend/Consul/another resource, config fetch, retry in Lua | FiveM/Lua adaptation of backend-resilience — SafeCall/clampNum, boot retry, NUI error signaling |

### AssettoServer

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **assettoserver-plugin** | AssettoServer plugin, AssettoServerModule, Qmmands/ACModuleBase, ChatMessage packet, plugin YAML config, plugin publish | C#/.NET plugin survival guide for the AssettoServer runtime — two-contract version pinning, disabled-by-default YAML config, forbidden runtime constructs + static accessor bridge, curl dual-transport backend calls, Mono.Cecil bug-hunter gate |
| **assettoserver-ops** | server_cfg.ini, entry_list.ini, extra_cfg.yml, checksum mismatch, AI traffic, WSL2 ports, plugin deploy | Operating an AssettoServer dedicated AC server — config anatomy, checksum/CSP troubleshooting, AI-traffic enablement discipline, Docker/WSL2 orchestration, rite-gated plugin sync |
| **assettoserver-csp-lua** | CSP online script, in-game overlay/HUD/toast, transparentWindow, DirectWrite/dwriteText, ac.OnlineEvent, sound in game, empty box / glued text / packet never arrives | The client-side Lua layer served by the server — single-window draw-list doctrine, DirectWrite trap table, byte-parity OnlineEvent packets, remote images/audio by URL (zero-install), mockup-first workflow and probes |

### Frontend

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **fivem-nui-react** | NUI, CEF, SendNUIMessage/useNUIEvent, ui_page, tokens.css | FiveM/RedM NUI React conventions — Lua↔React bridge (multiplexed callback, uiReady handshake, invisible-by-default), Vite-for-CEF build, CEF rendering quirks, tokens design-system law, browser dev-mode |
| **react-api-client** | React SPA calling a REST API, axios client, auth store, error codes | Typed-envelope client discipline — ErrorCodes + ApiException, zod parsers that throw on drift, tokens-only auth persistence with single-flight refresh, realtime polling facade, dedup nonce on paid mutations |

### Process & git

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **openspec** | OpenSpec, /opsx, proposal, spec delta, change-id | Vanilla OpenSpec spec-driven workflow (explore → propose → validate → apply → archive) |
| **openspec-drivezone** | the DriveZone "rito", forked schema | DriveZone forked-schema variant — mandatory Fallback / Tests & Bug-Hunter / Validation gates |
| **conventional-commit** | creating/amending commits, commit messages, /commit, opening/editing PRs | Conventional Commits + gitmoji icon per type; forbids AI attribution in commits & PRs |
| **backlog** | /backlog <idea>, "create a backlog item", "turn this idea into an issue" | Turns a natural-language idea into a context-rich GitHub issue placed in a Project v2 with fields set — repo & multi-repo workspace modes, first-run config wizard, preview before creation |

### DevOps & docs

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **documentation** | README, SETUP, TECHNICAL, CHANGELOG, "document this", "write the docs" | Analyzes the project first, then creates the documentation set the project actually needs |
| **helm-migration** | "migrate to helm", "convert yaml to helm", "generate values.yaml" | Converts K8s YAML to Helm values.yaml/env.yaml — **requires the solvelab chart template repository** |

### Tooling

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **claude-statusline** | "configure my Claude Code status line", statusLine in settings.json, statusline.sh, "add context/cost/git to my statusline", install a statusline gist | Sets up or customizes the Claude Code status bar — ships a ready-made 4-line script (model/context/git/cost/rate-limits/cache) plus the full JSON-field reference; safe install, custom-build rules, and gist sharing |

### Game (React Three Fiber — 10 topics)

| Skill | Covers |
|-------|--------|
| **r3f-fundamentals** | Canvas, useFrame/useThree, JSX elements, events, refs, extend, Leva |
| **r3f-animation** | useFrame motion, useAnimations, springs, morph/skeletal, procedural walk/jump cycles, zustand perf |
| **r3f-assets** | Model loading (useGLTF, Draco, gltfjsx), textures (useTexture, colorSpace, FBO), Suspense/preload |
| **r3f-geometry** | Built-in/custom BufferGeometry, instancing, Points/Lines, Text3D |
| **r3f-interaction** | Pointer events, camera controls, drag/gestures, KeyboardControls, screen↔world |
| **r3f-lighting** | Light types/cost, shadows, Environment/IBL/HDR (canonical home), lighting recipes |
| **r3f-materials** | Material comparison, PBR props, Drei special materials, multi-material |
| **r3f-physics** | Rapier — RigidBody, colliders, forces, joints, sensors, instanced physics |
| **r3f-postprocessing** | EffectComposer, Bloom, DOF, SSAO/N8AO, Outline/selection, custom effects |
| **r3f-shaders** | shaderMaterial + HMR, uniforms, GLSL snippets (noise/fresnel/dissolve), onBeforeCompile |

### api-resilience-testing

**Skill**: `skills/api-resilience-testing/SKILL.md`
**Reference**: `skills/api-resilience-testing/references/negative-test-catalog.md`

Tests REST/HTTP APIs **beyond the happy path** — negative, fuzz, contract, and security testing — to catch invalid, malformed, out-of-contract, or hostile inputs before they reach production. Triggers automatically when adding/changing an endpoint, reviewing an API PR, writing API tests, or designing request/response schemas.

Use any of these phrases to trigger it:

- `Test this API for resilience`
- `Run negative testing on these endpoints`
- `Try to break this API / audit the API`
- `Review this API PR for validation and security gaps`

**The skill runs a 10-step workflow:** map endpoints → capture contracts → design positive + negative scenarios → try to break it → validate status codes → validate safe error responses → verify auth/authz (incl. BOLA/IDOR & mass assignment) → hunt critical bugs (500s, partial writes, retry duplicates) → suggest automated tests → produce a resilience checklist.

| Covers | Examples |
|---|---|
| Input validation | missing/null/empty fields, wrong types, out-of-range, malformed JSON, oversized payloads |
| Headers & content | missing/wrong `Content-Type`, unsupported `Accept` |
| Auth & authorization | missing/expired/tampered tokens, forbidden roles, BOLA/IDOR, mass assignment |
| Status & errors | input errors are 4xx not 5xx; RFC 9457 error shape; no stack-trace/SQL/path leakage |
| State & contract | no partial write on failure, retry idempotency, OpenAPI conformance |

#### How to verify the skill was used

After running the prompt, check that:
- [ ] The AI mapped every endpoint with its request/response contract first
- [ ] Both positive **and** negative scenarios were produced (not just happy path)
- [ ] Each negative case asserts a status code **and** a safe error body
- [ ] Auth/authz cases include BOLA/IDOR and mass assignment
- [ ] A filled resilience checklist with flagged gaps was produced

### documentation

**Skill**: `skills/documentation/SKILL.md`

Use any of these phrases to trigger the documentation skill:

- `Document this project`
- `Write the docs for this codebase`
- `Update the README`
- `Create the project documentation`

**The skill analyzes your project first and decides which documents to create.** It doesn't always create the same files — it creates what your project actually needs.

| Project type | Documents typically created |
|---|---|
| Simple API | `README.md`, `docs/SETUP.md`, `docs/TECHNICAL.md`, `docs/API.md` |
| Discord bot | `README.md`, `docs/SETUP.md`, `docs/TECHNICAL.md` |
| ML pipeline | `README.md`, `docs/SETUP.md`, `docs/PIPELINE.md`, `docs/MODEL.md` |
| CLI tool | `README.md`, `docs/SETUP.md`, `docs/CLI.md` |
| Open source library | `README.md`, `docs/SETUP.md`, `docs/SDK.md`, `CONTRIBUTING.md`, `CHANGELOG.md` |
| Microservices | `README.md`, `docs/SETUP.md`, `docs/TECHNICAL.md`, `docs/DEPLOYMENT.md`, `docs/EVENTS.md` |

#### Testing the skill

Open your project in your AI tool and use the appropriate prompt:

```
Document this project following the documentation skill.
Analyze the codebase and create all documentation files this project needs.
```

Watch for these signs that the skill is working:
- The AI reads the codebase **before** writing anything
- Lists which documents it will create based on the project type
- More than just `README.md` is created depending on the project

#### How to verify the skill was used

After running the prompt, check that:
- [ ] The AI scanned the codebase before writing anything
- [ ] `README.md` has a centered header with badges
- [ ] All relevant docs were created based on what the project actually is
- [ ] No generic or empty documents were created

### helm-migration

**Skill**: `skills/helm-migration/SKILL.md`

Converts Kubernetes YAML manifest files to Helm chart files following your chart template structure. Generates two files per migration:

| File | Contents |
|------|---------|
| `values.yaml` | Workload definition — deployment, daemonset, containers, ports, probes, resources |
| `env.yaml` | Environment resources — secrets, configmaps, PVCs |

Use any of these phrases to trigger the helm-migration skill:

- `Migrate this YAML to Helm`
- `Convert this YAML to values.yaml`
- `Generate values.yaml for this manifest`
- `Helm migration`

For best results, use this prompt:
```
Migrate this YAML-file to Helm following the helm-migration skill.
Charts template path: [PATH_TO_CHARTS_TEMPLATE]
Source YAML-file: [PATH_TO_YAML_FILE]
Save files to: [DESTINATION_PATH]
```

**What the skill always does:**
- Reads your charts template structure before generating anything
- Removes `tolerations` from all generated files — no exceptions
- Adds explanatory comments to every section
- Generates `env.yaml` only when secrets, configmaps or PVCs are present
- Preserves `secretKeyRef` references in `values.yaml` and creates empty secret entries in `env.yaml` with a warning to fill in values

#### How to verify the skill was used

After running the prompt, check that:
- [ ] The AI read the charts template before generating files
- [ ] `values.yaml` follows your chart template structure exactly
- [ ] `env.yaml` was created if secrets/configmaps/PVCs were present
- [ ] No `tolerations` appear in any generated file
- [ ] All sections have explanatory comments

---

## ➕ How to Add a New Skill

### 1. Create the canonical skill

```bash
mkdir -p skills/<skill-name>
```

Create `skills/<skill-name>/SKILL.md` — frontmatter + the full instructions in one self-contained file:

```yaml
---
name: my-skill
description: Use this skill when the user asks to [describe the task].
  Triggers include [list keywords and phrases that should activate this skill].
metadata:
  version: 1.0.0
license: MIT
---

[Full skill instructions here — patterns, rules, templates, examples.]
```

- `name` must match the directory name (CI enforces this).
- Put supporting material in `skills/<skill-name>/references/` and point to it with **relative paths** (`references/examples.md`) — never absolute paths, so the skill stays portable.
- Bump `metadata.version` whenever the skill's behavior changes.

### 2. Generate the tool wrappers

```bash
./generate.sh
```

This emits the Claude/Codex/Cursor/Copilot wrappers automatically. Commit them together with the skill — CI fails if they're out of sync.

### 3. Release

Commit with a [Conventional Commit](https://www.conventionalcommits.org) message and push — the release pipeline does the rest (version bump, changelog, tag, GitHub Release):

```bash
git commit -m "skill: add my-skill"   # skill:/feat: → minor release on push to master
git push origin master
```

### 4. Key guidelines for writing skills

| Guideline | Why |
|-----------|-----|
| Base on real examples | Skills derived from actual code/docs are more useful than generic templates |
| Be specific, not vague | "Use tables for env vars" is better than "format things nicely" |
| Include structure templates | Show the exact skeleton the AI should follow |
| State rules as imperatives | "Always include a troubleshooting section" not "it would be nice to have troubleshooting" |
| Keep it focused | One skill per task type. Don't combine "documentation" and "commit messages" |

---

## 🤝 Shared Conventions

The `shared/conventions/` folder is for coding standards and patterns that apply across all AI tools. Place files here when the same convention should be followed regardless of which tool is being used.

Examples of what belongs here:
- Code style guides (naming, formatting, error handling)
- Git conventions (commit messages, branch naming)
- Architecture patterns (folder structure, layering rules)
- API design standards (naming, versioning, error responses)

Reference shared conventions from tool-specific skills when needed:

```markdown
Follow the conventions defined in shared/conventions/api-design.md.
```

---

## 🛠️ Built with

| Tool | Purpose |
|------|---------|
| [Claude Code](https://claude.ai) | AI coding assistant |
| [OpenAI Codex](https://openai.com) | AI coding assistant |
| [Cursor](https://cursor.com) | AI-powered IDE |
| [GitHub Copilot](https://github.com/features/copilot) | AI coding assistant |
| [Bash](https://www.gnu.org/software/bash/) | Install and generate scripts |

---

## 📄 License

MIT
