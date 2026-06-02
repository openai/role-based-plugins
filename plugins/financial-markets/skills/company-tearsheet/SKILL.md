---
name: company-tearsheet
description: Use when creating source-backed public issuer tearsheets. Do not use for private diligence, fund diligence, vendors, or market maps.
---

# Company Tearsheet

## Skill Configuration

### User Context Preflight

Invoke `public-equity-investing:user-context` in preflight mode by loading `skills/user-context/SKILL.md` from the plugin root and running `python3 skills/user-context/scripts/user_context_preflight.py` with the shell working directory set to this plugin's root before searching connectors, retrieving evidence, or drafting output. Set the working directory before the first attempt; do not probe alternate relative paths. Use the returned envelope as authoritative for `saved_context`, `source_category_plan`, and `next_action`. Apply relevant `saved_context`. Do not read or reinterpret raw plugin state files unless preflight fails or the user explicitly asks for raw state inspection. Missing, malformed, or uninitialized context must not block tearsheet work.

During ordinary tearsheet work, do not initialize state or run onboarding or broad source setup. If `next_action.id = "offer_orientation"` and the parent router has not already handled it, complete the requested work first and append the router's one-line optional setup offer only once. Leave other onboarding steps to the explicit `user-context` flow.

### Source Resolution

Use `source_category_plan` from preflight to resolve only catalogued source categories needed for the current tearsheet. Prefer a user-named source first, then an active saved route when available. Attempt the smallest useful native read only when the workflow needs that source. If a route needs auth, connection, or setup, state the practical limitation and continue from prompt context, active artifacts, pasted or exported material, and public sources when the tearsheet can still be useful. Do not inspect unrelated source categories, run broad source setup, write connector readiness, or create, read, migrate, or update `category-state.json`.

The source-category plan covers the catalogued Public Equity Investing sources below. Use `references/source-and-evidence.md` for the broader evidence hierarchy and freshness rules.

### Workflow Sources

When this skill uses a source category, use it for the following information. These are semantic source categories, not fixed connector names.

- `company_filings_ir`: filings, IR materials, reported financials, and issuer disclosures needed for the factual baseline.
- `earnings_transcripts_presentations`: transcripts, presentations, events, and recent management commentary when they materially change the issuer read.
- `internal_research`: internal notes, expert context, prior research, and team discussions when they materially improve the baseline.
- `portfolio_models_trackers`: portfolio context, watchlists, models, and thesis trackers only when they materially change the investor lens or downstream route.
- `market_data_estimates`: market data, consensus, estimates, ownership, positioning, and provider exports needed for valuation context and freshness checks.

## Deliverable Intake

Apply the presentation-surface precedence in `../../shared/deliverable-intake-policy.md`. This workflow's natural artifact is a polished standalone HTML issuer tearsheet. Do not choose chat-only output unless the user explicitly requests a lightweight response.

Before source gathering or analysis for a new standalone reader-facing hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. When the user explicitly requests HTML for a tearsheet, that resolves the presentation surface to a polished standalone HTML tearsheet; ask only remaining material choices and do not treat HTML as a request for a standardized dashboard. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose

Create a source-backed baseline profile for a public issuer so downstream Public Equity Investing workflows start from the same factual view. The default artifact is an issuer baseline by design, not a memo, model, pitch, or recommendation.

Use this before or inside comps, DCF, 3-statement, earnings, model update, long/short pitch, memo, meeting-prep, thesis tracker, risk/sizing, hedge, event, catalyst, equity-risk credit-signal, and deck/report workflows when a fast public profile is needed.

Produce a compact polished standalone HTML tearsheet following `../../shared/html-artifact-standard.md` unless another format takes precedence; let the issuer's business model and requested review lens determine the hierarchy. Use chat only when the user explicitly requests a lightweight response. If the work expands into detailed thesis construction, scenarios, underwriting, or a full investment view, route the baseline into `initiating-coverage`, `memo-builder`, or the relevant owning workflow. Use `dashboard-builder` only when the user explicitly asks for a standardized dashboard, reusable dashboard template, or structured payload-driven render.

## Do Not Use

- Private company, sponsor-owned asset, private fund, LP/GP diligence target, vendor, customer, or commercial counterparty.
- Fund/asset-manager diligence profiles.
- Market maps, buyer lists, private-company sourcing screens, or diligence workplans.
- Full memos, valuation models, trade pitches, or investment recommendations.
- Do not compress a broader investment, earnings, comps, credit, or pitch request into a tearsheet; route to the owning full-analysis skill.

## Non-Negotiables

- Preserve source materials and user work.
- Prefer user-provided context/files, callable runtime apps/connectors when actually available, primary sources, user-provided provider exports, credible secondary sources, then labeled assumptions.
- Use `financial-source-of-truth` for source hierarchy, stale-data checks, citations, conflicts, and fact/assumption discipline.
- Use `financials-normalizer` or `excel-data-cleaner` first when source financials/tables are messy.
- Never invent missing facts, metrics, ratings, debt, valuation, ownership, customers, or KPIs.
- Label facts, calculations, estimates, management claims, user adjustments, assumptions, missing fields, and confidence.
- In a reader-facing artifact, translate internal evidence labels into plain investor language such as `Reported`, `Company-defined`, `Derived`, or `Not yet sourced`; retain exact evidence labels only in support data or when specifically requested.

## Workflow

1. **Classify profile.** Choose `public_company`, `equity_issuer_profile`, or `public_sector_peer`; identify downstream use case.
2. **Build source inventory.** Track `source_id`, source name/type, owner/provider, as-of date, retrieved-at date, period, location, freshness, and notes.
3. **Extract profile-critical facts.** Use only source-supported business, segment, geography, leadership, metrics, valuation, capital structure, KPI, recent event, risk, and evidence-gap fields relevant to the use case.
4. **Label evidence and confidence.** Use labels from `references/source-and-evidence.md` and confidence values `high`, `medium`, or `low`.
5. **Compose tearsheet.** For an HTML tearsheet, build a compact issuer baseline with an investor read, four or five decision-useful metrics, core business and earnings drivers, valuation context, concise catalysts/risks, material evidence gaps, source notes, and recommended next analytical route.
6. **Keep scope at baseline.** Do not allow a live event, long missing-data register, extensive diligence questions, or scenario work to overwhelm the issuer baseline. Escalate to an owning full-analysis workflow when that additional work becomes central.
7. **Run QC.** Confirm identity, periods, units, currency, sources, confidence, stale/conflicting data, derived-calculation support, and reader-facing legibility.

## Deterministic Helpers

```bash
python scripts/validate_tearsheet_json.py path/to/tearsheet.json
python scripts/build_tearsheet_markdown.py path/to/tearsheet.json output.md
```

The helpers validate/render structured inputs. They do not fetch data or replace source review. Raw JSON and generated Markdown are support or renderer-input artifacts unless the user explicitly asks for those formats.

For standardized dashboard handoffs only, use `references/DASHBOARD_PACK.md`. `company-tearsheet` owns the issuer baseline and source confidence; `dashboard-builder` owns the shared shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown support files behind the HTML artifact unless explicitly requested.

## When To Invoke Support

Load `shared/support-layer-routing-contract.md` when support services are needed. Use `financial-source-of-truth` for source hierarchy, stale data, conflicts, and fact/assumption labels; use `financials-normalizer` or `excel-data-cleaner` before using messy financials, ownership tables, market/security data, or KPI exports. Support artifacts stay secondary to the tearsheet, dashboard/report, or downstream owning workflow.

## Output Contract

User-facing response:

1. Tearsheet created: entity, profile type, scope, sources, as-of date.
2. Key takeaways: 3-5 bullets with estimates/assumptions marked.
3. Metric table: decision-useful metrics with period, units, source, confidence.
4. Risks/gaps: stale data, conflicts, missing facts, evidence flags.
5. Recommended next step or downstream handoff.

For a standalone HTML tearsheet, keep the first-read structure compact:

1. Investor read and four or five high-signal metrics.
2. Earnings-driver table or compact driver cards.
3. Use the visible heading `Valuation Context` or `Trailing Valuation Snapshot` when only historical or derived multiples are supported. Do not include `Debate` in the heading unless forward estimates, peer comparisons, target-price evidence, or explicit market expectations are sourced.
4. Concise catalyst-and-risk matrix.
5. Material evidence gaps, source ledger, and next analytical route.

Do not expand the tearsheet into a full initiation report, long diligence-question set, scenario package, or recommendation merely because HTML space is available.

## HTML Guidance

When HTML is requested or selected, load `../../shared/html-artifact-standard.md` and apply these workflow-specific rules:

- Lead with the factual investor read and the core earnings-driver question; the issuer baseline and earnings drivers are the primary objects.
- Prefer four or five distinct metric tiles, one earnings-driver comparison object, one compact valuation-context object, and one catalyst/risk object over repeated dashboard panels.
- When a current transaction, rumor, regulatory item, or other live event is material but not the requested focus, feature it in the investor read and catalyst/risk section and identify missing primary evidence in the evidence-gaps block. Do not thread it through earnings drivers, valuation, and multiple summary panels unless it directly changes those analyses.
- Keep missing ownership, positioning, factor, or consensus fields visible through a compact evidence-gaps block; do not render a long table of unsourced fields unless those fields are the requested diligence focus.
- Render visible evidence posture in plain language rather than internal labels such as `fact_source_reported` or `missing_required_source`.
- Keep citations traceable but readable: do not fragment tickers, years, dates, numeric ranges, metric names, or product labels into separately linked tokens.
- Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, and iterate on hierarchy, density, clipping, citation rendering, and whitespace before delivery.

## Reference Map

- `references/source-and-evidence.md`: source hierarchy, citations, stale-data, labels, conflicts.
- `references/profile-templates.md`: one-page and profile-specific templates.
- `references/metric-library.md`: metric categories, `sector-context-overlay` guidance, KPI guidance.
- `references/quality-checks.md`: profile QC checks.
- `references/integration-guide.md`: Public Equity Investing handoffs.

## Public Equity PM Judgment Layer

For substantial tearsheets, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Use-case modes: `long_only_baseline`, `hf_baseline`, `sell_side_coverage_starter`, `etf_index_constituent_profile`, `public_diligence_baseline`.

Required PM judgment:
- Keep the tearsheet factual, but make the next analytical route obvious.
- Include investor-useful fields when available: market cap, enterprise value, float, ADV/liquidity, index membership, ETF/passive ownership and flow relevance, top holders, short interest, borrow/crowding, factor exposure, ownership concentration, governance, capital allocation, sell-side coverage, consensus setup, balance-sheet risk, and key operating KPIs.
- Always identify unavailable or stale ownership, positioning, borrow, liquidity, factor, and consensus fields with an as-of/source requirement rather than silently omitting them. In reader-facing HTML, consolidate non-central missing fields into a compact evidence-gaps block instead of displaying a long low-information register.
- Do not turn a tearsheet into a recommendation; route investment decisions to initiating coverage, memo-builder, long-short-pitch, or thesis-tracker.
