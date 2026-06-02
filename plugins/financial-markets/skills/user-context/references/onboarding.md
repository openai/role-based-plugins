# Public Equity Investing User Context Onboarding

Use this reference only when the user explicitly asks to set up, resume, defer, quiet, or complete Public Equity Investing saved-context onboarding. Ordinary Public Equity Investing workflows do not invoke onboarding yet.

## Orientation

Render the canonical response template substantially verbatim. Do not add preference categories, examples, or connector claims unless the user asks for more detail.

### Orientation Response Template

```text
I can save a small local set of Public Equity Investing preferences and source pointers to improve future work. This setup is optional. Would you like to add preferences now, continue to source setup, defer setup, or quiet future setup guidance?
```

Update onboarding state before continuing:

- When the user chooses to add preferences, set `orientation.status` to `completed` and render the Memory Preferences response template.
- When the user chooses to continue to source setup, set `orientation.status` to `completed` and `memory_preferences.status` to `skipped`, then rerun preflight and render its next `copy_ref`.
- When the user chooses to defer setup, set top-level `status` to `deferred`.
- When the user chooses to quiet future setup guidance, set top-level `status` to `quiet`.

## Memory Preferences

Render the canonical response template substantially verbatim. Preserve the category labels and descriptions. When a category is already populated, omit it from the visible list unless the user asks to review saved context. Do not invent additional examples or recommend specific preferences.

### Memory Preferences Response Template

```text
Useful saved Public Equity Investing preferences include:

- Output Style: preferred formats, depth, audience, and recurring research conventions.
- Portfolio And Watchlists: key portfolio, watchlist, repository, and tracker pointers.
- Trusted Sources: preferred filings, transcripts, research locations, and source priorities.
- Modeling And Valuation: model templates, valuation methods, estimate sources, and KPI conventions.
- Thesis And Risk Tracking: thesis trackers, catalyst calendars, monitoring cadence, and review triggers.
- Compliance And Review: circulation limits, citation expectations, and approval gates.

Share any durable preferences or pointers you want saved, or say skip preferences to continue to source setup. Keep live company updates and one-off research requests in the active workflow.
```

Store only user-provided or user-approved durable context in `user-context.md`. Do not treat unresolved placeholders, inferred preferences, connector availability, or one-off research requests as saved facts.

Update `memory_preferences.status` in `onboarding-state.json`:

- Use `completed` after saving the durable preferences the user supplies.
- Use `skipped` when the user wants to continue to source setup without saving preferences.
- Use `deferred` when the user wants to provide preferences later.

After the preference step is resolved, rerun preflight and render its next `copy_ref` so the Source Setup offer follows immediately.

## Source Setup

Render the canonical response template substantially verbatim. Do not inspect plugins, apps, connectors, or `.app.json` until the user approves this step or explicitly asks to configure Public Equity Investing sources.

### Source Setup Response Template

```text
I can check which Public Equity Investing source tools are exposed and save setup routes for future workflows. This does not read source contents. Would you like me to check sources now, defer source setup, or skip it?
```

When the user approves source setup, follow `skills/user-context/references/source-category-runtime.md` from the plugin root. Keep the result concise: name useful exposed source routes, identify categories that still need a choice or access, and ask only the smallest necessary follow-up question. Store operational route selections under `onboarding-state.json` `connector_confirmation`; do not store them in `user-context.md`.

Update `source_setup.status` in `onboarding-state.json`:

- Use `completed` after each category is classified and any required user choice is resolved, including when the user chooses to continue with known gaps.
- Use `deferred` when the user wants to configure sources later.
- Use `skipped` when the user wants to continue without source setup.

Do not perform proof reads during this setup step. Actual source reads happen only when a focused workflow needs the source.

## Optional Automation

Render the canonical response template substantially verbatim. This step is optional and requires explicit acceptance before any automation is created.

### Automation Setup Response Template

```text
I can optionally set up a weekday Public Equity Investing watchlist brief in this conversation. It will surface catalyst, thesis, monitoring, and source-gap items for review without trading or changing source systems. Would you like to set it up, defer automation setup, or skip it?
```

When the user accepts, follow `skills/user-context/references/automation.md` from the plugin root. Store only concise operational metadata under `onboarding-state.json` `automations`; do not copy automation metadata into `user-context.md`.

Update `automations.status` in `onboarding-state.json`:

- Use `completed` after the accepted automation is created or an existing matching automation is refreshed.
- Use `deferred` when the user wants to decide later.
- Use `skipped` when the user does not want an automation.

## Complete Or Defer

Render the canonical response template substantially verbatim.

### Complete Or Defer Response Template

```text
Would you like me to record Public Equity Investing saved-context setup as completed, deferred, or quiet?
```

- Use `completed` when the user is satisfied with the saved context for now.
- Use `deferred` when the user wants to resume setup later.
- Use `quiet` when the user does not want setup reminders.

## State Repair

Render the canonical response template substantially verbatim. Do not overwrite or reset state unless the user explicitly requests it.

### State Repair Response Template

```text
I could not interpret the Public Equity Investing onboarding state. It needs repair before setup progress can be read reliably. Would you like me to repair it?
```

## Current Boundary

- Do not invoke onboarding from ordinary Public Equity Investing workflows yet.
- Do not inspect apps, connectors, plugins, `.app.json`, or source readiness during preflight.
- Inspect source setup surfaces only after the user approves the explicit Source Setup step or explicitly asks to configure sources.
- Inspect automation state only after the user approves the explicit Optional Automation step or explicitly asks to manage Public Equity Investing automations.
- Do not claim source readiness or live automation behavior without checking the matching runtime surface.
- Do not mutate state while running `scripts/user_context_preflight.py`.
