# Data Analytics Onboarding Examples

Use these compact cases to audit the core onboarding experience. They are regression anchors, not scripts. Governing rules remain in `onboarding.md`, the relevant skill's experience guidance, `../plugin-author-config/source-category-config.json`, `../plugin-author-config/automation-config.md`, `source-category-runtime.md`, `automation.md`, and the semantic-layer references.

## Case 1: Direct Onboarding Orientation

User says:

```text
@data-analytics let's onboard
```

Expected behavior:

- Open with a compact Data Analytics onboarding orientation that explains what the plugin does, how onboarding works, and that the user can answer `continue`, `skip`, or provide a real analytics anchor at each step.
- Do not initialize state files, create the user-context scaffold, inspect connectors, audit conflicts, create semantic layers, create background threads, install automations, or run hero prompts before sending the first orientation message.
- Make `Orientation` the first visible item, then `Check main analytics sources`; do not inspect connectors before the first orientation just to populate setup state.
- Explain that active or obvious one-app sources are informational only and will be tried only when a workflow needs them. Ask the user for help only where multiple apps are plausible, no app was found, setup/auth is needed, or manual fallback would materially change the result.
- Include environment conflicts only when overlapping broad analytics plugins or analytics-specific skills create real or likely routing conflicts; omit that note after a clean audit.
- Offer one concrete guided next action with real context, never placeholders such as `<metric>` or `<dashboard>`, while mirroring the canonical high-level onboarding checklist into the built-in thread task list when available: `Orientation`, `Check main analytics sources`, `Set Up Data Context`, and `Hero prompt`.
- Use `# Data Analytics Onboarding`, then a high-level prose paragraph that does not expose saved state paths, cache paths, or internal onboarding status.
- Explain hero workflows only when the flow reaches the first analysis prompt or the user asks for the full plan.
- End with one clear action close and show only the current action the user can approve now. Use a compact `**Next Step**` label only when the step needs the label; a self-contained numbered choice set can stand on its own. If the current step has open questions, make resolving them their own step and include those questions in the action close; if they are non-blocking, say what `okay` or `continue` will do by default.

## Case 2: High-Intent First Run

User says:

```text
@data-analytics diagnose why API ARR moved last week
```

Expected behavior:

- Begin the requested analytics workflow first and return a best-effort answer from available sources, even when no durable Data Analytics source-routing preferences or semantic-layer registry exist.
- Use visible source evidence if available rather than stopping at onboarding.
- Keep the artifact useful even while onboarding is missing or active.
- Add the `## Data Analytics Setup Required` CTA after the answer only when onboarding has not started, unless the request is already being answered inside a guided onboarding flow. If onboarding is already active, preserve the focused skill's own final natural continuation and do not ask whether to start onboarding.
- Add a `Context Gap` note only when missing source-routing preferences, semantic-layer context, source access, or setup materially weakens the analysis. The note should name the exact missing source, semantic layer, or decision anchor and the specific improvement it would unlock.
- Do not add a generic setup note; the onboarding CTA should say setup is required before Data Analytics can reliably reuse source choices and semantic-layer context, and end with the exact line: Reply `start` to continue.

## Case 3: Confirm A Selected Warehouse Route

User says:

```text
connect Databricks
```

Context: the previous onboarding response showed active/missing source confirmation and Databricks was the selected structured-data warehouse.

Expected behavior:

- Treat the reply as permission to record or repair the selected Databricks route and run the matching install, connect, or authorize path when that path is exposed.
- Do not run a proof query during onboarding merely to decide whether Databricks is active.
- Mark `structured_data` as `active` when the Databricks route is installed, available, surfaced, or otherwise evidenced strongly enough for its route kind; let the first real workflow-time read handle auth, query, or schema failures.
- If setup or auth is required, let that flow complete before moving on when the setup surface is exposed.
- If no native route exists, keep the category as `needs_confirmation`, `missing`, `unavailable`, `deferred`, or `skipped`, and ask whether to connect or authorize, use manual SQL or schema context, skip, or defer.

## Case 4: Missing Core Sources Stay In Source Setup

User says:

```text
continue
```

Context: Data Analytics found Google Drive and Notion for company docs, but no active data warehouse or team communication route. `functions.list_available_plugins_to_install` returned Databricks, BigQuery, Snowflake, Slack, and Teams.

Expected behavior:

- Keep the user in Step 2 or Step 2A and make the missing core choices prominent before semantic-layer setup.
- Say that core setup still needs the user's choice, list Data warehouse with Databricks, BigQuery, and Snowflake, list Team communication with Slack and Teams, and say company docs look covered through Google Drive or Notion when that is true.
- Do not quietly write `deferred`, `skipped`, `declined`, `unavailable`, or `not_applicable` for a core category just to advance onboarding.
- Do not introduce semantic-layer setup until each unresolved core source has an active or manual route, or the user explicitly chooses a known-gap fallback such as `defer core sources`.
- When the user explicitly defers a core source, record the matching `resolution` value such as `user_deferred` or `user_continued_with_known_gap`; a core fallback without that explicit resolution should surface again as `needs_confirmation`.

## Case 5: Semantic Layer Intake

User says:

```text
API ARR
```

Context: source setup confirmation is resolved and Data Analytics has enough source access or manual fallback to begin semantic-layer setup.

Expected behavior:

- Introduce semantic-layer setup briefly if it has not been introduced.
- Ask only for the smallest missing starting point if no trusted dashboard, table, SQL, doc, repo path, notebook, team thread, or recurring question is available.
- If enough useful context exists, run the semantic-layer setup flow directly instead of asking a broad questionnaire.
- Keep the ask grounded in one coherent product or business area; do not merge unrelated analytical areas into one layer unless the user explicitly asks.

## Case 6: Data Analytics Automations Are Automatic And Approval-Gated

User says:

```text
okay
```

Context: the previous onboarding response explained that recurring Data Analytics source polling can run in the background, listed Semantic Layer Weekly Source Polling with its configured cadence, and ended with a setup approval question. The visible step was semantic-layer refresh setup.

Expected behavior:

- Read `automation.md` and `../plugin-author-config/automation-config.md`.
- Install or repair `weekly_semantic_layer_refresh` unless the user has already declined, skipped, or deferred refresh for the current semantic layer.
- Mention the configured automation once with its cadence: Semantic Layer Weekly Source Polling runs weekly on Mondays at 9:00 AM local time.
- Use the configured dedicated pinned thread named `Semantic Layer Weekly Source Polling`.
- Confirm the automation prompt is a thin launcher for the semantic-layer polling workflow; the semantic-layer polling owner owns source inventory handling, source precedence, evidence standards, update boundaries, validation, and run-summary copy.
- Record automation metadata in `onboarding-state.json`.
- Immediately kick off one source polling run in the pinned `Semantic Layer Weekly Source Polling` thread, record its kickoff status under `semantic_layer_refresh`, and tell the user it is working in the background and visible in the `Pinned` section of the left sidebar.
- Continue to the next onboarding step after readback succeeds. Mention the refresh-thread status as a separate `FYI:` line when useful, then offer the first hero prompt. Do not run the hero workflow until the user accepts the prompt or provides a specific analysis question.

## Case 7: First Hero Prompt

User says:

```text
continue
```

Context: source setup confirmation, semantic-layer setup, and semantic-layer refresh resolution are complete, and Data Analytics has context for `API ARR`.

Expected behavior:

- Show exactly one strong context-derived hero prompt first.
- The prompt should be runnable as written, grounded in the available area, metric, dashboard, semantic layer, or goal, and ask for a decision-ready report through the product-business-analysis path.
- Load the selected hero skill's experience guidance before introducing or running it.
- End with explicit replies: `run it`, a written replacement prompt, or `skip`.
- Treat `skip` as finishing onboarding, not as a reason to show more prompt choices.
- Do not show three prompt choices initially.

## Case 8: Extra Hero Prompts

User says:

```text
show more prompts
```

Context: the user explicitly asks for more prompt ideas after the first hero prompt has run, been skipped, or been deferred.

Expected behavior:

- Offer at most two remaining context-derived prompt candidates.
- Each prompt should be runnable as written and grounded in real available context, not placeholders.
- End with explicit replies: `1`, `2`, a different analysis question, or `done`.
- Do not turn ordinary Data Analytics work into a recurring onboarding screen.

## Case 9: Ordinary Workflow While Onboarding Is Active

User says:

```text
@data-analytics which dashboard should I trust for weekly ARR reporting?
```

Expected behavior:

- Complete the requested analytics workflow.
- Do not interrupt with full onboarding.
- Do not include the `## Data Analytics Setup Required` start CTA when onboarding is already active. Preserve the focused skill's own final natural continuation, folding `continue onboarding` into that same final CTA when useful. If no focused-skill CTA exists, use the explicit onboarding `**Next Step**` resume CTA as the sole final close.
- If onboarding is quiet or complete, produce the requested Data Analytics artifact directly and end with one useful analytical next action, not an onboarding recap.
- If core onboarding is incomplete, fold the setup-resume path into the same final CTA instead of adding a second final onboarding CTA.
- If this completed one of the initial guided workflows, offer a beginner-friendly walkthrough only when the user asks for it or the active workflow owns that continuation.

## Case 10: Onboarding Status Check

User says:

```text
@data-analytics have we onboarded yet
```

Expected behavior:

- Answer the status directly from `user-context.md` and `onboarding-state.json`, or say onboarding has not started if the state is missing.
- Treat missing or active onboarding as a direct onboarding interaction, not a passive status lookup.
- Explain briefly that setup is required for the best Data Analytics experience because future source-routing choices and semantic-layer context help Data Analytics tailor future analysis work.
- End with one concrete next setup action that the user can approve now, using a compact `**Next Step**` label only when it improves clarity.

## Case 11: Scheduled Semantic-Layer Refresh Run Summary

Context: the semantic-layer refresh automation runs on its weekly schedule.

Expected behavior:

- Produce a concise user-facing run summary tied to the saved source inventory, checked sources, source-backed changes, validation, and review needs.
- For a no-change run, explicitly say no source-backed changes were found and list the sources checked.
- For an updated, blocked, or conflicted run, name the changed files or the concrete permission, connector, validation, or source conflict that prevented a clean update.
- Do not send a silent or empty update.

No-change shape:

```text
Status: no change
Sources checked: <source names>
Changes found: no source-backed changes found
Files changed: none
Validation: not run
Needs review: none
```
