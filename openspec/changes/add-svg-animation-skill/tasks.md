# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `256e37d` (topo de `backlog/109-svg-animation-skill`) em 2026-08-31:

      - `research/svg-animation/method.md` — dez ensaios; a classificação dos defeitos sai daqui.
      - `research/svg-animation/measurements.md` — toda medição, com navegador, máquina e o que os
        números NÃO cobrem.
      - `research/svg-animation/scenes/scenes.js` — as cenas e criaturas medidas.
      - `skills/bug-hunter/SKILL.md` — forma do frontmatter (`metadata.category`).
      - `.github/workflows/ci.yml` — as barreiras que uma skill deste repositório atravessa.

- [x] E.2 Contagens conferidas por comando, não afirmadas

      `grep -c '^## ' research/svg-animation/method.md` -> `17`

      `ls skills/svg-animation/references/regimes/ | wc -l` -> `9`

      `for f in .../regimes/*.md; do grep -cE '^\| [0-9]+ \|' $f; done` -> `7 9 5 8 9 7 6 7 6`
      (advected-field 7 · articulated-body 9 · ballistic-ensemble 5 · dispersive-wave-field 8 ·
      driven-oscillator 9 · growth-structure 7 · orbital-bodies 6 · radiant-point-set 7 ·
      threshold-discharge 6)

- [x] E.3 Achados de plataforma copiados de medição versionada, não de memória

      `grep -n 'particles-svg\|particles-canvas' research/svg-animation/measurements.md` ->
      `62:| 13 | particles-svg | 56.7 | 60.0 | 122.64 | 466.40 |` e
      `63:| 14 | particles-canvas | 59.9 | 0 | 0 | 124.83 |`. São essas duas linhas que
      `references/platform.md` cita como 466 ms/s contra 125 ms/s. Nenhuma lacuna: todo número
      publicado na referência de plataforma tem linha correspondente em `measurements.md`.

- [x] E.4 Toda grandeza dos dossiês carrega fonte, e o que não tem fonte diz que não tem

      `grep -c 'assumed\|unknown' skills/svg-animation/references/objects/*.md` ->
      `broadleaf-tree.md:2 · herring-gull.md:1 · night-sky.md:1 · sea-turtle.md:2`.
      Follow-up registrado: a frequência de batida da gaivota e a mistura espectral do céu noturno
      seguem `assumed` porque não foi encontrada fonte citável; ficam marcadas até que se ache uma.

## 2. Construção

- [x] C.1 `skills/svg-animation/SKILL.md` — processo, roteador de regime e os três portões
- [x] C.2 `references/regimes/*.md` — nove esquemas
- [x] C.3 `references/platform.md` — custo medido e armadilhas
- [x] C.4 `references/objects/*.md` — oito dossiês mais o README de formato
- [x] C.5 Registro no catálogo: README, marketplace, `generate.sh` rodado

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 A skill exercitada pelo caminho real, num pedido que ela nunca viu

      Entrada: **"uma bandeira tremulando no vento"** — escolhida de propósito no mesmo regime da
      árvore (`driven-oscillator`) e em domínio completamente diferente. Se o esquema carrega, a
      tese da arquitetura vale; se não carrega, ela cai.

      `node shot.mjs research/svg-animation/simulations/flag.html fl.png 1200 700 1800` ->
      `fl.png written`, e na imagem: pano preso e liso no mastro, amplitude crescendo até a ponta
      livre, crista viajando do mastro para a ponta entre quadros consecutivos, dobra legível pelo
      sombreado. Correto na primeira tentativa.

- [x] S.2 Matriz de casos como números

      `grep -cE '^//   Q[0-9]' flag.html` -> `9`, ou seja 9/9 perguntas do esquema com veredicto
      escrito. `grep -oE '\[(measured law|derived)\]'` -> 4; `grep -o '\[assumed\]'` -> 5.

      Tinha de disparar: portão de perspectiva 1/1 (bandeira de perfil não mostra nada);
      procedência em grandeza sem fonte publicada 5/5, todas na entrega; veredicto escrito 9/9.

      Tinha de ficar em silêncio: esquemas de outros regimes 8/8 não carregados; esquemas novos
      necessários 0/1 — não existe esquema de "tecidos" e não fez falta.

- [x] S.3 O que escapou

      Escapou uma coisa, e a contagem foi o que pegou. Na primeira passada, 6 das 9 perguntas do
      esquema tinham veredicto escrito e 3 tinham sido puladas em silêncio — o mesmo defeito
      "processo sem critério de parada" que originou a skill inteira. `perguntas com veredicto: 6/9`
      antes, `9/9` depois. Corrigido no produto e não só na simulação: `SKILL.md` passa a exigir
      veredicto escrito em toda pergunta, inclusive `n/a because <reason>`. Ler o arquivo não teria
      pegado; contar pegou.

- [x] S.4 O que a simulação provou sobre a arquitetura

      A pergunta Q5 do esquema `driven-oscillator` — o driver é estocástico? — a árvore responde SIM
      e a bandeira responde NÃO. Bandeira é flutter: instabilidade auto-excitada, frequência de
      Strouhal `f = St·U/L` = 1,07 Hz a 8 m/s, com onda viajando do mastro para a ponta; a
      turbulência só modula. Mesmo esquema, resposta diferente, modelo diferente. E a Q3 — amplitude
      de cada taxa, com fonte — forçou a amplitude a crescer do mastro à ponta e a ser zero no
      vínculo, que é justamente o erro clássico de bandeira em SVG.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 `bash scripts/validate-rite.sh` -> `rite gate OK`
- [x] Q.2 `python3 scripts/validate-repo-hygiene.py` -> `repo hygiene: 0 findings`
- [x] Q.3 `openspec validate add-svg-animation-skill --strict` -> `is valid`
- [x] Q.4 `python3 scripts/validate-skills.py` -> `skills checked: 35   findings: 0`
- [x] Q.5 `python3 skills/code-locale/references/check-identifier-locale.py --selftest` -> `selftest OK`

## 5. Validation & Closure (MANDATORY)

- [x] V.1 Todo critério de aceitação de #109 com veredicto e a evidência que o sustenta
- [x] V.2 PR #110 com `Closes #109` e a tabela de evidência
- [ ] V.3 `openspec archive add-svg-animation-skill --yes` depois do merge
