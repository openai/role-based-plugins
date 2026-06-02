# Data Analytics Onboarding Flow

Use this reference when `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` is missing or unreadable, when the user asks what Data Analytics can do, when the user asks to set up or customize Data Analytics, or when `onboarding-state.json` says onboarding is active and a nudge is due.

Onboarding is a mostly linear, nested step-card playbook. It is not a formal graph. Each step owns setup copy, output contract, action close, completion behavior, skip or defer behavior, and any loop or optional branch. Every onboarding message should handle one major user-visible step at most, mirror the overall progress list when the UI is available, and end with one clear action or question.

Store durable source-routing preferences explicitly selected for future use plus semantic-layer pointers in `user-context.md`. Store only operational onboarding progress, including connector-confirmation labels, skill experience progress, semantic-layer setup and refresh state, automation setup, and quiet or complete state, in `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json`. Keep onboarding state compact: do not put raw `list_available_plugins_to_install` results, full connector inventories, connector descriptions, copied source inventories, source URLs, source data, polling results, research result bodies, artifact text, source-gap notes, or analysis output in onboarding state; keep that content in `user-context.md`, the generated semantic-layer skill, the pinned polling thread, the current workflow artifact, or the source system. Record compact route metadata, counts, ids, statuses, timestamps, and durable pointers instead. Do not create, read, or update durable connector-readiness proof as part of onboarding. Data Analytics workflows use plugins, apps, or connectors when the workflow needs the source.

The first direct onboarding response is a response-first fast path. When the user asks to onboard, set up, or learn what Data Analytics can do and no Data Analytics state files exist yet, render Step 1 immediately. Do not run `../scripts/init_user_context_state.py`, write scaffold files, inspect connectors, audit conflicts, create semantic layers, create threads, install automations, start source discovery, or run workflows before that first message. After the user approves the next visible setup step, or whenever the user supplies context that should be saved, use `../scripts/init_user_context_state.py` when local shell access is available. In sandboxed local-shell environments, request elevated execution by default because it writes to `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`.

Related sources of truth:

- Use `semantic-layer/setup.md`, `semantic-layer/source-intake.md`, and `semantic-layer/connector-playbook.md` for semantic-layer intake, source inventory, evidence crawl, create/refresh/inspect/repair behavior, connector-specific recovery, and durable pointer writes.
- Use `../scripts/init_user_context_state.py` to create missing first-run state files only after the first orientation message has been shown and the user approves the next setup step, or immediately when the user provides context that should be saved.
- Use `../plugin-author-config/user-context-config.md` as the source for the minimal source-routing and semantic-layer registry scaffold.
- Use `../plugin-author-config/source-category-config.json` for static source category ids, labels, preferred plugin routes, and helper skills. Use `source-category-runtime.md` for plugin-first source setup, onboarding connector-confirmation labels, workflow-time source attempts, ON_USE auth behavior, fallback rules, and durable source-preference storage.
- Use each user-facing skill's inline experience guidance for first-run intro copy, starter prompts, anchor rules, normal next-step candidates, and onboarding-yield behavior.
- Use `../plugin-author-config/automation-config.md` for the author-owned default automation catalog. Use `automation.md` for runtime setup mechanics: installing the configured default during onboarding, deriving the target thread title from the automation name, creating the target thread, pinning and renaming it, kicking off Semantic Layer Weekly Source Polling in the pinned thread, readback checks, duplicate cleanup, and failure reporting. Use `semantic-layer/weekly-polling-automation.md` for the scheduled polling workflow contract.
- Use `onboarding-examples.md` for illustrative audit traces only.

## Skill Experience Delegation

Onboarding chooses which user-facing skill to try next, but the focused skill owns how it introduces itself and what a good first try looks like.

Before introducing or running a user-facing skill during onboarding, load that skill's inline experience guidance from `SKILL.md`. Use that guidance for:

- first-run intro copy;
- starter prompts and realistic `@data-analytics` examples;
- anchor rules and sensible defaults;
- normal next-step candidates;
- onboarding-yield behavior.

Do not duplicate skill-specific intro copy, starter prompt variants, anchor rules, or normal next-step behavior in this file. If the focused skill has enough user intent to run and has not been introduced yet, it should render the compact first-run intro section from its skill-owned guidance before normal workflow output. If onboarding or another parent workflow owns the final CTA, the skill should suppress its own final CTA and return status plus next-step candidates for that parent workflow to arbitrate.

## Common Onboarding Message Frame

Every onboarding message that is not complete must include primary content for the current step, then leave the user with one clear way to move forward. A natural final sentence, a compact action frame, or a self-contained numbered choice set can satisfy this requirement. Use the reference copy as the preferred onboarding voice and structure: preserve its core claims, ordering, and plain-language tone wherever the current setup state allows. Adapt only to reflect real source availability, skipped/deferred setup, installed plugins/connectors, or the user's current onboarding step. Do not revert to the older rigid `Next Step` cadence when a natural action question or selectable choice set is clearer, and do not introduce extra setup concepts not present in the reference copy.

Use this compact action frame when the step has multiple questions, a durable approval gate, or a complex choice that needs an explicit label:

```md
**Next Step**
{One clear action or question the user can answer now.}
```

`Next Step` is the action prompt, not the explainer. Put step results, workflow introductions, setup explanations, and teaching content in the primary content immediately before the frame, then keep `Next Step` short and decision-shaped. For simple one-question steps, a natural final sentence such as `Ready to set that up?` or `Should I set those up?` is preferred. For chooser steps where each numbered option is concrete and selectable, the list itself is the action prompt; do not add a redundant `Next Step` heading or final sentence such as `Pick 1 or 2`. Do not let the whole onboarding message be only a next-step frame.

When the current step has open questions, make resolving those questions its own visible onboarding step before introducing the next workflow. Include the questions in `Next Step` instead of leaving them only in the preceding step summary. Use a compact numbered list when there is more than one question. If the questions can be handled by sensible defaults, include the default escape hatch inside the relevant numbered item, including which defaults will be used and which optional gaps will be skipped, deferred, or revisited later. Do not add a separate summary prompt after the numbered list when the list already contains the questions and default path. Do not combine meaningful source, preference, admin, approval, or skip/defer decisions with a first-time workflow introduction.

When introducing a workflow, skill, or new onboarding concept for the first time in the current onboarding flow, introduce it in the primary content before the action close. For skills, use that skill's experience guidance. For onboarding concepts such as semantic layers or automations, briefly explain what it does, what inputs or state it can use, what output or result the user should expect, the recommended default action, and the option for the user to skip or provide a specific anchor instead. Keep the action close to the small action the user can take. Use the New Concept Introduction Pattern below whenever the current response enters a new concept.

When showing user-facing sample prompts during onboarding, teach the preferred invocation pattern: start with `@data-analytics`, then state the analytics job and the real anchor in natural language. Sample prompts should be realistic and analyst-shaped, such as `@data-analytics diagnose why subscription ARR moved last week.`, not placeholder-only prompts. If the prompt is meant to run against the user's actual context, fill it with a real metric, product area, dashboard, table, semantic layer, or decision question before showing it; otherwise label it as an example for later use.

Do not create tiny transition turns whose only purpose is asking whether to introduce the next onboarding item. If the current step has completed and the next item is an intro-only step, add a short transition note such as `Okay, I've saved that. Now let's move on to the next step.` or `Great, moving on.`, then render the next concept introduction or next hero prompt card in the same response with one final action close. Preserve real approval gates: data semantic-layer setup should introduce the concept before asking for anything the user would point a new analyst to, with explicit skip or defer language; Data Analytics automations should use a short transition sentence and ask whether to set up weekly polling without a separate `## Data Analytics Automations` heading; generated skill writes, connector installs, recurring automation creation, external system writes, and other approval-gated actions still need their own approval when the step requires it.

After the first hero prompt has run, been skipped, or been deferred, onboarding should continue to completion. Only when the user explicitly asks `show more prompts`, `next prompt`, `next demo`, `next guided workflow`, or similar should Data Analytics offer more prompt ideas instead of auto-running another workflow. Preserve any workflow-owned artifact or source-gap notes, clear the active selected skill before another choice, and enter `offer_extra_hero_prompts` only for that explicit request. Do not run another hero workflow until the user picks an offered prompt, names a workflow, or gives a specific metric, product area, dashboard, table, semantic layer, or decision anchor.

Exactly one final visible CTA or self-contained choice set should appear in the response. FYIs, readbacks, and automation breadcrumbs should be separate from the final action close and should not compete with it.

When onboarding is done, use this terminal frame:

```md
**Onboarding Complete**
You're set up to use Data Analytics with configured source routes or explicit fallbacks, a resolved data semantic layer choice, optional weekly polling if you enabled it, and a first analysis workflow ready to reuse.

You can start a new thread with any real analytics question, or keep going with another suggested prompt when useful.

**Next Step**
Say `okay` and I'll show another Data Analytics prompt, or start a new thread and include `@data-analytics` with any real analytics request.
```

Do not render `Next Step` as an H1/H2/H3 heading. Keep implementation details out of user-facing onboarding. Do not narrate file structures, cache paths, state paths, context-file mechanics, internal probe names, provider taxonomy, or raw state names unless the user explicitly asks for implementation details.

## New Concept Introduction Pattern

Use this pattern when the response enters a new skill or concept. It may appear after a short recap of the just-completed step when the only alternative would be a low-value `Want me to introduce...` transition. Keep exactly one final visible action close for the current actionable decision. Use a `**Next Step**` label only when the decision needs the label.

```md
## {Concept Name}

{Concept explanation.}

Example prompt: `@data-analytics {realistic prompt with a real or clearly illustrative anchor}.`

**Next Step**
{One compact action, approval question, or anchor request.}
```

For semantic layers, use `## Semantic Layer` and start the body with `A semantic layer is how Data Analytics keeps approved metric definitions, source-of-truth pointers, joins, caveats, and validation steps reusable for future analysis workflows.`

For Data Analytics automations, do not render a separate `## Data Analytics Automations` heading. Start with a simple explanation that these are recurring Codex tasks for semantic-layer source polling.

For skill introductions, use the skill display name as the heading, such as `## Metric Diagnostics`, not the machine skill id. Because the heading already names the skill, the body should start with `This skill...`, not `{Skill Name} is a skill in the Data Analytics plugin...`. Do not render user-facing CTAs with code-styled skill names such as `metric-diagnostics`; say `Metric Diagnostics`.

User-facing bullets should be polished sentence fragments or full sentences. Do not start bullets with lowercase words unless they are grammatically continuing an introductory sentence. Prefer capitalized fragments such as `A validated metric definition`, `Key driver context`, and `A decision-ready recommendation when relevant`. Bullets may omit periods when they are fragments; full-sentence bullets should use periods consistently.

## Progress Checklist Contract

Mirror this user-visible roadmap into the built-in thread task list when available:

1. Orientation
2. Check main analytics sources
3. Set Up Data Context
4. Hero prompt

`Semantic layer refresh setup` is a substep of data semantic layer setup, not a separate top-level onboarding milestone. Keep it in onboarding state because it matters operationally when a stable layer exists, but do not make the top-level experience feel like a fourth major setup track before the user sees value.

Before every onboarding response, refresh the checklist from current onboarding state after applying actions from that turn. If the response completed, skipped, or deferred a step, mark that step accordingly and mark the next unresolved visible step as `in_progress`.

Treat core onboarding as complete after source setup confirmation is resolved and the data semantic layer step is either set up from user-provided inputs, explicitly skipped, deferred, unavailable, or blocked with one concrete path. Source setup confirmation is not complete while `structured_data`, `team_communication`, or `company_docs` has an installable or otherwise actionable route question that the user has not explicitly resolved. If no stable semantic-layer target exists because the user skipped, deferred, or is blocked, do not require the refresh substep. Ordinary Data Analytics work should still answer best effort while onboarding is missing or active, then append the single preflight-provided setup obligation unless the response is blocked on a required clarification or the user asked for quiet behavior.

Treat a plain `yes`, `okay`, `continue`, `ready`, or similar reply after a next-step CTA as approval to perform the current visible next step unless the user names a different action. Treat `skip`, `skip for now`, `not now`, or similar as approval to mark the current visible step skipped or deferred when that step allows it, then continue.

## Step 1: Orientation

- ID: `start_data_analytics_onboarding`
- Type: `linear`
- Parent: none
- State field: `orientation`
- User-facing goal: Explain what Data Analytics helps with and move quickly to source setup confirmation.
- Entry condition: Direct onboarding trigger, first-run setup, "what can Data Analytics do?", or resumed onboarding with orientation missing.
- Stay here when: No state files exist and the first orientation has just been rendered.
- Exit when: The user approves the next setup step or state already records that orientation was shown.
- Completion: Record orientation as shown only after state exists.
- Next: Step 2, `confirm_analytics_sources`.
- Output contract: Preserve the meaning of this copy; light grammar cleanup is allowed. Do not add connector results, scaffolding, semantic-layer setup, automation setup, or hero workflow output to this first message.

```md
The Data Analytics plugin is set up to help Codex do higher-quality analytics work. Use it when you want to turn product or business data into insights, clear recommendations, decision-ready artifacts, and dashboards.

It can help you:

- Analyze product and business performance and create executive-ready insight reports.
- Diagnose metric movements and identify likely root causes.
- Create KPI reports such as WBRs, MBRs, scorecards, and operating reviews.
- Design KPIs, success measures, guardrails, and targets.
- Build dashboards with strong metrics, clear layout, and source notes.
- Analyze experiment or launch results and summarize the decision implications.
- Size market, product, customer, or segment opportunities.

It works best once it knows which analytical sources to use and which product areas, metrics, dashboards, tables, and recurring questions matter to you, so we'll do a short setup pass and then run a real analysis prompt.

Here's what we'll do:
1. Confirm the main analytics sources Codex can try when a workflow needs them
2. Set up data context from useful sources you provide, or skip it for now
3. Try one high-value analysis prompt using your real context

Data Analytics will automatically help when your request clearly matches an analytics workflow, and you can always mention it explicitly with a real question such as `@Data Analytics diagnose why subscription ARR moved last week.`

---

**Next Step**
Reply `continue` and I'll check which analytics sources Codex can use, only asking where you need to choose, connect, or use a fallback.
```

- Do not: initialize state, inspect connectors, create semantic layers, create automations, or run hero prompts before this first message.

## Step 2: Check Main Analytics Sources

- ID: `confirm_analytics_sources`
- Type: `linear`
- Parent: none
- State field: `connector_confirmation`
- User-facing goal: Give the user confidence about which analytics sources look usable and ask only for help where a source is ambiguous, missing, or needs IT or admin enablement.
- Entry condition: Orientation is complete or the user explicitly asks to continue setup.
- Stay here when: Source classification has not run or the active/missing source result has not been shown.
- Exit when: Every core source category is recorded as `active` or has a user-explicit `declined`, `deferred`, `skipped`, `unavailable`, or `not_applicable` fallback, any offered optional category is recorded as `active`, `missing`, `declined`, `deferred`, `skipped`, `unavailable`, or `not_applicable`, or the user explicitly chooses to continue with recorded known gaps.
- Completion: Store onboarding confirmation labels and resolved source routes in `onboarding-state.json`; do not write connector readiness to `user-context.md`.
- Next: Step 2A, `resolve_source_questions`, when any source category needs user input; otherwise Step 3A, `introduce_semantic_layer_setup`.
- Output contract: Return a concise standalone active/missing source result with one setup-ready heading line, bold bullets for available sources, one sentence naming remaining source gaps, and one clear setup question. Active connector or app sources are informational fallback routes, not winners, when a related plugin is installed or installable. This setup step, not preflight, inspects the environment, calls `functions.list_available_plugins_to_install` once for the setup pass, and writes resolved routes for each source category. Ask only when there are multiple mutually exclusive installed source tools, an installable related plugin needs approval, no source was found, or the category needs IT or admin help. Do not ask for a docs preference merely because both Google Drive and Notion are available; record both routes and let workflows use both. For missing sources and connector-covered sources, prefer plugin setup, then direct app or connector setup, then manual exports or pasted context. Core categories are not optional setup extras: if `structured_data`, `team_communication`, or `company_docs` lacks an active or manual route, make it part of the Step 2 question, keep installable core candidates as `needs_confirmation`, and do not introduce semantic-layer setup until the user installs a route or explicitly says to defer, skip, decline, mark unavailable, mark not applicable, or continue with a recorded known gap. Do not introduce semantic-layer setup in the same response when source questions remain. When core source questions remain and company docs are already covered, use this style:

```md
After some searching, it looks like you're already set up with Google Drive, Notion, and Spreadsheets.

Before Data Analytics sets up data context, I need your choice for these key sources:

1. **Data warehouse** lets Data Analytics query structured data directly for current, source-backed answers.
   Options: Databricks, BigQuery, Snowflake.
2. **Team communication** lets Data Analytics search recent discussions for context, decisions, and owners.
   Options: Slack, Teams.

Company docs look covered through Google Drive and Notion.

Optional sources can wait until a workflow or semantic-layer plan needs them:

3. **Dashboards and BI, if you use them** lets Data Analytics inspect dashboards and BI reports for metric definitions, filters, and saved views.
   Options: ThoughtSpot, Omni Analytics.
4. **Behavior signals, if you use them** adds product-usage evidence for funnel, retention, adoption, and experiment analysis.
   Options: Amplitude, Mixpanel.
5. **Notebook lab, if you use it** lets Data Analytics inspect prior analyses, reuse notebook logic, and continue exploratory work.
   Options: Hex, Deepnote.

You'll be prompted to install and authenticate plugins or connectors for whichever you select.

**Next Step**
Reply with the sources you want to connect now, or say `defer for now` to continue with manual or pasted context.
```

Do not render separate `Active sources`, `Sources I need your help with`, or `Missing sources and practical impact` headings unless the source result is too unusual for the concise shape.
- Reference copy: Active and appropriate sources are FYI only. Do not preflight-read installed or active sources just to prove they work. For each category, compare `saved_source_preferences` and `preferred` from preflight, configured `preferred_plugins` from `source-category-config.json`, legacy `preferred_apps` only when present, `.app.json` ids for configured preferred providers, the session `Available plugins` and `Available skills` blocks, and the single `functions.list_available_plugins_to_install` result for the setup pass. If one or more related plugins are installed with visible skill or tool surfaces, write them to `connector_confirmation` as active routes under `routes[]` with `source_kind: plugin`, `skill_surface`, plugin details, and evidence fields. Related means the plugin or provider itself matches the configured preferred plugin route, or its declared connector id matches a configured preferred provider id from `.app.json`; cross-source search surfaces are not active source routes for another category. Do not classify Notion, Google Drive, or a broad internal search tool as active team communication solely because it indexes Slack or Teams. If no related plugin is active but a related plugin is installable, highlight it as the recommended setup action even when an app or connector route is already active; explain that Data Analytics should prefer the plugin because it can add dedicated Data Analytics workflow support, and keep the existing app or connector route as fallback if the user defers or install visibility is pending. Rank plugin candidates by saved preferences first, then configured `preferred_plugins`, then legacy `preferred_apps` when present, then `.app.json` connector-id intersections. If no related plugin is installed or installable and exactly one plausible app or connector is installed or available, write it as active with `source_kind`, `skill_surface`, and route details when available, then let the workflow's first real read handle auth, query, or schema issues. If multiple plausible source tools are complementary rather than mutually exclusive, such as Drive and Notion for docs, write multiple active routes instead of asking the user to pick a winner. If multiple plausible source tools are mutually exclusive for the same category, ask the user which one to prefer and write the selected route only after resolving its plugin, app, connector, or manual route. Missing sources should explain practical workflow impact and list specific IT or admin options. Be prescriptive about pilot setup: warehouse access unlocks live metric definitions, table shape, query logic, and current-source validation; dashboards and BI let Data Analytics inspect dashboards and BI reports for metric definitions, filters, and saved views; behavior signals unlock product usage, funnels, retention, adoption, and experiment evidence; notebook labs let Data Analytics inspect prior analyses, reuse notebook logic, and continue exploratory work; Slack or Teams unlock recent discussion, owners, caveats, and decision context; Drive, SharePoint, or Notion unlock source-of-truth docs, specs, dashboard notes, and governance context; GitHub unlocks model, query, schema, and semantic-layer ownership.
- Next-step copy: If one or more source categories need user input, make the `Next Step` only about resolving those questions. When the Step 2 source result includes explanatory optional sources before a separate core-source reply line, render `**Next Step**` immediately before that final reply line so the action close stays visually distinct. If no source questions need input, move directly into Step 3A with a short transition note and the semantic-layer introduction; do not ask whether to introduce it.

### Step 2A: Resolve Source Questions

- ID: `resolve_source_questions`
- Type: `optional`
- Parent: `confirm_analytics_sources`
- State field: `connector_confirmation`; optional user preference saves go to `user-context.md`.
- User-facing goal: Let the user answer or skip meaningful source choices before Data Analytics introduces semantic-layer setup.
- Entry condition: Active/missing source confirmation found multiple plausible apps, no app, or IT or admin source gaps that need a user choice, preference, or acknowledgement.
- Stay here when: The user has not answered, skipped, deferred, or accepted defaults for the source questions.
- Exit when: The user provides the preference or source info, says to continue with defaults, skips, or defers the source questions.
- Completion: Save any clear low-risk source preference to `user-context.md`; record skipped, deferred, default, active, or unavailable handling in `onboarding-state.json`. A user-selected source may be recorded as `active` when its plugin, app, or connector is installed, available, surfaced, or active in the current environment with enough evidence for the route kind. The state entry must include resolved route fields such as `source_kind`, `skill_surface`, and plugin, app, connector, or manual details when available. For a core source fallback, record the user's explicit choice with `resolution: user_deferred`, `resolution: user_skipped`, `resolution: user_declined`, `resolution: user_marked_unavailable`, `resolution: user_confirmed_not_applicable`, or `resolution: user_continued_with_known_gap`; do not let an automatic or stale core fallback make source setup look complete. Do not create durable connector-readiness proof.
- Next: Step 3A, `introduce_semantic_layer_setup`.
- Output contract: Keep primary content focused on the source result and practical impact. Put only the unresolved source questions and skip or defer escape hatch in the action close. Do not ask for a docs preference when multiple docs routes can be used together:

```md
Please select the sources you want to set up now:

1. **Data warehouse** lets Data Analytics query structured data directly for current, source-backed answers.
   Options: Databricks, BigQuery, Snowflake.
2. **Team communication** lets Data Analytics search recent discussions for context, decisions, and owners.
   Options: Slack, Teams.

Company docs look covered through Google Drive and Notion.

Optional sources you can add now if useful:

3. **Dashboards and BI, if you use them** lets Data Analytics inspect dashboards and BI reports for metric definitions, filters, and saved views.
   Options: ThoughtSpot, Omni Analytics.
4. **Behavior signals, if you use them** adds product-usage evidence for funnel, retention, adoption, and experiment analysis.
   Options: Amplitude, Mixpanel.
5. **Notebook lab, if you use it** lets Data Analytics inspect prior analyses, reuse notebook logic, and continue exploratory work.
   Options: Hex, Deepnote.

You can defer warehouse or team communication access, but say it explicitly so Data Analytics records the known gap before moving on. Optional sources can wait; Data Analytics will ask again later only when a workflow would materially benefit from one of them.
```

After the user answers, install confirmed plugin or connector candidates one at a time, save any clear source preferences or accepted skips, then move directly into the semantic-layer introduction. Do not ask whether to introduce it. For routine source setup preferences in onboarding, do not render a saved-context recap or `Saved today` list; use only the short transition into Step 3A below, then render Step 3A in the same response:

If the user confirms an installable plugin or connector candidate returned by `functions.list_available_plugins_to_install`, call `functions.request_plugin_install` with `action_type: "install"`, the returned candidate `tool_type`, the returned candidate `id`, and a concise reason such as `Use Databricks as the preferred Data Analytics source for data warehouse.` Pass the returned `tool_type` directly; it may be `plugin` or `connector`. Do not call `request_plugin_install` in parallel with any other tool. If multiple related plugin candidates tie after saved preference order, configured `preferred_plugins` order, legacy `preferred_apps` order when present, and connector-id matching, ask the user to choose; if no related plugin candidate exists, say so and offer admin, app, connector, or manual fallback. If plugin install fails, setup fails, or install succeeds but the plugin-owned skills or tools are not visible yet, record the category as `needs_confirmation`, `deferred`, `deferred_environment_api_limitations`, or `skipped_for_now`; do not mark it active and do not treat the failed setup as a durable decline. Keep plugin-first setup eligible for retry in future workflows when that source category matters. If the user explicitly declines a plugin, suppress that plugin in the current workflow and fall back to the next related plugin candidate, existing connector or app route, or manual setup for that category; save a future `do not use` rule only when the user asks for durable avoidance.

If the user selects or confirms an installed or available plugin, app, or connector, treat it as usable for setup purposes only when the route evidence matches `source-category-runtime.md`, write the resolved route to `connector_confirmation`, and transition without a proof read. If the selected source is missing, use the matching source category and native plugin, app, or connector path: load any relevant helper skill from `source-category-config.json`, use tool discovery or exposed app tools if needed, and run the smallest safe read-only action only when a workflow needs the source. If the workflow-time read triggers auth or setup, let that flow complete before continuing and then write the resolved app or connector route. If no read action or setup route is exposed, keep the category unresolved and ask the user whether to install, connect, or authorize it, ask IT or admin to enable it, defer or skip the category, or proceed with manual or exported context. Adapt the source list in the transition to the resolved active or default sources, but when the standard onboarding source set applies, use this copy spine:

```md
Okay, that finishes source setup for now. Data Analytics can start with the active routes above, and I recorded any core source gaps you explicitly deferred. It can revisit warehouse, team communication, company docs, dashboard, behavior-signal, or notebook gaps when a workflow needs them.

Before we run the first analysis, let's set up data context from whatever useful context or sources you have.
```

- Do not: call installed or active connectors during onboarding merely to prove they work, call `request_plugin_install` without a returned install candidate, call `request_plugin_install` in parallel, persist `available`, `verified`, or automatic `blocked` as durable state, expose raw connector ids, or list speculative providers beyond the configured preferred plugins or apps.

## Step 3: Reusable Data Context Setup

Reusable data context setup is the second major onboarding milestone. Encourage the user to provide useful context or sources, but do not create a semantic layer unless the user provides or approves the inputs. The refresh automation offer exists, but it should feel like a small follow-up after the layer is real, not a separate onboarding detour before the user sees value.

### Step 3A: Introduce Reusable Data Context Setup

- ID: `introduce_semantic_layer_setup`
- Type: `linear`
- Parent: `semantic_layer_setup`
- State field: `semantic_layer_setup`
- User-facing goal: Explain what a data semantic layer is and ask for any useful context or source the user already has.
- Entry condition: Core source setup confirmation is resolved, or the user explicitly chose a recorded skipped, deferred, declined, unavailable, not-applicable, or continue-with-known-gap path for every unresolved core source.
- Stay here when: The data semantic layer concept has not been introduced and the user has not provided enough context or sources to create, plan, skip, defer, or block the layer.
- Exit when: The user provides useful context or sources that can be organized into a layer, asks for intake-only planning, skips, defers, or is blocked on one concrete missing input.
- Completion: Record the inferred or selected area, supplied starting context, or skip/defer/block resolution in `onboarding-state.json`.
- Next: Step 3B, `create_or_plan_semantic_layer`.
- Output contract: Explain that a data semantic layer helps Codex reuse metric definitions, tables, filters, and source-of-truth context for future analysis. Ask for anything the user would point a new analyst to, make clear Codex will organize the inputs, and include the explicit skip path:

```md
## Set Up A Data Semantic Layer

Codex gets better at data work when it understands the metric definitions, tables, filters, and source-of-truth context your team already uses.

Send anything you would point a new analyst to. I'll organize what you send into reusable guidance for future analysis.

Good starting points:
1. What this should help with, like a product or business area.
2. The source of truth for definitions or logic, like transformation code or repos, metric docs, a trusted data skill, reviewed SQL, dashboards, or recurring reports.
3. Data tables or catalogs you frequently use.
4. Places where data definitions, caveats, or changes are discussed, like team channels or threads.

Reply with any starting points, or say `skip for now`.
```

- Do not: require the user to name a product or business area up front, merge unrelated areas into one layer unless the user explicitly asks, ask for a broad source inventory before accepting useful inputs, create a layer from ambient connector availability alone, or pretend an ungrounded skeleton is source-backed.

### Step 3B: Create Or Plan Semantic Layer

- ID: `create_or_plan_semantic_layer`
- Type: `linear`
- Parent: `semantic_layer_setup`
- State field: `semantic_layer_setup`
- User-facing goal: Create, refresh, inspect, repair, or plan one source-backed semantic layer.
- Entry condition: The user supplied useful context or sources that can be organized into one or more coherent layers, or explicitly requested intake-only planning.
- Stay here when: The source inventory, crawl, create/refresh work, validation, durable pointer write, or one concrete blocked input is still unresolved.
- Exit when: The semantic layer is created, refreshed, inspected, repaired, planned with a stable target path and source inventory, skipped, deferred, or blocked on one concrete missing input.
- Completion: Write durable semantic-layer pointers to `user-context.md`; write operational setup status, source inventory path, starting-source count when useful, and compact connector-gap labels to `onboarding-state.json`. Do not copy source URLs, source inventory rows, or crawl output into onboarding state.
- Next: Step 3C, `offer_semantic_layer_refresh`, when a stable target path and pollable source inventory exist; otherwise Step 4A, `offer_first_hero_prompt`.
- Output contract: Read `semantic-layer/setup.md`, `semantic-layer/source-intake.md`, and `semantic-layer/connector-playbook.md`. Infer the likely organizing area from the user's inputs, split unrelated areas when needed, and ask one clarifying question only when organization would materially change the crawl or destination. Resolve connectors lazily as the selected evidence lanes need them. Build the source inventory before crawling. If a needed source route is selected but has not yet been read successfully in the current workflow, attempt the actual source read only when that semantic-layer lane needs it, then handle auth, query, schema, skip, or manual fallback in context. When enough user-provided or user-approved source-backed context exists, create or refresh the target standalone semantic-layer skill, validate it, write the durable pointer into `user-context.md`, and report the exact created or updated paths plus connector gaps. If blocked, state the exact missing connector, permission, source, or destination decision and ask for the smallest useful fallback.
- Transition after successful create or refresh:

```md
The semantic layer is set up and saved for future Data Analytics runs.
```

### Step 3C: Offer Semantic Layer Refresh

- ID: `offer_semantic_layer_refresh`
- Type: `optional`
- Parent: `semantic_layer_setup`
- State field: `semantic_layer_refresh`
- User-facing goal: Offer weekly source polling only after the semantic layer has a stable target path and pollable source inventory.
- Entry condition: Semantic-layer setup is created or planned with a stable target path plus source inventory.
- Stay here when: Weekly polling is applicable and the user has not accepted, declined, deferred, or marked it unavailable.
- Exit when: Weekly polling is accepted and read back, declined, deferred, unavailable, skipped because no semantic layer exists, or blocked on one concrete prerequisite.
- Completion: Record the operational resolution in `onboarding-state.json`; read `automation.md` and `semantic-layer/weekly-polling-automation.md` for approved automation setup.
- Next: Step 4A, `offer_first_hero_prompt`.
- Output contract: Ask the dedicated weekly polling question only when a stable target path and pollable source inventory exist. Keep the reply choices explicit:

```md
---

**Next Step**
Reply `set up weekly refresh` if you want Data Analytics to poll this semantic layer's sources each week, `skip refresh` to leave it manual, or `continue` to move on to the first analysis prompt.
```

- Do not: create an automation silently, claim refresh is active before readback succeeds, or keep asking after onboarding is complete or quiet unless the user explicitly reopens setup.

## Step 4: Hero Prompt

The hero prompt is the first value demonstration. Show one strong prompt first, make it report-first, and build it from real context gathered during source setup confirmation, any data semantic layer setup the user chose, and workflow-time source reads. Do not require a semantic layer before offering the prompt, and do not start with a three-option chooser. After the first prompt is run, skipped, or deferred, finish onboarding. Offer more prompt ideas only when the user explicitly asks for them later.

### Step 4A: Offer First Hero Prompt

- ID: `offer_first_hero_prompt`
- Type: `linear`
- Parent: `hero_prompt`
- State field: `hero_prompt_choice`
- User-facing goal: Show one runnable, context-derived report prompt that demonstrates the setup is useful.
- Entry condition: Core onboarding is complete, or the user explicitly chooses to try a workflow with known setup gaps.
- Stay here when: No first hero prompt has been accepted, run, skipped, or deferred.
- Exit when: The user says `run it`, `okay`, writes a different prompt, names a specific analysis question, skips, or defers the first hero prompt.
- Completion: Record the suggested prompt, selected skill, any selected anchor, and the disposition in `hero_prompt_choice`.
- Next: Step 4B, `run_first_hero_prompt`, when the user accepts or gives enough intent to run; Step 5, `complete_or_quiet`, when the user skips or defers.
- Output contract: Read the selected hero skill's inline experience guidance. Use `data_analytics_preflight.context.primary_hero_prompt` when available. The first hero prompt should select `product-business-analysis` and explicitly ask for a decision-ready report so the workflow hands the result to `$build-report`. The prompt must be runnable as written and use a real metric, product area, dashboard, table, semantic layer, or decision anchor from context. If no specific prompt can be formed, ask for the one missing product area, metric, dashboard, table, or decision anchor instead of showing placeholders. Use this shape:

```md
Now that the semantic layer is ready, here's the first Data Analytics prompt I'd try:

`@Data Analytics {context-derived runnable prompt}`

---

**Next Step**
Reply `run it` to try out this prompt, write the prompt you would rather try instead, or `skip` to finish onboarding.
```

- Do not: show three hero prompts initially, ask the user to say `change prompt`, include placeholders as if they are real context, or run the hero prompt in the same response as the first offer unless the user already gave an unambiguous prompt or said to run it.

### Step 4B: Run First Hero Prompt

- ID: `run_first_hero_prompt`
- Type: `linear`
- Parent: `hero_prompt`
- State field: `hero_prompt_choice`, `hero_workflow`, and `skill_experience.<selected_skill>.first_tried_at`
- User-facing goal: Run the selected first hero workflow and show one useful Data Analytics output without an extra confirmation turn.
- Entry condition: The user accepted the suggested prompt, provided a revised prompt, named a specific analysis question, or directly asked to run the selected hero skill with enough anchor context.
- Stay here when: The workflow is running, blocked on source auth, waiting for the smallest manual fallback needed by the selected skill, or no viable anchor exists.
- Exit when: The output has been delivered or the user skips this workflow.
- Completion: Mark the selected hero skill tried and record only compact prompt disposition metadata in onboarding state. Preserve workflow-owned artifact or source-gap notes in the workflow artifact or current response, not onboarding state.
- Next: Step 5, `complete_or_quiet`.
- Output contract: Use the selected skill's workflow guidance and run the workflow directly. If the selected skill has not been introduced yet, briefly name what is being run before the normal workflow output. Do not render a `What Happened`, `Recap`, or walkthrough heading by default.
- Ending:

```md
---

**Next Step**
Reply with a follow-up if you want to keep digging into this analysis, or say `show more prompts` if you want another Data Analytics prompt after onboarding.
```

- Do not: show extra prompt choices before the first result has been delivered, add a second onboarding CTA, or claim the prompt succeeded if required source access is still blocked.

### Step 4C: Offer Extra Hero Prompts

- ID: `offer_extra_hero_prompts`
- Type: `optional`
- Parent: `hero_prompt`
- State field: `hero_prompt_choice`, `completed_hero_prompts`, and `deferred_hero_prompts`
- User-facing goal: Offer up to two additional context-derived prompts only when the user explicitly asks for more prompt ideas after the first prompt is run, skipped, or deferred.
- Entry condition: The user explicitly asks for more prompt ideas after the first hero prompt has been run, skipped, or deferred.
- Stay here when: Additional context-derived prompt candidates are still worth offering and the user has not completed or quieted onboarding.
- Exit when: The user picks one, names another analysis question, skips, defers, or says to continue normal work.
- Completion: Record tried, skipped, deferred, or dismissed prompt candidates in onboarding state as compact skill/status/timestamp metadata only. Keep prompt history bounded; do not copy generated artifacts or source-gap notes into onboarding state.
- Next: Step 4B again when the user picks another prompt, or Step 5, `complete_or_quiet`.
- Output contract: Use `data_analytics_preflight.context.extra_hero_prompt_candidates` when available. Offer at most two prompts, each runnable as written. Keep the CTA explicit:

```md
---

**Next Step**
Reply `1` or `2` to try one of these, name a different analysis question, or say `done` to finish onboarding.
```

- Do not: turn normal Data Analytics work into a recurring welcome screen, offer only placeholder prompts, or hide the user's `done` path.

## Step 5: Completion Or Quiet

- ID: `complete_or_quiet`
- Type: `terminal`
- Parent: none
- State field: `status`
- User-facing goal: Stop automatic onboarding nudges once setup is meaningfully ready or the user asks for quiet.
- Entry condition: Core onboarding is resolved and the first hero prompt is run, skipped, or deferred, or the user asks to stop setup nudges.
- Stay here when: The user explicitly reopens onboarding or asks for setup status.
- Exit when: `status` is `complete` or `quiet`.
- Completion: Use `complete` when source setup confirmation, data semantic layer setup or explicit skip/defer/block resolution, any applicable refresh substep, and first hero prompt resolution are done. Use `quiet` when the user does not want more onboarding nudges.
- Terminal frame:

```md
---

**Onboarding Complete**
You're set up to use Data Analytics with configured source routes or explicit fallbacks, a resolved data semantic layer choice, and a first analysis workflow ready to reuse. Start a new thread with any real analytics question, or keep going with another suggested prompt when useful.
```

## Completion Criteria

Core onboarding is complete when criteria 1 and 2 are resolved. Full guided onboarding remains `active` until all criteria are satisfied or the user asks for quiet:

1. Source setup has covered each required source type as `active`, or as a user-explicit `skipped`, `deferred`, `declined`, `unavailable`, or `not_applicable` fallback recorded with `resolution: user_skipped`, `resolution: user_deferred`, `resolution: user_declined`, `resolution: user_marked_unavailable`, `resolution: user_confirmed_not_applicable`, or `resolution: user_continued_with_known_gap`. A manual source route counts as `active` only when its state entry records `source_kind: manual`; `needs_confirmation`, `missing`, or a required source fallback without one of those explicit resolution values still require the user to choose, install, skip, defer, decline, mark unavailable, mark not applicable, or continue with a recorded known gap before core setup is complete.
2. The data semantic layer step is resolved. The user either provides useful context or sources and a layer is created, refreshed, inspected, repaired, or planned with a stable target path and source inventory; explicitly skips or defers; or is blocked on one concrete missing input. The semantic-layer refresh substep is required only when a stable target path and pollable source inventory exist; otherwise mark refresh skipped, unavailable, deferred, or not applicable.
3. The first hero prompt is run, skipped, or deferred.

Connector behavior is workflow-time behavior: Data Analytics tries the relevant configured source route when a workflow needs it, continues when it works, and asks for connect, auth, skip, or manual fallback when it does not.

## CTA Arbitration

Invariant: exactly one final visible CTA per response.

- Ordinary skill run: the skill renders its normal next step from its experience guidance and its own workflow policy.
- Guided onboarding run: onboarding renders the final CTA; the skill suppresses its final CTA and returns next-step candidates.
- Onboarding review loop: final CTA is review, accept, continue, save, skip, or defer, not a skill continuation.
- Helper/provider skill: no intro or CTA unless explicitly requested.
- Ordinary skill run with an onboarding reminder obligation: merge the reminder into the single final action close or use the onboarding setup CTA as the sole final CTA. Do not render a standalone onboarding reminder that asks the user to continue onboarding and then render a separate skill-owned CTA.
- Automation setup/readback: keep automation cards and breadcrumbs visually separate from the action close.

## Workflow Walkthrough On Request

Do not render `What Happened`, `Recap`, or another walkthrough heading by default in onboarding demo outputs, ordinary direct skill runs, post-completion guided exploration, automation readbacks, follow-up turns, or source-gap replies. If the user explicitly asks what happened, asks how Data Analytics produced the result, or says yes to a walkthrough offer, then explain the observable steps.

When a walkthrough is requested, explain the observable tool/app calls, retrievals, source gaps, and artifact assembly at a beginner-friendly level without revealing hidden reasoning. Keep it grounded in visible activity: sources attempted, what worked, what did not, useful facts found, and how those facts shaped the artifact.

End the walkthrough by offering one valuable next action: continue to the next uncompleted guided workflow, fix the highest-value missing source, save a useful preference discovered during the run, or take a practical seller action from the artifact. Preserve the one-final-CTA rule.

## Ordinary Workflow Onboarding CTA

Use this template only after answering an ordinary Data Analytics workflow request while onboarding is missing or has not started. Do not use it for direct onboarding/status/setup responses, and do not use it when `onboarding-state.json` says onboarding is already active.

Do not use this template when the immediate workflow is blocked on a required clarification. Clarification questions always become the single final action close and suppress onboarding CTAs for that response.

```md
---

## Data Analytics Setup Required

This is required before Data Analytics can reliably use your configured sources and any authoritative semantic-layer context you choose to set up. It also gives you a useful overview of the plugin's key functionality.

Reply `start` to continue.
```

## Active Core Onboarding Reminder

Use this only after an ordinary Data Analytics workflow when onboarding is already active and a reminder would be useful. Do not use it for direct onboarding, setup, status, TODO-list, or capability-orientation responses; those should render the current onboarding step and its compact `**Next Step**` block instead. Do not use the `## Data Analytics Setup Required` start CTA, and do not ask whether to start onboarding. When the focused skill already owns a better final action close, fold `or say \`continue onboarding\` to resume setup` into that same final close instead of rendering a separate onboarding block. When this reminder is the sole final close, make the move-forward action explicit:

```md
---

**Next Step**
Reply `continue onboarding` and I'll resume with the next unfinished setup step.
```

## Context Gap Note

Use this only after an ordinary Data Analytics workflow when missing saved context or a failed workflow-time source materially reduced confidence, completeness, or ability to act.

```md
Data Analytics would get sharper here with a little more saved context, such as trusted dashboard or table pointers, metric definitions, semantic-layer context, source-of-truth docs, or preferred output format.
```

## Environment Conflict Audit

After the first orientation message, direct onboarding may include a lightweight environment conflict audit so the user can tell whether Data Analytics will be the analytics workflow that actually triggers. Do not run this audit before sending the first orientation message when no Data Analytics state exists yet. The audit is about routing and user experience, not connector availability.

Flag a plugin or skill as a conflict candidate when it broadly overlaps with one or more Data Analytics workflows and could plausibly capture the same natural-language request. Do not flag connector providers or source helpers as conflicts merely because Data Analytics uses those sources. Do not write clean audit results or conflict lists into onboarding state. If conflicts materially affect the user's setup, explain them in the current onboarding response.
