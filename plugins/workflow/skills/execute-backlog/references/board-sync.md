# Board sync — status transitions and linking

Reuses the `backlog` skill's config (`project.owner`, `project.number`, `fields.status`) and the
same runtime-ID discipline: resolve project/field/option/item IDs fresh each run (see the
`backlog` skill's `references/gh-projects.md` for the base recipes).

## Find the item for an issue

```bash
gh project item-list NUM --owner OWNER --format json --jq '
  .items[] | select(.content.url == "ISSUE_URL") | .id'
# not on the board → add it: gh project item-add NUM --owner OWNER --url ISSUE_URL
```

## Transitions — step by step, never skipping

The card advances one column per lifecycle event; it must never jump straight from Backlog to a
late column:

| Moment | Target column |
|---|---|
| Item created by the `backlog` skill | config `defaults.status` (usually "Backlog") |
| Completeness gate passed (item is executable) | config `columns.ready` (default: option named like "Ready") |
| Plan approved, implementation starting | config `columns.in_progress` (default: "In progress") |
| PR(s) opened | config `columns.review` (default: "In review") |
| PR merged by a human (issue auto-closed via `Closes #n`) | "Done" — **never set by the skill**; enable the board's built-in workflow *Item closed → Done* |

If a run starts with the card already past a column (e.g. resumed work, card manually moved),
apply only the transitions that are still ahead of its current position — never move a card
backwards without asking.

Optional config extension (backwards-compatible — absent keys fall back to name heuristics):

```yaml
columns:
  ready: Ready
  in_progress: In progress
  review: In review
```

Configured/heuristic name not among the Status options → warn, leave status untouched, continue
(board sync is never a reason to fail the execution).

```bash
gh project item-edit --project-id PROJECT_ID --id ITEM_ID \
  --field-id STATUS_FIELD_ID --single-select-option-id OPTION_ID
```

## PR ↔ issue linking

- Primary repo PR body: `Closes #<n>` (auto-closes on merge — the skill itself never closes).
- Secondary repo PRs: `Relates to <issue-url>` — `Closes` across repos does not auto-close and
  misleads reviewers.
- Final issue comment: list every PR, validation summary, and any approved scope deviations.

## Recovery

| Failure | Recovery |
|---|---|
| item-edit fails | report exact command with resolved IDs; execution result stands |
| PR created but issue comment failed | `gh issue comment <url> --body-file <file>` |
| item missing from board | `gh project item-add` then retry the transition |
