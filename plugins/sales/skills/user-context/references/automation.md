# Sales Onboarding Automations

Use this reference only when Sales onboarding is setting up, checking, repairing, or later offering recurring Sales automations. Keep this file as the runtime owner for automation setup. Keep ordinary onboarding flow, copy, and workflow choices in `onboarding.md`.

The automation catalog is `../plugin-author-config/automation-config.md`. Always read it before setup and use its `Name`, `Frequency`, and `Instructions`; do not duplicate focused-skill workflow rules in automation prompts.

## Default Setup

Initial Sales onboarding sets up exactly two automations unless the user skips or defers them:

| Automation id | Thread | Model/thinking | Schedule | Prompt | Kickoff |
| --- | --- | --- | --- | --- | --- |
| `weekly_sales_company_research` | Dedicated projectless thread titled `Sales Company Research`, pinned | `model="gpt-5.5"`, `thinking="xhigh"` when supported | Weekly Monday 9:00 AM local time | Configured `Instructions` from `automation-config.md` | Send one setup kickoff to the pinned thread |
| `daily_sales_tips` | Dedicated projectless thread titled `Sales Tips`, pinned | `model="gpt-5.5"`, `thinking="low"` when supported | Weekdays 9:00 AM local time | Configured `Instructions` from `automation-config.md` | No setup kickoff; let the first scheduled check-in run on its own |

Do not install `daily_meeting_prep` during initial onboarding. Offer Sales Daily Meeting Prep later from the Prepare For Meeting journey only, using a dedicated pinned thread titled `Sales Daily Meeting Prep`, `model="gpt-5.5"`, and `thinking="low"` when supported.

If a tool cannot set model or thinking for heartbeat automations, set them on the target thread or Sales Company Research kickoff when supported, record the limitation in onboarding state, and do not fall back to `gpt-5`.

The onboarding thread is never an automation target. Do not rename, pin, unpin, attach a heartbeat to, or send kickoff messages into the current onboarding thread while setting up Sales automations. Only the two dedicated automation target threads may be renamed, pinned, and attached to heartbeat automations.

## Fast Setup Checklist

After the user approves Sales automation setup:

1. Discover `automation_update` and the thread tools: `create_thread`, `set_thread_title`, `set_thread_pinned`, and `send_message_to_thread`. Use `list_threads` only to reuse a clearly matching existing pinned automation thread with the exact configured title; never treat the current onboarding thread as reusable, even if it has been accidentally renamed or pinned.
2. Read `../plugin-author-config/automation-config.md` and identify the two default automation ids, names, frequencies, and prompts.
3. For each default automation, create or reuse its dedicated projectless thread, capture the returned or reused thread id, set the exact configured title on only that thread id, pin only that thread id, and keep its thread id.
4. Create or update the automation with `kind="heartbeat"`, `destination="thread"`, the configured prompt, the configured cadence converted to the narrowest supported RRULE, `status="ACTIVE"`, and the exact `targetThreadId` of the dedicated automation thread.
5. Read back `$CODEX_HOME/automations/<automation_id>/automation.toml` when available. Confirm `kind = "heartbeat"`, the stored `target_thread_id` matches the pinned thread, the prompt and cadence match the config, and no cron-only workspace fields are present. Use `automation_update mode=view` only when file readback is unavailable.
6. Send one kickoff message only to the pinned Sales Company Research thread after readback succeeds: tell `$sales:sales-company-research` to run scheduled research mode now. Do not send an immediate Sales Tips kickoff during onboarding; the first Sales Tips check-in should happen on its normal weekday schedule so it does not interrupt guided onboarding.
7. Update `onboarding-state.json` with only operational metadata: canonical automation id, `kind`, readback status, target thread id/title, target thread pin status, Sales Tips schedule-only disposition when useful, and `initial_resource_discovery` status/thread info. Do not copy tip text, research results, saved resources, source URLs, or customer details into onboarding state.
8. Stop. Report the concise setup result and move to the first hero workflow chooser. Do not inspect hero workflow skill files or run another guided workflow until the user picks one.

## Readiness Rules

Only say the default automation setup is complete when both default automations are heartbeat-backed, targeted to their dedicated pinned threads, read back successfully, and the Sales Company Research kickoff has started or was explicitly deferred by the user. Sales Tips does not need an immediate kickoff; it is complete when the scheduled automation is installed, read back, and pointed at its pinned thread.

Do not mark setup complete after a plain cron automation, an automation attached to the onboarding thread, missing readback, missing target thread metadata, or a missing first Sales Company Research kickoff.

If `automation_update` cannot persist a dedicated heartbeat thread after one repair attempt, use the fallback path: set up only Sales Tips with the configured prompt and cadence, skip Sales Company Research and the research kickoff, record the limitation as `environment_api_limitations`, and report it as a fallback rather than full setup.

Ask for explicit user approval before deleting automations, pausing automations, unpinning threads, or cleaning up duplicate/stale Sales automation resources.

## Thin Prompts

Automation prompts and kickoff prompts should be thin launchers:

- Sales Company Research: load and follow `$sales:sales-company-research` in scheduled research mode, using that skill's dynamic discovery and output contract.
- Sales Tips automation prompt: load and follow `$sales:suggest-sales-next-step` in scheduled Sales check-in mode. Do not send this as a setup kickoff during onboarding.

Do not paste source-family lists, ranking rules, save gates, output examples, model names, reasoning effort, or focused-skill workflow contracts into automation prompts or kickoff messages.

## User-Facing Result

When full setup succeeds, use this shape and then stop:

```md
Automations are set up and read back cleanly.

- **Sales Company Research**: deeply searches across your company context and saves key resources to improve speed and correctness. It runs weekly on Mondays at 9:00 AM local time. I also kicked off the first research run in the pinned **Sales Company Research** thread.
- **Sales Tips**: looks at how you've been using Codex and gives you one practical Sales workflow to try next. It runs weekdays at 9:00 AM local time, starting with its next scheduled run.

Core onboarding is done. Pick a workflow to try first:

1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.
2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.
3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.
```

When fallback Sales Tips setup succeeds, use this shape:

```md
The full Sales automation setup hit an environment/API limitation, so I used the fallback path and set up Sales Tips instead.

- **Sales Tips**: looks at how you've been using Codex and gives you one practical Sales workflow to try next. It runs weekdays at 9:00 AM local time, starting with its next scheduled run.
- **Skipped for now**: Sales Company Research was not set up in this environment, so I skipped the context-gathering kickoff and did not ask you for source links here.

Core onboarding is done with the fallback automation. Pick a workflow to try first:

1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.
2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.
3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.
```
