# Public Equity Investing Source Category Runtime

Use `skills/user-context/plugin-author-config/source-category-config.json` from the plugin root as the static catalog of Public Equity Investing source categories, labels, and preference hints. The catalog is a routing aid, not proof that a plugin, app, connector, or manual source is usable for the current user.

## Ownership

- `.app.json` declares app and connector dependencies the plugin can request. It does not prove installation, authorization, preference, or readability.
- `skills/user-context/plugin-author-config/source-category-config.json` owns static category ids, labels, and preferred plugins or apps.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` owns durable user-approved source preferences, source-of-truth pointers, and "do not use" rules.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json` owns operational setup confirmations under `connector_confirmation`.
- Do not create, read, or migrate `category-state.json`.

## Read-Only Preflight

Preflight is a reader. Its `source_category_plan` returns static routing hints, saved setup confirmations, and unresolved setup gaps. It must not inspect apps, connectors, plugins, or `.app.json`; choose a plugin, app, connector, or manual route; claim readiness; perform proof reads; or write state.

## Explicit Setup

Source route selection belongs in the user-approved Source Setup onboarding step, an explicit source-setup turn, or later workflow-time repair. Do not inspect setup surfaces before the user opts in.

During one setup pass:

1. Start from unresolved categories in preflight `source_category_plan`.
2. Read the session `Available plugins` and `Available skills` blocks. Call `functions.list_available_plugins_to_install` once and reuse the result for every category in the pass. Load `.app.json` only to map preferred app names to declared connector ids.
3. Prefer a related installed plugin with visible plugin-owned skill or tool surface, then an installable related plugin, then an exposed app or connector, then manual or exported context.
4. Ask before installing or authorizing anything. Ask the user to choose only when multiple plausible routes tie, an installable plugin needs approval, no suitable source is exposed, or IT/admin help may be required.
5. Write the selected operational route under `onboarding-state.json` `connector_confirmation`. Do not write source setup state to `user-context.md`.

Use `status: active` only when the selected plugin, app, or connector surface is exposed clearly enough to attempt later. This is setup-only evidence, not a readiness claim. Use `needs_confirmation`, `missing`, `deferred`, `skipped`, or `unavailable` when the route is not active. Include `source_kind` and compact plugin, app, connector, or manual route details when known. Do not guess connector ids or infer active status from `.app.json`.

Do not perform connector reads merely to prove setup. If the user approves an installable candidate returned by `functions.list_available_plugins_to_install`, call `functions.request_plugin_install` with that exact candidate id and tool type. Do not call `request_plugin_install` in parallel with other tools.

## Workflow Use

Attempt actual connector reads only when the active workflow needs the source. Before telling the user that a source is ready, use the smallest safe native read-only probe for that source. A successful read is evidence for that run only, not durable connector-readiness state. When a source is unavailable, continue from pasted, uploaded, or exported context when the workflow can still produce a useful limited answer.
