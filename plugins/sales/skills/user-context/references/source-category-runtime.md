# Sales Source Category Runtime

This reference owns how Sales uses source categories at workflow time. Plugin-author editable category ids, labels, preferred plugins/apps, and helper skills live in `../plugin-author-config/source-category-config.json`.

A source category is the kind of sales evidence a workflow may need, such as CRM, calendar, docs, meeting notes, email, Slack, or enrichment. The catalog is a routing aid, not a record of plugin, app, or connector setup.

## Ownership Map

- `.app.json` declares app and connector dependencies the plugin can request through the install/connect/auth flow. It is not proof that an app is installed, authorized, preferred, or readable for the current user.
- `../plugin-author-config/source-category-config.json` owns static source category ids, seller-facing labels, preferred plugin/app order, and category-level `relevant_skills`.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` owns durable user-approved source preferences, source-of-truth links, team conventions, examples, formatting preferences, "do not use" rules, and operating notes.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json` owns onboarding progress, connector-confirmation labels, guided workflow progress, and automation metadata.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/category-state.json` is legacy-only. Normal onboarding and preflight should not create it, read it, or update it. If an older copy exists, do not treat it as durable connector proof. Migrate any explicit user choices that still matter into `user-context.md` as source preferences or decline rules, then leave automatic readiness fields behind.

## Setup-Owned Source Routes

Source route selection happens during onboarding, an explicit source-setup turn, or workflow-time repair for a missing/broken source, not during ordinary preflight. The setup/search step is responsible for inspecting the current environment, preferring related plugins before raw app/connector routes, asking for installation or setup when needed, and writing resolved routes to `onboarding-state.json` under `connector_confirmation`.

Preflight is a reader. It should return the configured routes that setup wrote, plus unresolved setup gaps, but it must not choose a plugin, app, connector, or manual route on its own. Runtime workflows consume the configured routes.

During setup, prefer source routes in this order:

1. Installed/enabled related plugin from the session `Available plugins` block when it has visible plugin-owned skill/tool surface.
2. Installable related plugin returned by `functions.list_available_plugins_to_install`, including a plugin that contains or declares a connector/app id from the category's preferred list.
3. Installed or installable app/connector returned by the same install listing or exposed in the session/tool surface.
4. Manual, uploaded, pasted, or exported context.
5. Missing/unavailable with practical IT/admin options.

At the start of onboarding source resolution or explicit source setup, call `functions.list_available_plugins_to_install` once and reuse those results for all source categories in that pass. Also read the session `Available plugins` block to identify installed plugins, and read the session `Available skills` block when deciding whether an installed plugin has plugin-owned skills exposed. Load `../plugin-author-config/source-category-config.json` for category `preferred_plugins` and `preferred_apps`, and load `.app.json` to map preferred app names to configured app/connector ids.

Installed source tools are treated as usable for setup purposes only when their surface is visible enough to use later. If setup finds one or more installed related plugins with visible plugin-owned skill/tool surfaces for the same category, write all useful routes as active under `routes` and let workflows choose among them by evidence need. Do not force a preference question just because several non-conflicting sources are available, such as Google Drive and Notion for docs; the agent can use both. If setup finds an installed app or connector and also finds a related plugin candidate, prefer the plugin anyway because Sales workflows should use plugin-owned skills and tools when available; keep the app/connector route as fallback if the user defers or install visibility is pending. If setup finds one installed app or connector and no related plugin candidate, write the app/connector route as active and let the workflow try the actual read only when it needs that source. Do not perform a read merely to prove an installed source works during onboarding.

Do not mark a plugin route as active unless there is enough evidence: the plugin is listed in `Available plugins` or was just installed successfully with `request_plugin_install`, the relevant app/connector/tool surface is callable or exposed, and plugin-owned skills are visible in `Available skills` when that plugin is expected to provide skills. If plugin install succeeds but skills/tools are not visible until the next turn or session refresh, record the route as `needs_confirmation` or deferred/pending and ask the user to continue after refresh. Do not silently mark it `plugin_owned`.

Use only these setup evidence strings unless this contract is intentionally updated:

- `plugin_install_evidence`: `plugin_in_available_plugins`, `request_plugin_install_completed`, `installed_plugin_skill_visible`, `plugin_owned_skill_visible`, or `user_confirmed_installed_plugin`.
- `skill_surface_evidence`: `plugin_skills_visible`, `plugin_owned_skill_visible`, or `plugin_owned_skills_visible`.
- `app_surface_evidence` or `tool_surface_evidence`: `callable_app_tools_visible`, `callable_plugin_tools_visible`, or `plugin_tools_visible`.
- `connector_surface_evidence`: `request_plugin_install_completed_or_callable_surface_visible` or another explicit connector-surface proof returned by setup.

Recommended active plugin route state:

```json
{
  "connector_confirmation": {
    "crm": {
      "status": "active",
      "preferred": "HubSpot",
      "source_kind": "plugin",
      "skill_surface": "plugin_owned",
      "plugin": {
        "id": "hubspot@openai-curated",
        "name": "HubSpot"
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
    "document_store": {
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

Recommended active app/connector route state:

```json
{
  "connector_confirmation": {
    "crm": {
      "status": "active",
      "preferred": "Salesforce",
      "source_kind": "connector",
      "skill_surface": "sales_vendored_helper",
      "connector": {
        "id": "REPLACE_WITH_SALESFORCE_APP_OR_CONNECTOR_ID",
        "name": "Salesforce"
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

For quick ordinary workflow runs, prefer a bounded first pass over exhaustive triangulation. A useful default is one canonical source attempt, one narrow fallback when the first pass is empty/thin/misleading, and then a user-facing answer with source limitations and an offer to continue. If a connector times out, rate-limits, or consumes roughly the time of two slow source calls for a non-required enrichment lane, return the best available partial result instead of continuing low-yield retrieval.

Do not spend more than roughly three to five minutes of active retrieval on a user-facing workflow without yielding back to the user. If that budget is reached before the answer is strong, stop searching and give a concise checkpoint: what was checked, the best current candidates or partial answer, the limiting gap, and one recommended next step. Choose that next step by usefulness: ask the user to clarify or steer when the search space is ambiguous, suggest continuing deeper when results are promising but incomplete, or suggest acting on the current best answer when it is good enough. Do not continue silent low-yield retrieval merely because more sources or query variants remain.

For each source category a workflow actually attempts:

1. Read saved source preferences, source-of-truth pointers, and "do not use" rules from `user-context.md`.
2. Read the configured `connector_confirmation` route or `routes` from preflight. If the category is active and one route has `source_kind: plugin`, use the plugin-owned skill or callable tool surface for the active task. If several routes are active, choose by fact ownership and likely authority; use multiple routes when doing so would materially improve confidence, such as searching both Drive-native assets and Notion source-of-truth pages.
3. If the route is missing, incomplete, broken, manual-only, or connector/app-based, first run the plugin-first setup branch below before using connector fallback. Ask before installing unless the user explicitly requested installation. When a connector route is already active, still prefer an available related plugin because the plugin can add dedicated Sales workflow support.
4. For `source_kind: app` or `source_kind: connector`, attempt the smallest useful app/connector read for the active task. For apps covered by marketplace `policy.authentication: ON_USE`, this attempted use should trigger setup or authorization when needed. Load Sales' vendored helper skill only when the configured route has `skill_surface: sales_vendored_helper`.
5. For `source_kind: manual`, use pasted, uploaded, exported, or otherwise user-provided context.
6. If the read works, continue the workflow with citations or source notes as appropriate. A successful read is evidence for this run only; do not write connector readiness state.
7. If the configured route fails, explain the practical blocker and offer the next best path: install or reconnect a related plugin when available, connect or authorize the app, install the connector when exposed, ask IT/admin, skip that source for this run, or use a manual/exported fallback. Preferred and active routes are always retryable in future workflows unless the user explicitly saves a durable `do not use` rule; when a future workflow needs a source and the route is missing, unauthorized, stale, or broken, try it again and prompt the user to install, connect, reauthorize, or choose a fallback.
8. Save a default, source preference, source-of-truth pointer, decline, or "do not use this source" rule only when the user explicitly asks to remember it, chooses it as a future default, provides a link or fact to save, or declines a source for future use.

## Plugin-First Setup For Missing Sources

When setup finds that a needed source category is not already covered by a proven active plugin route, prefer related plugin setup before raw app/connector setup or manual fallback. Preflight surfaces this as `setup_action: run_plugin_first_source_setup`, `plugin_preference_order`, and `setup_recovery.type: plugin_first_source_setup`.

1. Build the plugin preference order from `saved_source_preferences` when preflight provides them first, then the source category's configured `preferred_plugins`, then `preferred_apps`. Use that order to rank plugins, but do not require the user to have saved a preference before plugin setup is attempted.
2. Check the session `Available plugins` block for an installed plugin whose name, id, description, or declared app/connector ids match a preferred plugin or app for the category. If it has visible plugin-owned skill/tool surface, write it as the active route.
3. If no installed related plugin exists, call `functions.list_available_plugins_to_install` if it has not already been called in this setup pass, then look for related plugin candidates.
4. A candidate is related when its `name` or `display_name` matches a preferred plugin or app, its `id` clearly names the preferred plugin/app, its `app_connector_ids` intersects the `.app.json` ids for any category preferred app, or its description clearly names the same provider/category and no better preferred plugin/app match exists.
5. Prefer plugin candidates over connector candidates even when the app/connector route is already callable or active. If one related plugin candidate is clearly best by saved preference order, configured `preferred_plugins`/`preferred_apps` order, or connector-id intersection, ask one clear install/defer question unless the user explicitly requested installation. If the user confirms, call `functions.request_plugin_install` with the exact returned candidate `tool_type` and `id`. Do not call `request_plugin_install` in parallel with any other tool.
6. If multiple related plugin candidates tie after saved preference order, configured `preferred_plugins`/`preferred_apps` order, and connector-id matching, ask the user to choose among only those tied relevant candidates.
7. If installation or setup fails, or install succeeds but plugin skills/tools are not visible yet, keep the plugin setup path retryable. Record `needs_confirmation`, `deferred`, `deferred_environment_api_limitations`, or `skipped_for_now` for operational state, not `declined`, and surface plugin-first setup again in a future workflow when that source category is material. Use connector/app or manual fallback for the current run when useful.
8. If the user declines a plugin, suppress that plugin for the current workflow and continue with the next related plugin candidate, the existing app/connector route, another user-selected source, or manual/exported context. Save a durable `do not use` or `do not offer` rule only when the user explicitly asks for that future behavior.
9. If no related plugin candidate exists, use the same install-list results and exposed session tools to find an installed or installable app/connector candidate.
10. If one plausible app or connector is available and no plugin route is chosen, ask the user to confirm it if needed, then record the app/connector route in `connector_confirmation` without a proof read.
11. If multiple plausible apps or connectors are available and no plugin route is chosen, ask the user which one to prefer and record that route after selection.
12. If no matching plugin, app, or connector is available, explain the practical workflow impact and ask the user to install/connect/authorize a preferred source, ask IT/admin to enable one, defer/skip the category, or use manual/exported context.
13. If no setup route is available or the user skips setup, write the manual/skipped/deferred route and use pasted, uploaded, exported, or manual context for the current run when that can satisfy the evidence need.

Example install-list candidate shape:

```json
{
  "tool_type": "plugin",
  "id": "hubspot@openai-curated",
  "name": "HubSpot",
  "display_name": "HubSpot",
  "app_connector_ids": ["REPLACE_WITH_HUBSPOT_APP_OR_CONNECTOR_ID"],
  "description": "Use HubSpot CRM records and sales workflows from Codex."
}
```

Do not proactively suggest every installable plugin; show only plugins related to the current Sales source category. Do not use `tool_search` as proof that a plugin is installed. Installation evidence must come from the session `Available plugins` block or a successful `request_plugin_install` call. Do not guess plugin ids; call `request_plugin_install` only with an exact candidate returned by `list_available_plugins_to_install`.

When an attempted source fails, distinguish failure class before giving the user a setup CTA:

- `needs re-auth`: the connector explicitly says reauthentication or reauthorization is required. Ask the user to reconnect or authorize that app.
- `not ready / startup issue`: the app or MCP server times out during startup, handshake, client creation, or transport setup. Say the connector did not become ready, suggest retrying shortly or checking app/runtime status, and do not tell the user to reconnect unless the app later returns a re-auth error.
- `missing or unsupported`: the connector/app is not installed, not exposed, or lacks the needed action. Offer install/admin enablement, skip, or manual/exported fallback.
- `query/schema issue`: the source is reachable but the requested object, field, filter, or query shape failed. Use the relevant helper skill's recovery rules before asking the user.

## Relevant Skills

If an attempted category's plan includes `relevant_skills`, load the matching helper skill only when the configured source route is `source_kind: app` or `source_kind: connector` and `skill_surface: sales_vendored_helper`. The helper skill adds provider-specific connector rules only; the focused Sales workflow remains authoritative for the seller task and output.

## Missing Sources And Fallbacks

When a plugin, connector, or app cannot be used, keep the message seller-facing. Say what source is missing and why it matters for the current job, such as `meeting notes or call recordings are needed for transcript-backed follow-up`. Avoid implementation-facing labels like `category-state`, `preflight`, or raw category ids unless the user asks.

Preferred apps are source-category hints, not the only route. During setup, if a preferred source is missing, try an appropriate app/connector alternative only when it can genuinely satisfy the same evidence need. Do not satisfy a source through a related connector that merely mirrors or imports the native source's content unless the user has saved that mirrored source as the source of truth.

Docs preferences are light source-selection hints, not provider lockouts or strong ranking overrides. A saved preference such as `look in Notion first for Sales docs` means give Notion a small first-look bias when it fits the current evidence need, but still actively consider Google Drive, SharePoint, Slack-linked docs, email attachments, CRM-linked files, and other available sources. For broad discovery tasks, especially Sales Company Research, do not let a preferred docs provider or the static preferred-app catalog dominate the search plan: search across all available and authorized source families early enough to compare candidates by authority, artifact type, freshness, and future workflow value. Include non-doc knowledge surfaces such as company knowledge bases, wikis, internal messaging, CRM, email, calendar, meetings, issue trackers, dashboards/reporting tools, and customer-facing asset libraries whenever they can plausibly contain a better Sales source. Use Google Drive whenever the artifact type points there, including Drive-native files, Docs, Sheets, decks, folders, customer-shareable collateral, enablement libraries, or linked assets. Use multiple docs sources when doing so would materially improve confidence or source authority.

Manual input, pasted notes, and exports are valid fallbacks after a real connector attempt fails, the connected route is unsupported in the environment, the user declines connector use, or the current need is urgent enough to bypass setup. Treat manual fallbacks as one-run inputs unless the user asks Sales to remember a preference or source pointer.

## Durable Source Preferences

Save durable source choices in `user-context.md`, not connector readiness JSON. Good saved entries include:

- preferred CRM or meeting-notes source;
- first-look docs preference such as `look in Notion first for internal source-of-truth pages, but still use Google Drive for Drive-native files, Docs, Sheets, decks, shareable collateral, linked folders, or evidence likely to live there`;
- source-of-truth docs, hubs, trackers, reports, or channels;
- source priority such as `prefer Zoom over Notion meeting notes`;
- write-safety rules such as `never write CRM without review`;
- explicit avoidance such as `I do not have ZoomInfo; do not try enrichment connectors unless I say access changed`;
- team-specific conventions for when a source should win over another source.

Use the normal memory shape from `plugin-memory.md`: resource or fact name, `Date Added`, `Useful Context`, and `Future Use`. Include freshness and fallback expectations when they affect future workflow behavior.

## Onboarding Connector Confirmation

Onboarding may classify each source category so the user understands what Sales can use, what needs setup, and what may require IT/admin help. These labels and route metadata are operational onboarding state, not durable connector-readiness proof, and they belong under `connector_confirmation` in `onboarding-state.json`.

When explaining source coverage during onboarding, make the practical workflow value concrete:

- `crm`: account, opportunity, owner, pipeline, contact, activity, forecast, and account-status context for meeting prep, follow-up, deal strategy, prioritization, account signals, and forecast review.
- `calendar`: upcoming meetings, invite details, attendee lists, timing, and daily/scheduled meeting selection.
- `meeting_notes`: transcripts, recordings, customer language, commitments, objections, decisions, and follow-up evidence.
- `document_store`: account plans, mutual action plans, discovery notes, enablement assets, business-case sources, and source-of-truth docs.
- `spreadsheets`: Sheets, spreadsheet models, Excel files, CSV exports, owner trackers, account lists, and forecast or planning tables.
- `external_messaging`: customer asks, promised follow-ups, scheduling context, attachments, and engagement signals.
- `internal_messaging`: account-team coordination, blockers, source routing, internal follow-up drafts, and escalation context.
- `data_enrichment`: company, contact, firmographic, technographic, and market-signal details when CRM or user-provided lists are thin.
- `agreements`: contracts, e-signature status, approval routing, agreement lifecycle context, and deal paperwork signals.

Use exactly these statuses:

- `active`: setup found or installed one or more source routes and wrote either route-level `routes[]` entries or backward-compatible `source_kind`, `skill_surface`, and route details when available. This is FYI only. Do not perform an eager read just to prove an installed source works; attempt active sources only when a workflow needs them.
- `needs_confirmation`: setup found multiple plausible source tools, an installable related plugin that needs approval, or a selected source preference that still needs a route recorded. Ask the user which source to prefer or whether to install the plugin when needed. If the selected source is an installed plugin, app, or connector, write the chosen route and let the workflow's first real read handle auth, query, or schema failures. If the selected source is missing, use plugin setup before connector/app setup and manual fallback.
- `missing`: setup found no matching installed plugin, connector, or app. Explain what Sales workflows will be weaker without it and list concrete IT/admin options, such as installing the plugin/connector, authorizing the app for Codex, or using a manual/exported fallback for now.
- `deferred`, `skipped`, `declined`, or `unavailable`: setup did not choose an active route. Include practical impact and the next best plugin/app/connector/manual path when useful. Treat failed setup, pending plugin visibility, temporary unavailability, and `skipped_for_now` as retryable while related plugins may become available later. Treat `declined` as a current-workflow suppression unless the user explicitly saves a future `do not use` rule.

Recommended state shape:

```json
{
  "connector_confirmation": {
    "calendar": {
      "status": "active",
      "preferred": "Google Calendar",
      "confirmed_at": "2026-05-23T00:00:00Z"
    },
    "document_store": {
      "status": "active",
      "routes": [
        {"preferred": "Google Drive", "source_kind": "plugin"},
        {"preferred": "Notion", "source_kind": "plugin"}
      ]
    },
    "crm": {
      "status": "needs_confirmation",
      "candidates": ["Salesforce", "Agentforce Sales", "HubSpot"]
    },
    "meeting_notes": {
      "status": "missing",
      "options": ["Zoom", "Granola", "Otter.ai", "Fireflies", "Outreach", "Rox"]
    }
  }
}
```

Do not write `available`, `verified`, `checked`, `installed`, or automatic `blocked` as durable source status. If the user chooses a default source or says to avoid one in the future, save that user-approved preference in `user-context.md`.

## Onboarding Behavior

First-run onboarding should not perform connector reads before the first orientation message. After the user approves setup, run source setup/search, call `functions.list_available_plugins_to_install` once, prefer related plugins over raw app/connector routes, and write resolved routes for each category to `connector_confirmation`. Do not preflight-read installed or active connectors merely to prove they work. Active sources are informational only; do not ask the user to confirm every source when setup finds clear active installed plugins, apps, or connectors that can coexist in the same category. Ask for help only when there are multiple mutually exclusive plausible source tools, an installable related plugin needs approval, no source was found, or IT/admin action may be needed. For missing or connector-covered sources, use plugin setup before connector/app setup and manual fallback. Introduce Sales, confirm active/missing sources, set up Sales Company Research and Sales Tips in the initial automation step, then let the user choose the first guided hero workflow from Prepare For Meeting, Follow Up After Call, and Prioritize Accounts. Offer Sales Daily Meeting Prep later after the user has tried and iterated on Prepare For Meeting. When a guided workflow needs a source, the focused workflow tries the configured source route at that moment and handles plugin install, auth, connection, skip, or manual fallback in context.

During onboarding, explain at a high level that Sales works best when it has active workflow sources plus saved source pointers and preferences. Ask for memory/resource pointers after the first useful output, not before the user has seen value.
