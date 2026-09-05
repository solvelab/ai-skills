## Context

`scripts/validate-spec-rite.py` (338 linhas em `bfc400d`) é o único gate deste repositório que lê o
**diff** e o **corpo do PR**: `resolve_base()` tenta `SPEC_RITE_BASE`, `GITHUB_BASE_REF`,
`origin/master`, `origin/main`; `changed_paths()` roda `git diff --name-only <base>...HEAD`;
`read_pr_body()` lê `pull_request.body` do arquivo em `GITHUB_EVENT_PATH` (nunca via `env:`, que o
Actions imprime no log — run 32648727841), com `PR_BODY` como override; `WAIVER` é ancorado no começo
da linha, casado como texto, com `MIN_REASON = 8`; `evaluate()` é função pura das entradas, e é o
que `--selftest` exercita com `DEFECTS` e `SILENT`; `main()` imprime um skip em evento que não é
`pull_request` e falha com `S0` quando não há base em CI.

`metadata.version` hoje: presença e formato verificados pelo step *Skill frontmatter checks*
(`grep -qE '^  version: [0-9]+\.[0-9]+\.[0-9]+'` sobre o bloco de frontmatter). Nenhum script lê o
valor. `generate.sh` copia o `SKILL.md` inteiro para `claude/skills/<x>/` e `plugins/<grupo>/skills/<x>/`,
então a linha aparece também nas árvores geradas.

Dois pontos do histórico servem de fixture real, medidos em `bfc400d` (2026-09-05):

- `cf767ee` (issue #76): 20 caminhos em `skills/`, 13 skills; 12 com `version` idêntica na base e
  no HEAD; `code-locale` sem `SKILL.md` na base (skill nova).
- PR #122, squash `e13c16a` sobre `d2918ed`: 6 skills, todas com `version` maior no HEAD
  (`1.2.1→1.3.0`, `1.0.1→1.1.0`, `1.4.0→1.5.0`, `1.2.0→1.3.0`, `1.7.0→1.8.0`, `1.0.0→1.1.0`).

## Goals / Non-Goals

**Goals**

- Um PR que altera qualquer coisa sob `skills/<x>/` sem mover `metadata.version` de `<x>` e sem a
  linha de dispensa reprova, nomeando a skill, a versão na base, a versão no HEAD e as duas saídas.
- `--selftest` com um defeito injetado por regra e os casos que têm de ficar mudos, no CI.
- A dispensa é PR-wide, para que uma varredura catálogo-inteiro custe uma linha.
- O gate diz o que não cobre, no próprio docstring.

**Non-Goals**

- Bumps retroativos nas 20 skills medidas (fora de escopo pela issue).
- Decidir **quanto** bumpar (major/minor/patch) — o gate exige movimento para cima, não magnitude.
- Ler `metadata.version` em algum consumidor (`install.sh`, wrappers): o campo continua informativo
  para máquinas; o que muda é que a promessa ao humano passa a ser medida.
- Tocar `scripts/validate-spec-rite.py`: o novo gate importa dele apenas `MIN_REASON`, para que as
  duas dispensas exijam o mesmo tamanho de motivo por construção, não por cópia.
- Tocar qualquer outro step de `ci.yml`.

## Decisions

### D1 — Gate separado, no mesmo idioma, não uma regra a mais no spec-rite

`validate-spec-rite.py` responde "existe uma change ligada a este diff?"; a pergunta aqui é "cada
skill editada moveu sua versão?". São inputs diferentes (o segundo lê o conteúdo de dois blobs por
skill) e saídas diferentes (achados por skill). Misturar as duas no mesmo `evaluate()` tornaria o
selftest de cada uma dependente da outra. O novo script copia a **forma** — as mesmas funções de
plumbing com os mesmos nomes, o mesmo leitor do corpo, o mesmo skip, o mesmo `annotate` — para que
quem já leu um leia o outro sem custo.

### D2 — "Conteúdo mudou" é qualquer caminho sob `skills/<x>/`, exceto a linha `  version:`

Para cada skill com caminho alterado no diff `<merge-base>...HEAD`: se algum caminho alterado não é o
`SKILL.md`, o conteúdo mudou. Se só o `SKILL.md` mudou, os dois blobs são comparados com todas as
linhas `  version:` removidas; iguais → só a versão mudou → a skill não entra na regra do bump
(mas entra na regra de regressão, D4). Rename e whitespace disparam o gate — aceito na issue: é
exatamente o que a dispensa escrita resolve.

Alternativa rejeitada: contar só linhas do corpo do `SKILL.md`, ignorando `references/`. O commit
`bb6b391` moveu 139 arquivos para `references/` "sem perder linha"; pelo critério do README seria
"sem mudança de comportamento". Mas um `references/*.md` é conteúdo que o agente lê; excluí-lo cria a
classe de PR que edita doutrina sem tocar o `SKILL.md` e passa mudo. O custo (uma linha de
dispensa em varreduras estruturais) foi aceito na decisão.

### D3 — Árvores geradas nunca contam; skill nova passa; skill removida passa

`claude/`, `codex/`, `cursor/`, `copilot/` e `plugins/` são saída de `generate.sh` e já têm o seu
gate (*Wrappers in sync*). Um diff confinado a elas não é uma edição de skill. Skill sem `SKILL.md`
na base não tem versão anterior contra a qual "subir" — passa. Skill sem `SKILL.md` no HEAD foi
removida — não há versão a mover, e a remoção é regulada por `skills-catalog`, não por este gate.

### D4 — Versão que desce é achado sempre; a dispensa cobre só o bump ausente

`Skill-version: none — <motivo>` diz "esta edição não merece bump". Não existe motivo legítimo para
`1.8.0 → 1.7.0`; um número que anda para trás é erro de edição, e a dispensa não o cobre. Regra
separada (`V2`), com mensagem própria, para que o achado nomeie a regressão e não peça uma linha de
dispensa que não resolveria nada.

### D5 — A dispensa é PR-wide, com o mesmo `MIN_REASON` do spec-rite

Uma linha por skill transformaria uma varredura de 12 skills em 12 linhas de boilerplate — o risco
que a issue nomeou. Uma linha cobre o PR todo; o motivo tem de ter pelo menos `MIN_REASON`
caracteres, importado de `validate-spec-rite.py` (não copiado) para que os dois gates nunca exijam
tamanhos diferentes. Uma linha `Skill-version: none` sem motivo é achado (`V3`), com a mesma
separação que o spec-rite faz entre "motivo curto" e "sem motivo".

### D6 — Skip em evento que não é `pull_request`, impresso, como o spec-rite

Em `push` para `master` não há corpo de PR a ler e o diff contra a própria base é vazio; o gate
imprime `skill-version gate: skipped (event push, not pull_request)` e sai 0. Em CI sem base
resolvível, falha com `V0` — um gate que não consegue medir não aprova. Fora de CI sem base, imprime
o skip e sai 0, como o irmão.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| A linha `Spec-rite:` / `Skill-version:` no corpo do PR | `execute-backlog` (`references/spec-rite.md`, *In the PR body*) | link — a seção ganha um parágrafo com a segunda linha; o README aponta para o script, não restata o protocolo |
| Um check declara dentro de si o que não cobre | `skills-authoring` (*Authoring rules are machine-enforced*) + `verify-before-claiming` | already canonical — o novo script traz o seu KNOWN LIMIT no docstring |
| Um gate carrega selftest com um defeito injetado por regra | `skills-authoring` (*Authoring rules are machine-enforced*) | already canonical — `--selftest` com `DEFECTS`/`SILENT` |
| Bump de `metadata.version` a cada mudança de skill | `README.md` (contrato ao contribuidor) + requisito novo em `skills-authoring` | move — a regra deixa de ser só prosa do README e ganha um requisito e um gate; o README passa a nomear o gate |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — grupo de simulação de `tasks.md` |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — nomes de função, labels de selftest, nome do step em inglês |

## Risks / Trade-offs

- **A dispensa vira boilerplate.** → `MIN_REASON` compartilhado com o spec-rite; e a linha é uma por
  PR, não por skill, então uma varredura honesta custa uma frase.
- **Rename/whitespace/typo dispara o gate.** → Aceito na issue; a linha de dispensa é a saída, e o
  achado a nomeia.
- **O gate reprova o próprio PR desta change** (edita `skills/execute-backlog/references/spec-rite.md`).
  → `execute-backlog` sobe `1.8.0 → 1.8.1` no mesmo PR; o gate fica mudo por bump, não por dispensa.
- **`git show <base>:skills/<x>/SKILL.md` em skill com muitos caminhos alterados custa um processo por
  skill.** → 35 skills no catálogo; pior caso ~70 `git show`, medido em segundos no CI. Sem cache por
  desenho: simplicidade sobre velocidade num gate que roda uma vez por PR.
- **Semver com pré-release (`1.2.3-beta`).** → O gate compara a tupla `(major, minor, patch)`; o
  step de frontmatter só exige esse prefixo. Um bump só de pré-release conta como "não moveu" —
  declarado no KNOWN LIMIT; nenhuma skill do catálogo usa pré-release hoje.

## Open Questions

Nenhuma. O que poderia virar achismo — quais skills `cf767ee` e o PR #122 tocaram e com que
versões, o que `generate.sh` copia, o que o step de frontmatter verifica — foi medido e está em
`tasks.md` com comando e saída.
