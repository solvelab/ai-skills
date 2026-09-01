## Context

O item #107 pede pesquisa profunda sobre animação SVG e uma decisão sobre onde esse conhecimento
mora. A decisão precisa ser tomada com prova, e a prova precisa de lar.

Estado do repositório, lido em `a8405ae`:

- 34 skills. Cobertura de SVG: duas URLs de badge em
  `skills/documentation/references/templates.md:26-27`.
- `skills/r3f-animation/` (`category: game`, v1.2.0) cobre animação em React Three Fiber. Seu
  `references/procedural-animation-patterns.md` é esqueleto/ossos em three.js; seu
  `references/procedural-walk-cycle-bipedal-character.md` é a coisa mais próxima de uma receita de
  movimento que o catálogo tem, e é 3D, presa a framework e fixada em
  `three@0.185`/`@react-three/fiber@9.7`.
- `plugins/`: `game` tem 12 skills, `frontend` tem 1 (`react-api-client`), `nui` tem 1.
- `generate.sh:1-15` declara a fonte única: `skills/<name>/SKILL.md`. `claude/`, `codex/`,
  `cursor/`, `copilot/` e `plugins/` são todos gerados a partir dela.
- `scripts/validate-repo-hygiene.py:29-31` afere a contagem publicada (`all N`) em `README.md` e
  `.claude-plugin/marketplace.json` contra o número de diretórios em `skills/`.

Ferramental disponível para medir, probado nesta máquina:

```
/home/diegops/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome --version
-> Google Chrome for Testing 151.0.7922.34
npx playwright --version
-> Version 1.62.1
```

## Goals / Non-Goals

**Goals:**

- Dar lar a prova executável, de modo que uma alegação de custo do catálogo possa ser reexecutada
  por quem revisa.
- Fixar que medição publicada carrega método e ambiente.
- Manter o pacote entregue aos consumidores exatamente como está.

**Non-Goals:**

- Escrever a skill de animação SVG. Esta change registra a regra e hospeda a pesquisa; a skill é
  item seguinte, aberto depois que a decisão existir.
- Transformar os protótipos em suíte de teste mantida. Eles são evidência datada, não regressão.
- Rodar navegador no CI. A medição é feita e registrada por quem executa; o CI continua sem
  navegador.

## Decisions

### D1 — A prova vive fora de `skills/`

`research/<assunto>/`. Razão verificada, não estética: `generate.sh:1-15` lê apenas
`skills/<name>/SKILL.md` e gera todo o resto a partir dela. Um diretório fora de `skills/` fica
versionado, revisável e reexecutável sem entrar em nenhum plugin — o consumidor que habilita
`ai-skills-frontend` não baixa protótipo nenhum.

A alternativa considerada era `skills/<nome>/examples/`. Rejeitada por duas razões: embarcaria os
protótipos em todo consumidor do plugin, e exigiria que a skill já existisse — o que inverteria a
ordem, porque é a pesquisa que decide se a skill deve existir.

### D2 — Alegação de custo exige lastro nomeado

Um número de performance no catálogo passa a precisar de um artefato reexecutável neste
repositório ou de um benchmark publicado nomeado. Sem nenhum dos dois, a alegação sai.

Isso não é rigor decorativo. O caso que originou a regra: o blog do Chrome diz que animações SVG
têm aceleração por hardware por padrão desde o Chromium 89; o `README.md` de
`blink/renderer/core/animation` na tag 85 dizia que o Chromium não compõe animações de elementos
com transform SVG; e no `main` de hoje a frase sobre SVG não está mais lá. Três leituras, nenhuma
conclusiva, sobre o fato mais repetido da área. A saída é medir.

### D3 — Medição carrega método

Toda medição registrada declara o que foi medido, como, em qual navegador e versão, e em que
classe de dispositivo. Um número sem método não é reexecutável e, portanto, não é evidência — é
uma alegação com aparência de dado.

### D4 — O showcase é vista, não implementação

A demonstração publicada renderiza os mesmos protótipos versionados. Divergiu, o repositório
vence, porque é a cópia que sobrevive ao link. O showcase existe para que a qualidade visual seja
julgada olhando, não lendo — uma técnica que fica mecânica na tela não é recomendada por melhor
que seja seu número.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Pesquisar antes de afirmar; rotular verificado/inferido/desconhecido; relatar o que não se achou | `verify-before-claiming` | already canonical — a change aplica a doutrina e não a reescreve |
| Prova observada, não esperada, antes de declarar entrega | `verify-before-claiming` | already canonical — citada no grupo de simulação de `tasks.md` |
| Um check declara o que não cobre | `skills-catalog` (spec do repositório) | already canonical — o relatório declara o alcance de cada medição |
| API externa versionada é fixada | `skills-authoring` (*Versioned external APIs are pinned*) | already canonical — toda alegação sobre biblioteca de animação leva versão |
| Bloco de código roda como escrito ou é marcado como excerto | `skills-authoring` (*Code blocks compile or are marked*) | already canonical — vale para os protótipos e para o relatório |

Nenhuma skill é editada por esta change, então não há doutrina duplicada a mover.

## Risks / Trade-offs

- **O diretório de pesquisa vira depósito.** Mitigação: a regra é sobre lastro de alegação, não
  sobre guardar rascunho; o que não sustenta uma afirmação publicada não pertence ali.
- **Os protótipos apodrecem**, porque nada os exercita depois. Trade-off aceito e declarado: são
  evidência datada no momento da medição, não suíte mantida. O relatório diz isso em vez de
  fingir cobertura contínua.
- **A medição é presa a um ambiente** e pode ser lida como universal. Mitigação: D3 obriga
  navegador, versão e classe de dispositivo dentro de cada número.
- **O link do showcase morre.** Mitigação: D4 — o repositório é o artefato de registro.

## Open Questions

Uma, e ela é o objeto da pesquisa, não um buraco no desenho: se elementos SVG animados por
`transform` são compostos fora da main thread no Chromium atual. As três leituras disponíveis se
contradizem (ver D2). A resposta sai da medição, e o que a medição não alcançar entra no relatório
como não sabido, com o comando que foi tentado.
