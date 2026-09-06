# Change: Harness, arms isolados e baseline medido para a doutrina TDD

## Why

O mantenedor quer publicar uma skill `tdd` no catálogo (item #183). Antes de escrevê-la, três
fatos medidos nesta sessão dizem por que o primeiro item é um harness e não a skill:

1. **O catálogo não carrega nenhuma doutrina de ordem de teste.**
   `grep -rniE "\btdd\b|test-driven|red[- ]green|test first|failing test" skills/ claude/ plugins/ openspec/`
   -> zero ocorrências reais; o único match é `skills/claude-statusline/SKILL.md:79`
   (`green <50`), um limiar de cor de barra. O que existe é o contrário: o fluxo publicado em
   `skills/execute-backlog/SKILL.md:116-126` fixa passo 7 **Implement**, passo 8 **Tests**;
   `skills/bug-hunter/SKILL.md:4` roda *after implementing a change*; e
   `skills/lean-code/SKILL.md:123-131` fixa o piso de uma checagem executável sem dizer quando ela
   é escrita.

2. **Uma skill de ordem de teste é doutrina de comportamento, e prosa não a valida.**
   O que a skill promete é inverter a sequência em que o agente escreve arquivos. Frontmatter
   uniforme, `openspec validate --strict` verde e revisão de prosa não observam essa sequência. O
   grupo `Simulation & Field Proof` do schema (`openspec/schemas/skills-rite/templates/tasks.md`,
   S.1-S.3) prova que o artefato foi exercitado pelo caminho real — não que ele mudou o resultado.
   Sem arms comparados, a skill do item 2 só poderia citar folclore, e o catálogo já rejeita isso
   (`skills-catalog`: *A published cost claim carries re-runnable backing*).

3. **A casa para esse tipo de prova já existe e tem forma.** `research/lean-code/` (#145) e
   `research/svg-animation/` classificam ou medem **antes** de a skill ser escrita.
   `research/lean-code/protocol.md` congela arms, métricas e os quatro vereditos antes da primeira
   célula paga; `research/lean-code/run.py` (2748 linhas) carrega `--selftest`, `--prepare-arms`,
   `--probe-isolation`, `--matrix`, `--report --export`; e o número resultante aparece em
   `README.md:652` com as condições ao lado.

Sem harness auto-testado, arms provados por sonda e um número medido no modelo diário, o item #183
teria de escolher entre publicar uma doutrina não medida ou não publicar nada.

## What Changes

- Cria `research/tdd/`, fora do que `generate.sh` publica: `protocol.md` (arms, célula, métricas,
  vereditos SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE escritos antes de rodar, congelado com o sha),
  `run.py` (`--selftest`, `--prepare-arms`, `--probe-isolation`, `--matrix`, `--classify`,
  `--report --export`), `arms-block.md` (o bloco de doutrina que define o arm de tratamento),
  `scorer-venv.txt`, `PIN`, `README.md`, `results.md`, `results/`.
- Dois arms: `baseline` (o ambiente do mantenedor sem hooks, plugins nem doutrina) e `doctrine`
  (o mesmo, mais o bloco de `arms-block.md` anexado ao `CLAUDE.md` da célula). O arm `skill` — a
  skill publicada carregada como project skill — é de #183 e **não** roda aqui.
- Quatro métricas por célula: `order` (o primeiro write em caminho de teste veio antes do primeiro
  em caminho de produção, lido do transcrito `stream-json`), `red` (a suíte que o agente escreveu
  falha quando aplicada sozinha sobre a semente), `green` (o código final passa numa **suíte
  oculta** que o agente nunca viu) e `test_added_lines` (guarda contra inflar suíte).
- Seis tarefas em `research/tdd/tasks/`, Python/pytest, cada uma com semente commitada, prompt e
  suíte oculta: três de comportamento especificado, duas com fronteira no enunciado e uma de
  correção de bug.
- `run.py` **importa** a camada genérica de `research/lean-code/run.py` (arms, isolamento,
  processo, diff, agregação) em vez de copiá-la; `PIN` grava o sha lido e o `--selftest` carrega um
  teste de contrato sobre cada símbolo importado.
- A célula do TDD não herda o `NO_RUN` do lean-code: aquele texto diz *"Only the code you write is
  measured, not its execution"*, o que enviesa um experimento sobre ordem de teste. `NO_RUN_TDD`
  proíbe rodar servidor, instalar dependência e abrir browser, e não diz nada sobre escrever teste.
- Bash permanece bloqueado na célula (`--disallowedTools Bash`, herdado do aparato de isolamento
  provado). O KNOWN LIMIT correspondente fica escrito no protocolo: mede-se a ordem de escrita e a
  qualidade do que sobra, não o laço de feedback vivido pelo agente.

## Capabilities

### Modified Capabilities

- `skills-catalog`: o requisito *A published cost claim carries re-runnable backing* ganha o caso
  do claim de **ordem de produção** — a fonte do dado de ordem tem de ser o transcrito, e o registro
  tem de declarar se o agente medido podia executar alguma coisa, porque um claim sobre ciclo
  vermelho-verde medido com execução desligada é um claim sobre ordem de escrita.

## Impact

- Novo diretório `research/tdd/` — versionado e revisável, nunca publicado: `generate.sh:224-234`
  copia apenas `skills/` para `plugins/`.
- Nenhum arquivo em `skills/`, `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`,
  `generate.sh`, `README.md` da raiz ou `.github/workflows/`.
- Acoplamento novo e declarado: `research/tdd/run.py` importa símbolos de
  `research/lean-code/run.py`. O contrato é testado pelo `--selftest`, que é o gate do `--matrix`.
- Custo: 6 tarefas x 2 arms x n=3 = 36 células. A $0.35/célula medida em #145 (27 células, $9.4529),
  cerca de $13, com teto por `--budget-usd`.
- Depende de `claude` CLI no PATH (probado: `2.1.263`) e de um venv fixado para a suíte oculta —
  `python3 -c "import pytest"` falha no python do sistema (`3.14.5`).
