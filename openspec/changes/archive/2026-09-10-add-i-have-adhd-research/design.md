# Design — research/i-have-adhd

## Context

O item #246 pede que o parecer sobre `ayghri/i-have-adhd` seja uma medição, não uma leitura. A casa
já tem forma: `research/lean-code/` e `research/tdd/` medem uma doutrina no modelo diário do
mantenedor, com condições provadas isoladas por sonda e o veredito congelado antes da primeira
célula paga.

O que muda aqui é a natureza do que se mede. O lean-code conta linhas; o tdd lê ordem no
transcrito. Uma skill de forma da resposta não deixa nada no diff e nenhum contador diz se o texto
ficou "acionável". O upstream resolveu isso com um juiz LLM cego pareado, e o desenho abaixo reusa
esse instrumento em vez de inventar outro — declarando, em cada número, o que um juiz não prova.

## Goals / Non-Goals

**Goals:**

- Responder uma pergunta só: instalado como se instala, no modelo diário, o i-have-adhd faz melhor
  do que o caveman que já está ligado?
- Medir pelos dois caminhos — o do upstream (prompt) e o real (plugin + hook) — e dizer de qual
  veio cada número.
- Reusar o harness do upstream sem modificá-lo, e a camada de processo e sonda do lean-code sem
  copiá-la.
- Congelar condições, modos, métricas e vereditos antes da primeira célula paga.

**Non-Goals:**

- Escrever qualquer skill, hook ou plugin no catálogo; mudar `~/.claude` do mantenedor.
- Casos novos. Os 14 do upstream ficam intactos para comparabilidade com o número publicado dele.
- Fase agêntica com ferramentas. Só existe como item 3 se este der sinal.
- Um juiz de outra família como controle. É o item 3, se houver.
- Gate de CI "plugin carrega" — item próprio, se o mantenedor quiser.

## Decisions

**D1 — O harness do upstream é vendorizado inteiro e importado, nunca reescrito.**
`scripts/run_evals.py` e `scripts/judge.py` são stdlib, têm `main()` guardado por
`if __name__ == "__main__"` (`run_evals.py:407`, `judge.py:333`) e testes próprios que passam aqui
(`unittest discover -s tests` -> `OK`). `judge.py` faz `sys.path.insert` e `import run_evals`
(`judge.py:14-17`), então o carregador local registra `run_evals` em `sys.modules` antes de
carregar `judge`. O `PIN` do vendor grava commit, data e sha256 por arquivo; o `--selftest` refaz
os hashes e roda os testes do upstream.

**D2 — O laço de células é local, porque o do upstream acopla rótulo e prompt.**
`run_evaluations` (`run_evals.py:245-340`) deriva o prompt do rótulo da condição: `candidate` e
`comparator` recebem obrigatoriamente `<response_style>` (`_condition_prompt`, `:205-216`). No
modo `plugin` a regra entra pelo hook e o prompt tem de ser nu, mas o rótulo tem de continuar
`candidate`. Em vez de rotular tudo `baseline` e reescrever o campo depois — o que mente no
arquivo até o pós-processamento — `run.py` carrega um laço próprio de ~60 linhas que reusa
`_parse_response`, `_neutral_cwd`, `read_jsonl`, `completed_keys` e `load_cases` do upstream,
escreve linhas com o mesmo esquema (`case_id, trial, condition, runner, response, usage,
cost_usd`) e é resumível pela mesma chave. O juiz do upstream lê essas linhas sem saber a diferença.

**D3 — Modo `plugin`: `--plugin-dir` + `CLAUDE_CONFIG_DIR` de rascunho por condição.**
`--setting-sources ""` (o isolamento do upstream) descarta o `settings.json` do usuário e com ele
`enabledPlugins`; `--plugin-dir <path>` carrega um plugin "for this session only" (probado no
`--help` de `2.1.267`). O candidato carrega `vendor/i-have-adhd/` inteiro (manifest, `hooks/`,
`skills/`), e o `CLAUDE_CONFIG_DIR` da condição carrega o flag `.i-have-adhd-always` que
`hooks/always-on.mjs` lê. O comparador carrega o cache instalado do caveman (`installed_plugins.json`
-> `81536f57b330`), porque é isso que roda na máquina do mantenedor; o hook dele escreve
`.caveman-active` no `CLAUDE_CONFIG_DIR` da condição — evidência secundária de que disparou. O
baseline não carrega plugin. Se `--plugin-dir` não disparar `SessionStart` em `-p`, a sonda diz
e o modo `plugin` não roda: o protocolo registra o fato em vez de fingir.

**D4 — A sonda prova o hook, não uma sentinela.**
No lean-code a regra entra por `CLAUDE.md` e a sentinela prova que o arquivo foi lido. Aqui a
regra entra por hook, então a prova é o evento: uma chamada por condição com `--output-format
stream-json --include-hook-events`, lida por `parse_stream` do lean-code (`hook_names`). Passa
quando `candidate` e `comparator` mostram `SessionStart` 3/3 e `baseline` 0/3 (modo `plugin`), e
0/3 nas três (modo `prompt`). `probe_gate` do lean-code não serve — ele conta `caveman` como hook
do mantenedor (`MAINTAINER_HOOK_NAMES`), e aqui o caveman é tratamento; a regra da sonda é local.

**D5 — O juiz é o do upstream, pareado, cego, mesmo modelo; e nunca sozinho.**
`judge.py` já faz o que a doutrina exige: rótulos permutados por hash do grupo, só a região
`judge:begin/end` da rubrica chega ao juiz, grupo incompleto é reportado. O juiz é o mesmo modelo
do gerador — limitação herdada do upstream e escrita no protocolo. Ao lado de cada score há duas
quantidades contadas nas mesmas respostas: `output_tokens` (do `usage` que o CLI devolve e a linha
já guarda) e `forbidden_phrase_hits` (as frases que a regra 10 do próprio upstream proíbe, lista
literal no protocolo). Contadas, nunca julgadas.

**D6 — O veredito é lido contra o comparador, em ambos os modos.**
A tabela do protocolo (ADOPT / NO-CLAIM / REJECT) compara candidato com comparador, exige
correctness e safety a ≤ 0.1 do baseline, zero blocker fora de `agent-owned-edit` (caso que o
próprio upstream declarou impassável sem ferramentas), e trata `partial-success` como gatilho de
REJECT quando o blocker "causa afirmada sem evidência" reaparece em ≥ 2 de 3 trials — porque esse
é o anti-padrão de `verify-before-claiming`, e um ganho de forma não paga uma perda de grounding.
Modos que discordam dão NO-CLAIM.

**D7 — Modelo e custo.** Gerador e juiz em `claude-fable-5-1` (o `model` de
`~/.claude/settings.json`, sem o sufixo de janela). Piloto em Haiku n=1 em dois casos, nunca
reportado. `--budget-usd` por invocação, teto 25 (limite do harness do upstream); a matriz é
resumível por linha, então um estouro para e continua depois.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Método de medição de ganho de comportamento (condições, célula, sonda, vereditos antes do número) | `research/lean-code/protocol.md` | already canonical — este protocolo cita e reusa; o que muda (juiz, hook) está em D4–D5 |
| Claim publicado carrega backing re-executável, método e alcance | `skills-catalog` spec (MODIFIED aqui) | move — o requisito ganha o caso do claim de qualidade da resposta |
| Não afirmar o que não foi probado; relatar a lacuna | `verify-before-claiming` | link — D3 e D6 aplicam; o grupo Evidence & Sources cita, não restata |
| Reusar antes de escrever (a escada) | `lean-code` | link — D1 e D2 são a escada aplicada |
| Simulação pelo caminho real antes de considerar entregue | `execute-backlog` (passo 8) e o grupo S do schema | already canonical — o modo `plugin` é o caminho real |
| Metodologia adversarial (quebrar o que já foi escrito) | `bug-hunter` | link — fora do escopo desta medição |
| A forma da resposta em si (as dez regras) | `vendor/i-have-adhd/skills/i-have-adhd/SKILL.md` (upstream) | **não mora aqui** — é o tratamento medido, não doutrina do catálogo |

## Risks / Trade-offs

- **O veredito pode ser REJECT ou NO-CLAIM.** São resultados legítimos, escritos antes de rodar.
- **`--plugin-dir` pode não disparar `SessionStart` em `-p`.** D3/D4: a sonda decide; sem hook, o
  modo `plugin` não roda e o resultado diz por quê.
- **Juiz da mesma família pode premiar o próprio estilo.** Declarado; o controle de outra família
  é item 3.
- **Três trials é pouco.** O próprio upstream registrou SD por caso até 0.95. O protocolo trata
  deltas por caso abaixo de 0.5 como ruído e lê o veredito no agregado.
- **Acoplamento com dois harnesses.** `PIN` + teste de contrato no `--selftest`, que é o gate do
  `--matrix`.
- **Custo desconhecido no modelo diário.** Teto por invocação, piloto barato, comando de cada
  célula gravado antes de rodar.
