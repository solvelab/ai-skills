## Context

O detector `skills/code-locale/references/check-identifier-locale.py` (45,6 KB, lido em `80ee53c`)
já tem o modo de adoção: `--diff FILE` lê linhas adicionadas de um unified diff (`-` para stdin) e
sai 1 quando um tier que gate (`pt-verb`, `pt-noun`, `pt-morphology`, path) reporta; `en-unknown` é
consultivo e nunca muda o exit code sem `--gate-unknown`. As saídas já existem: `WAIVER_RE`
(`locale-ok:`) na linha 99 e `ALLOWLIST_FILE = ".identifier-locale-allow"` na 98. `EXT_LANG`
(211-216) tokeniza `.py .lua .js .jsx .mjs .cjs .ts .tsx .cs .sql .yml .yaml .json .sh .bash`; outra
extensão tem o caminho medido e o conteúdo reportado como *skipped*.

`load_english()` (414-445) resolve as listas de palavras por `Path(__file__).resolve().parent` e
**não falha** quando faltam: o conjunto fica vazio, e todo segmento vira `en-unknown`. Medido nesta
sessão com o detector copiado sozinho para um diretório vazio: o fixture `def calcular_total(itens)`
dá o mesmo `findings: 1` e `rc=1`, mas passa a listar `orders` (o nome do arquivo) como
`path-en-unknown`. Um detector baixado por URL, sozinho, é correto no gate e ruidoso no consultivo.

O que já existe por camada: `locale-rite.py` (hook `PostToolUse`, README 306-347) mede o **write**
de uma sessão Claude Code com o `settings.json` wired; o step C9 de `scripts/validate-skills.py`
mede os **fences** dos `.md` deste catálogo. Nenhuma das duas roda num repositório de destino, e
nenhuma roda para um humano digitando `git commit`.

## Goals / Non-Goals

**Goals:**

- Um repositório qualquer adota o gate copiando **um arquivo** (o hook) ou **um bloco YAML** (o
  step), sem clonar este catálogo e sem assistente.
- O hook recusa um commit cujo diff staged introduz um identificador em português, e aceita o mesmo
  commit com `# locale-ok: <motivo>` — o mesmo detector, o mesmo exit code, as mesmas saídas.
- O step de CI falha o PR com um achado e passa sem; o detector vem de uma **tag** deste
  repositório, nunca de `master`, e o download é conferido por sha256.
- Cada arquivo declara no próprio cabeçalho o que não cobre.

**Non-Goals:**

- Reimplementar qualquer tier do detector no hook ou no step: os dois só o **invocam**.
- Gate no tier consultivo (`--gate-unknown`): decisão de cada repositório, documentada como opt-in.
- Suporte a outro CI que não GitHub Actions; o comando de uma linha serve de base para os demais.
- Wiring nos repositórios do mantenedor; opção no `install.sh`.

## Decisions

### D1 — O hook invoca o detector, não o reimplementa

`git diff --cached --no-color --no-ext-diff --no-renames --src-prefix=a/ --dst-prefix=b/ |
PYTHONIOENCODING=utf-8:surrogateescape python3 <detector> --diff -` é o comando inteiro (os flags e a
variável: D7). O que o hook acrescenta é **onde encontrar** o detector e **como explicar** o exit 1. Alternativa rejeitada:
embutir um subconjunto das regras em bash/awk — o requisito *A shipped enforcement script declares
what escapes it* exige que o que roda seja o script embarcado, e o CI deste catálogo prova
exatamente ele (`ci.yml`, step *Identifier-locale detector self-test*).

### D2 — Ordem de localização: explícito → clone → download pinado

1. `$LOCALE_CHECK` — caminho explícito, para quem vendorizou o detector no próprio repositório.
2. `$AI_SKILLS_HOME/skills/code-locale/references/check-identifier-locale.py`, depois
   `~/ai-skills/...` — o clone que `install.sh` deste catálogo cria; é o caminho do mantenedor e
   traz as listas de palavras ao lado, então o tier consultivo funciona por inteiro.
3. Download de `https://raw.githubusercontent.com/solvelab/ai-skills/<TAG>/skills/code-locale/references/check-identifier-locale.py`
   com `curl -fsSL`, sha256 conferido por `python3 -c 'import hashlib...'` (sem depender de
   `sha256sum`/`shasum`, que variam entre Linux e macOS), cache em
   `$(git rev-parse --git-dir)/locale-check/<TAG>/` — dentro de `.git/`, nunca versionado, nunca
   baixado duas vezes para a mesma tag.

`TAG` e `SHA256` são defaults no topo do arquivo (`v2.21.0`,
`4e72af47225d6259f6b69db638af6db6c586c7ee6800e401941e08c223413ff2` — medido com
`git show v2.21.0:... | sha256sum`, idêntico ao HEAD) e podem ser sobrescritos por
`LOCALE_CHECK_TAG` / `LOCALE_CHECK_SHA256`. Trocar a tag sem trocar o hash **falha alto** de
propósito: um pin que aceita qualquer conteúdo não é um pin. `LOCALE_CHECK_SHA256=skip` desliga a
conferência, por escrito, para quem quer só o pin por tag.

O pin vale **só para a fonte 3**. As fontes 1 e 2 rodam o arquivo que está naquele caminho, sem
digest: `LOCALE_CHECK` é a cópia vendorizada de quem a definiu, e `~/ai-skills` é o clone que
`install.sh` cria com `git clone` sem `--branch` (`install.sh:186`), no commit em que o dono deu o
último `pull`. Um commit aceito localmente e o step de CI (sempre pinado) podem rodar versões
diferentes do detector — o cabeçalho do hook diz isso em *THE PIN*, e o delta da spec exige o pin e o
digest **quando o artefato baixa**, não em toda fonte. Alternativa rejeitada (review de 2026-09-05):
conferir o sha256 do arquivo local e cair para download quando divergir — quebraria o caminho do
mantenedor sempre que o clone estivesse à frente da tag (o detector mudou em `master`), e o modo
download perde o tier consultivo (listas ausentes). O trade-off fica declarado, não escondido.

Alternativa rejeitada: baixar também as três listas de palavras (`english-words.txt.gz`, 1,0 MB,
`programming-words.txt`, `not-english.txt`). São quatro URLs e quatro hashes para copiar; o ganho é
só o tier consultivo. No modo download o hook passa `--no-english` e diz isso na saída — o gate é
idêntico, e quem quiser o consultivo tem o caminho 2 ou vendoriza as listas ao lado (caminho 1).

### D3 — Sem `python3` o hook recusa, não aprova

"A gate that cannot measure must not approve" é a regra que `validate-spec-rite.py` já aplica ao
`fetch-depth`. Aqui: `python3` ausente → mensagem nomeando o binário e o `--no-verify`, exit 1.
Alternativa rejeitada: sair 0 com aviso — um hook silenciosamente inerte é o estado que a issue
descreve como problema.

### D4 — A saída do hook é a saída do detector mais um rodapé com as três saídas

O detector já imprime `path:line:token [tier]` e a linha exata de waiver a adicionar. O hook não
reformata: repassa e acrescenta um rodapé de quatro linhas — `# locale-ok: <motivo>` na linha ou
imediatamente acima, `.identifier-locale-allow` para nome de arquivo, `git commit --no-verify` como
o bypass **deliberado** (nomeado, não escondido: a doutrina do catálogo é informar e deixar a
decisão com o autor). Tudo em stderr: um hook de git que escreve em stdout polui `git commit -v`.

### D5 — O step de CI é um job inteiro, com `permissions: contents: read`

O que o `ci.yml` deste repositório já faz (issue #117): job com permissão mínima,
`persist-credentials: false`, `fetch-depth: 0` porque `git diff origin/<base>...HEAD` precisa da
merge-base, e `pull_request` como único gatilho — em `push` não há `github.base_ref` e o comando
não tem o que medir. O pin é a tag na URL do `curl` mais `sha256sum -c` (no runner Ubuntu o
coreutils está garantido; no hook, que roda em qualquer máquina, é python3 — D2).

O bloco `run:` começa com `set -o pipefail`. O shell padrão de um `run:` é `bash -e {0}` **sem**
`pipefail` (página *workflow syntax* do GitHub; não probado num runner), e a primeira versão deste
design tomou isso como desejável — "o exit code do pipe é o do `python3`". Medido no review de
2026-09-05 com o bloco verbatim sob `bash -e`: base ausente do clone → `fatal: ambiguous argument
'origin/release/9...HEAD'`, o detector lê um stream vazio, imprime `findings: 0` e o step fica
**verde** (rc=0). Isso viola a regra que o próprio `ci-step.md` enuncia ("a gate that cannot measure
must not approve") e que D3 aplica ao hook. Com `pipefail` o mesmo caso sai 128 e o step falha. O
`fetch-depth: 0` continua necessário — ele é o que faz a medição possível; o `pipefail` é o que
impede a aprovação quando ela não aconteceu. `shell: bash` daria o mesmo efeito (a mesma página o
documenta como `bash --noprofile --norc -eo pipefail {0}`); a linha explícita viaja para outro CI.

### D7 — O diff tem a forma fixada, e um exit 1 sem `findings:` não é uma medição

Quatro flags em `git diff`, nos dois artefatos, cada um contra um caso medido no review de
2026-09-05 em que a configuração git do repositório ou do usuário mudava o que o detector lê:

| Flag | Sem ele (medido) |
|---|---|
| `--no-ext-diff` | `diff.external` troca o unified diff pela saída do driver: `wc -c` → 0, `findings: 0`, commit com `buscar_cliente` aprovado (rc=0) |
| `--no-renames` | `git mv orders.py relatorio.py` vira `rename to` sem `--- /dev/null`; o detector só mede o caminho nesse header (`check-identifier-locale.py:632-646`) → rc=0. Com o flag o rename é delete + add e `relatorio.py` é reportado pelo caminho |
| `--src-prefix=a/ --dst-prefix=b/` | `diff.mnemonicPrefix=true` escreve `+++ i/relatorio.txt`; o detector tira só `b/` e o allowlist `relatorio.txt` deixa de casar → recusa de um caminho legitimamente grandfathered |

`PYTHONIOENCODING=utf-8:surrogateescape` no `python3`: um hunk com bytes fora de UTF-8 (arquivo
legado latin-1, comum nas bases que a skill mira) abortava o detector com `UnicodeDecodeError` na
leitura do stdin — exit 1 — e o hook explicava esse exit 1 como "the staged diff adds a non-English
name", com três saídas que não consertam nada. Com o handler os bytes passam e só os nomes são
julgados (`legacy.py` latin-1 + linha inglesa → rc=0; + `buscar_cliente` → achado, rc=1).

E o hook só trata exit 1 como recusa por achado quando a saída traz a linha `findings:` que o
detector imprime ao terminar o scan; qualquer outro exit 1 (traceback, `LOCALE_CHECK` apontando para
um script errado) vira `rc=70` e cai no ramo "the detector itself failed" — ainda recusa, porque nada
foi medido, mas com a causa certa.

Trade-off aceito do `--no-renames`: renomear um arquivo legado cujo conteúdo ainda tem nomes em
português relê o conteúdo inteiro como adicionado e encontra o gate naquele momento (medido:
`relatorio.py` com `calcular_total` → `report.py` recusado no conteúdo). É o mesmo caso que o
`ci-step.md` já declarava para "mover um nome legado de um arquivo para outro": a hora da migração
é a hora do waiver ou do rename de tier 2. Um rename puro de arquivo limpo fica mudo; um rename
**para** nome em português é reportado pelo caminho — a razão do flag. Alternativa rejeitada:
ensinar o detector a ler `rename to` — edição no detector, fora do escopo desta issue e desta
ownership; fica em `tasks.md` E.4 como follow-up.

### D8 — bash 3.2 é o piso, porque o macOS de fábrica é bash 3.2

Sob `set -u`, `"${EXTRA_ARGS[@]}"` com array vazio é *unbound variable* em todo bash < 4.4 — o
`/bin/bash` de qualquer macOS. Medido em `docker run bash:3.2` e `bash:4.3`: o hook original recusava
**100 %** dos commits (`line 154: EXTRA_ARGS[@]: unbound variable`, rc=1, 0 commits), inclusive os
em inglês, e a primeira simulação só tinha rodado em bash 5.2. A expansão `${arr[@]+"${arr[@]}"}`
é a forma que sobrevive nos dois; o cabeçalho declara `bash 3.2+` em *Dependencies* e a simulação
tem os dois containers como casos.

### D6 — A seção do `SKILL.md` cabe numa tela e não repete a doutrina

Uma frase, dois links relativos (`references/pre-commit-locale.sh`, `references/ci-step.md`) e a
tabela de três camadas. O corpo da skill já explica `--diff`, `locale-ok:` e o allowlist; a seção
aponta para *Reviewing a diff* em vez de reescrever. Links relativos porque `generate.sh` reescreve
`](references/` para a URL do repositório no wrapper do Cursor e `plugins/` copia `references/`
inteira — as duas formas resolvem.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Camada de máquina em inglês; `--diff` como modo de adoção; `locale-ok:` e `.identifier-locale-allow` | `code-locale` | already canonical — os dois arquivos novos vivem dentro dela e apontam para *Reviewing a diff* em vez de reescrever |
| Um script embarcado declara o que não cobre | `skills-catalog` (spec, *A shipped enforcement script declares what escapes it*) | already canonical — o hook e o step carregam a própria lista de escapes no cabeçalho |
| Um gate que não consegue medir não aprova (base ausente, `python3` ausente) | `scripts/validate-spec-rite.py` (precedente) + spec `skills-catalog`, *The rite gates evidence before it gates quality* | already canonical — D3 e D5 citam, não reescrevem |
| Pin por versão probada, com a regra de bump ao lado | `ci.yml` (precedente dos pins de `claude-code` e `openspec`) | already canonical — o hook e o step trazem TAG + sha256 e a frase de bump |
| Prova pelo caminho real antes de declarar entrega | `verify-before-claiming` | already canonical — grupo de simulação de `tasks.md` |
| Identificadores em inglês no que a change introduz | `code-locale` | already canonical — `LOCALE_CHECK`, `LOCALE_CHECK_TAG`, `locate_check`, `run_check`, ids de step em inglês |

## Risks / Trade-offs

- **O detector baixado por URL muda** → pin por tag + sha256 embutido; trocar um sem o outro falha
  alto (D2). A frase de bump está no cabeçalho do hook e no `ci-step.md`.
- **Modo download sem as listas de palavras vira ruído consultivo** → medido (Context); o hook passa
  `--no-english` nesse modo e imprime uma linha dizendo que o tier consultivo está desligado e como
  ligá-lo. O gate não muda.
- **`git commit --no-verify` anula o hook** → é o bypass deliberado e está **nomeado** no rodapé e
  no cabeçalho; o step de CI é a camada que o pega, e a tabela do `SKILL.md` diz isso.
- **`git diff --cached` inclui só o que está staged** → é o comportamento correto para `git add -p`
  (mede o hunk que vai no commit), e um commit vazio (`--allow-empty`) passa com `findings: 0`.
- **Um repositório legado fica vermelho no primeiro commit** → não: `--diff` mede só linhas
  adicionadas (docstring do detector, *WHY --diff IS THE DEFAULT ADOPTION MODE*); conteúdo existente
  nunca é reportado, e isso está na lista de escapes.
- **`shellcheck` e `act` não estão nesta máquina** → `bash -n` roda; o step é validado com o
  mesmo comando do `run:` sobre um clone com `origin/main`, e a simulação declara qual foi.
- **O hook roda em bash antigo (macOS)** → piso declarado 3.2 e probado em container (D8).
- **`--no-renames` relê o conteúdo de um arquivo renomeado** → trade-off declarado nos dois
  cabeçalhos e em D7; a alternativa (detector lendo `rename to`) é follow-up.
- **Fontes 1 e 2 do hook não têm pin** → declarado em *THE PIN* e em D2; o CI é a camada pinada.

## Open Questions

Nenhuma. As nove observações do review de 2026-09-05 foram reproduzidas antes de qualquer edição
(`$SCR/repro139.py`, `before`: 7 de 10 casos fora do esperado; `after`: 10/10) e estão em D2, D5,
D7 e D8. As três lacunas que poderiam virar achismo — se a raw URL na tag responde 200, qual é o
sha256 do detector na tag, e o que o detector faz sem as listas de palavras ao lado — foram medidas
antes de escrever e estão em `tasks.md` E.2 com comando e saída.
