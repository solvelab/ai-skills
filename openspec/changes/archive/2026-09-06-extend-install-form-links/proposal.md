# Change: Wrapper Copilot com link do SKILL.md por URL e bloco de pull compartilhado

## Why

Dois follow-ups de distribuição registrados em E.4 das changes `define-cross-skill-references`
(#121) e `harden-distribution-scripts` (#113), lidos em `e7f5fe8` (topo de `master`, 2026-09-06):

1. `generate.sh:196` escreve no wrapper Copilot `Follow the instructions in
   [SKILL.md](../../skills/${name}/SKILL.md)`. O README (linha 151) manda copiar
   `copilot/instructions/*.instructions.md` sozinho para `.github/instructions/` do projeto, e ali o
   link relativo morre — o próprio README (linha 150) admite: *"the SKILL.md link still expects the
   clone"*. A regra R5 de #121 converteu só os links de `references/` para URL do repositório; o link
   do próprio `SKILL.md` ficou de fora. Medido: `grep -c '\.\./\.\./skills' copilot/instructions/*.md`
   -> 36 arquivos, 36 links relativos.
2. `install.sh:176-183` e `update.sh:61-68` carregam duas cópias do mesmo bloco — `pull --ff-only`
   com `advice.diverging=false`, a mensagem *Fast-forward failed*, a dica `./update.sh --force`, o
   `fatal:` do git indentado. Foi assim que #113 encontrou o `install.sh` cru enquanto o `update.sh`
   já explicava. O E.4 de #113 desistiu de compartilhar porque "os dois rodam via `curl | bash` sem o
   repositório presente" — mas o bloco de pull só roda **sobre um clone que já existe** em
   `~/ai-skills`, e esse clone carrega `scripts/`.

## What Changes

- `generate.sh`, bloco do Copilot: o link do `SKILL.md` passa a ser
  `https://github.com/solvelab/ai-skills/blob/master/skills/<name>/SKILL.md`, a mesma forma
  (`REPO_BLOB_URL`) que o bloco já usa para `references/`. Os 36 `copilot/instructions/*.md` são
  regenerados; nenhum outro wrapper muda (`claude/`, `codex/`, `cursor/`, `plugins/` sem diff).
- `scripts/lib/git-sync.sh` (novo): a função `pull_ff_only <dir>` — o pull fast-forward, a mensagem
  de divergência, a dica de `--force` e o detalhe do git — existe uma vez. `install.sh` (re-run sobre
  um clone) e `update.sh` (caminho sem `--force`) carregam o arquivo **do clone que vão sincronizar**
  (`$INSTALL_DIR/scripts/lib/git-sync.sh`), porque é o único lugar que os dois scripts conhecem quando
  rodam por `curl | bash`. Um clone anterior a este arquivo é recusado com a dica de rodar o
  `./update.sh` que ele mesmo carrega, uma vez.
- `scripts/smoke-install-scripts.sh`: os 17 casos continuam; ganha o caso que compara byte a byte o
  bloco de divergência impresso por `update.sh` e por `install.sh` sobre o mesmo clone divergido, e o
  caso que prova a recusa sobre um clone sem o arquivo compartilhado.

Nada aqui é **BREAKING** para consumidores do catálogo: nenhuma skill entra, sai ou muda de nome;
`npx skills add` e os plugins não leem `copilot/`. Para quem instala pelo README, o wrapper Copilot
copiado sozinho passa a resolver o link do `SKILL.md`; para quem re-roda o instalador por `curl` sobre
um clone anterior a esta versão, o script pede uma passada pelo `update.sh` do próprio clone.

## Capabilities

### New Capabilities

_Nenhuma._ Nenhum skill novo entra no catálogo.

### Modified Capabilities

- `skills-authoring`: *Cross-skill references resolve in every install form* — a regra dos wrappers
  Cursor/Copilot passa a cobrir também o link do próprio `SKILL.md`, com o cenário em que um wrapper
  copiado sozinho aponta o `SKILL.md` pela URL do repositório.

## Impact

- `generate.sh` (só o bloco `# --- GitHub Copilot ---`, ~:192-200) e, por regeneração, os 36
  `copilot/instructions/<name>.instructions.md`.
- `install.sh`, `update.sh` — o bloco de pull vira uma chamada a `pull_ff_only`; cabeçalhos dizem de
  onde o arquivo compartilhado é lido e o que acontece quando não existe.
- `scripts/lib/git-sync.sh` (novo), `scripts/smoke-install-scripts.sh` (dois casos novos; a matriz
  passa de 17 para 19).
- Nenhum `SKILL.md` é tocado; a composição do catálogo (36 skills) fica idêntica. `README.md` não
  está entre os arquivos deste item: a nota da linha 150 (*"the SKILL.md link still expects the
  clone"*) fica desatualizada e é registrada como follow-up em `tasks.md` E.4.
- `skills-catalog` não muda: o cenário *A diverged clone is refused with the recovery hint, by both
  scripts* já exige a mesma mensagem nos dois; o arquivo compartilhado é **como** ela passa a ser a
  mesma, e o caso novo do smoke test é a medida desse cenário, não um requisito novo.
