---
name: review-forecast
description: Generate a forecast review with risk analysis, recommendation posture, and change detection using CRM truth, pasted or exported pipeline context, account notes, and optional meeting, email, document, or internal-message evidence.
---

# Review Forecast

Use this skill for forecast review requests such as:

- forecast my book
- generate a sales forecast with risk analysis
- show movement between snapshots
- review these forecast accounts and tell me what should stay in commit

This skill produces a structured forecast review for one seller book, team, period, pipeline view, or narrowed deal set. Optimize the default path for a fast manager-ready forecast readout: exact scope, open forecast rollup, top risk deals, keep/downgrade recommendations, evidence gaps, and practical next actions. Run deeper forensic history or enrichment only when the user asks for it, supplies comparison snapshots, or a top deal's recommendation materially depends on missing evidence. The initial review is read-only: it may draft manager notes, spreadsheet views, CRM-ready next steps, or deal-risk follow-up. Do not write CRM fields, change forecast categories, update close dates, message owners, or assign tasks unless the user explicitly approves a reviewed downstream action.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the forecast review also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the forecast review.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided, connector-visible, or explicitly inferable context to identify the forecast scope and at least one source of forecast or pipeline truth.

The skill can produce a limited forecast review from pasted pipeline tables, CSV/exported snapshots, CRM report exports, user-linked docs, account notes, or prior Sales outputs when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require one forecast scope anchor:

- [required] `owner_name` or `owner_email`
- [required] `focus_accounts`
- [required] `focus_opportunities`
- [required] a named `forecast_period`, team, book, pipeline view, or deal set that can be resolved from available context

Require one forecast truth source:

- [required] `crm` opportunity or forecast data, or sufficient `pipeline_export`, `current_snapshot`, pasted table, CRM report export, or user-linked forecast context

Require these seller-facing forecast choices:

- [required] `forecast_posture_standard`: whether the review should optimize for defending Commit, identifying Upside, or producing a conservative manager-ready forecast
- [required] `forecast_category_convention`: the team or user convention for interpreting Commit, Best Case/Upside, Pipeline, and any other forecast categories used in the source data
- [required] `amount_basis`: the amount field to use for the forecast review and downstream artifact, such as CARR/ARR, ACV, TCV, weighted amount, or the CRM primary amount

Accept when provided:

- `comparison_snapshot`
- `enrichment_mode`: `none`, `light`, or `standard`; default to `light` for a current-state forecast review and to `standard` only when the user asks for a deeper review or supporting evidence would materially change a top deal's risk call
- `include_call_evidence`
- `include_chat_signals`
- account notes, manager notes, forecast assumptions, or known deal-risk context

**Context Rules:**

- If a required scope anchor is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- If `forecast_posture_standard`, `forecast_category_convention`, or `amount_basis` is missing, first check saved Sales context, CRM metadata, manager notes, RevOps docs, forecast docs, or user-provided/exported field names for concrete defaults. If the value is still missing or only inferable, ask the user to confirm or supply it before producing the forecast review.
- Treat ambiguous company-like proper nouns, partner names, account shorthands, and opportunity shorthands as possible customer/account or deal-set anchors unless the request clearly indicates an internal-only person, product, or topic. When `crm` is available, include a bounded CRM lookup before relying on docs, notes, messages, exports, or public context alone. If CRM returns one high-confidence account/opportunity match, use it as the primary scope candidate; if multiple plausible matches remain, ask the user to choose from concrete candidates.
- Before asking the user to paste a pipeline table, CRM report export, forecast scope, or forecast convention, first try the workflow source categories that can own those missing inputs: `crm` for opportunity/forecast truth and CRM conventions, `document_store` for manager notes, forecast docs, RevOps docs, and source-of-truth pages, then `meeting_notes`, `external_messaging`, or `internal_messaging` only when they can cheaply clarify a top-deal scope or risk candidate. Manual/exported forecast data is the fallback after those categories are unavailable, empty, or insufficient.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

If no usable forecast truth source is available from connectors, exports, pasted context, or linked user context, stop and ask for one. Do not invent forecast posture from account anecdotes alone.

**Input Request Format Examples:**

```md
Which forecast, book, period, or deal set should I review?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

```md
Before I review it, please confirm these forecast choices:

1. **Forecast posture:** defend Commit, identify Upside, or conservative manager-ready?
2. **Category convention:** how should I interpret Commit, Best Case/Upside, and Pipeline?
3. **Amount basis:** should I use CARR/ARR, ACV, TCV, weighted amount, or the CRM primary amount?

I found `{source-derived default}` for `{field}`. Correct anything off, or say `use those defaults`.
```

Proceed with a sensible default only when the active thread, saved context, CRM view, user-provided export, or prior Sales artifact clearly identifies the forecast scope, includes enough forecast truth to review, and resolves the required forecast choices above.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: opportunity truth, amount, stage, forecast category, close date, owner, account, next step, activity fields, historical snapshots, current pipeline views, CRM report exports, and user-approved CRM conventions.
- `meeting_notes`: recent customer-call evidence, stakeholder coverage, decision process, urgency, objections, next steps, and timing signals.
- `document_store`: account plans, forecast docs, manager notes, close plans, deal-desk trackers, approval trackers, and source-of-truth pages about forecast conventions.
- `external_messaging`: recent customer email or external-message evidence that materially changes timing, engagement, stakeholder, or risk confidence.
- `internal_messaging`: blocker, approval, manager, deal-desk, product, legal, procurement, or account-team signals when the user wants internal context.
- user-provided context: pasted pipeline tables, CSV/exported snapshots, CRM report exports, account notes, manager notes, forecast assumptions, prior Sales outputs, and linked context that can seed or constrain the review.

Source obligations by intent:

- `crm` opportunity/forecast data or a user-provided/exported forecast snapshot is required as forecast truth. When named customer/account/opportunity anchors are supplied, inferred, or confirmed, use CRM when available before optional evidence lanes. Meeting notes, docs, email, and chat are evidence lanes, not substitutes for missing opportunity truth.
- Use `meeting_notes`, `external_messaging`, `internal_messaging`, and `document_store` only when the user asks for enrichment, the forecast truth is thin, or a top deal's recommendation materially depends on missing customer/account evidence.
- When optional evidence lanes are checked and produce no relevant result, report `checked/no match` only for lanes that would affect confidence in a top recommendation. Do not prolong the default path to exhaust every lane.

Authority and gaps:

- Prefer `crm` or a user-provided/exported pipeline snapshot as the forecast truth source. Treat meeting notes, docs, email, and chat as evidence lanes, not substitutes for missing opportunity truth.
- Do not let meeting notes, docs, email, chat, public context, or third-party enrichment override CRM-owned forecast, account, or opportunity truth.
- Treat optional evidence lanes as confidence and risk context only; do not use them to change forecast posture unless the forecast truth source supports the underlying deal state.
- Continue from sufficient manual or exported context when `crm` is unavailable, and label that the review is based on user-provided/exported forecast data.
- If both `crm` truth and manual/exported forecast data are unavailable, stop and report the missing source of truth.
- Treat `meeting_notes`, `document_store`, `external_messaging`, and `internal_messaging` as optional enrichment lanes. If they fail or are unavailable, continue when the forecast truth source is sufficient and label the missing lanes explicitly.
- Use saved Sales user context for company-specific forecast category interpretation, close-date norms, stage exit criteria, approval rules, and source preferences only when read through `sales:user-context`.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the review-forecast experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Review Forecast
This skill helps inspect forecast posture, risk, pipeline quality, and next actions for a book, team, period, or narrowed deal set. It can use CRM, account notes, meeting/call evidence, Slack, docs, and user-provided forecast assumptions. It produces deal risk, movement, evidence gaps, forecast posture, and practical next actions.

Definitions:
- Commit: deals or revenue expected with high confidence, using the team's sourced forecast convention when available.
- Hygiene signal: a data or process issue, such as stale close date or missing next step, that may weaken forecast confidence.
- Concentration risk: too much forecast confidence depending on one deal, owner, stage, segment, product, or timing bucket.

```

Starter prompts:

- Primary default prompt: `Review a forecast for risk and next actions.`
- `@Sales review my forecast for this month and flag the biggest risks.`
- `@Sales look at these committed deals and tell me what could slip.`
- `@Sales review the enterprise forecast and suggest the next actions by deal.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Review Forecast next-step behavior and action text. Onboarding, spreadsheet creation, draft creation, CRM writeback, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the forecast-review continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `review-forecast` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/writing/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the forecast readout** | The first substantive forecast review has just been produced. | `Anything you'd change in the forecast readout before we make it operational?` |
| **2. Review the revised forecast readout** | The user asked for any change to the review, including a posture adjustment, risk wording, rollup detail, evidence note, source adjustment, or formatting tweak. Make the change in chat first. | `Anything else you'd change? If that looks good, want me to move the forecast, risks, and assumptions into a spreadsheet so it is easier to adjust and build on?` |
| **3. Prepare the projection artifact** | The user accepts the review, says no changes are needed, says a revision looks good, or asks to operationalize the forecast. | Prefer offering a spreadsheet for projections, risk rollups, assumptions, and scenario adjustments; when a spreadsheet would not help, offer manager notes, CRM hygiene update text, risk follow-up, or an owner/action tracker. |
| **4. Review the spreadsheet, notes, or update draft** | A spreadsheet, manager note, CRM-ready update, or risk tracker exists, or the user asks to change it. | `Anything you'd change before I save, share, or write the approved forecast updates?` |
| **5. Share, save, or write approved forecast action** | A reviewed spreadsheet, note, tracker, or update draft exists and does not need edits. | Offer the specific supported action, such as saving the spreadsheet, sharing the manager note, posting the approved risk summary, or writing approved CRM hygiene or next-step updates. Do not post, send, or write CRM changes unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the forecast readout, treat a lightweight acknowledgement as acceptance and move to `Prepare the projection artifact`. If the previous continuation offered to prepare a spreadsheet, notes, tracker, or update draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post, send, or write externally. If the previous continuation offered to share, save, or write a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Procedure

### 1. Normalize the request

- Use owner scope as the primary path unless the user explicitly names accounts, opportunities, a forecast report, a team, or a pipeline view.
- If the user names accounts or opportunities without an owner, run a narrowed override scope and say the owner-book lane was bypassed intentionally.
- Normalize fields from `references/request-schema.yaml` only when structured input validation, YAML normalization, or machine-readable field shape matters.
- For named teams, segments, books, or pipeline views that map to a canonical CRM report filter or field, use that canonical scope first and state the exact filter in `Review Scope`. For example, if a Startups forecast is represented by `Sales_Coverage_Opp__c = 'Startups'`, use that first instead of broadening across owner, account, and stamped segment fields.
- Broaden beyond the canonical scope only when the user asks for a broader book definition, saved context says the canonical field is incomplete, or the canonical query returns an implausibly empty/thin result. When broadening, label the broader filter and avoid comparing it as if it were the canonical forecast.
- Default `enrichment_mode` to `light` for ordinary team/period/current-state reviews; use `standard` only when the user asks for a deep review or when missing supporting evidence would materially change a high-value recommendation; use `none` when the user asks for forecast-data-only review.
- If neither owner scope nor narrowed deal scope is present, follow `Required Inputs` and ask for the missing scope anchor.
- If any of `forecast_posture_standard`, `forecast_category_convention`, or `amount_basis` remains unresolved after source/context checks, follow `Required Inputs` and ask for the missing forecast choice before producing the review.

### 2. Resolve forecast truth

- Prefer `crm` for opportunity truth and forecast comparison.
- If `crm` is unavailable, continue with sufficient CSV exports, CRM report exports, pasted pipeline tables, user-linked forecast docs, `current_snapshot`, or `pipeline_export`.
- If the review uses user-provided/exported data rather than live `crm`, state that in `Review Scope`.
- If current versus prior coverage is partial, label that directly.
- If data is too thin for posture changes, downgrade to a risk-only readout rather than pretending to know the forecast.

### 3. Collect bounded raw data

Normal CRM fast path:

1. Run only the minimum schema discovery needed to identify scope, amount, forecast, stage, owner, close-date, next-step, activity, and risk fields. Skip current-user and account-object discovery unless the scope is "my book" or account-level fields are needed.
2. Gather current open deals in the requested period using the canonical scope filter when one exists.
3. Build the open forecast rollup first, normally by forecast category and optionally stage: deal count, CARR or primary amount, and expected forecast amount.
4. Inspect detail rows only for the highest-value, highest-risk, stale, or materially changed opportunities.
5. Gather prior snapshot rows only when the user supplied a comparison snapshot, a named CRM forecast snapshot/report is available, or the user explicitly asks for movement.

Rules:

- Keep the raw evidence set bounded and explicit.
- Use aggregate rollups as the backbone of the review, then layer risk commentary under the rollup.
- For a first-pass forecast review, do not run OpportunityHistory or broad historical queries just to create a movement narrative. If no prior snapshot was supplied or resolved, say that true forecast movement is unavailable and use current-state risk and hygiene signals instead.
- If OpportunityHistory is used without a prior forecast snapshot, label it as CRM field history, not forecast-snapshot movement.
- When risk coverage depends on unavailable or thin signals, name those missing signals before making a recommendation.
- Do not interpret company-specific forecast categories, stage gates, or commit/upside norms beyond source-backed user context, CRM metadata, manager notes, RevOps docs, or user-provided guidance.

### 4. Run bounded enrichment

- Use `meeting_notes` for recent customer-call evidence only when it materially changes risk or confidence, especially for the top one to three uncertain deals.
- Use `external_messaging` for customer engagement, timing, stakeholder, or blocker signals only when it materially changes risk or confidence.
- Use `internal_messaging` for blocker, approval, manager, deal-desk, or product signals when the user wants internal context or when saved context says internal signals are expected for forecast review.
- Use `document_store` for account plans, forecast notes, close plans, approval trackers, or process docs when they materially sharpen the review.
- Do not enrich every deal by default. Complete the CRM or exported-data forecast readout first, then offer or run a targeted enrichment pass for the few deals where support evidence would change the recommendation.
- Do not broaden enrichment after a required anchor clarification. Resolve the anchor first.

### 5. Evaluate risk and posture

Evaluate each material deal across:

- clear next steps;
- timing credibility;
- stakeholder coverage;
- decision-process visibility;
- proof of urgency;
- recent customer engagement;
- data freshness.

Flag hygiene signals when supported, such as missing next steps, close dates that no longer look credible, stale engagement, and meaningful stage, amount, forecast-category, or timing changes.

Flag portfolio-level concentration risk when too much forecast posture depends on one stage, owner, segment, account, product, or timing bucket without clear next actions.

Use simple labels such as `low`, `moderate`, and `high` risk rather than false precision. Distinguish between sourced risk signals and directional inferences.

### 6. Build recommendation changes

- Compare current and prior snapshots when available.
- Include a concise `What Changed` subsection when the user supplies both current and prior snapshots.
- Recommend posture changes only when the evidence supports the change.
- Phrase unsupported posture changes as questions or follow-up checks, not recommendations.
- Keep forecast-category, stage, amount, and close-date changes draft-only unless the user explicitly asks for CRM update language; even then, draft only and do not write.

### 7. Render the forecast review

Return a structured forecast review in text or document-ready format. Do not require a custom renderer or docx pipeline.

Required sections:

1. `Review Scope`
2. `Overall Forecast Posture`
3. `Key Movements`
4. `Highest-Risk Deals`
5. `Recommendation Changes`
6. `Evidence Gaps`
7. `Follow-Up Actions`

For each important claim, show the supporting source or state that it is an inference from available data.

`Overall Forecast Posture` should usually include the open forecast category rollup for the requested scope, with deal count and the forecast's primary amount fields. `Key Movements` should include true movement only when a prior forecast snapshot or explicit comparison source exists. If there is no prior snapshot, keep the section but say that true movement was not evaluated and summarize current-state signals such as Closed Won already booked, open Commit concentration, stale May close dates, missing next steps, or large closed-lost/churn rows.

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Output Rules

- Keep the review useful for forecast decisions.
- Keep risk labels simple and defensible.
- Avoid false precision when the source data is incomplete.
- If the user supplied comparison snapshots, include what changed without implying certainty that the data does not support.
- Explain whether the review used live CRM truth, exported CRM/report data, pasted pipeline data, or another user-provided source.
- Name evidence gaps, source gaps, and confidence limits where they affect recommendations.
- Keep facts and inference separate. Label uncertain recommendations as `Likely`, `Possible`, or `Needs confirmation`.
- Do not fabricate opportunities, amounts, stages, close dates, owners, forecast categories, customer engagement, or links.
- Do not write CRM, send messages, assign owners, or update documents during the initial review. Only perform those actions after a reviewed downstream draft or update is explicitly approved by the user and the available tool supports it.
