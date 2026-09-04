# Change: Cumprir os limites da spec Agent Skills e medi-los no CI

## Why

`README.md:25` e `README.md:381` afirmam que o catálogo segue o padrão aberto Agent Skills. A
especificação desse padrão (agentskills.io/specification) fixa `description` em 1–1024 caracteres e
`compatibility` em 1–500. O validador de referência do padrão — o pacote `skills-ref` 0.1.1, cujo
binário se chama `agentskills` — reprova 5 das 35 skills do catálogo, medido em 2026-09-04 sobre
`d2918ed`:

```
skills/assettoserver-csp-lua   rc=1 :: Description exceeds 1024 character limit (1076 chars)
skills/backlog                 rc=1 :: Description exceeds 1024 character limit (1265 chars)
skills/code-locale             rc=1 :: Description exceeds 1024 character limit (1398 chars)
                                       Compatibility exceeds 500 character limit (728 chars)
skills/execute-backlog         rc=1 :: Description exceeds 1024 character limit (1344 chars)
skills/verify-before-claiming  rc=1 :: Description exceeds 1024 character limit (1222 chars)
ok=30 bad=5 total=35
```

Nenhum gate do repositório mede isso. `scripts/validate-skills.py` só compara a description com
o corpo (C4); `claude plugin validate --strict` aceita uma description de 2000 caracteres (medido
na issue #112). E o próprio spec do catálogo empurra na direção contrária: o requisito *Triggers
live in the description, not the body* manda dobrar todo gatilho e toda cláusula "Do NOT use" para
dentro da description, sem teto. Um gate de tamanho sozinho brigaria com esse requisito na próxima
dobra — por isso o teto e a reconciliação com a dobra entram no spec juntos.

O impacto hoje é de conformidade e portabilidade: o Claude Code carrega a description inteira, mas
qualquer consumidor que use o validador de referência rejeita um sexto do catálogo.

## What Changes

- `skills-authoring` ganha os tetos de 1024 (`description`) e 500 (`compatibility`), medidos em
  caracteres do valor YAML parseado, e a cláusula de que a dobra de gatilhos respeita o teto: o que
  não cabe vai para a primeira linha do corpo ou para `references/`, nunca fica na description.
- `scripts/validate-skills.py` ganha o check `C10 frontmatter limits`, que mede o valor parseado
  (o C4 mede o bloco cru, que dá 6–26 caracteres a mais) com `len()` em caracteres, como
  `skills_ref/validator.py`, e declara dentro de si o que não cobre.
- `META_HEADING` (C8) passa a casar também `## When to use this skill`, que hoje escapa; a seção
  com esse título em `skills/api-resilience-testing/SKILL.md` é removida porque seu conteúdo já
  está na description.
- `scripts/selftest-validate-skills.py` ganha uma mutação por check novo ou alargado: C10 com
  description inflada e C8 com a heading alargada. 13/13 vira 15/15.
- `.github/workflows/ci.yml` instala `skills-ref==0.1.1` na mesma linha de `pip` que já instala o
  PyYAML e ganha um step, logo depois do self-test do validador, que roda `agentskills validate`
  sobre cada diretório de `skills/` — pinado, com comentário explicando o pin.
- As 5 descriptions saem para ≤1024 e a `compatibility` de `code-locale` para ≤500 sem perder
  nenhuma frase de gatilho entre aspas; a tabela antes/depois fica em `tasks.md`.
- `README.md:25` e `:381`: o link "Agent Skills" passa a apontar para a especificação;
  `vercel-labs/skills` fica como o CLI `npx skills` da Opção A.
- `metadata.version` sobe (minor) nas 6 skills editadas; `./generate.sh` regenera os wrappers.

## Capabilities

### Modified Capabilities

- `skills-authoring`: *Uniform frontmatter metadata* ganha os tetos de caracteres; *Triggers live
  in the description, not the body* ganha a cláusula de que a dobra respeita o teto e alarga a
  lista de headings proibidas com `When to use this skill`; *Authoring rules are machine-enforced*
  ganha o cenário em que uma description acima do teto falha o build nomeando skill, check e
  tamanhos, e o cenário em que o validador de referência pinado roda no CI.

## Impact

- Skills afetadas (description encurtada, `metadata.version` minor): `code-locale` (também a
  `compatibility`), `execute-backlog`, `backlog`, `verify-before-claiming`,
  `assettoserver-csp-lua`. `api-resilience-testing` perde a seção `## When to use this skill` e
  também sobe de versão. Nenhuma skill é adicionada, removida ou renomeada: a composição do
  catálogo (35) e a descoberta via `npx skills` ficam idênticas.
- `scripts/validate-skills.py`, `scripts/selftest-validate-skills.py`: check novo, heading
  alargada, duas mutações.
- `.github/workflows/ci.yml`: um step novo e uma dependência pinada na linha de `pip`.
- `README.md:25,381`; wrappers gerados em `claude/`, `codex/`, `cursor/`, `copilot/`, `plugins/`.
- Fora de escopo, por decisão da issue #112: tornar fatal a linha `checks skipped` do validador;
  reduzir o orçamento total de tokens das descriptions; mudar como o Claude Code roteia skills.
