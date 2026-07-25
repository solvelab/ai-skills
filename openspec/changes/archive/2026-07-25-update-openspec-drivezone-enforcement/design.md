## Context

The DriveZone rite skill was written assuming the forked `schema.yaml` + templates make the three
gate sections structurally mandatory. Probe testing during the skills-rite rollout (PR #13) proved
CLI 1.6.0 never validates custom template sections; the repo closed the gap with
`scripts/validate-rite.sh` + a CI step. The skill must now tell the truth and carry the pattern.

## Goals / Non-Goals

**Goals:**
- Truthful enforcement statement: schema = advisory scaffolding; script + CI = hard gate.
- The hard-gate pattern documented once, in its canonical home (`openspec-drivezone`).

**Non-Goals:**
- Deploying the gate script into DriveZone repositories (DriveZoneFivem board work).
- Changing the three gate sections themselves (names, content, order stay as-is).

## Decisions

- **Keep the three gates unchanged; fix only the enforcement story.** Alternative considered:
  redesigning the gates around CLI-checkable structures (e.g. encoding gates as spec scenarios).
  Rejected — heavier, and the script+CI pattern already proves out in this repo.
- **Point to `scripts/validate-rite.sh` as the canonical example instead of inlining a full copy.**
  Alternative: embed the script verbatim in the skill. Rejected — inline copies drift; the
  single-canonical-home rule applies to code samples too. The skill shows the pattern (grep headings
  + `validate --all --strict`, CI wiring) and links the live script.
- **Version bump 2.0.0 → 2.1.0.** Content correction + new pattern section, no breaking change to
  how the skill is consumed.

## Canonical Home & Cross-Links (MANDATORY)

| Rule / doctrine touched | Canonical skill | Action (link / move / already canonical) |
|---|---|---|
| Hard rite-gate pattern (script + CI enforcing gate headings) | `openspec-drivezone` | establish here; link `scripts/validate-rite.sh` (ai-skills) as live example |
| Vanilla OpenSpec lifecycle & `--strict` semantics | `openspec` | link (already canonical) |
| Adversarial QA methodology behind the Tests gate | `bug-hunter` | link (already canonical, unchanged) |
| Fallback doctrine behind the Fallback gate | `backend-resilience` / `fivem-fallback` | link (already canonical, unchanged) |

## Risks / Trade-offs

- [Stale wrappers if `generate.sh` is skipped] → CI "Wrappers in sync" step fails the PR; task group
  covers regeneration explicitly.
- [Adopters read old cached copies of the skill] → version bump 2.1.0 signals the correction;
  changelog line in the PR body.
