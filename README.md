<div align="center">

  # 🧠 AI Skills

  **Personal collection of reusable AI skills and conventions for coding assistants.**

  [![Claude Code](https://img.shields.io/badge/Claude_Code-supported-8A2BE2?logo=anthropic&logoColor=white)](https://claude.ai)
  [![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-planned-24292e?logo=github&logoColor=white)](https://github.com/features/copilot)
  [![OpenAI Codex](https://img.shields.io/badge/OpenAI_Codex-planned-412991?logo=openai&logoColor=white)](https://openai.com)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)]()
  [![Install](https://img.shields.io/badge/install-one--line-brightgreen?logo=gnubash&logoColor=white)](#-install)

</div>

Each skill is an instruction file that teaches an AI tool how to perform a specific type of task — like writing documentation, creating commits, or following code conventions.

Currently supports **Claude Code**, with placeholder folders for Cursor, GitHub Copilot, and OpenAI Codex.

---

## 🚀 Install

### Option A — One-line terminal install

```bash
curl -sSL https://raw.githubusercontent.com/solvelab/ai-skills/master/install.sh | bash
```

This will:
- Clone this repository into `~/ai-skills`
- Configure Claude Code globally via `~/.claude/CLAUDE.md`
- Skills will be available in every project automatically

### Option B — AI prompt install

Paste this into Claude Code, GitHub Copilot, or any AI coding assistant:

> Install ai-skills from https://github.com/solvelab/ai-skills into ~/ai-skills
> and configure Claude Code globally by adding the skills path to ~/.claude/CLAUDE.md.

### Option C — Manual install

```bash
# 1. Clone the repository
git clone https://github.com/solvelab/ai-skills.git ~/ai-skills

# 2. Add to ~/.claude/CLAUDE.md
mkdir -p ~/.claude
echo '
## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.
' >> ~/.claude/CLAUDE.md
```

---

## 📁 Repository Structure

```
ai-skills/
├── claude/
│   └── skills/
│       ├── documentation/
│       │   ├── SKILL.md                  # Documentation writing skill
│       │   └── references/
│       │       └── examples.md           # Real-world documentation examples
│       └── helm-migration/
│           ├── SKILL.md                  # Kubernetes YAML to Helm migration skill
│           └── references/
│               └── examples.md           # Before/after migration examples
├── cursor/                               # Rules for Cursor (planned)
├── copilot/                              # Instructions for GitHub Copilot (planned)
├── codex/                                # Instructions for OpenAI Codex (planned)
├── shared/
│   └── conventions/                      # Cross-tool conventions (planned)
└── README.md
```

| Folder | Purpose |
|--------|---------|
| `claude/skills/` | Skill definitions for Claude Code — one folder per skill |
| `cursor/` | Rules and configurations for Cursor |
| `copilot/` | Instructions for GitHub Copilot |
| `codex/` | Instructions for OpenAI Codex |
| `shared/conventions/` | Coding standards shared across all tools |

---

## 🧩 How Claude Code Skills Work

### What is a skill?

A skill is a markdown instruction file (`SKILL.md`) that Claude reads before performing a task. It contains patterns, rules, and examples that guide Claude to produce consistent, high-quality output for a specific type of work.

Think of skills as reusable expertise — instead of explaining your documentation style every time, you write it once in a skill file and Claude follows it automatically.

### Where skills live

Each skill has its own folder inside `claude/skills/`:

```
claude/skills/<skill-name>/SKILL.md
```

### How Claude detects and uses skills

Claude Code automatically matches skills to tasks based on the **YAML frontmatter** at the top of each `SKILL.md` file:

```yaml
---
name: documentation
description: Use this skill whenever the user asks to create, update, write
  or improve any documentation for a software project. Triggers include
  requests mentioning README, docs, SETUP, TECHNICAL, CHANGELOG...
---
```

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier for the skill |
| `description` | Natural language description of when to activate the skill. Claude matches the user's request against this text to decide whether to load the skill. |

When a user's request matches the description, Claude loads the full `SKILL.md` content and follows its instructions.

---

## ⚙️ How to Configure Claude Code to Use These Skills

### Option 1: Reference in your project's CLAUDE.md

Add a line to the `CLAUDE.md` file in any project where you want these skills available:

```markdown
## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.
```

### Option 2: Global CLAUDE.md

Add the reference to your global Claude Code config at `~/.claude/CLAUDE.md` so skills are available in every project:

```markdown
## Skills

Skills are located at ~/ai-skills/claude/skills/.
Each skill has a SKILL.md file. Read the relevant skill before performing any matching task.
```

### Option 3: Copy skills into a project

Copy the skill folder directly into a project's `.claude/skills/` directory:

```bash
cp -r ~/ai-skills/claude/skills/documentation /path/to/project/.claude/skills/
```

---

## 📦 Skills Available

| Skill | Triggers | What It Does | Status |
|-------|----------|--------------|--------|
| **documentation** | README, SETUP, TECHNICAL, CHANGELOG, "document this", "write the docs" | Analyzes the project first, then creates all documentation files the project actually needs | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |
| **helm-migration** | "migrate to helm", "convert yaml to helm", "generate values.yaml", "yaml to helm" | Converts Kubernetes YAML manifests to Helm values.yaml and env.yaml following your chart template structure | ![stable](https://img.shields.io/badge/status-stable-brightgreen) |

### documentation

**File**: `claude/skills/documentation/SKILL.md`

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

For best results, use this prompt:
```
Document this project following the documentation skill.
Analyze the codebase and create all documentation files this project needs.
```

> 💡 **Tip:** Skills activate automatically — you don't need to reference them by name. Just describe what you want and Claude reads the right skill for the task.

#### Testing the skill in your project

Open your project in Claude Code:
```bash
cd /path/to/your/project
claude
```

Then paste this prompt:
```
Document this project following the documentation skill.
Analyze the codebase and create all documentation files this project needs.
```

Watch for these signs that the skill is working:
- Claude reads the codebase **before** writing anything
- Claude lists which documents it will create based on the project type
- More than just `README.md` is created depending on the project

#### How to verify the skill was used

After running the prompt, check that:
- [ ] Claude scanned the codebase before writing anything
- [ ] `README.md` has a centered header with badges
- [ ] All relevant docs were created based on what the project actually is
- [ ] No generic or empty documents were created

### helm-migration

**File**: `claude/skills/helm-migration/SKILL.md`

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
Charts template path: /path/to/your/charts-template
Source YAML-file: /path/to/your/manifest.yaml
Save files to: /path/to/destination/
```

**What the skill always does:**
- Reads your charts template structure before generating anything
- Removes `tolerations` from all generated files — no exceptions
- Adds explanatory comments to every section
- Generates `env.yaml` only when secrets, configmaps or PVCs are present
- Preserves `secretKeyRef` references in `values.yaml` and creates empty secret entries in `env.yaml` with a warning to fill in values

#### How to verify the skill was used

After running the prompt, check that:
- [ ] Claude read the charts template before generating files
- [ ] `values.yaml` follows your chart template structure exactly
- [ ] `env.yaml` was created if secrets/configmaps/PVCs were present
- [ ] No `tolerations` appear in any generated file
- [ ] All sections have explanatory comments

---

## ➕ How to Add a New Skill

### 1. Create the skill folder and file

```bash
mkdir -p claude/skills/<skill-name>
touch claude/skills/<skill-name>/SKILL.md
```

### 2. Add YAML frontmatter

Start the file with `name` and `description`:

```yaml
---
name: my-skill
description: Use this skill when the user asks to [describe the task].
  Triggers include [list keywords and phrases that should activate this skill].
---
```

Write the `description` as if you're telling Claude "use this when you see these kinds of requests". Be specific about trigger words and phrases.

### 3. Write the skill instructions

After the frontmatter, write the instructions Claude should follow. Use this structure:

```markdown
# Skill Name

You are a [role]. When asked to [task], follow the patterns below.

## Core Principles

1. **Principle**: Explanation
2. **Principle**: Explanation

## Structure / Template

Show the expected output structure.

## Rules

- Specific rules Claude must follow
- Formatting conventions
- What to include and what to avoid

## Examples

Real examples showing the expected output.
```

### 4. Key guidelines for writing skills

| Guideline | Why |
|-----------|-----|
| Base on real examples | Skills derived from actual code/docs are more useful than generic templates |
| Be specific, not vague | "Use tables for env vars" is better than "format things nicely" |
| Include structure templates | Show the exact skeleton Claude should follow |
| State rules as imperatives | "Always include a troubleshooting section" not "it would be nice to have troubleshooting" |
| Keep it focused | One skill per task type. Don't combine "documentation" and "commit messages" |

---

## 🤝 Shared Conventions

The `shared/conventions/` folder is for coding standards and patterns that apply across all AI tools — not just Claude Code. Place files here when the same convention should be followed regardless of which tool is being used.

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
| [Claude Code](https://claude.ai) | AI coding assistant — primary target |
| [GitHub](https://github.com) | Hosting and version control |
| [Bash](https://www.gnu.org/software/bash/) | One-line install script |

---

## 📄 License

MIT
