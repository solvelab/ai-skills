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

## Transitions

| Moment | Target column |
|---|---|
| Plan approved, work starting | config `columns.in_progress` (default: option named like "In progress") |
| PR(s) opened | config `columns.review` (default: option named like "In review") |

Optional config extension (backwards-compatible — absent keys fall back to name heuristics):

```yaml
columns:
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
