## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion. Shape gated by scripts/validate-rite-evidence.py once ticked:
       E.1  a repo-relative path AND the commit sha or date it was read at
       E.2  at least one `command` -> a fragment of its output
       E.3  names the gap, or states explicitly that there is none
       E.4  lists a follow-up, or states explicitly that there is none -->

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `bfc400d` (topo de `master`, 2026-09-05):

      - `scripts/validate-spec-rite.py` — 338 linhas; `resolve_base()` (`SPEC_RITE_BASE`,
        `GITHUB_BASE_REF`, `origin/master`, `origin/main`), `read_pr_body()` com `PR_BODY` acima de
        `GITHUB_EVENT_PATH`, `changed_paths()` com `git diff --name-only <base>...HEAD`, `WAIVER` e
        `WAIVER_NO_REASON` ancorados no começo da linha, `MIN_REASON = 8`, `evaluate()` pura,
        `DEFECTS`/`SILENT`, skip impresso fora de `pull_request`, `S0` sem base em CI.
      - `.github/workflows/ci.yml` — 20 steps em `jobs.validate`; step *Skill frontmatter checks*
        com `grep -qE '^  version: [0-9]+\.[0-9]+\.[0-9]+'` sobre o bloco de frontmatter; step
        *Spec-rite self-test* em `:184-185`, seguido de *Claude plugin validation*.
      - `README.md:194` e `:864` — as duas frases da regra do bump (a issue cita `:180`/`:824`;
        o arquivo cresceu). `README.md:876-889` descreve o spec-rite no corpo do PR — não está entre os
        dois lugares deste item (ver E.4).
      - `skills/execute-backlog/SKILL.md` — `metadata.version: 1.8.0`;
        `skills/execute-backlog/references/spec-rite.md:78-88` — seção *In the PR body*.
      - `generate.sh:1-31` — copia o `SKILL.md` inteiro para `claude/skills/<x>/` e
        `plugins/<grupo>/skills/<x>/`; a linha `  version:` aparece portanto nas árvores geradas.
      - `openspec/specs/skills-authoring/spec.md` — *Uniform frontmatter metadata* exige o campo,
        não o movimento; *Authoring rules are machine-enforced* pede selftest com um defeito por regra.
      - `openspec/changes/archive/2026-09-04-close-ci-gate-holes/{proposal,design,tasks}.md` e
        `specs/**` — modelo de estilo.
      - `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md` e `schema.yaml`.
      - `scripts/validate-rite.sh` e `scripts/validate-rite-evidence.py:1-60,157-200` — a forma que
        cada caixa marcada deve ter.
      - Histórico: `cf767ee` (issue #76) e `e13c16a` (squash do PR #122 sobre `d2918ed`) via
        `git show --stat` — os dois pontos usados como fixture em S.1.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada; comando e fragmento da
      saída registrados

      ```
      openspec --version                                          -> 1.6.0
      python3 --version                                           -> Python 3.14.5
      ls skills | wc -l                                           -> 35
      openspec new change add-skill-version-gate --schema skills-rite
      -> Created change 'add-skill-version-gate' at openspec/changes/add-skill-version-gate/
      openspec validate add-skill-version-gate --strict           -> Change 'add-skill-version-gate' is valid
      ```

      Versões por skill nos dois pontos do histórico (script de probe com `git diff --name-only` +
      `git show <rev>:skills/<x>/SKILL.md | grep '^  version:'`):

      ```
      cf767ee^..cf767ee: 20 skill paths, 13 skills
      -> api-resilience-testing: base=['  version: 1.2.1'] head=['  version: 1.2.1']
      -> backlog: base=['  version: 1.3.0'] head=['  version: 1.3.0']
      -> code-locale: base=[] head=['  version: 1.0.0']
      -> execute-backlog: base=['  version: 1.5.0'] head=['  version: 1.5.0']
      -> [...] 12 skills com base == head, 1 sem SKILL.md na base
      d2918ed..e13c16a: 6 skill paths, 6 skills
      -> api-resilience-testing: base=['  version: 1.2.1'] head=['  version: 1.3.0']
      -> execute-backlog: base=['  version: 1.7.0'] head=['  version: 1.8.0']
      -> [...] 6 de 6 com head > base
      ```

      ```
      grep -rln "version: 1.8.0" claude codex cursor copilot plugins | grep execute-backlog
      -> claude/skills/execute-backlog/SKILL.md
      -> plugins/workflow/skills/execute-backlog/SKILL.md
      python3 -c "import importlib.util; ..." (módulo carregado por spec_from_file_location sem registrar em sys.modules)
      -> AttributeError: 'NoneType' object has no attribute '__dict__'   (dataclasses.py:814, Python 3.14.5)
      ```

- [x] E.3 O que não pôde ser probado

      - O comportamento do gate **na run real do GitHub Actions** (payload `GITHUB_EVENT_PATH` escrito
        pelo runner, `GITHUB_BASE_REF` real, `fetch-depth: 0`) não é medível localmente; foi
        reproduzido com payload fabricado e ambiente `GITHUB_ACTIONS=true` num clone descartável
        (S.1). A prova final é a run do PR desta change.
      - `V0 base revision` (checkout raso em CI) não foi exercitado end-to-end: exigiria um clone com
        `--depth 1` sem `origin/master`; a regra é cópia literal do `S0` do irmão, que também só a
        declara.
      - Semver com pré-release: nenhuma skill do catálogo usa (`grep -E '^  version: .*-' skills/*/SKILL.md`
        -> vazio), então o comportamento "sufixo mudou, tupla igual → não moveu" é lido do código, não
        observado num caso real; declarado no KNOWN LIMIT.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #119 e a decisão da Opção A pediram e nada além. Notados pelo caminho
      e **não** feitos, como follow-up:

      - `README.md:876-889` (seção *3. Release*) descreve o que o CI lê no corpo do PR e cita só a
        linha `Spec-rite`; não é um dos dois lugares da regra do bump que este item possui. Adicionar
        ali a linha `Skill-version` é follow-up.
      - Bumps retroativos nas 20 skills medidas na issue — fora de escopo pela própria issue.
      - `validate-spec-rite.py` importado por `spec_from_file_location` sem `sys.modules` funciona
        porque não tem `@dataclass`; este gate registra o módulo antes do `exec_module`. Fazer o
        mesmo no irmão é higiene, não deste item.
      - `gates.sh` (runner local do orquestrador, fora do repositório) não roda o gate novo; foi rodado
        à parte em S.1.
      - `validate-spec-rite.py` lê o diff sem `-z` e recebe caminhos com aspas e escapes octais quando
        `core.quotePath` está ativo (padrão); como a regra dele é "existe caminho fora de `openspec/`",
        o caminho quotado continua ofensor e o gate falha fechado — mas a mensagem nomeia o caminho
        escapado. Trocar para `-z` lá é higiene do irmão, não deste item.

## 2. O gate `scripts/validate-skill-version.py` (D1–D6)

- [x] 2.1 `resolve_base`, `changed_paths`, `read_pr_body` e o skip fora de `pull_request` no idioma
      de `validate-spec-rite.py`; `MIN_REASON` importado do irmão. Única divergência (revisão do PR,
      D1): `changed_paths` roda `git diff --name-only -z` e separa por NUL — sem a flag um caminho
      com byte não-ASCII chega quotado (`"skills/x/caf\303\251.md"`) e `skills_in()` o descarta

      ```
      grep -n "def resolve_base\|def read_pr_body\|def split_nul_paths\|def changed_paths\|MIN_REASON = \|not pull_request\|\"-z\"" scripts/validate-skill-version.py
      -> 101:MIN_REASON = _sibling_min_reason()
      -> 120:def resolve_base(root: Path) -> str | None:
      -> 136:def read_pr_body() -> str:
      -> 162:def split_nul_paths(out: str) -> list[str]:
      -> 168:def changed_paths(root: Path, base: str, head: str = "HEAD") -> list[str]:
      -> [...] "diff", "--name-only", "-z", f"{base}...{head}"],
      -> [...] print(f"  skill-version gate: skipped (event {event}, not pull_request)")
      python3 scripts/validate-skill-version.py --selftest | grep MIN_REASON
      -> HELPER  MIN_REASON agrees with the spec-rite gate
      ```

- [x] 2.2 `collect()` lê o diff por skill: caminhos sob `skills/<x>/`, versão na base e no HEAD, e
      se o conteúdo mudou além da linha `  version:`; árvores geradas ignoradas

      `collect(root, base, head)` em `:214`; medido contra o histórico real em S.1 (13 skills em
      `cf767ee`, `code-locale` com `base_version=None`; 6 em `e13c16a`). Helpers no selftest:

      ```
      python3 scripts/validate-skill-version.py --selftest | grep HELPER
      -> HELPER  version parsed from frontmatter
      -> HELPER  version-only edit compares equal
      -> HELPER  body edit compares different
      -> HELPER  semver orders numerically, not lexically
      -> HELPER  generated trees are dropped
      -> HELPER  references group under their skill
      -> HELPER  NUL-separated names are read verbatim, quotes and newlines included
      -> HELPER  a non-ASCII name still groups under its skill
      -> HELPER  changed_paths() survives core.quotePath on a real repository
      ```

      O último helper é a única sonda de plumbing do selftest (`_probe_quoted_path()` em `:347`):
      `git init` num diretório temporário, dois commits, `skills/probe/references/café.md` no segundo,
      `core.quotePath=true` forçado. Mutação (mesmo script com `-z` removido e `splitlines()` de volta):

      ```
      sed 's/"--name-only", "-z",/"--name-only",/; s/return split_nul_paths(out)/return [l for l in out.splitlines() if l]/' [...] | python3 - --selftest
      -> HELPER FAIL  changed_paths() survives core.quotePath on a real repository
      -> 7/7 defect classes detected, 11/11 false-positive cases stayed silent, 10/11 helper cases correct
      ```

- [x] 2.3 `evaluate()` pura: `V1` skill editada sem bump e sem dispensa; `V2` versão que desce;
      `V3` dispensa sem motivo utilizável; skill nova e wrapper-only mudos

      `evaluate(skills, pr_body)` em `:249`, sem I/O; `V2` avaliado antes e independente da dispensa
      (`:251-259`). Saída de um achado, observada:

      ```
      evaluate([SkillDiff('backlog', ('skills/backlog/SKILL.md',), '1.5.0', '1.5.0', True)], '')
      -> V1 unbumped skill — skills/backlog/ changed 1 path(s) — skills/backlog/SKILL.md — with metadata.version 1.5.0 on the base and 1.5.0 on HEAD. Either raise `  version:` in skills/backlog/SKILL.md above 1.5.0, or add one line `Skill-version: none — <reason>` to the pull request body (it covers every skill in this diff)
      evaluate([... '1.8.0', '1.7.0' ...], 'Skill-version: none — typo fix in one sentence')
      -> V2 version moved backwards — skills/backlog/SKILL.md metadata.version went from 1.8.0 (base) to 1.7.0 (HEAD). [...] A `Skill-version: none` line does not cover this
      ```

- [x] 2.4 `--selftest`: editada sem bump → achado; com bump → mudo; com dispensa → mudo; skill nova →
      mudo; wrapper-only → mudo; versão que desce → achado; dispensa sem motivo → achado

      ```
      python3 scripts/validate-skill-version.py --selftest
      -> CAUGHT  V1 unbumped skill: ''
      -> CAUGHT  V1 unbumped skill: 'see the Skill-version: none — reason line elsewhere'
      -> CAUGHT  V2 version moved backwards: 'Skill-version: none — typo fix in one sentence'
      -> CAUGHT  V3 waiver reason: 'Skill-version: none — x'
      -> CAUGHT  V3 waiver reason: 'Skill-version: none'
      -> SILENT  edited with a bump
      -> SILENT  edited with a waiver
      -> SILENT  twelve skills, one waiver
      -> SILENT  new skill
      -> SILENT  version-only edit
      -> SILENT  wrapper-only diff
      -> 7/7 defect classes detected, 11/11 false-positive cases stayed silent, 11/11 helper cases correct
      -> exit=0
      ```

- [x] 2.5 Docstring lista as regras e o KNOWN LIMIT

      ```
      grep -n "^  V[123] \|^KNOWN LIMIT" scripts/validate-skill-version.py
      -> 13:  V1 a skill with changed content has a metadata.version on HEAD that is semver-greater than on the
      -> 16:  V2 a metadata.version never moves backwards — a lower number is an editing error, and no reason
      -> 18:  V3 the waiver names a usable reason (the same minimum length as the spec-rite waiver, imported
      -> 28:KNOWN LIMIT: this proves that the number MOVED, not that it moved by the right amount (a patch bump
      ```

## 3. CI e documentação

- [x] 3.1 `ci.yml`: steps *Skill version gate* e *Skill version self-test* logo depois de *Spec-rite
      self-test*

      ```
      python3 -c "import yaml; d=yaml.safe_load(open('.github/workflows/ci.yml')); n=[s['name'] for s in d['jobs']['validate']['steps']]; i=n.index('Spec-rite self-test (the gate is itself gated)'); print(len(n), n[i:i+4])"
      -> 22 ['Spec-rite self-test (the gate is itself gated)', 'Skill version gate (an edited skill moves its metadata.version, or the body waives it)', 'Skill version self-test (the gate is itself gated)', 'Claude plugin validation (vendor validator, blocking)']
      -> run: python3 scripts/validate-skill-version.py | python3 scripts/validate-skill-version.py --selftest
      ```
- [x] 3.2 `README.md`: as duas frases da regra dizem que o bump é medido pelo gate e nomeiam a linha
      `Skill-version: none — <motivo>`

      ```
      grep -n "validate-skill-version" README.md
      -> 194:Each skill also carries its own `metadata.version` [...] The bump is measured, not trusted: [`scripts/validate-skill-version.py`](scripts/validate-skill-version.py) diffs every pull request against its base [...] `Skill-version: none — <reason>` covering the whole diff. [...]
      -> 864:- Bump `metadata.version` whenever the skill changes. CI measures it (`scripts/validate-skill-version.py`): [...] unless its body carries `Skill-version: none — <reason>`.
      ```

- [x] 3.3 `skills/execute-backlog/references/spec-rite.md`, *In the PR body*: parágrafo com a linha
      `Skill-version`; `metadata.version` de `execute-backlog` 1.8.0 → 1.8.1; `bash generate.sh`

      ```
      grep -n "Skill-version" skills/execute-backlog/references/spec-rite.md
      -> 92:skill without moving its version: `Skill-version: none — <the reason these edits deserve no bump>`.
      grep -n "^  version:" skills/execute-backlog/SKILL.md claude/skills/execute-backlog/SKILL.md plugins/workflow/skills/execute-backlog/SKILL.md
      -> skills/execute-backlog/SKILL.md:17:  version: 1.8.1
      -> claude/skills/execute-backlog/SKILL.md:17:  version: 1.8.1
      -> plugins/workflow/skills/execute-backlog/SKILL.md:17:  version: 1.8.1
      bash generate.sh -> Generated 10 category plugins in plugins/ (descriptions derived from the tree)
      git status --porcelain (depois do commit 1f9b27b) -> (vazio)
      ```

## 4. Simulation & Field Proof (MANDATORY)

<!-- Shape gated by scripts/validate-rite-evidence.py once ticked:
       S.1  an `entry point` -> a fragment of the OBSERVED output
       S.2  the case matrix as counts (n/n)
       S.3  names what escaped or misbehaved, or states explicitly that nothing did -->

- [x] S.1 O gate exercitado pelo caminho real: `evaluate()` contra o histórico (`cf767ee` tem de
      produzir achados; o branch do PR #122 tem de ficar mudo) e o script pelo entry point com
      `GITHUB_EVENT_PATH` fabricado, com e sem a dispensa

      **Histórico real** — `collect(root, base, head)` + `evaluate()` importados de
      `scripts/validate-skill-version.py` (`f787d65`, 2026-09-05), apontados para os dois commits:

      ```
      collect(W, 'cf767ee^', 'cf767ee'); evaluate(skills, '')
      -> 13 skill(s), 13 with content, 12 finding(s)
      -> code-locale: None -> 1.0.0 content=True paths=5          (skill nova: sem achado)
      -> FINDING V1 unbumped skill: skills/backlog/ changed 2 path(s) — skills/backlog/SKILL.md, skills/backlog/references/issue-template.md — with metadata.version 1.3.0 on the base and 1.3.0 on HEAD. [...]
      -> FINDING V1 unbumped skill: skills/execute-backlog/ changed 3 path(s) [...] 1.5.0 on the base and 1.5.0 on HEAD. [...]
      -> [...] 12 achados V1, um por skill existente
      collect(W, 'cf767ee^', 'cf767ee'); evaluate(skills, 'Closes #76\n\nSkill-version: none — cross-reference line to code-locale in nine skills; the rest is the new skill\n')
      -> 13 skill(s), 13 with content, 0 finding(s)
      collect(W, 'd2918ed', 'e13c16a'); evaluate(skills, '')          (PR #122)
      -> 6 skill(s), 6 with content, 0 finding(s)
      -> execute-backlog: 1.7.0 -> 1.8.0 content=True paths=1  [...]
      collect(W, 'origin/master', 'HEAD'); evaluate(skills, '')        (este branch)
      -> 1 skill(s), 1 with content, 0 finding(s)
      -> execute-backlog: 1.8.0 -> 1.8.1 content=True paths=2
      ```

      **Entry point real** — `python3 scripts/validate-skill-version.py` como subprocesso a partir da
      raiz, com `GITHUB_ACTIONS=true GITHUB_EVENT_NAME=pull_request GITHUB_BASE_REF=master` e o corpo
      só no arquivo apontado por `GITHUB_EVENT_PATH` (`{"pull_request":{"body":...}}`), num clone
      descartável do worktree (`git clone <worktree> scratch/e2e-clone`, branch `probe` a partir de
      `f787d65`); o worktree ficou limpo (`git status --porcelain` -> vazio antes e depois):

      ```
      branch como commitado, corpo "Closes #119\n\nSpec-rite: add-skill-version-gate\n"
      -> skill-version gate: 0 findings (base origin/master, 1 skill(s) changed, 1 with content changes)   exit=0
      + linha no fim de skills/backlog/SKILL.md, commit, mesmo corpo (sem Skill-version)
      -> ::error::V1 unbumped skill — skills/backlog/ changed 1 path(s) — skills/backlog/SKILL.md — with metadata.version 1.5.0 on the base and 1.5.0 on HEAD. [...]
      -> skill-version gate: 1 findings (base origin/master, 2 skill(s) changed, 2 with content changes)   exit=1
      mesmo diff, corpo com "Skill-version: none — probe: one trailing line added, no rule changed"
      -> skill-version gate: 0 findings (base origin/master, 2 skill(s) changed, 2 with content changes)   exit=0
      mesmo diff, corpo "Skill-version: none\n"
      -> ::error::V3 waiver reason — the pull request body carries `Skill-version: none` with no reason — [...]   exit=1
      mesmo diff, sem GITHUB_EVENT_PATH (corpo degrada para vazio)
      -> ::error::V1 unbumped skill — [...]   exit=1
      mesmo diff, GITHUB_EVENT_NAME=push
      -> skill-version gate: skipped (event push, not pull_request)   exit=0
      mesmo diff + `  version: 1.5.0` -> `1.5.1`, corpo vazio
      -> skill-version gate: 0 findings (base origin/master, 2 skill(s) changed, 2 with content changes)   exit=0
      mesmo diff + `  version:` -> `1.4.0` (abaixo da base 1.5.0), corpo "Skill-version: none — probe: pretend this is fine"
      -> ::error::V2 version moved backwards — skills/backlog/SKILL.md metadata.version went from 1.5.0 (base) to 1.4.0 (HEAD). A version never goes down; restore it above 1.5.0. A `Skill-version: none` line d[...]   exit=1
      branch limpo + linha só em claude/skills/backlog/SKILL.md, corpo vazio
      -> skill-version gate: 0 findings (base origin/master, 1 skill(s) changed, 1 with content changes)   exit=0
      branch limpo + skills/zz-probe/SKILL.md novo, corpo vazio
      -> skill-version gate: 0 findings (base origin/master, 2 skill(s) changed, 2 with content changes)   exit=0
      ```

      **Fixture da revisão — caminho que o git quota.** Clone descartável do worktree, commit de
      `skills/backlog/references/café.md` (conteúdo `x`) sem bump, `core.quotePath` não definido
      (`git config --get core.quotePath` -> vazio; padrão `true`), `SKILL_VERSION_BASE=<commit anterior>`:

      ```
      git diff --name-only BASE...HEAD
      -> "skills/backlog/references/caf\303\251.md"
      python3 scripts/validate-skill-version.py            (script em 3c91f54, antes da correção)
      -> skill-version gate: 0 findings (base 3c91f54[...], 0 skill(s) changed, 0 with content changes)   exit=0
      python3 scripts/validate-skill-version.py            (script corrigido, --name-only -z)
      -> ::error::V1 unbumped skill — skills/backlog/ changed 1 path(s) — skills/backlog/references/café.md — with metadata.version 1.5.0 on the base and 1.5.0 on HEAD. [...]
      -> skill-version gate: 1 findings (base 3c91f54[...], 1 skill(s) changed, 1 with content changes)   exit=1
      mesmo diff, PR_BODY="Skill-version: none — probe: quoted-path fixture"
      -> skill-version gate: 0 findings (base 3c91f54[...], 1 skill(s) changed, 1 with content changes)   exit=0
      mesmo diff, git config core.quotePath false (caixa que não quota)
      -> skill-version gate: 1 findings (base 3c91f54[...], 1 skill(s) changed, 1 with content changes)
      git ls-files skills | grep -cP '[^\x00-\x7F]'   -> 0   (nenhum caminho assim no catálogo hoje)
      ```

      No próprio worktree, sem ambiente de CI:

      ```
      python3 scripts/validate-skill-version.py
      -> skill-version gate: 0 findings (base origin/master, 1 skill(s) changed, 1 with content changes)   exit=0
      GITHUB_ACTIONS=true GITHUB_EVENT_NAME=push python3 scripts/validate-skill-version.py
      -> skill-version gate: skipped (event push, not pull_request)   exit=0
      python3 scripts/validate-skill-version.py --selftest
      -> 7/7 defect classes detected, 11/11 false-positive cases stayed silent, 11/11 helper cases correct   exit=0
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Tinha de disparar e disparou | 7/7 | histórico `cf767ee` sem dispensa (12 achados V1, contado como 1); entry point: edição sem bump sem dispensa (1), dispensa sem motivo (1), sem payload (1), versão abaixo da base com dispensa (1); fixture da revisão: caminho quotado sem bump, `quotePath` padrão (1) e `false` (1) |
      | Tinha de ficar mudo e ficou | 9/9 | histórico: `cf767ee` com dispensa PR-wide (1), PR #122 com 6 bumps (1), este branch (1); entry point: branch commitado (1), bump patch (1), dispensa com motivo (1), wrapper-only (1), skill nova (1); fixture da revisão com dispensa (1) |
      | Skip declarado | 2/2 | `GITHUB_EVENT_NAME=push` no clone e no worktree — `skipped (event push, not pull_request)` |
      | Selftest | 3/3 | 7/7 defeitos, 11/11 mudos, 11/11 helpers |
      | Mutação detectada | 1/1 | `-z` removido → `HELPER FAIL changed_paths() survives core.quotePath [...]`, 10/11, exit 1 |
      | Escape conhecido ficou mudo | 1/1 | caminho quotado com o script de `3c91f54`: `0 skill(s) changed`, exit 0 — o escape que a revisão apontou, fechado nesta rodada (S.3) |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      - **Importação do gate quebrou na primeira tentativa**: carregar `validate-skill-version.py` com
        `importlib.util.spec_from_file_location` sem registrar em `sys.modules` falha em Python 3.14.5
        na criação do `@dataclass SkillDiff` (`dataclasses.py:814`, `AttributeError: 'NoneType' object
        has no attribute '__dict__'`). O script passou a registrar o módulo irmão antes do
        `exec_module`, e o comentário em `_sibling_min_reason()` avisa quem importar este arquivo do
        mesmo jeito. Não afeta o caminho do CI (o script roda como programa).
      - **A primeira versão do probe de "versão que desce" não desceu**: baixou `1.5.1 → 1.5.0`, que é
        igual à base, e o gate ficou (corretamente) mudo com a dispensa presente. Corrigido para
        `1.4.0`; o `V2` disparou. Defeito do probe, não do gate — registrado porque um caso de
        simulação mal construído passa em silêncio.
      - O PR #122 tocou **6** skills, não 5 como a issue estimou; todas bumpadas, resultado mudo.
      - `README.md` cita `:180`/`:824` na issue; hoje as frases estão em `:194`/`:864`. Editadas as
        duas, nenhuma outra.
      - `V0 base revision` (CI sem `fetch-depth: 0`) não exercitado (E.3).
      - **Escape apontado na revisão do PR, reproduzido e fechado**: com o script de `3c91f54`, um
        caminho que o git quota (`skills/backlog/references/café.md`, `core.quotePath` padrão) saía de
        `git diff --name-only` como `"skills/backlog/references/caf\303\251.md"`, `skills_in()` o
        descartava e o gate aprovava com `0 skill(s) changed` — falha aberta, o oposto do irmão. A
        simulação original não construiu esse caso porque nenhum caminho do catálogo tem byte não-ASCII
        (`git ls-files skills | grep -cP '[^\x00-\x7F]'` -> 0; `code-locale` proíbe) — buraco na
        medição, não regressão presente. Corrigido com `--name-only -z` + `split_nul_paths()`, três
        helpers novos no selftest (um deles comita o caminho num repositório temporário), mutação
        confirmada. Registrado no docstring do script e em D1.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: name == directory, description dobrada,
      author solvelab, version semver, category no conjunto, license MIT, compatibility presente

      Única skill tocada: `execute-backlog` (só a linha `  version:` no `SKILL.md`).

      ```
      awk '<frontmatter() de generate.sh>' skills/execute-backlog/SKILL.md | grep -E '^name:|^  version:|^  author:|^  category:|^license:|^compatibility:|^description: >-'
      -> name: execute-backlog / description: >- / author: solvelab / version: 1.8.1 / category: process / license: MIT / compatibility: >-
      gates.sh -> PASS frontmatter   (o shell do step, sobre as 35 skills)
      ```

- [x] Q.2 Conteúdo de skill tocado em inglês — o parágrafo novo em `references/spec-rite.md:90-97`
      está em inglês; `validate-skills.py` -> `skills checked: 35   findings: 0`
- [x] Q.3 Gatilhos de descrição testáveis — não se aplica: nenhuma `description` muda
- [x] Q.4 Sem doutrina duplicada: tabela Canonical Home em `design.md` (seis linhas); o README nomeia o
      gate e a linha sem restatar o protocolo, que mora em `execute-backlog/references/spec-rite.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — nomes de função (`collect`, `moved_up`,
      `skills_in`), `SkillDiff`, labels de selftest, nome dos steps (`code-locale`)

      ```
      git diff origin/master...HEAD -- .github scripts | python3 skills/code-locale/references/check-identifier-locale.py --diff -
      -> findings: 0   exit=0
      ```

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-skill-version-gate --strict` verde

      ```
      openspec validate add-skill-version-gate --strict -> Change 'add-skill-version-gate' is valid   (openspec 1.6.0)
      bash scripts/validate-rite.sh -> rite evidence gate: 0 findings [...] rite gate OK
      ```

- [x] V.2 Descoberta do catálogo intacta: 35 skills, sem órfão

      ```
      ls skills | wc -l                       -> 35
      python3 scripts/validate-skills.py      -> skills checked: 35   findings: 0   (C7: nenhum wrapper órfão)
      python3 scripts/validate-repo-hygiene.py -> repo hygiene: 0 findings   (H2: contagens publicadas == 35)
      ```

- [x] V.3 README / docs atualizados onde a change altera o uso — `README.md:194` e `:864` (3.2),
      `skills/execute-backlog/references/spec-rite.md` (3.3); o parágrafo *3. Release* do README fica
      como follow-up (E.4)
- [x] V.4 `openspec archive add-skill-version-gate --yes` depois de todos os grupos acima `[x]`


      ```
      openspec archive add-skill-version-gate --yes
      -> Specs updated successfully.
      -> Change 'add-skill-version-gate' archived as '2026-09-05-add-skill-version-gate'.
      ```