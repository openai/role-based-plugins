# Workflow Source Resolution

Use this reference only during ordinary Public Equity Investing workflows after `skills/user-context/scripts/user_context_preflight.py` returns `source_category_plan`. Source setup remains owned by `skills/user-context/references/source-category-runtime.md`.

Resolve only the categories needed for the current workflow. Prefer a user-named source first, then an active saved `configured_route`. Attempt the smallest useful native read only when the workflow needs that source. If a route needs authentication, connection, entitlement, or setup, state the practical limitation and continue from prompt context, active artifacts, pasted or exported material, and public sources when the workflow can still be useful. Do not inspect unrelated categories, run broad source setup, write connector readiness, or create, read, migrate, or update `category-state.json`.

Treat named providers, internal research stores, calendars, email, messaging, document stores, and portfolio systems as callable only when the runtime exposes a scoped route. Otherwise request a user-provided export or use a clearly labeled fallback. A configured `.app.json` entry is not proof of availability or entitlement.

## Provider Guides

Load a provider guide only after the current workflow attempts a category, selects that provider as its concrete route, and confirms the scoped route is callable. Do not load provider guides merely because `.app.json` declares the dependency or the source-category plan names a preferred provider.

- If the selected callable route is Daloopa, load `skills/public-equity-investing/internal-support/daloopa-provider-guide/INTERNAL.md`.
- If the selected callable route is Quartr, load `skills/public-equity-investing/internal-support/quartr-provider-guide/INTERNAL.md`.

## Categories

- `company_filings_ir`: filings, IR materials, reported financials, and disclosures.
- `earnings_transcripts_presentations`: transcripts, presentations, events, and management commentary.
- `internal_research`: internal notes, expert context, research, and team discussions.
- `portfolio_models_trackers`: portfolio context, watchlists, models, and thesis trackers.
- `market_data_estimates`: market data, consensus, estimates, ownership, positioning, and provider exports.
