---
name: user-context
description: Load or manage the Data Analytics plugin's durable source-routing preferences, onboarding logic, setup progress, and semantic-layer registry.
---

# User Context

This skill is the Data Analytics plugin's source-routing, semantic-layer registry, setup, and onboarding layer. It loads explicit future source-routing choices, semantic-layer pointers, onboarding progress, and reusable setup obligations for Data Analytics workflows. It does not act as general Data Analytics memory.

## Mandatory Pre-Answer Gate

- For ordinary Data Analytics preflight, use `scripts/data_analytics_preflight.py` as the default state-read path when local shell access is available.
- Apply the same gate on behalf of other Data Analytics skills that call `data-analytics:user-context` as part of their own mandatory preflight before answering, searching connectors, retrieving evidence, creating artifacts, or drafting output.
- When running the preflight script through a command tool, set the tool's `max_output_tokens` to at least `25000` so the complete payload remains visible as the registry grows. If the tool output is truncated, warn the user that Data Analytics could not load all source-routing preferences and semantic-layer registry entries in one pass, then rerun with a higher cap and do not use the payload until the complete output is visible.
- Treat the script payload as satisfying the read requirement only when it reports read status for `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` and renders the compact context it will use in `context.user_context`, `context.source_preferences`, `context.source_category_config`, `context.connector_confirmation`, `context.connector_setup_summary`, `context.semantic_layers`, `context.hero_prompt_candidates`, `context.primary_hero_prompt`, `context.extra_hero_prompt_candidates`, and `control`.
- Do not treat listing files, checking that files exist, or saying they should be read as sufficient; source-routing preferences, semantic-layer pointers, source category mapping, and onboarding obligations must be loaded and applied.
- If the script fails, cannot render the compact Data Analytics context the workflow will use, local shell access is unavailable, or the request is direct context maintenance, actually read the relevant state files manually before answering or writing.
- If the user-context file is absent or unavailable, follow `references/onboarding.md` for first-run behavior.
- Read `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json` only when onboarding state, semantic-layer refresh setup, hero prompt progress, or progressive nudges are relevant.

## Skill Configuration

### Audience And Language

Write for Data Analytics users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Data Analytics impact: what Data Analytics is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is Meeting notes: May 19 or Slack thread: May 15-21. Use plain text labels only when no useful URL or stable connector-visible link is available, and say (no useful link available) when that absence matters.

## Purpose

User Context keeps two durable Data Analytics-scoped things in a local state file: source-routing choices explicitly selected for future use, and semantic-layer registry pointers. Operational onboarding bookkeeping belongs in a separate JSON state file so `user-context.md` stays small, readable, and cheap to load. Do not use `user-context.md` as a general memory file for arbitrary facts, preferences, output style, caveats, accepted drafts, or "remember this" requests.

Use this skill as the fast preflight for every substantive Data Analytics workflow before ordinary work begins. Use it as the primary workflow when the user asks to onboard, set up, inspect source-routing preferences, inspect semantic layers, create or maintain a semantic layer, or reset Data Analytics setup. If the user asks Data Analytics to remember arbitrary context, explain that general memory is not supported here; persist only an explicit future source-routing choice or a semantic-layer registry pointer produced by semantic-layer setup.

## Reference Loading

`SKILL.md` owns the normal preflight, direct read, narrow write, onboarding handoff, and first-run setup path. Load references selectively:

- Use `scripts/data_analytics_preflight.py` as the normal read-only preflight implementation when local shell access is available. Its JSON payload owns Data Analytics state-file read status, compact user-context normalization, source-routing preferences, source category configuration, connector confirmation and setup summary, semantic-layer registry, hero prompt candidates, file provenance, onboarding progress, and final response obligations for ordinary workflows.
- Keep first-run state creation automated through `scripts/init_user_context_state.py`; it copies the bundled templates into the user's Data Analytics state directory. Do not run it before the first direct onboarding orientation when no state exists. Run it after the user approves the first setup step, or when an explicit future source-routing choice or semantic-layer registry pointer needs persistence. When running through a sandboxed local shell, request elevated execution by default because the initializer writes under `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`, outside the project workspace. After initialization, write only the narrow supported `user-context.md` fields and related JSON state files.
- Use `scripts/reset_user_context_state.py` for explicit debugging reset requests that clear local Data Analytics user-context and onboarding state. The helper backs up known state files before removing them from the active state directory.
- Use `references/onboarding.md` when first-run orientation, core source setup confirmation, semantic-layer setup, semantic-layer refresh setup, semantic-layer weekly source polling setup, hero prompt sequencing, onboarding completion, onboarding status, Data Analytics TODOs, walkthroughs, environment conflict audit, or onboarding-state updates are active.
- Use `references/semantic-layer/setup.md` when onboarding, direct setup, or maintenance work needs to create, refresh, inspect, or repair a semantic layer. Use `references/semantic-layer/source-intake.md` for seed-source intake and source inventory shaping, `references/semantic-layer/connector-playbook.md` for semantic-layer source-lane connector behavior, and `references/semantic-layer/skill-template.md` for the generated semantic-layer skill shape.
- Use `plugin-author-config/user-context-config.md` for the copy-ready minimal user-context scaffold.
- Use `plugin-author-config/source-category-config.json` for source category ids, labels, preferred plugin routes, and relevant helper skills.
- Use `references/source-category-runtime.md` for workflow-time source attempts, onboarding connector confirmation, plugin-first source setup, ON_USE auth behavior, failure classes, fallback rules, and explicit future source-routing choice storage.
- Use `references/onboarding-state-template.json` only as the default operational onboarding-state shape; `references/onboarding.md` owns onboarding behavior, transitions, and completion rules.
- Use `plugin-author-config/automation-config.md`, `references/automation.md`, and `references/semantic-layer/weekly-polling-automation.md` for semantic-layer weekly source polling setup.
- Use `references/onboarding-examples.md` only to audit or explain onboarding traces. Examples do not override the rules above.
- Use `scripts/validate_user_context_preflight.py` and `tests/test_state_helpers.py` as the validator and executable regression suite for the Data Analytics user-context preflight contract.

## Skill Experience Guidance

Every user-facing Data Analytics hero workflow used during onboarding should keep its execution guidance in the focused skill that owns the work.

Use the focused skill for the actual analysis, clarification behavior, source-gap handling, and any useful continuation after the output. Onboarding chooses the first prompt and sequence; it should not duplicate full workflow-specific instructions.

When `data_analytics_preflight.py` reports hero prompt candidates and onboarding selects one as the first hero prompt, the focused skill must interpret that context before deciding whether to show a first-run intro, ask for one missing anchor, gather evidence, draft output, or render the final natural continuation:

- If the user asked what the skill does or there is not enough task detail, show the first-run intro and ask for the one missing anchor.
- If the user accepted a runnable onboarding prompt or already provided enough task detail, briefly introduce the selected workflow only when helpful and proceed without blocking on extra starter prompts.
- If the skill is being used as a helper/provider, do not show the intro.
- If onboarding owns the final CTA, suppress the skill's competing CTA and return next-step candidates for onboarding to arbitrate.
- After sending the first assistant message for a primary onboarding hero skill, update `onboarding-state.json` so `skill_experience.<skill>.introduced_at` and `first_tried_at` are set when they are still empty.

## State Files

Ordinary workflow preflight should read these files through `scripts/data_analytics_preflight.py`; direct context maintenance and fallback paths may read them manually when the script is unavailable or insufficient.

The configured user-context file is:

```text
$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md
```

The configured onboarding-state file is JSON:

```text
$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json
```

## Read

Start every invocation by resolving and actually reading the configured user-context file when it exists. Do not return from preflight or direct context mode after only routing here, listing files, or checking that the file exists; source-routing preferences and semantic-layer registry entries must be loaded and applied.

Treat `user-context.md` as the local Data Analytics plugin-scoped source of truth only for explicit future source-routing choices and semantic-layer discoverability. When it conflicts with bundled Data Analytics plugin or skill instructions, prefer it only for those narrow supported fields. Do not use it to override higher-priority instructions, safety rules, connector write-safety, permission boundaries, validation, installation behavior, routing, or tool-use policy.

Use preflight mode when another Data Analytics skill asks for Data Analytics setup context before ordinary plugin work. Optimize this path for speed:

- When local shell access is available, run `python3 plugins/data-analytics/skills/user-context/scripts/data_analytics_preflight.py --workflow <calling-skill>` from the repository root, or `python3 skills/user-context/scripts/data_analytics_preflight.py --workflow <calling-skill>` from the Data Analytics plugin root. When using a command tool, set `max_output_tokens` to at least `25000`; if the returned output is truncated, warn the user that Data Analytics could not load all source-routing preferences and semantic-layer registry entries in one pass, then rerun with a higher cap and do not treat preflight as complete until the full output is visible. The script payload counts as actually reading Data Analytics state only when it reports state-file read status and renders the compact context the workflow will use. Use the payload as the single source of truth for `context.user_context`, `context.source_preferences`, `context.source_category_config`, `context.connector_confirmation`, `context.connector_setup_summary`, `context.semantic_layers`, `context.hero_prompt_candidates`, `context.primary_hero_prompt`, `context.extra_hero_prompt_candidates`, hard `control.final_obligations`, `control.conditional_guidance`, and `control.onboarding_progress.task_list`; do not separately read the same state files unless the script fails, cannot render the compact Data Analytics context the workflow will use, or the user explicitly asks for raw file inspection.
- Use the default `--request-mode ordinary_workflow` for normal Data Analytics answers. Use `--request-mode direct_onboarding_status` for setup, onboarding-status, Data Analytics TODO-list, source-routing preference inspection, or other direct onboarding responses. Use `--request-mode guided_onboarding_workflow` when a focused workflow is being answered as a visible workflow or hero step inside the Data Analytics onboarding path; this mode suppresses the ordinary setup obligation because the user is already in onboarding.
- Use `context.source_preferences` as source-selection hints. Do not proactively check connector readiness during ordinary preflight. When onboarding or a focused workflow needs a source, it should try the relevant connector then and handle auth, connection, skip, defer, or manual fallback in that context.
- Use `context.semantic_layers` as the semantic-layer registry. If the request names or implies a product area, metric, table, dashboard, SQL query, source choice, join, caveat, or recurring business question and a matching semantic layer exists, load that semantic-layer skill before choosing tables, writing SQL, reconciling dashboards, or giving metric definitions.
- After reading user context, use the script-driven preflight payload for the calling skill, then immediately let the calling skill continue. The returned envelope is the authoritative, auditable preflight context; do not hide a larger raw-state payload behind it. The payload is not user-facing and must not be rendered unless the user explicitly asks for implementation details.
- Do not browse linked sources, run broad searches, summarize unrelated sections, or ask setup questions during ordinary preflight.
- If `onboarding-state.json` exists, parse only the relevant fields for whether onboarding is active, quiet, complete, whether core onboarding is complete, and any concrete next actions. Do not echo raw onboarding-state content into ordinary preflight output; use file provenance plus the normalized onboarding, source, semantic-layer, and hero-prompt fields the script returns. During ordinary preflight, return at most one concrete guided next step that the calling skill may append after answering the immediate request. If core onboarding is still incomplete, the next step should direct the user back to the next unresolved core setup item: source setup confirmation or semantic-layer setup. During direct onboarding, setup-status answers, or user requests for the Data Analytics TODO list, use `references/onboarding.md` to render the single visible compact `**Next Step**` block and mirror the compact high-level roadmap into the built-in thread task list when available.
- Treat `context.connector_setup_summary.unresolved_core_ids` and `context.connector_setup_summary.next_action` as authoritative during onboarding. Do not advance into semantic-layer setup because a core source entry merely says `deferred`, `skipped`, `declined`, `unavailable`, or `not_applicable`; preflight reopens that source as `needs_confirmation` unless onboarding state records the user's explicit known-gap resolution.
- Use the returned `data_analytics_preflight` envelope as the source of truth for saved context, source category configuration, connector setup summary, semantic-layer registry, primary hero prompt, extra hero prompt candidates, onboarding progress, final obligations, and conditional guidance. Treat saved context and semantic layers as source-selection inputs, not as substitutes for workflow-time reads from connected or provided sources.
- If `user-context.md` is missing, read `references/onboarding.md`, return that no durable Data Analytics source-routing preferences or semantic-layer registry are available, use the script-driven payload or documented manual fallback to provide conditional setup guidance, and let the caller continue. Do not run the initializer or scaffold state merely because the file is missing. Do not interrupt ordinary plugin work with setup or stop at a setup request. For a high-intent first-run workflow request, tell the caller to answer the user's concrete query first using bundled instructions, user-provided material, and available connectors or sources; if the requested artifact cannot be completed or is meaningfully weaker because a source or semantic layer is missing, give the best truthful answer from the attempted sources and name the practical gap using `references/onboarding.md#context-gap-note`. Append the ordinary-workflow setup obligation only when preflight returns it because onboarding has not started; do not offer to start onboarding when `onboarding-state.json` already says onboarding is active.
- If a referenced source is inaccessible, stale, ambiguous, or missing, say that directly only when the missing source affects the current task, then continue with the available context.

### Script-Driven Preflight Payload

Preflight mode must use `scripts/data_analytics_preflight.py` as the authoritative payload before ordinary work continues. The script output owns `request_mode`, `current_skill_experience`, `context.user_context`, `context.source_preferences`, `context.source_category_config`, `context.connector_confirmation`, `context.connector_setup_summary`, `context.semantic_layers`, `context.hero_prompt_candidates`, `context.primary_hero_prompt`, `context.extra_hero_prompt_candidates`, `control.response_mode`, hard `control.final_obligations`, `control.conditional_guidance`, and `control.onboarding_progress.task_list`. Do not hand-author, recreate, or mentally reconstruct the payload when the script is available; use the JSON fields the script returned.

For ordinary Data Analytics workflow requests, honor `control.final_obligations` exactly as returned by the script. The calling skill must answer the immediate request first, then satisfy any returned setup CTA or core-onboarding reminder. When the focused skill does not otherwise own a final continuation, append the returned template intact. When the focused skill has its own final continuation, fold the setup reminder or move-on path into that same final natural continuation so the response has one final visible CTA, not a standalone setup reminder plus a second skill CTA. Do not downgrade a hard obligation into a passive setup aside or a context-gap explanation. Do not use that hard obligation for direct onboarding/setup/status responses, focused workflows launched from the visible onboarding path, or responses where the immediate workflow must ask a required clarification; those callers should use `direct_onboarding_status` or `guided_onboarding_workflow` request mode when appropriate, and clarification-only responses should end with the clarification as the sole final natural continuation.

When the script fails, cannot render the compact Data Analytics context the workflow will use, or local shell access is unavailable, fall back to the manual file-read path described above: actually read the relevant state files, use only fields known from those files or the missing-file condition, apply `references/onboarding.md` for direct onboarding/status behavior, and state any missing source or semantic-layer gap only when it materially affects the current answer. Restore script-driven validation as soon as local shell access is available.

Use direct context mode when the request is primarily about setup, source-routing preferences, semantic layers, or context maintenance:

- If `user-context.md` exists, read it before answering or writing.
- If the user asks what Data Analytics remembers, say Data Analytics does not keep general memory here; summarize only explicit future source-routing choices and registered semantic layers.
- If the user asks Data Analytics to remember arbitrary context, do not save it. Explain that this file only persists explicit future source-routing choices and semantic-layer registry entries.
- If the user explicitly selects a future source-routing default or a future source to avoid, update only the matching source category in `user-context.md`.
- When the request starts, resumes, updates, checks, or completes Data Analytics setup or onboarding, perform the requested sub-step and then apply the step cards in `references/onboarding.md` before answering. The first direct onboarding orientation with no existing Data Analytics state is a response-first fast path: render the orientation immediately, then initialize state only after the user approves the next setup step or a supported `user-context.md` write is needed. Other setup interactions include onboarding-status checks, source setup confirmation, semantic-layer setup or refresh, hero-prompt selection, and completed or deferred guided workflow updates.
- Treat onboarding-status questions such as "have we onboarded yet?", "am I set up?", "is Data Analytics configured?", or "what setup is missing?" as direct onboarding interactions, not as ordinary context lookup. Answer the status through the common onboarding finalizer: if onboarding is missing or active, strongly guide the user into the current compact `**Next Step**` block with built-in thread task-list updates when available; if onboarding is complete, say so and offer one useful Data Analytics workflow. Do not end an incomplete onboarding-status answer with only a passive or optional setup suggestion.

Outside explicit linked-source refresh, semantic-layer setup, or semantic-layer refresh work, retrieve linked Google Docs, Drive files, Notion pages, or other resources only when they are accessible through available connectors or explicit local APIs and the user asked to inspect or refresh that source. Do not use browser automation, in-app browser, or Computer Use as fallback retrieval paths for ordinary context-source retrieval.

## Onboarding

Use `references/onboarding.md` as the source of truth when the user asks what Data Analytics can do, asks to set up Data Analytics, invokes onboarding, asks whether onboarding is complete, asks for Data Analytics TODOs, asks which sources Data Analytics can try, asks to create or inspect a semantic layer during onboarding, or when `onboarding-state.json` says onboarding is active and a nudge is due. During ordinary preflight, do not show full onboarding; parse only relevant JSON fields and return the hard setup obligation or one source/semantic-layer gap note when applicable, then let the calling skill continue. When onboarding is already active during an ordinary workflow, do not ask whether to start onboarding. If core onboarding is incomplete, answer only directly requested Data Analytics work best effort and direct the user back to the next unresolved core setup item. If core onboarding is complete, preserve the workflow's own final natural continuation and mention resuming guided onboarding only as a short non-competing note when directly useful. During the first direct onboarding message with no state, render Step 1 directly from `references/onboarding.md` without creating scaffold files first.

When direct context work happens while onboarding is missing or active, apply the current step-card continuation in `references/onboarding.md` before finalizing. This includes source setup confirmation, onboarding-status checks, source-routing preference changes, semantic-layer setup or refresh, hero prompt selection, and skill-experience updates. A recap of the just-completed sub-step is not sufficient while onboarding is active unless onboarding is complete, quiet, or stopped by the user. During source setup confirmation, surface unresolved `structured_data`, `team_communication`, and `company_docs` before optional source categories and do not downgrade installable core routes into quiet optional deferrals.

When a focused workflow is run from the visible onboarding path, call preflight with `--request-mode guided_onboarding_workflow` so the workflow can answer normally without adding a redundant onboarding reminder. Focused hero skills own their own first-run banner, anchor rules, prompt execution behavior, and next-step guidance. Onboarding owns the first prompt choice, extra prompt sequencing, and state updates.

## Action-Oriented Continuation

Default Data Analytics outputs should be useful launchpads, not dead ends. In almost all cases, after answering the user's immediate request, add one concise next step that helps them act on the result. Good next steps continue the same workflow by iterating on the analysis, validating one gap, creating the next artifact, checking one missing source, setting up or refreshing a semantic layer, or showing one remaining hero prompt when onboarding owns the final CTA. Do not recommend moving to another Data Analytics skill as a generic continuation; route elsewhere only when the user's request has clearly changed or the current workflow's own routing rules say another skill owns the job.

Avoid asking for setup context merely to fill onboarding state. Ask only high-uncertainty, high-impact questions whose answers would significantly improve future outputs, semantic-layer quality, connector setup, or the active workflow. If onboarding is active, the current step card in `references/onboarding.md` governs the next step; otherwise use the ordinary action-oriented continuation rules here.

Show at most one direct CTA during ordinary workflow output unless the user explicitly asks for options, onboarding, setup, or the Data Analytics TODO list. When onboarding has not started in an ordinary workflow, that CTA must be the `## Data Analytics Setup Required` template from preflight, even if the immediate artifact is otherwise complete, unless the immediate workflow is blocked on a required clarification. Clarifications always become the final natural continuation and suppress onboarding CTAs for that response. When onboarding is already active and core onboarding is incomplete, direct the user to finish the next core setup item before continuing non-urgent Data Analytics workflows. When onboarding is active and core onboarding is complete, preserve the workflow-owned final natural continuation and mention resuming guided onboarding only as a short non-competing note when useful. For direct onboarding and setup-status flows, follow `references/onboarding.md` instead: render the single visible compact `**Next Step**` block, mirror the compact high-level roadmap into the built-in thread task list when available, and check tasks off as the user completes, approves, declines, or makes them unnecessary. Skip the CTA only when the user asks for quiet behavior, the request is sensitive or high-pressure enough that a follow-up would be distracting, onboarding is complete and the workflow has no reasonable next action, or the focused workflow already owns a better clarification.

## Write

Write only two kinds of durable Data Analytics user context to `user-context.md`:

- explicit future source-routing choices, such as `Prefer: Databricks` or `Avoid: Snowflake`, under the matching source category;
- semantic-layer registry pointers under `# Semantic Layers`.

Do not store general memory, arbitrary "remember this" content, analytical priorities, copied source-of-truth links, saved dashboards, saved tables, saved docs, source inventories, output preferences, accepted-output preferences, quiet-ending preferences, automatic connector readiness, operational onboarding status, connector-audit bookkeeping, hero prompt progress, or semantic-layer refresh metadata in `user-context.md`. Area-specific metric, dashboard, table, source-of-truth, caveat, and definition anchors belong inside the semantic layer itself.

First-run state creation remains automated when persistence is needed: run `python3 plugins/data-analytics/skills/user-context/scripts/init_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/init_user_context_state.py` from the Data Analytics plugin root, to copy `plugin-author-config/user-context-config.md` and seed `onboarding-state.json` from `references/onboarding-state-template.json`. Do not run this command just to show the first direct onboarding orientation. In sandboxed local-shell environments, request elevated execution on the first attempt because the target state directory is under `$CODEX_HOME`, not the project workspace. After initialization, modify `user-context.md` directly. For multi-entry approvals, read the current state once, update every touched source category in one coherent edit, update `onboarding-state.json` once when onboarding bookkeeping changes, then run `scripts/data_analytics_preflight.py --workflow user-context` or the relevant workflow preflight to confirm the supported context reads back cleanly. Keep `onboarding-state.json` compact: do not persist raw `list_available_plugins_to_install` results, full connector inventories, connector descriptions, copied source inventories, source URLs, prompts beyond the compact current onboarding choice, artifact text, source-gap notes, or analysis output. Store resolved route metadata, counts, ids, statuses, timestamps, and durable pointers instead. Never run parallel writes against the same Data Analytics state files.

For semantic-layer setup, refresh, inspection, or repair, read `references/semantic-layer/setup.md`. Write durable layer pointers into the `# Semantic Layers` section of `user-context.md` and update operational setup or refresh metadata in `onboarding-state.json`. Do not keep semantic-layer discoverability only in onboarding state.

For explicit debugging reset requests only, run `python3 plugins/data-analytics/skills/user-context/scripts/reset_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/reset_user_context_state.py` from the Data Analytics plugin root. The helper backs up active Data Analytics state files, then leaves the plugin ready for fresh onboarding. Never perform this reset for ordinary onboarding, source-routing preference edits, setup retries, source refresh work, or vague troubleshooting.

Use this source-routing structure:

```md
# Data Analytics Source Routing Preferences

Store durable Data Analytics source-routing choices explicitly selected for future use.

## structured_data

- Prefer: Databricks
- Avoid: Snowflake
```

Use this semantic-layer registry shape:

```md
# Semantic Layers

- Area: Customer onboarding
  - Skill Name: api-semantic-layer
  - Skill Path: /absolute/path/to/api-semantic-layer
  - Source Inventory Path: /absolute/path/to/api-semantic-layer/references/source-inventory.md
  - Last Updated: 2026-06-01
```

## First Run Setup

Use first-run setup in direct context mode when `user-context.md` is missing, unreadable, or lacks the bundled minimal scaffold. For a pure onboarding or "what can Data Analytics do?" request, show the orientation first and defer scaffold creation. If a supported future source-routing choice or semantic-layer pointer needs persistence, create the scaffold first, then update only the relevant supported section.

For first-run setup after the first orientation, use `scripts/init_user_context_state.py` to create missing local state files when possible, then read `plugin-author-config/user-context-config.md` and treat the bundled source category sections as a minimal routing scaffold, not a questionnaire. Read `references/onboarding.md` before presenting first-run orientation, source setup confirmation guidance, semantic-layer setup guidance, or hero prompt sequencing. Read the relevant hero skill's experience guidance before presenting that skill's intro, prompt, or anchor rule.

After the user approves the next setup step, supplies an explicit future source-routing choice, or semantic-layer setup needs a durable registry pointer:

1. Run `python3 plugins/data-analytics/skills/user-context/scripts/init_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/init_user_context_state.py` from the Data Analytics plugin root, when local shell access is available. In sandboxed local-shell environments, request elevated execution on the first attempt because it writes to `$CODEX_HOME/state/plugins/data-analytics`. If the script is unavailable, create `$CODEX_HOME/state/plugins/data-analytics`, copy the content below `## Default User Context` from `plugin-author-config/user-context-config.md` into `user-context.md` with the required top note, and create `onboarding-state.json` from `references/onboarding-state-template.json`.
2. Read the resulting `user-context.md`, preserving every source category's `Prefer` and `Avoid` rows plus the `# Semantic Layers` registry section.
3. Update only the approved source-routing choice or semantic-layer pointer. Do not append disconnected general memory.
4. Read the resulting `onboarding-state.json`, then update onboarding state with operational onboarding progress, connector confirmation labels, semantic-layer setup or refresh metadata, hero prompt progress, and skill experience progress.
5. Continue the user's original request using the updated supported context.

If the user declines setup, continue the original request without durable source-routing preferences or semantic-layer registry. Keep the explanation user-facing; do not describe internal files unless the user asks.
