# Change: Skill tdd — a ordem do teste ganha casa canônica, sem número

## Why

Três fatos, todos medidos ou lidos nesta sessão:

1. **O catálogo não diz quando o teste é escrito, e o que diz é o contrário.**
   `grep -rniE "\btdd\b|test-driven|red[- ]green|test first|failing test"` sobre `skills/`,
   `claude/`, `plugins/` e `openspec/` -> zero ocorrências reais. O fluxo publicado em
   `skills/execute-backlog/SKILL.md:121-126` fixa passo 7 **Implement**, passo 8 **Tests**.
   `skills/bug-hunter/SKILL.md:4` roda *after implementing a change*.
   `skills/lean-code/SKILL.md:123-131` fixa o piso de uma checagem e diz explicitamente que o que
   está além dele é `bug-hunter` — sem dizer nada sobre quando a checagem é escrita.

2. **A doutrina foi medida e o efeito de comportamento é total.** `research/tdd/` (#182, mergeada em
   `6d85973`, change arquivada em `21f228c`): 36 células no `opus[1m]`, n=3, dois arms.
   `order` — o teste escrito antes da implementação — e a escrita de teste vão de **0/18** no
   baseline para **18/18** no arm de tratamento, e todos os 18 testes falham de verdade na semente
   limpa (`red` 18/18). Não há sobreposição entre os arms em nenhuma das seis tarefas.

3. **E o veredito proíbe citar número.** O efeito em correção não é mensurável ali: o baseline já
   acertava a suíte oculta 18/18, então não havia folga. Pela letra de `research/tdd/protocol.md`
   isso é **NO-CLAIM**, cuja linha diz *no number appears in any README or SKILL.md*.

A skill existe pela disciplina que impõe, não por um ganho publicado. E o mapa canônico de
`openspec/specs/skills-authoring/spec.md:11-21` não tem entrada para ordem de teste, então publicar
sem resolver isso deixaria duas fontes divergentes sobre a mesma regra.

## What Changes

- Cria `skills/tdd/SKILL.md` (`metadata.category: testing`, logo plugin `ai-skills-testing` por
  derivação) e `skills/tdd/references/track-python-pytest.md`.
- O núcleo da doutrina é o texto **efetivamente medido**, `research/tdd/arms-block.md`. A `SKILL.md`
  é superconjunto e não pode contradizê-lo.
- O mapa canônico de `skills-authoring` ganha `test order → tdd`, e o requisito ganha um cenário
  para o par de skills que tocam o mesmo assunto em tempos diferentes (`tdd` antes, `bug-hunter`
  depois).
- `skills-catalog` ganha o requisito *Test order has a canonical home*, incluindo a regra de que
  uma skill cuja única medição deu NO-CLAIM não carrega número.
- Cross-links recíprocos em `skills/execute-backlog/SKILL.md` (passo 8, opt-in, ordem default
  intacta), `skills/bug-hunter/SKILL.md`, `skills/lean-code/SKILL.md` e
  `skills/python-rest-api/SKILL.md`. `metadata.version` sobe em cada uma.
- `./generate.sh` e as duas tabelas do `README.md`.

**Não muda**: a ordem default de `execute-backlog`; nada em `research/`; nenhum número em lugar
nenhum.

## Capabilities

### New Capabilities

Nenhuma capability nova de spec: a doutrina entra como requisito ADDED em `skills-catalog`.

### Modified Capabilities

- `skills-catalog`: ADDED *Test order has a canonical home* — a skill que governa quando o teste é
  escrito: o teste primeiro e falhando pela razão certa, o que torna esse teste legítimo, as
  fronteiras que o enunciado obriga, quando o ciclo **não** se aplica, o caráter opt-in que não
  inverte o fluxo publicado, e a proibição de número sob um veredito NO-CLAIM. Quatro cenários.
- `skills-authoring`: MODIFIED *Single canonical home per rule* — o mapa canônico ganha `tdd`
  (ordem do teste), mais um cenário para duas skills que tocam o mesmo assunto em tempos diferentes.

## Impact

- Catálogo passa de 36 para 37 skills; `ai-skills-testing` de 2 para 3, com a descrição regenerada
  por `generate.sh:241-250` e conferida por `validate-repo-hygiene.py` (H3).
- Quatro skills existentes ganham cross-link e sobem `metadata.version`
  (`scripts/validate-skill-version.py`).
- Wrappers em `claude/`, `codex/`, `cursor/`, `copilot/` e `plugins/testing/` regenerados; o gate de
  sync do CI (`.github/workflows/ci.yml:49-68`) reprova se ficarem fora do commit.
- Nenhum número de ganho entra no repositório publicado.
