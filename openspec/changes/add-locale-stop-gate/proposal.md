# Change: Gate de Stop — medir o diff não commitado do turno, cubra Bash e heredoc

## Why

O rito do code-locale é medido no momento da escrita por `claude/global/hooks/locale-rite.py`, que só
vê `Write|Edit|MultiEdit|NotebookEdit`. Tudo o que chega ao disco por **Bash** — `cat > x <<'EOF'`,
`sed -i`, um script — nunca é medido na sessão. Medido ao vivo em 2026-09-05 (issue #138):
`cat > servico_cliente.py <<'EOF' … def buscar_cliente(id_usuario)` gravou o arquivo e nenhum hook
disparou. O modo `auto` do harness ainda instrui a editar arquivos por Bash em vez das ferramentas
dedicadas — o caminho mais usado é o que escapa.

O harness tem o evento certo: **Stop** dispara uma vez por turno, recebe `cwd` e `stop_hook_active`,
e um `decision: "block"` com `reason` impede o modelo de encerrar o turno. Probado no bundle instalado
(`claude 2.1.261`), não só na doc: o schema de entrada é
`hook_event_name:C("Stop"),stop_hook_active:P()`; o leitor da resposta copia `decision:"block"`,
`reason` e `systemMessage` do **topo** do objeto, e para `Stop` o `hookSpecificOutput` só carrega
`additionalContext` (`LU(e,"Stop",r)`). O detector já tem o modo certo: `check-identifier-locale.py
--diff -` lê só linhas adicionadas de um diff unificado.

## What Changes

- `claude/global/hooks/locale-stop-gate.py` (novo), no formato dos hooks irmãos: `evaluate()` pura,
  `--selftest`, contrato de `argv` explícito (só `--selftest`; qualquer outro argumento imprime usage
  e sai 2), payload malformado mudo com exit 0. Num payload de Stop: se `cwd` está num work tree git,
  monta o diff não commitado (`git diff <HEAD|árvore vazia> --no-color` mais, para cada arquivo de
  `git ls-files --others --exclude-standard`, `git diff --no-index --no-color /dev/null <path>`;
  binários pulados; total de linhas limitado a um N declarado, e o truncamento é dito no motivo);
  passa o diff ao detector embarcado (`scan_diff`, com o `.identifier-locale-allow` do repositório);
  havendo achado gating e `stop_hook_active` falso e `LOCALE_RITE_MODE != inform` → bloqueia o
  encerramento com os achados e as três saídas; `stop_hook_active` verdadeiro → não bloqueia de novo
  e devolve o que sobrou como `systemMessage` (o segundo turno é a última chance, não um loop); fora
  de git, diff vazio, só achado consultivo, ou modo `inform` → silêncio.
- `.github/workflows/ci.yml`: um step `Locale stop-gate hook self-test`, logo após o step do
  `locale-rite`.
- `README.md`, seção dos hooks: snippet completo do `settings.json` com `UserPromptSubmit`,
  `PreToolUse` e `PostToolUse` (matcher `Write|Edit|MultiEdit|NotebookEdit`, o `PreToolUse` que a
  issue #137 entrega em paralelo, com `LOCALE_RITE_MODE=inform`) e o bloco `Stop` novo, mais a tabela
  "qual camada pega o quê".

## Capabilities

### Modified Capabilities

- `skills-catalog`: requisito ADDED *The code-locale rite closes the turn, not only the write*. O
  requisito existente *The code-locale rite is enforced at the moment of the write*
  (`openspec/specs/skills-catalog/spec.md:781`) cobre a ferramenta de escrita; este cobre o resultado
  — o diff não commitado ao fim do turno, independente de como o arquivo foi escrito — com os
  cenários: heredoc com nome em português bloqueia o encerramento; renomeado, o turno encerra;
  `stop_hook_active` não bloqueia de novo; fora de git, silêncio; modo `inform`, silêncio.

## Impact

- `claude/global/hooks/locale-stop-gate.py` — arquivo novo; só stdlib + `git`; importa o detector por
  caminho, como `locale-rite.py` faz.
- `.github/workflows/ci.yml` — um step de `Validate`.
- `README.md` — seção dos hooks.
- Nenhuma skill do catálogo muda: nenhum `SKILL.md` é tocado; `locale-rite.py`, `personal-rules.md` e
  `skills/**` ficam com as issues #137 e #139, que rodam em paralelo. Quem já tem os hooks wired não
  precisa mudar nada além de acrescentar o bloco `Stop`.

Fora de escopo, por decisão registrada na issue #138: bloquear a chamada Bash em si (parsear heredoc
é frágil; o resultado é o que importa), repositórios sem git, e o wiring em `~/.claude/settings.json`
do mantenedor (configuração pessoal; o snippet vai no README e no resultado da execução).
