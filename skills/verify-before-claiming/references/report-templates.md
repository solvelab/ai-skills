# Report templates

Read this when you are about to produce output. The rules live in `SKILL.md`; these are the shapes.

## Claim labels

### Verified

The source travels with the claim, inline, at the point it is made — not in a footnote and not at
the end of the message, because the reader acts on the sentence, not on the appendix.

> The `timeout` parameter accepts a float (`httpx/_client.py:1402`, httpx 0.28.1 resolved via
> `importlib.metadata`).

> `gh project field-list` returns an empty `options` array for org-level issue fields — reproduced
> with `gh project field-list 3 --owner solvelab --format json` on gh 2.92.0.

Prefer citing **the command that reproduces the fact** over citing its location: the reader can
re-run a command in two seconds, and a re-runnable citation is the only kind that survives a
skeptical reader.

### Inferred

A conclusion drawn from verified facts, marked as one, naming what it was drawn from.

> Bodies over 2 MB are rejected before the handler runs — **inferred** from `max_body` in
> `settings.py:18` plus the middleware order in `app.py:44`. Not measured.

### Unknown

Never a hedged sentence. It goes to the not-found report.

### In code

Chat scrolls away; the code ships. The marker goes at the line that depends on the unverified fact,
and it names three things: what is unverified, what was checked, and what would confirm it.

```python
# UNVERIFIED: retry_on_timeout may not exist on this client version.
# Checked: importlib.metadata reports 0.28.1; the installed source has no such kwarg.
# Confirm by: running tests/test_client.py::test_retry against the pinned version.
retry_on_timeout=True,
```

## The not-found report

```markdown
**Not found: does the client expose a per-request retry limit?**

Searched:
- rung 1 — `rg -n "max_retries|retries" --hidden` -> 0 hits in this repo
- rung 2 — resolved 6.19.8 via `npm ls --depth 0`; read the installed `types/*.d.ts` -> no such
  option on the request type
- rung 3 — `undici --help` -> not a CLI, no probe available
- rung 4 — fetched the 6.x dispatcher documentation -> the option is absent from the page

Not searched:
- rung 5 — no web-search tool in this environment

**Still unknown:** whether the option exists under another name in this major.

**Options:**
(a) you tell me the value and I wire it;
(b) I implement the bounded retry in the caller, which covers the case without that option and uses
    only surface I verified above;
(c) I write a 10-line probe against the installed version and run it — about two minutes;
(d) I open an upstream issue and we proceed with (b) meanwhile.
```

Rules the template enforces:

- The search log names **commands**. "I looked around" is not a search log, and a log with no
  commands in it is indistinguishable from one that was never run.
- *Not searched* is a required section when any rung was skipped, with the reason. A silently
  omitted rung reads as an exhausted search.
- At least one option must move the work forward without the missing fact, when such an option
  exists. A not-found that only says "I do not know" is half a deliverable.

## Doing / Not doing / Assumptions

Produced before acting, not after. It is short on purpose — if it is long, the scope is unclear and
that is itself the finding.

```markdown
**Doing:** add the `--json` flag to the export command and its test.
**Not doing:** touching the import path, the CLI help text, or the two other commands that share
the formatter.
**Assumptions:** the flag prints to stdout (matching `list --json`, which I read at
`cli/list.py:31`); no schema version field is required.
```

Anything under **Assumptions** that would change the shape of the work needs a yes before you
start. Everything else can proceed under a stated assumption.

## Mid-flight scope change

Used when implementation proves the agreed scope wrong. Stop at a safe point first — never a
half-applied refactor.

```markdown
**Agreed:** add the retry wrapper to the two call sites in `sync.py`.
**Found:** both call sites go through `client.request()`, which already retries internally
(`client.py:88`, verified). Wrapping them would double the retry budget from 3 to 9.
**Why the agreed path fails:** the requested change makes the timeout worse, not better.
**Options:** (a) tune the existing internal retry instead — 1 file, no new code path;
(b) proceed as agreed and I document the compounded budget;
(c) stop here and re-groom the item.
```

Never silently re-scope. Recording an approved deviation on the issue and moving the board card is
`execute-backlog`'s job; this template only covers stopping and reporting.
