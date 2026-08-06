## Context

The `r3f-*` family is the catalog's largest body of code — 267 `tsx` blocks across ten skills, 75% of
their total lines. Unlike prose doctrine, code either compiles or it does not, which makes this the
one skill family whose correctness is fully mechanically checkable. It had never been checked.

The instrument: extract every fenced `tsx`/`ts` block into its own module, install the real dependency
set, and run `tsc` over all of them. Errors are then classified — parse failures, unresolved imports,
type errors on `unknown` — and only the classes that a real project would also hit are counted as
defects.

## Goals / Non-Goals

**Goals**
- Every block tagged `tsx` either compiles against a stated stack, or is marked as an excerpt.
- The stack it compiles against is written in the skill, not assumed.
- The fix is verified by re-running the same compiler, not by inspection.

**Non-Goals**
- No teaching content changes. Not a single explanation, section, or example was rewritten — only
  imports, ref types, fence tags and excerpt markers.
- No structural split into `references/`. The size problem is real (556-1,145 lines, no `references/`
  anywhere in the family) and is left for its own proposal, so that these compile numbers stay
  attributable to this change alone.
- No migration to R3F v10 / drei 11. Both are alpha; the skills name the coming rename instead.

## Decisions

**D1 — Pin by verification, not by aspiration.** The block says "verified against" and names exact
versions, because that is what was actually run. A range or a "latest" claim would be unverifiable and
would rot silently — the precise failure mode this change is fixing.

**D2 — The compiler decides what is an excerpt.** A first pass marked blocks whose first code line
starts with `<`; 13 blocks slipped through because they open with an `import` and only then drop into
bare JSX. Rather than refine the heuristic, the remaining failures from the compiler run were marked
directly. The oracle is the tool, not a guess about the tool.

**D3 — `three/addons/…` over `three/examples/jsm/….js`.** Both resolve; `three/addons/*` is the
package's own export alias and is shorter. Verified that the extensionless form resolves in neither.

**D4 — Ref types are inferred from the JSX, not invented.** `<mesh ref={r}>` → `THREE.Mesh`. Where the
element is a drei component the type is `React.ComponentRef<typeof X>`, which stays correct across
drei versions instead of naming an internal class. 21 refs could not be inferred mechanically and were
handled by a second pass keyed on the element kind; 5 remain untyped and are reported rather than
guessed at.

**D5 — Report the residual instead of forcing it to zero.** 1 parse failure and 5 type failures
survive, in blocks that omit their own imports or use an untyped zustand store. Editing them blind
would risk changing what they teach, which D1 of the Non-Goals forbids. The numbers are stated in the
proposal.

**D6 — The authoring rule generalizes past r3f.** Any skill carrying code against a versioned external
API has this exposure. The rule goes into `skills-authoring`, where the gate can catch the next one.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| R3F scene setup, hooks, JSX elements | `r3f-fundamentals` | already canonical — code corrected only |
| Asset loading (`useGLTF`, `useLoader`, loader imports) | `r3f-assets` | already canonical — loader import paths corrected |
| Lighting, environment, shadows | `r3f-lighting` | already canonical — helper import corrected |
| Camera controls | `r3f-interaction` | already canonical — control refs typed |
| Custom shader materials | `r3f-shaders` | already canonical — material refs typed, one GLSL block retagged |
| Code-block and version-pin conventions for every skill | `openspec/specs/skills-authoring` | spec delta, not skill content |

## Risks / Trade-offs

- [The pin ages — three and drei ship often] → it names what was verified and when, which is falsifiable;
  an unpinned skill was silently wrong instead. Re-running the probe is the maintenance action.
- [`React.ComponentRef<typeof X>` is less readable than a concrete class] → but it survives a drei
  version bump, which a concrete internal class does not.
- [52 excerpt markers add a line to 52 blocks] → they are the only thing distinguishing "this is
  illustrative" from "this is broken", which is exactly the confusion the audit found.
- [Ten files touched with no structural change makes for a wide diff] → the diff is mechanical and each
  class of edit is independently verifiable by re-running the compiler.
