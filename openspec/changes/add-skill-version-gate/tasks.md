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

- [ ] 2.1 `resolve_base`, `changed_paths`, `read_pr_body` e o skip fora de `pull_request` no idioma
      exato de `validate-spec-rite.py`; `MIN_REASON` importado do irmão
- [ ] 2.2 `collect()` lê o diff por skill: caminhos sob `skills/<x>/`, versão na base e no HEAD, e
      se o conteúdo mudou além da linha `  version:`; árvores geradas ignoradas
- [ ] 2.3 `evaluate()` pura: `V1` skill editada sem bump e sem dispensa; `V2` versão que desce;
      `V3` dispensa sem motivo utilizável; skill nova e wrapper-only mudos
- [ ] 2.4 `--selftest`: editada sem bump → achado; com bump → mudo; com dispensa → mudo; skill nova →
      mudo; wrapper-only → mudo; versão que desce → achado; dispensa sem motivo → achado
- [ ] 2.5 Docstring lista as regras e o KNOWN LIMIT

## 3. CI e documentação

- [ ] 3.1 `ci.yml`: steps *Skill version gate* e *Skill version self-test* logo depois de *Spec-rite
      self-test*
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
