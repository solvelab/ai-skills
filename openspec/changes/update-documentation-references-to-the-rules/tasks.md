# Tasks

## 1. Evidence & Sources (MANDATORY)

- [x] E.1 Every local path this change relies on was OPENED and read, not recalled — recorded with
      the commit or timestamp it was read at

      Lidos em `bd8254b` (master, base de `backlog/190-documentation-follows-its-own-rules`) em
      2026-09-07:

      - `skills/documentation/references/check-doc-structure.py` — a docstring com o bloco KNOWN
        LIMIT (`:17-32`), as constantes (`:43-72`), `headings()` (`:117-124`), `fold()` (`:127-135`),
        `anchor_of()` (`:138-148`), `check_index()` (`:181-220`), `scan()` (`:372-378`) e
        `SELFTEST_CASES` (`:385`).
      - `skills/documentation/SKILL.md` — as onze seções `##` e a tabela de `:53-60`.
      - `skills/documentation/references/examples.md` — as três seções reais e as cercas em
        `:9,86,92,188,194,291`.
      - `skills/documentation/references/templates.md` — as cinco seções reais, as nove cercas, e a
        tabela de categorias de pré-requisito em `:239-250`.
      - `skills/documentation/references/information-architecture.md` — a régua que este item aplica.
      - A issue #190 inteira, incluindo o comentário que a manda para a sessão do repositório.

- [x] E.2 Every external tool, CLI flag, config key, API name or version this change asserts was
      probed against the installed version; the command and a fragment of its output are recorded

      `python3 skills/documentation/references/check-doc-structure.py skills/documentation/`
      -> `findings: 7 in 4 file(s); rules run: R1,R2,R3,R4,R6,R7`

      `python3 skills/documentation/references/check-doc-structure.py
      skills/documentation/references/information-architecture.md` -> `findings: 0 in 1 file(s)`
      — a régua passa; é o resto da skill que não.

      `python3 skills/documentation/references/check-doc-structure.py skills/ | grep -oE "\[R[0-9]\]"
      | sort | uniq -c` -> `80 [R1]`, `142 [R2]`, `19 [R6]`; total `findings: 241 in 142 file(s)`.

      `openspec new change update-documentation-references-to-the-rules --schema skills-rite`
      -> `Created change ...`

      `openspec validate update-documentation-references-to-the-rules --strict` sobre um change
      **sem** `specs/` -> `Ensure change has deltas in specs/: use headers ## ADDED/MODIFIED/...`
      — é a resposta à pergunta que o item deixou aberta: um change só de tarefas não valida neste
      schema.

      `grep -m1 "version:" skills/documentation/SKILL.md` -> `  version: 3.2.0`

- [x] E.3 Anything that could NOT be probed is written down as an open question (design.md, or here
      when there is no design.md) — never stated as fact, never filled with a plausible substitute

      Uma lacuna, e um erro de leitura corrigido antes de virar decisão:

      (a) **Aberta: se os índices continuam corretos com o tempo.** R1 acusa uma seção nova ausente
      do índice, mas nada acusa um índice que aponte para uma âncora que deixou de existir. O
      detector não implementa isso e este item não muda o detector. Fica como limite conhecido.

      (b) **Corrigido, não uma lacuna.** Uma primeira medição minha chamou `CHECKS[rule]` direto e
      contou 21 e 25 seções em `examples.md` e `templates.md`, o que faria o índice listar os
      cabeçalhos internos dos exemplos. Estava errada: o CLI passa por `scan()`, que chama
      `strip_fences` antes das regras. Pelo caminho real são **3** e **5** seções. Registrado aqui
      porque a conclusão errada teria produzido dois arquivos piores, e o que a evitou foi rodar o
      CLI em vez de acreditar no script.

- [x] E.4 Scope check: this change does only what the proposal asked. Adjacent improvements noticed
      along the way are listed here as follow-ups, not performed

      Follow-ups anotados e **não** feitos:

      - Os **234 achados restantes** no catálogo depois deste item (`R1` 79, `R2` 139, `R6` 19 fora
        de `skills/documentation/`), medidos em `bd8254b`. É item próprio: o *Fora de escopo* de
        #190 diz que qualquer outra skill é medição separada.
      - Uma checagem de âncora morta no detector, para a lacuna (a) de E.3.
      - `headings()` promete na docstring `"outside a fence"` e não filtra cerca nenhuma; quem
        filtra é `scan()`. Funciona porque todo caminho de produção passa por `scan()`, mas a
        docstring engana quem importar a função — foi o que me enganou. Correção de uma linha de
        comentário ou de código, no detector, que este item põe fora de escopo.

## 2. Índices (R1)

- [ ] 2.1 `SKILL.md` ganha `## Contents` cobrindo as onze seções, âncoras geradas por `anchor_of()`
- [ ] 2.2 `references/examples.md` ganha `## Contents` com as três seções reais
- [ ] 2.3 `references/templates.md` ganha `## Contents` com as cinco seções reais

## 3. Células longas (R2)

- [ ] 3.1 `SKILL.md:56` — a condição encolhe e os quatro nomes de arquivo descem para `## AGENTS.md`
- [ ] 3.2 `references/templates.md` — a tabela de categorias perde a coluna de fontes, que vira
      lista abaixo; as três células de 206/172/172 deixam de existir
- [ ] 3.3 Continência conferida: nenhuma frase apagada, contagem antes e depois mais leitura do diff

## 4. Catálogo

- [ ] 4.1 `metadata.version` da `documentation` sobe
- [ ] 4.2 `./generate.sh` rodado e wrappers commitados junto

## 5. Simulation & Field Proof (MANDATORY)

- [ ] S.1 The artifact was exercised through its real entry point; the command and a fragment of the
      observed output are recorded (or: this change touches no runtime artifact)
- [ ] S.2 Case matrix measured, as counts: cases that had to fire and did, cases that had to stay
      silent and did, known escapes that stayed silent
- [ ] S.3 What escaped or behaved differently than expected is named here — or it is stated
      explicitly that nothing did

## 6. Quality Gates (MANDATORY)

- [ ] Q.1 Frontmatter da `documentation` uniforme, valores conferidos
- [ ] Q.2 Conteúdo em inglês
- [ ] Q.3 Description e triggers da `documentation` inalterados — este item não mexe em roteamento
- [ ] Q.4 Nenhuma doutrina duplicada: as sete regras continuam só em `information-architecture.md`
- [ ] Q.5 Exemplos de código em inglês (`code-locale`)

## 7. Validation & Closure (MANDATORY)

- [ ] V.1 `openspec validate update-documentation-references-to-the-rules --strict` green
- [ ] V.2 Catalog discovery intact: 37 skills, sem órfão, sem drift de wrapper
- [ ] V.3 O detector sai com `findings: 0` sobre `skills/documentation/`
- [ ] V.4 `openspec archive update-documentation-references-to-the-rules --yes` after all groups
      above are `[x]`
