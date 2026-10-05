# Change: Fazer o rito enxergar o repositório a partir da raiz de um workspace e de uma subpasta

## Why

Cada artefato do rito acha o repositório a partir do `cwd` da sessão, e nenhum deles sobe até a raiz
do repositório nem desce até os repositórios filhos de um workspace (issue #261). Medido em
2026-10-04 com os artefatos de `6fbda3a` (topo de `origin/master`), a partir do workspace do Mantis
— raiz sem `.git`, um filho `mantis-computer` que roda `openspec` com `spec_rite.policy: required`:

| `cwd` | frase do spec rite (`backlog-rite.py`) | `[ -d openspec ]` | Stop gate | write gate, `Write` de `mantis-computer/crates/core/src/servicos/x.rs` |
|---|---|---|---|---|
| raiz do workspace | ausente | not found | mudo (`rev-parse` sai 128) | deny em `mantis-computer/crates/core/src/servicos/x.rs` — caminho medido a partir do workspace, allowlist procurada acima do repo |
| `mantis-computer/` | presente | found | mede o repo | deny em `crates/core/src/servicos/x.rs` (correto) |
| `mantis-computer/src-tauri/` | ausente | not found | mede o repo | mudo: o caminho medido vira só `x.rs` |

O gate de spec, que por doutrina falha fechado (*The development rite is enforced outside the model's
discretion*), falha aberto e calado justamente no modo que a skill `backlog` declara suportar
("Works in any git repository or multi-repo workspace directory"). O contorno vive num comentário do
`backlog.yml` do workspace e depende de disciplina — o que o requisito proíbe.

## What Changes

- **`claude/global/hooks/backlog-rite.py`** — a frase do spec rite passa a valer para o `openspec/`
  mais próximo entre o `cwd` e a raiz do repositório em que ele está (subida no sistema de arquivos
  até o primeiro `.git`, diretório ou arquivo, sem chamar git) — a resolução que a própria CLI do
  `openspec` faz, limitada à raiz. A raiz é achada de qualquer profundidade, e um `cwd` que carrega
  `openspec/` abaixo de uma raiz que não carrega continua com a frase de hoje. Da raiz de um
  workspace (fora de qualquer repo, com filhos diretos que têm `.git`), uma frase só nomeia os filhos
  que têm `openspec/`; sem filho assim, nenhuma frase, como hoje. Um diretório fora de qualquer repo
  que carrega `openspec/` mantém a frase de hoje.
- **`claude/global/hooks/locale-rite.py`** — a allowlist e o caminho medido saem da raiz do
  repositório do arquivo escrito, por um único helper que serve a direção de identificadores e a de
  prosa; o `cwd` vira fallback só para um arquivo fora de qualquer repositório (a regra que
  `declared_prose` já segue).
- **`claude/global/hooks/locale-stop-gate.py`** — da raiz de um workspace, mede o diff não commitado
  de cada filho, cada um com a própria allowlist e o próprio `.code-locale`, num só motivo, com o
  caminho prefixado pelo diretório do filho e a dica da allowlist relativa ao filho. O teto de linhas
  é compartilhado, o tempo total fica abaixo do timeout da fiação, e o que não couber é declarado como
  não medido, nunca omitido. O mesmo prazo passa a valer para um repositório só: um Stop que passe
  dele bloqueia uma vez dizendo o que não mediu, em vez de depender do kill da fiação. Isso desvia da
  linha de Risks da issue ("Um git que passa de `GIT_TIMEOUT` continua deixando o gate mudo"), que
  continua valendo para a chamada git que estoura o próprio timeout: o desvio é registrado como
  comentário na issue antes da primeira edição.
- **`skills/backlog`** (passo 6, `references/backlog-config.md`, `references/issue-template.md`) e
  **`skills/execute-backlog`** (`references/spec-rite.md` e a cláusula de workspace no passo 5 do
  `SKILL.md`, que FR4 nomeia) — o rito é detectado onde vive para o repositório alvo (em modo repo, o
  `openspec/` mais próximo entre o `cwd` e a raiz git; em modo workspace, a raiz de cada repositório
  afetado), os comandos do `openspec` rodam com esse diretório como diretório de trabalho, e em
  modo workspace a seção Spec rite traz um veredito por repositório afetado que roda o workflow, com
  a policy lida do `.github/backlog.yml` dele, depois do `backlog.yml` do workspace, depois do padrão
  que falha fechado. `metadata.version`: `backlog` 1.5.2 -> 1.6.0, `execute-backlog` 1.9.0 -> 1.10.0.
- **Docstrings** (KNOWN LIMIT e *WHAT THE SELFTEST DOES NOT COVER*), **`README.md`** (as seções dos
  hooks) e os **selftests** dos três hooks; cópias geradas por `generate.sh`.

Nada é **BREAKING** para quem consome o catálogo: nenhuma skill entra, sai ou muda de nome, e num
repositório com o `cwd` na raiz cada artefato decide como antes para o trabalho dentro desse
repositório. Mudam só dois casos com o `cwd` na raiz, os dois declarados: a escrita num arquivo de
outro repositório (ou de um submódulo) passa a ser medida pela raiz e pela allowlist dele (FR6), e
um Stop que passe do prazo declarado diz o que não mediu.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `skills-catalog`:
  - *The development rite is enforced outside the model's discretion* — o workflow é procurado do
    `cwd` até a raiz do repositório dele, em qualquer profundidade (o mais próximo vale), e, da raiz de
    um workspace, em cada repositório filho, nomeando os que o rodam.
  - *The backlog skills declare their place in one rite* — detecção, comandos e policy por repositório
    alvo; em modo workspace, um veredito por repositório afetado.
  - *The code-locale rite is enforced at the moment of the write* — a allowlist e o caminho medido
    são os do repositório do arquivo escrito; o `cwd` só serve fora de qualquer repositório.
  - *The code-locale rite closes the turn, not only the write* — da raiz de um workspace, cada filho é
    medido; teto de linhas compartilhado, orçamento de tempo declarado, e a frase "silent ... under
    one second ... outside a git work tree" é reescrita para o que foi medido.

## Impact

- Skills tocadas: `backlog` (`SKILL.md`, `references/backlog-config.md`,
  `references/issue-template.md`) e `execute-backlog` (`references/spec-rite.md` e uma cláusula no
  passo 5 do `SKILL.md`: FR4 nomeia esse passo, e o "skip when there is none" dele é o que vira no-op
  na raiz do workspace; a issue não lista o arquivo, então a inclusão vai no comentário de ajustes
  aprovados). A composição do catálogo não muda.
- Hooks: `backlog-rite.py`, `locale-rite.py`, `locale-stop-gate.py` — os casos atuais dos três
  selftests continuam com os mesmos nomes e o mesmo resultado esperado; fixtures sem `.git` ganham o
  marcador para que a subida pare nelas.
- Repo: `README.md` (`:326`, `:404`, `:430-434`), `openspec/specs/skills-catalog/spec.md` (pelo
  delta, no archive), cópias geradas em `plugins/`, `claude/skills/`, `cursor/rules/`, `codex/`,
  `copilot/`.
- Quem roda os hooks a partir de um repositório com o `cwd` na raiz não vê diferença no trabalho
  dentro desse repositório (as duas exceções estão no fim de *What Changes*). A partir de uma
  subpasta ou da raiz de um workspace, os hooks passam a medir e a lembrar o que antes calavam — um
  clone alheio como filho de workspace passa a ser medido (saídas: a allowlist do filho e
  `LOCALE_RITE_MODE=inform`).

Fora de escopo, por decisão da issue: outro repositório quando o `cwd` já está num (limite declarado);
workspace com mais de um nível e os hooks lerem `workspace.repos`; a busca de `load_allowlist` acima
da fronteira do repositório; a raiz do `scripts/validate-spec-rite.py` (#260); Rust no
`check-identifier-locale.py`.
