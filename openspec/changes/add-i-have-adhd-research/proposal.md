# Change: Medir o i-have-adhd contra o caveman no modelo diário antes de qualquer adoção

## Why

O item #246 pede um parecer sobre `ayghri/i-have-adhd` que não seja achismo. Três fatos medidos na
sessão de grooming (2026-09-10) dizem por que o primeiro item é uma medição e não uma skill:

1. **O catálogo não tem skill de forma da resposta e a doutrina de medição exclui julgar prosa.**
   `grep -il 'brevity\|preamble\|response style' skills/*/SKILL.md` -> só `fivem-nui-react`, sem
   relação; `research/lean-code/protocol.md:30` diz *"What is not measured: chat output ... quality
   as judged by an LLM"*. Uma skill cujo efeito inteiro é a forma do texto não tem `added_lines`
   para contar: ou se julga, com o método declarado, ou não se mede.

2. **O upstream mediu, mas noutro modelo, contra baseline nu, pelo prompt e reprovou no próprio
   gate.** `evals/RESULTS.md` (clone em `ff690b6`): opus-4-8, 14 casos, 3 trials, juiz da mesma
   família; ponderado 4.045 -> 4.473; *"Release gate: FAILED"* (3 blockers); `partial-success`
   −0.63 com o juiz anotando *"asserts 'missing auth header' as the definitive cause ... without
   any evidence"*. O harness injeta a skill no prompt (`scripts/run_evals.py:205-216`,
   `<response_style>`), não pelo hook `SessionStart` que é o caminho real de instalação.

3. **O mantenedor já roda um incumbente.** Plugin `caveman` 2.3.1 (`installed_plugins.json`,
   `gitCommitSha 81536f57b3…`), hook `SessionStart` que injeta `skills/caveman/SKILL.md` filtrado
   pelo nível ativo (`src/hooks/caveman-activate.js:257-341`). Um candidato que vence o baseline nu
   e perde para o caveman não é ganho.

Validado offline nesta máquina em 2026-09-10: `python3 scripts/run_evals.py validate` ->
`Evaluation cases are valid.`; `python3 -m unittest discover -s tests` -> `OK` (Python 3.14.5);
`claude --version` -> `2.1.267`, com as nove flags do runner do upstream e `--plugin-dir`,
`--include-hook-events`, `--setting-sources` presentes no `--help`.

## What Changes

- Cria `research/i-have-adhd/`, fora do que `generate.sh` publica (`generate.sh` copia só
  `skills/` para `plugins/`): `protocol.md` (condições, modos de injeção, métricas, vereditos
  ADOPT / NO-CLAIM / REJECT escritos antes de rodar, congelado com o sha), `run.py`
  (`--selftest`, `--prepare-conditions`, `--probe`, `--matrix`, `--judge`, `--report --export`),
  `PIN` (símbolos importados de `research/lean-code/run.py`), `README.md`, `results.md`,
  `results/`.
- Vendoriza o harness do upstream **sem modificação** em `research/i-have-adhd/vendor/i-have-adhd/`
  (`scripts/run_evals.py`, `scripts/judge.py`, `evals/cases.jsonl`, `evals/rubric.md`, os testes,
  o plugin inteiro que o `--plugin-dir` carrega — `.claude-plugin/plugin.json`, `hooks/`,
  `skills/i-have-adhd/SKILL.md` — e `LICENSE`), com `PIN` (commit, data, sha256 por arquivo).
  `run.py` importa `run_evals` e `judge` por `importlib`; nunca copia.
- Vendoriza a proveniência do comparador em `research/i-have-adhd/vendor/caveman/`
  (`skills/caveman/SKILL.md`, `LICENSE` da parte MIT, `PIN` com versão, commit e sha256 do que o
  hook carrega). O plugin em si é carregado do cache instalado por `--plugin-dir`, porque é o que
  o mantenedor roda.
- Três condições: `baseline` (prompt nu), `comparator` (caveman), `candidate` (i-have-adhd). Dois
  modos de injeção: `prompt` (o do upstream, `<response_style>` no prompt) e `plugin`
  (`CLAUDE_CONFIG_DIR` de rascunho por condição + `--plugin-dir`; para o candidato, o flag
  `.i-have-adhd-always` que o hook dele lê). `--setting-sources ""` em toda célula, como o upstream.
- Sonda paga e pequena antes da matriz: no modo `plugin`, `--output-format stream-json
  --include-hook-events` tem de mostrar o hook `SessionStart` 3/3 em `candidate` e `comparator` e
  0/3 em `baseline`; no modo `prompt`, 0/3 nas três. Sem sonda passada, nenhuma célula paga roda.
- Métricas: as cinco do juiz do upstream (rubrica pinada por sha256), o `blocker`, e duas contadas
  nas mesmas respostas: `output_tokens` (do `usage` do CLI) e `forbidden_phrase_hits` (as frases
  que a regra 10 do próprio upstream proíbe).
- Juiz: `judge.py` do upstream, cego, mesmo modelo do gerador (`claude-fable-5-1`), um grupo
  `(case, trial)` por chamada; um arquivo de respostas e um de notas por modo.
- Sequência: piloto Haiku n=1 (nunca reportado) -> sonda -> matriz no modelo diário, 14 casos ×
  3 condições × 3 trials × 2 modos -> juiz -> `results.md` com o veredito lido pela tabela.

## Capabilities

### Modified Capabilities

- `skills-catalog`: o requisito *A published cost claim carries re-runnable backing* ganha o caso
  do claim de **qualidade da resposta**: juiz LLM permitido só com juiz nomeado, cegamento
  registrado, rubrica pinada e uma quantidade contada ao lado; o incumbente do mantenedor é uma
  condição, não nota de rodapé; uma regra cujo caminho real é hook é medida pelo hook em pelo
  menos um conjunto de condições, e cada número diz o modo de injeção; um score de chat sem
  ferramentas não é vendido como comportamento agêntico.

## Impact

- Novo diretório `research/i-have-adhd/` — versionado e revisável, nunca publicado.
- Nenhum arquivo em `skills/`, `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`,
  `generate.sh`, `README.md` da raiz ou `.github/workflows/`. Nenhuma skill afetada.
- Acoplamento novo e declarado: `research/i-have-adhd/run.py` importa símbolos de
  `research/lean-code/run.py` (`parse_stream`, `run_process`, `strip_export`, `claude_version`,
  `now_stamp`, `outside_repo`) e do harness vendorizado; o `--selftest` carrega um teste de
  contrato sobre cada símbolo e é o gate do `--matrix`.
- Custo: 252 células + 84 grupos de juiz no modelo diário. O run do upstream custou $2.67 + $0.92
  por 84 linhas em opus-4-8; o preço do modelo diário não é conhecido aqui — o teto `--budget-usd`
  por invocação (≤ 25, limite do harness do upstream) decide, não a estimativa.
- Depende de `claude` CLI no PATH (probado: `2.1.267`), `node` (hook do candidato e do
  comparador) e do plugin caveman instalado no cache (comparador em modo `plugin`).
