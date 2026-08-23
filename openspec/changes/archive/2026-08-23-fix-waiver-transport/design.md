## Context

`scripts/validate-spec-rite.py:227` lê o corpo do PR de `os.environ.get("PR_BODY", "")`, alimentado
por `.github/workflows/ci.yml:103-107`:

```yaml
        env:
          PR_BODY: ${{ github.event.pull_request.body }}
```

O Actions imprime o bloco `env:` no cabeçalho do passo, então o corpo sai no log. Medido no run
`32648727841` (job `97216916829`), com o corpo do PR #90 inteiro — tabelas, seções e tudo.

O que **não** está errado, e não muda: o corpo entra como valor de `env`, nunca interpolado no texto
do `run:`, então não há superfície de injeção; e a regex `WAIVER` é ancorada e o script não executa
nada do que lê.

## Goals / Non-Goals

**Goals:**

- O gate lê a dispensa sem que o corpo do PR passe por um canal que o CI ecoa.
- A troca não afrouxa nenhuma regra de decisão nem a forma da linha de dispensa.
- O leitor novo é coberto por teste, porque é a superfície nova.

**Non-Goals:**

- Mudar a forma da dispensa, as regras `S0`/`S1`/`S2`, a allowlist de release ou a isenção de diff
  confinado a `openspec/`.
- Mascarar com `::add-mask::`.
- Auditar outros passos do `ci.yml`. Nenhum outro recebe entrada de terceiro hoje.
- Declarar `spec_rite` no `.github/backlog.yml` deste repositório.

## Decisions

**`GITHUB_EVENT_PATH` em vez de `env`.** É o arquivo que o próprio runner escreve com o payload do
webhook — documentado como *"The path to the file on the runner that contains the full event webhook
payload"*. `github.event` é exatamente esse payload, então `pull_request.body` está lá por
construção: é a mesma origem que hoje alimenta o `env`, lida um passo antes. Nada precisa ser
passado pelo workflow, e o que não é passado não é impresso.

**`PR_BODY` fica, rebaixado a override.** Ele é o que torna o gate testável fora do CI — os cenários
end-to-end do change anterior dependem dele. Precedência: `PR_BODY` definido vence; senão o payload;
senão vazio. O override primeiro, e não por último, porque a única razão de alguém defini-lo
explicitamente é querer aquele valor.

**`::add-mask::` foi descartado.** Mascarar trata sintoma: o dado continua atravessando o canal e o
log vira `***` no meio de um bloco que existe para ser lido. A correção é o dado não passar por ali.

**Falha de leitura vira corpo vazio, não traceback.** `json.load` em `try/except` estreito, com
aviso. Se o gate morrer porque o canal de leitura tropeçou, ele deixa de ser gate e vira flake — e o
efeito prático seria bloquear PRs por um motivo que nada tem a ver com o rito. Corpo vazio mantém a
decisão nas regras que já existem: sem dispensa, `S1` dispara se houver caminho fora de `openspec/`.

**O delta modifica o requisito existente, não acrescenta um vizinho.** *The rite gates evidence
before it gates quality* já tem o parágrafo que trata a dispensa como entrada não confiável. "Não
publique o que lê" é a outra metade da mesma preocupação com o mesmo dado. Um requisito novo ao lado
dele partiria a doutrina em dois lugares que precisam ser lidos juntos — exatamente o que
`skills-authoring` proíbe.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Ciclo OpenSpec e formato dos artefatos | `openspec` | já canônica — este change não a toca |
| Gate de spec no rito backlog-first (detecção, veredito, transporte da dispensa) | `skills/execute-backlog/references/spec-rite.md` | já canônica — e verificado que ela **não** nomeia o transporte, então não muda |
| Entrada não confiável: casar como texto, nunca executar | a spec `skills-catalog` (*The rite gates evidence...*) + `scripts/validate-spec-rite.py` | já canônica — este change acrescenta a metade "não publique", no mesmo requisito |
| Não afirmar sem probar (o `env:` ecoado foi medido, não suposto) | `verify-before-claiming` | já canônica — nenhuma doutrina reescrita aqui |

## Risks / Trade-offs

- **O payload não trazer `pull_request.body`** → o override e o corpo vazio cobrem, e o critério de
  aceite do log prova qual caminho rodou no CI real.
- **Afrouxar a checagem sem perceber ao trocar o transporte** → os cenários `S1`/`S2` do `--selftest`
  ficam intactos e são a rede; o leitor novo ganha casos próprios.
- **Perder contexto ao depurar uma dispensa recusada, agora que o log não mostra o corpo** → a
  mensagem de erro do gate já cita a forma esperada da linha; o corpo do PR continua a um clique.
- **O arquivo do payload ser grande** → é lido uma vez, e só a chave do corpo é usada.

## Open Questions

_Nenhuma._ A única incerteza — se a chave existe no arquivo — é resolvida pela execução de CI deste
próprio PR, e o fallback cobre o caso contrário sem quebrar nada.
