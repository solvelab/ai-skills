# Change: A documentação ganha um mapa fixo, um dono por informação e um par de idiomas

## Why

A skill `documentation` decide quais documentos um projeto ganha por uma tabela *earned* — `README.md`
incondicional, o resto por condição, mais um slot aberto `docs/<topic>.md`
(`skills/documentation/SKILL.md:67-77`). O resultado é o que ela promete: um conjunto diferente por
repositório. Medido em 2026-09-12 sobre os 39 repositórios git de `mvp/` (18 deles rodam OpenSpec),
varrendo a raiz e `docs/` de cada um:

| Fato medido | Número |
|---|---|
| nomes distintos para o slot de arquitetura | `docs/TECHNICAL.md` 19 · `ARCHITECTURE.md` 12 · `docs/DESIGN.md` 1 |
| repositórios que carregam **dois** desses nomes ao mesmo tempo | 11 de 39 |
| nomes distintos para o slot de operação | `DEPLOYMENT.md` 6 · `INFRASTRUCTURE.md` 4 · `DEPLOYMENT_GUIDE.md` 2 · `RUNBOOK.md` 2 · `DEPLOY.md` 1 · `COMO-SUBIR.md` 1 |
| seções `##` em `docs/TECHNICAL.md`, sob o mesmo nome | de 7 a 25 (o template prescreve 10) |
| documentos de requisitos em toda a frota | 0 |
| diretórios de ADR em toda a frota | 0 |
| relatórios transitórios soltos na raiz ou em `docs/` | 21 |
| nomes de arquivo em português | 5 (`COMO-SUBIR.md`, `CORRECAO_MARKETPLACE_COMPLETA.md`, `revalidacao-hermes.md`, …) |

Quatro lacunas da skill produzem esses números, e nenhuma é acidente de uso:

1. **Sem vocabulário canônico.** A tabela é por condição, não por conceito. Dois repositórios que
   ganham o mesmo direito escrevem nomes diferentes, e onze deles escreveram os dois.
2. **Sem dono por informação.** A skill tem "one term per concept" (estilo 3) e não tem "one home
   per fact": uma tabela de variáveis de ambiente é legítima no README, no `SETUP.md` e no
   `TECHNICAL.md` ao mesmo tempo, e as três divergem sem que nada aponte.
3. **Sem casa para requisito, decisão e relatório datado.** Requisito é delegado a `openspec`
   (`SKILL.md:244`), que só existe em 18 dos 39 repositórios e guarda delta por change, não um
   documento cumulativo; ADR aparece em uma célula (`SKILL.md:93`) sem pasta nem formato; relatório
   transitório não é mencionado, e 21 deles estão misturados com documentação permanente.
4. **Sem auditoria de layout.** `references/check-doc-structure.py` mede a página (R1-R7), nunca o
   repositório, então layout legado nunca é detectado — e `SKILL.md:226` ("keep the existing
   structure") manda preservá-lo.

Uma quinta lacuna é uma decisão do mantenedor, tomada em 2026-09-12 na issue #251: a documentação
precisa existir em inglês e em português. O estilo 7 (`SKILL.md:220-222`) fixa um idioma só e não
tem regra de espelho nem de paridade.

Os dois arquivos de referência também já divergem entre si: `templates.md:309-321` prescreve dez
seções para `TECHNICAL.md` e `examples.md:207-212` demonstra seis.

## What Changes

- `documentation` → **4.0.0** (major: muda quais arquivos a skill produz, renomeia o canônico do
  slot de arquitetura e introduz a árvore espelho).
  - A tabela *earned* e o slot aberto `docs/<topic>.md` saem. Entra o **mapa de documentos**: slot
    (Diátaxis) → nome canônico em inglês → condição → nomes legados que ele absorve. Slot não ganho
    não vira arquivo: vira uma linha `not applicable: <reason>` no índice do README.
  - Entra a **matriz de posse**: cada tipo de fato (variáveis de ambiente, endpoints, portas e
    recursos, requisitos, decisões, comandos de desenvolvimento, troubleshooting) tem um documento
    dono e uma forma fixa; fora do dono, só link.
  - Entra o **par de idiomas**: `README.md` + `README.pt-BR.md` na raiz, `docs/en/` + `docs/pt-BR/`
    espelhados. Inglês é a fonte, pt-BR nasce no mesmo commit, os blocos de código são idênticos nos
    dois. O estilo 7 é reescrito nesses termos.
  - `docs/en/REQUIREMENTS.md` passa a ser incondicional (propósito, usuários, `FR-n`/`NFR-n`,
    glossário). Onde há `openspec/specs/`, ele indexa e linka as capabilities em vez de copiá-las.
  - `docs/en/adr/NNNN-<slug>.md` (MADR) ganha regra e esqueleto; `docs/reports/YYYY-MM-DD-<slug>.md`
    passa a ser o único lugar de artefato transitório.
- `references/check-doc-layout.py` — novo detector, irmão do que já existe: audita o **repositório**,
  não a página. Sete regras (L1 slot canônico presente ou declarado, L2 legado com destino, L3 `.md`
  solto na raiz, L4 relatório datado fora de `docs/reports/`, L5 nome de arquivo em português, L6
  paridade en/pt-BR, L7 posse da informação), `--selftest` com um defeito injetado por regra, nunca
  move arquivo.
- `references/information-architecture.md` ganha as sete regras de layout com fonte, medição e
  veredito, no mesmo formato das sete de página.
- `references/templates.md` e `references/examples.md` passam a cobrir os documentos canônicos novos
  e a concordar seção por seção.
- `skills/code-locale/SKILL.md` ganha uma linha: a árvore espelho é a exceção declarada da regra de
  prosa única, e o suporte a escopo por caminho em `.code-locale` é trabalho de outro item.
- `research/documentation-layout/` — o levantamento de frota re-executável (o número acima), a
  medição de falso positivo por regra e a simulação end-to-end da skill pelo caminho real.

## Capabilities

### New Capabilities

- (nenhuma — `skills-catalog` ganha um requisito)

### Modified Capabilities

- `skills-catalog`: ADDED *Project documentation layout has a canonical home* — a skill que decide
  quais documentos existem passa a publicar um mapa fechado por conceito, um dono por informação, o
  par de idiomas com fonte única e um detector que audita o layout do repositório.

## Impact

- Skill afetada: `documentation` (4.0.0). `code-locale` recebe uma linha de fronteira, sem mudança de
  comportamento (patch).
- Mirrors regenerados: `plugins/docs/`, `claude/skills/documentation/`, `cursor/rules/documentation.mdc`,
  `copilot/instructions/documentation.instructions.md`.
- Consumidores: todo repositório já documentado passa a ter layout legado detectável. A migração dos
  39 repositórios de `mvp/` **não** está aqui — é item por workspace, depois desta publicação.
- Bloqueio conhecido para essa migração, não para esta change: `.code-locale` declara um idioma de
  prosa por repositório, sem escopo por caminho, então a árvore no idioma não declarado é apontada
  pelo detector de prosa. Nenhum repositório da frota declara `.code-locale` hoje (medido: 0 de 39),
  então o bloqueio é futuro e a skill o nomeia em vez de silenciá-lo.
- Nenhuma dependência nova: o detector é stdlib, como o irmão dele.
