# Sales Onboarding Flow

Use this reference when `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` is missing or unreadable, when the user asks what Sales can do, when the user asks to set up or customize Sales, or when `onboarding-state.json` says onboarding is active and a nudge is due.

Onboarding is a mostly linear, nested step-card playbook. It is not a formal graph. Each step owns setup copy, output contract, action close, completion behavior, skip or defer behavior, and any loop or optional branch. Every onboarding message should handle one major user-visible step at most, mirror the overall progress list when the UI is available, and end with one clear action or question.

Store durable personalization and user-approved source preferences in `user-context.md`. Store only operational onboarding progress, including connector-confirmation labels, skill experience progress, automation setup, and discovery proposal status, in `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json`. Do not put saved-resource manifests, saved-category lists, source URLs, research result bodies, or artifact text in onboarding state; keep that content in `user-context.md`, the pinned research thread, or the source system. Do not create, read, or update durable connector-readiness proof as part of onboarding. Sales workflows use plugins, apps, or connectors when the workflow needs the source.

The first direct onboarding response is a response-first fast path. When the user asks to onboard, set up, or learn what Sales can do and no Sales state files exist yet, render Step 1 immediately. Do not run `../scripts/init_user_context_state.py`, write scaffold files, inspect connectors, audit conflicts, create threads, install automations, start discovery, or run workflows before that first message. After the user approves the next visible setup step, or whenever the user supplies context that should be saved, use `../scripts/init_user_context_state.py` when local shell access is available. In sandboxed local-shell environments, request elevated execution by default because it writes to `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`.

Related sources of truth:

- Use `plugin-memory.md` for all plugin memory save/update policy, linked-source population, broad instruction capture, correction capture, Sales Company Research save/review policy, iteration-to-memory review, and the required saved-memory or research-complete recap copy.
- Use `../scripts/init_user_context_state.py` to create missing first-run state files only after the first orientation message has been shown and the user approves the next setup step, or immediately when the user provides context that should be saved.
- Use `../plugin-author-config/user-context-config.md` as the source for plugin-specific memory category names and compact descriptions.
- Use `../plugin-author-config/source-category-config.json` for static source category ids, labels, preferred plugins/apps, and helper skills. Use `source-category-runtime.md` for plugin-first source setup, onboarding connector-confirmation labels, workflow-time source attempts, ON_USE auth behavior, fallback rules, and durable source-preference storage.
- Use each user-facing skill's inline experience guidance for first-run intro copy, starter prompts, anchor rules, normal next-step candidates, and onboarding-yield behavior.
- Use `../plugin-author-config/automation-config.md` for the author-owned default automation catalog. Use `automation.md` for runtime setup mechanics: installing configured defaults during onboarding, deriving target thread titles from automation names, creating target threads, pinning and renaming them, kicking off Sales Company Research in the pinned thread, readback checks, duplicate cleanup, and failure reporting.
- Use `onboarding-examples.md` for illustrative audit traces only.

## Skill Experience Delegation

Onboarding chooses which user-facing skill to try next, but the focused skill owns how it introduces itself and what a good first try looks like.

Before introducing or running a user-facing skill during onboarding, load that skill's inline experience guidance from `SKILL.md`. Use that guidance for:

- first-run intro copy;
- starter prompts and realistic `@Sales` examples;
- anchor rules and sensible defaults;
- normal next-step candidates;
- onboarding-yield behavior.

Do not duplicate skill-specific intro copy, starter prompt variants, anchor rules, or normal next-step behavior in this file. If the focused skill has enough user intent to run and has not been introduced yet, it should render the compact first-run intro section from its skill-owned guidance before normal workflow output. If onboarding or another parent workflow owns the final CTA, the skill should suppress its own final CTA and return status plus next-step candidates for that parent workflow to arbitrate.

For hero prompts, onboarding owns the choice set and sequencing, but each skill still owns the prompt wording. The first hero chooser offers up to three core hero skills from `prepare-for-meeting`, `follow-up-after-call`, and `prioritize-accounts`. Later hero choosers may include previously tried workflows as repeat options plus at least one untried core workflow while any remain. Build the user-facing option labels and one-sentence descriptions from each skill's experience guidance; do not make preflight carry those descriptions, and do not include sample prompts inside the chooser. Once the user picks an option, treat the numbered choice as consent to try that workflow with its recommended default anchor. Record the selected skill in onboarding state, render that skill's compact first-run intro above the normal workflow output, and run the workflow unless the selected skill truly cannot proceed without one missing anchor. After that hero workflow is accepted, skipped, or deferred, offer the skill-owned next artifact action when useful, then return to the next demo workflow chooser.

## Common Onboarding Message Frame

Every onboarding message that is not complete must include primary content for the current step, then leave the user with one clear way to move forward. A natural final sentence, a compact action frame, or a self-contained numbered choice set can satisfy this requirement. Use the reference copy as the preferred onboarding voice and structure: preserve its core claims, ordering, and plain-language tone wherever the current setup state allows. Adapt only to reflect real source availability, skipped/deferred setup, installed plugins/connectors, or the user's current onboarding step. Do not revert to the older rigid `Next Step` cadence when a natural action question or selectable choice set is clearer, and do not introduce extra setup concepts not present in the reference copy.

Use this compact action frame when the step has multiple questions, a durable approval gate, or a complex choice that needs an explicit label:

```md
**Next Step**
{One clear action or question the user can answer now.}
```

`Next Step` is the action prompt, not the explainer. Put step results, workflow introductions, setup explanations, and teaching content in the primary content immediately before the frame, then keep `Next Step` short and decision-shaped. For simple one-question steps, a natural final sentence such as `Ready to set that up?` or `Should I set those up?` is preferred. For chooser steps where each numbered option is concrete and selectable, the list itself is the action prompt; do not add a redundant `Next Step` heading or final sentence such as `Pick 1, 2, or 3`. Do not let the whole onboarding message be only a next-step frame.

When the current step has open questions, make resolving those questions its own visible onboarding step before introducing the next workflow. Include the questions in `Next Step` instead of leaving them only in the preceding step summary. Use a compact numbered list when there is more than one question. If the questions can be handled by sensible defaults, include the default escape hatch inside the relevant numbered item, including which defaults will be used and which optional gaps will be skipped, deferred, or revisited later. Do not add a separate summary prompt after the numbered list when the list already contains the questions and default path. Do not combine meaningful source, preference, admin, approval, or skip/defer decisions with a first-time workflow introduction.

When introducing a workflow, skill, or new onboarding concept for the first time in the current onboarding flow, introduce it in the primary content before the action close. For skills, use that skill's experience guidance. For onboarding concepts such as plugin memory or automations, briefly explain what it does, what inputs or state it can use, what output or result the user should expect, the recommended default action, and the option for the user to skip or provide a specific anchor instead. Keep the action close to the small action the user can take. Use the New Concept Introduction Pattern below whenever the current response enters a new concept.

When showing user-facing sample prompts during onboarding, teach the preferred invocation pattern: start with `@Sales`, then state the sales job and the real anchor in natural language. Sample prompts should be realistic and seller-shaped, such as `@Sales prepare me for my Acme renewal call tomorrow.`, not placeholder-only prompts. If the prompt is meant to run against the user's actual context, fill it with a real meeting, call, account, or topic before showing it; otherwise label it as an example for later use.

Do not create tiny transition turns whose only purpose is asking whether to introduce the next onboarding item. If the current step has completed and the next item is an intro-only step, add a short transition note such as `Okay, I've saved that. Now let's move on to the next step.` or `Great, moving on.`, then render the next concept introduction or next hero choice card in the same response with one final action close. Preserve real approval gates: first-time plugin memory should introduce `## Plugin Memory` before the first save and then save accepted narrow, low-risk workflow preferences by default; Sales automations should use a short transition sentence and ask whether to set up the recommended automations without a separate `## Sales Plugin Automations` heading; externally visible writes, docs, Slack/email drafts, high-risk memory, and connector setup still need their own approval when the step requires it.

In the hero workflow loop, user replies such as `next workflow`, `move on`, `next demo`, `next guided workflow`, `continue`, or similar mean "show the next demo workflow choices," not "auto-run the next sequential skill." Treat that reply as acceptance or skip/defer of the current artifact as appropriate, save any accepted narrow reusable preference if plugin memory policy allows it, clear the active selected skill for the next choice, and enter `choose_next_hero_prompt`. Do not run another hero workflow until the user picks `1`, `2`, or `3`, names a workflow, or gives a specific meeting, call, or question anchor.

Exactly one final visible CTA or self-contained choice set should appear in the response. FYIs, readbacks, and automation breadcrumbs should be separate from the final action close and should not compete with it.

When onboarding is done, use this terminal frame:

```md
**Onboarding Complete**
Congrats, you're set up. Sales now has the context, preferences, automations, and example workflows it needs to be useful in your day-to-day work.

You've tried the three core workflows: Prepare For Meeting, Follow Up After Call, and Prioritize Accounts.

You can keep going through the rest of the Sales skills one by one to get familiar with what else is available. Next up, I recommend **Analyze Account Signals**, which helps find recent account and customer signals for an active account, owner portfolio, or watchlist.

**Next Step**
Say `okay` and I'll introduce Analyze Account Signals, or start a new thread and include `@Sales` with any real Sales request.
```

Do not render `Next Step` as an H1/H2/H3 heading. Keep implementation details out of user-facing onboarding. Do not narrate file structures, cache paths, state paths, context-file mechanics, internal probe names, provider taxonomy, or raw state names unless the user explicitly asks for implementation details.

## New Concept Introduction Pattern

Use this pattern when the response enters a new skill or concept. It may appear after a short recap of the just-completed step when the only alternative would be a low-value `Want me to introduce...` transition. Keep exactly one final visible action close for the current actionable decision. Use a `**Next Step**` label only when the decision needs the label.

```md
## {Concept Name}

{Concept explanation.}

Example prompt: `@Sales {realistic prompt with a real or clearly illustrative anchor}.`

**Next Step**
{One compact action, approval question, or anchor request.}
```

For plugin memory, use `## Plugin Memory` and start the body with `Plugin memory is how the Sales plugin remembers approved preferences, source-of-truth links, examples, and team conventions for future Sales workflows.`

For Sales automations, do not render a separate `## Sales Plugin Automations` heading. Start with a simple explanation that these are recurring Codex tasks for company research and tips.

For skill introductions, use the skill display name as the heading, such as `## Prepare For Meeting`, not the machine skill id. Because the heading already names the skill, the body should start with `This skill...`, not `{Skill Name} is a skill in the Sales plugin...`. Do not render user-facing CTAs with code-styled skill names such as `follow-up-after-call`; say `Follow Up After Call`.

User-facing bullets should be polished sentence fragments or full sentences. Do not start bullets with lowercase words unless they are grammatically continuing an introductory sentence. Prefer capitalized fragments such as `A quick call summary`, `Next steps and owners`, and `External follow-up copy when relevant`. Bullets may omit periods when they are fragments; full-sentence bullets should use periods consistently.

## Progress Checklist Contract

Mirror this user-visible roadmap into the built-in thread task list whenever available. The labels should describe the overall onboarding flow, not implementation substeps.

1. Orientation
2. Connector setup/confirmation
3. Sales automation setup
4. First hero prompt
5. Other hero prompts

Do not replace this checklist with local work-plan labels such as `Load Sales memory policy`, `Search useful resources`, `Draft proposed Sales context`, `Ask for approval to save`, `Probe active connectors`, `Create prep doc`, or `Attach calendar artifact`.

Before every onboarding response, refresh the checklist from current onboarding state after applying actions from that turn. Do not reuse a stale checklist from an earlier thread turn. If the response completed, skipped, or deferred a step, mark that step accordingly and mark the next unresolved visible step as `in_progress` before sending. This is especially important late in onboarding after automation setup, draft creation, call-follow-up iteration, prioritize-accounts handoffs, or completion handoffs.

Treat **core onboarding** as complete after the first two setup items after Orientation are resolved: connector setup/confirmation and Sales automation setup. Until core onboarding is complete, ordinary `@Sales` workflow prompts should answer only when they are urgent or directly requested, then direct the user back to complete the next unresolved core setup item. After core onboarding is complete, Sales can continue through the guided workflows or handle ordinary Sales work without a core-setup warning.

Treat a plain `yes`, `yep`, `ready`, `get started`, or similar reply after a next-step CTA as approval to perform the current visible next step unless the user names a different step. Treat `skip`, `skip for now`, `not now`, or similar as approval to mark the current visible step skipped or deferred when that step allows skipping, then continue to the next step.

## Step 1: Orientation

- ID: `start_sales_onboarding`
- Type: `linear`
- Parent: none
- State field: `orientation`
- User-facing goal: Introduce the Sales plugin, explain what onboarding will do, and get to the first setup action quickly.
- Entry condition: Direct onboarding trigger, first-run setup, "what can Sales do?", or resumed onboarding with orientation missing.
- Stay here when: No state files exist and the first orientation has just been rendered.
- Exit when: The user approves the next setup step, provides saveable Sales context, or state already records that orientation was shown.
- Completion: Record orientation as shown only after state exists.
- Next: Step 2, `confirm_connected_sources`.
- Output contract: Render the reference copy below as the preferred copy spine. Preserve the core claims, order, and plain-language tone while adapting only to the user's current setup state. Do not add connector results, scaffolding, automation setup, discovery, or workflow output to this first message.
- Reference copy spine:

```md
The Sales plugin improves Codex at sales-related work by pulling in relevant business context and leveraging expertly created workflow logic.

**How it works**
- It automatically improves your experience for a range of sales-related work.
- You can also explicitly use it by adding `@Sales` to your Codex messages.

**What it can do**
1. Level up your meetings by building a personalized brief beforehand with exactly what you need to know and what needs to get done, then helping with follow-up.
2. Help you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.
3. Help you win deals by prepping customer-focused competitive briefs, positioning your offerings, and understanding new features so you have the most up-to-date knowledge.

These workflows require access to your CRM, meeting notes, Slack, email, docs, and other context to perform well. Ready to set that up?
```

- Do not: initialize state, inspect connectors, audit conflicts, create threads, install automations, start discovery, or run workflows before this first message.

## Step 2: Confirm Active/Missing Sources

- ID: `confirm_connected_sources`
- Type: `linear`
- Parent: none
- State field: `connector_confirmation`
- User-facing goal: Give the user confidence about which source categories look usable and ask only for help where a source is ambiguous, missing, or needs IT/admin enablement.
- Entry condition: Orientation is complete or the user explicitly asks to continue setup.
- Stay here when: Source classification has not run or the connected-sources result has not been shown.
- Exit when: Every source category is recorded as `active`, `missing`, `declined`, `deferred`, `skipped`, or `not_applicable`, or the user chooses to continue with known gaps.
- Completion: Store onboarding confirmation labels and the resolved source routes in `onboarding-state.json`; do not write connector readiness to `user-context.md`.
- Next: Step 2A, `resolve_source_questions`, when any source category needs user input; otherwise Step 3A, `introduce_sales_automations`.
- Output contract: Return a concise standalone connected-sources result with one setup-ready heading line, bold bullets for available sources, one sentence naming remaining source gaps, and one clear setup question. Active connector/app sources are informational fallback routes, not winners, when a related plugin is installed or installable. This setup step, not preflight, inspects the environment, calls `functions.list_available_plugins_to_install` once for the setup pass, and writes resolved routes for each source category. Ask only when there are multiple mutually exclusive installed source tools, an installable related plugin needs approval, no source was found, or the category needs IT/admin help. Do not ask for a docs preference merely because both Google Drive and Notion are available; record both routes and let workflows use both. For missing sources and connector-covered sources, prefer plugin setup, then direct app/connector setup, then manual exports or pasted context. Do not introduce or run the first workflow in the same response when source questions remain. When the common preferred sources match the current session, use this style:

```md
After some searching, it looks like you're already set up with Google Calendar, Gmail, Slack, Google Drive, Notion, and Spreadsheets.

There are a few more connectors we can add to help Sales work as well as possible:

1. **CRM** provides account status, deal stage, owners, contacts, pipeline risk, and what needs to happen next.
   Options: Agentforce Sales, HubSpot, Close, Zoho, Pipedrive.
2. **Meeting notes** improves meeting prep and follow-ups, and grounds CRM updates in real customer context.
   Options: Zoom, Granola, Otter.ai, Fireflies, Outreach, Rox.
3. **Data enrichment** fills in company and contact details when account context is thin, so prioritization and outreach are sharper.
   Options: ZoomInfo, Clay, HG Insights, Rox, Apollo, Actively, Meticulate.
4. **Contracts** surfaces signature status, approval routing, and deal paperwork blockers before close or renewal conversations.
   Options: Docusign.

You'll be prompted to install and authenticate plugins or connectors for whichever you select. You can skip anything now; Sales will ask again later only when a workflow would materially benefit from one of these systems.
```

Do not render separate `Active sources`, `Sources I need your help with`, or `Missing sources and practical impact` headings unless the source result is too unusual for the concise shape.
- Reference copy: Active and appropriate sources are FYI only. Do not preflight-read installed or active sources just to prove they work. For each category, compare `saved_source_preferences` and `preferred` from preflight, `preferred_plugins`/`preferred_apps` from `source-category-config.json`, `.app.json` ids for preferred apps, the session `Available plugins` and `Available skills` blocks, and the single `functions.list_available_plugins_to_install` result for the setup pass. If one or more related plugins are installed with visible skill/tool surfaces, write them to `connector_confirmation` as active routes under `routes[]` with `source_kind: plugin`, `skill_surface`, plugin details, and evidence fields. If no related plugin is active but a related plugin is installable, highlight it as the recommended setup action even when an app or connector route is already active; explain that Sales should prefer the plugin because it can add dedicated Sales workflow support, and keep the existing app/connector route as fallback if the user defers or install visibility is pending. Rank plugin candidates by saved preferences first, then configured `preferred_plugins`/`preferred_apps`, then `.app.json` connector-id intersections. If no related plugin is installed or installable and exactly one plausible app or connector is installed or available, write it as active with `source_kind`, `skill_surface`, and route details when available, then let the workflow's first real read handle auth, query, or schema issues. If multiple plausible source tools are complementary rather than mutually exclusive, such as Drive and Notion for docs, write multiple active routes instead of asking the user to pick a winner. If multiple plausible source tools are mutually exclusive for the same category, ask the user which one to prefer and write the selected route only after resolving its plugin, app, connector, or manual route. Missing sources should explain practical workflow impact and list specific IT/admin options. Be prescriptive about pilot setup: Salesforce/CRM unlocks account, opportunity, pipeline, owner, forecast, and contact context; Calendar unlocks upcoming meetings, invite details, attendees, timing, and daily prep; Zoom, Granola, Fireflies, or another meeting-notes source unlocks transcripts, customer language, commitments, objections, and follow-up evidence; Slack/internal messaging unlocks account-team coordination and internal blockers; Drive/Docs/Notion unlock account plans, MAPs, discovery notes, source-of-truth docs, and enablement assets; agreement sources unlock contract status, signature progress, approval routing, and deal-paperwork context.
- Data enrichment copy: Data enrichment adds missing company, contact, account, firmographic, technographic, and market-signal details from trusted third-party or internal data sources. It cleans up account lists, discovers contacts, fills thin CRM context, and scans market signals when the core CRM does not have enough detail. Preferred options are ZoomInfo, Clay, HG Insights, Rox, Apollo, Actively, or Meticulate. If none is available in this Codex environment, say that clearly and ask the user to contact IT or a workspace admin to see whether access can be enabled.
- Next-step copy: If one or more source categories need user input, make the `Next Step` only about resolving those questions. If no source questions need input, move directly into Step 3A with a short transition note and the Sales automation introduction; do not ask whether to introduce it.

### Step 2A: Resolve Source Questions

- ID: `resolve_source_questions`
- Type: `optional`
- Parent: `confirm_connected_sources`
- State field: `connector_confirmation`; optional user preference saves go to `user-context.md`.
- User-facing goal: Let the user answer or skip meaningful source choices before Sales introduces the next workflow.
- Entry condition: Connected-source confirmation found multiple plausible apps, no app, or IT/admin source gaps that need a user choice, preference, or acknowledgement.
- Stay here when: The user has not answered, skipped, deferred, or accepted defaults for the source questions.
- Exit when: The user provides the preference/source info, says to continue with defaults, skips, or defers the source questions.
- Completion: Save any clear low-risk source preference to plugin memory using `plugin-memory.md`; record skipped/deferred/default handling in `onboarding-state.json`. A user-selected source may be recorded as `active` when its plugin, app, or connector is installed, available, surfaced, or active in the current environment with enough evidence for the route kind. The state entry must include the resolved route fields such as `source_kind`, `skill_surface`, and plugin/app/connector/manual details when available. Do not create durable connector-readiness proof.
- Next: Step 3A, `introduce_sales_automations`.
- Output contract: Keep primary content focused on the source result and practical impact. Put only the unresolved source questions and skip/defer escape hatch in the action close. Do not ask for a docs preference when multiple docs routes can be used together:

```md
Please select any connectors you want to set up now:

1. **CRM** provides account status, deal stage, owners, contacts, pipeline risk, and what needs to happen next.
   Options: Agentforce Sales, HubSpot, Close, Zoho, Pipedrive.
2. **Meeting notes** improves meeting prep and follow-ups, and grounds CRM updates in real customer context.
   Options: Zoom, Granola, Otter.ai, Fireflies, Outreach, Rox.
3. **Data enrichment** fills in company and contact details when account context is thin, so prioritization and outreach are sharper.
   Options: ZoomInfo, Clay, HG Insights, Rox, Apollo, Actively, Meticulate.
4. **Contracts** surfaces signature status, approval routing, and deal paperwork blockers before close or renewal conversations.
   Options: Docusign.

You can skip anything now; Sales will ask again later only when a workflow would materially benefit from one of these systems.
```

After the user answers, install confirmed plugin or connector candidates one at a time, save any clear source preferences or accepted skips, then move directly into the Sales automation introduction. Do not ask whether to introduce it. For routine source setup preferences in onboarding, do not render the full `Saved Sales Plugin Memory.` recap or `Saved today` list; use only the short transition line below, then render Step 3A in the same response:

If the user confirms an installable plugin or connector candidate returned by `functions.list_available_plugins_to_install`, call `functions.request_plugin_install` with `action_type: "install"`, the returned candidate `tool_type`, the returned candidate `id`, and a concise reason such as `Use Agentforce Sales as the preferred Sales source for CRM.` Pass the returned `tool_type` directly; it may be `plugin` or `connector`. Do not call `request_plugin_install` in parallel with any other tool. If multiple related plugin candidates tie after saved preference order, configured `preferred_plugins`/`preferred_apps` order, and connector-id matching, ask the user to choose; if no related plugin candidate exists, say so and offer admin/app/manual fallback. If plugin install fails, setup fails, or install succeeds but the plugin-owned skills or tools are not visible yet, record the category as `needs_confirmation`, `deferred`, `deferred_environment_api_limitations`, or `skipped_for_now`; do not mark it active and do not treat the failed setup as a durable decline. Keep plugin-first setup eligible for retry in future workflows when that source category matters. If the user explicitly declines a plugin, suppress that plugin in the current workflow and fall back to the next related plugin candidate, existing connector/app route, or manual setup for that category; save a future `do not use` rule only when the user asks for durable avoidance.

If the user selects or confirms an installed or available plugin, app, or connector, treat it as usable for setup purposes only when the route evidence matches `source-category-runtime.md`, write the resolved route to `connector_confirmation`, and transition without a proof read. If the selected source is missing, use the matching workflow source category and native plugin/app/connector path: load any relevant helper skill from `source-category-config.json`, use tool discovery or the exposed app tools if needed, and run the smallest safe read-only action for that app when a workflow needs the source. If the read triggers auth/setup, let that flow complete before continuing and then write the resolved app/connector route. If no read action or setup route is exposed, keep the category unresolved and ask the user whether to install/connect/authorize it, ask IT/admin to enable it, defer/skip the category, or proceed with manual/exported context. Adapt the source list in the transition to the resolved active/default sources, but when the standard onboarding source set applies, use this copy spine:

```md
Okay, that finishes source setup for now. Sales will use Google Calendar, Gmail, Slack, Google Drive, Notion, and Spreadsheets, and can revisit CRM, meeting notes, enrichment, or contracts when a workflow needs them.

Next, we can set up some simple automations to ensure Sales keeps getting better for you.

1. **Sales Company Research:** Deeply searches across your company context and saves key resources to improve speed and correctness. It runs weekly on Mondays at 9:00 AM local time.
2. **Sales Tips:** Looks at how you've been using Codex and suggests one practical Sales workflow to try next. It runs weekdays at 9:00 AM local time.

Should I set those up? They'll run in a different thread and notify you when they have something to review.
```

- Do not: call installed or active connectors during onboarding merely to prove they work, call `request_plugin_install` without a returned install candidate, call `request_plugin_install` in parallel, persist `available`, `verified`, or automatic `blocked` as durable state, expose raw connector ids, or list speculative enrichment vendors beyond the configured preferred plugins/apps.

## Step 3: Sales Automations

Sales plugin automations use a real approval gate: first introduce the concept and recommended onboarding automations, then set them up only after the user approves setup. This is the second core onboarding setup item after connector setup/confirmation. Sales Daily Meeting Prep is intentionally not part of this initial bundle; offer it later after the user has tried and iterated on Prepare For Meeting.

### Step 3A: Introduce Sales Automations

- ID: `introduce_sales_automations`
- Type: `linear`
- Parent: `sales_automations`
- State field: `automations_intro`
- User-facing goal: Explain recurring Codex Sales tasks before installing them.
- Entry condition: Connected-source confirmation and any source-question handling are complete, skipped, or deferred.
- Stay here when: The Sales automation concept has not been introduced.
- Exit when: The user says `okay`, asks to set up all or some automations, skips, or defers.
- Completion: Record `automations_intro.status = shown` or equivalent once the overview has been shown.
- Next: Step 3B, `setup_sales_automations`.
- Output contract: Read `../plugin-author-config/automation-config.md` before rendering this step and list every default onboarding automation with its configured `Name` and `Frequency`. Never list an automation without its run cadence. Put the automation explanation in primary content and end with the user's setup decision. Use this copy spine:

```md
Next, we can set up some simple automations to ensure Sales keeps getting better for you.

1. **Sales Company Research:** Deeply searches across your company context and saves key resources to improve speed and correctness. It runs weekly on Mondays at 9:00 AM local time.
2. **Sales Tips:** Looks at how you've been using Codex and suggests one practical Sales workflow to try next. It runs weekdays at 9:00 AM local time.

Should I set those up? They'll run in a different thread and notify you when they have something to review.
```

- Do not: install or repair automations in the same response that first introduces automations.

### Step 3B: Set Up Sales Automations

- ID: `setup_sales_automations`
- Type: `linear`
- Parent: `sales_automations`
- State field: `automations.weekly_sales_company_research`, `automations.daily_sales_tips`, and `initial_resource_discovery`
- User-facing goal: Set up recurring Sales help and keep plugin memory fresh without asking the user to manually pre-populate durable preferences.
- Entry condition: The user approved Sales automation setup after the automation introduction.
- Stay here when: Any configured default onboarding automation is not installed or readback is incomplete, the one-time Sales Company Research search has not been kicked off in the pinned thread, research still needs to save high-confidence results or present review-only candidates, or the fallback Sales Tips automation has not been read back after environment/API limitations blocked the full setup.
- Exit when: `weekly_sales_company_research` and `daily_sales_tips` are installed or explicitly declined/skipped/deferred, and the one-time Sales Company Research search in the pinned automation thread has been started, completed, saved high-confidence eligible entries, presented review-only candidates, found no useful additions, or been skipped/deferred. Also exit when environment/API limitations block the full default setup and the fallback Sales Tips automation has been persisted and read back.
- Completion: Record canonical automation id/thread metadata under each matching `automations.<automation_id>` object, record the one-time research kickoff/result under `initial_resource_discovery`, and mark core onboarding complete when connector setup/confirmation is also resolved. Do not send or require a one-time Sales Tips kickoff during onboarding; Sales Tips should run on its normal schedule after setup. In the fallback regular tips path, record `weekly_sales_company_research` and `initial_resource_discovery` as skipped or deferred because of `environment_api_limitations`, record the fallback Sales Tips automation metadata, and mark core onboarding complete when connector setup/confirmation is also resolved.
- Next: Step 4A, `choose_first_hero_prompt`.
- Output contract: Set up the approved automations by following the short checklist in `automation.md`, then report the result and stop at the first workflow chooser. Do not load hero workflow skill files or run a demo workflow until the user picks one.

Pre-tool gate: before the first automation, thread, kickoff, or onboarding-state mutation in this step, open `automation.md` and `../plugin-author-config/automation-config.md`. Identify only the two default onboarding automations, their configured names, frequencies, prompts, target thread titles, model/thinking values, readback requirements, and kickoff requirements. Then execute the `automation.md#Fast Setup Checklist` directly.

Install or repair only `weekly_sales_company_research` and `daily_sales_tips`. Each needs a dedicated pinned thread, heartbeat automation, readback, and state update. Sales Company Research also needs the one-time setup kickoff in its pinned thread. Sales Tips must not be kicked off immediately during onboarding; let its first check-in happen on the normal weekday schedule. Cron automations, automations without a dedicated pinned target thread, automations without readback, or automations whose thread metadata has not been recorded in onboarding state do not satisfy this step. The current onboarding thread must stay unchanged; only the dedicated automation target threads created or reused by `automation.md` may be renamed, pinned, and attached to heartbeat automations. The initial Sales Company Research kickoff belongs in the pinned `Sales Company Research` thread, not in the main onboarding thread. Tell the user the automation threads are visible in the Pinned section when setup succeeds.

If environment or API limitations block the full default automation bundle, use the fallback daily tips path from `automation.md`: skip Sales Company Research, skip the initial context-gathering kickoff, do not ask the user for context links as part of automation setup, and install or repair only the regular `daily_sales_tips` automation using its configured prompt and cadence. Report this as a fallback rather than a full automation setup. Do not say Sales Company Research is ready; say it was skipped or deferred because this environment could not support the full automation setup.

When setup/readback succeeds, use this shape:

```md
Automations are set up and read back cleanly.

- **Sales Company Research**: deeply searches across your company context and saves key resources to improve speed and correctness. It runs weekly on Mondays at 9:00 AM local time. I also kicked off the first research run in the pinned **Sales Company Research** thread.
- **Sales Tips**: looks at how you've been using Codex and gives you one practical Sales workflow to try next. It runs weekdays at 9:00 AM local time, starting with its next scheduled run.

{Optional company research FYI from the rules below.}

Core onboarding is done. Pick a workflow to try first:

1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.
2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.
3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.

```

When the fallback Sales Tips setup succeeds, use this shape:

```md
The full Sales automation setup hit an environment/API limitation, so I used the fallback path and set up Sales Tips instead.

- **Sales Tips**: looks at how you've been using Codex and gives you one practical Sales workflow to try next. It runs weekdays at 9:00 AM local time, starting with its next scheduled run.
- **Skipped for now**: Sales Company Research was not set up in this environment, so I skipped the context-gathering kickoff and did not ask you for source links here.

Core onboarding is done with the fallback automation. Pick a workflow to try first:

1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.
2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.
3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.

```

Do not compress the three hero choices into one inline sentence such as `Pick one to try first: 1 ... 2 ... 3 ...`; each numbered option must be on its own line as `1. **{Name}:** {brief description}`. The numbered choice set is the final action prompt by itself; do not add a `Next Step` heading or a redundant final sentence such as `Pick 1, 2, or 3`.

After automation setup or readback, move directly into the first hero prompt choice. Mention the research thread only when readback confirms saved entries or review-only candidates that need user attention. If state or readback confirms entries were saved, use: `FYI: The pinned thread **"{thread_title}"** saved high-confidence Sales memory resources and listed what changed so you can edit or remove anything later.` If state or readback confirms review-only candidates exist, use: `FYI: The pinned thread **"{thread_title}"** has Sales memory candidates for you to review before saving.` Only say saved entries or proposals exist when state or readback confirms them.

When moving from automation setup to the first hero prompt, render the choice step instead of assuming Prepare For Meeting:

```md
Automations are set up and read back cleanly.

Core onboarding is done. Pick a workflow to try first:

1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.
2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.
3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.

```

Keep automation breadcrumbs, readback cards, and created-card text visually separate from the choice set. Do not put tool-card text in the same paragraph as the chooser. The numbered choice set is the final action prompt; do not add a second CTA.

- Do not: use `multi_agent_v1.spawn_agent`, ad hoc `codex_app.create_thread` calls, ad hoc projectless Codex threads, or repeated background-thread retries for first-run company research outside the dedicated automation target threads created by `automation.md`. Do not pause, delete, unpin, or clean up automations without explicit user approval.

## Step 4: First Hero Prompt

This is the first value demonstration. Onboarding lets the user choose which of the three core hero workflows to try first: `prepare-for-meeting`, `follow-up-after-call`, or `prioritize-accounts`. The onboarding flow owns the choice step and sequencing; each skill's experience guidance owns the skill introduction, starter prompts, anchor rules, and normal next-step candidates.

Hero demos use a repeatable artifact loop: choose a workflow, run it, ask whether to improve the output, optionally take the skill-owned next action after the user accepts, then return to the next demo workflow chooser. Track the active loop with status-only fields such as `hero_workflow.current_skill` and `hero_workflow.current_status` when those fields are available. Do not create growing history arrays or store artifact output in onboarding state. Suggested statuses are `selected`, `running`, `output_delivered`, `reviewing`, `accepted`, `action_offered`, `action_completed`, `skipped`, and `deferred`.

### Step 4A: Choose First Hero Prompt

- ID: `choose_first_hero_prompt`
- Type: `linear`
- Parent: `first_hero_prompt`
- State field: `hero_prompt_choice`; compatibility field: `meeting_prep_prompt`
- User-facing goal: Let the user choose the first Sales workflow they want to see, with three concrete, realistic options.
- Entry condition: Core onboarding is complete: connector setup/confirmation is resolved and Sales automation setup is installed, skipped, declined, or deferred.
- Stay here when: No first hero workflow has been selected, skipped, or deferred.
- Exit when: The user picks `1`, `2`, or `3`, names a specific meeting/call/question, asks for a specific core workflow, skips, or defers the first hero prompt.
- Completion: Record `hero_prompt_choice.status = selected|skipped|deferred`, `hero_prompt_choice.selected_skill`, any `hero_prompt_choice.selected_anchor` supplied by the user, and the three offered skills in `hero_prompt_choice.last_offered_skills`.
- Next: Step 4B, `introduce_selected_first_hero`, only when the user asked to learn about a selected workflow without running it, or Step 4C, `run_selected_first_hero`, when the user picked a numbered option or gave enough intent to try the workflow.
- Output contract: Load `skills/prepare-for-meeting/SKILL.md`, `skills/follow-up-after-call/SKILL.md`, and `skills/prioritize-accounts/SKILL.md` for inline experience guidance. Use each skill's first-run and starter guidance to render a short choice card with exactly three options. Do not invent a fourth option. Each option should include only the display name and one sentence of value. Do not include sample prompts in the chooser; sample prompts belong in skill introductions, the marketplace prompt list, or the index skill. Use this shape:

```md
Now that setup is done, pick the first Sales workflow you want to try:

1. **Prepare For Meeting:** Creates a concise brief for an upcoming customer or high-value sales meeting.
2. **Follow Up After Call:** Turns a recent call or notes into a follow-up package.
3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.
```

- Do not: introduce or run one of the three skills in the same response as the choice card unless the user already supplied an unambiguous workflow and anchor before the choice step was shown. Do not render the choices as an inline sentence such as `Pick one to try first: 1 ... 2 ... 3 ...`. Do not include example prompts in the chooser. Do not add a redundant final sentence telling the user to pick a number when the numbered options are already the action prompt. When the user later picks `1`, `2`, or `3`, treat that reply as consent to run the selected workflow with the recommended default anchor, not as a request for another intro-only turn.

### Step 4B: Introduce Selected First Hero Workflow

- ID: `introduce_selected_first_hero`
- Type: `linear`
- Parent: `first_hero_prompt`
- State field: `hero_prompt_choice.selected_skill` and `skill_experience.<selected_skill>.introduced_at`
- User-facing goal: Explain the selected first hero workflow before asking the user to run it.
- Entry condition: The user selected or clearly implied one of `prepare-for-meeting`, `follow-up-after-call`, or `prioritize-accounts`.
- Stay here when: The selected skill has not been introduced.
- Exit when: The user says `okay`, provides the required anchor, skips, or defers this workflow.
- Completion: Record `skill_experience.<selected_skill>.introduced_at`.
- Next: Step 4C, `run_selected_first_hero`.
- Output contract: Load the selected skill's experience guidance and use its first-run intro, starter prompts, and anchor rules. Introduce the workflow with the New Concept Introduction Pattern: use the skill display heading, start fresh with `This skill...`, include a realistic `@Sales` example, and keep `Next Step` to a compact action prompt using that skill's default anchor behavior. For Prepare For Meeting, ask the user to say `okay` to pick a meeting or name one; make clear that `okay` means the skill will search `calendar` for candidate meetings before asking for manual meeting details. For Follow Up After Call, ask the user to say `okay` so the skill can search `calendar` and `meeting_notes` for recent call candidates, or name one; do not ask for pasted notes/transcripts until those source categories are unavailable or yield no plausible candidates. For Prioritize Accounts, ask the user to say `okay` to prioritize open pipeline by default, or name an account list, territory, ICP, or planning focus.
- Use this step only when the user explicitly asks to learn about the workflow before running it, or when the selected workflow cannot proceed until the user provides one missing anchor. If the user picked `1`, `2`, or `3` from the hero chooser, skip the intro-only turn and proceed to Step 4C.
- Do not: run the selected skill in the same response as its introduction when you are explicitly asking for a missing anchor.

### Step 4C: Run Selected First Hero Demo

- ID: `run_selected_first_hero`
- Type: `linear`
- Parent: `first_hero_prompt`
- State field: `skill_experience.<selected_skill>.first_tried_at`; compatibility field: `meeting_prep_run` when the selected skill is `prepare-for-meeting`
- User-facing goal: Run the selected first hero workflow and show one useful seller-facing output without a separate prompt-confirmation step.
- Entry condition: The selected skill has been introduced and the user approved running it, the user provided the required anchor, or the user picked `1`, `2`, or `3` from the hero chooser and the selected skill can run with its recommended default anchor.
- Stay here when: The workflow is running, blocked on source auth, waiting for the smallest manual fallback needed by the selected skill, or no viable anchor exists.
- Exit when: The output has been delivered or the user skips this workflow.
- Completion: Mark `skill_experience.<selected_skill>.first_tried_at`; compatibility state may also record `meeting_prep_run` completed when the selected skill is `prepare-for-meeting`.
- Next: Step 4D, `review_and_iterate_first_hero`.
- Output contract: When the user picks `1`, `2`, or `3` from the hero chooser, says yes/okay/continue after the selected skill introduction, or names a specific meeting, call, account, or question, apply that skill's Anchor Rules and run the workflow directly. If the selected skill has not been introduced yet, render its compact first-run intro section immediately above the normal workflow output. If the user names a specific anchor, use that anchor. Only ask a follow-up if no good anchor can be found or multiple options are genuinely ambiguous.
- Demo result contract: The first onboarding hero result should begin with one short unheaded transition sentence, then the actual output, then one compact feedback action close. For Prepare For Meeting, use this shape: `Here's your meeting prep, using {brief context about the selected meeting, source coverage, and any assumptions Sales made}.` For Follow Up After Call, briefly say which call was chosen and whether it is internal or external. For Prioritize Accounts, briefly say which account universe or default planning scope was used and any major source assumption. Keep the preface high-level and beginner-friendly for someone who may have no prior knowledge of what an agent does, but do not use a `What Happened`, `Recap`, or other walkthrough heading by default. If the user asks how Sales produced the result, use the on-request walkthrough guidance below.
- Ending:

```md
Is there anything you'd change to make this clearer or more useful, or should we show the next demo workflow choices?
```

- Do not: offer doc creation, calendar attachment, plugin memory setup, automations, or the next workflow in the same response as the first output. Do not render that feedback CTA as an H2/H3 heading.

### Step 4D: Review And Iterate

- ID: `review_and_iterate_first_hero`
- Type: `repeatable`
- Parent: `first_hero_prompt`
- State field: `first_guided_workflow_review`
- User-facing goal: Let the user shape the first output before saving preferences or moving on.
- Entry condition: The first selected hero workflow output has been delivered.
- Stay here when: The user gives feedback, asks for changes, or has not accepted the result.
- Exit when: The user says the output looks good, asks to move on, skips, or the iteration is otherwise accepted.
- Completion: Record review completion and any accepted reusable preference candidate.
- Next: Step 4E, `save_plugin_memory`, if a reusable preference emerged; otherwise Step 4F, `offer_first_hero_action_or_next_demo`.
- Output contract: If the user gives feedback, revise the draft and ask only:

```md
How does that look? Any other changes, or should we show the next demo workflow choices?
```

Do not ask whether the change applies only to this artifact or future outputs inside the iteration loop. Do not ask to save plugin memory on every iteration. Do not save plugin memory on every iteration. The final action close for an iteration must never be a narrow-preference save approval; offer another tweak, the selected skill's natural artifact action when applicable, or the option to show the next demo workflow choices. When the user accepts the revised output or asks to show the next demo workflow choices, inspect whether the accepted change is reusable. If a reusable preference emerged, introduce plugin memory in Step 4E if needed, summarize the preference, and save it by default when it is narrow, low risk, and clearly accepted. Broad, sensitive, ambiguous, or high-risk preferences always require explicit approval. After any required memory handling, offer the selected skill's natural next action in Step 4F before returning to the next demo workflow chooser.

### Step 4E: Introduce Plugin Memory And Save Preference

- ID: `save_plugin_memory`
- Type: `optional`
- Parent: `first_hero_prompt`
- State field: `plugin_memory_intro`, `accepted_preference_memory`
- User-facing goal: Teach plugin memory the first time a reusable preference emerges, then save approved memory.
- Entry condition: The user accepted an iteration and there is a reusable preference candidate, or the user directly asks Sales to remember something during onboarding.
- Stay here when: The first plugin-memory concept has not been introduced or the first save has not been completed/skipped.
- Exit when: The preference is saved, declined, skipped, deferred, or judged not reusable.
- Completion: Record `plugin_memory_intro.status = shown` and `accepted_preference_memory.status = saved|skipped|deferred|not_applicable`.
- Next: Step 4F, `offer_first_hero_action_or_next_demo`.
- Output contract: Use `plugin-memory.md` for the first-time save recap. Introduce memory with the New Concept Introduction Pattern: use `## Plugin Memory` and start fresh with `Plugin memory is how the Sales plugin remembers approved preferences, source-of-truth links, examples, and team conventions for future Sales workflows.` Explain that plugin memory stores durable preferences, trusted resources, source preferences, and team conventions. Mention that memory can include both source-of-truth resources and answer/style preferences, and that Sales Company Research can save high-confidence resource memory by default while surfacing uncertain candidates for review. Summarize the accepted preference, save it by default when it is narrow, low risk, and clearly accepted, then recap the exact saved preference.

```md
## Plugin Memory

Plugin memory is how the Sales plugin remembers approved preferences, source-of-truth links, examples, and team conventions for future Sales workflows. You can ask anytime to save things like "use this Notion page as the source of truth," "prefer inline citations," "always include attendee teams," or "answer exec-facing briefs in this style."

Saved Sales Plugin Memory.

Saved today:
- {accepted preference}
```

After the save recap, move directly into Step 4F with a short transition note. Only require explicit yes for broad, sensitive, ambiguous, high-risk, or externally visible preferences. Do not offer to create a prep doc after saving the preference unless the user explicitly asks for one or it is the skill-owned next action being offered in Step 4F.

### Step 4F: Offer First Hero Action Or Next Demo

- ID: `offer_first_hero_action_or_next_demo`
- Type: `optional`
- Parent: `first_hero_prompt`
- State field: `hero_workflow.current_status` and the selected skill's action metadata when available.
- User-facing goal: After the user accepts the first hero output, offer the most natural next action for that artifact, while keeping the onboarding path moving.
- Entry condition: The first hero output has been accepted, skipped, or the user asked to move on; any required plugin-memory handling is complete or not applicable.
- Stay here when: A skill-owned action such as creating a doc, drafting a Slack post, drafting an email, saving a source route, or creating CRM-ready notes has been offered and the user has not accepted, declined, or skipped it.
- Exit when: The user accepts the action, declines it, skips it, or asks to show the next demo workflow choices.
- Completion: Record `hero_workflow.current_status = action_offered|action_completed|skipped`.
- Next: Step 5A, `choose_next_hero_prompt`.
- Output contract: Load the selected skill's experience guidance and choose one concrete continuation from its normal next-step candidates. The action should be specific to the artifact just produced, not a generic onboarding CTA. Offer exactly one skill-owned action and the option to show the next demo workflow choices. If there is no useful artifact action, skip this step and go straight to Step 5A. Use this shape:

```md
Okay, I've saved that. Now let's move on to the next step.

Want me to {skill-owned action, e.g. create a shareable prep doc or draft the internal Slack recap}, or should I show the next demo workflow choices?
```

- Do not: offer multiple artifact actions at once, offer docs/calendar/Slack/email actions before the user accepts the output, or skip the next demo workflow choices option.

- Do not: ask the user to approve the same narrow preference repeatedly after plugin memory has already been introduced. Calendar attachment is explicit-user-request only.

## Step 5: Other Hero Prompts

After a hero workflow is accepted and any skill-owned artifact action is handled, onboarding returns to a chooser loop until `prepare-for-meeting`, `follow-up-after-call`, and `prioritize-accounts` have each been tried, skipped, or deferred. The chooser should show exactly three numbered options when at least three core options are available. Options may include previously tried hero workflows as repeat actions plus one or more untried workflows, so the user can repeat something useful without losing the onboarding path. Prefer at least one untried core workflow while onboarding is incomplete.

### Step 5A: Choose Next Hero Prompt

- ID: `choose_next_hero_prompt`
- Type: `repeatable`
- Parent: `other_hero_prompts`
- State field: `hero_prompt_choice.last_offered_skills`, `hero_prompt_choice.selected_skill`, `hero_workflow.current_status`, and `skill_experience.<skill>.first_tried_at`
- User-facing goal: Let the user choose the next Sales workflow to try, balancing useful repeats with untried core demo workflows.
- Entry condition: The first hero workflow is accepted, skipped, or deferred, and at least one core hero skill remains untried, or the user asks to keep exploring hero workflows.
- Stay here when: No hero workflow has been selected, skipped, or deferred for the current loop.
- Exit when: The user picks a numbered option, names a specific meeting/call/question, asks for a specific core workflow, skips, or defers the current offer.
- Completion: Record the offered skills in `hero_prompt_choice.last_offered_skills`, record `hero_prompt_choice.selected_skill`, and record any `hero_prompt_choice.selected_anchor` supplied by the user.
- Next: Step 5B, `introduce_selected_remaining_hero`, only when the user asked to learn about a selected workflow without running it, Step 5C, `run_selected_remaining_hero`, when the user picked a numbered option or gave enough intent to try the workflow, or Step 6, `complete_onboarding`, when all core hero skills are tried/skipped/deferred and the user does not want another demo.
- Output contract: Load each core hero skill's experience guidance. Render exactly three choices whenever possible. Choices can include the previous one or two workflows as repeat options, plus at least one untried core workflow while any remain. Preserve the core order `prepare-for-meeting`, `follow-up-after-call`, then `prioritize-accounts` unless the user's last artifact makes a different option clearly more relevant. The model owns the option descriptions by reading the skill experience guidance; preflight should only determine state and ordering. Use this shape:

```md
Pick the next Sales workflow you want to try:

1. **{Core skill display name}:** {One-sentence value description from that skill's experience guidance}
2. **{Core skill display name}:** {One-sentence value description from that skill's experience guidance}
3. **{Core skill display name}:** {One-sentence value description from that skill's experience guidance}
```

- Do not: hardcode Follow Up After Call or Prioritize Accounts as the next demo when multiple options make sense. Do not offer only previously tried workflows while untried core workflows remain. Do not bury the three choices inside a prose sentence. Do not include example prompts in the chooser. Do not add a redundant final sentence telling the user to pick a number when the numbered options are already the action prompt. When the user later picks a numbered option, treat that reply as consent to run the selected workflow with the recommended default anchor, not as a request for another intro-only turn.

### Step 5B: Introduce Selected Remaining Hero Workflow

- ID: `introduce_selected_remaining_hero`
- Type: `linear`
- Parent: `other_hero_prompts`
- State field: `hero_prompt_choice.selected_skill` and `skill_experience.<selected_skill>.introduced_at`
- User-facing goal: Explain the selected remaining hero workflow before asking the user to run it.
- Entry condition: The user selected or clearly implied one of the remaining core hero workflows.
- Stay here when: The selected skill has not been introduced.
- Exit when: The user says `okay`, provides the required anchor, skips, or defers this workflow.
- Completion: Record `skill_experience.<selected_skill>.introduced_at`.
- Next: Step 5C, `run_selected_remaining_hero`.
- Output contract: Load the selected skill's experience guidance and use its first-run intro, starter prompts, and anchor rules. Introduce the workflow with the New Concept Introduction Pattern: use the skill display heading, start fresh with `This skill...`, include a realistic `@Sales` example, and keep `Next Step` to a compact action prompt using that skill's default anchor behavior.
- Use this step only when the user explicitly asks to learn about the workflow before running it, or when the selected workflow cannot proceed until the user provides one missing anchor. If the user picked a numbered option from the hero chooser, skip the intro-only turn and proceed to Step 5C.
- Do not: run the selected skill in the same response as its introduction when you are explicitly asking for a missing anchor.

### Step 5C: Run Selected Remaining Hero Demo

- ID: `run_selected_remaining_hero`
- Type: `linear`
- Parent: `other_hero_prompts`
- State field: `skill_experience.<selected_skill>.first_tried_at`
- User-facing goal: Run the selected remaining hero workflow and show one useful seller-facing output.
- Entry condition: The selected skill has been introduced and the user approved running it, the user provided the required anchor, or the user picked a numbered option from the hero chooser and the selected skill can run with its recommended default anchor.
- Stay here when: The workflow is running, blocked on source auth, waiting for the smallest manual fallback needed by the selected skill, or no viable anchor exists.
- Exit when: The output has been delivered or the user skips this workflow.
- Completion: Mark `skill_experience.<selected_skill>.first_tried_at`; compatibility state may also record `call_followup_intro` or `internal_navigation_intro` where needed by legacy traces.
- Next: Step 5D, `review_and_continue_remaining_hero`.
- Output contract: Apply the selected skill's Anchor Rules and run the workflow directly. If the selected skill has not been introduced yet, render its compact first-run intro section immediately above the normal workflow output. If the selected skill is Follow Up After Call, Search the user's calendar for recent calls through the `calendar` source category and search `meeting_notes` for recent call evidence before asking for manual call evidence. Suggest a real call even if it is not a customer call. Prefer customer/prospect/partner/account calls, and fall back to a large, important-looking meeting as recent as possible. If the selected skill is Prioritize Accounts, prioritize open pipeline by default unless the user named an account list, territory, ICP, or planning focus; if no viable account universe is available, ask for the smallest missing scope. If the selected skill is Prepare For Meeting, pick a strong upcoming meeting from `calendar` unless the user named one. Begin the output with one short unheaded transition sentence, then the actual output, then one compact feedback action close. Do not use a `What Happened`, `Recap`, or other walkthrough heading by default.
- Follow-up CTA: After the output, ask for iteration first and stay in the review loop until the user accepts, asks to show the next demo workflow choices, or skips. Every iteration CTA should offer both paths: change the artifact or show the next demo workflow choices. Once accepted, offer the selected skill's natural next action in Step 5E before returning to Step 5A, or continue to Step 6 when no core demos remain and the user does not want another demo. If the accepted iteration introduced a reusable preference, apply `plugin-memory.md`: narrow, low-risk accepted preferences can be summarized and saved automatically after plugin memory has already been introduced; broad, sensitive, ambiguous, or high-risk preferences require explicit save approval.
- Do not: show placeholder prompts, keep asking for pasted notes when a suitable default can be chosen, or make the next workflow appear without the chooser loop when more than one untried option remains.

### Step 5D: Review And Continue Remaining Hero

- ID: `review_and_continue_remaining_hero`
- Type: `repeatable`
- Parent: `other_hero_prompts`
- State field: `skill_experience.<selected_skill>.first_tried_at` and any accepted preference memory
- User-facing goal: Let the user improve the current hero output, then either save reusable preferences, take the skill-owned artifact action, or show the next demo workflow choices.
- Entry condition: A remaining hero workflow output has been delivered.
- Stay here when: The user gives feedback, asks for changes, or has not accepted the result.
- Exit when: The user says the output looks good, asks to move on, skips, or the iteration is otherwise accepted.
- Completion: Record review completion and any accepted reusable preference candidate; mark the selected skill tried, skipped, or deferred.
- Next: Step 5E, `offer_remaining_hero_action_or_next_demo`.
- Output contract: If the user gives feedback, revise the draft and ask:

```md
How does that look? Any other changes, or should we show the next demo workflow choices?
```

If a reusable preference clearly emerged and plugin memory has already been introduced, summarize and save narrow, low-risk accepted preferences after the user accepts or asks to show the next demo workflow choices. If plugin memory has not been introduced, use Step 4E's plugin memory introduction and save pattern first, then return to this loop. After memory handling, offer the selected skill's natural next action in Step 5E.
- Do not: ask a separate follow-up question after the iteration CTA already offers change or move-on paths.

### Step 5E: Offer Remaining Hero Action Or Next Demo

- ID: `offer_remaining_hero_action_or_next_demo`
- Type: `optional`
- Parent: `other_hero_prompts`
- State field: `hero_workflow.current_status` and the selected skill's action metadata when available.
- User-facing goal: After the user accepts a later hero output, offer the natural skill-owned artifact action without trapping the user before the next demo workflow.
- Entry condition: The current hero output has been accepted, skipped, or the user asked to move on; any required plugin-memory handling is complete or not applicable.
- Stay here when: A skill-owned action has been offered and the user has not accepted, declined, skipped, or asked to move on.
- Exit when: The user accepts the action, declines it, skips it, or asks to show the next demo workflow choices.
- Completion: Record `hero_workflow.current_status = action_offered|action_completed|skipped`.
- Next: Step 5A, `choose_next_hero_prompt`, if the user wants another demo or any core hero skills remain; otherwise Step 6, `complete_onboarding`.
- Output contract: Load the selected skill's experience guidance and choose one concrete continuation from its normal next-step candidates. Offer exactly one skill-owned action and the option to show the next demo workflow choices. If there is no useful artifact action, skip this step and go straight to Step 5A or Step 6.

```md
Want me to {skill-owned action}, or should I show the next demo workflow choices?
```

- Do not: offer multiple artifact actions at once, offer docs/calendar/Slack/email actions before the user accepts the output, or omit the option to show the next demo workflow choices.

## Step 6: Completion

- ID: `complete_onboarding`
- Type: `terminal`
- Parent: none
- State field: `status`
- User-facing goal: Mark onboarding complete only when Sales is meaningfully ready for day-to-day use.
- Entry condition: Steps 1 through 5 are complete, skipped, or deferred where allowed.
- Stay here when: Completion criteria are not satisfied and the user has not explicitly asked to quiet onboarding.
- Exit when: Completion criteria are satisfied, or the user asks to quiet onboarding.
- Completion: Set `status` to `complete` only when the criteria below are satisfied. Set `status` to `quiet` only when the user asks to stop setup guidance.
- Next: none.
- Output contract: Use the `Onboarding Complete` frame from the common message frame. Tell the user they are ready to use Sales productively, name the three completed core workflows, and offer continued guided exploration through the remaining skills. The first recommended post-core skill is `Analyze Account Signals`; end with `Say \`okay\` and I'll introduce Analyze Account Signals, or start a new thread and include \`@Sales\` with any real Sales request.`
- Do not: say the user is fully onboarded while `status` is `active`.

## Completion Criteria

Core onboarding is complete when criteria 1 and 2 are resolved. Full guided onboarding remains `Status: active` until all criteria are satisfied:

1. Connector/source confirmation has covered every source category as active, missing with options explained, skipped, declined, deferred, or not applicable. Do not require active sources to prove readable during onboarding.
2. Sales Company Research and Sales Tips have each been installed, declined, skipped, or deferred, and the one-time company research kickoff in the pinned automation thread has run, started, saved high-confidence eligible memory, presented review-only candidates, found no useful additions, skipped, or deferred. Sales Tips does not need an immediate onboarding kickoff; its first check-in should run on the normal weekday schedule. This criterion is also resolved when environment/API limitations block the full default setup and the fallback Sales Tips automation has been persisted and read back while Sales Company Research and `initial_resource_discovery` are recorded as skipped or deferred for `environment_api_limitations`.
3. `prepare-for-meeting` has been tried, skipped, or deferred, and review/iteration/plugin-memory handling is resolved.
4. `follow-up-after-call` and `prioritize-accounts` have each been tried, skipped, or deferred.

Source behavior is configured during setup and consumed at workflow time: Sales reads the configured `connector_confirmation` route, tries that source when a workflow needs it, continues when it works, and asks for connect/auth, skip, or manual fallback when setup or runtime reveals a gap.

## Continued Guided Exploration

After core onboarding is complete, users can keep exploring by saying `okay`, `continue`, or naming another Sales workflow. Use each skill's experience guidance for intro/starter logic and continue in this order unless the user chooses a different workflow. When offering continued exploration, remind the user that they can also start a new thread and include `@Sales` with any real Sales request.

When introducing `Analyze Account Signals` during continued guided exploration, do not make skip the visible default. Use the skill's Anchor Rules and end with `Say \`okay\` and I'll pick a suitable account to analyze, or name an account, owner portfolio, or watchlist.` If no suitable account is visible after the user says `okay`, ask one concise clarification.

1. `analyze-account-signals`
2. `plan-deal-strategy`
3. `review-forecast`
4. `build-competitive-brief`
5. `find-customer-quotes`
6. `build-business-case`
7. `enrich-company-and-contact-data`
8. `find-key-internal-sources`
9. `get-rep-call-feedback`
10. `review-rep-call-trends`
11. `suggest-sales-next-step`

## CTA Arbitration

Invariant: exactly one final visible CTA per response.

- Ordinary skill run: the skill renders its normal next step from its experience guidance and its own workflow policy.
- Guided onboarding run: onboarding renders the final CTA; the skill suppresses its final CTA and returns next-step candidates.
- Onboarding review loop: final CTA is review, accept, continue, save, skip, or defer, not a skill continuation.
- Helper/provider skill: no intro or CTA unless explicitly requested.
- Ordinary skill run with an onboarding reminder obligation: merge the reminder into the single final action close or use the onboarding setup CTA as the sole final CTA. Do not render a standalone onboarding reminder that asks the user to continue onboarding and then render a separate skill-owned CTA.
- Automation setup/readback: keep automation cards and breadcrumbs visually separate from the action close.

## Workflow Walkthrough On Request

Do not render `What Happened`, `Recap`, or another walkthrough heading by default in onboarding demo outputs, ordinary direct skill runs, post-completion guided exploration, automation readbacks, follow-up turns, or source-gap replies. For the first three onboarding demo outputs, use only a short unheaded transition sentence before the artifact body. If the user explicitly asks what happened, asks how Sales produced the result, or says yes to a walkthrough offer, then explain the observable steps.

When a walkthrough is requested, explain the observable tool/app calls, retrievals, source gaps, and artifact assembly at a beginner-friendly level without revealing hidden reasoning. Keep it grounded in visible activity: sources attempted, what worked, what did not, useful facts found, and how those facts shaped the artifact.

End the walkthrough by offering one valuable next action: continue to the next uncompleted guided workflow, fix the highest-value missing source, save a useful preference discovered during the run, or take a practical seller action from the artifact. Preserve the one-final-CTA rule.

## Ordinary Workflow Onboarding CTA

Use this template only after answering an ordinary Sales workflow request while onboarding is missing or has not started. Do not use it for direct onboarding/status/setup responses, and do not use it when `onboarding-state.json` says onboarding is already active.

Do not use this template when the immediate workflow is blocked on a required clarification. Clarification questions always become the single final action close and suppress onboarding CTAs for that response.

```md
## Sales Setup Required

This is required before Sales can reliably use your connected sources and source and use your authoritative company context. It also gives you a useful overview of the plugin's key functionality.

Reply `start` to continue.
```

## Active Onboarding Reminder

Use this only after an ordinary Sales workflow when onboarding is already active and a reminder would be useful. Do not use the `## Sales Setup Required` start CTA, do not ask whether to start onboarding, and do not compete with the skill's final action close. Keep the note short and non-final, for example:

```md
Sales onboarding is still in progress; when you want to resume it, say `continue onboarding` in this thread.
```

## Core Onboarding Reminder

Use this after an ordinary Sales workflow when onboarding is already active but core onboarding is not complete. Do not use the `## Sales Setup Required` start CTA, and do not ask whether to start onboarding. The note should direct the user back to the next unresolved core setup item before more non-urgent Sales workflows:

```md
Sales core onboarding still needs {next_core_action}. Say `continue onboarding` in this thread and I'll finish that setup before we keep going with other Sales workflows.
```

When the primary workflow has its own final action close, do not render this reminder as a standalone paragraph. Fold it into the final action close as the move-on path, for example: `{skill continuation}. Otherwise say `continue onboarding` and I'll finish {next_core_action}.`

## Context Gap Note

Use this only after an ordinary Sales workflow when missing saved context or a failed workflow-time source materially reduced confidence, completeness, or ability to act.

```md
Sales would get sharper here with a little more saved context, such as the team hub, source-of-truth account docs, CRM update rules, approval trackers, or preferred output format.
```

## Environment Conflict Audit

After the first orientation message, direct onboarding may include a lightweight environment conflict audit so the user can tell whether Sales will be the sales workflow that actually triggers. Do not run this audit before sending the first orientation message when no Sales state exists yet. The audit is about routing and user experience, not connector availability.

Flag a plugin or skill as a conflict candidate when it broadly overlaps with one or more Sales workflows and could plausibly capture the same natural-language request. Do not flag connector providers or source helpers as conflicts merely because Sales uses those sources. Do not write clean audit results or conflict lists into onboarding state. If conflicts materially affect the user's setup, explain them in the current onboarding response and save only an explicit user preference or routing choice to `user-context.md` when the user asks Sales to remember it.

## Boundaries

- Do not put private or user-specific preferences into bundled `SKILL.md` files when they can live in `user-context.md`.
- Prefer saved `user-context.md` instructions over bundled Sales plugin or skill instructions for Sales plugin-scoped context represented by `../plugin-author-config/user-context-config.md`, user-provided preferences, examples, source pointers, and onboarding preferences.
- Do not use user-context onboarding to change routing, safety, validation, install behavior, or tool-use policy. Those changes belong in editable plugin source.
- If the state directory cannot be written, return the preference as a suggested snippet for `user-context.md` and say the write failed.
