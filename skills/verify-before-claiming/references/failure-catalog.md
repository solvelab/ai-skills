# Anti-pattern catalog

Read this when auditing a defect, or when a guess escaped and you are deciding whether the catalog
already covers it.

**Every row names the defect that earned it.** A row whose origin column is empty is removed, not
kept — `openspec/specs/skills-authoring/spec.md` → *Checklists are scored against field defects*:
"A checklist item without a traceable origin SHALL NOT be added." Every seed row below is citable
inside this repository, and each was re-read at HEAD `c965689` on 2026-08-06 before being written
down here.

| Anti-pattern | What it looks like | The defect that earned it |
|---|---|---|
| **Assumed enforcement** | trusting that a tool checks what its name implies | `openspec validate --strict` on CLI 1.6.0 validates delta-spec format but **not** custom template sections, so this repo's mandatory rite groups would have been advisory. Recorded in `scripts/validate-rite.sh`, which exists solely to make them structural. |
| **Negative claim from an unread source** | "that API does not exist", asserted without opening the SDK | The `withoutIO` myth: the CSP SDK marks that flag for three other Lua contexts, not for online scripts, which measurably do have web and file APIs. `skills/assettoserver-csp-lua/SKILL.md` records that a false "the API doesn't exist" claim pushes the next reader into bad architecture. |
| **Layout written from memory** | a directory tree in a README that no listing produced | Measured on a production repo: a README tree written without its `src/` prefix made every path unresolvable and one entry had been renamed months earlier — 9 of 10 entries wrong, in the block a reader trusts most. `skills/documentation/SKILL.md`. |
| **Assumed framework default** | a limit or a status code stated without measuring stock behavior | Measured on a stock API with no explicit limits: a 2 KB body of nested brackets returned **500**, and a 20 MB flat JSON body returned **200**, fully buffered — the opposite of what "sensible defaults" implies. `skills/api-resilience-testing/SKILL.md`. |
| **Guessed default masking a detection failure** | a fallback constant that fires exactly when detection failed | The target-framework fallback trap: "it is used exactly when detection failed, which is when you can least afford a guess." `skills/assettoserver-plugin/SKILL.md`. |
| **Plausible-but-wrong command** | a step stated without its command, executed by whatever looks obvious | Resolving an issue's linked pull requests by text search instead of the issue's own link graph. Measured in `skills/backlog/references/gh-projects.md`: a verbatim title search for an issue whose title contained punctuation returned **zero** results, so a search-based check would have reported "no duplicate" while one existed. |
| **Version drift with a silent symptom** | a dependency bumped to a release that fails quietly | conventional-changelog-conventionalcommits@9 is silently incompatible with the release-notes generator and produces **empty** release notes; pinned to @8 with that reason written in the workflow. `.github/workflows/ci.yml`. |
| **Unobservable trigger assumed observable** | a rule keyed on something the agent cannot actually see | "This repo is worked on by agents" is not observable from a checkout — measured: with that phrasing, **no run** produced the file it was supposed to trigger. `skills/documentation/SKILL.md`. |
| **Hand-copied fact that drifted** | a count in the docs that no longer matches the thing it counts | This catalog described itself as having 27 skills in one manifest and 30 in the README while the tree held 32, and described its own validator as running six checks while it implemented eight. Found by running `ls skills \| wc -l` instead of trusting the sentence. |

## Adding and removing rows

**Add** a row when a guess ships and someone catches it. Record both the class **and** the incident
that earned it — the incident is what lets a future reader judge whether the row still applies.

**Remove** a row when its origin column cannot be filled. A plausible-sounding failure mode with no
traceable defect behind it is itself an unverified claim, and a catalog that accumulates those
teaches the reader to skim past all of them.

A catalog that never grows is a catalog that stopped finding things.
