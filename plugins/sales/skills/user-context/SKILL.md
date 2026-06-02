---
name: user-context
description: Load or manage the Sales plugin's durable user context, onboarding logic, setup progress, automation metadata, saved preferences, non-obvious CRM conventions, source-of-truth pointers, book-of-business sources, internal team resources, account channels, approval trackers, trusted examples, approved Sales Company Research saves, "please remember" requests, and broad future-facing instructions such as always/never/prefer/next-time feedback after a Sales draft.
---

# User Context

This skill is the Sales plugin's durable context, setup, and onboarding layer. It loads saved preferences, source pointers, CRM conventions, onboarding progress, automation metadata, and reusable sales context for Sales workflows; it also owns direct requests to view, save, update, or reset Sales context and the shared onboarding logic that turns setup state into the next visible action.

## Mandatory Pre-Answer Gate

- For ordinary Sales preflight, use `scripts/sales_preflight.py` as the default state-read path when local shell access is available.
- Apply the same gate on behalf of other Sales skills that call `sales:user-context` as part of their own mandatory preflight before answering, searching connectors, retrieving evidence, or drafting output.
- When running the preflight script through a command tool, set the tool's `max_output_tokens` to at least `25000` so the complete payload remains visible as context grows. If the tool output is truncated, warn the user that Sales preflight was truncated and that Sales plugin memory or preflight context may be getting bloated, then rerun with a higher cap and do not use the payload until the complete output is visible.
- Treat the script payload as satisfying the read requirement only when it reports read status for `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` and renders the compact context it will use in `context.user_context`, `context.sources`, `context.automations`, and `control`.
- Do not treat listing files, checking that files exist, or saying they should be read as sufficient; saved preferences, profile, context, source preferences, and source-of-truth pointers must be loaded and applied.
- If the script fails, local shell access is unavailable, or the request is direct context maintenance, actually read the relevant state files manually before answering or writing.
- If the user-context file is absent or unavailable, follow `references/onboarding.md` for first-run behavior.
- Read `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json` only when onboarding state, skill experience progress, automations, or progressive nudges are relevant.

## Skill Configuration

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Purpose

User Context keeps durable, Sales plugin-scoped user context in a local state file instead of mixing private sales facts into reusable plugin instructions. Operational onboarding bookkeeping belongs in a separate JSON state file so `user-context.md` stays feasible for an average user to read, edit, and share. First-run setup should keep the template's unresolved starter categories visible in `user-context.md` as non-authoritative setup scaffolding once setup actually begins, because ordinary preflight reads are intentionally cheap and should not need to reread the bundled template just to know which configured categories are still missing. The first direct onboarding message is the exception: when no Sales state exists yet and the user asks to onboard or learn what Sales can do, render orientation from `references/onboarding.md` immediately and defer scaffolding until the user approves the next setup step or provides context to save.

Use this skill as the fast preflight for every substantive Sales workflow before ordinary work begins. Use it as the primary workflow when the user asks to remember, save, recall, inspect, set up, customize, or maintain Sales preferences, trusted examples, non-obvious CRM conventions, source-priority rules, book-of-business sources, internal team resources, account-channel guidance, approval trackers, account context, or other private context. Route requests to search available company context, fill missing setup entries, or run Sales Company Research to `sales-company-research`; use this skill to apply approved or high-confidence research saves, read/write state, and continue onboarding. Also use it when a follow-up user message after a Sales output gives a reusable instruction, correction, or preference, or when the user accepts an iterated Sales artifact and the accepted change may be reusable plugin memory, even if the user does not say "remember" or explicitly mention Sales.

## Reference Loading

`SKILL.md` owns the normal preflight, direct read, write, onboarding handoff, and first-run setup path. Load references **selectively** based on the user's request, the current state, and the relevant workflow's needs. Do not read every reference file on every invocation:

- Use `references/plugin-memory.md` for direct memory writes, broad future-facing instruction capture, correction capture, Sales Company Research save/review gates, linked-source population, successful-run learning, iteration acceptance learning, and exact save-recap behavior.
- Use `scripts/sales_preflight.py` as the normal read-only preflight implementation when local shell access is available. Its JSON payload owns Sales state-file reads, compact context, file provenance, and final response obligations for ordinary workflows.
- Keep first-run state creation automated through `scripts/init_user_context_state.py`; it copies the bundled templates into the user's Sales state directory. Do not run it before the first direct onboarding orientation when no state exists. Run it after the user approves the first setup step, or immediately when the user provides context that should be saved. When running through a sandboxed local shell, request elevated execution by default because the initializer writes under `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`, outside the project workspace. After that initialization, write Sales user context by directly editing `user-context.md` and related JSON state files. Prefer one batched edit for all approved changes over per-entry helper commands.
- Use `scripts/reset_user_context_state.py` for explicit debugging reset requests that clear local Sales onboarding or user-context state. The helper backs up known state files before removing them from the active state directory.
- Use `tests/test_state_helpers.py` as the executable regression suite for the user-context preflight contract. Do not read or run this file unless actively needed (e.g. for debugging or to validate new changes to the script).
- Use `scripts/init_user_context_state.py` for first-run scaffold creation when local state files are missing and a setup/save step needs persistence. Use `plugin-author-config/user-context-config.md` for category names and compact descriptions; the initializer adds the `## Saved Links And Context` placeholder section to every copied category.
- Use `references/onboarding.md` when first-run orientation, setup completion, environment conflict audit, automation setup, guided step-card continuation, progressive onboarding, agent-journey walkthroughs, or onboarding-state updates are active.
- Use the primary workflow skill's inline experience guidance whenever a user-facing Sales skill owns the active intent. The focused skill owns first-run intro copy, starter prompts, anchor rules, normal next-step candidates, and onboarding-yield behavior. Onboarding may choose which skill to run next, but it should not duplicate skill-specific intro copy or starter prompt variants.
- Use `plugin-author-config/source-category-config.json` for source category ids, labels, preferred plugins/apps, and helper skills. Use `references/source-category-runtime.md` for workflow-time connector use, ON_USE auth behavior, fallback rules, and user-approved source preference storage.
- Use `plugin-author-config/automation-config.md` for default Sales onboarding automation names, frequencies, and instructions. The target thread title is derived from the automation name. Use `references/automation.md` for runtime setup mechanics such as creating heartbeat automations, creating/pinning/renaming target threads, readback, state updates, and cleanup approval.
- Use `references/onboarding-examples.md` only to audit or explain onboarding traces. Examples do not override the rules above.

## Skill Experience Guidance

Every user-facing Sales skill must define skill-owned experience guidance inline in `SKILL.md`. Loading the relevant skill-owned experience guidance is mandatory whenever that skill is the primary workflow. Read the skill's inline `First-Run Banner` and `Next Step Guidance` sections instead of looking for a separate experience reference.

Use skill-owned experience guidance for first-run intro copy, starter prompts, anchor rules, normal next-step candidates, the final continuation invariant for primary outputs and follow-up turns, and onboarding-yield behavior. Do not put skill-specific intro copy, starter prompt variants, anchor rules, or normal next-step behavior in onboarding. Onboarding may choose which skill to run next, but the skill owns how it introduces itself, what a good first try looks like, and which normal continuation to suggest after output, source gaps, fallback answers, clarification responses, and meta-question turns.

When `sales_preflight.py` reports that the current skill has not been introduced and the skill is the primary user-facing intent, the focused skill must interpret `control.current_skill_experience` immediately after preflight, before deciding whether to show a first-run intro, ask for anchors, gather evidence, draft output, or render the final natural continuation:

- If the user asked what the skill does or has not provided enough task detail, show the first-run intro and offer the primary starter prompt.
- If the user already provided enough task detail, render the compact first-run intro section from the skill's first-run guidance before normal output. Then proceed without blocking on starter prompts.
- If the skill is being used as a helper/provider, do not show the intro.
- If onboarding or another parent workflow owns the final CTA, suppress the skill's final continuation and return next-step candidates for that parent workflow to arbitrate.
- After sending the first assistant message for a primary user-facing skill, update `onboarding-state.json` so `skill_experience.<skill>.introduced_at` and `first_tried_at` are set when they are still empty.

After a normal primary output, follow-up answer, fallback/source-gap response, clarification answer, or meta-question response, follow the skill's `Next Step Guidance` exactly: end with one concrete user-visible next action phrased as a natural sentence or question in ordinary prose. Clarification questions must be the final natural continuation. Lead with the actual question the user needs to answer. When concrete lettered options are visible, make them usable as reply targets and omit generic one-detail framing or redundant reply-with-letter footers. Exactly one final visible CTA should appear in the response unless onboarding or another parent workflow explicitly owns the CTA; if the immediate workflow is blocked on a clarification, that clarification outranks onboarding and owns the final CTA.

## State Files

Ordinary workflow preflight should read these files through `scripts/sales_preflight.py`; direct context maintenance and fallback paths may read them manually when the script is unavailable or insufficient.

The configured user-context file is:

```text
$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md
```

The configured onboarding-state file is JSON:

```text
$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json
```

## Customization Guidance

When explaining how to customize Sales, always start with plugin user customization as the preferred path. The user can simply ask Sales to save a preference, example, source link, convention, definition, escalation path, or workflow note, and this skill stores it outside the plugin package in `user-context.md` so future runs can adapt without editing plugin files.

Name the sharing model clearly when relevant:

- `user-context.md` is local, Sales plugin-scoped user context and is not automatically synced to other users, but it is the normal lightweight way to share Sales customization. The user can ask for the full user-context file, edit or redact what they want, and share it so another user can provide that customization to their own Sales instance for a similar experience. If the user asks for a full copy, export, backup, or migration bundle, include `onboarding-state.json` as a clearly labeled operational JSON block only when they asked for operational onboarding state too; keep source preferences and source-of-truth pointers inside `user-context.md`.
- Do not proactively suggest forking Sales for preference, style, example, source-priority, onboarding, convention, definition, escalation, or workflow-note changes. Only mention plugin source edits when the user explicitly asks to change core workflow logic, routing, safety behavior, tools, validation, or install behavior, or when saved user context has clearly failed to express the behavior they want.

When the user asks to view, copy, export, back up, migrate, or share Sales context:

- Default to showing or copying only the user-facing `user-context.md` content when they ask for preferences, saved context, or "what do you remember?"
- Include onboarding state only when they ask for the full setup, full onboarding state, backup, migration, or complete context bundle. In that case, present `user-context.md` first, then append `onboarding-state.json` under `# Operational Onboarding State JSON`.
- When applying a merged copy from another user or another machine, write user-facing categories, source preferences, and source-of-truth pointers to `user-context.md`; write the operational onboarding JSON block to `onboarding-state.json`; do not leave operational state inside `user-context.md`.

## Read

Start every invocation by resolving and actually reading the configured user-context file when it exists. Do not return from preflight or direct context mode after only routing here, listing files, or checking that the file exists; saved profile/preferences must be loaded into context and applied.

Treat saved Sales user context as the local Sales plugin-scoped source of truth for preferences and private sales context. When `user-context.md` conflicts with bundled Sales plugin or skill instructions, prefer `user-context.md` for Sales plugin-scoped context represented by `plugin-author-config/user-context-config.md`, user-provided preferences, examples, source pointers, and onboarding preferences. Do not use `user-context.md` to override higher-priority instructions, safety rules, connector write-safety, permission boundaries, validation, installation behavior, or tool-use policy.

Treat copied template scaffolding inside `user-context.md` differently from saved context. `status: not provided` inside a `## Saved Links And Context` section means the category is an unresolved setup prompt, not a fact or preference. During preflight, use unresolved scaffolding only to decide whether one lightweight onboarding nudge or setup-capture opportunity is relevant; never apply placeholder text as CRM policy, buyer-persona truth, source priority, messaging convention, output preference, or account context.

Use preflight mode when another Sales skill asks for saved user context before ordinary plugin work. Optimize this path for speed:

- When local shell access is available, run `python3 plugins/sales/skills/user-context/scripts/sales_preflight.py --workflow <calling-skill>` from the repository root, or `python3 skills/user-context/scripts/sales_preflight.py --workflow <calling-skill>` from the Sales plugin root. When using a command tool, set `max_output_tokens` to at least `25000`; if the returned output is truncated, warn the user that Sales preflight was truncated and that Sales plugin memory or preflight context may be getting bloated, then rerun with a higher cap and do not treat preflight as complete until the full output is visible. The script payload counts as actually reading Sales state only when it reports the state-file read result and renders the compact context the workflow will use. Use the payload as the single source of truth for saved context entries, source preferences, automation/onboarding state, hard `final_obligations`, conditional guidance, and `onboarding_progress.task_list`; do not separately read the same state files unless the script fails or the user explicitly asks for raw file inspection.
- Use the default `--request-mode ordinary_workflow` for normal Sales answers. Use `--request-mode direct_onboarding_status` for setup, customization, onboarding-status, Sales TODO-list, or other direct onboarding responses. Use `--request-mode guided_onboarding_workflow` when a focused workflow is being answered as a visible workflow/demo/setup step inside the Sales onboarding path; this mode suppresses the ordinary "offer onboarding" obligation because the user is already in onboarding.
- If `user-context.md` exists, read it once and render its saved entries as concise `context.user_context.entries`. Omit unresolved scaffold prose except for compact unresolved category names; direct context maintenance can still read the raw file.
- Use source preferences, "do not use" rules, source-of-truth links, and source-priority guidance from `user-context.md` as connector-selection hints. Do not proactively check connector readiness during preflight. When a focused workflow needs a source, it should try the relevant connector then and handle auth, connection, skip, or manual fallback in that workflow.
- After reading user context, use the script-driven preflight payload for the calling skill, then immediately let the calling skill continue. The compact payload is the visible/auditable preflight context; do not hide a larger raw-state payload behind it.
- Also inspect any saved action-orientation preference. Unless the user has asked for quiet behavior or `user-context.md` says action-oriented follow-ups are declined or suppressed, tell the calling skill to end with one concrete next step that advances the current sales workflow, saves a useful preference/source pointer, proposes a follow-up artifact, checks one missing source or connector, or routes to one relevant sibling workflow.
- Do not browse linked sources, run broad searches, summarize unrelated sections, or ask setup questions during preflight.
- If `onboarding-state.json` exists, parse only the relevant fields for whether onboarding is active, quiet, complete, whether core onboarding is complete, and any concrete next actions. During ordinary preflight, return at most one concrete guided next step that the calling skill may append after answering the immediate request. If core onboarding is still incomplete, the next step should direct the user back to the next unresolved core setup item: connector setup/confirmation or Sales automation setup. During direct onboarding, setup-status answers, or user requests for the Sales TODO list, use `references/onboarding.md` to render one visible action close, using a compact `Next Step` block only when the step needs the label and letting a self-contained numbered choice set stand on its own. Mirror the compact high-level roadmap into the built-in thread task list when available.
- If `user-context.md` is missing, read `references/onboarding.md`, return that no saved Sales user context is available, use the script-driven payload or documented manual fallback to provide conditional context-gap guidance, and let the caller continue. Do not run the initializer or scaffold state merely because context is missing. Do not interrupt ordinary plugin work with setup or stop at a setup request. For a high-intent first-run workflow request, tell the caller to answer the user's concrete query first using bundled instructions, user-provided material, and available connectors or sources; if the requested artifact cannot be completed or is meaningfully weaker because saved context or a source is missing, give the best truthful answer from the attempted sources and name the practical gap using `references/onboarding.md#context-gap-note`. Append the `Ordinary Workflow Onboarding CTA` obligation only when preflight returns it because onboarding has not started; do not offer to start onboarding when `onboarding-state.json` already says onboarding is active.
- If a referenced source is inaccessible, stale, ambiguous, or missing, say that directly only when the missing source affects the current task, then continue with the available context.

### Script-Driven Preflight Payload

Preflight mode must use `scripts/sales_preflight.py` as the authoritative compact payload before ordinary work continues. The script output owns `response_mode`, `control.current_skill_experience`, `context.user_context`, `context.sources`, `context.automations`, hard `final_obligations`, conditional context-gap guidance, and `onboarding_progress.task_list`. Do not hand-author, recreate, or mentally reconstruct the payload when the script is available; use the JSON fields the script returned.

For ordinary Sales workflow requests, honor `final_obligations` exactly as returned by the script. The calling skill must answer the immediate request first, then satisfy any returned onboarding CTA obligation. When the focused skill does not otherwise own a final continuation, append the returned onboarding CTA template with its heading, body, and final reply line intact. When the focused skill has its own final continuation, fold the onboarding reminder or move-on path into that same final natural continuation so the response has one final visible CTA, not a standalone onboarding reminder plus a second skill CTA. Do not downgrade a hard obligation into a `One setup note`, a passive "future prep can get stronger" aside, or a context-gap explanation. Do not use that hard obligation for direct onboarding/setup/status responses, focused workflows launched from the visible onboarding path, or responses where the immediate workflow must ask a required clarification; those callers should use `direct_onboarding_status` or `guided_onboarding_workflow` request mode when appropriate, and clarification-only responses should end with the clarification as the sole final natural continuation.

When the script fails or local shell access is unavailable, fall back to the manual file-read path described above: actually read the relevant state files, use only fields known from those files or the missing-file condition, apply `references/onboarding.md` for direct onboarding/status behavior, and state any missing source or context gap only when it materially affects the current answer. Restore script-driven validation as soon as local shell access is available.

Use direct context mode when the request is primarily about saved context, setup, memory, or context maintenance:

- If `user-context.md` exists, read it before answering or writing.
- If the requested fact or preference is present, answer from the file.
- If the requested fact or preference is absent, say it is not saved yet and offer to add it, unless the user already supplied enough information to save it.
- If the user asks what Sales knows or remembers, summarize `user-context.md` by default. Mention bundled plugin docs only if the user explicitly asks about bundled docs, references, skills, or all available plugin resources.
- When the request starts, resumes, updates, checks, or completes Sales setup or onboarding, perform the requested sub-step and then apply the step cards in `references/onboarding.md` before answering. The first direct onboarding orientation with no existing Sales state is a response-first fast path: render the orientation immediately, then initialize state only after the user approves the next setup step or supplies context to save. Other setup interactions include customization, onboarding-status checks, Sales TODO-list requests, memory saves while onboarding is active, Sales Company Research save/proposal follow-up, automation setup or cleanup while onboarding is active, and completed or deferred guided workflow updates.
- Treat onboarding-status questions such as "have we onboarded yet?", "am I set up?", "is Sales configured?", or "what setup is missing?" as direct onboarding interactions, not as ordinary context lookup. Answer the status through the common onboarding finalizer: if onboarding is missing or active, strongly guide the user into the current action close with the shared direct-onboarding structure and built-in thread task list updates when available; if onboarding is complete, say so and offer one useful Sales workflow. Do not end an incomplete onboarding-status answer with only a passive or optional setup suggestion.

Outside explicit Sales Company Research or linked-source refresh work, retrieve linked Google Docs, Drive files, Notion pages, or other resources only when they are accessible through available connectors or explicit local APIs and the user asked to inspect or refresh that source. Do not use browser automation, in-app browser, or Computer Use as fallback retrieval paths for ordinary context-source retrieval.

## Onboarding

Use `references/onboarding.md` as the source of truth when the user asks what Sales can do, asks to set up or customize Sales, invokes onboarding, asks whether onboarding is complete, asks for Sales TODOs, or when `onboarding-state.json` says onboarding is active and a nudge is due. During ordinary preflight, do not show full onboarding; parse only relevant JSON fields and return the hard onboarding-offer obligation with the `Ordinary Workflow Onboarding CTA` template only when onboarding has not started, plus at most one conditional context-gap note when the current answer is materially weakened by missing setup. When onboarding is already active during an ordinary workflow, do not ask whether to start onboarding. If core onboarding is incomplete, answer only urgent or directly requested Sales work and direct the user back to the next unresolved core setup item. If core onboarding is complete, preserve the workflow's own final natural continuation and mention resuming guided onboarding only as a short non-competing note when it is directly useful. During the first direct onboarding message with no state, render the orientation and action close directly from `references/onboarding.md` without creating scaffold files first. During later direct onboarding, setup, customization, memory-save, guided-workflow-update, or Sales TODO-list paths while onboarding is missing or active, follow the current step card in `references/onboarding.md`, render one visible action close, and mirror the compact high-level roadmap into the built-in thread task list when that tool is available. When a focused workflow is run from that visible onboarding path, call preflight with `--request-mode guided_onboarding_workflow` so the workflow can answer normally without adding a redundant onboarding reminder.

Use `plugin-author-config/source-category-config.json` for category definitions and preferred plugins/apps, and `references/source-category-runtime.md` for workflow-time connector use and source preference storage. Use each user-facing skill's inline experience guidance for skill-specific introductions, starter prompts, anchor rules, and next-step candidates. Use `references/onboarding-examples.md` only to audit or explain the onboarding experience across cases.

When direct context work happens while onboarding is missing or active, apply the step-card continuation in `references/onboarding.md` before finalizing. This includes setup, onboarding-status checks, customization, Sales Company Research save/proposal follow-up, proposed user-context updates, memory saves, automation state changes, skill-experience updates, and preference changes. The current step card supplies the next action, and a recap of the just-completed sub-step is not sufficient unless onboarding is complete, quiet, or stopped by the user.

## Action-Oriented Continuation

Default Sales outputs should be useful launchpads, not dead ends. In almost all cases, after answering the user's immediate request, add one concise next step that helps them act on the result. Good next steps continue the same workflow by iterating, drafting or preparing the next artifact, offering a supported post/share/save/write action, or checking one missing source or connector that materially affects the current work. Do not recommend moving to another Sales skill as a generic continuation; only route elsewhere when the user's request has clearly changed or the current skill's own routing rules say another workflow owns the job.

Treat durable memory as a supporting lane, not the default primary CTA, unless the user directly asked to remember/save something or the workflow is in direct memory mode. When a run surfaces a potentially reusable preference, broad instruction, or source shortcut, first apply `references/plugin-memory.md` to decide whether to save now, ask before saving, or only mention it. If it is useful but not the main next action, render it as a short non-competing note before the final natural continuation, then keep the final CTA focused on iterating, operationalizing, or continuing the active sales artifact.

Avoid asking for setup context merely to fill onboarding state. Ask only high-uncertainty, high-impact questions whose answers would significantly improve future outputs, downstream memory triggering, memory usage criteria, or the active workflow. If onboarding is active, the current step card in `references/onboarding.md` governs the next step; otherwise use the ordinary action-oriented continuation rules here.

Show at most one direct CTA during ordinary workflow output unless the user explicitly asks for options, onboarding, setup, or the Sales TODO list. When onboarding has not started in an ordinary workflow, that CTA must be the `## Sales Setup Required` template from preflight, even if the immediate artifact is otherwise complete, unless the immediate workflow is blocked on a required clarification. Clarifications always become the final natural continuation and suppress onboarding CTAs for that response. When onboarding is already active and core onboarding is incomplete, direct the user to finish the next core setup item before continuing non-urgent Sales workflows. When onboarding is active and core onboarding is complete, preserve the workflow-owned final natural continuation and mention resuming guided onboarding only as a short non-competing note when useful. For direct onboarding and setup-status flows, follow `references/onboarding.md` instead: render one visible action close, mirror the compact high-level roadmap into the built-in thread task list when available, and check tasks off as the user completes, approves, declines, or makes them unnecessary. Skip the CTA only when the user asks for quiet behavior, the request is sensitive or high-pressure enough that a follow-up would be distracting, onboarding is complete and the workflow has no reasonable next action, or `user-context.md` records that action-oriented follow-ups are declined or suppressed.

If the user declines action-oriented endings or asks for quieter endings, save that preference under a concise category such as `# Action Orientation Preferences` using `references/plugin-memory.md`, and update `onboarding-state.json` to `quiet` when the request is specifically about onboarding nudges. If the user asks to resume action-oriented guidance, update the same category rather than adding a duplicate.

## Plugin Memory

Use `references/plugin-memory.md` for direct remember/save requests, broad future-facing instructions, correction capture, Sales Company Research save/review gates, linked-source population, and successful-run learning.

That reference is the source of truth for what to save, when to ask a high-leverage clarification, how to write clear memory entries, how to include remote doc/resource links, how to inspect accepted artifact iterations for reusable plugin memory, and how to recap saved memory with the right user-facing save or research-complete copy.

## Validation

After editing `scripts/sales_preflight.py`, state-file templates, onboarding finalization rules, memory write policy, or this skill's state-helper contract, run:

```bash
python3 -m unittest discover -s plugins/sales/skills/user-context/tests -p "test_*.py"
```

The tests must use temporary state directories and must not read or write the user's real `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}` files.

## Write

Write only Sales plugin-scoped user context to `user-context.md`: context represented by `plugin-author-config/user-context-config.md`, user-provided preferences, examples, source links, source-of-truth pointers, source priority, "do not use" source rules, definitions, constraints, conventions, setup priorities, and other private context that can improve future Sales workflows. Do not store connector readiness, automatic availability, operational onboarding status, connector-audit bookkeeping, skill-experience progress, or automation metadata in `user-context.md`; store onboarding progress or automation metadata in `onboarding-state.json`. Conversely, do not duplicate saved resources, saved categories, source URLs, artifact text, or saved-memory recaps into `onboarding-state.json`; keep those in `user-context.md`, the pinned research thread, or the live source.

First-run state creation remains automated when persistence is needed: run `python3 plugins/sales/skills/user-context/scripts/init_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/init_user_context_state.py` from the Sales plugin root, to copy `plugin-author-config/user-context-config.md` and seed `onboarding-state.json` from `references/onboarding-state-template.json` plus `plugin-author-config/automation-config.md`. Do not run this command just to show the first direct onboarding orientation. In sandboxed local-shell environments, request elevated execution on the first attempt because the target state directory is under `$CODEX_HOME`, not the project workspace. After that initialization, modify `user-context.md` directly. Do not call a write utility for ordinary memory saves, proposal saves, correction capture, source-link saves, or Sales Company Research approvals. For multi-entry approvals, read the current state once, update every touched category in one coherent edit, update `onboarding-state.json` only for changed operational bookkeeping, then run `scripts/sales_preflight.py --workflow user-context` or the relevant workflow preflight to confirm the saved context reads back cleanly. Never run parallel writes against the same Sales state files.

For discovery-derived, inferred, or not-yet-approved context, present the proposed entries in chat first and save only after the user approves the exact entries. Once approved, write the approved entries directly to `user-context.md`; do not ask the user to approve a helper command or perform one write per entry. If the direct edit is blocked by missing files, run the automated first-run initializer, reread the resulting files, and then apply the approved edit.

For explicit debugging reset requests only, run `python3 plugins/sales/skills/user-context/scripts/reset_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/reset_user_context_state.py` from the Sales plugin root, after the user explicitly asks to clear or reset local Sales plugin state for debugging. The helper moves known Sales state files to a timestamped sibling backup directory and leaves no active Sales state files behind when the state directory becomes empty. Never perform this reset for ordinary onboarding, memory edits, setup retries, source-refresh work, or vague troubleshooting. Prefer a dry-run-style explanation first when the request is ambiguous; report the backup path and mention that restoring means moving the backed-up files back into the state directory. If the helper is unavailable or fails, fall back to a manual backup move only when the user has clearly requested the reset, and report that fallback explicitly.

For write decisions, bias toward saving useful, low-risk Sales memory; infer definition, trigger, usage, source authority, freshness, and exclusions as much as possible; ask only when a clarification would significantly tighten future triggering, usage criteria, source authority, or freshness; read accessible remote sources before deriving memory from them; include stable source links in `user-context.md`; and recap saves using the copy in `references/plugin-memory.md`. Load `references/plugin-memory.md` when the write is ambiguous, source-derived, broad future-facing, correction-driven, or otherwise needs the full policy.

Use this category-block structure:

```md
# {Category}

- Description: {what this category is or does and when future Sales runs should apply it}

## Saved Links And Context

status: not provided
```

`user-context.md` is a user-editable surface. The user and agent can edit category names, `Description`, and `Saved Links And Context` directly. The agent may create new categories or revise category descriptions when the existing categories do not fit cleanly, when a clearer category would improve future triggering, or when discovered context changes how the category should be applied.

Put saved resources, linked docs, source pointers, channels, and user-confirmed facts under `## Saved Links And Context` using this shape:

```md
Resource or fact name (use a real Markdown link when a stable URL is available; otherwise use a connector-visible reference in plain text)
- Date Added: YYYY-MM-DD.
- Useful Context: {what this resource or fact represents}
- Future Use: {how future Sales runs should use it}
```

When a category has no saved resources yet, use exactly `status: not provided` under `## Saved Links And Context`. Do not add wrapper labels such as `Saved Information`, `Saved Context`, or `User-provided context`. When saving inline context with no external source, make the preference or fact itself the resource name and describe its origin in `Useful Context`; do not add filler bullets such as `user-provided inline`. Use the current date for `Date Added` when the resource is first saved; preserve the original date on later edits unless the old date is clearly wrong. Use `Future Use` for forward-looking retrieval, freshness, source-priority, and application guidance.

Keep `## Saved Links And Context` curated. Prefer one to three high-quality resources per category. Dedupe repeated URLs, titles, channels, and functional equivalents before saving; merge useful details into the best resource instead of adding parallel entries. Save only resources that add non-obvious, high-consequence guidance beyond what the active connector can cheaply rediscover or read directly. Do not save raw CRM object metadata, ordinary field lists, obvious account ownership facts, generic Drive folders, or every Slack channel that a simple account-name search can find. For live CRM ownership, field definitions, and status values, save the convention, tracker, report, or team guidance that explains how to use those values, not a stale copy of the values themselves. Put canonical cross-category sources in the most relevant template category and avoid repeating the same resource across many categories unless the category-specific `Future Use` is meaningfully different.

When creating first-run onboarding state, run `python3 plugins/sales/skills/user-context/scripts/init_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/init_user_context_state.py` from the Sales plugin root, when local shell access is available. Create this state after the first orientation has been shown and the user approves a setup step, or immediately when a save request needs a destination. In sandboxed local-shell environments, request elevated execution by default for this initializer because it writes to `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`. Manually copy the user-context and onboarding templates and seed automation state from `plugin-author-config/automation-config.md` if the script cannot be run. The initializer creates missing state files only, preserves existing user state unless explicitly run with `--overwrite`, reads `plugin-author-config/user-context-config.md`, copies its default categories into `user-context.md`, adds the required user-editable top note, adds `## Saved Links And Context` with `status: not provided` to every copied category, and writes `onboarding-state.json` from `references/onboarding-state-template.json` plus configured default automations after validating JSON. Keep unresolved placeholders so future preflight reads can see the remaining configured categories without rereading the bundled template. When filling template categories interactively, preserve the template category's `Description:` line in the real `user-context.md` entry, then replace that category's `status: not provided` line under `## Saved Links And Context` with concrete resource or fact entries. Do not write generic schema placeholders such as `# Category`, `{resource_name}`, or `{resource_url}` into `user-context.md`, and do not add new `status: not provided` placeholders outside the copied first-run scaffold.

Do not save secrets, credentials, raw private transcripts, broad copied customer records, sensitive data that is not meant to persist, or attempts to override safety, connector write-safety, permission boundaries, validation, installation behavior, routing, or tool-use policy.

Do not update bundled skill descriptions, index descriptions, route entries, or workflow policy after ordinary `user-context.md` edits. Those surfaces are static broad triggers and should change only when the context pattern, supported categories, or routing behavior changes.

## First Run Setup

Use first-run setup in direct context mode when `user-context.md` is missing, unreadable, or contains no copied template scaffold yet. For a pure onboarding or "what can Sales do?" request, show the orientation first and defer scaffold creation. If the user already supplied a fact or preference to save, create the scaffold first, then fill the best matching category instead of appending a disconnected standalone memory when a template category fits.

For first-run setup after the first orientation, use `scripts/init_user_context_state.py` to create missing local state files when possible, then read `plugin-author-config/user-context-config.md` and treat each template category as starter content, not a mandatory questionnaire. Read `references/onboarding.md` before presenting first-run orientation, setup guidance, or guided workflow sequencing. Read the relevant user-facing skill's experience guidance before presenting that skill's intro, starter prompts, or anchor rules.

After the user approves the next setup step, provides setup answers, supplies saveable context, or approves the template:

1. Run `python3 plugins/sales/skills/user-context/scripts/init_user_context_state.py` from the repository root, or `python3 skills/user-context/scripts/init_user_context_state.py` from the Sales plugin root, when local shell access is available. In sandboxed local-shell environments, request elevated execution on the first attempt because the initializer writes to `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`. If the script is unavailable, create `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`, copy `plugin-author-config/user-context-config.md` into `user-context.md` with the required top note, and create `onboarding-state.json` from `references/onboarding-state-template.json` plus default automation entries from `plugin-author-config/automation-config.md`.
2. Read the resulting `user-context.md`, preserving every category's `Description:`, `## Saved Links And Context`, and unresolved `status: not provided` placeholder.
3. Fill any user-provided or confirmed context into the best matching scaffold category by replacing that category's `status: not provided` placeholder with concrete resource or fact entries. If no template category fits, add a concise new category block after the scaffold.
4. Read the resulting `onboarding-state.json`, then update onboarding-state with operational onboarding progress, skill experience progress, and configured automation metadata. Save any source preference, default, source pointer, or "do not use" instruction in `user-context.md` only when the user explicitly provides or approves it.
5. Continue the user's original request using the newly saved context.

If the user declines setup, continue the original request without saved context. Keep the explanation user-facing; do not describe internal files unless the user asks.
