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

- [ ] 2.1 `scripts/validate-skills.py`: check `C10 frontmatter limits` mede `len()` do valor
      parseado de `description` (≤ `MAX_DESCRIPTION_CHARS` = 1024) e `compatibility`
      (≤ `MAX_COMPATIBILITY_CHARS` = 500), nomeia skill, check e tamanhos, declara dentro de si o
      que não cobre, e entra em `checks skipped` sem PyYAML (D1)
- [ ] 2.2 `META_HEADING` passa a casar `When to use this skill` (D5)
- [ ] 2.3 `scripts/selftest-validate-skills.py`: mutação C10 (description inflada acima de 1024
      parseados) e mutação C8 com o título alargado; 15/15
- [ ] 2.4 `.github/workflows/ci.yml`: `skills-ref==0.1.1` na linha de `pip` de `:83`; step novo
      logo após `Skill validator self-test` rodando `agentskills validate` por diretório, com o
      comentário do pin e do que não cobre (D3)
- [ ] 2.5 Gate primeiro: com C10 no lugar e as descriptions ainda intocadas, o validador reprova
      exatamente as 5 skills (D6) — saída registrada em S.1

## 3. Descriptions dentro do teto sem perder gatilho

- [ ] 3.1 As 5 descriptions ≤ 1024 e a `compatibility` de `code-locale` ≤ 500, medidas no valor
      parseado; o que saiu foi para o primeiro parágrafo do corpo (D4)
- [ ] 3.2 Tabela antes/depois das frases entre aspas, por skill — nenhuma perdida:

      | Skill | Frases entre aspas antes | Depois | Perdidas |
      |---|---|---|---|
      | `code-locale` | "código em português", "nome de variável em inglês", "rota em português", "traduz esse nome", "identificador em inglês", "should this be in English", "our code is half Portuguese", "naming convention", "ubiquitous language", "anti-corruption layer" (10) | as mesmas 10 | nenhuma |
      | `execute-backlog` | "implement issue #N", "execute this backlog item", "pick up this ticket" (3) | as mesmas 3 | nenhuma |
      | `backlog` | "create a backlog item", "add this to the backlog", "turn this idea into an issue", "groom this idea" (4) | as mesmas 4 | nenhuma |
      | `verify-before-claiming` | "you invented that", "don't guess", "achismo", "não inventa", "chutou", "pesquisa antes", "de onde tirou", "where did you see that", "cite the source", "that flag does not exist", "out of scope", "não foi isso que eu pedi" (12) | as mesmas 12 | nenhuma |
      | `assettoserver-csp-lua` | nenhuma frase entre aspas; gatilhos parentéticos (overlay, HUD, toast, in-game sound, login UI) e (empty flat box, glued or overlapping text, missing glyphs, sound plays only once) | os mesmos dois parênteses | nenhuma |

      O que saiu de cada description e para onde foi:

      | Skill | Saiu | Foi para |
      |---|---|---|
      | `code-locale` | "Covers the prose/machine boundary, the untranslatable-domain-term exception and its gate, the grooming glossary, the new-code-only migration policy, and a shipped detector…"; enumeração longa de tipos de identificador (module, REST route segment, topic name) | primeiro parágrafo do corpo; a enumeração completa já está na tabela *The two layers* |
      | `code-locale` (compat) | "measures the path of every file it is given"; "needs a harness that emits a post-write tool event" | bullet *The detector* no corpo |
      | `execute-backlog` | "following the repo's conventions", "(tests/lint/build/typecheck)", "Uses the backlog skill's config (.github/backlog.yml or workspace backlog.yml)" | primeiro parágrafo do corpo (já dizia "consumes the same config"; ganha os nomes dos arquivos) |
      | `backlog` | "so execute-backlog inherits a decision instead of making a new one"; "First run per repo/workspace launches a config wizard that writes .github/backlog.yml (repo mode) or backlog.yml (workspace mode)" | primeiro parágrafo do corpo; a seção `## Setup wizard` já existe |
      | `verify-before-claiming` | os sete degraus da escada entre parênteses; "verified/inferred/unknown claim labelling" | `## The research ladder` e o primeiro parágrafo do corpo já os carregam |
      | `assettoserver-csp-lua` | "Distilled from a production DriveZone server."; "from the server" | primeiro parágrafo do corpo |

- [ ] 3.3 `## When to use this skill` removida de `skills/api-resilience-testing/SKILL.md` (conteúdo
      já na description; nada dobrado)
- [ ] 3.4 `metadata.version` minor nas 6 skills editadas: `code-locale` 1.2.0→1.3.0,
      `execute-backlog` 1.7.0→1.8.0, `backlog` 1.4.0→1.5.0, `verify-before-claiming` 1.0.0→1.1.0,
      `assettoserver-csp-lua` 1.0.1→1.1.0, `api-resilience-testing` 1.2.1→1.3.0

## 4. README e wrappers

- [ ] 4.1 `README.md:25` e `:381`: "Agent Skills" aponta para `https://agentskills.io/specification`;
      `vercel-labs/skills` fica citado só como o CLI `npx skills` da Opção A
- [ ] 4.2 `./generate.sh` rodado; `git diff --exit-code` limpo depois

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 O artefato foi exercitado pelo caminho real; comando e fragmento da saída observada
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: name == diretório, description dobrada,
      author solvelab, version semver, category no conjunto, license MIT, compatibility presente
- [ ] Q.2 Todo conteúdo de skill tocado em inglês (locale do catálogo)
- [ ] Q.3 Gatilhos de descrição testáveis: as frases roteiam para esta skill e não colidem com
      uma irmã; "Do NOT use for" presente onde há sobreposição
- [ ] Q.4 Sem doutrina duplicada: nada reescrito inline; ver a tabela de Canonical Home em
      `design.md`
- [ ] Q.5 Todo exemplo de código em skill tocada usa identificadores em inglês; identificadores
      novos do script vêm do Glossary da issue #112 (`code-locale`)

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-agent-skills-limits --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: 35 skills, nenhum órfão ou renomeado
- [ ] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo
- [ ] V.4 `openspec archive add-agent-skills-limits --yes` depois que todos os grupos acima
      estiverem `[x]` — PR separado, depois do merge
