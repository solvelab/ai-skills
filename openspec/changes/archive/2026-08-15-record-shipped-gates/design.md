## Context

`openspec/specs/skills-authoring` já carrega o requisito *Authoring rules are machine-enforced*, que
exige script no CI com self-test injetando um defeito por check, e exige que cobertura parcial seja
declarada. Dois gates entregues em agosto de 2026 obedecem essa regra na implementação e escapam
dela no registro: nenhuma spec os descreve.

Medido no HEAD `c178c1b`:

```
$ grep -c "validate-rite-evidence\|evidence shape\|R1 " openspec/specs/*/spec.md
openspec/specs/skills-authoring/spec.md:0
openspec/specs/skills-catalog/spec.md:0
```

## Goals / Non-Goals

**Goals:**

- As specs vigentes descrevem os gates que o CI de fato roda.
- O rastro de decisão dos dois gates existe no arquivo, como o de qualquer outra mudança daqui.
- O registro é honesto sobre ser retroativo, em vez de racionalizar a ordem dos fatos.

**Non-Goals:**

- Mudar comportamento de qualquer script, workflow ou skill. Um `git diff` fora de `openspec/` é
  falha deste change, não escopo.
- Reabrir #79 ou #83, que estão entregues e verdes.
- Remediar os desvios equivalentes em `DriveZoneFivem/*`. Aqueles repositórios têm rito próprio,
  schema próprio e ganham item próprio em cada um.

## Decisions

**Um change para os dois gates.** Ambos são enforcement de regra de autoria e nasceram do mesmo
descuido de processo. Dois artefatos retroativos separados seriam lidos por ninguém; um artefato que
conta a história inteira tem chance de ser lido quando alguém perguntar por que o cenário de
frontmatter mudou. O delta continua tratando os dois requisitos separadamente.

**O change tem que sobreviver ao gate que ele documenta.** O grupo `Evidence & Sources` deste
`tasks.md` passa pelo `R1 evidence shape`. Se o change que registra o gate não passasse no gate,
uma das duas coisas estaria errada, e valeria descobrir qual antes de escrever a spec.

**A correção do cenário de frontmatter não é escopo novo — é dívida declarada.** O corpo do PR #84
registrou, na seção *Left in place, named*, que o cenário passaria a subdeclarar o gate e que
corrigir puxaria uma proposta. É essa proposta.

**O requisito novo vai em `skills-catalog`, não em `skills-authoring`.** `skills-authoring` governa
como um skill é escrito; o gate de evidência governa como um **change** é registrado. O precedente é
`add-verify-before-claiming`, que pôs *Claim verification has a canonical home* em `skills-catalog`
pela mesma razão.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Regra de autoria mecanizada com self-test e cobertura parcial declarada | `openspec` (lifecycle) + a spec `skills-authoring` | já canônica — este change só acrescenta cenários, sem reescrever a regra |
| Evidência exigida numa caixa ticada de grupo obrigatório | a spec `skills-catalog` e `scripts/validate-rite-evidence.py` | **nova home canônica** para a garantia; o script já era a implementação |
| Rito backlog-first e "todo change vira artefato" | `claude/global/personal-rules.md` → `backlog` / `execute-backlog` | já canônica — este change é consequência dela, não a redefine |
| Anti-chute: não afirmar sem consultar o precedente | `verify-before-claiming` | já canônica — a afirmação errada na #79 é uma instância do que ela proíbe; nenhuma doutrina é reescrita aqui |

Nenhum mecanismo de skill irmão é reproduzido inline.

## Risks / Trade-offs

- **Proposta retroativa vira teatro.** Risco principal. Mitigado por ela declarar-se retroativa na
  primeira linha do `Why`, citar PRs e releases, e nomear a afirmação errada que a originou em vez
  de omiti-la.
- **Agrupar os dois esconde um.** Mitigado pelo delta tratar os dois requisitos separadamente e pelo
  `tasks.md` ter grupo próprio para cada.
- **A deriva pode ser maior que os dois casos.** O `tasks.md` inclui uma varredura dos outros gates
  do CI contra as specs; o que aparecer vira item próprio, não escopo daqui — a alternativa é este
  change crescer sem fim.

## Open Questions

Nenhuma. A pergunta que existiria — separar em dois changes ou não — foi decidida em *Decisions* com
o motivo escrito.
