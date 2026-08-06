# Change: Close the secret question with a scanner, not a history rewrite

## Why

One item was left open across the whole catalog audit: two cluster node addresses, a customer org slug
and an app-name prefix, removed from the tree in #33 but still present in the published history. The
open question was whether to rewrite history.

Two measurements settled it.

**First, what is actually in the history.** A scan of **1879 blobs across every commit** found:

| class | result |
|---|---|
| AWS keys, GitHub/Slack tokens, Google API keys | **none** |
| private key blocks, JWTs | **none** |
| public IPv4 addresses | **none** |
| connection string carrying a password | **1** — `postgresql://<user>:<password>@`, a documentation example |
| private RFC1918 addresses | **2** — the known `10.160.0.*` pair |

**No credentials.** The residual is two non-routable addresses and a sample connection string in a
teaching example.

**Second, what a rewrite would cost and achieve.** The values live in 2 commits; the repo has **0
forks and 0 stars**, so nothing external would break — but it carries **40 published tags**, and every
commit after the first would change SHA, orphaning the references in 26 merged PRs. And it would not
achieve the goal: GitHub keeps unreferenced objects reachable by direct SHA until Support garbage-
collects them, so a force-push removes the data from the branch, not from GitHub.

Rewriting 40 tags and every SHA, breaking every clone, to not-actually-remove two RFC1918 addresses is
the wrong trade. **The thing worth doing is making the answer permanent instead of one-off.**

## What Changes

- New `scripts/scan-secrets.py` with two deliberately different modes:
  - **default — working tree.** Gates CI, exits 1 on any credential class. This is the part that can
    be kept clean, so this is the part that gates.
  - **`--history` — every blob in the full history.** Reports and exits 0. A secret removed in a later
    commit is still published and worth knowing about, but it cannot be fixed by a later commit, and a
    gate that can never go green is a gate everyone learns to ignore.
  - Private addresses and internal hostnames are reported as **operational detail**, never as a build
    failure.
- Wired into the CI `validate` job as *Secret scan (working tree)*.
- `documentation` → 3.0.1: the example connection string becomes `postgresql://REPLACE_ME:REPLACE_ME@`
  — the only string in the catalog that a scanner (or a reader) could mistake for a real credential.
- README documents both modes and why they differ.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — the catalog carries no credentials, enforced on the working
  tree, audited over history, with operational detail reported distinctly from secrets.

## Impact

- New `scripts/scan-secrets.py`; `.github/workflows/ci.yml`; `skills/documentation/references/examples.md`;
  README; regenerated wrappers.
- Working tree: **no credentials found**, and CI now keeps it that way.
- The published history retains two RFC1918 addresses and one sample connection string. That is
  recorded here as a decision, not an oversight — see below.

## The rewrite decision, recorded

Not done, deliberately. If the repository owner still wants those bytes gone from GitHub, the force-push
is the *smaller* half of the job: GitHub must also be asked to purge the unreferenced objects, which
requires the owner's authenticated request to Support. This change does not pre-empt that; it makes the
question answerable at any time with `python3 scripts/scan-secrets.py --history`.
