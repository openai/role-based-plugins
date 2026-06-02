# Data Analytics Onboarding Automations

Use this reference only when Data Analytics onboarding is setting up, checking, repairing, or later offering recurring Data Analytics automations. Keep this file as the runtime owner for automation setup. Keep ordinary onboarding flow, copy, and workflow choices in onboarding.md.

The automation catalog is ../plugin-author-config/automation-config.md. Always read it before setup and use its Name, Frequency, and Instructions; do not duplicate focused-skill workflow rules in automation prompts.

## Default Setup

After the current semantic layer has a stable target skill path and a usable, pollable source inventory, Data Analytics offers exactly one refresh automation unless the user skips or defers it:

| Automation id | Thread | Model/thinking | Schedule | Prompt | Kickoff |
| --- | --- | --- | --- | --- | --- |
| `weekly_semantic_layer_refresh` | Dedicated projectless thread titled `Semantic Layer Weekly Source Polling`, pinned | `model="gpt-5.5"`, `thinking="xhigh"` when supported | Weekly Monday 9:00 AM local time | Configured `Instructions` from `automation-config.md` | Send one setup kickoff to the pinned thread |

The refresh automation is optional: do not create it during the first onboarding orientation, before those prerequisites exist, or without explicit user approval unless the user already directly instructed Data Analytics to set up weekly polling.

If a tool cannot set model or thinking for heartbeat automations, set them on the target thread or Semantic Layer Weekly Source Polling kickoff when supported, record the limitation in onboarding state, and do not fall back to `gpt-5`.

The onboarding thread is never an automation target. Do not rename, pin, unpin, attach a heartbeat to, or send kickoff messages into the current onboarding thread while setting up Data Analytics automations. Only the dedicated automation target thread may be renamed, pinned, and attached to heartbeat automations.

## Fast Setup Checklist

After the user approves Data Analytics automation setup:

1. Discover `automation_update` and the thread tools: `create_thread`, `set_thread_title`, `set_thread_pinned`, and `send_message_to_thread`. Use `list_threads` only to reuse a clearly matching existing pinned automation thread with the exact configured title; never treat the current onboarding thread as reusable, even if it has been accidentally renamed or pinned.
2. Read `../plugin-author-config/automation-config.md` and identify the default automation id, name, frequency, and prompt.
3. For the default automation, create or reuse its dedicated projectless thread, capture the returned or reused thread id, set the exact configured title on only that thread id, pin only that thread id, and keep its thread id.
4. Create or update the automation with `kind="heartbeat"`, `destination="thread"`, the configured prompt, the configured cadence converted to the narrowest supported RRULE, `status="ACTIVE"`, and the exact `targetThreadId` of the dedicated automation thread.
5. Read back `$CODEX_HOME/automations/<automation_id>/automation.toml` when available. Confirm `kind = "heartbeat"`, the stored `target_thread_id` matches the pinned thread, the prompt and cadence match the config, and no cron-only workspace fields are present. Use `automation_update mode=view` only when file readback is unavailable.
6. Send one kickoff message only to the pinned Semantic Layer Weekly Source Polling thread after readback succeeds: run the configured semantic-layer source polling instructions now.
7. Update `onboarding-state.json` with only operational metadata: canonical automation id, `kind`, readback status, target thread id/title, target thread pin status, and semantic-layer refresh kickoff status/thread info. Do not copy semantic-layer content, polling results, source URLs, or source data into onboarding state.
8. Stop. Report the concise setup result and move to the first hero prompt step. Do not inspect hero workflow skill files or run another guided workflow until the user picks one.

## Readiness Rules

Only say the default automation setup is complete when the default automation is heartbeat-backed, targeted to its dedicated pinned thread, read back successfully, and the Semantic Layer Weekly Source Polling kickoff has started or was explicitly deferred by the user.

Do not mark setup complete after a plain cron automation, an automation attached to the onboarding thread, missing readback, missing target thread metadata, or a missing first Semantic Layer Weekly Source Polling kickoff.

If `automation_update` cannot persist a dedicated heartbeat thread after one repair attempt, use the fallback path: leave semantic-layer refresh manual, record the limitation as `environment_api_limitations`, and report it as a fallback rather than full setup.

Ask for explicit user approval before deleting automations, pausing automations, unpinning threads, or cleaning up duplicate/stale Data Analytics automation resources.

## Thin Prompts

Automation prompts and kickoff prompts should be thin launchers:

- Semantic Layer Weekly Source Polling: load and follow `semantic-layer/weekly-polling-automation.md` in scheduled source polling mode, using that reference's source inventory, update boundary, validation, and output contract.

Do not paste source precedence, evidence standards, update boundaries, validation commands, output examples, model names, reasoning effort, or focused-skill workflow contracts into automation prompts or kickoff messages.

## User-Facing Result

When setup succeeds, use this shape and continue to the next onboarding step:

```md
Semantic-layer refresh is set up and read back cleanly.

- **Semantic Layer Weekly Source Polling**: checks the saved source inventory each week and posts its review summary in the pinned **Semantic Layer Weekly Source Polling** thread. I also kicked off the first source polling run in that thread.
```

When setup cannot be completed, use this shape and continue to the next onboarding step:

```md
Weekly semantic-layer refresh is still manual because the automation could not be persisted and read back cleanly.

- **Current setup**: the semantic layer and source inventory are saved.
- **Refresh status**: manual for now. I recorded the setup blocker so refresh can be repaired later without repeating semantic-layer setup.
```
