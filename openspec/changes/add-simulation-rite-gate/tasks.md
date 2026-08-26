## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos abertos e lidos, não recordados, no commit `afa547e` (2026-08-26):
      `scripts/validate-rite.sh` (laço sobre changes ativas, regra de primeiro e último grupo),
      `scripts/validate-rite-evidence.py` (`_shape_ok`, `check_evidence_shape`, `CHECKS`, `DEFECTS`,
      `report_density`, KNOWN LIMIT 3), `openspec/schemas/skills-rite/schema.yaml`,
      `openspec/schemas/skills-rite/templates/tasks.md`, `.github/workflows/ci.yml` (passo
      "Claude plugin validation (best-effort)"), `openspec/specs/skills-catalog/spec.md`
- [x] E.2 Probes contra a versão instalada, 2026-08-26:
      `claude --version` -> `2.1.246 (Claude Code)`;
      `claude plugin validate . --strict` -> `✔ Validation passed`;
      `claude plugin validate <fixture> --strict` -> `✘ Validation failed (--strict treats warnings
      as errors)` com `❯ description: No description in frontmatter` — prova que o validador nativo
      inspeciona `SKILL.md` dentro do plugin;
      `claude plugin eval .` -> `` `plugin eval` is currently in early access `` (não roda nesta conta);
      `claude plugin details caveman` -> `Always-on: ~2,681 tok` — inventário e custo projetado
- [x] E.3 Não probado e registrado como pergunta aberta em design.md, nunca afirmado: a semântica
      exata do `--threshold` do `plugin eval`, o schema do `aggregate-result.json`, e o nome da
      variável de ambiente de early access. A referência embutida do produto não os declara, e o
      comando não pode ser executado aqui para medir.
- [x] E.4 Escopo: esta change entrega o gate do rito e liga o validador nativo que já roda. Listados
      como follow-up e **não** executados — (a) autorar suítes de `claude plugin eval`, bloqueado por
      early access; (b) `/skill-doctor`, mesmo gate; (c) medir o custo always-on do próprio catálogo
      com `claude plugin details`, que exige instalar o plugin localmente.

## 2. Grupo novo no schema e no template

- [x] 2.1 `openspec/schemas/skills-rite/templates/tasks.md`: grupo `Simulation & Field Proof
      (MANDATORY)` com `S.1`, `S.2`, `S.3`, imediatamente antes de `Quality Gates (MANDATORY)`
- [x] 2.2 `openspec/schemas/skills-rite/schema.yaml`: a instrução de tasks descreve o quinto gate e
      sua posição, ao lado dos quatro
- [x] 2.3 O comentário do template explica a forma que cada caixa deve, como o grupo de evidência já faz

## 3. Enforcement

- [x] 3.1 `scripts/validate-rite.sh`: presença do grupo vira estrutural, com erro nomeando arquivo e grupo
- [x] 3.2 `scripts/validate-rite-evidence.py`: `_simulation_shape_ok()` com as regras de `S.1`–`S.3`
- [x] 3.3 `check_simulation_shape()` registrado em `CHECKS`
- [x] 3.4 Três entradas novas em `DEFECTS`, uma por regra, no formato existente
- [x] 3.5 KNOWN LIMIT atualizado: sete tipos de caixa com regra, e a mesma incapacidade de detectar
      saída inventada

## 4. Validador nativo bloqueante

- [x] 4.1 `.github/workflows/ci.yml`: remover `continue-on-error: true` e `|| true` do passo de
      validação de plugin
- [x] 4.2 Pinar `@anthropic-ai/claude-code` na versão probada, com o motivo no comentário do passo
- [x] 4.3 Provado nos dois sentidos: verde neste repositório, vermelho no fixture controlado

## 5. Rito e documentação

- [x] 5.1 `skills/execute-backlog/SKILL.md` (+ `references/`): a simulação entra no plano de aprovação
      e na evidência do PR
- [x] 5.2 `README.md`: o rito passa a descrever cinco gates
- [x] 5.3 `./generate.sh` re-executado; espelhos idênticos

## 6. Simulation & Field Proof (MANDATORY)

<!-- O grupo que esta change introduz, preenchido por ela mesma. Forma exigida:
     S.1  ponto de entrada em `backticks` -> fragmento da saída OBSERVADA, ou declaração explícita
          de que a change não toca artefato de runtime
     S.2  a matriz medida em números (n/n)
     S.3  o que escapou ou se comportou diferente do esperado, ou "nada escapou" explícito -->

- [x] S.1 Gates exercitados contra diretórios de change sintéticos, numa cópia descartável do repo,
      2026-08-26. Change sem o grupo ->
      `::error::Missing mandatory group 'Simulation & Field Proof (MANDATORY)'`.
      Change com as três caixas infladas (`- [x] S.1 Simulei o gate e funcionou`) ->
      `rite evidence gate: 3 findings`, uma por regra:
      `R2 simulation shape — S.1 names no entry point and no observed output`,
      `R2 simulation shape — S.2 carries no counts`,
      `R2 simulation shape — S.3 neither names what escaped nor states that nothing did`.
      Change declarando ausência de runtime -> `rite evidence gate: 0 findings`.
      Validador nativo pinado: `claude plugin validate <fixture> --strict` ->
      `✘ Validation failed (--strict treats warnings as errors)`; `claude plugin validate . --strict`
      -> `✔ Validation passed`.
- [x] S.2 Matriz medida: 2/2 casos que deviam reprovar reprovaram (grupo ausente, caixas infladas);
      3/3 casos que deviam passar passaram (grupo correto no gate estrutural, grupo correto no gate
      de forma, declaração explícita de ausência de runtime); 7/7 classes de defeito detectadas pelo
      `--selftest`, sendo 3 novas (`R2 simulation shape: S.1/S.2/S.3`); 2/2 sentidos do validador
      nativo provados (vermelho no fixture, verde no repositório).
- [x] S.3 Um comportamento diferente do previsto, e mantido de propósito: `validate-rite.sh` não fixa
      a **posição** do grupo novo — ele só ancora primeiro e último grupo, então uma change que
      colocasse a simulação depois do Quality Gates passaria no gate estrutural. Está registrado no
      comentário do script e na D1 do design; fixar a posição exigiria mudar as âncoras existentes,
      o que está fora do escopo desta change. Nada mais escapou.

## 7. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado: `name` == diretório, descrição dobrada,
      `metadata.author: solvelab`, `metadata.version` semver bumpado, `category` no conjunto
      controlado, `license: MIT`, `compatibility` presente
- [x] Q.2 Todo conteúdo tocado do skill em inglês (locale do catálogo)
- [x] Q.3 Gatilhos da descrição testáveis e sem colisão com skill irmão; fronteira "Do NOT use for"
      presente onde há sobreposição
- [x] Q.4 Sem doutrina duplicada: o template aponta para `verify-before-claiming` e `bug-hunter` em
      vez de repetir o texto deles (design.md, tabela Canonical Home)
- [x] Q.5 Todo exemplo de código tocado usa identificadores, rotas, chaves e nomes de evento em
      inglês; termo mantido em outra língua carrega o motivo inline

## 8. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-simulation-rite-gate --strict` verde
- [x] V.2 Descoberta do catálogo intacta: `python3 scripts/validate-skills.py` verde, 34 skills
- [x] V.3 README / docs atualizados onde o rito muda
- [ ] V.4 `openspec archive add-simulation-rite-gate --yes` depois do merge do PR
