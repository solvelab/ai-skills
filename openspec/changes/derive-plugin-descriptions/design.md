## Context

`generate.sh` (201 linhas em `d2918ed`) gera os wrappers por ferramenta e, a partir da linha 145,
os plugins agrupados por categoria: `rm -rf plugins/`, cópia de cada `skills/<name>/` para
`plugins/<grupo>/skills/<name>/` (grupo = `metadata.category`, com `git|process -> workflow`), e um
`plugin.json` por grupo cuja `description` vem do array fixo `GROUP_DESC` (linhas 150-161), com o
fallback `:-Skill group ${group}` na linha 190. `VERSION_STR` é lido na linha 180 por
`tr -d '[:space:]'`, com `|| echo 0.0.0` se o arquivo faltar — depois de todos os wrappers já terem
sido gravados.

`.claude-plugin/marketplace.json` e `.claude-plugin/plugin.json` são escritos à mão; só o campo
`version` deles é tocado por `scripts/set-version.sh:18-19`, via `sed` sobre a forma literal
`"version": "<atual>"`. `set-version.sh` é o `prepareCmd` do semantic-release (`.releaserc.json`) e
chama `generate.sh` na linha 22, então a ordem no release é: `VERSION` → `sed` nos dois JSON →
`generate.sh` → commit dos assets (`plugins/**`, os dois JSON, `VERSION`, `CHANGELOG.md`).

`scripts/validate-repo-hygiene.py` tem dois checks (H1 bytecode, H2 `all N`) com um defeito
injetado cada no `--selftest`; H2 lê só `README.md` e `marketplace.json` (`COUNT_FILES`, linha 30).

## Goals / Non-Goals

**Goals:**

- Depois de `./generate.sh`, cada `plugins/<g>/.claude-plugin/plugin.json` e cada entrada do
  `marketplace.json` nomeia exatamente as skills do grupo, com a contagem certa; uma skill que muda
  de categoria altera os três artefatos na próxima geração sem edição manual.
- Um texto publicado que nomeia skill fora do grupo, omite uma do grupo, ou publica uma contagem
  nua, falha o build nomeando arquivo, grupo e diferença.
- `VERSION` inválido derruba o gerador com exit ≠ 0 antes de gravar qualquer arquivo, e
  `set-version.sh 1.2.3garbage` é recusado pela mesma regex.
- Segunda run de `generate.sh` sem diff; o release não produz segundo diff.

**Non-Goals:**

- Mudar a composição dos grupos (`group_of`, categorias das skills), o nome, a `source` ou a
  versão de qualquer plugin.
- `install.sh`, `update.sh`, `.github/workflows/ci.yml` (ver *Impact* na proposta).
- Gerar o `README.md`: ele continua escrito à mão; o que muda são as linhas listadas na proposta.
- Verificar semanticamente o texto do tema de cada grupo.

## Decisions

### D1 — O tema é a única coisa escrita à mão; nomes e contagem vêm de `plugins/<g>/skills/`

`GROUP_DESC` vira `GROUP_THEME`: uma frase por grupo, sem nomes de skill nem número. A descrição
publicada é montada na geração como `"<tema> (<N> skills: <nomes>)"`, com os nomes lidos por
`ls -1 plugins/<g>/skills/ | LC_ALL=C sort` — a ordem é fixada por locale para a saída ser a mesma
em qualquer máquina e a segunda run não produzir diff.

O fallback `:-Skill group ${group}` some. Um grupo que aparece na árvore sem tema derruba o gerador
com `❌ generate.sh: no GROUP_THEME for plugin group '<g>'` e exit 1. Uma categoria nova passa a
exigir um tema explícito, que é exatamente o momento em que alguém deveria decidir o que o plugin
novo é.

### D2 — `VERSION` é validado no topo do gerador, com uma regex partilhada

A guarda sai da linha 180 e vai para logo depois do `[ -d "$SKILLS" ]` da linha 24, antes do
primeiro `mkdir`/`>`: um `VERSION` inválido sai com exit 1 sem ter tocado `codex/AGENTS.md`, os
wrappers ou `plugins/`. A regex é `^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$`, guardada numa
variável (`SEMVER_RE`) porque `[[ =~ ]]` só trata a expressão como regex quando ela não vem entre
aspas. `set-version.sh:13` recebe a mesma string literal. O `|| echo 0.0.0` também some: um
`VERSION` ausente vira string vazia, que a regex recusa — `0.0.0` chegando a 10 `plugin.json` é a
mesma classe de defeito silencioso que `2.15.1dirtychange`.

`ci.yml:47` não recebe a regex nesta change (decisão do orquestrador). A cobertura em CI é
transitiva: o step *Wrappers in sync with skills/* roda `generate.sh` antes do step de coerência de
versão, então um `VERSION` inválido já falha ali.

### D3 — O gerador reescreve os dois JSON da raiz por round-trip JSON, e só o campo `description`

`generate.sh` passa a chamar um trecho `python3` embutido que carrega
`.claude-plugin/marketplace.json` e `.claude-plugin/plugin.json`, substitui só as `description`
e grava com `json.dumps(indent=2, ensure_ascii=False) + "\n"`. Medido em `d2918ed`: esse
round-trip reproduz os dois arquivos **byte a byte**, então a reescrita é idempotente por
construção e o campo `version` sai com a forma exata `"version": "X.Y.Z"` que o `sed` de
`set-version.sh:18-19` casa. Python foi escolhido em vez de `sed`/`awk` porque o valor é JSON com
travessão e setas em UTF-8 e porque o resto dos gates do repositório já depende de `python3`.

Regras da reescrita:

- entrada com `source: "./plugins/<g>"` recebe a descrição derivada do grupo `<g>`; grupo sem
  entrada, ou entrada cujo grupo não existe na árvore, derruba o gerador (adicionar/remover plugin
  é decisão humana, fora desta change);
- a entrada do bundle (`source: "./"`) publica `FULL bundle (all N skills). ...` com `N` = número
  de diretórios em `skills/`, que é a forma que H2 já gate;
- o `plugin.json` raiz recebe
  `Reusable AI skills for coding assistants — all N skills across M per-domain plugins: <g>: <tema>; ...`,
  com o `all N` na forma que H2 gate;
- o arquivo só é regravado quando o conteúdo muda.

### D4 — H3 verifica pertencimento; H2 recusa a contagem nua

H3 (`check_plugin_membership`) lê, para cada `plugins/<g>/skills/`, o conjunto de diretórios, e
exige em `plugins/<g>/.claude-plugin/plugin.json` e na entrada do `marketplace.json` com
`source: ./plugins/<g>` uma descrição casando `\((\d+) skills: ([^)]*)\)` em que `N` é o tamanho da
lista e a lista é igual ao conjunto de diretórios. A mensagem nomeia o arquivo, o grupo, os nomes
sobrando e os faltando (ou a contagem errada). Descrição sem o parêntese é finding: sem lista não há
o que comparar.

H2 ganha `UNSCOPED_COUNT_CLAIM = \((\d+) (?:topics|skills)\)`: uma contagem entre parênteses sem
lista de nomes. Ela não é comparada a nada — nem ao total nem a um grupo, porque o texto não diz a
qual conjunto se refere — e é reprovada pela forma, com a instrução de escrever `all N` (total,
H2) ou `(N skills: <nomes>)` (grupo, H3). Ela roda sobre `README.md`, os dois JSON da raiz e os
`plugin.json` por grupo. Em `README.md` ela ignora o interior de blocos ``` ``` ```: `README.md:345`
é um comentário numa árvore de diretórios ilustrativa (`r3f-*/SKILL.md # ... (10 topics)`),
verdadeiro hoje e fora das linhas que esta change edita; um comentário de diagrama não é a mesma
classe de claim que um cabeçalho ou um manifesto. `.claude-plugin/plugin.json` entra em
`COUNT_FILES`, para o `all N` da descrição raiz (D3) ficar sob H2.

O que os dois checks não cobrem, declarado dentro deles: o texto do tema (a parte antes do
parêntese) não é verificado semanticamente — um tema que diz "Kubernetes" num grupo de FiveM passa;
a tabela de `README.md:50-55` que nomeia as skills por plugin é prosa e fica review-only; contagens
dentro de blocos de código são review-only.

### D5 — README: a linha muda de tabela; o cabeçalho nomeia em vez de contar

`svg-animation` vai para a tabela Frontend, ao lado de `react-api-client`. O cabeçalho Game perde
"— 10 topics" e o parágrafo abaixo dele diz, por nome, o que o plugin `ai-skills-game` embarca além
das linhas da tabela (`assettoserver-plugin` e `assettoserver-csp-lua`, que têm tabela própria
acima). Sem número nenhum ali: um número escrito à mão numa prosa que H3 não lê é a deriva que a
change está removendo. As linhas 50-55 viram uma tabela `Plugin | Ships` com os nomes das skills de
cada plugin — também prosa, também review-only, e registrada como follow-up (gerar esse bloco a
partir da mesma fonte).

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Um check declara o que não cobre | `skills-catalog` (spec do repositório, *The uncovered part is declared, not implied*) | already canonical — H3 e o padrão novo de H2 aplicam a regra dentro de si, sem reescrevê-la |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — citado no grupo de simulação de `tasks.md` |
| Identificadores em inglês, prosa na língua do repositório | `code-locale` | already canonical — `GROUP_THEME`, `SEMVER_RE`, `check_plugin_membership` seguem o glossário da issue #114 |
| Formato de commit | `conventional-commit` | already canonical — nada é reescrito aqui |

Nenhuma skill do catálogo é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **Parêntese longo na UI do `/plugin`** (`workflow` com 7 nomes, `game` com 12, a descrição raiz
  com 10 temas). Truncamento não medido: nenhuma ferramenta local renderiza a listagem do
  marketplace sem instalar o plugin. Registrado como limite conhecido; `claude plugin validate
  --strict` não impõe tamanho (verificado na simulação).
- **Ordem no release.** `set-version.sh` grava `VERSION`, faz o `sed` da versão nos dois JSON e só
  então chama `generate.sh`; a reescrita de D3 lê a versão já nova e não a toca. Um `generate.sh`
  rodado **antes** do `sed` produziria o mesmo resultado, porque a versão não entra na derivação
  das descrições. Verificado na simulação com uma cópia do repositório e `set-version.sh 9.9.9`.
- **Dependência de `python3` em `generate.sh`.** Já era dependência de fato de todo gate do
  repositório e do runner (`ubuntu-latest`); passa a ser dependência do gerador também. Um ambiente
  sem `python3` falha alto no `python3 -` (exit 127 sob `set -e`), não em silêncio.
- **Um grupo novo exige três edições humanas** (tema em `GROUP_THEME`, entrada no
  `marketplace.json`, categoria em `ci.yml:58`). Trade-off aceito: a alternativa — o gerador
  inventar a entrada do marketplace — é a decisão automática que a issue explicitamente deixa fora
  de escopo.
- **H3 depende de uma forma textual** (`(N skills: a, b)`). Quem reescrever o formato da
  descrição no gerador precisa mudar a regex; o `--selftest` cai se a regex parar de casar, que é
  o comportamento desejado.

## Open Questions

Nenhuma. Os pontos que poderiam virar achismo — a fidelidade do round-trip JSON, o comportamento
de `[[ =~ ]]` com a regex ancorada, o de `set -u` sobre chave ausente em array associativo, e a
posição de `README.md:345` dentro de um bloco de código — foram medidos e estão em `tasks.md` com
comando e saída.
