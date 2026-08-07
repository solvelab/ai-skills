# Research ladder — commands per rung

Read this when you are about to execute a rung, not before. The ordering and the rules live in
`SKILL.md`; this file is the command catalog.

**Provenance of this file.** Every command marked *probed* below was run on the machine this skill
was written on, 2026-08-06, against: ripgrep 14.1.1, git 2.47.3, Python 3.14.5, pip 26.1.1,
uv 0.11.28, npm 11.14.1, pnpm 9.15.9, gh 2.92.0, openspec 1.6.0, Node.js v26.0.0. Ecosystems whose
toolchain was **not installed** on that machine are marked *unprobed* and carry the method rather
than a command presented as checked. That distinction is the whole point of this skill: an unprobed
command written as if probed would be exactly the defect being documented.

## Rung 1 — this repo

The repo is authoritative for everything the project owns. Never recall a path, a config key or a
symbol that a search would settle.

```bash
rg -n "max_retries" --hidden --glob '!.git'
rg -n --files-with-matches "TimeoutError"
rg -tpy -n "def create_client"
git log -S "max_retries" --oneline
git log -p -1 --follow -- path/to/file.py
```

- `rg -S` for smart case, `-w` for whole word when a short symbol produces noise.
- `git log -S` finds the commit that *introduced or removed* a string — the fastest route to "why
  is it like this", which no other rung can answer.
- When the symbol has no hits, that is itself a finding: the thing may not exist in this project,
  and the next rung is the dependency, not the web.

## Rung 2 — the installed dependency

Two steps, always in this order: **resolve the version, then read that version's code.** Reading
the source without pinning the version is how a correct answer about the wrong release is produced.

### Resolving the installed version — probed

```bash
python3 -c "import importlib.metadata as m; print(m.version('httpx'))"
pip3 show httpx
uv pip show httpx
npm ls --depth 0
pnpm list --depth 0
```

`importlib.metadata` is the most reliable Python form: it reports what is *importable in this
interpreter*, which is the thing that will run, rather than what a manifest says should be there.

### Resolving the installed version — unprobed on this machine

The toolchain was absent, so the method is given and the exact invocation must be confirmed with
`--help` (rung 3) before it is relied on: Rust (`cargo`), Go (`go`), .NET (`dotnet`), Ruby
(`gem`/`bundler`), PHP (`composer`), Java (`mvn`/`gradle`), Dart (`pub`). In every one of these the
same two-step applies — ask the package manager what is installed, then read that version's source.

### Finding the lockfile without recalling its name

Do not recite a filename from memory. Ask the filesystem:

```bash
ls -1 | rg -i "lock|\.lock$"
git ls-files | rg -i "lock"
```

A lockfile that exists but disagrees with the installed version means the environment was not
synced — report that rather than picking whichever number you prefer.

### Reading the installed source

```bash
python3 -c "import httpx, pathlib; print(pathlib.Path(httpx.__file__).parent)"
node -p "require.resolve('undici')"
```

Then `rg` inside that directory. The installed source is definitionally correct about the API,
because it is the code the process will execute. It is *not* authoritative about intent, guarantees
or limits that live only in prose — that is rung 4.

## Rung 3 — the tool itself

What the installed binary does, as opposed to what its documentation says it does.

```bash
gh --version
openspec --version
rg --help
git help log
```

- Prefer `--help` on the exact subcommand, not the root: flags differ per subcommand and the root
  help hides them.
- A `--dry-run` or `--check` flag, where one exists, is the strongest rung-3 evidence: it exercises
  the real code path without changing state.
- Probes stay read-only. If the only way to answer is to mutate something, that is no longer a
  probe — it needs approval first.

## Rung 4 — official documentation, pinned to the installed version

Fetch, never recall. Build the URL from the version resolved at rung 2:

- Upstream source at the exact tag — the most reliable form, because the tag is the code:
  `raw.githubusercontent.com/<org>/<repo>/v<version>/<path>`
- Versioned documentation sites — `readthedocs` `/en/v<version>/`, or the project's own
  `/docs/<version>/` path
- Release notes and changelog for the range between the installed version and the one you remember

`latest` documentation read against a pinned older dependency is the single highest-yield way to
produce a confident wrong answer. If only `latest` is reachable, say so in the citation.

## Rung 5 — web search

Search answers exactly one class of question: **what changed after your cutoff, and what is broken
now.** Deprecations, migration notes, known bugs, security advisories.

A result is a **lead**, not a fact. It becomes a fact when the primary source it points at is
fetched — the upstream repository, the release notes, the vendor's own page. A blog post quoting a
changelog is not the changelog.

## Rung 6 — the user

Reachable only after 1-3 are exhausted. Authoritative for intent, priority, business rules,
credentials, and anything living in a system you cannot read. Ask one batched round of objective
questions, and state what you already established so the user is not asked to repeat the repo.

## Offline degradation

| Missing | What still works | What to do |
|---|---|---|
| Web-search tool | rungs 0-4 | Answer from source and docs; state that post-cutoff changes were not checked |
| Web-fetch tool | rungs 0-3 | Answer from the installed source; state that documented guarantees were not read |
| Both | rungs 0-3 | The installed code still settles API questions; semantics and limits go to rung 6 |
| Network entirely | rungs 0-3 | Same as above; name the unavailable rungs explicitly in the report |
| Dependency not installed | rungs 0-1 | The repo's own usage and tests are the only local evidence; do not infer the API from the call site alone — a call site can be wrong |

The absence of a rung is never evidence that the unverified answer is probably correct.
