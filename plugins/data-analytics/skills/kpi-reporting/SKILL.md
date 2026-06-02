---
name: kpi-reporting
description: "Produce leadership-ready KPI updates, scorecards, WBR/MBR/QBR summaries, target and pacing readouts, operating status narratives, and performance updates for known KPIs. Use when the work is to define KPI reporting context, validate metric definitions, present actuals versus comparison or plan, summarize validated drivers, and state implications or next actions."
---

# KPI Reporting

Use this skill to turn business or product metrics into decision-ready operating readouts for leaders and teams. The job is to define the KPI contract, report status against the right comparison and target, include validated driver context, and state the operating implication clearly.

Clarify with the user when a missing input would materially change the analytical frame or recommendation. Otherwise make a reasonable assumption, state it, and proceed.

This skill owns the KPI readout: what should be reported, how metrics should be interpreted, whether driver context is validated, and what operating takeaway follows. It does not own metric-system design, new driver investigation, or final artifact polish.

Use $metric-diagnostics when the readout needs fresh driver investigation, then return here to package the validated finding.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `data-analytics:user-context` in preflight mode by loading [data-analytics:user-context](../user-context/SKILL.md) and running its preflight script before answering, searching connectors, retrieving evidence, creating artifacts, or drafting output. Do not look for a callable MCP tool named `data-analytics:user-context`. Use the returned `data_analytics_preflight` envelope as the source of truth for saved context, source-category mapping, semantic-layer registry, onboarding/final-response obligations, and conditional guidance; use saved context and semantic layers as source-selection inputs, not as substitutes for workflow-time reads from connected or provided sources. Do not read or reinterpret raw plugin state files unless preflight fails, declares required content omitted, local shell access is unavailable, or the user explicitly asks for raw state inspection.

### Source Discovery And Verification

Use the relevant semantic layer first when one exists. Treat it as the starting map for candidate metrics, tables, joins, filters, caveats, source precedence, and known conflicts.

Do not stop at the semantic layer or the first plausible source. Search across the relevant available company source lanes, including structured data or data warehouses, dashboards, company docs, team communication, notebooks, code repositories, and other connected company knowledge or data that could change the answer.

For source-backed analytical work, always verify through live source reads. When the answer depends on data, run fresh data queries against the available structured-data sources before drawing conclusions, even when the semantic layer already names likely tables or definitions.

Use the combined evidence to determine which source controls the answer, note meaningful disagreements, and state why the selected source is authoritative.

### Source Access Guardrail

Before querying sources, building artifacts, or drawing conclusions, determine whether the answer requires a specific source of truth.

If a required source is unavailable, stop that path. Tell the user what source is needed, ask them to make it available or provide a reviewed fallback, and do not treat weaker substitutes as equivalent.

If the missing source is only optional enrichment, continue with the strongest available evidence and label the gap when it materially affects the answer.

## Workflow

### 1. Clarify The Readout Purpose

Understand who the readout is for, what conversation it supports, and what is being reported before drafting. Anchor the update in the period being evaluated, the comparison or target that makes performance interpretable, and the freshness cutoff.

Ask the user for missing context when it would help make the readout more accurate or useful.

### 2. Define The Metric Framework

Decide which metrics belong in the readout and what role each one plays before pulling numbers. If the framework already exists, confirm it and use it. If it is missing or weak, use $design-kpis before reporting.

Start with the primary KPI, then add the smallest set of supporting metrics needed to explain status. Supporting metrics can explain movement, guard against harmful tradeoffs, or show whether performance is pacing as expected.

Lead with the metric that matters most to the audience. Do not add every available cut or comparison; include the metrics and slices decision-makers actually use, plus any that materially explain this update.

### 3. Lock Metric Definitions And Sources

Confirm the KPI definition, source, time window, reporting cutoff, comparison period, and any target or pacing expectation before interpreting performance. If a target or pacing basis is missing, ask before treating one as authoritative. Use $analyze-data-quality when source quality issues could change the reported metrics.

For all KPI updates, make a focused source pass across `~~structured_data`, `~~company_docs`, `~~team_communication`, and `~~dashboards_or_bi` before drafting. Do not infer from a sparse prompt that source-backed actuals are unavailable. Use structured data for actuals, metric definitions, and comparison periods; use the other lanes for additional business context and source-of-truth guidance.

If any core definition is unclear, ask the user to clarify before making precise claims. When a metric definition changed, show comparable restated history when available; otherwise call out the break clearly.

### 4. Pull The Topline Actuals

Do not draft or render a WBR, MBR, scorecard, or KPI update from placeholders. Query or inspect connected structured-data sources for core actuals first. If actuals are blocked or insufficient, stop and say what source or access is needed unless the user explicitly asked for a template or mockup.

Reproduce the topline actual before explaining movement or driver context.

For each headline KPI, include the current value, the absolute and relative change versus the comparison period, and a short interpretation.

Call out anything that makes the current value hard to compare with the prior period before interpreting the movement, such as a tracking change, data backfill, partial outage, or missing day.

### 5. Put The Numbers In Context

Compare actuals against the context that makes performance interpretable. When a target, plan, pacing model, benchmark, historical range, or relevant peer group is defined, identify it and compare performance against it before judging status.

If the goal has a deadline, do not just report whether the metric is above or below target. Show whether it is on pace to hit the target by the end of the period. Use the provided pacing definition when available. If none is defined or found, ask the user; when proceeding with a calculated fallback, state that it was calculated and explain the method.

When useful, include absolute and percent variance to target and a red/yellow/green status. Make clear what comparison or pacing basis the status label uses.

### 6. Explain Validated Drivers

KPI updates need driver context, but driver claims must be validated before they are presented as explanations. A plausible story is not enough.

When the readout needs to explain drivers, use $metric-diagnostics to identify and validate them. If trusted reporting or prior analysis already validates the drivers, use that evidence instead of re-running the diagnostic.

### 7. Add Business Context And Operating Implications

After identifying the likely drivers, use $gather-business-context to look for business context that helps explain what happened and what it means for the readout. Let the driver analysis guide what context to look for, and connect context to the metric only when evidence supports the link.

Translate the evidence, driver analysis, and business context into the operating implication for the business. State whether the movement is concerning, what next step or action is warranted, and whether the main KPI is on track, at risk, or ahead of plan. Recommend action only when the evidence supports it; otherwise name the next validation step.

### 8. Validate The Readout

After the analysis is assembled and before shaping the final readout, use $validate-data to review whether the numbers, methodology, caveats, and evidence support the claimed status, drivers, and implications. Resolve material issues before sharing; carry remaining limitations into the readout.

### 9. Shape The Readout

Use the output shape the user requested. If they did not specify one, ask what format they want before building the readout. Common shapes include an inline written update, a document or report, a slide, or a slide deck.

After the format is selected, load `references/report-templates.md` and use the matching pattern as a starting point. Adapt it to the audience, evidence, and artifact.

Use $build-report for document or report outputs; it will handle report visuals and route chart work through $visualize-data. For inline updates, slides, or deck drafts that do not go through $build-report, use $visualize-data only when chart selection or visual QA materially affects the readout.

For slide or deck requests, use the user's requested output surface. If they want a presentation-style artifact, use $build-report to create a report artifact or HTML. If they need a native slide or deck, finalize the KPI story here, then pass the content to the appropriate presentation surface and keep the layout simple. Ask which path they want when the requested output is unclear.

## Standards

### Metric Standards

- Never present a KPI as precise when its definition, source, time window, or comparison basis is unclear.
- Make calculation logic, inclusion or exclusion rules, grain, and time treatment explicit when they affect interpretation.
- Reconcile totals and compare against prior reporting when possible.
- Do not compare periods, cuts, or targets that are not definitionally compatible. Call out definition changes, backfills, denominator shifts, or calendar effects when they affect the movement.

### Status And Pacing Standards

- Include the headline takeaway, current actual, relevant comparison, target or pacing context, driver summary, and implication unless the user asks for a narrower readout.
- Put actuals next to the target, plan, benchmark, or baseline when available so the reader can judge performance immediately.
- If a target is time-bound, show whether current performance is on pace using the provided pacing definition or a clearly stated calculated fallback.
- Keep recurring metric sections consistent across runs. If a requested section is missing because data, definitions, or validation are unavailable, explain the omission briefly.
- Use traffic-signal status only when it helps prioritize action. Pair color with text and state the basis for the status.
- Round numbers consistently, label units, and surface caveats when they change interpretation.

### Driver Standards

- Quantify drivers whenever the evidence supports it; do not use descriptive prose as a substitute for sizing the effect.
- Report the few drivers, contributors, or known non-drivers that matter for interpreting the KPI movement.
- Separate validated drivers from business context or hypotheses.
- Do not elevate business events into causes unless the timing, affected population, and measured change support the link.
- State whether the movement is broad-based or concentrated when that changes the operating implication.
- If driver evidence remains unresolved, name the uncertainty or diagnostic follow-up instead of inventing an explanation.

### Presentation Standards

- Write for executives and operators who skim: lead with the answer, then the evidence.
- Use business-readable numbers and compact formats such as `123k (+8% w/w, +19% m/m)`.
- Replace generic adjectives like `strong`, `healthy`, or `soft` with the metric evidence that justifies them.
- Keep caveats close to the claim they affect, and omit caveats that do not change interpretation.
- Use charts, tables, scorecards, or KPI cards only when they make the takeaway easier to understand and remain readable in the final delivery context.
