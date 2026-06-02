# Sales Automation Config

Plugin authors edit this file when adding, removing, renaming, or clarifying default Sales onboarding automations. Keep setup mechanics, thread creation, pinning, readback, duplicate cleanup, failure handling, and automation tool usage in `../references/automation.md`.

The default automations are installed during initial Sales onboarding. Later journey automations are offered only when a focused workflow reaches the right point. This config should stay friendly for plugin authors: name the automation, say how often it should run, and write the instructions. The dedicated thread title is derived from `Name`. Runtime mechanics such as heartbeat kind, RRULE conversion, tool calls, target thread ids, pinning, readback, cleanup, and state metadata belong in `../references/automation.md`.

## Automation Entry Shape

Every automation entry must use this shape:

```md
`automation_id`

- Name: human-facing automation name.
- Frequency: seller-facing cadence and local time.
- Instructions: thin launcher instructions for the scheduled run.
```

Do not add model, reasoning effort, heartbeat kind, RRULEs, tool names, user-specific target thread ids, canonical automation ids, install status, readback evidence, cleanup state, onboarding notification copy, or per-user preferred times here. Those belong in `../references/automation.md` or `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json`.

## Default Automations

`daily_sales_tips`

- Name: Sales Tips.
- Frequency: weekdays at 9:00 AM local time.
- Instructions: Load and follow `$sales:suggest-sales-next-step` in scheduled Sales check-in mode. Produce a short natural-language check-in on recent Sales work and the next Sales workflow worth trying, preserving the heartbeat automation response format.

`weekly_sales_company_research`

- Name: Sales Company Research.
- Frequency: weekly on Mondays at 9:00 AM local time.
- Instructions: Load and follow `$sales:sales-company-research` in scheduled research mode. Use the skill's dynamic source discovery, Sales user-context save policy, review gates, coverage-note guidance, and output contract, and compare against entries already flagged or saved from this pinned thread.

## Later Journey Automations

These automations are not installed during initial onboarding. Offer them only from the focused workflow journey that owns the behavior.

`daily_meeting_prep`

- Name: Sales Daily Meeting Prep.
- Frequency: weekdays at 9:00 AM local time.
- Instructions: Load and follow `$sales:prepare-for-meeting` in scheduled meeting prep mode. Inspect today's calendar, choose the highest-value meeting where prep would materially help while preferring customer-facing or account-related meetings, prepare only that meeting, and return DONT_NOTIFY when no qualifying meeting needs prep.
