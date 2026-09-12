## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Lidos em 2026-09-12, na master em `c59b1f9`: `skills/documentation/SKILL.md` (as 246
      linhas), `skills/documentation/references/templates.md`,
      `skills/documentation/references/examples.md`,
      `skills/documentation/references/information-architecture.md`,
      `skills/documentation/references/check-doc-structure.py`, `skills/code-locale/SKILL.md`,
      `skills/code-locale/references/check-prose-locale.py`, `claude/global/hooks/locale-rite.py`,
      `scripts/validate-rite.sh`, `scripts/validate-rite-evidence.py`, `.github/backlog.yml`,
      `openspec/config.yaml` e `openspec/specs/skills-catalog/spec.md`
- [x] E.2 Frota medida em 2026-09-12, 39 repositórios git de `mvp/` (raiz e `docs/` de cada um):
      `find . -maxdepth 3 -type d -name .git | xargs -n1 dirname | while read r; do find "$r" -maxdepth 2 -iname '*.md' …; done | awk -F/ '{print $NF}' | sort | uniq -c | sort -rn`
      -> `55 README.md / 33 CHANGELOG.md / 21 SETUP.md / 19 TECHNICAL.md / 12 ARCHITECTURE.md / 9 API.md / 6 DEPLOYMENT.md / 4 INFRASTRUCTURE.md / 2 RUNBOOK.md / 2 DEPLOYMENT_GUIDE.md`;
      contagem de seções `grep -cE '^## ' docs/TECHNICAL.md` -> de `7` (`tools/ai-commit-messages`)
      a `25` (`filial/filial-backend-rest-api`); requisitos e ADR
      `find . -maxdepth 4 \( -iname 'REQUIREMENTS.md' -o -type d -iname adr \) | wc -l` -> `0`;
      declaração de prosa `find . -maxdepth 3 -name '.code-locale' | wc -l` -> `0`;
      CLI `openspec --version` -> `1.6.0`
- [x] E.3 Duas lacunas ficam abertas e nenhuma foi preenchida por substituto plausível. (a) A issue
      #251 afirma "9 workspaces (~25 repos)"; a contagem real na mesma varredura é 39 repositórios
      git, 18 com `openspec/` — os números desta change são os medidos, e a divergência está escrita
      no PR. (b) O efeito do detector de prosa do `code-locale` sobre a árvore espelho não pôde ser
      observado em repositório real: nenhum dos 39 declara `.code-locale`, então o conflito é
      previsto pela leitura do código, não medido em campo.
- [x] E.4 Melhorias adjacentes notadas e **não** executadas aqui, cada uma como follow-up: migrar os
      39 repositórios da frota (item por workspace); declaração de prosa com escopo por caminho em
      `.code-locale` (item em `code-locale`); o slot `KEYBINDS.md` que `openspec-drivezone` exige e o
      mapa não cobre; e a divergência de versão entre `plugins/docs/plugin.json` (3.4.0) e a skill
      (3.3.0), que é o esquema de versionamento do catálogo e não um defeito

## 2. Mapa, posse e idioma no SKILL.md

- [x] 2.1 Substituir a tabela *earned* e o slot aberto `docs/<topic>.md` pelo mapa de documentos
      (slot → canônico → condição → legados absorvidos)
- [x] 2.2 Escrever a matriz de posse (fato → dono → forma fixa → o que vai nos outros documentos),
      com a exceção única do quick start
- [x] 2.3 Escrever a regra do par de idiomas: fonte em inglês, espelho pt-BR no mesmo commit,
      blocos de código idênticos; reescrever o estilo 7 nesses termos
- [x] 2.4 Escrever a regra de migração: legado é movido, nunca duplicado; "keep the existing
      structure" passa a valer só para o que já é canônico
- [x] 2.5 Atualizar descrição do frontmatter, `## Contents`, `## See also` e
      `metadata.version` → 4.0.0

## 3. Templates e exemplos

- [x] 3.1 `templates.md`: esqueletos de `REQUIREMENTS.md`, `ARCHITECTURE.md`, `OPERATIONS.md`,
      ADR (MADR) e relatório datado, com a forma fixa de cada fato da matriz
- [x] 3.2 `templates.md`: remover a seção `## Folder Structure` do esqueleto de README, que
      contradiz a regra anti-árvore do próprio SKILL.md
- [x] 3.3 `examples.md`: exemplo por documento canônico, espelhando o template seção por seção, com
      um par en/pt-BR demonstrado

## 4. O detector de layout

- [x] 4.1 `references/check-doc-layout.py` com L1-L7, no padrão do irmão (stdlib, `Finding`,
      `--list/--rules/--exclude/--selftest`, saída 1/0/2, `KNOWN LIMIT` na docstring)
- [x] 4.2 `--selftest` com um defeito injetado por regra e um layout limpo bilíngue que não pode
      disparar nada
- [x] 4.3 `information-architecture.md`: as sete regras de layout com fonte publicada, medição e
      veredito, no formato das sete de página

## 5. Pesquisa e fronteiras

- [x] 5.1 `research/documentation-layout/`: protocolo com o veredito escrito antes, levantamento de
      frota re-executável e a tabela medida por regra
- [x] 5.2 Medir falso positivo de L1-L7 na frota real e registrar por regra; regra acima do
      limiar de R6 (7 em 10) não publica com gate
- [x] 5.3 `skills/code-locale/SKILL.md`: uma linha declarando a árvore espelho como exceção e
      nomeando o item que resolve o escopo por caminho
- [x] 5.4 Regenerar mirrors (`plugins/docs/`, `claude/skills/`, `cursor/rules/`, `copilot/`) pelo
      fluxo existente, nunca à mão

## 6. Simulation & Field Proof (MANDATORY)

- [x] S.1 Exercitada pelo caminho real, skill instalada em `.claude/skills/documentation/` de uma
      cópia descartável de um repositório real:
      `claude -p "Documente este repositório. Siga a skill documentation." --permission-mode acceptEdits`
      -> `Documentado. 13 arquivos, duas árvores.` (49 turnos, 819 s, US$ 4,83). Auditoria do
      resultado: `python3 references/check-doc-layout.py <repo>` -> `findings: 0`. Segunda célula
      (repo com `openspec/`) foi bloqueada pelo rito global do próprio mantenedor e não escreveu
      nada: registrada como bloqueada, não como resultado, em `research/documentation-layout/simulation.md`
- [x] S.2 Matriz medida, em contagens: documentos produzidos dentro do mapa 13/13; fora do mapa 0/13;
      slots não ganhos declarados com motivo 4/4; espelho presente 6/6; contagem de `##` igual entre
      fonte e espelho 6/6; `.md` soltos na raiz 0; cabeçalho de env vars em 2 arquivos (os dois
      SETUP.md) e de endpoints em 2 (os dois API.md); achados L1-L7 no resultado 0; selftests
      `check-doc-layout.py --selftest` 9/9 e `survey.py --selftest` 0 falhas
- [x] S.3 Escapou um falso positivo de L7 que nem o selftest nem a frota produziriam: o espelho de
      raiz `README.pt-BR.md` carrega legitimamente a tabela do README, e a comparação era por nome de
      arquivo. Corrigido dobrando a etiqueta de idioma antes de comparar o dono, com caso novo no
      layout limpo do selftest. Também ficou de fora, e está dito: a célula com `openspec/` não rodou,
      então "REQUIREMENTS.md indexa em vez de copiar" e "legado migra em vez de duplicar" seguem sem
      medição end-to-end. E o teto de gasto declarado (US$ 5) foi estourado: US$ 7,02 no total

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme nas skills tocadas: name == diretório, description folded,
      `metadata.author` solvelab, semver, category do conjunto controlado, license MIT, compatibility
- [x] Q.2 Todo o conteúdo tocado das skills em inglês (locale do catálogo)
- [x] Q.3 Gatilhos da description testáveis: as frases que um usuário diria roteiam para esta skill
      e não colidem com irmãs; fronteira "Do NOT use for" presente
- [x] Q.4 Sem doutrina duplicada: cada regra transversal tocada linka a skill canônica da tabela do
      `design.md` em vez de restatement
- [x] Q.5 Todo exemplo de código nas skills tocadas usa identificadores, rotas, chaves e nomes de
      evento em inglês; termo mantido em outro idioma carrega a razão inline (`code-locale`)

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate update-documentation-document-map --strict` verde
- [x] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py`,
      `scripts/validate-agents.py`, `scripts/validate-repo-hygiene.py` e
      `scripts/validate-skill-version.py` verdes; contagem de skills publicada bate
- [x] V.3 README do catálogo atualizado onde a composição ou o uso mudam
- [ ] V.4 `openspec archive update-documentation-document-map --yes` **depois** do merge — a change
      fica ativa neste PR, por rito
