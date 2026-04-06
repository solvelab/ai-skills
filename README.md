<div align="center">

  # 🧠 AI Skills

  **Personal collection of reusable AI skills and conventions for coding assistants.**

  [![Claude Code](https://img.shields.io/badge/Claude_Code-supported-8A2BE2?logo=anthropic&logoColor=white)](https://claude.ai)
  [![OpenAI Codex](https://img.shields.io/badge/OpenAI_Codex-supported-412991?logo=openai&logoColor=white)](https://openai.com)
  [![Cursor](https://img.shields.io/badge/Cursor-supported-000000?logo=cursor&logoColor=white)](https://cursor.com)
  [![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-supported-24292e?logo=github&logoColor=white)](https://github.com/features/copilot)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)]()
  [![Install](https://img.shields.io/badge/install-one--line-brightgreen?logo=gnubash&logoColor=white)](#-install)

</div>

Each skill is an instruction file that teaches an AI tool how to perform a specific type of task — like writing documentation, creating commits, or following code conventions.

Supports **Claude Code**, **OpenAI Codex**, **Cursor**, and **GitHub Copilot** from a single source of truth — no duplication.

---

## 🚀 Install

### Option A — One-line terminal install

```bash
# Claude Code (default)
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash

# OpenAI Codex
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash -s -- --tool codex

# All tools
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash -s -- --tool all
```

This will:
- Clone this repository into `~/ai-skills`
- Configure the selected AI tool to use the skills
- Skills will be available automatically

### Option B — AI prompt install

Paste this into Claude Code, Codex, or any AI coding assistant:

> Install ai-skills from https://github.com/solvelab/ai-skills into ~/ai-skills
> and configure my tool globally by adding the skills path to the appropriate config file.

### Option C — Manual install

```bash
# 1. Clone the repository
git clone https://github.com/solvelab/ai-skills.git ~/ai-skills

# 2. Configure your tool (choose one):

# Claude Code — add to ~/.claude/CLAUDE.md
echo '
## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.
' >> ~/.claude/CLAUDE.md

# OpenAI Codex — add to ~/.codex/AGENTS.md
echo '
# AI Skills

Skills are located at ~/ai-skills/codex/skills/.
Each skill has an AGENTS.md file with instructions for specific tasks.
' >> ~/.codex/AGENTS.md

# Cursor — generate inline .mdc files
cd ~/ai-skills && ./generate.sh
# Then copy cursor/rules/*.mdc to your project's .cursor/rules/

# GitHub Copilot — copy instruction files
cp ~/ai-skills/copilot/instructions/*.instructions.md /path/to/project/.github/instructions/
```

---

## 📁 Repository Structure

```
ai-skills/
├── shared/
│   ├── conventions/                          # Cross-tool coding standards
│   └── skills/                               # Shared skill content (single source of truth)
│       ├── documentation/
│       │   ├── content.md                    # Documentation writing instructions
│       │   └── references/
│       │       └── examples.md               # Real-world documentation examples
│       ├── helm-migration/
│       │   ├── content.md                    # Helm migration instructions
│       │   └── references/
│       │       └── examples.md               # Before/after migration examples
│       └── game/
│           └── r3f-*/                        # React Three Fiber skills (11 topics)
│               └── content.md
├── claude/
│   └── skills/                               # Claude Code wrappers (SKILL.md)
│       ├── documentation/SKILL.md
│       ├── helm-migration/SKILL.md
│       └── game/r3f-*/SKILL.md
├── codex/
│   ├── AGENTS.md                             # Codex global index
│   └── skills/                               # OpenAI Codex wrappers (AGENTS.md)
│       ├── documentation/AGENTS.md
│       ├── helm-migration/AGENTS.md
│       └── game/r3f-*/AGENTS.md
├── cursor/
│   └── rules/                                # Cursor rules (.mdc, auto-generated)
│       ├── documentation.mdc
│       ├── helm-migration.mdc
│       └── r3f-*.mdc
├── copilot/
│   └── instructions/                         # GitHub Copilot wrappers (.instructions.md)
│       ├── documentation.instructions.md
│       ├── helm-migration.instructions.md
│       └── r3f-*.instructions.md
├── generate.sh                               # Generates inline wrappers (Cursor)
├── install.sh                                # One-line installer with --tool flag
└── README.md
```

| Folder | Purpose |
|--------|---------|
| `shared/skills/` | Skill content — written once, shared by all tools |
| `claude/skills/` | Claude Code wrappers with YAML frontmatter for skill detection |
| `codex/skills/` | OpenAI Codex wrappers using `@./path` file includes |
| `cursor/rules/` | Cursor .mdc rules with content inlined (auto-generated) |
| `copilot/instructions/` | GitHub Copilot wrappers with markdown link references |
| `shared/conventions/` | Coding standards shared across all tools |

---

## 🔀 Multi-Tool Architecture

Skills are split into two parts:

1. **Content** (tool-agnostic) — the actual instructions, templates, and rules. Lives in `shared/skills/`. Written once.
2. **Wrapper** (tool-specific) — a thin file that tells the AI tool to read the shared content. Lives in the tool directory.

```
shared/skills/documentation/content.md    ← Single source of truth (530 lines)
        │
        ├── claude/skills/documentation/SKILL.md        ← YAML frontmatter + "Read content.md"
        ├── codex/skills/documentation/AGENTS.md         ← @../../shared/.../content.md
        ├── cursor/rules/documentation.mdc               ← Content inlined (auto-generated)
        └── copilot/instructions/documentation.md        ← Markdown link to content.md
```

| Tool | Wrapper format | File include support | Wrapper size |
|------|---------------|---------------------|-------------|
| **Claude Code** | `SKILL.md` (YAML + MD) | Natural language instruction | ~15 lines |
| **OpenAI Codex** | `AGENTS.md` (plain MD) | `@./path` native syntax | ~4 lines |
| **Cursor** | `.mdc` (YAML + MD) | None — content inlined via `generate.sh` | Full content |
| **GitHub Copilot** | `.instructions.md` (plain MD) | Markdown links `[label](path)` | ~5 lines |

---

## 🧩 How Skills Work

### What is a skill?

A skill is a markdown instruction file that an AI reads before performing a task. It contains patterns, rules, and examples that guide the AI to produce consistent, high-quality output.

Think of skills as reusable expertise — instead of explaining your documentation style every time, you write it once and every AI tool follows it automatically.

### How each tool discovers skills

| Tool | Discovery mechanism |
|------|-------------------|
| **Claude Code** | Reads `SKILL.md` files from paths configured in `~/.claude/CLAUDE.md`. Matches skills to tasks using the YAML `description` field. |
| **OpenAI Codex** | Reads `AGENTS.md` files from configured paths and walks the directory tree. Follows `@./path` includes automatically. |
| **Cursor** | Reads `.mdc` files from `.cursor/rules/` in the project directory. Applies rules based on YAML `globs` or `alwaysApply` settings. |
| **GitHub Copilot** | Reads `.instructions.md` files from `.github/instructions/`. Follows markdown link references to external files. |

---

## 📦 Skills Available

| Skill | Triggers | What It Does | Status |
|-------|----------|--------------|--------|
| **documentation** | README, SETUP, TECHNICAL, CHANGELOG, "document this", "write the docs" | Analyzes the project first, then creates all documentation files the project actually needs | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **helm-migration** | "migrate to helm", "convert yaml to helm", "generate values.yaml", "yaml to helm" | Converts Kubernetes YAML manifests to Helm values.yaml and env.yaml following your chart template structure | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-fundamentals** | R3F Canvas, hooks, JSX elements, events, refs | React Three Fiber fundamentals for 3D scenes in React | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-animation** | useFrame, useAnimations, spring physics, keyframes | R3F animation patterns and procedural motion | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-geometry** | 3D shapes, BufferGeometry, instancing | R3F geometry creation and optimization | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-interaction** | Pointer events, controls, gestures | R3F user interaction and input handling | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-lighting** | Lights, shadows, Environment, IBL | R3F lighting setup and configuration | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-loaders** | useGLTF, useLoader, Suspense, preloading | R3F asset loading patterns | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-materials** | PBR materials, shader materials | R3F material creation and styling | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-physics** | Rapier, RigidBody, colliders, forces | R3F physics simulation | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-postprocessing** | Bloom, DOF, screen effects | R3F post-processing visual effects | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-shaders** | GLSL, shaderMaterial, uniforms | R3F custom shader development | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **r3f-textures** | useTexture, cubemaps, HDR environments | R3F texture loading and configuration | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |

### documentation

**Shared content**: `shared/skills/documentation/content.md`

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

### helm-migration

**Shared content**: `shared/skills/helm-migration/content.md`

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

---

## ➕ How to Add a New Skill

### 1. Create the shared content

```bash
mkdir -p shared/skills/<skill-name>
touch shared/skills/<skill-name>/content.md
```

Write the skill instructions in `content.md`. This is the single source of truth — all AI tools will read from this file.

### 2. Create tool-specific wrappers

#### Claude Code

```bash
mkdir -p claude/skills/<skill-name>
```

Create `claude/skills/<skill-name>/SKILL.md`:

```yaml
---
name: my-skill
description: Use this skill when the user asks to [describe the task].
  Triggers include [list keywords and phrases that should activate this skill].
---

Read and follow all instructions in ~/ai-skills/shared/skills/<skill-name>/content.md
```

#### OpenAI Codex

```bash
mkdir -p codex/skills/<skill-name>
```

Create `codex/skills/<skill-name>/AGENTS.md`:

```markdown
# My Skill

@../../shared/skills/<skill-name>/content.md
```

#### Cursor

Run `./generate.sh` to auto-generate `.mdc` files from shared content.

#### GitHub Copilot

Create `copilot/instructions/<skill-name>.instructions.md`:

```markdown
# My Skill

Follow the instructions in [content.md](../../shared/skills/<skill-name>/content.md)
```

### 3. Key guidelines for writing skills

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
