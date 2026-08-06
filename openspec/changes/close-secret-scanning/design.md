## Context

The catalog audit closed 32 skills and left exactly one item open: whether to rewrite git history to
purge operational values published in #33's predecessor. The question had been raised twice and
deferred twice, correctly — it is the owner's call — but "deferred" is not "answered".

## Goals / Non-Goals

**Goals**
- Answer what is actually in the history, with a measurement rather than a memory.
- Make the answer reproducible at any time instead of one-off.
- Prevent the next credential from entering the tree at all.

**Non-Goals**
- Not rewriting history. Reasoned below; the decision and its reasoning are recorded so it is a
  decision, not a lapse.
- Not gating on history. A gate that cannot pass teaches people to bypass gates.
- Not a vault or a rotation policy. This repository holds documentation, not running services.

## Decisions

**D1 — Measure before deciding.** The rewrite question was being argued from a memory of what was
committed. Scanning 1879 blobs across every commit turned it into a table: no keys, no tokens, no
private keys, no JWTs, no public addresses. The decision changes completely once the answer is "two
RFC1918 addresses and a teaching example" rather than "secrets".

**D2 — Do not rewrite, and say why in the proposal.** Cost: 40 published tags and every subsequent SHA,
orphaning references in 26 merged PRs. Benefit: none that the goal actually wants, because GitHub keeps
unreferenced objects reachable by SHA until Support purges them. A force-push would remove the data
from the branch and leave it on GitHub — the appearance of a fix.

**D3 — Two modes, and the split is the point.** Gating the working tree is achievable and therefore
enforceable. Gating history is neither: the only way to make it pass is the rewrite this change
declined. Reporting history without gating keeps the information available without creating a
permanently-red check.

**D4 — Report private addresses separately from credentials.** An RFC1918 address in a public repo is
worth removing and is not a breach. Folding it into the same failure class as an AWS key would train
everyone to read the scanner's output as noise, which is how real findings get missed.

**D5 — Fix the example rather than teach the scanner to ignore it.**
`postgresql://<user>:<password>@` is a documentation sample, and the honest fix is to make it
unmistakable — `REPLACE_ME` — instead of adding a suppression that would also hide a real one. The
requirement now says example credentials must be written so nobody has to guess.

**D6 — Leave the owner's half of the job stated.** If the bytes must go from GitHub, the force-push is
the smaller half; the owner has to ask Support to purge unreferenced objects. Saying so is more useful
than performing the half that does not achieve the goal.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| No credentials in the catalog; scanning and its two modes | `openspec/specs/skills-authoring` | establish here (new requirement) |
| Mechanical enforcement of authoring rules | `scripts/validate-skills.py` | unchanged; the secret scan is a sibling gate, not part of it |
| Not recording run values (addresses, org slugs) in a skill | `k8s-tune-resources` | already canonical — the standing rule added in #33 |
| Documentation examples and placeholders | `documentation` | already canonical — example corrected |

## Risks / Trade-offs

- [The scanner's patterns will miss a novel secret format] → true of every scanner; the classes cover
  the formats that actually appear in this repository's languages, and adding one is a line.
- [Placeholder detection could hide a real secret that contains the word "test"] → possible, and the
  reason the requirement pushes examples toward `REPLACE_ME` rather than relying on heuristics.
- [History keeps its two addresses] → recorded as a decision with its cost/benefit, and re-checkable
  in one command whenever the owner wants to revisit it.
