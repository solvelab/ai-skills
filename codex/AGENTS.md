# AI Skills — Codex Configuration

This directory contains skill wrappers for OpenAI Codex CLI.

Each skill references shared content from `shared/skills/` — no duplication.

## Available Skills

| Skill | Path |
|-------|------|
| Documentation | `codex/skills/documentation/AGENTS.md` |
| Helm Migration | `codex/skills/helm-migration/AGENTS.md` |
| R3F Animation | `codex/skills/game/r3f-animation/AGENTS.md` |
| R3F Fundamentals | `codex/skills/game/r3f-fundamentals/AGENTS.md` |
| R3F Geometry | `codex/skills/game/r3f-geometry/AGENTS.md` |
| R3F Interaction | `codex/skills/game/r3f-interaction/AGENTS.md` |
| R3F Lighting | `codex/skills/game/r3f-lighting/AGENTS.md` |
| R3F Loaders | `codex/skills/game/r3f-loaders/AGENTS.md` |
| R3F Materials | `codex/skills/game/r3f-materials/AGENTS.md` |
| R3F Physics | `codex/skills/game/r3f-physics/AGENTS.md` |
| R3F Post-processing | `codex/skills/game/r3f-postprocessing/AGENTS.md` |
| R3F Shaders | `codex/skills/game/r3f-shaders/AGENTS.md` |
| R3F Textures | `codex/skills/game/r3f-textures/AGENTS.md` |

## Setup

Configure Codex to use these skills by adding the skill paths to your `~/.codex/config.toml` or referencing them from your project's `AGENTS.md`.
