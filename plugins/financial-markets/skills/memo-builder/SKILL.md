---
name: memo-builder
description: Use when drafting or reviewing formal public-equity investment memos. Do not use for live trade construction or credit-first memos; use long-short-pitch or Credit Markets as appropriate.
---

# Memo Builder

## Skill Configuration

### User Context Preflight

Before searching connectors, retrieving evidence, or drafting output, run `python3 skills/user-context/scripts/user_context_preflight.py` with the shell working directory set to this plugin's root, and follow the returned `saved_context`, `source_category_plan`, and `next_action`. Set the working directory before the first attempt; do not probe alternate relative paths. Missing context must not block the requested workflow. Do not initialize state or run onboarding during ordinary workflow work.

If `next_action.id = "offer_orientation"` and the parent router has not already handled it, complete the requested work first and append its one-line optional setup offer once.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Use `source_category_plan` lazily and attempt only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`.

## Deliverable Intake

Apply the presentation-surface precedence in `../../shared/deliverable-intake-policy.md`. This workflow's natural artifact is a polished standalone HTML investment memo. Do not choose chat-only output unless the user explicitly requests a lightweight response.

Before source gathering or analysis for a new standalone reader-facing hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Goal

Produce decision-grade Public Equity Investing memos that are evidence-led, numerically auditable, and ready for PM, committee, client, or internal research review.

This skill owns formal written artifacts and synthesis. It does not own raw trade construction; use `long-short-pitch` first when the user needs variant perception, trade expression, sizing considerations, add/trim/exit/cover rules, or pair-trade mechanics.

## Use When

Use this skill when the user asks for:

- IC memo, investment memo, committee note, client memo, research note, PM update, or equity event note
- memo rewrite, upgrade, shortening, pressure test, or QA review
- synthesis of outputs from models, comps, scenarios, earnings, event-driven equity, balance-sheet-risk, or long/short pitch work
- committee-ready framing with source posture, valuation, scenarios, risks, catalysts, open items, and recommendation

Credit-first memos route out: Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis. This skill may synthesize Credit Markets output only when the final deliverable is a common-equity or listed-equity memo.

Do not use when the user asks to "pitch this long/short," "make this investable," "build a pair trade," "what is the variant perception," or "what would make us cover/add/trim." Use `long-short-pitch`.

## Artifact Boundary

- Default deliverable: produce the full decision-grade memo. For a substantive investment committee memo, buy-side investment memo, or reusable/source-heavy public-equity memo, produce a polished standalone HTML investment committee memo following `../../shared/html-artifact-standard.md` unless the user requests another surface, a quick/no-file answer, `.docx`, or a standardized dashboard.
- For other substantial written memo modes, produce a polished standalone HTML memo or report appropriate to the requested audience, following `../../shared/html-artifact-standard.md`, unless another surface is selected.
- Chat can be the presentation surface only when the user explicitly requests a lightweight response; Markdown is formatting, not the deliverable contract.
- This local skill does not ship native `.docx` or `.xlsx` templates/scripts. Route workbook-backed outputs to the model/workbook skills.
- Create `.docx` or `.xlsx` artifacts only when the user explicitly asks and an appropriate document/spreadsheet tool, template, or user-provided file is available.
- If no document/template support is available, provide the memo in chat or HTML report form and keep JSON/Markdown support files out of the lead handoff unless explicitly requested.
- Use `dashboard-builder` only when the user explicitly asks for a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render. On that path, load `references/DASHBOARD_PACK.md`; `memo-builder` owns memo synthesis, narrative architecture, evidence selection, and audience framing, while `dashboard-builder` owns the standardized shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input.

## Source And Mode Selection

Use the strongest available source tier and label assumptions, stale data, proxies, and unsupported figures. Load `references/source-policy.md` for source priority and minimum inputs.

Default to the full memo mode that best fits the decision. Use a compressed mode only when the user explicitly asks for a `summary`, `short`, `quick`, `one-page`, `brief`, `TL;DR`, or review-only output:

- `ic-note`
- `investment-memo`
- `event-driven-committee-note`
- `pm-update`
- `client-research-note`
- `qa-review`

Load `references/memo-modes.md` for mode selection and `references/output-contracts.md` for section-level contracts.

## When To Invoke Support

Load `shared/support-layer-routing-contract.md` for source/data/QC/style support. Use `financial-source-of-truth` before final claims, metrics, citations, or management assertions. Use `financials-normalizer` before building from messy financials, consensus exports, guidance tables, segment data, share count, net debt, or capital allocation inputs. Use `excel-data-cleaner` before relying on malformed tables or mixed fiscal periods. Use `deck-report-qc` before circulating a memo-derived deck/report or source-heavy packet, and use `style-guide-adapter` only after substance is locked. These support artifacts stay secondary; `memo-builder` owns the memo and investment judgment.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: evidence, model/valuation, risks and catalysts, narrative synthesis, and memo QA. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Default Memo Spine

Use this full spine unless another memo mode is clearly requested:

1. `Recommendation / Decision Ask`
2. `Executive Summary`
3. `Thesis and Evidence`
4. `What Must Be True`
5. `Valuation / Scenario Work`
6. `Risks, Disconfirmers, and Mitigants`
7. `Catalysts and Monitoring`
8. `Implementation Considerations`
9. `Open Items / Data Requests`

If the memo is screen-grade because source context is thin, say so before the first metric table.

## Handoffs

Upstream inputs this skill can synthesize:

- source/evidence: `financial-source-of-truth`, `financials-normalizer`, `company-tearsheet`
- models/valuation: `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `scenario-sensitivity-generator`
- earnings/research: `earnings-preview`, `earnings-deep-dive`, `initiating-coverage`
- trade/event/risk: `long-short-pitch`, `event-driven-analyzer`, `portfolio-risk-management`
- monitoring and QC: `thesis-tracker`, `catalyst-calendar`, `deck-report-qc`, `style-guide-adapter`

Use `sector-context-overlay` only when issuer economics clearly match a supported sector; load `references/sector-overlays.md` only for memo-specific sector framing.

## Rendering And Compression

- Lead with the decision ask or conclusion.
- For a standalone HTML investment committee memo, make the first-read layer a compact memo opening: recommendation / decision ask, decision hinge, what is priced in, valuation or scenario skew, and any source limitation that changes the action. Do not repeat the same recommendation across a dashboard-style hero, summary tile, and full decision panel.
- Keep background proportionate; preserve recommendation, scenario/downside, source posture, catalysts, monitoring, and open items.
- Use tables only when they compress decision-critical information.
- For long memos, put source caveats and open items near the end, but do not bury data limitations that affect the recommendation.
- Sparse source context should produce a full screen-grade memo skeleton with assumptions, missing evidence, and upgrade path, not a shortened memo.
- State source readiness in decision-specific terms when evidence supports only one direction of action, such as `sufficient to decline initiation today; insufficient to support initiation`, rather than using broad readiness labels that imply the entire underwrite is decision-grade.
- Keep citations traceable but readable in HTML: do not fragment tickers, prices, EPS ranges, percentages, dates, multiples, or metric labels into separately linked tokens.
- Before delivering standalone local HTML, visually inspect the opening viewport and decision-critical downstream sections through local headless-browser screenshots, not the in-app Browser plugin. Check desktop and narrow-screen legibility, clipping, citation density, whitespace, and that the page does not acquire horizontal overflow.

## QA

Before finalizing, verify:

- recommendation and decision hinge are clear
- material numbers are sourced, model-derived, or explicit assumptions
- downside is mechanistic, not generic
- `what must be true` items are measurable
- valuation/pricing/recovery support matches memo type
- a multi-year valuation using forward-period earnings and an exit or terminal multiple shows either present value using an explicit discount-rate / required-return assumption or annualized return / IRR versus a stated hurdle; undiscounted terminal price appreciation alone does not support initiation
- disconfirmers and monitoring triggers are present
- trade-construction asks are handed to `long-short-pitch`

Load `references/quality-workflow.md` for the full quality bar and workflow.

## Public Equity PM Judgment Layer

For substantial memos, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Memo modes to support: `buy-side-investment-memo`, `pm-update`, `sell-side-research-note`, `client-research-note`, `etf-index-diligence-note`, and `public-equity-diligence-memo`.

Required PM judgment:
- Every full memo needs a decision hinge, what must be true, what is priced in, downside mechanism, measurable disconfirmers, source posture, and action discipline.
- Build-from-scratch memo mode must include an intake checklist, source packet requirements, first-pass house view, variant wedge, priced-in debate, estimate path, valuation/skew, downside mechanism, catalysts, disconfirmers, action rules, and exact evidence needed to upgrade from screen-grade to decision-grade.
- Sell-side notes need rating/target-price debate, estimate revision bridge, variant versus Street, risk-to-rating, and compliance-safe wording.
- ETF/index notes need mandate, methodology, holdings/weights, tracking-error or benchmark implications, factor exposure, liquidity, and rebalance/corporate-action risk.
