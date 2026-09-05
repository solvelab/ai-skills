## Context

Três hooks vivem em `claude/global/hooks/` e nenhum vê o que Bash grava. Lidos em `80ee53c`
(2026-09-05):

- `locale-rite.py` (285 linhas): o modelo de forma. `evaluate(payload, check)` em 164-182,
  `selftest()` em 185-259, `main()` em 262-284 com `args == ["--selftest"]` (264), usage + exit 2 para
  qualquer outro argumento, `isinstance(payload, dict)` como guarda (276). Importa o detector por
  caminho (`CHECK_PATH = parents[3] / "skills/code-locale/references/check-identifier-locale.py"`,
  linha 63). Matcher `Write|Edit|MultiEdit|NotebookEdit`; a issue #137 acrescenta o `PreToolUse` que
  nega.
- `skills/code-locale/references/check-identifier-locale.py`: `scan_diff(stream, allow, english)` em
  612-666 lê só linhas `+` de um diff unificado, agrupa por run, e dispara o tier de caminho só quando
  o cabeçalho anterior foi `--- /dev/null` (633-641). `load_allowlist(start)` em 401-412 sobe pelos
  pais até achar `.identifier-locale-allow`. `is_vendored(path)` em 393 **não** é chamado por
  `scan_diff` — o `main()` só o aplica ao modo de caminhos.
- `.github/workflows/ci.yml:146-147`: step `Locale write-gate hook self-test`; os steps dos irmãos em
  149-153.
- `README.md:235-346`: a seção dos hooks — `### Enforcing the rite` em 235, snippet `UserPromptSubmit`
  em 252-271, `### The grounding rite` em 283, `### The locale rite` em 306 ("third hook" em 308),
  `PostToolUse` com matcher `Write|Edit` em 314-330 (319), a citação final em 343-346.

O bundle instalado (`readlink -f $(which claude)` → `~/.local/share/claude/versions/2.1.261`, um só
ELF, `grep -a`) diz o que a doc deixa ambíguo. Trechos, com o nome minificado de cada função:

- Entrada do Stop: `hook_event_name:C("Stop"),stop_hook_active:P(),last_assistant_message:s().optional()`
  — e `SubagentStop` com o mesmo `stop_hook_active` mais `agent_id`, `agent_transcript_path`.
- Leitura da resposta (`PMe`): `f=o.decision==="approve"?void 0:X5(r,"reason",o.reason)`,
  `y=X5(r,"systemMessage",o.systemMessage)`, e o objeto devolvido é
  `{...o.decision==="block"&&{decision:"block"}, ...y!==void 0&&{systemMessage:y},
  ...f!==void 0&&{reason:f}, ...x!==void 0&&{hookSpecificOutput:x}}`. Ou seja, `decision`, `reason` e
  `systemMessage` são lidos do **topo**.
- O que bloqueia (`eg`): `if("decision"in e&&e.decision==="block")return!0; if("continue"in
  e&&e.continue===!1)return!0;` e, no `hookSpecificOutput`, só `permissionDecision` deny/ask (que é
  PreToolUse).
- `hookSpecificOutput` de Stop (`LU(e,"Stop",r)`): `let o=X5(e,"additionalContext",
  r.additionalContext);return{hookEventName:t,...o!==void 0&&{additionalContext:o}}` — qualquer outra
  chave aninhada (um `decision` dentro de `hookSpecificOutput`) é **descartada sem erro**.
- Caps (`AKr`): `{reason:2000,stopReason:2000,systemMessage:4000,additionalContext:8000,
  permissionDecisionReason:2000}`.
- Guarda de loop: `let Od=a.CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8; if(Od>0&&Pc>Od)` … "A hook blocked
  the turn from ending ${Pc} consecutive times — overriding and ending turn. For Stop/SubagentStop
  hooks, check stop_hook_active in the input and return success while it's true."

## Goals / Non-Goals

**Goals:**

- Um turno que gravou nome em português na camada de máquina por qualquer caminho — heredoc, `sed`,
  ferramenta de escrita com o hook em `inform` — não encerra até renomear ou dispensar.
- O gate mede só o **diff não commitado** (rastreado contra `HEAD`, mais os não rastreados): legado só
  entra se o turno o tocou.
- Silêncio, exit 0 e menos de 1 s quando não há nada a medir: fora de git, diff vazio, só achado
  consultivo, modo `inform`, payload malformado.
- Nunca um loop: o segundo Stop (`stop_hook_active: true`) não bloqueia; devolve o que sobrou como
  `systemMessage` e encerra.

**Non-Goals:**

- Bloquear a chamada Bash em si (PreToolUse em `Bash`): parsear heredoc/`sed`/scripts é frágil, e o
  que importa é o resultado no disco — a issue registra a decisão.
- Medir repositórios fora do `cwd`, ou o que já foi commitado no mesmo turno (KNOWN LIMIT, no
  docstring).
- Achados consultivos (`en-unknown`) no Stop. São uma pergunta ("isso é inglês?"), não um veredito, e
  o detector já os declara não-bloqueantes; bloquear o encerramento por uma pergunta seria mudar a
  doutrina do check por dentro de um hook.
- Tocar `locale-rite.py`, `personal-rules.md` ou `skills/**` — issues #137 e #139, em paralelo.

## Decisions

### D1 — A saída é `{"decision": "block", "reason": …}` no topo; nada aninhado

As duas leituras da doc divergem (topo vs. `hookSpecificOutput`). O bundle decide: `eg` só bloqueia
por `decision` no topo, `PMe` lê `reason`/`systemMessage` no topo, e `LU` descarta tudo que não seja
`additionalContext` dentro de `hookSpecificOutput` de Stop. Emitir os dois seria tolerado (a chave
aninhada é ignorada, não rejeitada), mas emitiria uma forma que o bundle comprovadamente não lê — e
um leitor futuro copiaria a forma errada. Fica só o topo. O caso de forma do selftest afirma
`decision == "block"`, `reason` string até 2000, e **ausência** de `hookSpecificOutput`.

Motivo e mensagem respeitam os caps medidos (`reason:2000`, `systemMessage:4000`) truncando aqui,
para que a cauda cortada seja a nossa (as saídas ficam no fim e são o que não pode sumir) e não a do
harness.

### D2 — O diff é montado do topo do work tree, contra `HEAD` ou contra a árvore vazia

`git -C <cwd> rev-parse --show-toplevel` decide se há repositório (rc≠0 → silêncio) e de onde medir.
Medir do topo, não do `cwd`, torna os caminhos do diff relativos à raiz do projeto — o que o tier de
caminho do detector espera (`project_relative(path, None)`, "the caller already handed a
project-relative path (diff mode does)") — e coerentes entre `git diff` e `ls-files`.

`git diff HEAD` falha num repositório sem commit (`fatal: ambiguous argument 'HEAD'`, rc=128, medido).
A base é `HEAD` quando `git rev-parse --verify -q HEAD` responde, senão a árvore vazia
(`git hash-object -t tree /dev/null` → `4b825dc…`, medido): um repositório recém-criado mede tudo o
que já foi adicionado ao índice como novo.

Rename detection fica no padrão do `git diff`: um arquivo em português **movido sem edição** aparece
como rename, não como `--- /dev/null`, e o tier de caminho não dispara. É a leitura fiel de "legado só
entra se o turno o tocou"; declarado no docstring.

### D3 — Não rastreados entram um a um por `git diff --no-index /dev/null <path>`; binários pulados

`git ls-files --others --exclude-standard` respeita `.gitignore` e `info/exclude` — `node_modules/`
e `.venv/` ignorados nunca entram. Para cada caminho, `git diff --no-index --no-color /dev/null
<path>` produz exatamente o cabeçalho que `scan_diff` espera (`--- /dev/null` / `+++ b/<path>`,
medido; rc=1 é "há diferença", não erro). Um arquivo com NUL nos primeiros 8 KiB é binário e é pulado
antes de chamar o git — o git também não emitiria linha `+` nenhuma, mas o `+++` que emitiria faria o
tier de caminho medir um `.pdf`; o gate mede código, e um nome de binário fica declarado como limite.

### D4 — Um teto de linhas declarado, nunca um corte em silêncio

O harness mata hooks lentos, e um `git diff` de milhares de linhas mais o detector por cima poderia
passar do tempo. O total de linhas do diff é limitado a `MAX_DIFF_LINES = 4000`; passado o teto, o que
sobra não é medido e o motivo **diz** isso ("diff truncated at N lines; run the check on the rest").
Cada chamada ao git tem `timeout=5`; um git que estoura o tempo devolve silêncio, porque um gate que
não consegue medir não pode segurar o turno para sempre — e esse é o único caso em que "não medir"
vira "não bloquear", declarado como KNOWN LIMIT.

### D5 — Só achados gating bloqueiam; vendored é filtrado depois do scan

`scan_diff` é chamado com `english=None`: sem a lista inglesa não há tier `en-unknown`, o scan fica
~110 ms mais rápido (`load_english` medido em 109 ms para 369 786 palavras) e o Stop julga só o que o
detector tem certeza. `scan_diff` não aplica `is_vendored` (só o modo de caminhos aplica); o hook
filtra os achados cujo `path` é vendored, para que um `vendor/` rastreado editado não segure o turno.

### D6 — `stop_hook_active` verdadeiro nunca bloqueia; devolve `systemMessage`

O bundle tem uma guarda própria (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP ?? 8`) que sobrescreve um hook que
bloqueia 8 vezes seguidas. O gate não chega perto: bloqueia uma vez, e no Stop seguinte — o harness
marca `stop_hook_active: true` — devolve só `{"systemMessage": …}` com o que ainda está em
português. O segundo turno é a última chance, não um loop: quem leu o motivo e não renomeou decidiu; o
gate registra e sai. Declarado no docstring e no README.

### D7 — `LOCALE_RITE_MODE=inform` silencia o gate, e é a mesma variável da issue #137

Uma sessão inteira em modo informativo é uma decisão do usuário, e as três saídas que o motivo lista
são as mesmas do gate de escrita: `# locale-ok: <motivo>` inline (o detector já honra na linha ou na
anterior), `.identifier-locale-allow` na raiz do repositório (para nomes de arquivo, a única saída) e
`LOCALE_RITE_MODE=inform`. Um nome de variável por rito, não por hook.

### D8 — Só `Stop` e `SubagentStop` são avaliados; qualquer outro `hook_event_name` é silêncio

Os dois eventos têm o mesmo `stop_hook_active` no bundle. O README wira só `Stop`; o hook aceita os
dois para que um wiring em `SubagentStop` funcione sem edição, e ignora qualquer outro evento — um
matcher errado não pode virar um bloqueio em PostToolUse.

### D9 — O selftest cria um repositório git em `tempfile.TemporaryDirectory()`

Cada caso tem o repositório que precisa: um commit inicial com um arquivo limpo, depois o arquivo
novo em português (não rastreado), a edição do rastreado, a edição limpa, o diretório sem `.git`, o
mesmo payload com `stop_hook_active: true`, o modo `inform` (passado como parâmetro `env` ao
`evaluate`, não mutando `os.environ`), o teto de linhas (parâmetro `max_lines`) e os três payloads
malformados mais o argumento desconhecido pelo entry point real (`subprocess`), como o irmão faz.
Identidade do git via `-c user.email -c user.name`, para não depender da máquina.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Camada de máquina em inglês; o que é prosa e o que é código; as saídas (`locale-ok:`, allowlist) | `code-locale` | already canonical — o motivo do bloqueio cita as saídas e aponta para a skill, não reescreve a regra |
| O detector e seu modo `--diff` (linhas adicionadas, tier de caminho só em `--- /dev/null`) | `code-locale` (`references/check-identifier-locale.py`) | already canonical — o hook importa e chama; não duplica o scan |
| Um check embarcado carrega selftest, declara o que não cobre e é gated pelo CI | `skills-catalog` (*A shipped enforcement script declares what escapes it*) | already canonical — o delta acrescenta um requisito que a cita |
| O gate de escrita (PreToolUse/PostToolUse) e o modo `inform` | `skills-catalog` (*The code-locale rite is enforced at the moment of the write*) + issue #137 | link — o README descreve o wiring dos dois e a tabela diz qual camada pega o quê |
| Prova observada pelo caminho real antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Kit por repositório (pre-commit, step de CI) para outros assistentes e humanos | `code-locale` (issue #139) | link — a tabela do README aponta; nada é implementado aqui |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **Repositório alheio cheio de legado em português segura o turno** → o gate mede só o diff não
  commitado; linhas não tocadas nunca entram; um rename puro não dispara (D2).
- **Diff enorme e lento** → teto de 4000 linhas declarado no motivo, `timeout=5` por chamada ao git,
  silêncio quando o git não responde (D4). O tempo em diff vazio e em 500 linhas está medido em
  `tasks.md`.
- **Loop de bloqueio** → uma vez, depois `systemMessage` (D6); a guarda do bundle (cap 8) fica como
  segunda rede.
- **Nome legítimo de domínio bloqueado** → as três saídas no fim do motivo, sempre dentro do cap
  (D1, D7).
- **O hook não vê o que foi commitado no mesmo turno, nem outro repositório, e vira `SubagentStop`
  em subagentes** → KNOWN LIMIT no docstring (TR3 da issue); o kit da issue #139 é a camada que
  sobrevive a isso.
- **A forma da saída muda numa versão futura do harness** → o docstring grava versão e trecho; o
  selftest fixa a forma; a doc pinada é a segunda fonte.

## Open Questions

Nenhuma que vire achismo: a forma da saída, o cap, a guarda de loop, o cabeçalho do `--no-index`, o
comportamento em `HEAD` inexistente e fora de git foram medidos antes de escrever, e estão em
`tasks.md` com comando e saída. O que **não** foi medido nesta execução é o harness real disparando o
hook num Stop de sessão — o wiring é configuração pessoal fora do PR; a simulação alimenta o entry
point real com payloads no formato do schema do bundle (E.3).
