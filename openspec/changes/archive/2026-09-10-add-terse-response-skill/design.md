# Design — skills/terse-response

## Context

O item #248 troca um plugin de terceiro (dois hooks em node por sessão, atualizado de um
repositório que o mantenedor não controla) por texto mantido no catálogo. A casa já tem forma:
uma skill em `skills/<name>/` para o roteador, e um bloco em `claude/global/personal-rules.md`
para o always-on, exatamente como `lean-code` (skill + bloco *Lean Code*), `code-locale` e
`verify-before-claiming`.

## Goals / Non-Goals

**Goals:**

- Mesmo efeito que o mantenedor tem hoje (nível `full` do caveman), com zero código executável e
  zero fonte externa no caminho da sessão.
- Doutrina com casa canônica: uma skill, um bloco que linka, uma linha no mapa canônico.
- Um gate barato e pré-declarado antes de publicar: não ficar mais longo que o caveman.

**Non-Goals:**

- Níveis de intensidade, wenyan, comandos `/caveman-*`, `cavecrew`, stats, engine, cloud.
- Hook de qualquer tipo, mesmo próprio: o bloco no `personal-rules.md` já entra em toda sessão.
- Regras de forma do i-have-adhd (NO-CLAIM em #246) ou qualquer claim numérico de economia.
- Tocar `~/.claude` do mantenedor pelo PR: a remoção do plugin é checklist, executado por ele.

## Decisions

**D1 — Um nível só.** O mantenedor roda `full` (`~/.claude/.caveman-active`). Seis níveis com
tabela e exemplos são 40 % do texto do upstream para zero uso; a skill fixa as regras do `full`
e a frase de saída. Quem quiser outro registro edita a skill, não escolhe um nível.

**D2 — Always-on por bloco, não por hook.** O caveman injeta por `SessionStart` porque é um
plugin instalado em máquinas alheias. Aqui o always-on já existe: `~/.claude/CLAUDE.md` inclui
`claude/global/personal-rules.md` por `@`, e os três blocos existentes provam o mecanismo em toda
sessão. O único artefato novo fora de `skills/` é o bloco no `personal-rules.md`.
Efeito colateral aceito: o bloco entra também em sessões onde o plugin `ai-skills-workflow` não
está habilitado — igual aos outros três.

Emenda de 2026-09-10, medida pelo caminho real antes do PR: um bloco-resumo de 12 linhas **não**
segura o registro — com só o bloco, Haiku respondeu à mesma pergunta em 1030 caracteres de prosa
com títulos; com o texto inteiro da skill no contexto, 813 (Haiku) e 855 (Fable, artigos
caídos). O caveman também injeta o `SKILL.md` inteiro pelo hook, não um resumo. O bloco fica
curto e termina em `@../../skills/terse-response/SKILL.md` — o `@` do `CLAUDE.md` resolve
imports aninhados relativos ao arquivo que os contém — de modo que a skill inteira entra no
contexto sem hook, sem cópia e sem duplicar doutrina.

**D3 — Harvest com PIN, texto adaptado.** `skills/caveman/SKILL.md` é MIT (o `LICENSE` do
upstream classifica `skills/` fora dos módulos BSL). O texto é reescrito no formato do catálogo
(frontmatter uniforme, prosa em inglês, sem seção *Usage*), com `references/upstream.md`
gravando commit, sha256 do arquivo lido, licença, o que entrou e o que ficou de fora. Não é cópia
byte a byte: a skill tem de passar `skills-authoring`, e o upstream mistura doutrina com
mecanismo de plugin.

**D4 — A medição é um gate de não-regressão, não uma claim.** `research/i-have-adhd/results.md`
mediu que regras de forma alongam a resposta no Fable. A skill nova só precisa não ficar mais
longa que o que ela substitui. Reuso de `research/i-have-adhd/run.py` (`--matrix --mode prompt`
com `--case` nos 14 casos, n=1, Haiku, sem `--judge`): condições `baseline` (sem skill),
`comparator` (`vendor/caveman/skills/caveman/SKILL.md`) e `candidate` (a skill nova, apontada por
um flag `--candidate-skill`), razão pareada de caracteres nas respostas limpas. Limiar escrito
antes de rodar: mediana da razão candidate/comparator ≤ 1,05 -> publica; senão REWRITE e roda de
novo, dentro do mesmo teto de $3. O resultado vai em `research/i-have-adhd/results.md` como seção
datada, não na skill. Nenhum número entra na skill.

**D5 — Desligar é frase, não flag.** "stop caveman" / "normal mode" continuam valendo (o
mantenedor já as usa), mais "stop terse". Sem arquivo de estado, sem tracker por prompt: o modelo
lê a instrução no contexto e obedece à frase — é como os outros blocos do `personal-rules.md`
funcionam.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Forma tersa da resposta de chat, o que nunca comprime, frase de saída, auto-clareza, fronteiras | `terse-response` | **move** — sai do plugin de terceiro para a skill; o mapa canônico de `skills-authoring` ganha a entrada |
| Always-on de uma regra pessoal | `claude/global/personal-rules.md` (bloco) | already canonical — o bloco linka a skill, não restata |
| Não afirmar ganho sem medição | `verify-before-claiming` e o requisito *A published cost claim carries re-runnable backing* de `skills-catalog` | link — D4 aplica |
| Reusar antes de escrever | `lean-code` | link — reuso do harness de #246 em vez de outro |
| Onde uma regra vira skill, hook ou script | `agent-delegation` | link — D2 é a decisão "skill + bloco, não hook", pela doutrina de lá |
| Idioma da prosa e dos identificadores | `code-locale` | link — a skill preserva o idioma do usuário na resposta e é escrita em inglês |

## Risks / Trade-offs

- **A skill própria alongar a resposta.** D4 pega antes de publicar.
- **Perder a auto-clareza em avisos de segurança.** Fronteira explícita na skill, com o mesmo
  exemplo de operação destrutiva do upstream.
- **Deriva em sessões longas** (o tracker do caveman existia para isso). O bloco always-on está no
  contexto de toda sessão; se a deriva aparecer, é um item novo, não um hook agora.
