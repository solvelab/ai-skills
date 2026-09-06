# Change: Skill lean-code — escada reusar-antes-de-escrever, causa raiz, lente de revisão

## Why

O item #145 (`add-lean-code-research`) mediu o que o modelo diário do mantenedor deixa atrás quando
ninguém lhe diz quanto código sobra. As contagens abaixo são as de
`research/lean-code/results/20260905-211512-baseline-defects.md` — `opus[1m]` resolvido pelo CLI
para `claude-opus-5[1m]`, Claude Code `2.1.261`, `n=3` × 9 tarefas = 27 células, `correct` 27/27,
`safe` 27/27, $9,45 — e **não** as do upstream (Haiku 4.5, CC 2.1.177, outro repositório):

| Defeito lido nos diffs (células de 27) | Onde | Degrau da lente |
|---|--:|---|
| classe de exceção custom para um guard (`class_for_oneliner`) | 6 — `trace-transfer` 3/3, `safe-path` 3/3 | `yagni:` |
| tolerância especulativa de entrada (moeda, separador de milhar, BOM, `nan`, drive letters) | 6 — `csv-sum` 3/3, `safe-path` 3/3 | `yagni:` |
| decomposição em helpers de um loop curto (`_find_amount_field`, `_iter_rows`, `_parse_amount`, `_reject`) | 4 — `csv-sum` 3/3, `safe-path` 1 | `shrink:` |
| validação de tipo/negatividade que ninguém pediu (`_check_amount`) | 3 — `trace-transfer` 3/3 | `yagni:` |
| expansão de docstring/comentário (29 das 102 linhas médias do `csv-sum`) | 12 | prosa, não código |
| `no_check` (sem nenhum check executável) | 3/27 — `react-use-orders`, estrutural | piso de um check |
| `prose_gt_code` | 1/27 — `sql-user` 2 | contrato de saída |

Em `added_lines`: `csv-sum` média **102** (81/98/127) contra uma referência de 10 linhas;
`safe-path` **67,7** (59/62/82) contra 7; `trace-transfer` **27** contra um guard de 2 linhas.
`cache` (12,7 vs 10), `sql-user` (7,7 vs 3) e `reuse-slug` (9) ficaram perto da referência.
`new_dependency` 0/27, `guard_dropped` 0/27, `patched_caller_only` 0/27, `reimplemented_existing`
0/27 — o baseline **não** tem os defeitos que o upstream corrige de forma mais vistosa (perder guard,
reimplementar, remendar só o caller nomeado); tem **over-build concentrado**: exceção custom,
tolerância que ninguém pediu, helpers para dez linhas, docstring maior que o código. É isso que a
skill mira, e é por isso que as seções dela vêm nessa ordem.

E o catálogo não tem lar para a regra. Medido em `f11ba7a`:

```
grep -rniE "yagni|less code|smallest change|speculative|over-engineer|dead code|tech debt" skills/ claude/global/personal-rules.md | wc -l
-> 0
```

O que existe é disciplina de **escopo** (`verify-before-claiming`, *Doing / Not doing /
Assumptions*; `execute-backlog`, *Scope is law*), de **duplicação em prosa** (`documentation`) e uma
única regra de contenção de dependência (`log-event-collector`, "no new supply chain for the sake of
ergonomics"). Nenhuma skill diz quando não escrever código, reusar antes de criar, qual é o tamanho
mínimo de uma mudança, ou como revisar um diff pelo que ele podia perder.

Fonte da doutrina: DietrichGebert/ponytail v4.9.0 (MIT, `974d940a`), `skills/ponytail/SKILL.md`
(~120 linhas) e `skills/ponytail-review/SKILL.md`. O upstream mediu que a **redação** carrega o
efeito (−54 % LOC com o texto literal contra −33 % com a paráfrase "Follow YAGNI, prefer
one-liners", e a paráfrase perdeu um guard: 19/20); por isso a escada, a regra de causa raiz e os
carve-outs entram verbatim, com o aviso MIT em `references/upstream.md`.

## What Changes

- `skills/lean-code/SKILL.md` (1.0.0, `category: process` → plugin `workflow`): tese em três frases
  ("lean" é o que **sobra**, nunca velocidade), índice das quatro references, `## The ladder` (7
  degraus verbatim), `## Bug fix = root cause, not symptom` (verbatim), `## Rules` (verbatim com duas
  edições: marcador `ponytail:` → `lean:`; a regra "ship the lazy version and question it" passa a
  deferir ao bloco *Doing / Not doing / Assumptions* de `verify-before-claiming`), `## What the
  delivery looks like` (trailer `[code] → skipped: [X], add when [Y]` obrigatório, sem teto de
  três linhas), `## Never simplified away` (verbatim, linha de hardware generalizada para "uma
  constante que modela o mundo físico continua um knob"), `## Reviewing a diff` (as 5 tags, o
  formato, `net:`, a guarda de escopo, o parágrafo *Repo-wide*, e onde ficam `/simplify` e
  `/code-review`), `## Marking a deliberate simplification`, `## What the baseline measured` (as
  contagens acima; "skill arm: measured in `research/lean-code/results.md`"), `## When this skill
  defers`, `## See also`, rodapé de atribuição.
- `skills/lean-code/references/`: `platform-native.md` (aparado, sem Swift, lookup e não matriz de
  suporte), `simplification-ledger.md` (grep, formato de linha, tag `no-trigger`, coexistência com
  `locale-ok:`), `review-examples.md` (❌/✅, email-validation antes/depois, um marcador e sua linha
  do ledger, um exemplo de causa raiz), `upstream.md` (repo, tag, commit, aviso MIT integral, mapa
  verbatim/reescrito/descartado, proveniência por regra, números do upstream com condições).
- Uma linha *See also* em `verify-before-claiming`, `bug-hunter`, `code-locale` e
  `log-event-collector`, com bump patch em cada.
- `generate.sh`: `GROUP_THEME[workflow]` ganha "and the lean-code doctrine". `README.md`: membro em
  `ai-skills-workflow`, linha em *Process & git*, `all 35` → `all 36`, a frase "the 35 that `git
  archive HEAD` ships". Wrappers regenerados.
- `claude/global/personal-rules.md`: seção `## Lean Code (the best code is the code never written)`
  depois de *Code Locale*, oito linhas, fechando com o link para a skill; o mesmo bloco sem o
  heading em `research/lean-code/arms-block.md`, para o arm da skill.
- `research/lean-code/run.py`: `--prepare-arms --claude-block <file>` — o arm `skill` recebe a
  sentinela **mais** o bloco always-on no `CLAUDE.md` da célula, o `baseline` só a sentinela; sha256
  do bloco em `arm.json`; preflight confere; casos novos no `--selftest`. `protocol.md` e o README
  da pesquisa registram a opção. Nenhum artefato medido do baseline muda.
- Parte paga (matriz do arm `skill`, lente nos três diffs, veredito, `results.md`): **do
  mantenedor**, com os comandos exatos entregues neste PR; as linhas ficam por marcar no `tasks.md`.

Fora de escopo, por decisão da issue: reescrever regras de irmãos; hook novo; check de validador
para "lean" (certificaria forma, não julgamento); kit de adoção do ledger por repositório; níveis
lite/full/ultra, gain, help, flags, statusline, hooks, adaptadores e MCP do upstream.

## Capabilities

### New Capabilities

Nenhuma capability nova de spec: a doutrina entra como requisito ADDED em `skills-catalog`.

### Modified Capabilities

- `skills-catalog`: ADDED *Code volume has a canonical home* — a skill que governa quanto código
  sobra: escada, causa raiz, carve-outs no topo com links, marcador + ledger, lente com tags e
  `net:`, deferência ao guarda de escopo, nenhum número não medido aqui. Seis cenários: recurso
  nativo substitui build custom; report de um caller corrige a função compartilhada; guard de
  fronteira sobrevive à simplificação; simplificação deixa marcador que o ledger acha e o sem
  gatilho é tagueado; questionar a necessidade é proposta, não omissão; saída da revisão é uma linha
  por achado e termina com o `net:`.
- `skills-authoring`: MODIFIED *Single canonical home per rule* — o mapa canônico ganha `lean-code`
  (volume de código: escada, causa raiz, carve-outs, `lean:` + ledger, lente), e um cenário para a
  instância de contenção de dependência que linka o degrau geral em vez de repetir a escada.

## Impact

- Skill **adicionada**: `lean-code`. A composição do catálogo passa de 35 para 36 — mudança
  breaking para quem lê a descoberta via `npx skills add --list` pela contagem; `README.md` e o gate
  H2 de `validate-repo-hygiene.py` acompanham.
- Skills **editadas** (uma linha *See also* + bump patch): `verify-before-claiming` 1.1.0 → 1.1.1,
  `bug-hunter` 2.2.4 → 2.2.5, `code-locale` 1.4.1 → 1.4.2, `log-event-collector` 1.1.1 → 1.1.2.
- `generate.sh` (só a string `GROUP_THEME[workflow]`), `README.md`, `claude/global/personal-rules.md`,
  `research/lean-code/{run.py,protocol.md,README.md,arms-block.md}`, wrappers gerados em `claude/`,
  `codex/`, `cursor/`, `copilot/`, `plugins/workflow/`.
- Release: `feat` → minor.
- Nada em `hooks/`, `ci.yml` ou `install.sh` muda.
