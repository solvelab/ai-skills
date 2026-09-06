## 1. Evidence & Sources (MANDATORY)

<!-- Sempre o PRIMEIRO grupo: sondar antes de escrever. Registrar o COMANDO e um fragmento da SAÍDA
     CRUA, nunca uma conclusão. -->

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      No `solvelab/ai-skills`, lidos em `85c453d` (topo de `master`, 2026-09-05):

      - `skills/documentation/SKILL.md` — 185 linhas; `metadata.version: 3.0.3` na linha 13; a linha
        *Extract the facts* em `:36-37`, enumerando env var, endpoint, comando e porta do compose.
      - `skills/documentation/references/templates.md` — 366 linhas; *Setup guide conventions* em
        `:219-230`, com "Prerequisites as `- [ ]` checkboxes" em `:222` e "Verify after every step…
        the output it should print" em `:223-224`.
      - `openspec/config.yaml` — `schema: skills-rite`; a regra "Never write a doctrine line whose
        evidence is not recorded in the Evidence & Sources group".
      - `openspec/specs/skills-authoring/spec.md` — 16 requisitos; *Single canonical home per rule*
        (`:11`), *Prescribed numbers carry the rule that produces them* (`:146`), *Checklists are
        scored against field defects* (`:349`).
      - `scripts/validate-rite.sh` e `scripts/validate-rite-evidence.py` — as quatro posições
        obrigatórias e as formas E.1-E.4 / S.1-S.3.
      - `openspec/changes/archive/2026-08-06-harden-documentation-skill/design.md` — decisões `D3`
        (checabilidade) e `D7` (esqueletos para `references/`).

      No `solvelab/feldt`, lidos em `1975ada` (topo de `main`, 2026-09-05):

      - `docs/SETUP.md` — §1 *Pré-requisitos* com quatro caixas e o bloco `### Confira o cluster`.
      - `deploy/feldt.yaml` — `storage: 1Gi` (`:39`), `nodePort: 30080` (`:63`) e `30081` (`:88`),
        `runAsUser`/`fsGroup: 65532` (`:113-114`), `cpu: 50m`/`memory: 128Mi` (`:155-156`),
        `limits` `200m`/`256Mi` (`:158-159`), `readOnlyRootFilesystem: true` (`:162`).
      - `deploy/standalone/README.md` — §1, com a tabela de três leituras do mesmo `curl`.

- [x] E.2 Ferramentas e fontes externas sondadas: comando -> fragmento da saída

      - `grep -rniE 'kubernetes 1\.|k8s 1\.|kubectl 1\.|versão mínima|minimum version' docs/ README.md deploy/ AGENTS.md`
        no feldt -> nenhuma linha (saída vazia; o `echo '(fim)'` seguinte foi a única coisa impressa).
      - `sed -n '/^## 1\. Pré-requisitos/,/^## 2\./p' docs/SETUP.md` ->
        `# Esperado: um bloco JSON com clientVersion e serverVersion`.
      - `grep -nE 'resources|memory|cpu|requests|limits|containerPort|nodePort|fsGroup|runAsUser' deploy/feldt.yaml`
        -> `155:              cpu: 50m` e `156:              memory: 128Mi`.
      - `openspec --version` -> `1.6.0`.
      - `openspec validate update-documentation-prerequisites --strict` ->
        `Change 'update-documentation-prerequisites' is valid`.
      - Fontes externas, por requisição: `https://docs.k3s.io/installation/requirements` -> seções
        *Architecture*, *Operating Systems*, *Hardware* (`"2 cores"` e `"2 GB"` para server, `"1 core"`
        e `"512 MB"` para agent) e *Networking* (`"port 6443"`, `"8472"`, `"51820/51821"`).
      - `https://grafana.com/docs/grafana/latest/setup-grafana/installation/` -> mínimos
        `"512 MB"` de memória, `"1 core"` de CPU, disco de 10-50 GB por porte; SO suportados;
        bancos `"SQLite 3"`, `"MySQL 8.0+"`, `"PostgreSQL 12+"`; navegadores Chrome, Firefox, Safari,
        Edge, com "JavaScript must be enabled".
      - `https://www.thegooddocsproject.dev/template/installation-guide` -> a seção *Before you begin*
        pede `"Necessary dependencies or packages"`, `"Required version for your system or other
        system requirements"` e `"Specialist knowledge or skills"`.
      - `https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/required-rbac-permissions` e
        `https://docs.portainer.io/start/install-ce/server/kubernetes/baremetal` -> permissões RBAC e
        StorageClass default como pré-requisitos declarados.

- [x] E.3 O que não deu para sondar

      Não foi possível abrir o `didevlab/housek8s`, que guarda o manifesto vivo do feldt: o
      repositório não está clonado nesta máquina e o acesso não foi testado. Isso não afeta a doutrina
      deste change — os números vêm do espelho `deploy/feldt.yaml`, que o CI do feldt exige idêntico
      ao vivo, byte a byte, no step *Atualizar a tag nos dois manifestos*. Também não foi sondado
      nenhum cluster: as afirmações sobre StorageClass e RBAC vêm das fontes externas citadas em E.2,
      não de medição própria, e entram no esqueleto como categoria a documentar, nunca como número.

- [x] E.4 Escopo e desdobramentos

      Dois desdobramentos ficam registrados e fora deste change. **Primeiro:** o `docs/SETUP.md` §1 do
      feldt continua com as nove lacunas medidas; corrigi-lo aqui confundiria a prova com o conserto,
      então vira item no repositório dele. **Segundo:** o requisito autoral novo provavelmente tem
      violações em outras skills do catálogo — a varredura por "verificação prescrita sem valor de
      aprovação" nas 35 skills não foi feita, e abre item próprio se achar mais de um caso.

## 2. Doutrina no SKILL.md

- [x] 2.1 A linha *Extract the facts* passa a nomear o manifesto de implantação como fonte de
      recursos, armazenamento, portas, identidade e modo de filesystem
- [x] 2.2 Regra do valor que aprova, com a razão de uma verificação sem critério não verificar
- [x] 2.3 Regra do egress como pré-requisito, com a razão de a falha dele ser silenciosa
- [x] 2.4 `metadata.version` `3.0.3` -> `3.1.0`

## 3. Esqueleto no references/templates.md

- [x] 3.1 Lista de categorias de pré-requisito nas convenções do `docs/SETUP.md`, cada uma com a
      fonte externa que a pede e marcada como condicional quando não se aplica a todo produto
- [x] 3.2 Forma de tabela de diagnóstico para sintoma único com remédios opostos

## 4. Simulation & Field Proof (MANDATORY)

- [x] S.1 O artefato foi exercitado pelo seu ponto de entrada real; o comando e um fragmento da saída
      observada estão registrados

      O artefato é doutrina, e o ponto de entrada dela é alguém aplicando a doutrina a um repositório
      real. Aplicada em rascunho ao `solvelab/feldt` em `1975ada`, **sem commitar nada lá**:

      - entry point: as dez categorias do esqueleto novo caminhadas contra `docs/SETUP.md` §1, com
        `re.search` por categoria e fronteira de palavra -> `categorias cobertas: 1/10   ausentes: 9/10`
      - entry point: as mesmas categorias cruzadas com `deploy/feldt.yaml` -> `Compute NÃO` com
        `cpu: 50m, memory: 128Mi, limits`; `Storage NÃO` com `storage: 1Gi`;
        `Identity and permissions NÃO` com `runAsUser: 65532, fsGroup: 65532`
      - entry point: `bash generate.sh` -> `Generated wrappers for 35 skills:` e
        `Generated 10 category plugins in plugins/`
      - entry point: `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`
      - entry point: `bash scripts/validate-rite.sh` -> `rite gate OK`

- [x] S.2 Matriz de casos medida, como contagens

      Doutrina contra o campo: 10/10 categorias caminhadas; 1/10 coberta pelo `docs/SETUP.md` §1 do
      feldt (Dependencies); 9/10 ausentes — e 3 delas com o dado já escrito no `deploy/feldt.yaml`,
      dois diretórios ao lado. As nove batem, uma a uma, com as nove lacunas medidas antes de a regra
      existir: a regra reproduz o achado em vez de inventar outro.

      Regra do valor que aprova: 12 verificações prescritas com `# Esperado:` em `docs/SETUP.md`;
      1/12 confirmada sem valor de aprovação (`um bloco JSON com clientVersion e serverVersion`);
      3/4 marcações da heurística derrubadas na conferência à mão (ver S.3); 8/12 não marcadas.

      Portões do repositório: 35/35 skills sem achado; 22/22 classes de defeito detectadas pelo
      selftest do validador; 4/4 pelo selftest de higiene; 12/12 padrões de segredo; 17/17 casos do
      smoke de distribuição; 6/6 links externos novos em `200`; 0/1 change ativa com achado no rito.

- [x] S.3 O que escapou ou se comportou diferente do esperado

      Duas coisas, e as duas são o mesmo defeito que este change corrige — um instrumento cujo
      resultado esperado é satisfeito por algo que não é o fato medido.

      **Primeira:** a primeira rodada da simulação devolveu `Compute SIM`, contradizendo o que já se
      sabia. O marcador `RAM` casava dentro de **Tele*gram***, na linha do destino de alerta. Com
      fronteira de palavra a categoria volta a `NÃO`, e a contagem passa de `2/10` para `1/10`. O
      número que não fechava era do instrumento, não do campo.

      **Segunda:** a heurística que procura verificação sem valor de aprovação marcou 4 linhas e 3
      caíram na conferência à mão — `qualquer código HTTP, rápido — um 404 já prova o caminho` **é**
      um critério; `uma linha "kind":"lost" … "kind":"recovered"` nomeia strings exatas; `uma linha
      com a senha` aprova pela existência da linha. Sobra 1 defeito real em 12. Isso é medição direta
      da decisão `D3` do `design.md`: um detector sobre prosa erra nos dois sentidos, e é por isso que
      o requisito autoral novo entra declaradamente sem validador.

## 5. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado
      Evidência: o loop do `ci.yml` replicado sobre `skills/*/SKILL.md` -> `frontmatter fail=0 sobre
      35 skills`; `metadata.version: 3.1.0` na `documentation`, semver, `author: solvelab`,
      `category: docs` no conjunto controlado, `license: MIT`, `compatibility` presente,
      `name` == diretório, description em `>-`.
- [x] Q.2 Todo conteúdo de skill tocado em inglês (locale do catálogo)
      Evidência: as três regras novas do `SKILL.md` e o bloco novo do `templates.md` são inglês;
      `python3 skills/code-locale/references/check-identifier-locale.py --selftest` -> `selftest OK: 7
      content tiers fire, 16 clean cases stay silent`; `python3 scripts/validate-skills.py` ->
      `skills checked: 35   findings: 0`, que inclui a checagem de locale do catálogo.
- [x] Q.3 Gatilhos da description testáveis e sem colisão com skill irmã
      Evidência: `git diff master -- skills/documentation/SKILL.md | grep -cE '^[-+] *description'` ->
      `0`; nenhum gatilho se moveu, e a description já dispara em "SETUP" e "install". A cláusula
      "Do NOT use for non-software documentation tasks" continua no lugar.
- [x] Q.4 Sem doutrina duplicada
      Evidência: a regra do egress termina apontando `backend-resilience` para o comportamento em
      runtime, em vez de repeti-lo; a escada de pesquisa continua só em `verify-before-claiming`; a
      tabela Canonical Home do `design.md` tem sete linhas, três `establish here (new)`, duas
      `link (already canonical)`, uma `already canonical` e uma `spec delta`.
- [x] Q.5 Todo exemplo de código em skill tocada usa identificador em inglês
      Evidência: o único bloco novo é a tabela de diagnóstico do `templates.md`, em markdown, com
      `--max-time` e códigos HTTP — sem identificador de código; detector de locale -> `findings: 0`.

## 6. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate --strict` verde e `validate-rite.sh` verde
      Evidência: `openspec validate update-documentation-prerequisites --strict` ->
      `Change 'update-documentation-prerequisites' is valid`; `bash scripts/validate-rite.sh` ->
      `rite gate OK`.
- [x] V.2 Descoberta do catálogo intacta
      Evidência: `ls -d skills/*/ | wc -l` -> `35`, o mesmo de antes; nenhuma skill criada, removida
      ou renomeada; `bash generate.sh` -> `Generated wrappers for 35 skills` e `10 category plugins`;
      `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`, que inclui a coerência
      das contagens publicadas.
- [x] V.3 README e docs atualizados onde o change altera composição ou uso
      Evidência: o change não altera composição nem uso do catálogo — nenhuma skill entra, sai ou muda
      de nome, e nenhuma contagem publicada se move. `README.md` intocado de propósito;
      `python3 scripts/validate-repo-hygiene.py --selftest` -> `4/4 defect classes detected`, e o
      check H2 é justamente o que reprovaria uma contagem defasada.
- [ ] V.4 `openspec archive update-documentation-prerequisites --yes` depois do merge do PR
