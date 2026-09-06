# Design — research/tdd

## Context

O item #182 pede o aparato que mede uma doutrina de ordem de teste antes de ela virar skill (#183).
A casa já tem forma: `research/lean-code/` mediu uma doutrina de volume de código no modelo diário
do mantenedor, com arms provados isolados por sonda e o veredito congelado antes da primeira célula
paga; `research/svg-animation/` classificou defeitos antes de a skill existir.

O que muda aqui é a natureza da métrica. O lean-code mede uma **quantidade** que o diff já carrega
(`added_lines`). Uma doutrina de TDD promete uma **sequência** — o teste antes da implementação — e
sequência não sobrevive no diff final: `git diff` mostra o estado, não a ordem em que os arquivos
foram escritos. O desenho abaixo existe para tornar essa sequência observável sem inventá-la.

## Goals / Non-Goals

**Goals:**

- Tornar `order`, `red`, `green` e `test_added_lines` mensuráveis por célula, cada um com um
  instrumento que o `--selftest` prova com um defeito injetado.
- Reusar o aparato de arms e isolamento já provado, em vez de reescrevê-lo.
- Congelar arms, célula, métricas e vereditos antes da primeira célula paga, e registrar
  literalmente o que a medição não cobre.
- Entregar a #183 um número reprodutível deste repositório, ou um veredito que diga que a skill não
  deve ser escrita como planejada.

**Non-Goals:**

- Escrever `skills/tdd/SKILL.md`, seus triggers, seu track ou seus cross-links — é #183.
- Medir o arm `skill` (a skill publicada carregada como project skill) — também #183.
- Alterar qualquer skill publicada, o `generate.sh`, o README da raiz ou o CI.
- Medir o laço de feedback vermelho-verde vivido pelo agente. Ver *Decisions*, D3.
- Extrair uma camada de harness compartilhada entre os dois experimentos. Ver *Decisions*, D4.

## Decisions

**D1 — O segundo arm é `doctrine`, não `skill`.**
O item, como redigido, pedia arms `baseline` e `skill` e ao mesmo tempo proibia escrever a skill.
Contradição resolvida com o mantenedor e registrada em
https://github.com/solvelab/ai-skills/issues/182#issuecomment-5561046947: o tratamento é um bloco de
doutrina em `research/tdd/arms-block.md`, anexado ao `CLAUDE.md` da célula via `--claude-block`.
É o papel que `research/lean-code/arms-block.md` cumpre para o arm `block` de lá. Precedente direto:
em #145 apenas o `baseline` rodou e o arm da skill ficou para #146.

**D2 — `order` vem do transcrito, com fallback declarado.**
A célula roda com `--output-format stream-json` (existe em `claude 2.1.263`, probado) e o harness lê
a sequência de eventos `tool_use`: `order` é verdadeiro quando o primeiro `Write`/`Edit` cujo
caminho satisfaz `is_test_path` precede o primeiro em caminho de produção. Quando o transcrito não
expõe a sequência, o harness cai no mtime dos arquivos do workspace e **grava que caiu** — o campo
distingue medida de fallback, e um número apoiado em fallback não é publicado como medida de ordem.

**D3 — Bash fica bloqueado; `red` e `green` são medidos fora da célula.**
O item deixava a escolha aberta. Liberar Bash exigiria trocar `--permission-mode acceptEdits` por
`bypassPermissions` (os valores aceitos em `2.1.263` são `acceptEdits, auto, bypassPermissions,
manual, dontAsk, plan`), o que executaria comandos arbitrários num laço headless não assistido e
invalidaria o reuso da sonda e do preflight já provados. As três métricas de resultado não precisam
disso: `red` roda a suíte do agente sozinha sobre a semente limpa e exige falha; `green` roda a
suíte oculta contra o código final. O custo é declarado como KNOWN LIMIT no protocolo — mede-se a
ordem de escrita e a qualidade do que sobra, não o laço de feedback. O viés é idêntico nos dois
arms, então a comparação continua justa e o valor absoluto de `green` é um piso.

**D4 — Importar `research/lean-code/run.py`, não copiá-lo.**
Medido: aquele módulo importa limpo — o nível de módulo é só docstring, imports, defs/classes e
constantes puras, e `main()` está guardado em `if __name__ == "__main__"` (linha 2747). Copiar 2748
linhas para trocar quatro detectores é exatamente o que `lean-code` proíbe. O que **não** é
importável fica explícito: `TASK_IDS` e `TASKS_DIR` são fixos no experimento de lá,
`SELFTEST_PASSED` é global daquele módulo, e `cell_command` fixa `--output-format json`. Esses
quatro têm versão local. O acoplamento é declarado em `research/tdd/PIN` e verificado por um teste
de contrato dentro do `--selftest`, que é o gate do `--matrix`: se um edit futuro no harness do
lean-code quebrar o contrato, nenhuma célula paga roda.

**D5 — O system prompt da célula é variável de tratamento e é reescrito.**
`NO_RUN` (`research/lean-code/run.py:227-231`) diz *"include tests if you normally would"* e
*"Only the code you write is measured, not its execution"*. Num experimento sobre ordem de teste a
segunda frase sugere ao modelo que teste não conta. `NO_RUN_TDD` mantém a proibição de rodar
servidor, instalar dependência e abrir browser — a razão original, que continua válida com Bash
bloqueado — e não diz nada sobre escrever ou não escrever teste. O texto literal entra no protocolo
como parte da definição da célula, idêntico nos dois arms.

**D6 — Suíte oculta, nunca a do agente.**
`green` é medido por uma suíte que a semente não contém e que o agente nunca vê, executada num venv
fixado por `scorer-venv.txt`. Pontuar pela suíte que o próprio agente escreveu premiaria escrever
testes fracos, que é o oposto do que a doutrina promete.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Método de medição de ganho de comportamento (arms, célula, sonda de isolamento, vereditos) | `research/lean-code/protocol.md` | already canonical — este protocolo cita e reusa, não redefine o método |
| A doutrina TDD em si (ciclo, o que conta como teste vermelho, quando o ciclo não se aplica) | futura `tdd` (#183, `add-tdd-skill`) | **não mora aqui** — `arms-block.md` é o tratamento medido, não a redação da skill |
| Ordem de teste no fluxo de execução de um item | futura `tdd`; `execute-backlog` ganha o link em #183 | link — este item não toca `skills/execute-backlog/SKILL.md` |
| Metodologia adversarial (quebrar o que já foi escrito) | `bug-hunter` | link — fora do escopo desta medição |
| O piso de uma checagem executável atrás de lógica não trivial | `lean-code` | link — `test_added_lines` existe para que TDD não vire licença de suíte inflada, e a regra do piso continua de lá |
| Reusar antes de escrever (a escada) | `lean-code` | link — D4 é a escada aplicada, não uma regra nova |
| Claim publicado carrega backing re-executável, método e alcance | `skills-catalog` spec (MODIFIED aqui) | move — o requisito ganha o caso do claim de ordem de produção |
| Não afirmar o que não foi probado; relatar a lacuna | `verify-before-claiming` | link — o grupo Evidence & Sources cita, não restata |
| Simulação pelo caminho real antes de considerar entregue | `execute-backlog` (passo 8) e o grupo S do schema | already canonical |

## Risks / Trade-offs

- **O veredito pode matar #183.** NO-CLAIM e REWRITE são resultados legítimos e estão escritos
  antes de rodar. É o propósito do item, não uma falha dele.
- **`stream-json` pode não expor a sequência no formato esperado.** Mitigado por D2: o fallback
  existe, é registrado como fallback, e um número de ordem apoiado nele não é publicado como medida.
- **Acoplamento entre dois experimentos.** Mitigado por D4 (PIN + teste de contrato no gate). A
  alternativa — extrair uma camada comum — mexeria num experimento arquivado e reprodutível, e foi
  recusada por isso.
- **Seis tarefas podem não separar os arms.** Se a dispersão engolir o efeito, o protocolo manda
  repetições adicionais nas tarefas afetadas antes de qualquer releitura, como no lean-code.
- **A suíte oculta pode ser injusta com uma implementação correta porém diferente.** Mitigado
  testando comportamento descrito no prompt, nunca estrutura interna; e cada tarefa tem referência
  boa e ruim que o `--selftest` usa para provar o scorer antes de qualquer célula paga.
- **Custo.** Teto por `--budget-usd` em toda invocação, piloto barato antes da matriz, e o comando
  de cada célula é gravado antes de rodar.
