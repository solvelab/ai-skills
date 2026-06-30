---
name: conventional-commit
description: Format every git commit message using Conventional Commits (type(scope): description) prefixed with a gitmoji icon matching the type. Use whenever creating a commit, amending a commit, or writing a commit message via /commit, heredoc, -m flag, or any skill. Never include Co-Authored-By/Claude attribution.
metadata:
  author: diegops
  version: 1.0.0
  category: git
---

# conventional-commit

Every commit message must follow **Conventional Commits**, prefixed with a **gitmoji icon** matching the type.

## Format

```
<icone> <tipo>(<escopo opcional>): <descrição curta no imperativo>

<corpo opcional explicando o "porquê", não o "o quê">
```

- Subject line in Portuguese (project convention), imperative mood, no trailing period.
- Scope is optional but encouraged when the change is localized to a module/folder.
- Body only when the "why" isn't obvious from the diff or subject.

## Type → icon mapping

| Tipo | Ícone | Uso |
|---|---|---|
| `feat` | ✨ | nova funcionalidade |
| `fix` | 🐛 | correção de bug |
| `refactor` | ♻️ | refatoração sem mudar comportamento |
| `docs` | 📝 | documentação |
| `chore` | 🧹 | tarefas de manutenção, configs, deps |
| `test` | ✅ | testes |
| `style` | 🎨 | formatação, estilo, sem mudança de lógica |
| `perf` | ⚡ | performance |
| `ci` | 👷 | CI/CD |
| `build` | 📦 | build system, dependências |
| `revert` | ⏪ | reverter commit anterior |
| `security` | 🔒 | correções de segurança |

When the change doesn't cleanly fit one type (e.g. multiple concerns), pick the dominant one — don't stack icons.

## Hard rules

- **NEVER** include `Co-Authored-By: Claude` (or any variant — Claude Opus, Claude Sonnet, `<noreply@anthropic.com>`) in any commit message, new commit, amend, rebase, squash, or via any skill/heredoc/-m flag. This is non-negotiable.
- Always use `git commit -m "$(cat <<'EOF' ... EOF)"` heredoc pattern to avoid shell escaping issues.
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
