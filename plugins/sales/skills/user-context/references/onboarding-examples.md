# Sales Onboarding Examples

Use these compact cases to audit the core onboarding experience. They are regression anchors, not scripts. Governing rules remain in `onboarding.md`, `plugin-memory.md`, the relevant skill's experience guidance, `../plugin-author-config/source-category-config.json`, `../plugin-author-config/automation-config.md`, `source-category-runtime.md`, and `automation.md`.

## Case 1: Direct Onboarding Orientation

User says:

```text
@sales help me get started
```

Expected behavior:

- Open with a compact Sales onboarding orientation that explains what the plugin does, how onboarding works, and that the user can answer `yes`, `skip`, or send a link at each step.
- Do not initialize state files, create the user-context scaffold, inspect connectors, audit conflicts, run discovery, spawn subagents, create background threads, or install automations before sending the first orientation message.
- Make `Orientation` the first visible item, then `Connector setup/confirmation`; do not inspect connectors before the first orientation just to populate setup state.
- Explain that active or obvious one-app sources are informational only and will be tried only when a workflow needs them. Ask the user for help only where multiple apps are plausible, no app was found, or IT/admin action may be needed.
- Include `Sales tools` only when overlapping broad Sales plugins or sales-specific skills create real or likely conflicts; omit this bullet after a clean audit.
- Offer one concrete guided next action with real context, never placeholders such as `<paste notes>` or `<company>`, while mirroring the canonical high-level onboarding checklist into the built-in thread task list when available: `Orientation`, `Connector setup/confirmation`, `Sales automation setup`, `First hero prompt`, and `Other hero prompts`.
- Use `# Sales Onboarding`, then a high-level prose paragraph that does not expose saved state paths, cache paths, or internal onboarding status.
- Explain guided workflows only when the flow reaches demos or the user asks for the full plan.
- End with one clear action close and show only the current action the user can approve now. Use a compact `**Next Step**` label only when the step needs the label; a self-contained numbered choice set can stand on its own. If the current step has open questions, make resolving them their own step and include those questions in the action close; if they are non-blocking, say what `okay` will do by default. Do not combine meaningful open questions with a first-time workflow introduction. When the next step introduces a workflow for the first time, put the explanation in primary content before the action close; the action frame should stay small.
- Do not add a time estimate to meeting-notes/provider connection by default. For Sales Company Research, say it saves high-confidence Sales memory in its pinned thread and asks for review only for uncertain, sensitive, or lower-confidence candidates.

## Case 2: High-Intent First Run

User says:

```text
@sales prep me for my 3pm customer meeting
```

Expected behavior:

- Begin the requested Prepare For Meeting workflow first and return a best-effort answer from available sources, even when no saved Sales context exists.
- Use calendar and source evidence if available rather than stopping at onboarding.
- Keep the artifact useful even while onboarding is active.
- Add the `## Sales Setup Required` CTA after the brief only when onboarding has not started, unless the request is already being answered inside a guided onboarding flow. If onboarding is already active, preserve the skill's own final natural continuation and do not ask whether to start onboarding.
- Add a `**Context Gap**` note only when missing saved context, source access, or setup materially weakens the prepare-for-meeting answer. The note should name the exact missing information and the specific improvement it would unlock.
- Do not add a generic setup note; the onboarding CTA should say setup is required before Sales can reliably use connected sources and authoritative company context, and end with the exact line: Reply `start` to continue.
- If the meeting prep counts as the first onboarding guided workflow, start with one short unheaded transition sentence such as `Here's your meeting prep, using {source coverage and assumptions}.`, then the actual output. End with one compact feedback CTA asking what the user would change to make it clearer or more useful, or whether to save any reusable preference and move on.

## Case 3: Durable Preference During Onboarding

User says:

```text
@sales onboard me, and remember that I prefer concise prep briefs with risks first.
```

Expected behavior:

- Save the low-risk Sales plugin-scoped preference immediately.
- Start the recap with `Saved Sales Plugin Memory.`
- If this is the first plugin-memory mention in onboarding, explain that plugin memory can remember trusted resources and answer/style preferences for future Sales workflows before listing the exact saved preference.
- Continue onboarding with the saved preference reflected in the next useful guided workflow or setup suggestion.

## Case 4: Sales Automations Are Automatic And Approval-Gated

User says:

```text
okay
```

Context: the previous onboarding response explained that recurring Sales workflows can run in the background, listed Sales Company Research and Sales Tips with their configured cadences, and ended with `Should I set those up? They'll run in a different thread and notify you when they have something to review.` The visible step was `Sales automation setup`.

Expected behavior:

- Read `automation.md` and `../plugin-author-config/automation-config.md`.
- Install or repair `weekly_sales_company_research` and `daily_sales_tips` unless the user has already declined, skipped, or deferred a specific automation.
- Mention each configured automation once with its cadence: Sales Company Research runs weekly on Mondays at 9:00 AM local time, and Sales Tips runs weekdays at 9:00 AM local time.
- Use the configured dedicated pinned thread named `Sales Company Research`.
- Confirm the automation prompt is a thin launcher for `$sales:sales-company-research`; the skill owns dynamic source discovery, source-family coverage, ranking, save gates, and output copy.
- Explain that Sales Company Research compares against entries already flagged or saved from that pinned thread, saves high-confidence plugin memory by default, and asks for review only for uncertain, sensitive, or lower-confidence candidates.
- Record automation metadata for all three automations in `onboarding-state.json`.
- Do not kick off Sales Tips during onboarding; install and read back the automation, then let its first check-in happen on the normal weekday schedule.
- Immediately kick off one company research search in the pinned `Sales Company Research` thread, record it under `initial_resource_discovery`, and tell the user it is working in the background and visible in the `Pinned` section of the left sidebar.
- Continue to the next onboarding step after readback succeeds. Mention discovery-thread status as a separate `FYI:` line, then offer the first hero prompt choice card with Prepare For Meeting, Follow Up After Call, and Prioritize Accounts. Load each skill's experience guidance for option wording and include realistic `@Sales` examples when introducing a selected workflow. The three numbered choices can be the action close by themselves; do not add a redundant final line asking the user to pick `1`, `2`, or `3`.

## Case 5: Ordinary Workflow While Onboarding Is Active

User says:

```text
@sales who knows about enterprise SSO migration?
```

Expected behavior:

- Complete the requested find-key-internal-sources workflow.
- Do not interrupt with full onboarding.
- Do not include the `## Sales Setup Required` start CTA when onboarding is already active. Preserve the skill's own final natural continuation, and optionally add a short non-final note that onboarding is still in progress.
- If onboarding is quiet or complete, produce the requested Sales artifact directly and end with one useful seller action, not an onboarding recap.
- If this completed one of the initial guided workflows, offer a beginner-friendly `Agent Journey` walkthrough or the next concrete setup or workflow step.

## Case 6: Onboarding Status Check

User says:

```text
@sales have we onboarded yet
```

Expected behavior:

- Answer the status directly from `user-context.md` and `onboarding-state.json`, or say onboarding has not started if the state is missing.
- Treat missing or active onboarding as a direct onboarding interaction, not a passive status lookup.
- Explain briefly that setup is required for the best Sales experience because saved preferences, workflow-time source choices, and team context help Sales tailor future prep, follow-up, and other seller-ready work.
- End with one concrete next setup action that the user can approve now, using a compact `**Next Step**` label only when it improves clarity.

## Case 7: Scheduled Check-In Heartbeat Shape

Context: suggest-sales-next-step automation runs on a weekday at 9:00 AM.

Expected behavior:

- Produce a short check-in card tied to recent usage, calendar/source signals, or visible setup gaps.
- Suggest one specific prompt grounded in real context, such as `Use Sales follow-up-after-call for today's Acme implementation sync notes.`
- Preserve heartbeat XML at the end of scheduled-mode output.

No-notification shape:

```text
<heartbeat>
  <decision>DONT_NOTIFY</decision>
  <message>No useful Sales check-in suggestion right now.</message>
</heartbeat>
```
