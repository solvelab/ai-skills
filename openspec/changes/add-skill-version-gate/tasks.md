## 1. Evidence & Sources (MANDATORY)

<!-- Always the FIRST group: probe before you write. Record the COMMAND and a fragment of its
     RAW OUTPUT, never a conclusion. Shape gated by scripts/validate-rite-evidence.py once ticked:
       E.1  a repo-relative path AND the commit sha or date it was read at
       E.2  at least one `command` -> a fragment of its output
       E.3  names the gap, or states explicitly that there is none
       E.4  lists a follow-up, or states explicitly that there is none -->

- [ ] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos
- [ ] E.2 Ferramentas e comportamentos probados contra a versão instalada; comando e fragmento da
      saída registrados
- [ ] E.3 O que não pôde ser probado, escrito como questão aberta — nunca como fato
- [ ] E.4 Checagem de escopo: a change faz só o que a proposta pediu; melhorias adjacentes ficam
      listadas como follow-up

## 2. O gate `scripts/validate-skill-version.py` (D1–D6)

- [x] 2.1 `resolve_base`, `changed_paths`, `read_pr_body` e o skip fora de `pull_request` no idioma
      exato de `validate-spec-rite.py`; `MIN_REASON` importado do irmão

      ```
      grep -n "def resolve_base\|def read_pr_body\|def changed_paths\|MIN_REASON = \|not pull_request" scripts/validate-skill-version.py
      -> 94:MIN_REASON = _sibling_min_reason()
      -> 113:def resolve_base(root: Path) -> str | None:
      -> 129:def read_pr_body() -> str:
      -> 155:def changed_paths(root: Path, base: str, head: str = "HEAD") -> list[str]:
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
      -> 7/7 defect classes detected, 11/11 false-positive cases stayed silent, 8/8 helper cases correct
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
- [ ] 3.2 `README.md`: as duas frases da regra dizem que o bump é medido pelo gate e nomeiam a linha
      `Skill-version: none — <motivo>`
- [ ] 3.3 `skills/execute-backlog/references/spec-rite.md`, *In the PR body*: parágrafo com a linha
      `Skill-version`; `metadata.version` de `execute-backlog` 1.8.0 → 1.8.1; `bash generate.sh`

## 4. Simulation & Field Proof (MANDATORY)

<!-- Shape gated by scripts/validate-rite-evidence.py once ticked:
       S.1  an `entry point` -> a fragment of the OBSERVED output
       S.2  the case matrix as counts (n/n)
       S.3  names what escaped or misbehaved, or states explicitly that nothing did -->

- [ ] S.1 O gate exercitado pelo caminho real: `evaluate()` contra o histórico (`cf767ee` tem de
      produzir achados; o branch do PR #122 tem de ficar mudo) e o script pelo entry point com
      `GITHUB_EVENT_PATH` fabricado, com e sem a dispensa
- [ ] S.2 Matriz de casos medida, em contagens
- [ ] S.3 O que escapou ou se comportou diferente do esperado

## 5. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: name == directory, description dobrada,
      author solvelab, version semver, category no conjunto, license MIT, compatibility presente
- [ ] Q.2 Conteúdo de skill tocado em inglês
- [ ] Q.3 Gatilhos de descrição testáveis, sem colisão com skill irmã
- [ ] Q.4 Sem doutrina duplicada: cada regra transversal restada inline virou link (tabela Canonical
      Home em `design.md`)
- [ ] Q.5 Identificadores em inglês em todo exemplo de código tocado (`code-locale`)

## 6. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-skill-version-gate --strict` verde
- [ ] V.2 Descoberta do catálogo intacta: 35 skills, sem órfão
- [ ] V.3 README / docs atualizados onde a change altera o uso (regra do bump e linha de dispensa)
- [ ] V.4 `openspec archive add-skill-version-gate --yes` depois de todos os grupos acima `[x]`
