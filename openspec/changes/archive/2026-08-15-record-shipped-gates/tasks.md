## 1. Evidence & Sources (MANDATORY)

<!-- Sempre o PRIMEIRO grupo: prove antes de escrever. Registre o COMANDO e um fragmento da SAÍDA
     CRUA, nunca uma conclusão. Doutrina: skill verify-before-claiming. -->

- [x] E.1 Todo caminho local que este change usa foi ABERTO e lido em `c178c1b` em 2026-08-15, não
      recordado: `openspec/specs/skills-catalog/spec.md` (o requisito *The rite gates evidence
      before it gates quality*, cujo texto integral o delta reproduz),
      `openspec/specs/skills-authoring/spec.md` (*Uniform frontmatter metadata* e
      *Authoring rules are machine-enforced*), `.github/workflows/ci.yml` (passo de frontmatter e
      passo do self-test do rito), `scripts/validate-rite-evidence.py`, `scripts/validate-rite.sh`,
      `openspec/changes/archive/2026-08-07-add-repo-hygiene-gates/proposal.md` e
      `openspec/changes/archive/2026-08-06-enforce-authoring-checks/proposal.md` (os dois
      precedentes que provam que gate novo levava proposta neste repositório).
- [x] E.2 Ferramentas probadas nesta máquina em 2026-08-15: `python3 --version` -> `Python 3.14.5`;
      `openspec --version` -> `1.6.0`; `gh --version` -> `gh version 2.92.0 (2026-04-28)`.
      A deriva foi medida, não suposta:
      `grep -c "validate-rite-evidence\|evidence shape\|R1 " openspec/specs/*/spec.md` ->
      `skills-authoring:0` e `skills-catalog:0`.
      E o gate que este change documenta foi confirmado ativo por simulação, num change temporário
      com as quatro caixas em forma de conclusão:
      `python3 scripts/validate-rite-evidence.py` -> quatro erros `R1 evidence shape`, um por caixa
      (`E.1 cites no repo-relative path`, `E.2 states a conclusion, not a probe`, `E.3 neither names
      a gap nor states there is none`, `E.4 neither names a follow-up nor states there is none`).
- [x] E.3 O que não pôde ser provado está escrito, não afirmado: a intenção original por trás da
      frase *"ajuste de gate existente, não capacidade nova"* registrada na issue #79 não é
      recuperável — só o resultado é, e o resultado é que o precedente contradiz a frase. O change
      registra o fato, não uma reconstrução do raciocínio.
      Um falso alarme também fica registrado em vez de virar conclusão: uma varredura por NOME DE
      ARQUIVO (`grep -rlc <script> openspec/specs/`) sugeriu que cinco gates estavam sem registro.
      Ao ler as specs, `scan-secrets` está coberto por *The catalog carries no credentials*,
      `validate-repo-hygiene` por *The repository itself is gated, not only its skills* e
      `validate-rite` por *The rite gates evidence before it gates quality* — descritos por
      comportamento, sem citar o nome do script. A deriva real são os dois casos deste change; a
      varredura por nome de arquivo é heurística ruim e não vale como medida.
- [x] E.4 Verificação de escopo: este change faz só o que a proposta pediu. Notado e **não** feito,
      listado como follow-up: os desvios equivalentes em `DriveZoneFivem/backend-drivezone` e
      `DriveZoneFivem/fivem-drivezone`, que têm rito e schema próprios e ganham item em cada
      repositório — remediá-los daqui seria escopo que ninguém pediu.

## 2. Deltas de spec

- [x] 2.1 `specs/skills-authoring/spec.md` — MODIFIED *Uniform frontmatter metadata*: os sete campos -> escrito; `openspec validate --strict` verde
      passam a ser enforçados, com asserção de **valor** onde o requisito fixa um, e o cenário de
      rejeição nomeia todos
- [x] 2.2 `specs/skills-catalog/spec.md` — MODIFIED *The rite gates evidence before it gates -> escrito; texto integral do requisito reproduzido
      quality*: a camada de forma, a regra por tipo de caixa, o relatório de densidade sem gate, e a
      ressalva de que forma não é verdade
- [x] 2.3 Confirmar que nenhum arquivo fora de `openspec/` foi tocado -> `git diff --cached --name-only master` lista 5 caminhos, todos sob `openspec/changes/record-shipped-gates/`

## 3. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo SKILL.md tocado — **não aplicável**: este change não toca -> confirmado pelo diff acima
      nenhum skill, e `git diff --name-only master` prova
- [x] Q.2 Todo conteúdo de skill tocado em inglês — **não aplicável** pelo mesmo motivo -> confirmado pelo diff acima
- [x] Q.3 Triggers da description testáveis e sem colisão — **não aplicável**, nenhuma description -> confirmado pelo diff acima
      muda
- [x] Q.4 Sem doutrina duplicada: o requisito de `skills-catalog` foi MODIFICADO em vez de um novo -> MODIFIED em vez de ADDED, decisão registrada no design
      ser criado ao lado, justamente para não duplicar doutrina sobre o mesmo assunto
- [x] Q.5 Exemplos de código em inglês — **não aplicável**, nenhum exemplo novo -> confirmado pelo diff acima

## 4. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate record-shipped-gates --strict` verde e `bash scripts/validate-rite.sh` -> `Change 'record-shipped-gates' is valid`; `rite gate OK` 3 passed 0 failed; `validate-rite-evidence.py` -> 0 findings sobre este próprio change
      verde, incluindo o `R1` sobre o grupo Evidence deste próprio change
- [x] V.2 Descoberta do catálogo intacta: 34 skills, `validate-skills.py` sem findings -> `validate-skills.py` 34 skills / 0 findings; selftest 13/13
- [x] V.3 Loop de CI completo verde e `./generate.sh && git diff --exit-code` limpo -> hygiene 0 findings; scan-secrets limpo; rite-evidence selftest 4/4; `./generate.sh && git diff --exit-code` limpo
- [x] V.4 `openspec archive record-shipped-gates --yes` -> `Totals: + 0, ~ 2, - 0` e `archived as '2026-08-15-record-shipped-gates'`
- [x] V.5 Depois do archive: o cenário de frontmatter nomeia `metadata.author` e `compatibility`
      (verificado por grep, 1 ocorrência). A outra asserção da issue — `validate-rite-evidence`
      aparecer em `openspec/specs/` — **não é atendida como escrita, e o critério é que estava
      errado**. O delta descreve o gate por comportamento ("enforced in shape", "per box kind",
      "presence, position and shape, and not the truth of the contents") sem citar o nome do script,
      que é a convenção deste repositório: `grep -rn "scripts/.*\.py" openspec/specs/*/spec.md`
      retorna **uma** ocorrência em todas as specs. O critério nasceu da mesma heurística de nome de
      arquivo que o E.3 deste change desmente. A substância — o gate está descrito nas specs — está
      atendida; a medida é que era ruim