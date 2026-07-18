# gh recipes — GitHub Projects v2

Everything below is plumbing for the workflow in SKILL.md. `OWNER` = `project.owner`, `NUM` =
`project.number` from config.

## Preflight

```bash
gh auth status 2>&1 | grep -i 'token scopes'      # must contain 'project'
# missing → tell the user to run:  gh auth refresh -s project,read:project
```

## Discovery

```bash
gh project list --owner OWNER --format json --jq '.projects[] | {number, title}'
gh project view NUM --owner OWNER --format json --jq '{id, title}'          # .id = PROJECT_ID (PVT_…)
gh project field-list NUM --owner OWNER --format json                       # fields + select options
```

Resolve a field and a select option by name (case-insensitive):

```bash
gh project field-list NUM --owner OWNER --format json --jq '
  .fields[] | select(.name | ascii_downcase == "status")
  | {fieldId: .id, options: (.options // [])}'
# option id: .options[] | select(.name | ascii_downcase == "backlog") | .id
```

## Create and place the item

```bash
gh issue create -R OWNER/REPO --title "TITLE" --body-file /tmp/body.md \
  --label enhancement                        # only labels that exist: gh label list -R OWNER/REPO
# → prints the issue URL; capture it.

gh project item-add NUM --owner OWNER --url ISSUE_URL --format json --jq .id
# → ITEM_ID (PVTI_…)
```

## Set fields (one call per field)

```bash
# single-select (Status, Priority, Size):
gh project item-edit --project-id PROJECT_ID --id ITEM_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID

# number (Estimate):
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --number 5

# text / date:
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --text "…"
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --date 2026-07-18
```

## Verify (evidence for the report)

```bash
gh issue view ISSUE_URL --json number,title,labels,url
gh project item-list NUM --owner OWNER --format json --jq '
  .items[] | select(.content.url == "ISSUE_URL")
  | {id, status: .status, fields: .}'
```

## Org issue fields (Priority/Effort mirrored into the board)

A single-select field that `gh project field-list` returns with an **empty options array** is
usually not a Project custom field but an **organization issue field** mirrored into the board
(`updateProjectV2Field` fails with "Only custom fields can be updated"). Handle it at the issue
level instead:

```bash
# discover org-level fields + their option names/ids
gh api /orgs/OWNER/issue-fields

# set a value on the issue (value = option NAME as a string)
echo '[{"field_id": FIELD_ID, "value": "Medium"}]' | \
  gh api -X POST /repos/OWNER/REPO/issues/NUM/issue-field-values --input -

# verify
gh api /repos/OWNER/REPO/issues/NUM/issue-field-values \
  --jq '.[] | "\(.issue_field_name) = \(.single_select_option.name)"'
```

Only use option names returned by `/orgs/OWNER/issue-fields`. The board mirror may lag behind
`gh project item-list`; the issue-field-values endpoint is the source of truth.

## Duplicate check

```bash
gh issue list -R OWNER/REPO --search "KEY TERMS in:title,body" --state open \
  --json number,title,url --limit 10
```

## Recovery (partial failure — never delete the issue)

| Failed step | Recovery command to report |
|---|---|
| `item-add` | `gh project item-add NUM --owner OWNER --url ISSUE_URL` |
| `item-edit` on field X | the exact `gh project item-edit …` line with resolved IDs |
| label didn't exist | `gh label create NAME -R OWNER/REPO` then `gh issue edit URL --add-label NAME` |
