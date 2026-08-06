# Change: Make the r3f code blocks compile, and say what they compile against

## Why

The ten `r3f-*` skills are 8,352 lines, 75% of which is fenced code — 267 blocks tagged `tsx`. None of
them states a version. Not one line in 8,352 pins `three`, `@react-three/fiber`, `@react-three/drei`,
or `react`, in a stack that is mid-migration: R3F v10 (alpha) renames `state.gl` to `state.renderer`
and moves off `THREE.Clock`, and drei 11 (alpha) targets WebGPU. A reader cannot tell which era the
code targets, and neither can an agent.

Every block was extracted and compiled against the real stack — `three@0.185.1`,
`@react-three/fiber@9.7.0`, `@react-three/drei@10.7.8`, `react@19.2.8`, TypeScript with `jsx:
react-jsx`. **66 of 267 blocks tagged `tsx` (24.7%) were not valid TSX as written:**

| defect | count | what it was |
|---|---|---|
| does not parse | 33 | bare JSX excerpts and two blocks that were not TypeScript at all (one CSS, one GLSL), all tagged `tsx` |
| unresolved import | 7 | `three/examples/jsm/loaders/GLTFLoader` and siblings — extensionless, which stopped resolving; verified that `three/addons/loaders/GLTFLoader.js` does resolve |
| does not typecheck | 26 | `useRef()` with no type parameter, so every `ref.current.position` is an error on `unknown` |

The typing was also internally inconsistent: 70 bare `useRef()` against 27 already-typed
`useRef<THREE.Mesh>(null)` — the same family teaching both.

After the fixes, recompiled against the same stack:

| | before | after |
|---|---|---|
| blocks that do not parse | 33 | **1** |
| unresolved imports | 7 | **0** |
| untyped-ref failures | 26 | **5** |

The residual 5 are blocks that omit their own imports or use an untyped zustand store; the residual 1
is a fragment. Two remaining unresolved imports in the probe (`lodash/throttle`,
`react-error-boundary`) are third-party packages the probe did not install — not defects.

## What Changes

- All ten `r3f-*` skills gain a **verified-against block** under the title naming the exact stack the
  code was compiled against, the meaning of the `tsx` tag, and the R3F v10 rename that is coming.
- **8 stale imports** rewritten from `three/examples/jsm/<path>` to `three/addons/<path>.js`.
- **49 + 14 `useRef()` calls typed**, inferring the type from the element the ref is attached to
  (`<mesh>` → `THREE.Mesh`, drei components → `React.ComponentRef<typeof X>`, custom materials →
  `THREE.ShaderMaterial`).
- **52 illustrative fragments marked** with a leading `// excerpt — not a complete module` line, so a
  compile check can skip what was never meant to be a module. The compiler picked which ones: any
  block that failed to parse.
- **2 blocks retagged** to the language they actually are (`css`, `glsl`).
- No prose, structure, or teaching content changed. This change only makes the code true.

## Capabilities

### New Capabilities

### Modified Capabilities

- `skills-authoring`: ADDED requirement — a code block tagged with a compiled language SHALL be a
  complete, compiling module or be marked as an excerpt, and a skill whose content targets a versioned
  external API SHALL state the version it was verified against.

## Impact

- `skills/r3f-*/SKILL.md` (10 files) and every regenerated wrapper tree (`claude/`, `codex/`,
  `cursor/`, `copilot/`, `plugins/`).
- README: the Game section gains a note that the r3f code is version-pinned and compile-checked.
- Consumers: code copied from these skills now typechecks under `strict` in a project on the pinned
  stack, instead of erroring on `unknown`.
- Out of scope, deliberately: the size problem. These skills remain 556-1,145 lines with no
  `references/` directory. Splitting them is a separate proposal — this one changes no structure so
  the compile results stay attributable.
