# Design — endurecer o validador de agentes

## Context

`scripts/validate-agents.py` nasceu no PR #202 com A1–A7 e `selftest-validate-agents.py` com 22
casos, que cobrem o caminho de conteúdo: campo ausente, YAML quebrado, nome fora do padrão, limites,
`tools` mal declarado, corpo curto, seção ausente, subdiretório e órfão.

O que ele não cobria é o caminho de **entrada malformada** e o de **valor nulo**, e foi isso que o
`bug-hunter-analyst` atacou. Oito achados, dois deles falso verde.

## Goals / Non-Goals

**Goals:**

- Nenhum falso verde: um campo obrigatório sem valor reprova, e a checagem de órfão roda mesmo quando
  o diretório canônico sumiu.
- Nenhuma entrada de arquivo termina a execução por exceção; cada uma vira achado nomeado e os demais
  agentes continuam sendo checados.
- Uma decisão escrita para cada ponto onde hoje há comportamento não declarado.
- Um caso de selftest por defeito, cada um declarando o check que deve provocar.

**Non-Goals:**

- Transformar erro de ambiente em achado silencioso. Cada tratamento nomeia o caminho e o exit
  continua não-zero.
- Cobrir as seis linhas de ataque que não produziram nada. Ficam registradas como já examinadas.
- Mexer em agente, skill, `generate.sh`, H4 ou README.

## Decisions

**D1 — Presença é valor, não chave.** `field not in meta` vira um teste de valor nulo. É a correção
mínima que fecha o achado 1 inteiro, incluindo `tools: ~`, sem tocar em nenhum dos checks seguintes:
com o campo tratado como ausente, A2–A5 param de ter o que pular.

**D2 — `check_layout()` sai do caminho condicional.** A ausência de `agents/` deixa de ser um
`return` e passa a ser uma condição que a própria checagem de órfão avalia: sem fonte canônica,
qualquer cópia gerada é órfã. O `return` antecipado existia para o caso legítimo "repositório sem
agentes", que continua sendo zero achados — mas agora **porque a checagem rodou**, não porque foi
pulada.

**D3 — Recusar âncora e alias YAML, em vez de limitar a expansão.** Um teto de tamanho no bloco não
para uma bomba pequena que expande muito, e um teto de tempo é frágil e dependente da máquina.
Frontmatter de agente não tem uso legítimo para âncora: recusá-la remove a classe inteira, é
determinístico, e a mensagem diz o que fazer. É o mesmo raciocínio de `lean-code` — a solução que
não precisa de heurística ganha da que precisa.

**D4 — A saída é sanitizada na fronteira de registro, não em cada interpolação.** Sanitizar em
`add()` cobre todo achado presente e futuro; sanitizar em cada f-string cobre só os quatro sítios de
hoje e é esquecido no quinto. O valor problemático continua visível, com o caractere não codificável
substituído.

**D5 — O A7 compara conteúdo.** `generate.sh` copia com `cp --no-preserve=mode`, então a cópia gerada
é byte a byte igual à fonte; comparar é barato e fecha o buraco. A alternativa — declarar no cabeçalho
que o A7 compara só o nome e que a divergência é problema do gate de sync — foi recusada: a lei que o
requisito publica é "nada é publicado sem fonte canônica", e uma cópia divergente **é** conteúdo
publicado sem fonte.

**D6 — Qualquer espaço em branco depois dos `##` é aceito.** A regra atual exige espaço ASCII e
reprova `##\tWhen to invoke`, que um renderizador de Markdown aceita. Reprovar um cabeçalho válido é
um falso positivo do gate, e um gate que reprova o que a ferramenta aceita treina o autor a ignorá-lo.

**D7 — Cada correção ganha um caso de selftest, e o formato dele não muda.** O arquivo já reprova
quando o defeito é pego pelo check errado; os casos novos entram na mesma lista declarando o check
que devem provocar. Nenhuma infraestrutura nova.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Composição e autoria da camada de agentes; a lei de órfão e o que ela compara | `agents-catalog` | already canonical — MODIFIED nos dois requisitos tocados |
| Metodologia adversarial que produziu os oito achados | `bug-hunter` | link — os achados vieram de um agente que executa aquela metodologia; ela não é restatada aqui |
| Menor privilégio em `tools` e contrato de saída | `agent-delegation` | already canonical — o achado do `tools: ~` é uma violação daquela regra passando pelo gate, não uma regra nova |
| Não afirmar o que não foi probado | `verify-before-claiming` | link — o grupo Evidence cita, não restata |
| Volume de código | `lean-code` | link — D3 e D4 são as duas aplicações da escada aqui: a solução sem heurística e a correção na fronteira em vez de em cada sítio |

## Risks / Trade-offs

- **Engolir exceção demais e transformar erro de ambiente em achado silencioso.** Mitigado por um
  critério de aceite explícito: cada tratamento nomeia o caminho, e o exit continua não-zero.
- **Recusar âncora YAML quebrar um agente legítimo.** Nenhum dos três publicados usa âncora, e o
  formato do harness não a documenta. Se algum dia um caso legítimo aparecer, a mensagem do achado é
  onde a exceção será discutida.
- **O A7 comparando conteúdo duplicar o gate de sync do CI.** Aceito e escrito em D5: o gate de sync
  compara a árvore inteira contra `generate.sh`; o A7 publica a lei de fonte canônica e agora a
  cumpre. Dois gates que pegam o mesmo defeito por caminhos diferentes é redundância barata, não
  duplicação de doutrina.
- **Um nono ataque existir.** É o desenho: o selftest cresce por defeito encontrado, não por
  antecipação. As seis linhas que não produziram nada estão registradas para não serem reexaminadas.
