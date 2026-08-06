## Context

Every audit in this catalog stopped at the same five skills with the same reason: no Assetto Corsa
server, no FXServer, no DriveZone repos. Coverage was honestly reported as 26 of 31 — but "cannot run
it" had quietly become "cannot audit it", and those are different claims.

## Goals / Non-Goals

**Goals**
- Audit the five without their runtimes, using the lenses that do not need one.
- Fix what those lenses find, with probed evidence.
- Say plainly which of the five needed no change, rather than editing to make a number move.

**Non-Goals**
- Not simulating a runtime. Nothing here pretends to have executed a plugin or a FiveM resource.
- Not restructuring any of the five. Their layout, references and doctrine stand.
- Not manufacturing findings for the three that came out clean.

## Decisions

**D1 — Probe the public half of a runtime claim.** "The type is missing in the host runtime" reads
unverifiable, but it decomposes into two checkable facts: which .NET version introduced the type, and
which framework the pinned upstream tag targets. Both are public. Together they settled the question
without an Assetto Corsa install.

**D2 — A fallback default that contradicts a constraint is worse than no default.** The `net9.0`
fallback applies exactly when TFM detection failed — the moment a wrong guess is most likely to be
believed. It is corrected to the probed value, and the reasoning is written next to it so the next
person bumping the pin does not reintroduce a convenient default.

**D3 — Version-scope the ban instead of deleting or freezing it.** `System.Threading.Lock` is genuinely
absent on net8.0 and genuinely present on net9.0. A rule that is true only under a condition has to
state the condition, or it becomes false the day the pin moves — silently, since the Cecil assert
enforcing it would keep passing.

**D4 — Apply the newest adversarial lens to the skills that never got it.** The five defect classes
added to `bug-hunter` in #37 came from defects found elsewhere in the catalog. `fivem-lua`'s
trust-boundary section fails *Observable degradation* squarely: it validates and returns, and the word
"log" does not appear anywhere in the skill.

**D5 — Silence at a trust boundary is the defect, not the rejection.** Dropping a forged event is
correct. Dropping it with no counter means the section's own instruction to "rate-limit it" has
nothing to rate-limit on, and an attack is indistinguishable from quiet. The fix is a counter and a
log line, not stricter validation.

**D6 — Report the three that needed nothing.** `assettoserver-ops` and `assettoserver-csp-lua` were
read in full and scanned with every lens; both already carry dense enforcement statements and none of
the defect classes applies cleanly. `openspec-drivezone` was corrected by an earlier change. Editing
them to make the audit look thorough would be the failure this catalog's rules were written to remove.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| AssettoServer plugin build contract and forbidden constructs | `assettoserver-plugin` | already canonical — TFM corrected, Lock row version-scoped |
| FiveM trust boundary (`source`, validation) | `fivem-lua` | already canonical — rejection observability added |
| Adversarial defect classes applied as a lens | `bug-hunter` | link (already canonical) |
| Fallback observability in a service | `backend-resilience` | link (already canonical) — same principle, different runtime |
| Cecil-based forbidden-construct gate | `bug-hunter/references/track-dotnet-plugin.md` | unchanged; the scoping note points at it |

## Risks / Trade-offs

- [The TFM pin ages when upstream moves to .NET 9] → that is precisely why the Lock row is now
  version-scoped and says what to do at the bump, instead of carrying a silently-false ban.
- [A rejection counter is state a resource must reset] → the rule says to window it; unbounded
  counters were the failure mode `log-event-collector` already documented.
- [Three of five needed no edit] → stated as a result rather than hidden, so the coverage number
  means what it says.
