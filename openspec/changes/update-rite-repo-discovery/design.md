## Context

Lido em `6fbda3a` (`chore(release): 3.5.1`, topo de `origin/master`) em 2026-10-04, numa extração
`git archive origin/master` — o checkout local `~/ai-skills` está em `1abce62`, 2 commits atrás, e
entre os dois nenhum arquivo citado aqui mudou além de `.github/workflows/ci.yml`.

Cada artefato acha o repositório a partir do `cwd`, cada um de um jeito:

- `claude/global/hooks/backlog-rite.py:110-116` — `has_spec_rite` testa só
  `os.path.isdir(os.path.join(cwd, SPEC_RITE_DIR))`; `cwd` ausente ou não-string vira `os.getcwd()`.
  As fixtures do selftest (`:162-165`) são `with-rite/openspec` e `without-rite`, **sem** `.git`, e o
  docstring (`:46-50`) promete que o resultado "does not depend on where it runs".
- `claude/global/hooks/locale-rite.py:383-384` e `:300-302` — `root = Path(cwd) if cwd else
  Path.cwd()`, `check.load_allowlist(root)`, `check.project_relative(path, root)`. Na mesma hook,
  `declared_prose` (`:267-282`) já sobe a partir do arquivo escrito e só cai no `cwd` quando a subida
  não achou fronteira nenhuma.
- `claude/global/hooks/locale-stop-gate.py:318-321` — `git rev-parse --show-toplevel` a partir do
  `cwd`; `top is None` (git ausente ou timeout) e `top[0] != 0` (não é repo) dão o mesmo `None`, e
  `evaluate` sai mudo (`:442-445`). O docstring declara o limite (`:99`: "A repository other than the
  one `cwd` is in, or a working directory outside any git work tree").
- `skills/backlog/SKILL.md:96-97` e `skills/execute-backlog/references/spec-rite.md:13-17` —
  `[ -d openspec ]` e `openspec list` relativos ao `cwd`, enquanto o passo 2 da mesma skill sobe até a
  raiz para achar a config (`SKILL.md:79-80`). `spec-rite.md:48` nomeia "`.github/backlog.yml`, or
  the workspace `backlog.yml`" sem dizer de qual repositório.
- Funções do detector que os hooks chamam (`skills/code-locale/references/check-identifier-locale.py`):
  `load_allowlist` (`:456-466`) sobe a partir do diretório dado e para no primeiro
  `.identifier-locale-allow`; `project_relative` (`:528-541`) devolve só o nome do arquivo quando ele
  está fora do `root`; em modo diff o tier de caminho compara a allowlist com o caminho relativo ao
  repositório (`:716-717`); `PathFinding.render` (`:296-302`) imprime `{self.path}` como a linha a
  acrescentar na allowlist.
- `skills/code-locale/references/check-prose-locale.py:167-181` — `find_declaration` para no primeiro
  `.code-locale` **ou** `.git` (`:179`, `(parent / ".git").exists()`), então não é uma subida pura até
  a raiz do repositório.

Decisões anteriores que esta change revê, citadas:

- `openspec/changes/archive/2026-08-23-add-spec-rite-gate/proposal.md:40` — "a frase extra é emitida
  apenas quando há `openspec/` no `cwd` do payload". A condição continua sendo "o workflow existe";
  muda **onde** ela é medida: do `cwd` até a raiz do repositório dele (o mais próximo vale), e nos
  filhos de uma raiz de workspace.
- `openspec/changes/archive/2026-09-05-add-locale-stop-gate/design.md:62` — non-goal "Medir
  repositórios fora do `cwd` [...] (KNOWN LIMIT, no docstring)". O non-goal se estreita para "outro
  repositório quando o `cwd` já está num": os filhos de uma raiz de workspace passam a ser medidos.

## Goals / Non-Goals

**Goals:**

- Cada artefato age sobre o repositório a que o trabalho pertence: a raiz git acima do `cwd`, em
  qualquer profundidade; da raiz de um workspace, cada repositório filho. Mudo só onde não há
  repositório nenhum.
- Com o `cwd` na raiz de um repositório, cada artefato decide como hoje para o trabalho dentro dele;
  as duas exceções são declaradas — a escrita num arquivo de outro repositório, medida pela raiz
  dele (FR6, D4), e o Stop que passa do prazo (D5). Os casos atuais dos três selftests mantêm nome e
  resultado esperado.
- Os selftests não dependem do repositório em que rodam (o docstring do `backlog-rite.py` já promete
  isso; a subida nova o ameaçaria se as fixtures ficassem sem `.git`).

**Non-Goals:**

- Outro repositório quando o `cwd` já está num (sessão em `mantis-computer/` escrevendo em
  `../mantis-contracts/`): continua limite declarado — saber o que o turno escreveu exigiria ler o
  transcript.
- Workspace com mais de um nível; os hooks lerem `workspace.repos` do `backlog.yml`.
- A busca de `load_allowlist` acima da fronteira do repositório (`check-identifier-locale.py:458-465`).
- A raiz errada do `scripts/validate-spec-rite.py` (#260); Rust no `check-identifier-locale.py`.

## Decisions

### D1 — A raiz é a primeira `.git` subindo no sistema de arquivos, sem chamar git, nos dois hooks que não chamam git

`backlog-rite.py` e `locale-rite.py` sobem a partir do diretório inicial (resolvido, como
`find_declaration` faz em `check-prose-locale.py:174`) até o primeiro diretório que contém `.git` —
diretório ou arquivo, porque work tree ligada e submódulo usam arquivo (TR1). No `backlog-rite.py` a
mesma subida olha `openspec/` em cada nível, do `cwd` até a raiz (D3). O Stop gate continua com
`git rev-parse --show-toplevel`, que já paga e já precisa; onde o git e a subida discordam sobre o que
é um repositório, o limite é declarado (D5), não resolvido com uma terceira cópia da subida.

Alternativas consideradas:

- **Helper compartilhado em `skills/code-locale/references/`** — rejeitado: amarra `backlog-rite.py`
  (hoje só stdlib) a arquivos da skill `code-locale`, obriga um terceiro bump de `metadata.version` e
  mais cópias geradas, por uma função de seis linhas.
- **Reusar a fronteira de `find_declaration`** — rejeitado: ela para num `.code-locale` aninhado, que
  pode estar numa subpasta, e devolveria uma "raiz" que não é a do repositório.
- **`git rev-parse` no `backlog-rite.py`** — rejeitado (TR1): um processo por prompt num hook de
  `UserPromptSubmit`, para responder o que um `stat` responde.

A subida existe duas vezes (uma por hook): `# lean: subida de seis linhas duplicada em dois hooks ->
extrair quando um terceiro chamador aparecer`. Precedente da casa para duplicar em vez de importar:
`split_nul_paths` em `scripts/validate-spec-rite.py:176-184`.

### D2 — Raiz de workspace: fora de qualquer repositório, com filhos diretos que têm `.git`

A definição é a da skill `backlog` (`SKILL.md:81-82`; `backlog-config.md:8`, "a directory whose
subdirectories are git repos of one org"), sem redefinição (TR2). Só filhos diretos, em ordem de
nome, para que a saída seja determinística. Os hooks **não** leem `workspace.repos`:
`# lean: todo filho com .git é medido -> ler workspace.repos quando um clone alheio medido for
reportado como ruído`. A saída para esse caso já existe hoje: a allowlist do filho e
`LOCALE_RITE_MODE=inform`.

### D3 — `backlog-rite.py`: a frase segue o repositório; na raiz do workspace, nomeia os filhos

Quatro ramos, nesta ordem:

1. Raiz achada acima do `cwd` → a frase de hoje se algum diretório do `cwd` até a raiz, inclusive,
   tem `openspec/` — o mais próximo vale (FR1). É a resolução da própria CLI:
   `findRepoPlanningRootSync` devolve o ancestral mais próximo com `openspec/`
   (`dist/core/planning-home.js:37-38` do `@fission-ai/openspec` 1.6.0 instalado), e aqui ela para
   na raiz do repositório. Olhar só `<raiz>/openspec` regrediria um caso que hoje dispara: medido em
   2026-10-04 com o hook de `6fbda3a`, `cwd=mono/packages/app` (com `openspec/`, raiz `mono` sem) →
   frase presente, e `openspec list --json` dali → `nearest` em `mono/packages/app`.
2. Sem raiz, `<cwd>/openspec` existe → a frase de hoje. O OpenSpec não exige git; tirar esse ramo
   apagaria em silêncio o lembrete que existe hoje num diretório assim.
3. Sem raiz, filhos com `.git` **e** `openspec/` → uma frase só, nomeando esses filhos e só eles
   (FR2), dizendo que a change nasce e é validada **naquele** repositório.
4. Nada disso → sem frase, como hoje.

Selftest: as fixtures atuais ganham `.git`, para que a subida pare nelas e o resultado não dependa do
`TMPDIR`; os 16 casos mantêm nome e resultado, e um caso novo fixa a subpasta que carrega `openspec/`
abaixo de uma raiz que não carrega (frase presente, como hoje). Os casos novos que precisam de um
diretório **fora** de qualquer repositório (raiz de workspace com e sem filho com `openspec/`, o
ramo 2) verificam essa pré-condição e imprimem `SKIP` com o motivo quando o diretório temporário
está dentro de um repositório — o mesmo padrão de `locale-rite.py:839-847`. Alternativas: um
parâmetro de teto só para o selftest (mais superfície no caminho de produção) ou honrar
`GIT_CEILING_DIRECTORIES` numa subida que não chama git (semântica emprestada que ninguém pediu);
ficou o precedente.

### D4 — `locale-rite.py`: allowlist e caminho medido saem da raiz do repositório do arquivo escrito

Um helper (TR4) devolve a raiz do repositório do arquivo escrito, subindo a partir do diretório do
arquivo (D1), e o `cwd` do payload — ou `Path.cwd()` — só quando a subida não acha repositório
nenhum: a regra que `declared_prose` (`:274-276`) já segue para a declaração de prosa. `findings_for`
e `prose_findings_for` passam a usá-lo; `declared_prose` fica como está, porque a declaração tem a
própria subida (para em `.code-locale`).

Efeito medido nas fixtures (2026-10-04, hooks de `6fbda3a`): da raiz de workspace, `Write` em
`child/servicos/x.py` com `servicos` na allowlist do filho → `deny` hoje; de `child/` → mudo. De
`src-tauri/`, `Write` em `crates/core/src/servicos/x.rs` do mesmo repo → mudo hoje (o caminho medido
vira `x.rs`); da raiz do repo → `deny` com `path-pt-noun`. Depois da change, os dois pares decidem
igual qualquer que seja o `cwd`.

Selftest: o caso da allowlist (`:674-682`) e o da escrita em arquivo legado (`:687-722`) usam um
diretório temporário sem `.git` como `cwd`; ganham `.git`, para que a subida pare neles. O rótulo do
primeiro passa a dizer "of the written file's repository"; o resultado esperado não muda.

### D5 — `locale-stop-gate.py`: da raiz de workspace, cada filho; um motivo; um teto de linhas; um orçamento de tempo

- **Raiz de workspace.** `rev-parse` que devolve `None` (git ausente ou timeout) continua deixando o
  hook mudo; código de saída diferente de zero (não é repositório) passa a listar os filhos diretos
  com `.git`. Sem filho, mudo, como hoje — o caso `cwd outside a git work tree is silent`
  (`:769-774`) continua valendo, porque `no-repo` não tem filho repositório. rc≠0 também sai de um
  repositório que o git não consegue abrir — medido em 2026-10-04: um `.git` arquivo que aponta para
  um gitdir inexistente dá `fatal: not a git repository: /nowhere/.git/worktrees/x` e rc=128, onde a
  subida de D1 vê uma raiz. Ali o Stop gate trata o `cwd` como raiz de workspace e mede só os filhos
  com `.git` que houver; o KNOWN LIMIT declara isso, em vez de uma terceira cópia da subida.
- **Cada filho pelo caminho existente** (TR3): `uncommitted_diff` (`:311-366`), `gating_findings`
  (`:369-374`, allowlist da raiz do filho) e `prose_findings` (`:256-273`, `.code-locale` da raiz do
  filho). Nada de diff unido entre repositórios: cada diff é medido contra a própria allowlist.
- **Caminho prefixado, saída intacta.** O motivo junta os achados de todos os filhos; cada linha de
  achado ganha `<filho>/` na frente, e a última linha que `PathFinding.render` imprime — a linha a
  acrescentar na allowlist — continua relativa ao filho. Medido: com o mesmo arquivo
  `servico_cliente.py` (conteúdo inglês) num filho, a entrada `child/servico_cliente.py` na allowlist
  do filho → `block`; a entrada `servico_cliente.py` → mudo. Reescrever `finding.path` com o prefixo
  publicaria uma saída que não funciona quando seguida — a "blind second attempt" que o write gate já
  evita. Alternativa rejeitada: agrupar por filho sob um cabeçalho (motivo mais longo contra o teto de
  2000 caracteres, e FR5 pede o caminho prefixado). O `FOOTER` (`:220-224`) passa a dizer "at the
  root of the repository that holds the file", e o comando de `UNMEASURED_REASON` (`:206-214`) vira
  `git -C <filho> diff HEAD | ...` por filho, porque `git diff HEAD` falha na raiz do workspace. O
  achado de prosa não imprime linha própria de allowlist: o render dele
  (`check-prose-locale.py:451-458`) manda "list the path in .identifier-locale-allow" sobre o caminho
  da primeira linha, que na raiz do workspace sai prefixado, e `path_allowlisted` (`:473-476`)
  compara com o caminho relativo ao filho. O `FOOTER` diz que a entrada da allowlist é o caminho sem
  o prefixo `<filho>/`, no `.identifier-locale-allow` do filho.
- **Teto e tempo compartilhados.** `MAX_DIFF_LINES` vale para o conjunto: cada filho recebe o que
  sobrou. O tempo ganha um prazo único para a execução, abaixo dos 30 s da fiação (`:123-131`, e
  `"timeout": 30` em `~/.claude/settings.json:215`): cada chamada git usa
  `min(GIT_TIMEOUT, tempo restante)`, e o filho não alcançado no prazo é declarado não medido, com a
  semântica do teto de linhas — bloqueia uma vez dizendo o que faltou e como medir, e no Stop seguinte
  vira mensagem. Uma chamada que estoura `GIT_TIMEOUT` com prazo sobrando continua silenciando,
  agora só aquele filho: a regra que já existe, por filho, para que um repositório travado não apague
  os achados dos outros.
- **Prazo esgotado não é timeout de git, nem no meio de um filho.** `run_git` hoje devolve `None`
  para os dois (`:294-295`), e a volta dos arquivos não rastreados pula com `continue` a chamada que
  devolve `None` (`:361-363`). Reaproveitada como está, uma chamada encurtada pelo prazo pularia em
  silêncio o resto dos arquivos do filho, e o filho entraria como medido. Por isso: com o prazo
  esgotado nenhuma chamada git nova é aberta (um `timeout` zero ou negativo ainda abriria o
  processo), a chamada encurtada pelo prazo é distinguível da que estourou `GIT_TIMEOUT`, e o filho
  interrompido entra como truncado — a semântica do teto. O selftest fixa o prazo esgotado antes de
  um filho e no meio dos arquivos não rastreados de um filho.
- **O custo do prazo em toda volta.** Um workspace cuja medição passa do prazo em todo Stop bloqueia
  uma vez por turno (no Stop seguinte vira mensagem). O docstring declara quantos filhos cabem no
  prazo e as saídas para esse caso: rodar de dentro do filho, ou `LOCALE_RITE_MODE=inform`.
- **Por que um prazo e não um número fixo de filhos.** O custo por repositório varia com o sistema de
  arquivos e, em 9p, de uma corrida para outra: o hook inteiro, com diff limpo, levou 1,11-2,12 s em
  `mantis-computer` (9p, `/mnt/d`) numa série sem comando registrado e 0,65-0,82 s em duas séries de
  3 com o comando em E.2, e 0,09-0,16 s em repositórios em tmpfs (2026-10-04). Um teto de filhos
  fixo seria um chute; o docstring declara os números medidos e quantos filhos cabem no prazo em cada
  caso, como TR3 pede. O mesmo prazo passa a valer para um repositório só: cada arquivo não
  rastreado custa uma chamada git (`:354-365`), então um repositório só também pode, em tese, passar
  do timeout da fiação — quanto isso custa em 9p não foi medido, e o que o harness faz nesse caso
  também não (Open Questions); com o prazo, o hook termina declarando o que faltou em vez de depender
  do kill.
- **"under one second" sai do requisito.** Medido acima: em 9p um repositório limpo ficou ora abaixo,
  ora acima de um segundo no mesmo dia — um segundo fixo não é uma garantia que o hook possa dar ali,
  e da raiz de um workspace o custo soma por filho. O requisito passa a falar de "o prazo que
  declara".

### D6 — Skills: o rito é detectado e operado onde vive para o repositório alvo

- Detecção: em modo repo, o `openspec/` mais próximo do `cwd` até a raiz que
  `git rev-parse --show-toplevel` dá (a regra de D3); em modo workspace, `<repo>/openspec` de cada
  repositório afetado (TR2/TR5). A CLI responde a mesma pergunta: `openspec list --json` traz
  `root.source` (`nearest` quando achou um `openspec/`, `implicit` quando não) e `root.path` —
  medido em 2026-10-04: raiz do workspace do Mantis → `implicit`; `mantis-computer/` e
  `mantis-computer/src-tauri` → `nearest` em `mantis-computer`. Um `root.path` fora da raiz git não é
  o workflow deste repositório. Testar só `<raiz>/openspec` regrediria o que o `[ -d openspec ]` de
  hoje acha: medido, de `mono/packages/app` (repositório `mono` sem `openspec/` na raiz),
  `[ -d openspec ]` → found e `[ -d "$root/openspec" ]` → not found. Não sobra `[ -d openspec ]`
  relativo ao `cwd` nos dois arquivos que a issue lista.
- Comandos: `openspec list`, `openspec new change`, `openspec validate` rodam com o diretório onde o
  workflow vive como diretório de trabalho. O `openspec` 1.6.0 não tem opção de caminho
  (`openspec list --help` só traz `--specs`, `--changes`, `--sort`, `--json`, `--store <id>`), sobe
  sozinho a partir de uma subpasta (medido em `mantis-computer/src-tauri`), e na raiz do workspace
  responde `No active changes found.` — uma resposta que lê como "não há workflow".
- Policy em modo workspace: `.github/backlog.yml` do repositório afetado, depois `backlog.yml` do
  workspace, depois `required`. A tabela de precedência é escrita uma vez, em `backlog-config.md`;
  `spec-rite.md` linka.
- `issue-template.md`: em modo workspace, a seção Spec rite traz um veredito por repositório afetado
  que roda o workflow; um afetado sem workflow não ganha linha.
- `metadata.version` minor nas duas skills (`backlog` 1.5.2 -> 1.6.0, `execute-backlog` 1.9.0 ->
  1.10.0): muda o comportamento, como o precedente `e738120` (veredito de spec, `backlog` 1.4.0).
- O passo 5 do `execute-backlog` (`SKILL.md:105-109`, "repo with a spec-driven workflow only; skip
  when there is none") é o texto que FR4 nomeia, e é ele que vira no-op na raiz do workspace antes
  de o protocolo de `spec-rite.md` ser lido. Recomendação: a cláusula "detected for the target
  repository — from a workspace root, in each affected repository" entra. A issue não lista o
  arquivo, então a inclusão vai no comentário de ajustes aprovados (Migration Plan).

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| O rito backlog-first é imposto fora da discrição do modelo; o lembrete nomeia o spec rite onde ele existe | `skills-catalog` (spec do repositório), artefato `claude/global/hooks/backlog-rite.py` | already canonical — o delta modifica o requisito; o README e o docstring apontam para ele, sem repetir a regra |
| O gate de spec entre o item e a primeira edição: detecção, veredito, policy, archive | `execute-backlog` (`references/spec-rite.md`) | already canonical — a detecção onde o workflow vive para o repositório alvo (D6) entra ali; o passo 6 do `backlog` usa o mesmo comando e linka para o protocolo, sem reescrevê-lo |
| Modos repo/workspace, config e precedência (inclusive a de `spec_rite` por repositório afetado) | `backlog` (`references/backlog-config.md`) | already canonical — a precedência é escrita uma vez ali; `spec-rite.md` linka |
| Definição de workspace (filhos diretos com `.git`) | `backlog` (`SKILL.md:81-82`, `references/backlog-config.md:8`) | already canonical — os três hooks citam a definição no docstring, não a redefinem |
| Ciclo de vida do OpenSpec (proposal, delta, validate, archive) | `openspec` (e o fork do repositório) | link — nada é reescrito nas skills de backlog |
| Allowlist `.identifier-locale-allow`, `locale-ok:`, `.code-locale`, `LOCALE_RITE_MODE=inform` | `code-locale` | already canonical — os hooks mudam **de onde** leem, não o que essas saídas são; nenhum texto da skill `code-locale` muda |
| O hook mede no momento da escrita; o gate de Stop fecha o turno | `skills-catalog` (spec do repositório) | already canonical — o delta modifica os dois requisitos; os docstrings declaram o KNOWN LIMIT novo |
| Identificadores novos em inglês | `code-locale` | already canonical — os nomes vêm do Glossary aprovado no plano |

## Risks / Trade-offs

- **Workspace com muitos filhos ou diff grande estoura o Stop** -> teto de linhas compartilhado,
  prazo único abaixo do timeout da fiação, e o que não couber é declarado (D5).
- **Um clone alheio como filho passa a ser medido** -> saídas: a allowlist do filho e
  `LOCALE_RITE_MODE=inform`; `workspace.repos` fica como `# lean:` com gatilho (D2).
- **A frase nomeando filhos vira ruído** -> só filhos com `openspec/`, numa frase só (D3).
- **Selftest dependente do lugar** -> fixtures com `.git`; casos que precisam de "fora de qualquer
  repositório" verificam a pré-condição e imprimem `SKIP` (D3, D4).
- **Repositório aninhado (um repo dentro de outro)** -> a primeira `.git` vence, a mesma semântica do
  git; um caso de selftest fixa isso no `backlog-rite.py`.
- **`load_allowlist` ainda sobe acima da fronteira do repositório** -> fora de escopo por decisão da
  issue: um repositório sem allowlist própria ainda pode herdar a de um diretório pai; continua
  declarado.
- **Uma pasta qualquer com clones vira raiz de workspace** -> pela definição de TR2, `$HOME` desta
  máquina já é uma: `ls -d ~/*/.git ~/.[!.]*/.git` → `/home/diegops/.oh-my-zsh/.git/` e
  `/home/diegops/ai-skills/.git/`. Uma sessão aberta em `~` passa a ter o diff de `~/ai-skills` e do
  clone do oh-my-zsh medido em todo Stop, e o motivo manda renomear arquivos que a sessão não tocou.
  A saída é a de qualquer clone alheio (allowlist do filho, `LOCALE_RITE_MODE=inform`); o motivo do
  bloqueio nomeia o filho, e excluir diretórios ocultos fica como decisão do usuário, não como
  redefinição silenciosa de TR2.
- **Os hooks vivos mudam para toda sessão no merge** -> ver Migration Plan.

## Migration Plan

- **Onde implementar.** `~/.claude/settings.json` roda os hooks por caminho absoluto a partir da árvore
  de trabalho de `~/ai-skills` (`:121`, `:142`, `:148`, `:170`, `:214`), e cada hook carrega o check
  por `Path(__file__).resolve().parents[3]` (`locale-rite.py:155`, `locale-stop-gate.py:152`). Trocar
  de branch ou editar `~/ai-skills` troca os hooks de todas as sessões abertas de uma vez. A
  implementação vive numa `git worktree` **fora** de `~/ai-skills`, criada a partir de `origin/master`;
  `~/ai-skills` não sofre checkout, switch nem pull até o merge.
- **Ajustes aprovados, antes da primeira edição.** `execution-flow.md:34-35` manda registrar como
  comentário na issue os ajustes substantivos aprovados no plano. Entram ali: o prazo do Stop gate com
  bloqueio único para o que não foi medido, inclusive num repositório só (desvia de TR3 e da linha de
  Risks da issue), a cláusula do passo 5 do `execute-backlog/SKILL.md`, a resolução do `openspec/`
  mais próximo até a raiz, e os nomes NEW do Glossary.
- **Deploy.** Depois do merge, `~/ai-skills/update.sh` (fast-forward + `generate.sh`) move a árvore
  viva; a partir daí cada invocação de hook — um processo novo por evento — já roda a versão nova.
  Rollback: revert do PR e `update.sh` de novo.
- **Skills.** As sessões carregam as skills do cache de plugin
  (`~/.claude/plugins/cache/ai-skills/ai-skills-workflow/3.4.0`, marketplace `github`
  `solvelab/ai-skills`), não da árvore de trabalho; o texto novo chega com
  `claude plugin marketplace update ai-skills` + `claude plugin update ai-skills-workflow@ai-skills`
  + reinício da sessão, depois que o semantic-release publicar a versão.
- **Workspace do Mantis.** O comentário de `backlog.yml:50-53` e o `CLAUDE.md` da raiz ficam
  desatualizados no merge; atualizá-los cabe ao workspace (Dependencies da issue).
- **Archive.** PR separado depois do merge (`spec-rite.md:97-103`; precedentes #226, #234, #237,
  #245, #250, #253, #256).

## Open Questions

- O que o harness faz quando um hook de `Stop` passa do timeout (encerra o turno, trata como erro)
  não foi probado; é o que motiva o prazo de D5 em vez de confiar no kill.
- Se `--settings` soma ou substitui os hooks do escopo user, e se `--setting-sources project,local`
  suprime os hooks vivos e o plugin 3.4.0 instalado, foi lido só no `claude --help` (2.1.289). A
  corrida pelo harness (S.2) prova isso primeiro, antes de qualquer caso.
- Nomes novos aguardam aprovação no Glossary do plano: `find_repo_root`, `child_repos`,
  `spec_sentence` (substitui `has_spec_rite`, que passa a devolver qual frase anexar), `write_root`,
  `WORKSPACE_SPEC_RITE`, `TIME_BUDGET` (`time_budget` como parâmetro de `evaluate`).
- Valor do prazo (20 s, abaixo dos 30 s da fiação) versus um número fixo de filhos: a recomendação é o
  prazo (D5); um teto fixo é a alternativa com menos partes móveis.
- A cláusula de workspace no passo 5 do `execute-backlog/SKILL.md`: recomendado que entre (D6), e o
  registro vai no comentário de ajustes aprovados (rail 4 da skill).
