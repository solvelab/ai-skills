# Design — the two tracks the generation and scoring layers had not reached

## Context

The Python track carries `hypothesis 6.167.1` and `cosmic-ray 8.7.0`, each with the command scoped to
the changed module and the plausible-but-wrong command named. The Lua and .NET tracks carry neither,
because nothing was probed in those ecosystems when the layers were written.

This change probes them and writes down what it found, including where it found nothing.

## Goals / Non-Goals

**Goals:**

- Each track answers the two layers instead of ignoring them.
- Every statement about a tool is a probe result with the command that produced it.
- Where the ecosystem has no tool, the absence is recorded with the search that established it, so
  the next reader does not repeat it.

**Non-Goals:**

- Prescribing a command that was not run here. A named tool with no probe is the defect the rite was
  extended to prevent.
- Changing the stack-agnostic SKILL.md beyond its version block: the criteria and the ceilings are
  published and correct.
- New tracks, and any CI gate.

## Decisions

**D1 — Lua gets a declaration, not a prescription, and the declaration is probed.** LuaRocks 3.13.0
answers for the generation layer directly: `lua-quickcheck supports only Lua 5.1 and Lua 5.2`. CfxLua,
the runtime the track targets, is 5.4-based, so the ecosystem's property-based library does not reach
it. For the scoring layer there is nothing at all to reach: three exact-name searches on LuaRocks
returned empty result sets. The track says that, with the commands, rather than naming a tool nobody
here ran.

**D2 — What Lua does instead is stated, not left implied.** With no generator and no scorer, the
boundary witnesses nothing else will produce have to be written by hand. That is a weaker position
than the Python track's and the track says so; a reader who believes the layers are universal will
otherwise assume a tool exists and go looking.

**D3 — The .NET track answers the scoring question with what it already prescribes.** The failure
class that track exists for is "compiles, passes unit tests, dies inside the host". Mutating the
source scores the suite over logic; it says nothing about whether the published assembly survives the
host's reflection path. The scoring analogue already in the track is the Mono.Cecil assert set read
from the published DLL plus the `plugin-rite-status.json` proof the deploy gate refuses to skip. That
is written as the answer, with the boundary of what it does not cover.

**D4 — Stryker.NET is named as unprobed, or not named at all.** No .NET SDK was available here
(`command -v dotnet` -> absent), so nothing about it can be prescribed. It is mentioned only as the
tool a reader will reach for, with the explicit statement that this catalog has not run it, which is
the honest form of a pointer.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Enumerate / generate / score, and the condition each layer pays under | `bug-hunter` | already canonical — this change only completes its tracks |
| Report what could not be established instead of substituting a plausible answer | `verify-before-claiming` | link — D1 and D4 apply it |
| The trust boundary and the runtime rules the Lua track exercises | `fivem-lua` | link — already cross-linked from the track |
| The two-contract pinning and forbidden constructs of the .NET host | `assettoserver-plugin` | link — already cross-linked from the track |

## Risks / Trade-offs

- **A declaration reads as weaker than a command.** It is weaker, and that is the true state; the
  alternative is a tool named from memory, which is the failure this rite was written against.
- **The Lua answer ages.** A property-based library that supports 5.4 could appear. The probe carries
  its date and the command, so the next reader can re-run it in one line instead of trusting it.
- **The .NET answer could be read as "scoring does not apply to .NET".** It applies; what the track
  says is that the source-mutation form of it is not what that stack's failure class needs, and the
  unprobed status of Stryker.NET is stated rather than hidden.

## Open questions

- Whether `lua-quickcheck` would work against CfxLua if built for 5.4 was not established: no
  5.4 rock exists to install, and building one is outside this change.
