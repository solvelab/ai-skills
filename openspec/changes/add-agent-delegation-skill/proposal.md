# Change: Skill agent-delegation — a fronteira de artefato ganha casa canônica

## Why

Três decisões de arquitetura já foram tomadas neste repositório, e nenhuma das três tem casa
canônica. Todas foram lidas nesta sessão, em `55d8a48`:

1. **Até onde um subagente vai.** `skills/backlog/SKILL.md:84` e `skills/execute-backlog/SKILL.md:101`
   despacham o `Explore` built-in, e só para coleta de contexto. O limite foi escrito uma vez,
   dentro de uma change que hoje está arquivada:
   `openspec/changes/archive/2026-07-18-add-backlog-skill/design.md:20` — *"Subagents (Explore) are
   used internally for context collection only."* Arquivado não é publicado.

2. **O que vira gate e o que não vira.** O hook
   [`claude/global/hooks/verify-rite.py`](https://github.com/solvelab/ai-skills/blob/master/claude/global/hooks/verify-rite.py)
   recusa, em comentário, um detector PreToolUse citando *"advisory mechanisms are not sold as hard
   gates"*. A regra existe num comentário de implementação.

3. **Qual modelo e qual effort.** O único texto sobre isso é
   [`claude/global/personal-rules.md`](https://github.com/solvelab/ai-skills/blob/master/claude/global/personal-rules.md),
   seção *Model & Effort Tiering*, num arquivo que se auto-declara config pessoal do mantenedor e
   diz ao leitor para **não** adotar os defaults. Não é skill, não está entre as 37, não é instalada
   por `npx skills`, não é conferida por nenhum gate.

`openspec/specs/skills-authoring/spec.md:11-23` manda que toda regra transversal seja definida em
exatamente uma skill. Esta regra não está definida em nenhuma. O `README.md:536-540` define o que é
uma skill e não define nem hook, nem script de CI, nem agente — de modo que a escolha do artefato é
feita caso a caso, sem critério escrito.

O custo já está agendado: o item #198 cria a camada `agents/`. Sem o critério publicado antes, o
primeiro agente entra sem teste de admissão e os seguintes entram por imitação.

## What Changes

- Cria `skills/agent-delegation/SKILL.md` (`metadata.category: process`, logo plugin
  `ai-skills-workflow` por derivação), com quatro blocos: a fronteira de artefato (skill / hook /
  script de CI / agente), os três testes que qualificam um trabalho para delegação, o tiering de
  modelo e effort, e a regra de menor privilégio com contrato de saída.
- Cada linha da tabela de fronteira cita um artefato **real deste repositório** como exemplo, para
  que a regra não seja prosa genérica sobre "quando usar agentes".
- `claude/global/personal-rules.md` deixa de **definir** o tiering e passa a linkar a skill em no
  máximo uma linha, cumprindo a lei de casa canônica única.
- O mapa canônico de `skills-authoring` ganha `delegação e fronteira de artefato → agent-delegation`.
- `skills-catalog` ganha o requisito *Delegation and the artifact boundary have a canonical home*.
- Cross-links recíprocos em `skills/lean-code/SKILL.md` (quanto código × qual artefato),
  `skills/verify-before-claiming/SKILL.md` e `skills/bug-hunter/SKILL.md`. `metadata.version` sobe
  em cada uma das editadas.
- `./generate.sh` e as duas tabelas do `README.md`.

**Não muda**: nenhum agente é criado, nenhum diretório `agents/` nasce, `generate.sh` não ganha
alvo novo, nenhum validador é adicionado — tudo isso é #198, que depende desta change. As duas
skills que já delegam (`backlog`, `execute-backlog`) não mudam de comportamento.

## Capabilities

### New Capabilities

Nenhuma capability nova: a doutrina entra como requisito ADDED em `skills-catalog`.

### Modified Capabilities

- `skills-catalog`: ADDED *Delegation and the artifact boundary have a canonical home* — a skill que
  governa qual artefato uma regra transversal vira e quando despachar um subprocesso se paga:
  os três testes de admissão, os anti-padrões, o tiering por dificuldade, e a exigência de menor
  privilégio e contrato de saída. Quatro cenários.
- `skills-authoring`: MODIFIED *Single canonical home per rule* — o mapa canônico ganha
  `agent-delegation`, mais um cenário para a regra que hoje mora fora do catálogo (config pessoal,
  comentário de hook, change arquivada) e passa a ter casa.

## Impact

- Catálogo passa de 37 para 38 skills; `ai-skills-workflow` de 8 para 9, com a descrição regenerada
  por `generate.sh:241-250` e conferida por `scripts/validate-repo-hygiene.py` (H3).
- Três skills existentes ganham cross-link e sobem `metadata.version`
  (`scripts/validate-skill-version.py`).
- `claude/global/personal-rules.md` perde a definição do tiering — é config pessoal publicada como
  exemplo, não contrato de consumidor; nada que `npx skills` instala depende dela.
- Wrappers em `claude/`, `codex/`, `cursor/`, `copilot/` e `plugins/workflow/` regenerados; o gate
  de sync do CI reprova se ficarem fora do commit.
- **BREAKING para ninguém**: nenhuma skill existente muda de nome, categoria ou comportamento.
