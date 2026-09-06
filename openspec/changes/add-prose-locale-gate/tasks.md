## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `4ef1f3f` (`docs(openspec): arquiva as changes harden-gate-followups e
      extend-install-form-links (#178)`), topo de `master` em 2026-09-06:

      - `skills/code-locale/references/check-identifier-locale.py` — 942 linhas; KNOWN LIMIT 7 em
        42-47 (prosa retirada antes da análise); `COMMENT_SYNTAX` 203-213; `EXT_LANG` 215-220;
        `strip_prose()` 302-354; `is_vendored()` 397; `load_allowlist()` 405-415;
        `project_relative()` 477; `scan_text()` 556-589 (waiver na linha ou na anterior);
        `scan_diff()` 616-685; selftest 689-854; `main()` 858-937.
      - `skills/code-locale/references/programming-words.txt` (regras de linha 7-16) e
        `references/english-words.SOURCE.md` — forma dos arquivos de dados e da procedência.
      - `claude/global/hooks/locale-rite.py` — 655 linhas; `CHECK_PATH` 128; `written_text()`
        196-206; `first_line_of()` 209-228; `waiver_above()` 231-247; `findings_for()` 250-273;
        `deny_reason()` 308-335 (18 linhas por construção); `evaluate()` 350-388; selftest 391-628.
      - `claude/global/hooks/locale-stop-gate.py` — 653 linhas; `uncommitted_diff()` 233-288;
        `gating_findings()` 291-296; `evaluate()` 324-365; `_repo()` 391-399; selftest 407-626.
      - `skills/code-locale/references/pre-commit-locale.sh` — `locate_check()`, a linha do diff
        staged, o `case "$rc"` e a regra da linha `findings:`.
      - `skills/code-locale/references/ci-step.md` — o job, o pin por tag e o `sha256sum -c`.
      - `skills/code-locale/SKILL.md` — frontmatter (`version: 1.4.3`, description 996 chars),
        seções *The two layers*, *Reviewing a diff*, *Catching it at the write*, *Wire it in one
        minute*.
      - `openspec/specs/skills-catalog/spec.md:662-751`, `:846-961`, `:1406-1490` — os três
        requisitos modificados, com todos os cenários copiados no delta.
      - `openspec/config.yaml`, `openspec/schemas/skills-rite/templates/{proposal,design,tasks,spec}.md`,
        `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py` (regras E.1-E.4, S.1-S.3),
        `scripts/validate-skill-version.py`, `scripts/validate-skills.py` (C1, C11), `generate.sh`.
      - `openspec/changes/archive/2026-09-05-enforce-locale-on-write/{proposal,design,tasks}.md` e
        `specs/skills-catalog/spec.md`; `openspec/changes/archive/2026-09-04-close-ci-gate-holes/` —
        forma da casa.
      - `README.md:235-420` — a seção dos hooks e a tabela *Which layer catches what*.
      - `.github/workflows/ci.yml:130-175` — os steps de selftest, onde o novo entra.
      - Corpus de calibração (somente leitura):
        `/mnt/d/DOCUMENTS/Documents/Project/WSL/mvp/editaudiotomovie/omnivoice-tts/server_addons`
        (`inference.py`, `schemas.py`, `server_app.py`, `voices.py`, `tests/*.py`), lido em
        2026-09-06.

- [x] E.2 Ferramentas e comportamentos probados contra a versão instalada

      ```
      python3 --version                                   -> Python 3.14.5
      openspec --version                                  -> 1.6.0
      openspec new change add-prose-locale-gate --schema skills-rite
                                                          -> Created change 'add-prose-locale-gate' at openspec/changes/add-prose-locale-gate/
                                                          -> Schema: skills-rite
      python3 skills/code-locale/references/check-identifier-locale.py --selftest | tail -1
                                                          -> selftest OK: 7 content tiers fire, 16 clean cases stay silent, 6 path tiers fire, 10 path cases stay silent, 2 en-unknown tiers fire, 5 en-unknown cases stay silent
      which agentskills                                   -> (não instalado no PATH desta máquina)
      uvx --from skills-ref==0.1.1 agentskills --help     -> Usage: agentskills [OPTIONS] COMMAND [ARGS]...   (a mesma versão que o ci.yml pina)
      grep -h -n '^\s*#' server_addons/*.py | head        -> "# OmniVoice has a closed set of inline non-verbal tags that the tokenizer" [...]   (comentários em inglês, como a issue mediu)
      ```

- [x] E.3 O que não pôde ser probado

      Um item: o hook disparado pelo harness numa sessão real (`claude -p`) com um repositório
      temporário declarando `prose: pt-BR`. Este item roda num subagente, que não dispara o hook da
      sessão; a simulação alimenta os hooks por stdin com payloads na forma que o bundle 2.1.261
      declara (a mesma forma probada pela change `enforce-locale-on-write`), e a corrida real fica
      escrita em S.2 com o comando exato, para a sessão principal executar antes do merge.

- [x] E.4 Checagem de escopo

      A change faz o que a issue #179 pediu. Notados pelo caminho e **não** feitos, ficam como
      follow-up: (1) medir strings de UI e mensagens de log — decisão registrada como KNOWN LIMIT,
      não como pendência; (2) um `--fix` que traduza — a regra de Grounding proíbe inventar
      tradução; (3) `scan_diff()` do irmão aceitar um scanner por parâmetro em vez de o detector de
      prosa ter o próprio leitor de diff — o de prosa precisa de `.md` e não precisa do tier de
      caminho, então o leitor próprio (≈40 linhas) custa menos que generalizar o do irmão; (4) o
      catálogo declarar a própria prosa — repositório misto, fica de fora por decisão da issue.

## 2. Detector de prosa, listas de palavras e tokenizador compartilhado

- [ ] 2.1 `check-identifier-locale.py`: `split_prose(line, lang, state) -> (code, state, fragments)`
      com `kind` em `comment|docstring|string`; `strip_prose()` vira wrapper fino; selftest do irmão
      verde sem edição (D2)
- [ ] 2.2 `check-prose-locale.py`: importa o irmão por caminho; declaração (`.code-locale`,
      `find_declaration`, `load_declaration`, exit 2 em valor inválido); extração de
      comentários/docstrings por blocos (D3) e de parágrafos de `.md` fora de fences e frontmatter;
      limpeza e classificação (D4); waivers e allowlist; `--explain`, `--report`, `--diff -`,
      `--stdin --lang --path`, `--prose`, `--root`; KNOWN LIMIT no cabeçalho (D5)
- [ ] 2.3 `prose-words-pt.txt`, `prose-words-en.txt` (uma palavra por linha, interseção vazia
      afirmada no carregamento e no selftest) e `prose-words.SOURCE.md`
- [ ] 2.4 `--selftest` com os casos de FR5 da issue: declaração ausente, PT correto, EN gating em
      comentário e em docstring, fragmento curto pulado, trecho entre aspas ignorado, linha técnica
      pulada, `.md` inglês só consultivo, waiver na linha e na linha acima, caminho na allowlist,
      `--diff` com caminho vendored pulado, `--prose` override, declaração inválida exit 2,
      interseção vazia, direção inversa (`prose: en`, comentário português -> gating)

## 3. Hooks

- [ ] 3.1 `locale-rite.py`: localiza a declaração subindo do arquivo escrito; `PreToolUse` nega
      comentário/docstring gating com as três saídas; `PostToolUse` avisa; selftest com diretório
      temporário com e sem `.code-locale`, todos os casos existentes mantidos (D6)
- [ ] 3.2 `locale-stop-gate.py`: mede o diff com o detector de prosa quando a raiz declara; bloqueia
      em gating, `systemMessage` em `.md`; guarda de `stop_hook_active` mantida; selftest com
      repositório temporário com e sem `.code-locale`, todos os casos existentes mantidos (D6)

## 4. Kit, skill e wiring do repositório

- [ ] 4.1 `pre-commit-locale.sh` roda o detector de prosa sobre o diff staged quando
      `$(git rev-parse --show-toplevel)/.code-locale` existe; `ci-step.md` documenta o step extra
      e a declaração (D8)
- [ ] 4.2 `ci.yml`: step `Prose-locale detector self-test` ao lado do de identificadores; README:
      linhas dos hooks mencionam a direção de prosa
- [ ] 4.3 `SKILL.md` do `code-locale`: seção *Prose follows the repository* (declaração, o que é
      medido, o que escapa, as saídas, por que o catálogo não declara); `metadata.version` 1.4.3 ->
      1.5.0; description ≤ 1024 sem edição; `bash generate.sh` e wrappers commitados

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 Os artefatos exercitados pelo caminho real: `check-prose-locale.py --selftest`,
      `check-identifier-locale.py --selftest`, `locale-rite.py --selftest`,
      `locale-stop-gate.py --selftest`, e o detector por stdin/`--diff` com os payloads da issue
      (FR2, FR3) — comando e fragmento da saída observada
- [ ] S.2 Corrida na sessão real do mantenedor (não executável por este subagente — E.3): num
      repositório temporário declarando `pt-BR`, o harness nega o `Write` com comentário inglês,
      grava o comentário português e só avisa no `.md`. Comando exato, a rodar da sessão principal
      com os hooks wired em `~/.claude/settings.json`:

      ```
      T=$(mktemp -d) && cd "$T" && git init -q && printf 'prose: pt-BR\n' > .code-locale && \
      claude -p --permission-mode acceptEdits --model sonnet \
        'Do exactly these three tool calls and nothing else, in order, then stop: (1) Write the file orders/total.py with the content "# compute the total for the order and apply the discount\ndef total(x):\n    return x\n"; (2) Write the file orders/order_total.py with the content "# calcula o total do pedido e aplica o desconto\ndef total(x):\n    return x\n"; (3) Write the file NOTES.md with the content "This paragraph explains how the order total is computed for the customer.\n". Report which calls were denied and quote the denial reason.' ; \
      ls -R "$T" ; cat "$T"/orders/*.py 2>/dev/null
      ```

      Esperado: (1) negado com `CODE-LOCALE: write denied — ... comment reads as en, repo prose is
      pt` e as saídas no motivo, `orders/total.py` ausente; (2) gravado, `orders/order_total.py`
      existe com o comentário português; (3) gravado, com `[advisory] paragraph reads as en` no
      contexto do PostToolUse (o modelo relata o aviso, não uma negação). Registrar a saída
      observada aqui e ticar.
- [ ] S.3 Calibração (TR3, FR4): contagens de `--prose pt-BR --report` sobre `server_addons`
      (gating, consultivo, pulados por motivo, precisão adjudicada à mão ≥ 0,9, falsos positivos
      excluídos e como), `--prose en` sobre `skills/` + `claude/` (esperado 0 gating), `--prose
      pt-BR` sobre `openspec/changes/archive` (esperado 0 gating); o que escapou ou se comportou
      diferente do esperado

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter uniforme no `SKILL.md` tocado (`code-locale`): name == diretório, description
      dobrada, `metadata.author solvelab`, `metadata.version 1.5.0`, categoria `process`, MIT,
      compatibility presente
- [ ] Q.2 Conteúdo de skill tocado em inglês: SKILL.md, detector, listas, SOURCE, kit, docstrings e
      nomes de caso do selftest; proposal/design/tasks em português, como as changes da casa
- [ ] Q.3 Gatilhos de descrição testáveis — a description não muda (996/1024); "prose follows the
      repository's working language" já é gatilho da skill
- [ ] Q.4 Sem doutrina duplicada: hooks, kit e README **nomeiam** `.code-locale` e as saídas e
      apontam para a seção da skill; tabelas por linguagem importadas do irmão (design, Canonical
      Home)
- [ ] Q.5 Identificadores em inglês no que a change introduz —
      `python3 skills/code-locale/references/check-identifier-locale.py` sobre os arquivos novos e
      editados -> `findings: 0`

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate add-prose-locale-gate --strict` verde; `bash scripts/validate-rite.sh`
      verde; `python3 scripts/validate-skill-version.py` verde; runner de gates (`gates.sh`) todo
      `PASS` e `dirty-after: 0`; `agentskills validate skills/code-locale` verde
- [ ] V.2 Descoberta do catálogo intacta: `ls -d skills/*/ | wc -l` -> 36; `validate-skills.py`
      `skills checked: 36 findings: 0`
- [ ] V.3 README / docs: seção dos hooks menciona a direção de prosa; `ci-step.md` e SKILL.md
      documentam a declaração; wrappers regenerados
- [ ] V.4 `openspec archive add-prose-locale-gate --yes` depois que todos os grupos acima estiverem
      `[x]` — PR separado, como o repositório já faz
