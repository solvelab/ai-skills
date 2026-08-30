## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Caminhos locais abertos e lidos, com o commit em que foram lidos

      Lidos em `a8405ae` (topo de `master`) em 2026-08-30:

      - `generate.sh:1-15` — declara `skills/<name>/SKILL.md` como fonte única e lista os cinco
        destinos gerados (`claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/<group>/`).
      - `scripts/validate-repo-hygiene.py:29-31` — `COUNT_FILES = ("README.md",
        ".claude-plugin/marketplace.json")`, `COUNT_CLAIM = re.compile(r"\ball (\d+)\b")`.
      - `skills/r3f-animation/SKILL.md` — frontmatter `category: game`, `version: 1.2.0`, pin
        `three@0.185 · @react-three/fiber@9.7 · @react-three/drei@10.7 · react@19.2`.
      - `skills/r3f-animation/references/procedural-animation-patterns.md` — conteúdo é esqueleto e
        ossos (`skeleton.bones.find(b => b.name === 'Head')`, `headBone.rotation.y`).
      - `skills/documentation/references/templates.md:26-27` — as duas únicas ocorrências de `svg`
        no catálogo fora de `r3f`, ambas URLs de badge.
      - `openspec/specs/skills-catalog/spec.md` — capability alvo do delta.
      - `.github/workflows/ci.yml` — conjunto controlado de categorias e ausência de navegador no CI.

- [x] E.2 Ferramentas e comportamentos externos probados contra a versão instalada

      ```
      /home/diegops/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome --version
      -> Google Chrome for Testing 151.0.7922.34
      ```

      ```
      npx --yes playwright@latest --version
      -> Version 1.62.1
      ```

      ```
      grep -rniE '\bsvg\b' skills/*/SKILL.md skills/*/references/*.md | grep -v '^skills/r3f'
      -> skills/documentation/references/templates.md:26: [![CI](.../badge.svg)]...
      -> skills/documentation/references/templates.md:27: [![PyPI](.../package.svg)]...
      ```

      ```
      for p in plugins/*/; do echo "$(basename $p): $(ls -1 $p/skills | wc -l)"; done
      -> game: 12 | workflow: 7 | backend: 4 | devops: 3 | fivem: 2 | testing: 2
      -> docs: 1 | frontend: 1 | nui: 1 | tooling: 1
      ```

      Fontes externas lidas nesta rodada, com o que cada uma afirma:

      - `developer.chrome.com/blog/hardware-accelerated-animations` — "the current CSS properties
        that are hardware-accelerated by default only include `opacity`, `filter`, and `transform`";
        e "as of Chromium 89, Chrome will join the likes of Firefox to enable hardware-acceleration
        by default on SVG animations".
      - `chromium.googlesource.com/.../blink/renderer/core/animation/README.md` (`main`) — "A subset
        of style properties (currently transform, opacity, filter, and backdrop-filter) can be
        mutated on the compositor thread"; a decisão passa por
        `CheckCanStartAnimationOnCompositor()`. **Nenhuma menção a SVG no documento atual.**
      - `motion.dev/magazine/web-animation-performance-tier-list` — classifica animação de atributo
        SVG nativo (`d`, `cx`, `cy`, `r`) como C-Tier, disparando repaint por frame, e recomenda
        `transform` onde possível.
      - `w3.org/TR/SVG2/animate.html` — lista cinco formas de animar SVG (elementos de animação,
        CSS Animations, CSS Transitions, SVG DOM, Web Animations API) e afirma que "SVG does not
        mandate support for any of these animation methods".
      - GSAP: licença passou a gratuita, incluindo os plugins antes pagos (MorphSVG, DrawSVG,
        SplitText, ScrollTrigger, Inertia), a partir de 2025-04-30, sob a Webflow.

- [x] E.3 O que não pôde ser probado nesta rodada

      **A pergunta central segue aberta e é o objeto do trabalho:** se, no Chromium atual, uma
      animação de `transform` sobre elemento SVG roda na thread de composição. As três leituras se
      contradizem — o blog do Chrome diz que sim desde a 89; o `README.md` do Blink na tag 85 dizia
      que não; o `main` de hoje não menciona SVG. Ausência de menção não é prova de remoção da
      limitação. Fica registrado como pergunta aberta em `design.md` e será resolvido por medição,
      não por citação.

      Não probado ainda, e explicitamente pendente do grupo 2: custo real de `feTurbulence` e
      demais filtros; limiar de contagem de nós em que SVG perde para Canvas em partículas;
      comportamento de `prefers-reduced-motion` medido em vez de citado; custo comparado das
      técnicas de morphing. Nenhuma dessas entra no relatório como afirmação antes de ser medida.

      A qualidade das fontes secundárias encontradas na primeira busca é baixa (`svgai.org`,
      `zigpoll`, `boundev` têm marcas de conteúdo gerado em escala); nenhuma delas é usada como
      lastro. Registrado aqui para que a ausência delas no relatório não pareça descuido.

- [x] E.4 Checagem de escopo

      A change faz só o que o item #107 pediu: registra a regra sobre prova executável e hospeda a
      pesquisa. Notados pelo caminho e **não** feitos:

      - O plugin `frontend` tem uma única skill (`react-api-client`); se a decisão apontar para
        `frontend`, o grupo passa a duas. Redimensionar plugins não é assunto deste item.
      - `skills/r3f-animation/references/procedural-walk-cycle-bipedal-character.md` tem material
        de ciclo de caminhada que provavelmente se generaliza para 2D. Promover isso é decisão do
        item seguinte, não desta change.
      - O CI não valida HTML nem roda navegador. Se protótipos passarem a merecer gate, é item
        próprio.

## 2. Pesquisa, medição e decisão

- [x] 2.1 `research/svg-animation/` criado, fora de `skills/`, sem mover contagem publicada
- [x] 2.2 Harness de medição reexecutável: um comando abre o protótipo no Chrome for Testing
      151.0.7922.34 via Playwright 1.62.1, coleta tempo de frame por `requestAnimationFrame` e
      contadores de estilo/layout por CDP `Performance.getMetrics`, e imprime o resultado
- [x] 2.3 Protótipos comparativos do item, cada um autocontido e executável abrindo um arquivo:
      atributo SVG vs `transform`; CSS vs JavaScript; muitos nós vs `<defs>`/`<use>`; filtros SVG vs
      alternativa mais barata; SVG vs Canvas para partículas; duas técnicas de morphing; duas formas
      de onda natural
- [x] 2.4 A pergunta aberta de E.3 resolvida por medição — ou reportada como não resolvida, com o
      que foi tentado
- [x] 2.5 Catálogo de primitivas, cada uma com custo medido ou custo declarado como não medido
- [x] 2.6 Modelo de composição demonstrado em 6-8 cenas modelo cobrindo os casos difíceis
- [x] 2.7 Decisão arquitetural escrita: skill nova, skill existente ou divisão; nome,
      `metadata.category`, plugin de destino, esboço de seções, alternativas rejeitadas com razão
- [x] 2.8 Showcase publicado como Artifact, renderizando os mesmos protótipos versionados, com a
      técnica nomeada ao lado de cada cena e o comportamento sob `prefers-reduced-motion`

## 3. Simulation & Field Proof (MANDATORY)

- [x] S.1 Protótipos e harness exercitados pelo caminho real — navegador de verdade — com a saída
      observada registrada

      O harness roda o Chrome de verdade e mede. Saída da rodada final, íntegra em
      `research/svg-animation/measurements.md`:

      ```
      node measure.mjs --all --ms 5000
      -> browser: Google Chrome for Testing 151.0.7922.34
      -> label                            fps   presentedFps  layoutPerSec  taskMsPerSec
      -> 00-baseline-static               37.3  0.2           0             4.02
      -> 04-transform-css-html            36.8  59.9          0             65.15
      -> 03-transform-css-svg             36.8  59.9          37.0          60.07
      -> 08-layers-svg-element-transform  36.8  60.0          0             8.91
      -> 07-layers-group-transform        37.2  59.9          37.4          10.97
      -> 13-particles-svg                 59.8  56.7          60.0          466.40
      -> 14-particles-canvas              60    59.9          0             124.83
      ```

      As cenas foram abertas em navegador e **olhadas**, não só contadas:

      ```
      node probe.mjs scenes/index.html "figuras, animações"
      -> "8 figures, 757 animations"
      ```

      E capturadas em imagem para julgamento visual — foi assim que os dois defeitos de S.3
      apareceram. O showcase publicado renderiza as mesmas cenas:
      <https://claude.ai/code/artifact/f92ae439-2e51-4977-8f6f-acb481a0c031>

      Suporte de `d: path()` probado em vez de presumido, porque a medição do protótipo 16 só vale
      se a propriedade de fato animou:

      ```
      node probe.mjs prototypes/16-morph-css-path.html "..."
      -> {"animations":1,"computedD":"path(\"M 154.745 120 C 154.491 130.689 14","supported":true}
      ```

- [x] S.2 Matriz de casos medida, em contagens

      | Expectativa | Casos | Resultado |
      |---|---|---|
      | Protótipos que tinham de rodar e rodaram | 19/19 | rodada `--all`, nenhum erro |
      | Cenas que tinham de construir e construíram | 8/8 | 757 animações ativas |
      | Protótipos que sustentaram 60 fps compostos | 18/19 | único fora: `13-particles-svg` a 56.7 |
      | Pares comparativos que deram diferença mensurável | 7/7 | canal, camada, nós, filtro, partícula, morph, onda |
      | Temas do showcase que resolveram corretamente | 2/2 | claro e escuro, capturados |
      | Defeitos visuais achados por olhar o render | 3 | ver S.3 |

- [x] S.3 O que escapou, não pôde ser medido ou se comportou diferente do esperado

      **Três defeitos que só o render revelou**, todos corrigidos e registrados como doutrina:

      1. `transform-origin` em SVG começa em `0 0`, não no centro — o halo do sol saiu deslocado do
         sol. Corrigido com `transform-box: fill-box`; virou `report.md` §7b.
      2. `transform-box: fill-box` reinterpreta as coordenadas dentro do **atributo** `transform` —
         todas as folhas da árvore foram atiradas para fora da copa no instante em que a regra 1
         entrou. Corrigido por escopo; mesma seção.
      3. As legendas continham `<svg>` literal e, inseridas como HTML, engoliram o resto da frase.
         Corrigido com escape; a razão está inline no código.

      Nenhum dos três é achável lendo. Selftest verde e contagem de nós verde teriam passado por
      cima dos três.

      **O que não pôde ser medido**, declarado em vez de preenchido com substituto plausível:

      - Se filhos de SVG são compostos fora da main thread no Chromium atual. Três fontes primárias
        se contradizem; a medição resolve a questão de **layout** e não alcança a de composição,
        porque o domínio `Performance` do CDP não expõe contador de paint nem de raster — verificado
        contra este build, a lista tem `LayoutCount` e `RecalcStyleCount` e nada de paint.
      - Onde filtros animados quebram. O ponto de ruptura não foi procurado.
      - Qualquer coisa sobre Firefox, Safari ou telefone. Um motor, uma máquina, raster por software.

      **Limitação do harness que quase virou conclusão errada**: a coluna `fps` do amostrador rAF é
      artefato em headless — a página estática marca 37 e as ocupadas marcam 60, porque o Chrome
      afrouxa o rAF quando nada agenda trabalho. O sinal de throughput é `presentedFps`, e o
      baseline a **0.2** é a prova de que essa coluna mede o que diz.

## 4. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniforme em todo `SKILL.md` tocado — **não se aplica**: nenhuma skill é criada
      ou editada
- [x] Q.2 Conteúdo de skill tocado em inglês — **não se aplica** pelo mesmo motivo; o delta desta
      change está em inglês, como o catálogo exige
- [x] Q.3 Gatilhos de descrição testáveis — **não se aplica**: nenhuma descrição de skill muda
- [x] Q.4 Sem doutrina duplicada: a doutrina de pesquisa antes de afirmar é aplicada e linkada a
      `verify-before-claiming`, não reescrita; ver a tabela de Canonical Home em `design.md`
- [x] Q.5 Identificadores em inglês no que a change introduz — nomes de diretório, de arquivo e das
      primitivas — conforme o glossário da issue #107 e `code-locale`

## 5. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate add-svg-animation-research --strict` verde
- [x] V.2 Descoberta do catálogo intacta: contagem de skills inalterada em `README.md` e
      `.claude-plugin/marketplace.json`, sem órfão ou renomeado
- [x] V.3 README / docs atualizados onde a change altera composição ou uso do catálogo — a avaliar
      no fecho: a change não cria skill, mas cria diretório novo de primeiro nível
- [ ] V.4 `openspec archive add-svg-animation-research --yes` depois que todos os grupos acima
      estiverem `[x]`
