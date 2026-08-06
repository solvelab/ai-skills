## 1. Version pins

- [x] 1.1 Add a "Verified against" block under the title of all ten `r3f-*` skills naming
      `three@0.185`, `@react-three/fiber@9.7`, `@react-three/drei@10.7`, `react@19.2`
- [x] 1.2 State in that block what the `tsx` tag means (complete module, typechecks) and what
      `// excerpt` means
- [x] 1.3 Name the R3F v10 `state.gl` → `state.renderer` / `THREE.Timer` migration as a known
      upcoming break

## 2. Compile failures

- [x] 2.1 Rewrite the 8 `three/examples/jsm/<path>` imports to `three/addons/<path>.js`; verify both
      forms against the installed package
- [x] 2.2 Type every inferable bare `useRef()` from the element it is attached to
- [x] 2.3 Second pass for drei components (`React.ComponentRef<typeof X>`), custom materials
      (`THREE.ShaderMaterial`) and remaining lights
- [x] 2.4 Mark every block that fails to parse with `// excerpt — not a complete module`, using the
      compiler output to select them
- [x] 2.5 Retag the two blocks that are not TypeScript (`css`, `glsl`)
- [x] 2.6 Re-extract and recompile against the same stack; record before/after per defect class

## 3. Quality Gates (MANDATORY)

- [x] Q.1 Frontmatter uniform on all ten skills: name == directory, folded description,
      metadata.author solvelab, semver metadata.version, category in the controlled set, license MIT,
      compatibility present
- [x] Q.2 All touched skill content in English (catalog locale)
- [x] Q.3 Description triggers and every "For X use Y" cross-reference between the r3f skills survive
      unchanged
- [x] Q.4 No teaching content altered — the diff contains only imports, ref type parameters, fence
      tags, excerpt markers and the pin block
- [x] Q.5 Every quantified claim carries its measured number and conditions (skills-authoring:
      Simulated failure behaviour)
- [x] Q.6 No skill description promises a policy its body contradicts (skills-authoring: Description
      agrees with body)
- [x] Q.7 README Game section notes the pin and the compile check

## 4. Validation & Closure (MANDATORY)

- [x] V.1 `openspec validate harden-r3f-skills --strict` green
- [x] V.2 `scripts/validate-rite.sh` green
- [x] V.3 Wrappers in sync: `./generate.sh` then clean `git diff` on generated trees
- [x] V.4 CI frontmatter check passes locally on every `skills/*/SKILL.md`
- [x] V.5 Recompile proves the fix: parse failures 33 → 1, unresolved imports 7 → 0, untyped-ref
      failures 26 → 5, with the residual explained
- [x] V.6 Confirm no regression was introduced: every block now using `THREE.` without importing it
      already did so before this change
- [x] V.7 `openspec archive harden-r3f-skills --yes` after review
