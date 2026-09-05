# Change: Harness, arms isolados e baseline medido para a doutrina lean-code

## Why

O mantenedor quer adotar em `solvelab/ai-skills` a parte de desenvolvimento do `ponytail`
(DietrichGebert/ponytail, MIT, v4.9.0, clone lido em `974d940a` de 2026-09-04): a doutrina "o melhor
código é o que você nunca escreveu". Antes de escrever a skill, três fatos medidos nesta sessão dizem
por que o primeiro item é um harness e não a skill:

1. **O catálogo não carrega doutrina de volume de código.**
   `grep -rniE "yagni|less code|smallest change|speculative|over-engineer|dead code|tech debt"
   skills/ claude/global/personal-rules.md | wc -l` -> `0`, medido em `7709622`. O que existe é
   disciplina de escopo (`skills/verify-before-claiming/SKILL.md`, *Doing / Not doing / Assumptions*;
   `skills/execute-backlog/SKILL.md`, *Scope is law*) e de duplicação em prosa
   (`skills/documentation/SKILL.md`). Nenhuma skill diz quando não escrever código, reusar antes de
   criar, ou qual é o tamanho mínimo de uma mudança.

2. **Os números do upstream têm condições que não são as nossas.**
   `benchmarks/results/2026-06-18-agentic.md` do ponytail: Claude Code `2.1.177`, headless, Haiku 4.5
   (`claude-haiku-4-5-20251001`), `n=4`, LOC por `git diff` — **−54% LOC, −22% tokens, 20/20 seguro**;
   a paráfrase "Follow YAGNI principles, and prefer one-liner solutions" deu −33% e **19/20**
   (perdeu o guard de path traversal no `safe-path`); um benchmark externo citado na issue #126 do
   upstream achou que a doutrina "trims everyday bad-input handling on 5/24 tasks". O mantenedor usa
   `opus[1m]` (`~/.claude/settings.json`, chave `model`) e Claude Code `2.1.261` (`claude --version`).
   Nada disso foi medido nesse modelo nem nesta versão. O catálogo já rejeita esse tipo de claim
   (`skills-authoring`: *A quantified claim carries its measurement*; `skills-catalog`: *A published
   cost claim carries re-runnable backing*).

3. **A lição de contaminação do próprio upstream.** O mesmo relatório registra que um run anterior
   (`2026-06-17-agentic-safety.md`, gap de ~4%) foi marcado SUPERSEDED porque o hook `SessionStart`
   do plugin disparava em **todo** arm, inclusive no baseline — o baseline rodava a skill sem saber.
   O `~/.claude/settings.json` do mantenedor tem hooks em `PreToolUse`, `UserPromptSubmit`,
   `PostToolUse`, `Notification` e `Stop`, e o plugin `caveman` com hook `SessionStart`
   (`plugins/cache/caveman/caveman/81536f57b330/.claude-plugin/plugin.json`). Um baseline rodado
   nesse ambiente mediria o caveman, não o modelo.

Sem harness auto-testado, arms isolados provados por sonda e um baseline no modelo diário, a skill do
item 2 só poderia citar números de outro modelo em outro repositório. O precedente é
`research/svg-animation`: defeitos classificados **antes** de desenhar a skill.

## What Changes

- Cria `research/lean-code/` fora do que `generate.sh` publica: `protocol.md` (arms, célula,
  métricas, vereditos SHIP / INCONCLUSIVE / NO-CLAIM / REWRITE escritos antes de rodar, congelado
  com o sha), `run.py` (stdlib; `--selftest`, `--prepare-arms`, `--probe-isolation`, `--matrix`,
  `--classify`, `--rescore`, `--report --export`), `README.md`, `scorer-venv.txt`.
- Vendoriza do ponytail, com `LICENSE` e `PIN`: `benchmarks/agentic/tasks.py`, `benchmarks/loc.js`
  e os 11 `examples/*.md` (oráculo offline do contador de LOC).
- Seis tarefas do upstream (`safe-path`, `sql-user`, `csv-sum`, `cache`, `reuse-slug`,
  `trace-transfer`) e três do catálogo com semente, referência boa/ruim e `score()` que executa:
  `fastapi-create-item`, `fivem-shop-buy`, `react-use-orders` (este com scorer estrutural,
  declarado como tal).
- Arms em `CLAUDE_CONFIG_DIR` fora do repositório: `settings.json` do mantenedor sem
  `hooks`/`enabledPlugins`/`extraKnownMarketplaces`/`statusLine`/`permissions`, `CLAUDE.md` =
  `personal-rules.md` no ref mais uma linha-sentinela, `skills/` por symlink como o `install.sh`.
- `--matrix` recusa rodar sem `--selftest` verde na mesma invocação; `--report` recusa agregar
  stamps com `claude --version` ou id de modelo diferentes; `--export` remove `session_id`, texto
  de resposta, uuids e caminhos absolutos de HOME.
- Parte B do mesmo item (fora deste PR de harness): sonda de isolamento (Haiku, 3 chamadas),
  piloto (Haiku, n=1) e baseline no modelo diário (n=3, 9 tarefas) →
  `results/<stamp>-baseline-defects.md`.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `skills-catalog`: *A published cost claim carries re-runnable backing* passa a cobrir claims de
  **ganho de comportamento** de uma skill (menos código, guard mantido, reuso) — o registro nomeia id
  do modelo, versão do CLI, `n` e arms, e os arms têm de estar isolados dos hooks e plugins do
  mantenedor, com a sonda registrada ao lado do número.

## Impact

- Skills afetadas: **nenhuma**. Nada em `skills/`, `README.md`, `generate.sh` ou `ci.yml`; a
  composição do catálogo fica idêntica e o `generate.sh` não produz diff.
- Novo diretório `research/lean-code/` (versionado, não publicado), novo dir de change
  `openspec/changes/add-lean-code-research/`.
- Dependências de máquina para rodar (não para o gate): `node` (só o oráculo `loc.js` no selftest),
  `lua` 5.5 (scorer do `fivem-shop-buy`), um venv de scorer com `fastapi`/`httpx`/`pydantic` pinados
  em `scorer-venv.txt`, nunca commitado.
- A skill `lean-code`, a lente de revisão e o bloco em `personal-rules.md` são o item 2
  (`add-lean-code-doctrine`), que cita as contagens do baseline produzido aqui.
