## ADDED Requirements

### Requirement: Catalog composition after the quality review

The skills catalog SHALL contain 20 skills: the 17 retained/edited skills plus `backend-resilience`,
`openspec`, and `r3f-assets`, with `r3f-loaders` and `r3f-textures` removed (superseded by `r3f-assets`).

#### Scenario: npx discovery lists the full catalog

- **WHEN** `npx skills add <repo> --list` runs against the repository root
- **THEN** exactly 20 skills are discovered, including `backend-resilience`, `openspec` and `r3f-assets`
- **AND** `r3f-loaders` and `r3f-textures` are absent

### Requirement: Generic doctrine is reusable outside FiveM

Dependency-resilience doctrine SHALL live in `backend-resilience` (stack-agnostic principles with Python
examples) and adversarial-testing methodology SHALL live in `bug-hunter`'s stack-agnostic SKILL.md, so
non-FiveM projects can adopt them without pulling FiveM content.

#### Scenario: Python project adopts resilience patterns

- **WHEN** an agent working on a Python REST project needs fallback/negative-cache/retry guidance
- **THEN** `backend-resilience` provides the complete doctrine with no FiveM/Lua prerequisites
- **AND** `fivem-fallback` contains only the FiveM/Lua adaptation and links to `backend-resilience`

#### Scenario: Adversarial testing on a non-DriveZone stack

- **WHEN** an agent runs the bug-hunter rite on a project that is neither pytest nor FiveM
- **THEN** the SKILL.md mindset, universal checklist and output contract apply as-is
- **AND** stack specifics are opt-in reference files (`references/track-python-pytest.md`,
  `references/track-fivem-lua.md`)

### Requirement: r3f asset loading is a single skill

Model loading, texture loading/configuration and Suspense/caching patterns SHALL be covered by one
skill, `r3f-assets`.

#### Scenario: Texture task routes unambiguously

- **WHEN** a task involves loading textures or GLTF models in React Three Fiber
- **THEN** exactly one skill description (`r3f-assets`) claims that territory
