# Change: Skill terse-response — a resposta tersa ganha casa própria, sem hook nem plugin de terceiro

## Why

Três fatos, lidos ou medidos em 2026-09-10 (issue #248):

1. **O mantenedor depende de código executável de terceiro para 6,7 KB de texto.** O plugin
   `caveman@caveman` 2.3.1 (`~/.claude/settings.json:197`, fonte `github:JuliusBrussee/caveman`)
   roda dois hooks em node a cada sessão — `src/hooks/caveman-activate.js` (injeta
   `skills/caveman/SKILL.md` filtrado pelo nível e grava `~/.claude/.caveman-active`) e
   `caveman-mode-tracker.js` (reinjeta um lembrete por prompt e executa `caveman-stats` por
   `execFileSync`, linha 169) — mais `cavecrew-model-overrides.js:24-40`, que reescreve arquivos de
   agente por env var, 20+ skills, 6 comandos, engine sob BSL e skills de "Caveman Cloud". Hoje sem
   rede nos hooks (`grep -E 'fetch\(|https?://' src/hooks/*.js` vazio); amanhã, quem controla o
   repositório decide. O que é usado de fato: as regras de compressão do nível `full`
   (`~/.claude/.caveman-active` -> `full`), a frase de saída, a auto-clareza e a fronteira "código,
   commits e docs em prosa normal".

2. **O catálogo já tem always-on sem código.** Os blocos *Grounding*, *Code Locale* e *Lean Code*
   de `claude/global/personal-rules.md` entram em toda sessão pelo `@` de `~/.claude/CLAUDE.md`
   e cada um linka a skill canônica. Um bloco a mais custa o mesmo que o hook custa hoje (o texto no
   contexto) e não executa nada.

3. **Regra de forma de resposta não pode afirmar ganho sem medir.** `research/i-have-adhd/results.md`
   (#246, mergeado em `1122599`): no `claude-fable-5-1`, sem skill a mediana de caracteres por
   resposta limpa foi 210, com o caveman 453, com o i-have-adhd 479 — as duas regras alongaram. O
   mapa canônico de `openspec/specs/skills-authoring/spec.md` não tem entrada para forma de resposta;
   publicar sem resolver isso deixaria a regra sem casa.

## What Changes

- Cria `skills/terse-response/` (category `process`, grupo `workflow`): `SKILL.md` com a doutrina
  de resposta tersa harvestada de `skills/caveman/SKILL.md` (MIT) — um nível só (o `full`),
  regras de compressão, o que nunca cai (negações, números, termos técnicos, código, erros
  literais), sem abreviações inventadas nem setas, idioma do usuário preservado, a frase de saída,
  a auto-clareza (segurança, ação irreversível, sequência ambígua, pedido de clareza) e as
  fronteiras (código, commits, PRs, issues, docs, memória e mensagens a terceiros em prosa
  normal). `references/upstream.md` com PIN (commit `81536f57b3303b7de7f5bc5b564cc344f9112d68`,
  sha256 do `SKILL.md` lido, licença) e a lista do que ficou de fora e por quê.
- Bloco `## Terse Response` em `claude/global/personal-rules.md`, no padrão dos três existentes:
  resumo always-on em poucas linhas e link para a skill.
- Mapa canônico de `skills-authoring` ganha a entrada *forma de resposta tersa* -> `terse-response`.
- `README.md` (tabela de plugins, tabela de skills, contagem), `generate.sh`/`plugins/workflow`.
- Medição mínima, pré-declarada e barata, reusando `research/i-have-adhd/run.py` sem juiz: 14 casos
  × 3 condições (sem skill / caveman / `terse-response`) × n=1 em `claude-haiku-4-5-20251001`,
  modo `prompt`, teto único **$3**; veredito escrito antes: razão pareada de caracteres
  `terse-response`/caveman ≤ 1,05 na mediana das respostas limpas, senão REWRITE antes de publicar.
  A skill não publica número.
- Checklist de remoção do plugin no `README` da skill (ops do mantenedor, fora do rito).

## Capabilities

### New Capabilities

- (nenhuma — a capability `skills-catalog` ganha um requisito)

### Modified Capabilities

- `skills-catalog`: ADDED *Terse response has a canonical home* — a skill que governa a forma
  tersa da resposta de chat, o que ela nunca comprime, quando se desliga e onde não se aplica; sem
  número próprio até uma medição com veredito que o permita.
- `skills-authoring`: *Single canonical home per rule* — o mapa canônico ganha
  *forma de resposta tersa* -> `terse-response`.

## Impact

- Skills afetadas: nova `terse-response`; `ai-skills-workflow` passa a embarcar 10 skills
  (composição do plugin muda — breaking para quem lê a descrição do plugin, não para nenhum
  `enabledPlugins`).
- `claude/global/personal-rules.md` ganha um bloco (config do mantenedor, opt-in por `@`).
- Nenhum hook, script, node ou dependência nova: `find skills/terse-response -type f` lista só
  Markdown.
- Custo: ≤ $3 em Haiku, uma passada.
- A remoção do plugin é ação do mantenedor em `~/.claude`, documentada, fora do que o PR muda.
