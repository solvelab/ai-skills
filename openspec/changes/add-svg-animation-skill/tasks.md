# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 A classificação dos ~25 defeitos por tipo de conhecimento sai de
      `research/svg-animation/method.md` (dez ensaios) e `measurements.md`, ambos versionados
      neste repositório. Comando e saída registrados abaixo.
- [x] E.2 Cada pergunta obrigatória de cada esquema de regime cita o defeito medido que a originou,
      com o número. Nenhuma pergunta entra por parecer boa ideia.
- [x] E.3 Os achados de plataforma (`references/platform.md`) vêm de `measurements.md`, que nomeia
      o navegador, a máquina e o que os números NÃO cobrem.
- [x] E.4 Os dossiês de objeto citam a fonte de cada número; número sem fonte é marcado `assumed`.

### Evidência registrada

```
$ python3 scripts/validate-skills.py       -> skills checked: 35   findings: 0
$ python3 scripts/validate-repo-hygiene.py -> repo hygiene: 0 findings
$ openspec validate add-svg-animation-skill --strict -> valid
$ bash scripts/validate-rite.sh            -> rite gate OK

esquemas publicados: 9      perguntas obrigatórias por esquema: 5 a 9
  advected-field 7 · articulated-body 9 · ballistic-ensemble 5 · dispersive-wave-field 8
  driven-oscillator 9 · growth-structure 7 · orbital-bodies 6 · radiant-point-set 7
  threshold-discharge 6
dossiês semeados: 8 + README de formato
```

### Simulação end-to-end — `research/svg-animation/simulations/flag.html`

Pedido que a skill nunca viu: **"uma bandeira tremulando no vento"**. Escolhido de propósito:
mesmo regime da árvore (`driven-oscillator`), domínio completamente diferente. Se o esquema
carrega, a tese da arquitetura vale; se não carrega, ela cai.

```
regimes carregados                 1  (driven-oscillator)
esquemas novos necessários         0  — não existe esquema de "tecidos" e não fez falta
perguntas com veredicto escrito    9/9  (6 respondidas, 3 com "n/a porque…")
grandezas marcadas measured/derived  4
grandezas marcadas assumed           5  — todas aparecem no arquivo entregue
portão de perspectiva disparou       1  — bandeira de perfil não mostra nada; vista fixada
resultado                          correto na primeira tentativa
```

**O que a simulação provou.** A pergunta Q5 do esquema — *o driver é estocástico?* — a árvore
responde SIM e a bandeira responde NÃO: bandeira é flutter, instabilidade auto-excitada com
frequência bem definida (Strouhal `f = St·U/L`, 1,07 Hz a 8 m/s) e uma onda VIAJANDO do mastro
para a ponta; a turbulência só modula. Mesmo esquema, resposta diferente, modelo diferente. E a
Q3 — *amplitude de cada taxa, com fonte* — forçou a amplitude a crescer do mastro até a ponta e a
ser zero no mastro por vínculo, evitando amplitude uniforme, que é o erro clássico de bandeira.

**O que a simulação achou de errado na própria skill.** Contando as perguntas, 6 das 9 tinham
veredicto e 3 tinham sido puladas em silêncio — o mesmo defeito "processo sem critério de parada"
que originou a skill. Corrigido no `SKILL.md`: toda pergunta recebe veredicto escrito, inclusive
`n/a porque <razão>`. Só contar pegou isso; ler não teria pegado.

## 2. Construção

- [x] C.1 `skills/svg-animation/SKILL.md` — processo, roteador de regime e os três portões
- [x] C.2 `references/regimes/*.md` — um esquema por regime
- [x] C.3 `references/platform.md` — custo medido e armadilhas
- [x] C.4 `references/objects/*.md` — dossiês semeados a partir do que já foi construído
- [x] C.5 Registro no catálogo conforme o rito do repositório

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 A skill é exercitada pelo CAMINHO REAL num pedido que ela nunca viu, do zero, e o
      resultado é registrado — não basta ler a skill e declarar que funcionaria.
- [x] S.2 O portão de perspectiva é exercitado num pedido cujo eixo do mecanismo não aparece na
      vista pedida, e a skill tem de perguntar em vez de escolher.
- [x] S.3 O portão de procedência é exercitado numa grandeza sem valor publicado, e o `assumed`
      tem de aparecer na saída.
- [x] S.4 Contagens medidas da simulação registradas aqui, não impressões.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 `bash scripts/validate-rite.sh` verde
- [x] Q.2 `python3 scripts/validate-repo-hygiene.py` sem achados
- [x] Q.3 `openspec validate add-svg-animation-skill --strict` verde
- [x] Q.4 Validador de catálogo/plugin do repositório verde
- [x] Q.5 `code-locale`: prosa em português, identificadores e caminhos em inglês

## 5. Validation & Closure (MANDATORY)

- [x] V.1 Todo critério de aceitação de #109 recebe veredicto, com a evidência que o sustenta
- [x] V.2 PR com `Closes #109` e a tabela de evidência
- [ ] V.3 `openspec archive add-svg-animation-skill --yes` depois do merge
