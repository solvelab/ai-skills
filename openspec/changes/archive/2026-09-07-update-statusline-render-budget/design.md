# Design: orçamento de render do status line

## Context

O render quente mede 38–47 ms. Depois da change anterior, o bloco de tokens custa ~5 ms; as quatro
chamadas git custam 12 ms, das quais 9 são de uma só. O resto é interpretação de bash e formatação.

## Goals / Non-Goals

**Goals**
- Cortar o custo que a medição aponta, e só ele.
- Fazer o `SKILL.md` descrever o que o script faz, em vez de recomendar o que ele não faz.
- Fechar #219 com a medição, não com uma reescrita.

**Non-Goals**
- Não cachear o que já é barato.
- Não tocar no bloco de tokens nem no cursor do transcript.
- Não trocar o `jq` por extrator de regex.

## Decisions

### D1 — Cachear `git status --porcelain`, e só ele

Medido, média de 20 execuções no `ai-skills` (1032 arquivos versionados): `git status --porcelain`
9 ms; `git remote get-url origin`, `git symbolic-ref --short HEAD` e `git rev-parse --git-dir` 1 ms
cada. Cachear as três baratas acrescentaria três regras de invalidação para economizar 3 ms.

O branch fica **fora** do cache por um motivo que não é de custo: ele diz sobre o que um comando vai
agir. Um branch obsoleto no rodapé induz erro real; um contador de arquivos modificados obsoleto por
dois segundos, não.

### D2 — Validade por tempo, não por mtime

`.git/index` só muda quando algo é staged. Uma edição na árvore de trabalho — que é justamente o que
o contador `✚` mostra — não toca o índice, então invalidar por mtime deixaria o contador parado até
o próximo `git add`. Errado de um jeito silencioso.

A validade é de 2 segundos, lida de `$EPOCHSECONDS` (bash 5, sem fork — `date +%s` custaria um
processo, que é parte do que se está tentando economizar).

**Isto não conflita com o requisito de determinância** que a change anterior adicionou. Aquele
requisito diz que o que muda entre renders deve vir do payload; o estado do git nunca veio do
payload, e um render sem cache também muda quando a árvore muda. O cache adiciona atraso, não
não-determinância.

### D3 — A chave inclui o diretório

O registro guarda um hash de `$DIR`. Se o diretório mudar dentro da mesma sessão (`/add-dir`, `cd`),
o cache é descartado em vez de mostrar o estado de outro repositório. Sem isso o cache seria pior
que a lentidão.

### D4 — #219 fecha como `wontfix`, com a decomposição

Duas medições mudaram a resposta:

1. **O gargalo é o `jq`, não o I/O.** No transcript de 40 MB: `grep -c` 3 ms, `jq` com parse
   completo 336 ms, `cat > /dev/null` 151 ms (quase tudo syscall de escrita). Pré-filtrar com `grep`
   antes do `jq` foi medido e quase não paga: 322 ms -> 288 ms, porque as linhas com `usage` são
   21.6 MB dos 40 MB.
2. **O custo é pago uma vez por sessão, para sempre.** O cursor é keyed por `session_id`, e o
   transcript de 40 MB abrange **sete dias** (2026-08-23 a 2026-08-30) com `sessionId` constante —
   uma sessão retomada muitas vezes, mesmo id, mesmo arquivo. O cursor sobrevive a todo `--resume`.

O que restaria é trocar o `jq` por um extrator de regex em `awk`. Isso economizaria ~300 ms uma vez
por sessão, e custaria: um parser que assume ordem de chaves; um risco concreto de dupla contagem,
porque cada linha `assistant` repete as mesmas chaves dentro de `iterations`; e a perda da garantia
que a change anterior existiu para estabelecer, que é a contagem bater exatamente. Não é uma troca
que se faz por meio segundo uma vez por sessão.

## Canonical Home & Cross-Links (MANDATORY)

| Cross-cutting rule | Canonical home | Action |
|---|---|---|
| Onde um script publicado persiste estado, como o keia e como o poda | `openspec/specs/skills-catalog` § *Shipped scripts state what they persist* | **already canonical** — o cache do git entra sob ela: mesmo diretório, mesma poda de 30 dias, declarado no `SKILL.md` |
| Determinância do render | `openspec/specs/skills-catalog` § *A shipped script's output is a function of its input* | **link** — D2 explica por que um cache com validade não a viola; a regra não é reescrita aqui |
| Ler a grandeza que o host publica em vez de reconstruí-la | `openspec/specs/skills-catalog` § *A shipped script reads the quantity its host publishes* | **link** — D4 é a mesma doutrina aplicada ao custo: não trocar um número certo e lento por um aproximado e rápido |
| Quanto código uma mudança deixa para trás | skill `lean-code` | **link** — D1 e D4 são a escada aplicada: cachear só o que a medição aponta, e não escrever o parser |
| Idioma de identificadores vs. prosa | skill `code-locale` | **already canonical** — nenhum identificador novo em português |

## Risks / Trade-offs

- **Contador `●`/`✚` atrasado em até 2 s** → aceito e documentado. O branch, que é o valor que
  induziria erro, continua sem cache.
- **Mais um arquivo de estado** → mesmo diretório e mesma poda do cursor de tokens, declarado no
  `SKILL.md` conforme a requisição existente.
- **#219 fica aberta como custo conhecido** → 589 ms uma vez por sessão no pior transcript local.
  A alternativa media pior.

## Migration Plan

Nenhuma. O cache é criado no primeiro render e reconstruído se apagado. Rollback é reverter o commit.

## Open Questions

1. A validade de 2 segundos foi escolhida por raciocínio, não por medição de quantos renders
   acontecem por segundo numa sessão real — esta máquina não tem `refreshInterval` configurado, e
   sem ele os renders são disparados por evento, numa cadência que não foi medida. A consequência de
   errar é só quanto do custo se economiza, nunca correção.
2. Não foi medido o custo de `git status --porcelain` num repositório grande de verdade. O número de
   9 ms vem de um repositório de 1032 arquivos; o argumento de que escala é estrutural (o comando
   percorre a árvore), não medido em escala.
