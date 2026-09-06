## Context

O upstream (`ponytail`, MIT, v4.9.0, `974d940a`) é 159 arquivos e ~15,5k linhas, dos quais a
doutrina são ~120 (`skills/ponytail/SKILL.md`), copiadas byte a byte em sete adaptadores e checadas
no CI dele. O resto é distribuição. O payload portável é texto puro: a escada de sete degraus
(`:32-48`), a regra de causa raiz (`:50-54` — a única frase com medição isolada no upstream, 0/3 →
6/6), o bloco de regras (`:56-64`), o contrato de saída (`:66-75`), os carve-outs (`:90-112`) e a
lente de `ponytail-review` (tags, formato, `net:`, guarda de escopo).

O baseline deste catálogo (`research/lean-code/results/20260905-211512-baseline-defects.md`, lido em
`f11ba7a`) diz **o que** o modelo diário faz sem a doutrina: nenhum guard perdido, nenhuma
reimplementação, nenhum remendo só no caller — e over-build concentrado em quatro formas: exceção
custom para um guard (6/27), tolerância especulativa (6/27), helpers para um loop curto (4/27),
validação de tipo que ninguém pediu (3/27); mais docstring maior que o código (12/27) e 1/27 de
prosa maior que o diff. É essa distribuição, e não a do upstream, que ordena as seções da skill.

O catálogo já tem lar para o que não é volume: escopo (`verify-before-claiming:170-186`, *Off-script
guard*), fronteira de confiança (`fivem-lua`, `backend-resilience`), o que vem depois de um check
(`bug-hunter`), prosa (`documentation`), nomes (`code-locale`, com o ledger de `locale-ok:` em
`references/migration.md`). A skill nova aponta para cada um e não repete nenhum.

## Goals / Non-Goals

**Goals:**

- Um lar canônico para "quanto código sobra", escrito a partir das contagens medidas aqui.
- Verbatim onde o upstream mediu que a redação carrega o efeito; `references/upstream.md` marca o
  que é verbatim para uma edição futura saber o que toca.
- Carve-outs no topo, com links concretos, porque o risco medido fora ("trims everyday bad-input
  handling on 5/24 tasks") é exatamente cortar validação de entrada.
- Nenhum número sobre o efeito da skill até o arm dela rodar; o texto diz onde o número vai morar.
- O harness pronto para o arm da skill medir o mecanismo certo: skill instalada **e** bloco always-on.

**Non-Goals:**

- Persona "lazy", níveis de intensidade, scoreboard, help, flags, statusline, hooks, adaptadores.
- Reescrever a doutrina dos irmãos; hook novo; check de validador para "lean".
- Rodar a matriz, a lente nos três diffs ou escrever o veredito — parte paga, do mantenedor.

## Decisions

### D1 — Skill nova, não dobrar em `verify-before-claiming`

`verify-before-claiming` governa **se** uma afirmação ou um escopo é verdadeiro; esta governa
**quanto código sobra** quando o escopo já está certo. A lente de revisão (`delete:`/`stdlib:`/
`native:`/`yagni:`/`shrink:`) e o marcador `lean:` não teriam lar lá. Alternativa rejeitada:
seção nova em `verify-before-claiming` — misturaria dois eixos numa description que já está em 1024
e deixaria a lente sem nome para o roteador.

### D2 — Nome `lean-code`, categoria `process`, plugin `workflow`

"Lean" nomeia o que **sobra**, não velocidade: a persona "lazy" do upstream colide com "Prefer the
best long-term outcome over speed" das regras pessoais. `process` é a categoria de
`verify-before-claiming` e `code-locale`, e `generate.sh` a mapeia para o plugin `workflow`
(`group_of`, `git|process -> workflow`).

### D3 — Mapa verbatim / reescrito / descartado

| Item do upstream | Decisão | Motivo |
|---|---|---|
| Escada de 7 degraus + "runs *after* you understand the problem" (`SKILL.md:32-48`) | **verbatim** | −54 % vs −33 % da paráfrase: a redação carrega o efeito |
| "Bug fix = root cause, not symptom… grep every caller" (`:50-54`) | **verbatim** | única frase com medição isolada (0/3 → 6/6) |
| Bloco de regras (`:56-64`) | verbatim, duas edições | `ponytail:` → `lean:` com a gramática `<ceiling> -> <trigger>`; "ship the lazy version and question it in the same response" → deferir ao *Doing / Not doing / Assumptions* de `verify-before-claiming` (D6) |
| Contrato de saída `[code] → skipped: [X], add when [Y]` (`:66-75`) | trailer obrigatório; cai o teto "at most three short lines" | `verify-before-claiming` exige fontes inline; um teto duro brigaria com ele; a frase "every paragraph defending a simplification is complexity smuggled back in as prose" fica |
| Carve-outs (`:90-112`) | **verbatim** como seção de topo; a linha de hardware generalizada ("a constant that models the physical world stays a knob") | é o que manteve 20/20 seguro onde a paráfrase escorregou; PCA9685 é um exemplo, não a regra |
| Lente `ponytail-review` (tags, formato, ❌/✅, `net:`, guarda) | seção `## Reviewing a diff` na mesma skill | as 5 tags são os degraus vistos da cadeira do revisor; uma skill irmã duplicaria a escada |
| `ponytail-audit` | um parágrafo *Repo-wide* na lente | mesma lente, outra entrada |
| `ponytail-debt` | `references/simplification-ledger.md` | procedimento, não skill |
| `docs/platform-native.md` | `references/platform-native.md`, sem Swift, com nota de lookup | `skills-authoring` *Versioned external APIs are pinned* proíbe afirmar versão não probada |
| Persona "lazy", *Persistence*, *Intensity*, *Boundaries* ("stop ponytail"), gain, help, flags, statusline, hooks, MCP, adaptadores | **fora** | branding e distribuição |

### D4 — Marcador `# lean: <ceiling> -> <upgrade trigger>` e coexistência com `locale-ok:`

Separador ASCII `->` porque o ledger parseia (`grep -rnE '(#|//|--) ?lean: '`, depois split em
`->`); o upstream usa vírgula, que aparece dentro de qualquer teto ("global lock, per-account
locks…") e não separa nada. Um marcador por comentário: `locale-ok:` cobre a própria linha e a de
cima (`code-locale`, *Reviewing a diff*), então fica na linha acima do nome; `lean:` fecha a linha
de código. Um marcador sem `->` é linha do ledger com a tag `no-trigger`.

### D5 — Bloco always-on em `personal-rules.md` mais a skill

O mecanismo que o upstream mediu é regra **sempre presente** (a skill dele é copiada para o
`CLAUDE.md`/adaptador de cada host), não uma skill que o roteador escolhe. Oito linhas depois de
*Code Locale*, mesmo padrão de *Grounding*: as frases de efeito medido quase verbatim (escada, causa
raiz, sem interface de uma implementação, marcador + trailer, carve-outs, questionar = linha em
*Assumptions*) e o fecho com o link para a skill — nunca uma segunda cópia da doutrina (TR4). O mesmo
bloco, sem o heading, vai para `research/lean-code/arms-block.md`: é o que o arm `skill` injeta.

### D6 — O degrau 1 vira linha em *Assumptions*, nunca omissão muda

"Does this need to exist at all?" e o guarda de escopo puxam em direções opostas se cada um for
lido sozinho: um manda pular, o outro manda entregar o que foi pedido. A resolução já existe em
`verify-before-claiming:174-175`: a dúvida é uma linha em *Assumptions*, o usuário decide, e "User
insists on the full version → build it, no re-arguing" (carve-out verbatim) fecha o ciclo. A skill
linka, não reescreve.

### D7 — Seções ordenadas pelas contagens do baseline; nenhum número da skill

A escada e a regra de causa raiz vêm primeiro porque são o texto medido; depois *Rules* (exceção
custom 6/27, validação não pedida 3/27 → "no unrequested abstractions"), *What the delivery looks
like* (`prose_gt_code`, docstrings 29/102 → "if the explanation is longer than the code, delete the
explanation"), *Never simplified away* (o risco de cortar validação; `safe` 100 % é condição de
SHIP), *Reviewing a diff* (helpers 4/27 → `shrink:`), o marcador, e só então `## What the baseline
measured`, que cita as contagens **do baseline** e escreve "skill arm: measured in
`research/lean-code/results.md`" — nenhum número de ganho até a matriz rodar (FR2, FR3). O rodapé
cita os números do upstream com as condições deles (modelo, CLI, `n`) e diz que foram medidos lá.

### D8 — O arm da skill injeta o bloco pelo `CLAUDE.md` da célula, não pelo `personal-rules.md` real

No modo `settings-sources` a célula lê o `~/.claude/CLAUDE.md` **real** do mantenedor. Se o bloco
fosse medido só depois de entrar em `personal-rules.md` e ser puxado pelo `install.sh`, o baseline
também o veria — o mesmo tipo de contaminação que o upstream registrou. Por isso `--prepare-arms`
ganha `--claude-block <file>`: o arm `skill` grava `claude-snippet.md` = sentinela + conteúdo do
arquivo, o `baseline` grava só a sentinela; `arm.json` guarda `claude_block_sha256`; o preflight do
arm `skill` exige o bloco presente e o do `baseline` exige ausente; o `--selftest` ganha os dois
casos. Caminho para o CLI ler a skill: `skillOverrides.lean-code = "on"` (já no harness) exige
`~/.claude/skills/lean-code` existir — o mantenedor cria o symlink para a worktree antes de rodar,
e o preflight já recusa quando não existe. A regra de FR2 vale: o mantenedor roda o arm **antes**
de o bloco entrar no `personal-rules.md` real dele, ou mede o `rules_sha` e aceita que o baseline
de hoje é o de `6efed496`.

*Superado em parte por D10 (2026-09-06):* o caminho pelo symlink em `~/.claude/skills` não funciona
neste modo — o diretório de skills do usuário não é carregado; ficam o `--claude-block`, o sha do
bloco e o preflight do bloco.

### D9 — `platform-native.md` é lookup, não matriz de suporte

Cada linha "you think you need X → the platform has Y" é uma pista para o degrau 3/4, não uma
afirmação de disponibilidade. O cabeçalho diz isso e manda verificar contra o runtime pinado do
projeto; as versões que o upstream escreve ("Python 3.9+") saem, porque `skills-authoring` proíbe
afirmar versão não probada e nenhuma foi probada aqui. Swift sai (fora das stacks do catálogo).

### D10 — Três arms: `block` isola o mecanismo always-on e `skill` carrega a skill como skill de projeto

D8 supunha que `skillOverrides.lean-code = "on"` mais um symlink em `~/.claude/skills/lean-code`
levariam a skill à célula. Medido pelo mantenedor em 2026-09-05 (Claude Code 2.1.261, sessão
principal): com `--setting-sources project,local` o diretório de skills do usuário **não é
carregado** — três células da lente responderam "lean-code isn't in the available-skills list" e
tiveram leituras em `~/.claude/skills/` e `~/ai-skills/` negadas. O arm rotulado `skill` da stamp
`20260905-230209` (27 células, $9,08) mediu portanto sentinela + bloco, e só isso.

Decisão, em três partes:

1. **O arm `skill` carrega a skill como skill de projeto.** `--prepare-arms` grava em `arm.json`
   `project_skill_path` = `skills/lean-code` **deste checkout** e cada célula copia o diretório para
   `<workspace>/.claude/skills/lean-code` antes do commit da seed. Cópia, não symlink: uma célula em
   `acceptEdits` escreveria através de um symlink dentro do checkout, e a cópia deixa na seed o
   texto exato que a célula viu (`git add -f` de um symlink guardaria só o alvo). `HARNESS_PATHS` já
   exclui `.claude/`, então a cópia não entra em contador nenhum. Provado pago antes de mexer no
   harness: num cwd com esse layout, uma célula Haiku com `--tools ""` listou exatamente `lean-code`
   ($0,018) e uma com `--tools "Skill"` carregou a skill e devolveu o primeiro heading verbatim
   ($0,031). O preflight deixa de exigir `~/.claude/skills/lean-code` — irrelevante neste modo — e
   passa a exigir o caminho com `SKILL.md` no `skill` e ausente nos outros arms.
2. **Um arm `block` entre o baseline e a skill.** É exatamente o que a stamp `20260905-230209`
   mediu (sentinela + bloco, nenhuma skill), e isola o mecanismo que o upstream mediu — a regra
   sempre presente, equivalente da injeção por `SessionStart` do ponytail. A stamp é renomeada com
   `--relabel-arm skill block --reason …` (diretórios de célula, `arm` em results/summary/classify,
   `relabels` em `results.json`), nunca descartada: são $9 de medição do mecanismo always-on no
   modelo diário. Alternativa rejeitada: relatar a stamp como "skill, sem skill" em prosa — o
   `--report` agregaria dois arms diferentes sob o mesmo nome.
3. **A sonda vê a skill antes de a matriz pagar.** Quarto critério: uma chamada `--tools ""` pede a
   lista de skills disponíveis (só a lista, nunca uma skill citada no `CLAUDE.md` — o bloco cita
   `lean-code` em prosa); `skill_visible` 1/1 no `skill`, 0/1 em `baseline` e `block`, gravado por
   arm em `arms.json`; `--matrix --arms skill` recusa sem 1/1. É a contaminação que o upstream
   registrou, no sentido inverso: o arm de tratamento sem o tratamento.

Consequência para o veredito: a tabela do protocolo lê o arm `skill`; lida para `block`, isola o
mecanismo always-on e é relatada ao lado. `--report` aceita os três stamps e imprime o Δ de cada
arm de tratamento contra o baseline. O Claude Code atualizou para `2.1.263` em 2026-09-06; o arm
`skill` roda o binário `2.1.261` pinado (primeiro no `PATH`) ou o baseline e o `block` são
refeitos — a recusa por versão do `--report` é a regra, não o obstáculo.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Volume de código: escada de 7 degraus, causa raiz, regras de abstração, contrato `skipped:`, carve-outs, marcador `lean:` + ledger, lente `delete:`/`stdlib:`/`native:`/`yagni:`/`shrink:` | `lean-code` (**novo lar**) | move — do upstream para o catálogo, com atribuição MIT em `references/upstream.md` |
| Escopo *Doing / Not doing / Assumptions*; trabalho não pedido é claim não verificado | `verify-before-claiming` | link — a regra "ship the lazy version and question it" é reescrita como deferência; degrau 1 vira linha em *Assumptions*; uma linha *See also* de volta |
| Fronteira de confiança (validar payload, ator vem de `source`, clamp, safe defaults) | `fivem-lua`, `backend-resilience` | link — *Never simplified away* aponta, não reescreve |
| O que vem depois de um check: metodologia adversarial | `bug-hunter` | link — "one runnable check" é o piso em `lean-code`; o que passa disso é `bug-hunter`; uma linha *See also* de volta |
| Contenção de dependência (stdlib-only em container bare, "no new supply chain for ergonomics") | instância em `log-event-collector`; degrau geral em `lean-code` | link — o irmão mantém o texto e ganha uma linha *See also* para o degrau geral |
| Ledger de dívida de nomes (`locale-ok:`, tiers de migração) | `code-locale` (`references/migration.md`) | already canonical — `lean-code` só define a coexistência dos dois marcadores; uma linha *See also* em `code-locale` |
| Deletar seção morta, não copiar o que a ferramenta gera (prosa) | `documentation` | already canonical — `lean-code` defere para prosa em *When this skill defers* |
| `/simplify` e `/code-review` nativos do Claude Code | built-ins do harness, não skill | link — uma frase em *Reviewing a diff* diz que a lente roda **antes** dos dois |
| Método de medição (arms, célula, vereditos, sonda) | `research/lean-code/protocol.md` (não é skill) | already canonical — a skill cita o arquivo por URL, nunca o método |
| Números de efeito só quando medidos aqui | `skills-catalog` (*A published cost claim carries re-runnable backing*) | already canonical — `## What the baseline measured` cita as contagens do baseline e nomeia onde o arm da skill vai morar |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `claude_block`, `claude_block_sha256`, `arms-block.md` |

## Risks / Trade-offs

- **Cortar validação de entrada** (5/24 no benchmark externo) → carve-outs como seção de topo com
  links concretos; `safe` 100 % nas cinco tarefas de fronteira é condição de SHIP no protocolo; a
  tarefa de fronteira da simulação paga tem de manter o guard.
- **Conflito com o guarda de escopo** → D6: degrau 1 é linha em *Assumptions*, nunca omissão muda.
- **Diluição por paráfrase** → verbatim onde medido; `upstream.md` marca o que é verbatim.
- **Description ampla dispara em todo prompt de código** → medida offline em S.1 pela simulação
  lexical (6 prompts, 3 lean e 3 não-lean) e em sessão real pelo mantenedor; estreitar num
  follow-up se nunca disparar ou se roubar prompts de irmãos, não adivinhar agora.
- **O bloco always-on chega ao `personal-rules.md` real antes da matriz** → D8: o arm injeta o
  bloco pela célula; `rules_sha` em `arm.json` torna a deriva visível; o mantenedor roda a matriz
  com o `personal-rules.md` de `master` ou registra o sha.
- **Custo da matriz** (≈ $8–17 em Opus, inferido das médias do baseline) → `--max-budget-usd 1.00`
  por célula e `--budget-usd 15` na run.
- **`agentskills validate` 0.1.1 é o validador de referência** → rodado no venv da sessão; se o venv
  não existir a ausência é dita, não substituída.

## Open Questions

Nenhuma aberta para a parte A. A parte B (matriz, lente, veredito, `results.md`) fica com o
mantenedor e suas linhas estão por marcar no `tasks.md`, com os comandos exatos.
