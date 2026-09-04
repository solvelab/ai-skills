## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `d2918ed` (topo de `master`, 2026-09-04), no worktree do branch
      `backlog/112-agent-skills-limits`:

      - `scripts/validate-skills.py` — 9 checks C1–C9; C4 mede a description sobre o bloco cru
        (`fm = text.split("---", 2)`, `re.search(r"^description:..."` em `:223`); `META_HEADING`
        em `:277` casa só `How to Use|Trigger Test Cases|Prompt|Usage`; a lista `skipped` no
        `main()` já reporta `yaml parse (PyYAML not installed)`.
      - `scripts/selftest-validate-skills.py` — dict `MUTATIONS` com 13 entradas, uma por check;
        `caught = check.split()[0] in out and check in out`.
      - `.github/workflows/ci.yml` — `pip install --quiet pyyaml` em `:83`, `|| true` do `apt-get`
        em `:84` (intocado), step `Skill validator self-test` em `:87-88`, comentário-modelo do pin
        em `:120-128`.
      - `skills/api-resilience-testing/SKILL.md:43-49` — seção `## When to use this skill` que
        repete a description.
      - `skills/{code-locale,execute-backlog,backlog,verify-before-claiming,assettoserver-csp-lua}/SKILL.md`
        — frontmatter e primeiro parágrafo do corpo de cada uma.
      - `openspec/specs/skills-authoring/spec.md` — requisitos *Uniform frontmatter metadata*
        (`:48`), *Authoring rules are machine-enforced* (`:259`), *Triggers live in the
        description, not the body* (`:320`), copiados integralmente para o delta.
      - `openspec/specs/skills-catalog/spec.md:480-500` — cenário *The uncovered part is declared,
        not implied* e o requisito *The repository itself is gated*.
      - `README.md:25` e `:381` — os dois links "Agent Skills" para `vercel-labs/skills`.
      - `generate.sh` — o wrapper de `claude/skills/<n>/SKILL.md` copia o frontmatter inteiro, logo
        a description encurtada propaga por `./generate.sh`.
      - `openspec/changes/archive/2026-08-30-fix-release-race/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md` — modelo de estilo desta change.

- [x] E.2 Ferramentas, versões e comportamentos probados contra a versão instalada

      ```
      python3 -m venv <scratch>/venv-A && <venv>/bin/pip install skills-ref==0.1.1
      <venv>/bin/agentskills --version
      -> agentskills, version 0.1.1
      cat <venv>/.../skills_ref-0.1.1.dist-info/entry_points.txt
      -> [console_scripts]
      -> agentskills = skills_ref.cli:main
      ```

      ```
      sed -n '10,22p' <venv>/lib/python3.14/site-packages/skills_ref/validator.py
      -> MAX_SKILL_NAME_LENGTH = 64
      -> MAX_DESCRIPTION_LENGTH = 1024
      -> MAX_COMPATIBILITY_LENGTH = 500
      -> ALLOWED_FIELDS = { "name", "description", "license", "allowed-tools", "metadata", "compatibility", }
      grep -n "len(description)\|len(compatibility)" validator.py
      -> if len(description) > MAX_DESCRIPTION_LENGTH:
      -> if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
      ```

      ```
      curl -sL https://agentskills.io/specification | (strip html) | grep -E '1024|500 characters'
      -> description   Yes  Max 1024 characters
      -> compatibility   No  Max 500 characters
      -> Must be 1-1024 characters
      -> Must be 1-500 characters if provided
      ```

      ```
      bash <scratch>/run-agentskills.sh      # agentskills validate skills/<d>, um dir por chamada
      -> skills/assettoserver-csp-lua   rc=1 :: Description exceeds 1024 character limit (1076 chars)
      -> skills/backlog                 rc=1 :: Description exceeds 1024 character limit (1265 chars)
      -> skills/code-locale             rc=1 :: Description exceeds 1024 character limit (1398 chars)   - Compatibility exceeds 500 character limit (728 chars)
      -> skills/execute-backlog         rc=1 :: Description exceeds 1024 character limit (1344 chars)
      -> skills/verify-before-claiming  rc=1 :: Description exceeds 1024 character limit (1222 chars)
      -> ok=30 bad=5 total=35
      ```

      ```
      python3 -c 'yaml.safe_load(frontmatter); len(description)' sobre as 35   (valor parseado)
      -> code-locale desc=1398 compat=728 · execute-backlog 1344 · backlog 1265
      -> verify-before-claiming 1222 · assettoserver-csp-lua 1076 · svg-animation 998
      ```

      ```
      python3 scripts/validate-skills.py          (baseline, antes desta change)
      -> skills checked: 35   findings: 0
      python3 scripts/selftest-validate-skills.py
      -> 13/13 defect classes detected
      ```

      ```
      <venv>/bin/python -m skills_ref validate skills/r3f-geometry
      -> No module named skills_ref.__main__; 'skills_ref' is a package and cannot be directly executed
      <venv>/bin/python -m skills_ref.cli validate skills/r3f-geometry
      -> Valid skill: skills/r3f-geometry
      ```

      ```
      openspec --version -> 1.6.0        claude --version -> 2.1.260 (Claude Code)
      which luac -> /home/linuxbrew/.linuxbrew/bin/luac        python3 -c 'import yaml' -> 6.0.3
      ```

- [x] E.3 O que não pôde ser probado

      Uma lacuna: se o binário `agentskills` fica no `PATH` do runner `ubuntu-latest` depois de
      `python3 -m pip install`. Não há como executar o runner daqui; o primeiro run do CI deste
      branch é a prova. O fallback, se falhar, é `python3 -m skills_ref.cli validate` (probado
      acima). O comportamento de `claude plugin validate` com description de 2000 caracteres não foi
      re-medido aqui — é a medição da issue #112 (2.1.246 no CI, 2.1.260 local) e a change não
      depende dela.

- [x] E.4 Checagem de escopo

      A change faz só o que a issue #112 pediu. Notados pelo caminho e **não** feitos, como
      follow-up:

      - `svg-animation` está em 998 caracteres parseados (26 do teto); não é editada porque só as
        5 fora do teto mudam (fora de escopo da issue).
      - As 35 descriptions somam ~23k caracteres; reduzir o orçamento total fica fora de escopo.
      - `selftest-validate-skills.py` copia o repositório inteiro 15 vezes (uma por mutação); é
        lento mas não é assunto desta change.
      - `python -m skills_ref` não existe no pacote (só `skills_ref.cli`); um `__main__.py` seria
        contribuição upstream, não daqui.

## 2. Gate: C10, C8 alargado, selftest e validador de referência no CI

- [x] 2.1 `scripts/validate-skills.py`: check `C10 frontmatter limits` mede `len()` do valor
      parseado de `description` (≤ `MAX_DESCRIPTION_CHARS` = 1024) e `compatibility`
      (≤ `MAX_COMPATIBILITY_CHARS` = 500), nomeia skill, check e tamanhos, declara dentro de si o
      que não cobre, e entra em `checks skipped` sem PyYAML (D1)

      ```
      grep -n "MAX_DESCRIPTION_CHARS\|MAX_COMPATIBILITY_CHARS\|KNOWN LIMIT" scripts/validate-skills.py
      -> 298:MAX_DESCRIPTION_CHARS = 1024
      -> 299:MAX_COMPATIBILITY_CHARS = 500
      -> 318:    KNOWN LIMIT — what this check does NOT cover:
      ```

      Cópia do catálogo com a description de `r3f-geometry` inflada (valor parseado 1466):

      ```
      python3 scripts/validate-skills.py            (na cópia inflada)
      -> skills checked: 35   findings: 1
      ->   C10 frontmatter limits 1
      -> r3f-geometry
      ->    [C10 frontmatter limits] description is 1466 chars, limit 1024 (parsed value; 442 over)
      -> rc=1
      agentskills validate skills/r3f-geometry      (mesma cópia — os dois medem o mesmo número)
      -> Validation failed for skills/r3f-geometry:
      ->   - Description exceeds 1024 character limit (1466 chars)
      ```

      Sem PyYAML (import de `yaml` bloqueado com `sys.modules['yaml'] = None`):

      ```
      -> skills checked: 35   findings: 0
      ->   checks skipped: yaml parse (PyYAML not installed); frontmatter limits (PyYAML not installed)
      -> rc= 0
      ```

      A medida bruto-vs-parseado que justifica D1, re-medida com o `re.search` do C4 e o
      `yaml.safe_load` do C10 sobre as 35 skills:

      ```
      python3 <scratch>/measure-raw.py             (catálogo deste branch)
      -> svg-animation   raw= 1024 raw_strip= 1023 parsed=  998 delta= 26
      -> n=35 delta(raw C4 group1 - parsed): min=6 max=26
      python3 <scratch>/measure-raw.py d2918ed     (catálogo em master, antes do encurtamento)
      -> n=35 delta(raw C4 group1 - parsed): min=6 max=36
      ```

      A docstring, o `design.md`, a `proposal.md` e o delta diziam 26–36; corrigidos para 6–26
      no commit `abdc815`.

- [x] 2.2 `META_HEADING` passa a casar `When to use this skill` (D5)

      ```
      python3 -c 'META_HEADING.search(h + "\n")' para cada título
      -> '## When to use this skill' -> True
      -> '## When To Use This Skill' -> True
      -> '## How to Use' -> True
      -> '## When to use' -> False
      ```

- [x] 2.3 `scripts/selftest-validate-skills.py`: mutação C10 (description inflada acima de 1024
      parseados) e mutação C8 com o título alargado; 15/15

      ```
      python3 scripts/selftest-validate-skills.py
      -> [...]
      ->   CAUGHT  C8 meta section
      ->   CAUGHT  C8 meta section (when-to-use heading)
      ->   CAUGHT  C9 identifier locale
      ->   CAUGHT  C10 frontmatter limits
      -> 15/15 defect classes detected
      -> rc=0
      ```

- [x] 2.4 `.github/workflows/ci.yml`: `skills-ref==0.1.1` na linha de `pip` de `:83`; step novo
      logo após `Skill validator self-test` rodando `agentskills validate` por diretório, com o
      comentário do pin e do que não cobre (D3)

      ```
      git diff d2918ed -- .github/workflows/ci.yml
      -> -          python3 -m pip install --quiet pyyaml
      -> +          python3 -m pip install --quiet pyyaml skills-ref==0.1.1
      -> +      - name: Agent Skills reference validator (skills-ref, pinned, blocking)
      -> +        # The version is pinned on purpose: skills_ref/validator.py:15-22 whitelists the frontmatter
      -> +        # WHAT THIS COVERS AND WHAT IT DOES NOT: name (length, charset, == directory), description
      -> +          for d in skills/*/; do
      -> +            agentskills validate "$d" || fail=1
      ```

      O laço do step, rodado literalmente com o `agentskills` do venv no `PATH`:

      ```
      fail=0; for d in skills/*/; do agentskills validate "$d" || fail=1; done; echo "exit fail=$fail"
      -> Valid skill: skills/api-resilience-testing
      -> [...]
      -> Valid skill: skills/verify-before-claiming
      -> exit fail=0
      ```

- [x] 2.5 Gate primeiro: com C10 no lugar e as descriptions ainda intocadas, o validador reprova
      exatamente as 5 skills (D6) — saída registrada em S.1

      Árvore do commit `2ac99fe` (o commit do gate, anterior ao encurtamento) extraída com
      `git archive` e validada:

      ```
      python3 scripts/validate-skills.py            (árvore de 2ac99fe)
      -> skills checked: 35   findings: 7
      ->   C10 frontmatter limits 6
      ->   C8 meta section        1
      -> api-resilience-testing   [C8 meta section] `## When to use this skill` — move its content to the description
      -> assettoserver-csp-lua    [C10 frontmatter limits] description is 1076 chars, limit 1024 (parsed value; 52 over)
      -> backlog                  [C10 frontmatter limits] description is 1265 chars, limit 1024 (parsed value; 241 over)
      -> code-locale              [C10 frontmatter limits] compatibility is 728 chars, limit 500 (parsed value; 228 over)
      -> code-locale              [C10 frontmatter limits] description is 1398 chars, limit 1024 (parsed value; 374 over)
      -> execute-backlog          [C10 frontmatter limits] description is 1344 chars, limit 1024 (parsed value; 320 over)
      -> verify-before-claiming   [C10 frontmatter limits] description is 1222 chars, limit 1024 (parsed value; 198 over)
      -> rc=1
      ```

      Os 6 achados de C10 caem nas 5 skills da issue (duas linhas para `code-locale`); o sétimo
      é o C8 alargado pegando a seção que 3.3 remove.

## 3. Descriptions dentro do teto sem perder gatilho

- [x] 3.1 As 5 descriptions ≤ 1024 e a `compatibility` de `code-locale` ≤ 500, medidas no valor
      parseado; o que saiu foi para o primeiro parágrafo do corpo (D4)

      ```
      yaml.safe_load(frontmatter) sobre master (d2918ed) e HEAD
      -> code-locale             desc 1398->996  compat 728->487
      -> execute-backlog         desc 1344->994  compat 234->234
      -> backlog                 desc 1265->1000 compat 182->182
      -> verify-before-claiming  desc 1222->1012 compat 229->229
      -> assettoserver-csp-lua   desc 1076->1003 compat  76->76
      ```

      Onde o que saiu aterrissou, no corpo de cada skill em HEAD:

      ```
      grep -n "grooming glossary\|path of every file" skills/code-locale/SKILL.md
      -> 33:gate, the grooming glossary, the new-code-only migration policy, and a shipped detector a
      -> 44:- **The detector** — measures the path of every file it is given and the contents of the types
      grep -n "\.github/backlog.yml" skills/execute-backlog/SKILL.md
      -> 29:to the `backlog` skill; consumes the same config (`.github/backlog.yml` in repo mode,
      grep -n "config wizard" skills/backlog/SKILL.md
      -> 29:codebase. The first run per repo/workspace launches a config wizard that writes
      grep -n "research ladder\|inferred" skills/verify-before-claiming/SKILL.md
      -> 33:**inferred** and labelled as such, or **unknown** and reported. There is no fourth option. A
      -> 65:## The research ladder
      grep -n "production DriveZone" skills/assettoserver-csp-lua/SKILL.md
      -> 27:and code all arrive over the server's HTTP port. Distilled from a production DriveZone server:
      ```

- [x] 3.2 Tabela antes/depois das frases entre aspas, por skill — nenhuma perdida:

      Extraída por script (`re.findall(r'"([^"]+)"', description)`) sobre o valor parseado em
      `d2918ed` (antes) e em HEAD (depois); `LOST` é o conjunto antes − depois:

      ```
      python3 <scratch>/quotes.py
      -> == code-locale: desc 1398->996 chars; compat 728->487
      ->    quoted before (10) [...]  quoted after (10) [...]  LOST: []  NEW: []
      -> == execute-backlog: desc 1344->994 chars
      ->    quoted before (3)  quoted after (3)   LOST: []  NEW: []
      -> == backlog: desc 1265->1000 chars
      ->    quoted before (4)  quoted after (4)   LOST: []  NEW: []
      -> == verify-before-claiming: desc 1222->1012 chars
      ->    quoted before (12) quoted after (12)  LOST: []  NEW: []
      -> == assettoserver-csp-lua: desc 1076->1003 chars
      ->    quoted before (0)  quoted after (0)   LOST: []  NEW: []
      ->    LOST parens: ['different Lua contexts with different permissions']
      ```

      | Skill | Frases entre aspas antes | Depois | Perdidas |
      |---|---|---|---|
      | `code-locale` | "código em português", "nome de variável em inglês", "rota em português", "traduz esse nome", "identificador em inglês", "should this be in English", "our code is half Portuguese", "naming convention", "ubiquitous language", "anti-corruption layer" (10) | as mesmas 10 | nenhuma |
      | `execute-backlog` | "implement issue #N", "execute this backlog item", "pick up this ticket" (3) | as mesmas 3 | nenhuma |
      | `backlog` | "create a backlog item", "add this to the backlog", "turn this idea into an issue", "groom this idea" (4) | as mesmas 4 | nenhuma |
      | `verify-before-claiming` | "you invented that", "don't guess", "achismo", "não inventa", "chutou", "pesquisa antes", "de onde tirou", "where did you see that", "cite the source", "that flag does not exist", "out of scope", "não foi isso que eu pedi" (12) | as mesmas 12 | nenhuma |
      | `assettoserver-csp-lua` | nenhuma frase entre aspas; gatilhos parentéticos (overlay, HUD, toast, in-game sound, login UI) e (empty flat box, glued or overlapping text, missing glyphs, sound plays only once) | os mesmos dois parênteses, byte a byte | nenhuma — o único parêntese que mudou é a explicação do "Do NOT use" ("with different permissions" → "and permissions"), não um gatilho |

      O que saiu de cada description e para onde foi:

      | Skill | Saiu | Foi para |
      |---|---|---|
      | `code-locale` | "Covers the prose/machine boundary, the untranslatable-domain-term exception and its gate, the grooming glossary, the new-code-only migration policy, and a shipped detector…"; enumeração longa de tipos de identificador (module, REST route segment, topic name) | primeiro parágrafo do corpo (`:33`); a enumeração completa já está na tabela *The two layers* |
      | `code-locale` (compat) | "measures the path of every file it is given"; "needs a harness that emits a post-write tool event" | bullet *The detector* no corpo (`:44`) |
      | `execute-backlog` | "following the repo's conventions", "(tests/lint/build/typecheck)", "Uses the backlog skill's config (.github/backlog.yml or workspace backlog.yml)" | primeiro parágrafo do corpo (`:29`; já dizia "consumes the same config", ganha os nomes dos arquivos) |
      | `backlog` | "so execute-backlog inherits a decision instead of making a new one"; "First run per repo/workspace launches a config wizard that writes .github/backlog.yml (repo mode) or backlog.yml (workspace mode)" | primeiro parágrafo do corpo (`:29`); a seção `## Setup wizard` já existe |
      | `verify-before-claiming` | os sete degraus da escada entre parênteses; "verified/inferred/unknown claim labelling" | primeiro parágrafo do corpo (a escada, degrau a degrau) e `## The research ladder` (`:65`); os três rótulos já estavam em `:33` |
      | `assettoserver-csp-lua` | "Distilled from a production DriveZone server."; "from the server" | primeiro parágrafo do corpo (`:27`) |

- [x] 3.3 `## When to use this skill` removida de `skills/api-resilience-testing/SKILL.md` (conteúdo
      já na description; nada dobrado)

      ```
      git diff d2918ed HEAD -- skills/api-resilience-testing/SKILL.md | grep '^-'
      -> -## When to use this skill
      -> -Trigger whenever the work involves a REST/HTTP API: adding or changing an
      -> [...]
      grep -n "When to use" skills/api-resilience-testing/SKILL.md claude/skills/api-resilience-testing/SKILL.md
      -> (nenhuma linha) grep rc=1
      ```

- [x] 3.4 `metadata.version` minor nas 6 skills editadas: `code-locale` 1.2.0→1.3.0,
      `execute-backlog` 1.7.0→1.8.0, `backlog` 1.4.0→1.5.0, `verify-before-claiming` 1.0.0→1.1.0,
      `assettoserver-csp-lua` 1.0.1→1.1.0, `api-resilience-testing` 1.2.1→1.3.0

      ```
      grep -m1 '^  version:' em master (d2918ed) e HEAD, por skill
      -> code-locale              master=1.2.0 HEAD=1.3.0
      -> execute-backlog          master=1.7.0 HEAD=1.8.0
      -> backlog                  master=1.4.0 HEAD=1.5.0
      -> verify-before-claiming   master=1.0.0 HEAD=1.1.0
      -> assettoserver-csp-lua    master=1.0.1 HEAD=1.1.0
      -> api-resilience-testing   master=1.2.1 HEAD=1.3.0
      ```

## 4. README e wrappers

- [x] 4.1 `README.md:25` e `:381`: "Agent Skills" aponta para `https://agentskills.io/specification`;
      `vercel-labs/skills` fica citado só como o CLI `npx skills` da Opção A

      ```
      sed -n 25p README.md
      -> Skills follow the open [Agent Skills](https://agentskills.io/specification) standard (`skills/<name>/SKILL.md`), so every mainstream install path works — including the [`npx skills`](https://github.com/vercel-labs/skills) CLI of Option A.
      sed -n 381p README.md
      -> The canonical skill lives in `skills/<name>/SKILL.md` — a **self-contained** file following the open [Agent Skills](https://agentskills.io/specification) standard [...]
      grep -n "vercel-labs/skills" README.md
      -> 25:[...] (única ocorrência)
      ```

- [x] 4.2 `./generate.sh` rodado; `git diff --exit-code` limpo depois

      ```
      bash generate.sh
      -> Generated 10 category plugins in plugins/
      git diff --exit-code --stat
      -> diff rc=0
      git status --porcelain | wc -l
      -> 0
      ```

## 5. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo caminho real; comando e fragmento da saída observada

      **Validador de referência sobre as 35 skills** (`skills-ref==0.1.1` em venv, binário
      `agentskills`, uma chamada por diretório — o mesmo laço do step do CI):

      ```
      bash <scratch>/run-agentskills.sh
      -> skills/api-resilience-testing  rc=0 :: Valid skill: skills/api-resilience-testing
      -> skills/assettoserver-csp-lua   rc=0 :: Valid skill: skills/assettoserver-csp-lua
      -> skills/backlog                 rc=0 :: Valid skill: skills/backlog
      -> skills/code-locale             rc=0 :: Valid skill: skills/code-locale
      -> skills/execute-backlog         rc=0 :: Valid skill: skills/execute-backlog
      -> [...]
      -> skills/svg-animation           rc=0 :: Valid skill: skills/svg-animation
      -> skills/verify-before-claiming  rc=0 :: Valid skill: skills/verify-before-claiming
      -> ok=35 bad=0 total=35
      -> rc=0
      ```

      Antes do encurtamento o mesmo laço dava `ok=30 bad=5 total=35` (E.2).

      **C10 pelo caminho real** — dispara na cópia inflada e fica mudo no catálogo:

      ```
      python3 scripts/validate-skills.py            (cópia com r3f-geometry inflada a 1466)
      ->    [C10 frontmatter limits] description is 1466 chars, limit 1024 (parsed value; 442 over)
      -> rc=1
      python3 scripts/validate-skills.py            (catálogo)
      -> skills checked: 35   findings: 0
      -> rc=0
      ```

      **Simulação de roteamento por gatilho** — 3 prompts realistas por skill encurtada, 15 no
      total, pontuados contra as 35 descriptions de `master` (antes) e de HEAD (depois) por um
      roteador léxico (`<scratch>/route-sim.py`: frases entre aspas casadas ×3 + bigramas de
      conteúdo + unigramas/4). O roteador real é o modelo; o que se mede aqui é se o sinal
      lexical que cada description carrega para esses prompts sobreviveu ao corte:

      | Skill | Prompt | Antes → Depois | Vice |
      |---|---|---|---|
      | `code-locale` | "O PR introduz a rota /clientes/{id}/pedidos — rota em português é aceitável aqui ou traduz esse nome?" | code-locale 10.50 → 10.50 | verify-before-claiming 0.00 |
      | `code-locale` | "Should this be in English? The DB column is called data_nascimento and the enum values are PENDENTE/PAGO — our code is half Portuguese." | code-locale 9.75 → 9.50 | execute-backlog 0.75 → 0.50 |
      | `code-locale` | "Vamos criar a tabela de notas fiscais: o campo pode se chamar nota_fiscal_number ou o domain term tem que virar invoice? Qual a naming convention?" | code-locale 6.00 → 6.00 | verify-before-claiming 0.25 |
      | `execute-backlog` | "implement issue #112 end to end and open the PR with Closes" | execute-backlog 2.00 → 2.00 | backlog 0.25 |
      | `execute-backlog` | "pick up this ticket please: https://github.com/solvelab/ai-skills/issues/98" | execute-backlog 4.50 → 4.50 | verify-before-claiming 0.00 |
      | `execute-backlog` | "execute this backlog item, the one about the release race, on a dedicated branch" | execute-backlog 7.25 → 7.25 | verify-before-claiming 1.75 |
      | `backlog` | "add this to the backlog: the validator should also measure tokens, not only characters" | backlog 4.75 → 4.75 | svg-animation 0.50 |
      | `backlog` | "turn this idea into an issue in the GitHub Project: run agentskills validate in CI" | backlog 8.75 → 8.50 | execute-backlog 2.50 |
      | `backlog` | "groom this idea before I forget — a config wizard for backlog.yml in workspace mode" | backlog **8.75 → 4.75** | execute-backlog 1.00 → verify-before-claiming 0.50 |
      | `verify-before-claiming` | "de onde tirou essa flag --strict-sections? acho que ela não existe, não inventa" | verify-before-claiming 9.75 → 9.75 | conventional-commit 0.25 |
      | `verify-before-claiming` | "don't guess: which version of skills-ref does the CI install and where did you see that?" | verify-before-claiming 12.00 → 12.00 | openspec-drivezone 0.25 |
      | `verify-before-claiming` | "não foi isso que eu pedi — eu pedi só o diff, não pra reescrever o script; isso é out of scope" | verify-before-claiming 13.50 → 13.50 | openspec-drivezone 0.25 |
      | `assettoserver-csp-lua` | "my CSP overlay renders as an empty flat box with glued or overlapping text; the lua online script is served by AssettoServer" | assettoserver-csp-lua 13.50 → 13.50 | fivem-nui-react 0.50 |
      | `assettoserver-csp-lua` | "the ac.OnlineEvent packet from my toast script silently never arrives on the client, the C# plugin sends it fine" | assettoserver-csp-lua 2.75 → 2.75 | react-api-client 0.25 |
      | `assettoserver-csp-lua` | "write a HUD lua online script for the login UI with a remote image loaded by URL and DirectWrite text" | assettoserver-csp-lua 6.50 → 6.50 | openspec-drivezone 0.25 |

      ```
      python3 <scratch>/route-sim.py
      -> prompts=15  intended-top before=15/15  after=15/15  same-top before/after=15/15
      ```

      Leitura observada, prompt a prompt: em 12 dos 15 a pontuação é idêntica antes e depois,
      porque o que roteia é a frase entre aspas ou o parêntese de sintomas, e nenhum saiu. Em 2
      cai 0,25 — um unigrama de ruído que a description antiga tinha e a nova não ("are" em
      `code-locale`, "run" em `backlog`, medidos por diferença de conjuntos). Em 1 cai
      4,00: o prompt do wizard casava a frase "config wizard that writes .github/backlog.yml
      (repo mode) or backlog.yml (workspace mode)", que saiu da description e foi para o corpo;
      ainda assim `backlog` ganha por "groom this idea" com 4,75 contra 0,50 do segundo colocado.

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | `agentskills validate` sai 0 em cada skill | 35/35 | `ok=35 bad=0 total=35` (antes do corte: 30/35) |
      | C10 tinha de disparar e disparou | 1/1 | cópia inflada: `description is 1466 chars, limit 1024` |
      | C10 e `agentskills` medem o mesmo número | 1/1 | 1466 nos dois, na mesma cópia |
      | C10 tinha de ficar mudo e ficou | 35/35 | catálogo: `findings: 0` |
      | Selftest detecta cada classe | 15/15 | `15/15 defect classes detected` |
      | Gate primeiro reprova exatamente as 5 | 5/5 | árvore de `2ac99fe`: 6 achados C10 em 5 skills, nenhuma outra |
      | Frases entre aspas preservadas | 29/29 | 10+3+4+12+0, `LOST: []` nas 5 |
      | Roteamento léxico mantém a skill alvo | 15/15 antes, 15/15 depois | `same-top before/after=15/15` |
      | Prompt cuja margem caiu | 1/15 | wizard do `backlog`: 8,75 → 4,75, ainda primeiro |
      | Escape conhecido ficou mudo | 1/1 | description de 998 caracteres com ~1,3k tokens — ver S.3 |

- [x] S.3 O que escapou ou se comportou diferente do esperado

      1. **Um gatilho não citado enfraqueceu.** A frase do wizard (`backlog`) não estava entre
         aspas e saiu da description; um prompt que descreva o wizard sem dizer "groom this idea"
         ou "add this to the backlog" perde 4 pontos de sinal lexical. A skill continua a ganhar
         (4,75 contra 0,50), e a seção `## Setup wizard` do corpo carrega o conteúdo — mas é o
         único ponto onde o corte mudou uma medida.
      2. **Um parêntese mudou de forma.** Em `assettoserver-csp-lua`, "different Lua contexts
         with different permissions" virou "different Lua contexts and permissions". É a
         explicação de uma cláusula "Do NOT use", não um gatilho; o extrator de parênteses o
         lista como `LOST` e a tabela 3.2 o declara.
      3. **O que o gate não vê, declarado no próprio check:** C10 mede caracteres, não tokens. Uma
         description de 998 caracteres (`svg-animation`) passa; se alguém dobrar mais um gatilho
         nela cai fora por 1 e o gate avisa, mas o orçamento de ~100 tokens por skill que a spec
         sugere não é medido por ninguém — fora de escopo da issue.
      4. **Roteador léxico ≠ roteador real.** A simulação mede sobrevivência do sinal, não a
         decisão do modelo; um prompt sem nenhuma frase citada (o de `implement issue #112`)
         roteia por um único bigrama com pontuação 2,00, antes e depois. É o mesmo antes e
         depois, portanto não é regressão desta change, mas é margem fina que já existia.
      5. **`agentskills` no `PATH` do runner** continua sendo a lacuna de E.3: provado localmente
         com o venv no `PATH`, provado no CI só pelo primeiro run deste branch.

## 6. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: name == diretório, description dobrada,
      author solvelab, version semver, category no conjunto, license MIT, compatibility presente

      ```
      laço de frontmatter do ci.yml (mesmos 8 testes), sobre skills/*/SKILL.md
      -> PASS frontmatter
      agentskills validate                          (name charset/comprimento e whitelist de campos)
      -> ok=35 bad=0 total=35
      ```

- [x] Q.2 Todo conteúdo de skill tocado em inglês (locale do catálogo)

      As linhas adicionadas aos corpos das 6 skills (diff `d2918ed..HEAD`, fora do frontmatter)
      estão em inglês; as únicas sequências em português nas descriptions são as frases de
      gatilho entre aspas que já existiam em `master` (tabela 3.2). Detector de locale sobre os
      arquivos de script tocados:

      ```
      python3 skills/code-locale/references/check-identifier-locale.py scripts/validate-skills.py scripts/selftest-validate-skills.py .github/workflows/ci.yml
      -> findings: 0
      python3 scripts/validate-skills.py            (C9 identifier locale sobre os blocos de código das skills)
      -> skills checked: 35   findings: 0
      ```

- [x] Q.3 Gatilhos de descrição testáveis: as frases roteiam para esta skill e não colidem com
      uma irmã; "Do NOT use for" presente onde há sobreposição

      Simulação de S.1: 15/15 roteiam para a skill alvo, o segundo colocado nunca passa de 2,50
      (execute-backlog para um prompt de `backlog`, cuja cláusula "Do NOT use for implementing
      an existing issue (that is execute-backlog)" está preservada). As cláusulas "Do NOT use"
      das 5 descriptions permanecem, com os mesmos nomes de skill irmã:

      ```
      re.search(r"Do NOT use.*", description) sobre o valor parseado em HEAD
      -> code-locale: Do NOT use for commit subjects or PR bodies (that is conventional-commit), for docs prose (that is documentation), for case style or test naming (each stack's skill), or for i18n and user-facing translation.
      -> execute-backlog: Do NOT use for creating backlog items (that is backlog), for merging PRs, for deploying, or for non-GitHub trackers.
      -> backlog: Do NOT use for implementing an existing issue (that is execute-backlog), for creating pull requests, or for non-GitHub trackers (Jira, Linear, Trello).
      -> verify-before-claiming: Do NOT use for adversarially testing code already written (that is bug-hunter), for designing an API test suite (that is api-resilience-testing), for writing documentation pages (that is documentation), or for the plan-approval gate of a backlog item (that is execute-backlog).
      -> assettoserver-csp-lua: Do NOT use for the C# plugin side — packet classes, config, chat commands, publishing (that is assettoserver-plugin), for server configuration/deploy (that is assettoserver-ops), for CSP apps or track scripts (different Lua contexts and permissions), or for FiveM Lua (that is fivem-lua).
      ```

- [x] Q.4 Sem doutrina duplicada: nada reescrito inline; ver a tabela de Canonical Home em
      `design.md`

      `design.md:95` — `## Canonical Home & Cross-Links (MANDATORY)`. O limite de 1024/500 mora
      no delta de `skills-authoring` e é citado (não repetido) pela docstring de C10 e pelo
      comentário do step do CI, ambos apontando para `skills_ref/validator.py`. A seção
      `## When to use this skill` removida em 3.3 era a duplicata que sobrava.

- [x] Q.5 Todo exemplo de código em skill tocada usa identificadores em inglês; identificadores
      novos do script vêm do Glossary da issue #112 (`code-locale`)

      ```
      grep -n "MAX_DESCRIPTION_CHARS\|MAX_COMPATIBILITY_CHARS\|C10 frontmatter limits" scripts/*.py
      -> scripts/validate-skills.py:298:MAX_DESCRIPTION_CHARS = 1024
      -> scripts/validate-skills.py:299:MAX_COMPATIBILITY_CHARS = 500
      -> scripts/validate-skills.py:347:            add(skill, "C10 frontmatter limits",
      -> scripts/selftest-validate-skills.py:48: "C10 frontmatter limits": ("skills/r3f-geometry/SKILL.md",
      ```

      Os três nomes são os da tabela Glossary da issue (`MAX_DESCRIPTION_CHARS`,
      `MAX_COMPATIBILITY_CHARS`, `C10 frontmatter limits`); o quarto (`agentskills validate`) é
      o binário real. Nenhum exemplo de código foi adicionado às skills tocadas.

## 7. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-agent-skills-limits --strict` verde

      ```
      openspec validate add-agent-skills-limits --strict
      -> Change 'add-agent-skills-limits' is valid
      GITHUB_EVENT_PATH=<event com "Spec-rite: add-agent-skills-limits"> bash scripts/validate-rite.sh
      -> rite gate OK
      ```

- [x] V.2 Descoberta do catálogo intacta: 35 skills, nenhum órfão ou renomeado

      ```
      diff <(git ls-tree --name-only d2918ed skills/) <(git ls-tree --name-only HEAD skills/)
      -> (sem diff) same 35 dirs: 35
      ls claude/skills | wc -l ; ls codex/skills | wc -l
      -> 35 ; 35
      python3 scripts/validate-skills.py            (C7 orphan wrapper incluso)
      -> skills checked: 35   findings: 0
      ```

- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo

      A composição não muda; o uso sim — o padrão que o catálogo declara seguir passa a ser
      linkado pela especificação (4.1, `README.md:25` e `:381`). O validador de referência é
      documentado no próprio step do CI e no delta de `skills-authoring`.

- [x] V.4 `openspec archive add-agent-skills-limits --yes` depois que todos os grupos acima
      estiverem `[x]` — PR separado, depois do merge


      ```
      openspec archive add-agent-skills-limits --yes
      -> Specs updated successfully.
      -> Change 'add-agent-skills-limits' archived as '2026-09-04-add-agent-skills-limits'.
      ```