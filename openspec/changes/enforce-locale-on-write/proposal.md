# Change: Negar a escrita com nome em português na camada de máquina, não só avisar

## Why

O rito do code-locale existe em três camadas e nenhuma **impede** a escrita: a seção *Code Locale*
de `claude/global/personal-rules.md` (texto em contexto), a skill `code-locale` (doutrina + detector)
e o hook `claude/global/hooks/locale-rite.py`, que roda em `PostToolUse` — ou seja, depois que o
arquivo já foi gravado. Medido em `80ee53c` (2026-09-05) com o payload que a issue #137 descreve:

```
printf '{"hook_event_name":"PostToolUse","tool_name":"Write","cwd":"/tmp/x","tool_input":{"file_path":"/tmp/x/servico_pedido.py","content":"def calcular_total(preco):\n    return preco\n"}}' | python3 claude/global/hooks/locale-rite.py
-> {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "CODE-LOCALE: the write that just landed [...]
-> "systemMessage": "code-locale: 4 non-English names in the last write"}
-> rc=0
```

Quatro achados, e o arquivo já está no disco. O mantenedor relata que em sessões de várias
aplicações o modelo lê o aviso e segue; nada o obriga a renomear. O próprio bundle instalado
(`~/.local/share/claude/versions/2.1.261`) mostra o que o hook não usa: em `PreToolUse`,
`hookSpecificOutput.permissionDecision: "deny"` + `permissionDecisionReason` cancela a chamada
antes de ela rodar, e o payload desse evento já traz `tool_input.file_path` e o conteúdo — exatamente
o que `evaluate()` mede hoje. É medição, não proxy.

## What Changes

- `locale-rite.py` decide pelo `hook_event_name` do payload. Em `PreToolUse`, um achado gating
  (`pt-*`, `path-pt-*`) devolve `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny", "permissionDecisionReason": <cabeçalho + achados + as três
  saídas>}}`; só `en-unknown` não nega. Em `PostToolUse` o comportamento é o de hoje, byte a byte
  (consultivo, cobre o `en-unknown`). Uma decisão, dois envelopes: `evaluate()` continua a única
  função.
- O motivo da negação respeita o cap medido no bundle — `permissionDecisionReason:2000` caracteres
  **e** 20 linhas — e termina com as três saídas: `# locale-ok: <motivo>` inline, o nome ou o
  caminho em `.identifier-locale-allow`, e `LOCALE_RITE_MODE=inform` para a sessão inteira.
- `LOCALE_RITE_MODE=inform` (novo): o hook nunca nega; o aviso continua vindo do `PostToolUse`,
  como hoje.
- Selftest: casos de `PreToolUse` (negação por identificador, por caminho, silêncio com
  `locale-ok:`, silêncio com allowlist num cwd temporário, `inform`, só `en-unknown`, payload
  malformado), a forma e o cap do envelope de negação, a variável de ambiente lida pelo caminho real,
  e os casos de `PostToolUse` inalterados.
- Docstring do hook: modos, bloco de wiring dos **dois** eventos, o probe do `permissionDecision` ao
  lado do probe do `additionalContext`, e o KNOWN LIMIT de que escritas via Bash não passam por aqui.
- `personal-rules.md`, seção *Code Locale*: uma frase dizendo que a escrita é **negada** pelo hook,
  não só lembrada, e onde estão as saídas.

## Capabilities

### Modified Capabilities

- `skills-catalog`: o requisito *The code-locale rite is enforced at the moment of the write* deixa
  de exigir que o artefato "nunca bloqueie" e passa a exigir que, no evento que **precede** a
  escrita, um achado gating negue a chamada com os achados e as três saídas no motivo, que a mesma
  escrita com `locale-ok:` ou com a allowlist seja gravada em silêncio, que o modo informativo
  restaure o comportamento consultivo, e que `en-unknown` nunca negue. O evento que **segue** a
  escrita fica como está.

## Impact

- `claude/global/hooks/locale-rite.py` — o envelope de `PreToolUse`, o modo `inform`, o selftest e o
  docstring; a linha de comando não muda.
- `claude/global/personal-rules.md` — só a seção *Code Locale*.
- Wiring: quem já tem o bloco `PostToolUse` precisa **adicionar** um bloco `PreToolUse` com o mesmo
  matcher em `~/.claude/settings.json` (configuração pessoal, fora do PR; o snippet vai no resultado).
  Sem o bloco novo, o hook continua exatamente como hoje.
- Nenhuma skill do catálogo muda; a composição do catálogo fica idêntica.

Fora de escopo, por decisão da issue #137: escritas via Bash (heredoc, `sed`, scripts) — o hook não
as vê e esse é o gate de Stop da issue #138; prosa em inglês em repositório português; a seção dos
hooks no `README.md`, que outro item documenta junto com o wiring de todos os hooks.
