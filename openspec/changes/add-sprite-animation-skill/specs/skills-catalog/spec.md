## ADDED Requirements

### Requirement: Sprite sheet animation has a canonical home

The catalog SHALL carry one skill that governs the reproduction of ready-made frame-sheet art:
reading the sheet, normalising scale between pose groups drawn at different zooms, the single
cell shared by every pose, the frame rate, and the computation that keeps a walking figure's feet
from sliding. That skill is `sprite-animation`.

Every rule it publishes SHALL carry the defect that produced it, measured, and every number SHALL
be published as the formula that derives it rather than as a constant, because stride length,
travel distance and figure height differ per project. This is the catalog's general rule
*Prescribed numbers carry the rule that produces them* applied to this subject.

The skill SHALL state its boundary against `svg-animation` in both directions: `svg-animation`
owns understanding an object before drawing it and choosing the technology when no art exists;
`sprite-animation` owns replaying art that already exists as numbered frames. Neither reproduces
the other's mechanisms.

#### Scenario: A walking figure's feet slide and nothing fails

- **WHEN** an agent animates a walk cycle by picking a cycle duration and a travel duration
  independently
- **THEN** the skill supplies the computation that binds them —
  `speed = 2 × stride × fps ÷ frames_per_cycle` and `duration = distance ÷ speed` — so the defect
  is prevented rather than discovered on screen, since no test, typecheck or lint fails when the
  feet slide

#### Scenario: Pose groups drawn at different zooms are matched by an invalid proxy

- **WHEN** an agent tries to match the scale of a side-view pose group against a front-view group
  by measuring hair width, face width or any other single feature
- **THEN** the skill states that no such proxy is valid across viewing angles, and prescribes
  comparing the same figure side by side at candidate scales, aligned at the feet

#### Scenario: The walking direction is inferred from the drawing

- **WHEN** a sheet contains several pose groups and an agent decides which way a figure faces by
  looking at the frames
- **THEN** the skill requires one sheet per direction with the direction in the file name, so the
  question of which way the figure faces is not open to interpretation

#### Scenario: The frame rate does not divide the compositor rate

- **WHEN** a sprite animation is given a frame rate that does not divide 60
- **THEN** the skill states that one frame lasts two compositor updates and the next lasts three,
  and restricts the rate to divisors of 60

#### Scenario: The catalog gains a skill and its composition is updated with it

- **WHEN** `sprite-animation` is added to `skills/`
- **THEN** the README skill table and count, `generate.sh`, the embedding plugin and the
  `claude/skills/` mirror are updated in the same change, so `npx skills add <repo> --list` finds
  it with no orphan and no stale count
