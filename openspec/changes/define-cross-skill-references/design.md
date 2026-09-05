## Context

O catálogo é instalado de cinco formas, e só uma delas carrega a árvore inteira:

| Forma | O que chega ao disco | Quem documenta |
|---|---|---|
| clone + symlink | tudo; `~/.claude/skills/<nome>` → `~/ai-skills/skills/<nome>` | `README.md:131-134`, `install.sh` |
| `npx skills add solvelab/ai-skills` | só `skills/<nome>/` de cada skill escolhida | `README.md:44-46` |
| plugin de grupo | `plugins/<grupo>/skills/<nome>/` das skills daquele grupo | `generate.sh:199-212` |
| Cursor | `cursor/rules/<nome>.mdc` copiado isolado para `.cursor/rules/` | `README.md:144-145` |
| Copilot | `copilot/instructions/<nome>.instructions.md` copiado isolado | `README.md:147-148` |

Lido em `bfc400d` (2026-09-05):

- `scripts/validate-skills.py` — 411 linhas; `check_refs` (C1/C2) começa em `:75` e só julga inline
  paths que começam por `references/` ou `skills/` (`:97`), então `bug-hunter/references/x.md` nem é
  olhado; `check_limits` (C10) em `:309` já parseia a description com PyYAML — C13 reutiliza a mesma
  leitura; `main()` em 365-407 percorre `references/*.md` sem recursão (`glob`, não `rglob`).
- `scripts/selftest-validate-skills.py` — 72 linhas; cada mutação é `(relpath, mutate)` e o laço faz
  `p.read_text()` antes de escrever (`:65`), então uma mutação que CRIA arquivo (o órfão de C11) não
  cabe no laço de hoje.
- `generate.sh:171-173` — o sed do Cursor reescreve `](references/` para
  `](../../skills/${name}/references/`; `:176-185` — o wrapper Copilot é só dois links relativos
  (`../../skills/${name}/SKILL.md` e `../../skills/${name}/references/`).
- `openspec/specs/skills-authoring/spec.md:281-332` — *Authoring rules are machine-enforced* (texto
  copiado inteiro no delta); `:363-402` — *Triggers live in the description*, cujo cenário *Every
  skill states where it does not apply* é a regra que C13 passa a medir.
- As 35 descriptions parseadas: 16 sem literal "Do NOT use"; dessas, 10 redirecionam nomeando uma
  irmã sem crase ("see fivem-lua", "live in r3f-fundamentals", "that is fivem-nui-react", "use
  openspec-drivezone") e 6 não nomeiam ninguém ou nomeiam sem redirecionar (`python-rest-api`: "The
  baseline that api-resilience-testing and bug-hunter assume"; `svg-animation`: "the r3f-* skills").

## Goals / Non-Goals

**Goals**

- A regra de referência cruzada escrita no spec com um cenário por forma de instalação.
- Cada regra mecânica vira um check com selftest e com o que não cobre declarado dentro do check.
- Zero achados dos três checks nas skills que este item pode editar; os dois achados em
  `execute-backlog` nomeados como gap.
- Um `.mdc` ou `.instructions.md` copiado sozinho aponta `references/` para uma URL que responde 200.
- `bash generate.sh` duas vezes: segunda sem diff.

**Non-Goals**

- Pins `Verified against` como check (issue #131: exige provar em ambientes fora desta máquina).
- Reescrever a forma como Claude/Codex/plugins referenciam (funcionam: symlink e `@include` veem a
  árvore; o plugin copia a skill inteira).
- Inlinar `references/` no wrapper Cursor (a alternativa "inlining por forma de instalação" da issue):
  multiplicaria o tamanho dos `.mdc` e duplicaria doutrina que o spec manda manter num só lugar.
- Julgar caminhos `openspec/`, `scripts/`, `docs/`, `.github/`: a skill costuma estar descrevendo o
  repositório-alvo, e um check que não distingue isso reprovaria `documentation` inteira.
- Converter o link `SKILL.md` do wrapper Copilot em URL: R5 fala de `references/`; anotado em E.4.

## Decisions

### D1 — Forma canônica `skills/<skill>/references/<arquivo>` + frase, não URL nem inlining

Das três alternativas da issue (caminho canônico + declaração de dependência; URL; inlining por
`generate.sh`), a primeira é a única que resolve **e** continua legível dentro do clone, do symlink e
do `npx skills`: o prefixo `skills/` diz de onde o caminho parte e o nome da skill no meio diz o que
instalar quando ela não está. URL resolveria em todo lugar mas trocaria uma leitura local por uma
requisição de rede em cada consulta; inlining duplica doutrina. Fora de `skills/` (R2) a URL é a
única forma que resolve, porque nenhuma instalação carrega `research/` ou `claude/global/`.

### D2 — C12 julga três formas e declara o que não julga

(a) prefixo em `CATALOG_ONLY_ROOTS = (research/, claude/, codex/, cursor/, copilot/, plugins/)` —
entradas de topo que só um clone tem; (b) `<skill-do-catálogo>/references/…` sem `skills/` —
resolve em lugar nenhum; (c) link relativo com `..` que resolve fora de `skills/<x>/`. Tudo o mais
que C1 já aceita continua aceito. Caminhos sob `openspec/`, `scripts/`, `docs/`, `.github/` **não**
são julgados: `documentation` cita `docs/SETUP.md` (o repositório-alvo), `execute-backlog` cita
`openspec/config.yaml` (idem), e `verify-before-claiming/references/failure-catalog.md` cita
`scripts/validate-rite.sh` deste repositório — o check não distingue e a decisão foi declarar, não
adivinhar. O texto de link (`[research/svg-animation](https://…)`) é prosa: só o alvo é julgado, por
isso os links já em URL de `svg-animation` ficam mudos.

### D3 — C13 aceita lista literal ou redirecionamento nomeado

`ANTI_TRIGGER_PHRASES = ("Do NOT use", "do not use", "Not for", "that is `")` **ou**
`REDIRECT_WORDS = ("that is", "use", "see", "in", "to", "instead of")` seguido do nome exato de outra
skill do catálogo, com ou sem crase. Só a lista literal reprovaria dez descriptions que redirecionam
corretamente sem crase ("see fivem-lua"); só o redirecionamento aceitaria "Use when working in
fivem-lua" como cláusula — por isso o limite está escrito no check. `the r3f-* skills` não nomeia
skill e não passa: `svg-animation` passa a redirecionar a `r3f-animation`, a irmã que ganha o
redirecionamento recíproco (2D/SVG → `svg-animation`) neste mesmo item.

### D4 — C11 mede alcance, transitivo, só em `*.md`

BFS a partir de `SKILL.md` sobre links e inline paths (as duas bases que C1 aceita, mais a forma
`skills/<eu>/references/…`), fora de fences. Só `*.md` é julgado: `code-locale/references/*.py|txt|gz`
e `claude-statusline/references/statusline.sh` são carregados pelo markdown que os nomeia ou pela
ferramenta. Um link de diretório (`references/regimes/`) não alcança os arquivos dentro dele — um
índice linkado alcança; `svg-animation` já lista os 10 regimes um a um (`SKILL.md:103-112`), medido
zero órfãos em 29 skills com `references/`.

### D5 — Wrappers Cursor/Copilot por URL; o resto intocado

Cursor: o sed de `generate.sh:173` passa a reescrever `](references/` para
`](https://github.com/solvelab/ai-skills/blob/master/skills/${name}/references/`; e, quando a skill
tem `references/`, uma linha depois do frontmatter diz onde a pasta vive, porque a prosa do corpo
cita `references/x.md` em crase (não link) em 19 dos 35 `.mdc` — só 10 usam link — e o sed não toca
crases. Copilot: o link
`references/` vira `https://github.com/solvelab/ai-skills/tree/master/skills/${name}/references/`.
Probado: `curl -sI` nas duas formas de URL → `HTTP/2 200`. `claude/` (caminho `~/ai-skills/…` do
symlink), `codex/` (`@../../skills/…`, funciona porque o Codex lê a árvore) e `plugins/` (cópia da
skill inteira) não mudam.

### D6 — Os dois achados em `execute-backlog` ficam abertos, não editados

`skills/execute-backlog/**` é de outro item em paralelo. Editar duas linhas ali resolveria o gate
hoje e criaria conflito de merge amanhã; deixar o gate reprovar nomeando as duas linhas é o
comportamento que o check existe para ter. Registrado em `tasks.md` S.3 e no PR como gap, com o
comando que o fecha (`sed` das duas linhas + bump patch de `execute-backlog`).

### D7 — O selftest ganha mutação que cria arquivo

O laço passa a ler `p.read_text()` só quando o arquivo existe (`""` caso contrário), para que a
mutação de C11 possa escrever `skills/r3f-geometry/references/orphan-probe.md`. As de C12 e C13
seguem a forma de sempre: anexar `bug-hunter/references/track-fivem-lua.md` em crase a `fivem-lua`;
substituir a description de `r3f-physics` por uma sem cláusula.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Forma canônica de referência cruzada e o que cada instalação garante | `skills-authoring` (spec, requisito novo) | move — decisão da issue #121 vira requisito; as skills só recebem a forma corrigida, nenhuma restata a regra |
| Um check declara dentro de si o que não cobre | `skills-catalog` (spec) + `verify-before-claiming` | already canonical — os três checks novos seguem o padrão dos dez existentes |
| Toda description diz onde não se aplica | `skills-authoring` (*Triggers live in the description*) | already canonical — C13 só passa a medir o cenário que já existe |
| Adversarial track por stack (`track-*.md`) | `bug-hunter` | link — cinco skills passam a citar `skills/bug-hunter/references/track-*.md` nomeando `bug-hunter`; nada é copiado |
| Verdict de spec e sua leitura pelo executor | `execute-backlog` (`references/spec-rite.md`) | link — `backlog/references/*.md` cita `skills/execute-backlog/references/spec-rite.md`; texto inalterado |
| Hook de locale no write | `code-locale` | already canonical — só o caminho `claude/global/hooks/locale-rite.py` vira URL |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — nomes de função, constantes e labels de selftest em inglês |

## Risks / Trade-offs

- **C12 pode reprovar uma citação legítima de arquivo do próprio catálogo sob `scripts/` ou
  `openspec/`.** → Não julga essas raízes (D2); o que perde está escrito no check.
- **C13 aceita "in <irmã>" numa frase-gatilho.** → Declarado como KNOWN LIMIT; a lista literal é a
  forma recomendada nas seis descriptions corrigidas.
- **URL no wrapper troca leitura local por rede.** → Só nos dois wrappers que o README manda copiar
  sem a árvore, onde o caminho relativo já não resolvia; probado 200.
- **Mudar seis descriptions pode mudar roteamento.** → Cada frase entre aspas presente antes está
  presente depois (tabela em `tasks.md` 3.x); só se adiciona cláusula de não-uso, nunca se remove
  gatilho; tudo ≤ 1024 (C10 já gata).
- **O gate reprova em `master` até `execute-backlog` ser corrigido.** → Dois achados, nomeados por
  arquivo e linha; o item dono fecha com uma edição de duas linhas (D6).

## Open Questions

Nenhuma. As contagens em `master` (12 C12, 6 C13, 0 C11), as URLs (200) e a forma dos wrappers foram
medidas e estão em `tasks.md` com comando e saída.
