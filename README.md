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
`ai-skills` bundle for whoever really wants all 35.

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
`ai-skills-game`, ...) — dumping all 35 skills into every project is noise, not help.

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

### Enforcing the rite (optional hook)

The rules file states that every code change starts as a backlog item ([`backlog`](skills/backlog/) →
[`execute-backlog`](skills/execute-backlog/)). A rule in context only works if the assistant notices
it — and the failure mode is specific: a request to *diagnose* something drifts into implementing the
fix, and no new prompt ever arrives to trigger the rite.

`claude/global/hooks/backlog-rite.py` closes that gap. It is a `UserPromptSubmit` hook: the harness
runs it on every prompt, and its output becomes context for that turn. It **informs, never blocks** —
no tool call is denied, and the user can waive the rite explicitly.

Where the working directory carries `openspec/`, the reminder gains one extra sentence naming the
spec gate: the item also becomes an OpenSpec change, validated strict before the first edit outside
`openspec/`. The sentence is conditional on purpose — it never fires in a repo that has no such
workflow, so the reminder does not teach a step that does not exist there.

```jsonc
// ~/.claude/settings.json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/YOUR_USER/ai-skills/claude/global/hooks/backlog-rite.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "python3 /home/YOUR_USER/ai-skills/claude/global/hooks/verify-rite.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

It stays silent for prompts already inside the rite (`/backlog`, `/execute-backlog`, any slash
command), for explicit waivers ("sem backlog", "skip the rite"), and for anything that does not look
like a code change. It persists nothing and needs no credentials. A diagnostic question that
contains a change word — `erro`, `bug`, `falha`/`fail` ("por que o teste falha?") — does fire, on
purpose: the matcher is deliberately generous because a false positive costs one line of context
while a false negative costs traceability, the reminder itself says diagnosis is free, and the hook's
`--selftest` fixes that case as one that fires so a well-meant "fix" cannot revert it unread.

### The grounding rite (anti-achismo)

`claude/global/hooks/verify-rite.py` is the second hook in the array above. It carries the
[`verify-before-claiming`](skills/verify-before-claiming/) doctrine into context when a prompt reads
as **a guess being caught or research being demanded** — "achismo", "você inventou", "de onde
tirou", "essa flag não existe", "fora do escopo", "don't guess", "cite the source", "that's not what
I asked". Same contract as the backlog hook: informs, never blocks, silent on explicit waivers
("de cabeça", "pode chutar", "from memory is fine").

**What it deliberately does not do.** It fires on *corrections*, not on the guess itself. The moment
worth intercepting is internal to the model — "I am about to write a flag I have not read" — and no
prompt regex can see it. A per-turn preventive matcher was rejected because every plausible signal
list (library, API, flag, version) matches most technical prompts, and a reminder that fires on
every prompt stops being read, which would also degrade the backlog reminder next to it. Preventive
coverage lives in `personal-rules.md` instead, which loads once per session.

**Where enforcement actually happens.** This hook runs in the maintainer's own Claude Code sessions.
It does **not** run in CI, and it does not run for a contributor who clones this repo without wiring
it — it cannot enforce anything on a pull request. The gate that survives an unwired contributor is
`scripts/validate-rite.sh`, which refuses any active OpenSpec change whose `tasks.md` does not open
with an `Evidence & Sources (MANDATORY)` group. The hook makes the guess less likely; CI makes the
missing evidence visible.

### The locale rite (English machine layer, measured at the write)

`claude/global/hooks/locale-rite.py` is the third hook, and the only one that measures an artifact
instead of matching a prompt. It runs on `PostToolUse` for `Write|Edit`, feeds the written **path**
and the written **content** to [`check-identifier-locale.py`](skills/code-locale/references/check-identifier-locale.py),
and returns the findings to the assistant. Silent when the write is clean.

```jsonc
// ~/.claude/settings.json — alongside the UserPromptSubmit block above
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/YOUR_USER/ai-skills/claude/global/hooks/locale-rite.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Why a different event.** The other two rites match a prompt, so a reminder is the best they can do.
This one has the artifact in hand — the name that was just written — so it measures instead of
reminding. The findings travel in `hookSpecificOutput.additionalContext`, not on plain stdout:
`PostToolUse` is not one of the events that turn stdout into context (`UserPromptSubmit`,
`UserPromptExpansion`, `SessionStart` are), so a hook that printed would be silently useless.

Same contract as the other two: informs, never blocks, persists nothing, needs no credentials — and
where the check itself is missing it exits silently instead of failing, because an absent gate must
not present itself as an error.

> Like `personal-rules.md`, this is the **maintainer's** process. Edit the signal lists and the
> reminder text to match yours — both matchers cover Portuguese and English by default.

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

## 🗂️ Backlog Automation Quickstart (`/backlog` + `/execute-backlog`)

Turn ideas into GitHub Project items and drive them to merged PRs, from any repo or multi-repo
workspace. One-time setup per machine:

```bash
# 1. Install the skills (any install option works; quickest:)
npx skills add solvelab/ai-skills --skill backlog --skill execute-backlog -g

# 2. GitHub CLI authenticated WITH Projects scopes (once per machine)
gh auth login                                   # if not logged in yet
gh auth refresh -s project,read:project        # Projects v2 requires these extra scopes
```

Then, per project (first run only — a wizard writes the config):

```bash
cd ~/work/my-repo          # or a workspace folder containing several repos of one org
claude
> /backlog add social login authentication
# wizard: detects the org from git remotes → you pick the Project → fields mapped →
# writes .github/backlog.yml (repo mode) or backlog.yml (workspace mode) → commit it
# so every teammate inherits the setup on clone.
```

Daily flow:

| Command | What happens |
|---|---|
| `/backlog <idea>` | analyzes the repo for real context → drafts a structured issue → **preview for approval** → creates the issue + adds it to the Project with fields set (card in **Backlog**) |
| `/execute-backlog <n>` | reads the issue → completeness gate (card → **Ready**) → spec gate where the repo runs one → implementation plan for approval (card → **In progress**) → implements on `backlog/<n>-<slug>` following the repo's own rites → tests + validations → PR with `Closes #n` (card → **In review**) — never merges, never closes issues |
| you merge the PR | issue auto-closes; the board's built-in *Item closed → Done* workflow moves the card to **Done** |

**In a repo that runs a spec-driven workflow** (an `openspec/` directory), the two commands carry a
third gate between them. `/backlog` records the verdict in the item — the change that will register
the work, or a waiver written as a line with a reason — and `/execute-backlog` re-checks that verdict
against the real change surface, creates the change, and validates it strict **before** editing
anything outside `openspec/`. Raising a verdict needs no permission; lowering one stops for the user.
The policy is the repo's, in the `spec_rite` key of the backlog config; a repo that carries the
workflow and states no policy is treated as requiring the change. Protocol:
[`spec-rite.md`](skills/execute-backlog/references/spec-rite.md).

Requirements: `gh` ≥ 2.40 with the scopes above, write access to the target repos, and a GitHub
Project v2 in the org/user. Full details live in the skills themselves:
[`skills/backlog/`](skills/backlog/SKILL.md) · [`skills/execute-backlog/`](skills/execute-backlog/SKILL.md).

---

## 📦 Skills Available

> Counts in this README and in the plugin manifests are hand-written and therefore drift. The
> authority is the tree: `ls skills | wc -l`. If a number here disagrees with that command, the
> command is right — fix the number in the same change that noticed it.

### Backend & testing

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **python-rest-api** | creating/reviewing a Python API, FastAPI service, response envelope, project layout, request size/depth limits | Production conventions distilled from real solvelab services — layering, error envelope + code registry, never-raw-500 handlers, request limits (measured: 2 KB nested body → 500, 20 MB body → 200 without them), tenant isolation, service-token catalog, domain-state idempotency, testing stack (golden OpenAPI, fuzz gate) |
| **observability** | logging, metrics, tracing, `/metrics`, request-id / correlation middleware, "why was the outage invisible", health that reports degraded | Correlation, RED metrics and tracing for a backend service — one request id bound to every log line and propagated outward, route templates as labels (never raw paths or client-controlled values), the registry the fallback counter lives in, and when OpenTelemetry earns its cost |
| **backend-resilience** | external call, timeout, deadline, 5xx, dependency down, config fetch, retry, backoff, jitter, fallback, negative cache | Stack-agnostic resilience doctrine, ordered timeout → deadline → bounded retry → negative cache + single-flight → fallback → surface — idempotent-only retries with jittered backoff, response-shape validation, clamping, observable degradation (Python examples) |
| **api-resilience-testing** | "test/harden/break/audit/review the API", "negative testing", "fuzz", "API robustness", "API security", invalid payloads, status codes, auth, OpenAPI | Tests REST APIs beyond the happy path (negative/fuzz/contract/security); produces an endpoint map, scenarios, suggested tests, a resilience checklist and a measured baseline-behavior table so the checklist asserts codes the stack really returns |
| **bug-hunter** | "bug hunt", "adversarial test", break it, anti-forge, edge cases of a change | Per-change adversarial testing rite — universal checklist + opt-in stack tracks (Python/pytest, FiveM/Lua, .NET plugin) |
| **log-event-collector** | log tailer, log-to-event parser, file offset, log rotation, partial lines, backpressure, event dedup/idempotency, shutdown flush | Doctrine for a log-tailing collector sidecar — byte-offset persistence that never advances past the last complete line, rotation guard, atomic state, occurrence-keyed dedup, multi-line correlation, backpressure, exactly-once shutdown flush, golden log fixture |

### FiveM

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **fivem-lua** | RegisterNetEvent, RegisterNUICallback, fxmanifest, exports, NUI, CreateThread, StateBags, natives | CitizenFX Lua conventions — client-never-trusted boundary, explicit fxmanifest order, no busy loops, module-per-global, NUI focus/cleanup |
| **fivem-fallback** | FiveM resource calling backend/Consul/another resource, config fetch, retry in Lua | FiveM/Lua adaptation of backend-resilience — SafeCall/clampNum, deadline-bounded jittered boot retry, idempotent-only retries, NUI error signaling |

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
| **execute-backlog** | /execute-backlog <n>, "implement issue #N", "pick up this ticket" | Drives an existing backlog item to a validated PR: completeness gate, plan approved before code, branch-per-item, repo-discovered validations, `Closes #n` linking, board moved to review — never merges or closes issues itself |
| **verify-before-claiming** | "you invented that", "don't guess", "achismo", "pesquisa antes", "de onde tirou", "cite the source", "that flag does not exist", "out of scope" | Anti-guessing rite — cheapest-first research ladder (session context → this repo → the installed dependency → the tool itself → version-pinned docs → web search → the user), verified/inferred/unknown claim labelling, a not-found report that logs the commands it ran, the knowledge-cutoff rule (the lockfile wins), and the off-script scope guard |
| **code-locale** | naming a variable/function/route/column/event/config key, reviewing names in a diff, "código em português", "identificador em inglês", "should this be in English", "naming convention", "ubiquitous language" | Which natural language each artifact is written in — prose follows the repo, anything a machine parses is English and ASCII; the untranslatable-domain-term exception (CPF, boleto, nota fiscal) gated by the item's glossary or an inline `locale-ok:` reason; the anti-corruption layer for foreign payloads; new-code-only migration with expand/contract for contract-bearing names; ships a stdlib-only detector with `--diff` mode that this repo's CI runs and any project can wire into pre-commit |

### DevOps & docs

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **documentation** | README, SETUP, TECHNICAL, CHANGELOG, AGENTS.md, "document this", "write the docs" | Reads the code first, then creates only the documents the project earns — one purpose per page, claims written so a script can verify them (paths as links, trees rooted correctly, env tables from the config module), docs changed in the same commit as the code, and an `AGENTS.md` when a tool-specific instruction file already exists |
| **helm-migration** | "migrate to helm", "convert yaml to helm", "generate values.yaml" | Converts K8s YAML to Helm values.yaml/env.yaml — **requires the solvelab chart template repository** |
| **k8s-tune-resources** | "tune"/"reduce"/"scale down"/"ajustar resources" of pods on nodes with a label, across many repos | Bulk-edits resource requests across every repo behind a node label — discovery from pod images, then clone/patch/commit/push. **Pushes to many repos: runs `DRY_RUN=1` by default** |

### Tooling

| Skill | Triggers | What It Does |
|-------|----------|--------------|
| **claude-statusline** | "configure my Claude Code status line", statusLine in settings.json, statusline.sh, "add context/cost/git to my statusline", install a statusline gist | Sets up or customizes the Claude Code status bar — ships a ready-made 3-line script (model/effort/thinking/cost · repo/branch/diff/token-cost · context/rate-limits) plus the full JSON-field reference; safe install, custom-build rules, and gist sharing |

### Game (React Three Fiber — 10 topics)

Every code block in these skills is compile-checked: blocks tagged `tsx` are complete modules that
typecheck against `three@0.185` · `@react-three/fiber@9.7` · `@react-three/drei@10.7` · `react@19.2`,
and illustrative fragments carry a `// excerpt` marker. Each skill states the stack it was verified
against, and flags the R3F v10 `state.gl` → `state.renderer` rename that is coming.

| Skill | Covers |
|-------|--------|
| **svg-animation** | Classify the request into physical regimes, then draw: viewpoint gate, provenance on every quantity, regime schemas (articulated body, driven oscillator, dispersive waves, ballistic ensembles, growth structures, advected fields, discharges, orbits, point sets), measured SVG/CSS/Canvas costs |
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

## 📐 Spec-Driven Rite (OpenSpec)

Every change to this repository runs through [OpenSpec](https://github.com/Fission-AI/OpenSpec) with a
project-local forked schema, **`skills-rite`** (`openspec/schemas/skills-rite/`, selected by
`openspec/config.yaml`). Specs are the source of truth; changes are validated deltas against them:

```
openspec/
  specs/<capability>/spec.md      # current truth (updated only at archive)
  changes/<change-id>/            # active change: proposal.md, design.md, tasks.md, specs/ deltas
  changes/archive/<date>-<id>/    # history + base for future deltas
  schemas/skills-rite/            # the fork: schema.yaml + artifact templates
```

### Lifecycle (`/opsx` commands)

| Stage | Command | What happens |
|---|---|---|
| Explore | `/opsx:explore` | Thinking-partner mode — align the requirement, no implementation |
| Propose | `/opsx:propose <idea>` | Scaffolds proposal → spec deltas → design → tasks with the gates below |
| Validate | `openspec validate <id> --strict` + `./scripts/validate-rite.sh` | Gate before any code |
| Apply | `/opsx:apply <id>` | Implements each task, ticks `[x]` with evidence |
| Archive | `/opsx:archive <id>` | Merges deltas into `specs/`, moves the change to `archive/` |

### The four mandatory gates

- `design.md` → `## Canonical Home & Cross-Links (MANDATORY)` — every cross-cutting rule names its
  single canonical skill; siblings link instead of restating.
- `tasks.md` → `## Simulation & Field Proof (MANDATORY)` (third-to-last group) — proof the artifact
  was **run**, not only read: the entry point exercised, a fragment of the output observed, and the
  case matrix as counts. A change touching no runtime artifact says so explicitly. It exists because
  a green selftest and a green pipeline still shipped two defects that only an end-to-end run
  surfaced (2026-08-26, issue #95).
- `tasks.md` → `## Quality Gates (MANDATORY)` (second-to-last group) — adversarial review of every
  touched skill: uniform frontmatter, English-only content, testable non-colliding triggers.
- `tasks.md` → `## Validation & Closure (MANDATORY)` (last group) — strict validation green, catalog
  discovery intact, docs updated, then archive.

`tasks.md` also opens with `## Evidence & Sources (MANDATORY)` (first group) — what was read and
probed before anything was written. Evidence is what you *read*; simulation is what you *ran*.

### Where enforcement actually happens

The CLI's `openspec validate --strict` checks **delta-spec format only** — probe-verified on CLI
1.6.0, it does **not** check custom template sections, so the forked schema alone is advisory (it
feeds `/opsx` artifact generation). The **hard gate** is [`scripts/validate-rite.sh`](scripts/validate-rite.sh):
it requires the five gate headings in every active change (evidence group first, closure group
last) and runs
`openspec validate --all --strict`, wired as the **"OpenSpec rite gate"** step in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml). Run it locally before pushing — CI is the
backstop, not the first line.

Every check above iterates over *active changes*, which means a pull request that opened none used to
pass them all vacuously: the loop found nothing, `fail` stayed 0, and the gate printed `rite gate OK`.
That is how PR #80 and PR #84 shipped blocking CI gates with no proposal and had to be registered
retroactively by PR #88. [`scripts/validate-spec-rite.py`](scripts/validate-spec-rite.py) reads the
**diff** instead: a pull request touching anything outside `openspec/` (beyond the paths the release
automation writes) must carry an active change, a change archived in the same diff, or a waiver line
`Spec-rite: none — <reason>` in its body. The waiver is authored by whoever opened the PR, including
from a fork, so it is matched as text and never executed. The checkout runs at `fetch-depth: 0`
because a gate with no base revision cannot measure, and a gate that cannot measure must not approve.

A second gate checks the **content** of the skills themselves.
[`scripts/validate-skills.py`](scripts/validate-skills.py) runs eight checks over every
`skills/*/SKILL.md` and its references — referenced paths exist (C1), cross-skill references name a
real skill (C2), code blocks parse (C3, bash/yaml/json/lua/python), the description states no policy
the body contradicts (C4), versioned external APIs are pinned (C5), fence tags match their content
(C6), no generated wrapper is orphaned from a canonical source (C7), and no meta section sits in a
`SKILL.md` body where it cannot affect routing (C8). The list is the script's own docstring — run
`grep -E '^  C[0-9]' scripts/validate-skills.py` rather than trusting this paragraph. It reports any
check skipped for want of a tool rather than counting it as a pass.

Because a checker that never fails is not a checker,
[`scripts/selftest-validate-skills.py`](scripts/selftest-validate-skills.py) injects one known defect
per check into a throwaway copy of the catalog and asserts each one is detected. Both run in CI.

A third gate looks at the repository as a whole, which is the slice the others miss —
`validate-skills.py` walks only `skills/`, the secret scan hunts credentials, the rite gate reads
OpenSpec changes, and the wrapper-sync step diffs generated trees.
[`scripts/validate-repo-hygiene.py`](scripts/validate-repo-hygiene.py) runs two checks: **H1** no
compiled Python artifact is tracked, and **H2** every `all N` skill count published in `README.md`
and `.claude-plugin/marketplace.json` equals `ls skills | wc -l`. Both exist because both defects
actually shipped — a `.pyc` reached release `2.6.0`, and the published counts drifted to 27 and 30
against a tree of 32. It carries a `--selftest` mode on the same principle as the skill validator,
and each check states in its own docstring what it does **not** cover.

A fourth gate scans for credentials.
[`scripts/scan-secrets.py`](scripts/scan-secrets.py) has two modes on purpose: by default it scans the
**working tree** and fails the build on any credential class — that is the part that can be kept clean,
so that is the part that gates. With `--history` it walks every blob in the full git history and
**reports without gating**, because a secret removed in a later commit is still published and a gate
that can never go green is a gate everyone learns to ignore. Private (RFC1918) addresses are reported
as operational detail, never as a build failure.

```bash
python3 scripts/validate-skills.py           # 0 findings expected
python3 scripts/selftest-validate-skills.py  # 12/12 defect classes detected
python3 scripts/scan-secrets.py              # gate: no credentials in the working tree
python3 scripts/scan-secrets.py --history    # audit: what the published history still contains
```

### Per-machine setup

```bash
npm install -g @fission-ai/openspec   # CLI (>= 1.6.0)
openspec init --tools claude          # generates the /opsx commands into .claude/ (git-ignored, per machine)
```

### Board integration

Work arrives through the [backlog automation](#%EF%B8%8F-backlog-automation-quickstart-backlog--execute-backlog):
`/backlog <idea>` creates the card on the org Project, `/execute-backlog <n>` drives it through this
rite to a PR (real example: [PR #18](https://github.com/solvelab/ai-skills/pull/18) — proposal,
gates, strict + rite-gate validation, archive, evidence table).

---

## ➕ How to Add a New Skill

> Skill additions and edits go through the [Spec-Driven Rite](#-spec-driven-rite-openspec) above —
> `/opsx:propose` first, code after the gates are green.

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

Process-wide conventions are enforced by the [Spec-Driven Rite](#-spec-driven-rite-openspec):
authoring rules live in `openspec/specs/skills-authoring/spec.md`, catalog composition in
`openspec/specs/skills-catalog/spec.md`.

A coding standard that applies across tools and stacks — naming, commit format, error handling,
API design — is **a skill**, not a separate file tree. Skills are what every tool actually loads:
`install.sh` symlinks them into `~/.claude/skills/`, `generate.sh` mirrors them into the Codex,
Cursor and Copilot trees, and `scripts/validate-skills.py` validates their links and code blocks.

`openspec/specs/skills-authoring/spec.md` (*Single canonical home per rule*) governs how such a rule
is placed: it is defined in exactly one skill and referenced by a one-line link everywhere else.
Worked examples in this catalog:

| Cross-cutting rule | Canonical skill |
|---|---|
| Which language identifiers, routes and keys are written in | `skills/code-locale/` |
| Research before asserting; report what could not be found | `skills/verify-before-claiming/` |
| Commit and PR format | `skills/conventional-commit/` |

Reference one from a sibling skill with a single line under its `## See also`, never by restating
it:

```markdown
- `code-locale` — event names and StateBag keys are English even when the repo's prose is not.
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
