---
name: conventional-commit
description: >-
  Format every git commit message using Conventional Commits (type(scope) plus short description)
  prefixed with a gitmoji icon matching the type. Use whenever creating a commit, amending a commit, or
  writing a commit message via /commit, heredoc, -m flag, or any skill. Never include any AI
  attribution or co-author reference in commits.
metadata:
  author: solvelab
  version: 1.1.0
  category: git
license: MIT
compatibility: Works in any environment with git access.
---

# conventional-commit

Every commit message must follow **Conventional Commits**, prefixed with a **gitmoji icon** matching
the type.

## Format

```
<icon> <type>(<optional scope>): <short description in the imperative>

<optional body explaining the "why", not the "what">
```

- Subject line language follows the repo's existing convention (solvelab project repos use
  Portuguese; this catalog repo uses English) — check `git log` and match it.
- Imperative mood, no trailing period.
- Scope is optional but encouraged when the change is localized to a module/folder.
- Body only when the "why" isn't obvious from the diff or subject.

## Type → icon mapping

| Type | Icon | Use |
|---|---|---|
| `feat` | ✨ | new functionality |
| `fix` | 🐛 | bug fix |
| `refactor` | ♻️ | refactoring without behavior change |
| `docs` | 📝 | documentation |
| `chore` | 🧹 | maintenance tasks, configs, deps |
| `test` | ✅ | tests |
| `style` | 🎨 | formatting, style, no logic change |
| `perf` | ⚡ | performance |
| `ci` | 👷 | CI/CD |
| `build` | 📦 | build system, dependencies |
| `revert` | ⏪ | revert a previous commit |
| `security` | 🔒 | security fixes |

When the change doesn't cleanly fit one type (e.g. multiple concerns), pick the dominant one — don't
stack icons.

## Hard rules

- **NEVER** include any AI attribution or co-author reference in any commit message — no
  `Co-Authored-By: Claude` (or any variant/model name, or `<noreply@anthropic.com>`), in new commits,
  amends, rebases, squashes, or via any skill/heredoc/-m flag. This is non-negotiable and applies
  under all circumstances.
- Always use the `git commit -m "$(cat <<'EOF' ... EOF)"` heredoc pattern to avoid shell escaping
  issues.
- Only stage files relevant to the change being committed — never `git add -A`/`git add .` blindly.
- Prefer new commits over `--amend` unless the user explicitly asks to amend.

## Examples

```
✨ feat(auth): adiciona login via OAuth2

🐛 fix(api): corrige timeout em requisições concorrentes

♻️ refactor(rogue): divide deploy-resources.sh em scripts por contexto

deploy-resources.sh vira roteador fino que despacha para scripts/<folder>.sh,
permitindo adicionar novas pastas sem editar o roteador.
```
