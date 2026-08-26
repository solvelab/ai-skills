## Context

O repositório já entrega dois ritos como hook: `claude/global/hooks/backlog-rite.py` e
`claude/global/hooks/verify-rite.py`, ambos `UserPromptSubmit`, ambos justificados no próprio
docstring — *"the harness runs this on every prompt, so enforcement does not depend on the assistant
noticing a rule already in context"*. A capability `skills-catalog` especifica essa forma (cenários
em `openspec/specs/skills-catalog/spec.md:209` e `:472`).

O rito de locale não tem esse par. Ele existe como doutrina (`skills/code-locale/SKILL.md`), como
seção das regras globais (`claude/global/personal-rules.md`) e como detector de revisão
(`skills/code-locale/references/check-identifier-locale.py`), e mesmo assim o defeito reaparece.

O detector, além disso, não lê o caminho do arquivo que recebe — o artefato que a própria doutrina
lista primeiro entre os nomes que a máquina consome.

## Goals / Non-Goals

**Goals**

- O tier de caminho existe nos dois modos que o detector já expõe (arquivo e `--diff`).
- Um nome de arquivo em português escrito pelo assistente é reportado no momento da escrita, em
  qualquer repositório, sem depender de CI daquele repositório.
- Nenhum falso positivo novo: as regras que já protegem identificadores (vendor, `MIN_SEGMENT`,
  `DOMAIN_KEEP`, allowlist) valem igual para caminho.

**Non-Goals**

- Renomear nome existente, aqui ou em qualquer repositório. Os três tiers de
  `skills/code-locale/references/migration.md` continuam valendo.
- Ampliar `LEXICON`, cobrir espanhol/italiano/francês, ou mexer nos escapes deliberados listados no
  KNOWN LIMIT do detector.
- Bloquear a chamada de ferramenta. Como os outros dois ritos, este informa; a dispensa é do usuário.
- Entregar template de pre-commit/CI para repositórios de destino (adiado deliberadamente — o hook
  global já cobre toda sessão em todo repositório).

## Decisions

**D1 — O caminho é medido relativo ao diretório de trabalho, nunca absoluto.**
Um caminho absoluto carrega segmentos que o projeto não escolheu (`/home/<usuário>`, um diretório de
mount, o nome da máquina). Escanear `/home/diegops/ai-skills/...` inteiro produziria achado sobre o
nome da pasta pessoal de alguém. A regra: quando o caminho está dentro do `cwd`, mede-se a parte
relativa; quando não está, mede-se apenas o nome do próprio arquivo. Alternativa considerada e
descartada: escanear tudo e listar exceções — transfere ao usuário o custo de uma decisão que a
ferramenta consegue tomar sozinha.

**D2 — Em `--diff`, só o caminho de arquivo ADICIONADO é medido.**
Um diff que toca um arquivo legado de nome português reportaria o mesmo achado em todo commit até
alguém renomear — e renomear é exatamente o que a política de migração proíbe fazer por si só. O
sinal de "arquivo novo" já está no diff: o cabeçalho `--- /dev/null` que precede o `+++ b/<path>`.
Alternativa descartada: medir todo `+++ b/`, que transforma o gate em ruído permanente sobre código
que ele não deveria julgar.

**D3 — A dispensa de um caminho é a allowlist, não um comentário.**
Um nome de arquivo não tem onde carregar `# locale-ok: <motivo>`. O detector já tem o mecanismo:
`ALLOWLIST_FILE = ".identifier-locale-allow"`, lido por `load_allowlist()` subindo a árvore, e o
`Finding.render()` já imprime a linha a acrescentar. O achado de caminho reaproveita esse caminho de
saída em vez de inventar um segundo formato de dispensa.

**D4 — O hook devolve o achado por `hookSpecificOutput.additionalContext`, não por stdout puro.**
Em `PostToolUse`, stdout simples vai para o debug log e o modelo não vê. Probado nas duas pontas:
a documentação da versão instalada (`code.claude.com/docs/en/hooks`, lida em 2026-08-26) diz que as
exceções em que stdout vira contexto são `UserPromptSubmit`, `UserPromptExpansion` e `SessionStart`
— `PostToolUse` não está na lista; e o binário instalado (`claude 2.1.246`) lê o campo:
`let {additionalContext:a,...l}=e.hookSpecificOutput` com o teto `additionalContext:8000`. O hook
imprime JSON e sai 0. Alternativa descartada: `exit 2`, que a doc descreve como "shows stderr to
Claude" — funciona, mas é a porta de erro, e este rito não é erro: é informação.

**D5 — O hook importa o detector por caminho, não por subprocesso.**
O detector é stdlib-only e o hook vive no mesmo repositório, dois níveis acima
(`claude/global/hooks/` → `skills/code-locale/references/`). `importlib.util.spec_from_file_location`
carrega um arquivo cujo nome tem hífens sem exigir pacote. Isso evita pagar um processo Python novo
a cada `Write`/`Edit`. Se o detector não estiver presente (alguém copiou só o hook), o hook sai 0 em
silêncio — um gate ausente nunca vira exceção na cara do usuário.

## Canonical Home & Cross-Links (MANDATORY)

| Regra transversal | Skill canônico (dono) | Ação nesta change |
|---|---|---|
| Fronteira prosa/máquina, exceção de termo de domínio, política de migração | `code-locale` | já canônico — a change altera o detector **dentro** do skill dono, não replica a doutrina em outro lugar |
| Não improvisar tradução / afirmar sem probe | `verify-before-claiming` | link, sem restatement: o SKILL.md do `code-locale` já aponta para ele, e as decisões D4/D1 registram o probe em vez de recordar |
| Rito backlog-first (o hook novo é irmão dos dois existentes) | `backlog` / `execute-backlog` | link: o `locale-rite.py` não repete o texto do rito de backlog; ele cita a doutrina do `code-locale` e nada mais |
| Idioma de commit/PR | `conventional-commit` | intocado — esta change não altera regra de prosa de commit |

## Risks / Trade-offs

- **Ruído a cada escrita** → silencioso quando limpo; mede apenas o caminho tocado e o conteúdo
  escrito, nunca a árvore.
- **Latência em todo `Write`/`Edit`** → import de módulo em processo, stdlib, sem chamada a git e sem
  travessia de diretório. O orçamento é um arquivo.
- **Falso positivo em árvore legada** → D2 restringe o modo diff a arquivo adicionado, e o hook mede
  o arquivo que está sendo escrito agora, não o repositório.
- **A allowlist virar escape hatch ilimitado** → é o mesmo mecanismo já existente para
  identificadores, com o mesmo custo social: entra no repositório, aparece no diff, um revisor lê.
- **Hook é config do usuário; máquina sem wiring não ganha gate** → README documenta o wiring ao lado
  dos outros dois, e o próprio hook reporta nada em vez de falhar quando o detector some.
- **O tier de caminho não é modelo de língua** → o KNOWN LIMIT do detector ganha a linha
  correspondente; um nome fora do léxico continua passando, como já acontece para identificadores.

## Migration Plan

Não há migração. O tier novo só fala sobre arquivo adicionado (D2) e sobre a escrita corrente (hook),
então nenhuma árvore existente fica vermelha no dia seguinte. Rollback: remover o passo de CI e o
wiring do hook; o detector volta ao comportamento anterior removendo a função de caminho.

## Open Questions

- Nenhuma pendente sobre o mecanismo: os dois pontos que dependiam de comportamento externo (campo
  lido pelo harness em `PostToolUse`, e forma do payload) foram probados contra a versão instalada
  (D4). O que **não** foi probado: como outros harnesses (Codex, Cursor) expõem um evento equivalente
  — por isso a change entrega o hook apenas para o harness cujo contrato foi medido, e não afirma
  nada sobre os demais.
