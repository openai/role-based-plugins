# Data Analytics Source Category Runtime

This reference owns how Data Analytics resolves semantic source categories to real plugins, apps, connectors, exports, local files, or user-provided context. Plugin-author editable category ids, labels, preferred plugin routes, and helper skills live in `../plugin-author-config/source-category-config.json`.

A source category is the kind of analytical evidence a workflow may need, such as structured data, team communication, company docs, BI dashboards, notebooks, email, calendar, or code repositories. The catalog is a routing aid, not proof that a connector is installed, authorized, preferred, or readable for the current user.

## Ownership Map

- `.app.json` and `DEPENDENCIES.MD` declare possible app-backed routes. They are not readiness proof for the current user.
- `../plugin-author-config/source-category-config.json` owns static source category ids, labels, preferred plugin routes, and category-level `relevant_skills`.
- `$CODEX_HOME/state/plugins/data-analytics/user-context.md` owns durable user-approved source-routing preferences and semantic-layer registry pointers.
- `$CODEX_HOME/state/plugins/data-analytics/onboarding-state.json` owns compact onboarding progress, connector-confirmation labels, semantic-layer setup and refresh state, hero prompt progress, and environment conflict notes. Do not persist raw discovery or inventory payloads there.

## Setup-Owned Source Routes

Source route selection happens during onboarding, an explicit source-setup turn, or workflow-time repair for a missing or broken source, not during ordinary preflight. The setup or search step is responsible for inspecting the current environment, preferring related plugins before raw app or connector routes, asking for installation or setup when needed, and writing compact resolved routes to `onboarding-state.json` under `connector_confirmation`. Do not persist the raw `functions.list_available_plugins_to_install` response, full session plugin inventory, connector descriptions, or discovery transcript into onboarding state.

Preflight is a reader. It should return the configured routes that setup wrote, plus unresolved setup gaps, but it must not choose a plugin, app, connector, or manual route on its own. Runtime workflows consume the configured routes.

During setup, prefer source routes in this order:

1. Installed or enabled related plugin from the session `Available plugins` block when it has visible plugin-owned skill or tool surface.
2. Installable related plugin returned by `functions.list_available_plugins_to_install`, including a plugin that contains or declares a connector or app id from the category's configured preferred plugin route.
3. Installed or installable app or connector returned by the same install listing or exposed in the session or tool surface.
4. Manual, uploaded, pasted, or exported context.
5. Missing or unavailable with practical IT or admin options.

At the start of onboarding source resolution or explicit source setup, call `functions.list_available_plugins_to_install` once and reuse those results for all source categories in that pass. Also read the session `Available plugins` block to identify installed plugins, and read the session `Available skills` block when deciding whether an installed plugin has plugin-owned skills exposed. Load `../plugin-author-config/source-category-config.json` for category `preferred_plugins` and legacy `preferred_apps` only when present, and load `.app.json` to map configured preferred provider names to app or connector ids.

Installed source tools are treated as usable for setup purposes only when their surface is visible enough to use later. If setup finds one or more installed related plugins with visible plugin-owned skill or tool surfaces for the same category, write all useful routes as active under `routes` and let workflows choose among them by evidence need. Do not force a preference question just because several non-conflicting sources are available, such as Google Drive and Notion for company docs; the agent can use both. If setup finds an installed app or connector and also finds a related plugin candidate, prefer the plugin anyway because Data Analytics workflows should use plugin-owned skills and tools when available; keep the app or connector route as fallback if the user defers or install visibility is pending. If setup finds one installed app or connector and no related plugin candidate, write the app or connector route as active and let the workflow try the actual read only when it needs that source. Do not perform a read merely to prove an installed source works during onboarding.

Do not mark a plugin route as `active` unless there is enough evidence: the plugin is listed in `Available plugins` or was just installed successfully with `request_plugin_install`, the relevant app, connector, or tool surface is callable or exposed, and plugin-owned skills are visible in `Available skills` when that plugin is expected to provide skills. If plugin install succeeds but skills or tools are not visible until the next turn or session refresh, record the route as `needs_confirmation`, deferred, or pending and ask the user to continue after refresh. Do not silently mark it `plugin_owned`.

Use only these setup evidence strings unless this contract is intentionally updated:

- `plugin_install_evidence`: `plugin_in_available_plugins`, `request_plugin_install_completed`, `installed_plugin_skill_visible`, `plugin_owned_skill_visible`, or `user_confirmed_installed_plugin`.
- `skill_surface_evidence`: `plugin_skills_visible`, `plugin_owned_skill_visible`, or `plugin_owned_skills_visible`.
- `app_surface_evidence` or `tool_surface_evidence`: `callable_app_tools_visible`, `callable_plugin_tools_visible`, or `plugin_tools_visible`.
- `connector_surface_evidence`: `request_plugin_install_completed_or_callable_surface_visible` or another explicit connector-surface proof returned by setup.

Recommended active plugin route state:

```json
{
  "connector_confirmation": {
    "team_communication": {
      "status": "active",
      "preferred": "Slack",
      "source_kind": "plugin",
      "skill_surface": "plugin_owned",
      "plugin": {
        "id": "slack@openai-curated",
        "name": "Slack"
      },
      "plugin_install_evidence": "request_plugin_install_completed",
      "app_surface_evidence": "callable_app_tools_visible",
      "skill_surface_evidence": "plugin_skills_visible",
      "setup_action": "none_try_on_use"
    }
  }
}
```

Recommended active multi-route state:

```json
{
  "connector_confirmation": {
    "company_docs": {
      "status": "active",
      "routes": [
        {
          "preferred": "Google Drive",
          "source_kind": "plugin",
          "skill_surface": "plugin_owned",
          "plugin": {
            "id": "google-drive@openai-curated",
            "name": "Google Drive"
          },
          "plugin_install_evidence": "plugin_in_available_plugins",
          "skill_surface_evidence": "plugin_skills_visible",
          "setup_action": "none_try_on_use"
        },
        {
          "preferred": "Notion",
          "source_kind": "plugin",
          "skill_surface": "plugin_owned",
          "plugin": {
            "id": "notion@openai-curated",
            "name": "Notion"
          },
          "plugin_install_evidence": "plugin_in_available_plugins",
          "skill_surface_evidence": "plugin_skills_visible",
          "setup_action": "none_try_on_use"
        }
      ],
      "setup_action": "none_try_on_use"
    }
  }
}
```

Recommended active app or connector route state:

```json
{
  "connector_confirmation": {
    "structured_data": {
      "status": "active",
      "preferred": "Databricks",
      "source_kind": "connector",
      "skill_surface": "data_analytics_vendored_helper",
      "connector": {
        "id": "templated_apps_Databricks",
        "name": "Databricks"
      },
      "connector_surface_evidence": "request_plugin_install_completed_or_callable_surface_visible",
      "setup_action": "none_try_on_use"
    }
  }
}
```

Use `source_kind: manual` and `skill_surface: manual` only when the user chooses manual, uploaded, pasted, or exported context as the configured route for that source category.

## Runtime Source Resolution

Use sources only when the active workflow needs them. Do not proactively read every category during onboarding, and do not surface installed connectors as durable readiness state.

Choose sources by the fact they own, not by connector availability or convenience. When a workflow asks for stable ownership, approval, routing, source-of-truth, or "who/where should I ask" information, prefer the most canonical ownership or routing source available for that fact, such as a people directory, team directory, company knowledge base, maintained wiki page, verified routing doc, go-link index, source-of-truth hub, or saved source pointer. Use broad document search, chat/message search, public research, or mirrored sources as supporting evidence only when the canonical source is missing, stale, thin, contradicted, or the workflow explicitly needs recent discussion.

For quick ordinary workflow runs, prefer a bounded first pass over exhaustive triangulation. A useful default is one canonical source attempt, one narrow fallback when the first pass is empty, thin, or misleading, and then a user-facing answer with source limitations and an offer to continue. If a connector times out, rate-limits, or consumes roughly the time of two slow source calls for a non-required enrichment lane, return the best available partial result instead of continuing low-yield retrieval.

Do not spend more than roughly three to five minutes of active retrieval on a user-facing workflow without yielding back to the user. If that budget is reached before the answer is strong, stop searching and give a concise checkpoint: what was checked, the best current candidates or partial answer, the limiting gap, and one recommended next step. Choose that next step by usefulness: ask the user to clarify or steer when the search space is ambiguous, suggest continuing deeper when results are promising but incomplete, or suggest acting on the current best answer when it is good enough. Do not continue silent low-yield retrieval merely because more sources or query variants remain.

For each source category a workflow actually attempts:

1. Read saved source-routing preferences and "do not use" rules from `user-context.md`.
2. Read the configured `connector_confirmation` route or `routes` from preflight. If the category is `active` and one route has `source_kind: plugin`, use the plugin-owned skill or callable tool surface for the active task. If several routes are `active`, choose by fact ownership and likely authority; use multiple routes when doing so would materially improve confidence, such as searching both Drive-native assets and Notion source-of-truth pages.
3. If the route is missing, incomplete, broken, manual-only, or connector or app based, first run the plugin-first setup branch below before using connector fallback. Ask before installing unless the user explicitly requested installation. When a connector route is already `active`, still prefer an available related plugin because the plugin can add dedicated Data Analytics workflow support.
4. For `source_kind: app` or `source_kind: connector`, attempt the smallest useful app or connector read for the active task. For apps covered by marketplace `policy.authentication: ON_USE`, this attempted use should trigger setup or authorization when needed. Load Data Analytics' vendored helper skill only when the configured route has `skill_surface: data_analytics_vendored_helper`.
5. For `source_kind: manual`, use pasted, uploaded, exported, or otherwise user-provided context.
6. If the read works, continue the workflow with citations or source notes as appropriate. A successful read is evidence for this run only; do not write connector readiness state.
7. If the configured route fails, explain the practical blocker and offer the next best path: install or reconnect a related plugin when available, connect or authorize the app, install the connector when exposed, ask IT/admin, skip that source for this run, or use a manual or exported fallback. Preferred and `active` routes are always retryable in future workflows unless the user explicitly saves a durable `do not use` rule; when a future workflow needs a source and the route is missing, unauthorized, stale, or broken, try it again and prompt the user to install, connect, reauthorize, or choose a fallback.
8. Save a future source-routing default or "do not use this source" rule only when the user explicitly selects it for future use or declines that source for future use. Do not use `user-context.md` for general memory, arbitrary saved links, source-of-truth pointers, or area-specific caveats; those belong in the relevant semantic layer when one exists.

## Plugin-First Setup For Missing Sources

When setup finds that a needed source category is not already covered by a proven active plugin route, prefer related plugin setup before raw app or connector setup or manual fallback. Preflight surfaces this as `setup_action: run_plugin_first_source_setup`, `plugin_preference_order`, and `setup_recovery.type: plugin_first_source_setup`.

1. Build the plugin preference order from `saved_source_preferences` when preflight provides them first, then the source category's configured `preferred_plugins`, then legacy `preferred_apps` only when present. Use that order to rank plugins, but do not require the user to have saved a preference before plugin setup is attempted.
2. Check the session `Available plugins` block for an installed plugin whose name, display name, id, or declared app or connector ids match a configured preferred plugin route for the category. If it has visible plugin-owned skill or tool surface, write it as the active route.
3. If no installed related plugin exists, call `functions.list_available_plugins_to_install` if it has not already been called in this setup pass, then look for related plugin candidates.
4. A candidate is related only when the plugin or provider itself matches the configured preferred plugin route, or its declared `app_connector_ids` intersects the `.app.json` ids for a configured preferred plugin route. Legacy `preferred_apps` may contribute only when an older config still declares them. Do not treat broad search, mirrored content, imported content, or a description-level category similarity as enough to make a plugin related.
5. Prefer plugin candidates over connector candidates even when the app or connector route is already callable or active. If one related plugin candidate is clearly best by saved preference order, configured `preferred_plugins` order, legacy `preferred_apps` order when present, or connector-id intersection, ask one clear install or defer question unless the user explicitly requested installation. If the user confirms, call `functions.request_plugin_install` with the exact returned candidate `tool_type` and `id`. Do not call `request_plugin_install` in parallel with any other tool.
6. If multiple related plugin candidates tie after saved preference order, configured `preferred_plugins` order, legacy `preferred_apps` order when present, and connector-id matching, ask the user to choose among only those tied relevant candidates.
7. If installation or setup fails, or install succeeds but plugin skills or tools are not visible yet, keep the plugin setup path retryable. Record `needs_confirmation`, `deferred`, `deferred_environment_api_limitations`, or `skipped_for_now` for operational state, not `declined`, and surface plugin-first setup again in a future workflow when that source category is material. Use connector or app or manual fallback for the current run when useful.
8. If the user declines a plugin, suppress that plugin for the current workflow and continue with the next related plugin candidate, the existing app or connector route, another user-selected source, or manual or exported context. Save a durable `do not use` or `do not offer` rule only when the user explicitly asks for that future behavior.
9. If no related plugin candidate exists, use the same install-list results and exposed session tools to find an installed or installable app or connector candidate.
10. If one plausible app or connector is available and no plugin route is chosen, ask the user to confirm it if needed, then record the app or connector route in `connector_confirmation` without a proof read.
11. If multiple plausible apps or connectors are available and no plugin route is chosen, ask the user which one to prefer and record that route after selection.
12. If no matching plugin, app, or connector is available, explain the practical workflow impact and ask the user to install, connect, or authorize a preferred source, ask IT/admin to enable one, defer or skip the category, or use manual or exported context.
13. If no setup route is available or the user skips setup, write the manual, skipped, or deferred route and use pasted, uploaded, exported, or manual context for the current run when that can satisfy the evidence need.

Example install-list candidate shape:

```json
{
  "tool_type": "plugin",
  "id": "slack@openai-curated",
  "name": "Slack",
  "display_name": "Slack",
  "app_connector_ids": ["REPLACE_WITH_SLACK_APP_OR_CONNECTOR_ID"],
  "description": "Use Slack messages and Data Analytics workflows from Codex."
}
```

Do not proactively suggest every installable plugin; show only plugins related to the current Data Analytics source category. Do not use `tool_search` as proof that a plugin is installed. Installation evidence must come from the session `Available plugins` block or a successful `request_plugin_install` call. Do not guess plugin ids; call `request_plugin_install` only with an exact candidate returned by `list_available_plugins_to_install`.

When an attempted source fails, distinguish failure class before giving the user a setup CTA:

- `needs re-auth`: the connector explicitly says reauthentication or reauthorization is required. Ask the user to reconnect or authorize that app.
- `not ready / startup issue`: the app or MCP server times out during startup, handshake, client creation, or transport setup. Say the connector did not become ready, suggest retrying shortly or checking app or runtime status, and do not tell the user to reconnect unless the app later returns a re-auth error.
- `missing or unsupported`: the connector or app is not installed, not exposed, or lacks the needed action. Offer install or admin enablement, skip, or manual or exported fallback.
- `query/schema issue`: the source is reachable but the requested object, field, filter, or query shape failed. Use the relevant helper skill's recovery rules before asking the user.

Keep user-facing wording practical. Say what source is unavailable and why it matters for the analytical job, such as `I cannot reach the warehouse path for this workflow yet, so I cannot confirm metric definitions from live tables until Databricks is available to this workflow or you provide SQL/schema context.`

## Missing Sources And Fallbacks

When a plugin, connector, or app cannot be used, keep the message Data Analytics user-facing. Say what source is missing and why it matters for the current job, such as warehouse access or reviewed SQL or schema context is needed to validate metric definitions from live data. Avoid implementation-facing labels like `category-state`, `preflight`, or raw category ids unless the user asks.

Manual input, pasted notes, and exports are valid fallbacks after a real connector attempt fails, the configured route is unsupported in the environment, the user declines connector use, or the current need is urgent enough to bypass setup. Treat manual fallbacks as one-run inputs unless the user explicitly selects a future source-routing preference.

## Core Onboarding Categories

Show these categories first during onboarding:

- `structured_data`: Data warehouse.
- `team_communication`: Team communication.
- `company_docs`: Company docs.

Add optional categories only when the user's request, available sources, or semantic-layer plan makes them useful.

These are core onboarding categories, not optional setup extras. During direct onboarding, if one of them does not have an active plugin, app, connector, or manual route, keep it in the visible Step 2 or Step 2A source questions before introducing semantic-layer setup. If setup finds an installable related plugin for a core category, keep that category as `needs_confirmation` until the user installs it or explicitly chooses a fallback. Do not quietly write `deferred`, `skipped`, `declined`, `unavailable`, or `not_applicable` for a core category just to advance onboarding. A core fallback counts as resolved only when onboarding state records the user's explicit choice with `resolution: user_deferred`, `resolution: user_skipped`, `resolution: user_declined`, `resolution: user_marked_unavailable`, `resolution: user_confirmed_not_applicable`, or `resolution: user_continued_with_known_gap`. If a core fallback status appears without one of those explicit resolutions, preflight should surface it again as `needs_confirmation`.

## Onboarding Connector Confirmation

Onboarding may classify source categories so the user understands what Data Analytics can use, what needs setup, and what may require IT or admin help. These labels and route metadata are operational onboarding state, not durable connector-readiness proof, and they belong under `connector_confirmation` in `onboarding-state.json`.

When showing a category, explain the analytical value instead of only naming the connector family:

- `structured_data`: direct warehouse or SQL access lets Data Analytics query structured data for current, source-backed answers.
- `team_communication`: search recent discussions for context, decisions, and owners.
- `company_docs`: docs, specs, metric definitions, and source-of-truth pages can answer governance and business-context questions without querying live data.
- Optional categories should be explained only when offered: dashboards and BI for inspecting dashboards and BI reports for metric definitions, filters, and saved views, behavior signals for product-usage evidence, notebook lab for inspecting prior analyses, reusing notebook logic, and continuing exploratory work, email or calendar for recent operating context, and code repositories for model, query, schema, or semantic-layer ownership.

Use exactly these user-facing statuses:

- `active`: setup found or installed one or more source routes and wrote either route-level `routes[]` entries or backward-compatible `source_kind`, `skill_surface`, and route details when available. This is FYI only. Do not perform an eager read just to prove an installed source works; attempt active sources only when a workflow needs them.
- `needs_confirmation`: setup found multiple plausible source tools, an installable related plugin that needs approval, or a selected source preference that still needs a route recorded. Ask the user which source to prefer or whether to install the plugin when needed. If the selected source is an installed plugin, app, or connector, write the chosen route and let the workflow's first real read handle auth, query, or schema failures.
- `missing`: setup found no matching installed plugin, connector, or app. Explain what Data Analytics workflows will be weaker without it and list concrete IT or admin options, such as installing the plugin or connector, authorizing the app for Codex, or using a manual or exported fallback for now.
- `deferred`, `skipped`, `declined`, or `unavailable`: setup did not choose an active route. Include practical impact and the next best plugin, app, connector, or manual path when useful. Treat failed setup, pending plugin visibility, temporary unavailability, and `skipped_for_now` as retryable while related plugins may become available later. Treat `declined` as a current-workflow suppression unless the user explicitly saves a future `do not use` rule. For a core onboarding category, write one of these only after the user explicitly chooses that fallback and record the matching `resolution` value above; an automatic or stale core fallback must not make source setup look complete.

Use `source_kind: manual` and `skill_surface: manual` when the user chooses pasted SQL, exports, screenshots, local files, schemas, API results, CLI output, or another manual route. Manual is route metadata, not a separate onboarding status.

If the user says `connect Databricks`, `use Slack`, or `Google Drive should work`, treat that as permission to record or repair the selected source route and run the matching install, connect, or authorize path when that path is exposed. Do not run a proof query during onboarding. When a later workflow needs that source, attempt the actual source read then and handle auth, query, schema, skip, or manual fallback in context.

Recommended state shape:

```json
{
  "connector_confirmation": {
    "structured_data": {
      "status": "needs_confirmation",
      "preferred": "Databricks",
      "candidates": ["Databricks", "BigQuery", "Snowflake"]
    },
    "team_communication": {
      "status": "active",
      "preferred": "Slack",
      "confirmed_at": "2026-05-29T00:00:00Z"
    },
    "company_docs": {
      "status": "active",
      "preferred": "Google Drive",
      "source_kind": "manual",
      "skill_surface": "manual",
      "manual_source": "uploaded docs"
    }
  }
}
```

Do not write `available`, `verified`, `checked`, `installed`, or automatic `blocked` as durable source status. If the user chooses a future default or a source to avoid, save only that approved routing preference in `user-context.md`.

## Onboarding Behavior

The first direct onboarding response should not inspect connectors. After the user approves setup, run source setup or search, call `functions.list_available_plugins_to_install` once, prefer related plugins over raw app or connector routes, and write resolved routes for each category to `connector_confirmation`. Do not preflight-read installed or active connectors merely to prove they work. Active sources are informational only; do not ask the user to confirm every source when setup finds clear active installed plugins, apps, or connectors that can coexist in the same category.

Ask for help only when there are multiple mutually exclusive plausible source tools, an installable related plugin needs approval, no source was found, or IT or admin action may be needed. For missing or connector-covered sources, use plugin setup before connector or app setup and manual fallback. When a later focused workflow needs a source, that workflow attempts the configured source route at that moment and handles plugin install, auth, connection, skip, or manual fallback in context.

Do not advance from core source setup into semantic-layer setup while `structured_data`, `team_communication`, or `company_docs` is still `needs_confirmation` or `missing`. Optional categories may be deferred until a workflow or semantic-layer plan needs them. Core categories may also be deferred, skipped, declined, marked unavailable, or marked not applicable, but only after the user explicitly chooses that known-gap path and onboarding state records the matching `resolution`.
