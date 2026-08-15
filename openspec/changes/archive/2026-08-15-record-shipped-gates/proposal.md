## Why

**Este change é retroativo, e diz isso na primeira linha.** O código que ele descreve já está em
`master`: o gate de evidência entrou pelo PR #80 (release 2.10.0) e os checks de frontmatter pelo
PR #84 (release 2.11.0), ambos sem proposta OpenSpec. Ele não finge que a decisão foi tomada antes;
ele fecha o rastro que faltou e corrige a deriva que os dois deixaram nas specs.

O padrão do repositório era claro e foi contrariado. `2026-08-07-add-repo-hygiene-gates` entregou
`scripts/validate-repo-hygiene.py` — dois checks e um `--selftest` injetando um defeito por check —
com proposta completa. O PR #80 entregou `scripts/validate-rite-evidence.py` — um check e um
`--selftest` injetando um defeito por regra — sem nenhuma. A justificativa registrada na issue #79
foi *"ajuste de gate existente, não capacidade nova"*, e o arquivo desmente.

O custo não é o artefato ausente. É a deriva, medida no HEAD `c178c1b`:

```
$ grep -c "validate-rite-evidence\|evidence shape\|R1 " openspec/specs/*/spec.md
openspec/specs/skills-authoring/spec.md:0
openspec/specs/skills-catalog/spec.md:0
```

Existe um gate bloqueante no CI que nenhuma capability descreve. E o cenário
*CI rejects incomplete frontmatter* ainda nomeia três campos enquanto o passo enforça sete — sendo
que o próprio requisito manda o contrário: *"When the two disagree, the gate is authoritative and
this document is corrected"*. A correção prevista pela regra nunca foi feita.

## What Changes

- **Nada de comportamento.** Nenhum script, workflow ou skill é tocado. `git diff --name-only master`
  deve listar só caminhos sob `openspec/`.
- `skills-authoring` → *Uniform frontmatter metadata*: o cenário de rejeição passa a nomear os sete
  campos que o passo de CI de fato enforça, cumprindo a cláusula "gate is authoritative".
- `skills-catalog` → *The rite gates evidence before it gates quality*: **MODIFIED**, não um
  requisito novo. Ler a spec com atenção mostrou que ela já é exatamente sobre isto e ficou
  desatualizada de forma precisa — diz que *"the enforcing script SHALL state that it verifies the
  presence and position of the group and not the truth of its contents"*, o que deixou de descrever
  o rito quando um script irmão passou a verificar a **forma** do conteúdo. O delta registra a
  segunda camada e o relatório de densidade, mantendo intacta a ressalva de que nenhuma das duas
  verifica veracidade. Inventar um requisito novo ao lado de um que já cobre o assunto teria criado
  doutrina duplicada.
- **Um change para os dois**, e não dois. Ambos são o mesmo assunto: enforcement de regra de
  autoria. Separá-los produziria dois artefatos retroativos que ninguém leria em separado, e o
  delta trata os dois requisitos distintamente mesmo dentro de um change.

## Capabilities

### New Capabilities

_Nenhuma._ O comportamento já existe em `master`; o que falta é o registro.

### Modified Capabilities

- `skills-authoring`: *Uniform frontmatter metadata* passa a descrever os sete campos que o passo de
  CI de fato enforça, cumprindo a cláusula "gate is authoritative" do próprio requisito.
- `skills-catalog`: o requisito que já governa a evidência do rito passa a descrever também a
  camada que verifica a forma das caixas, e o relatório de densidade por grupo obrigatório.

## Impact

- `openspec/specs/skills-authoring/spec.md` e `openspec/specs/skills-catalog/spec.md`, após o archive.
- Nenhum arquivo de código, workflow ou skill. Consumidores do catálogo não veem diferença: os gates
  descritos aqui já rodavam antes deste change.
