## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos abertos e lidos, não recordados, no commit `3719a76` (2026-08-26):
      `skills/code-locale/references/check-identifier-locale.py` (docstring, `MIN_SEGMENT`,
      `ALLOWLIST_FILE`, `load_allowlist`, `is_vendored`, `classify`, `scan_text`, `scan_diff`,
      `selftest`, `main`), `skills/code-locale/SKILL.md`, `claude/global/hooks/backlog-rite.py`,
      `claude/global/hooks/verify-rite.py`, `.github/workflows/ci.yml` (linhas 81–120),
      `openspec/specs/skills-catalog/spec.md` (linhas 195–245 e 520–568),
      `openspec/schemas/skills-rite/schema.yaml`, `openspec/schemas/skills-rite/templates/tasks.md`,
      `scripts/validate-rite.sh`, `scripts/validate-spec-rite.py`, `scripts/validate-rite-evidence.py`
- [x] E.2 Probes contra a versão instalada, 2026-08-26:
      `python3 --version` -> `Python 3.14.5`;
      `claude --version` -> `2.1.246 (Claude Code)`;
      `openspec --version` -> `1.6.0`;
      `python3 skills/code-locale/references/check-identifier-locale.py <dir>/servicos_pedido/calculo_frete.py`
      -> `findings: 0` com `exit=0` (corpo em inglês, caminho em português — o defeito que motiva a change);
      `python3 skills/code-locale/references/check-identifier-locale.py --diff fake.diff` -> `findings: 0`, `exit=0`;
      `grep -aoh "additionalContext.\{0,60\}" ~/.local/share/claude/versions/2.1.246`
      -> `additionalContext:a,...l}=e.hookSpecificOutput` e `additionalContext:8000` — o campo que o
      harness instalado lê em `PostToolUse`, e seu teto em caracteres
- [x] E.3 Não probado, registrado como limite e não afirmado: como Codex, Cursor e Copilot expõem um
      evento equivalente ao `PostToolUse` — nenhum deles foi medido, então a change entrega o hook
      apenas para o harness cujo contrato foi lido, e o design registra isso em Open Questions. A
      documentação de hooks foi lida em `code.claude.com/docs/en/hooks` (2026-08-26) e confirmada
      contra o binário instalado; onde as duas fontes divergiriam, vale o binário.
- [x] E.4 Escopo: um desvio, autorizado e registrado — ampliar o léxico estava em Out of scope na
      issue #95, e o sweep de aceite mostrou que sem `servico(s)`, `calculo` e `relatorio(s)` o
      critério AC1 era falso (`servicos_pedido/calculo_frete.py` era pego só por `pedido`). O
      mantenedor autorizou em 2026-08-26 e a autorização está como comentário na issue.
      `python3 skills/code-locale/references/check-identifier-locale.py .` -> `findings: 0` depois da
      adição: nenhum falso positivo novo no repositório inteiro. Follow-ups listados e **não**
      executados — (a) template de pre-commit/CI para repositórios de destino, fora de escopo na
      issue; (b) `caveman-statusline.ps1` desatualizado em `~/.claude/hooks` (config pessoal, fora do
      repositório); (c) as palavras que seguem escapando (`prazo`, `chave`), registradas no
      KNOWN LIMIT em vez de adivinhadas por regra.

## 2. Tier de caminho no detector

- [x] 2.1 `scan_path()`: segmenta diretórios + radical do arquivo, aplica `segments()`/`classify()`,
      devolve `Finding` com tier prefixado e a linha de dispensa da allowlist
- [x] 2.2 Caminho medido relativo ao `cwd` quando dentro dele; apenas o nome do arquivo quando fora
      (design D1)
- [x] 2.3 Modo arquivo: `scan_path()` roda antes do teste de extensão, para que um tipo sem perfil de
      língua ainda tenha o caminho medido e o conteúdo reportado como `skipped`
- [x] 2.4 Modo `--diff`: caminho medido só quando o cabeçalho anterior é `--- /dev/null` (design D2)
- [x] 2.5 Exclusões herdadas verificadas: `is_vendored`, `MIN_SEGMENT`, `DOMAIN_KEEP`, allowlist
- [x] 2.6 KNOWN LIMIT do docstring ganha a linha do que o tier de caminho não alcança
- [x] 2.7 Léxico ampliado com `servico(s)`, `calculo`, `relatorio(s)` (desvio autorizado, ver E.4);
      assertion de colisão verde e field score do repositório em `findings: 0`

## 3. Hook de escrita

- [x] 3.1 `claude/global/hooks/locale-rite.py`: lê o payload `PostToolUse`, extrai `tool_name`,
      `tool_input.file_path` e o conteúdo escrito (`content` no `Write`, `new_string` no `Edit`)
- [x] 3.2 Importa o detector por `importlib.util.spec_from_file_location`; detector ausente → saída
      silenciosa 0 (design D5)
- [x] 3.3 Achados devolvidos em `hookSpecificOutput.additionalContext`, truncados ao teto medido;
      `systemMessage` curto para o usuário (design D4)
- [x] 3.4 Silêncio total quando limpo; payload ausente/malformado → exit 0 sem saída
- [x] 3.5 `--selftest` do próprio hook: escrita limpa, escrita com caminho português, payload
      malformado, tipo de arquivo sem perfil de língua

## 4. Cobertura e wiring

- [x] 4.1 `--selftest` do detector ganha os casos do tier de caminho (hit e clean)
- [x] 4.2 `.github/workflows/ci.yml`: passo de self-test do hook, ao lado dos existentes
- [x] 4.3 `README.md`: wiring do terceiro hook junto dos outros dois
- [x] 4.4 `skills/code-locale/SKILL.md`: o gate de escrita e a dispensa por allowlist documentados
- [x] 4.5 `./generate.sh` re-executado; espelhos idênticos ao `skills/`

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter do `skills/code-locale/SKILL.md` intacto e uniforme: `name == code-locale`,
      descrição dobrada, `metadata.author: solvelab`, `metadata.version` semver bumpado,
      `category` no conjunto controlado, `license: MIT`, `compatibility` presente e ainda verdadeira
      (o detector continua stdlib-only)
- [x] Q.2 Todo conteúdo tocado do skill em inglês (locale do catálogo)
- [x] Q.3 Gatilhos da descrição continuam testáveis e sem colisão com skill irmão; a fronteira
      "Do NOT use for" segue presente
- [x] Q.4 Sem doutrina duplicada: o hook novo não repete a doutrina do `code-locale` nem o texto do
      rito de backlog — ele aponta (design.md, tabela Canonical Home)
- [x] Q.5 Todo exemplo de código tocado usa identificadores, rotas, chaves e nomes de evento em
      inglês; termo mantido em outra língua carrega o motivo inline

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-locale-write-gate --strict` verde
- [x] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde e os 34 skills
      seguem publicados, sem órfão nem renomeado
- [x] V.3 README/docs atualizados onde o uso muda (wiring do hook)
- [ ] V.4 `openspec archive add-locale-write-gate --yes` depois que todos os grupos acima estiverem
      `[x]` — executado após o merge do PR, não antes
