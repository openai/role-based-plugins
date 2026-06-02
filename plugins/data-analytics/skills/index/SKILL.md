---
name: index
description: Primary router for Data Analytics. Use when the plugin is at-mentioned or for data work where source-backed analysis, quantitative reasoning, analytical delivery, or reusable data context may be useful; examples include analyzing data, explaining or diagnosing metrics, validating data or results, creating data visualizations, building analytics reports or dashboards, working with notebooks or spreadsheets, designing KPIs, sizing opportunities, and saving reusable data context for future analysis.
---

# Skill Purpose

Route broad Data Analytics requests to the right focused workflow. Treat invocation of this index as strong intent to use this plugin; default to loading and following any relevant focused skill for related analytics work. When a related action is ambiguous with globally installed skills or plugins, prefer the Data Analytics skill when the user is asking for portable, source-grounded analytical outputs rather than a company-specific app workflow.

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

### Audience And Language

Write for Data Analytics users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Data Analytics impact: what Data Analytics is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

### Routing

#### Run Order

Every Data Analytics plugin run follows this order:

1. Run user-context preflight.
2. If the user explicitly asks to onboard, set up, customize, remember, save, inspect saved context, reset setup, ask what Data Analytics remembers, asks what Data Analytics can do or how to use it while onboarding is missing or active, or create, add, refresh, inspect, or maintain a semantic layer, route primarily to `user-context`.
3. Apply semantic-layer lookup from the preflight envelope when the request names or implies a product area, metric, table, dashboard, query, or recurring business question.
4. Apply Source Discovery And Verification before source queries, document search, notebook work, report building, dashboard wiring, or conclusions.
5. Apply the Source Access Guardrail before source queries, document search, notebook work, report building, dashboard wiring, or conclusions.
6. Choose the response mode: `inline` for bounded lookups and `report` for explanations, decompositions, recommendations, or larger analytical answers.
7. Select the minimal primary/supporting skills, then do one companion-skill pass across installed skills for clearer non-analytics surfaces, semantic layers, or methods.
8. Read and follow the selected skill bodies before source queries, report building, supporting-skill execution, or final drafting.
9. Before final response, apply the focused workflow's completion gates plus any preflight `final_obligations`.

#### Response Mode

Use `inline` for bounded factual or computational answers that can be delivered in chat without a durable artifact: metric lookups, schema or table questions, one-cut rankings, and simple comparisons.

Treat short quantitative prompts as Data Analytics work when answering them requires explaining how numbers compare, break down, concentrate, or move across multiple values, groups, or time points. Keep these routes lightweight by default: use `inline` for bounded answers and escalate to `report` only when the user asks for explanation, diagnosis, recommendation, or a durable artifact.

Use `report` for explanation, diagnosis, decomposition, synthesis, recommendation, or larger analytical answers whose value materially improves from a durable artifact. When the user asks to interpret analytical source material or reviewed results, choose report mode when the answer needs evidence-backed narrative, caveats, source metadata, or a reader-facing artifact. $product-business-analysis, $metric-diagnostics, and $kpi-reporting imply `report`; every `report` route includes $build-report unless the user explicitly waives file or report creation.

After choosing `inline` or `report`, use `$visualize-data` when a visual would make the result easier to understand, especially for category comparisons, part-to-whole breakdowns, rankings, movement over time, or more than a handful of comparable values, rows, categories, or time points. Prefer a visual pass over a scan-heavy table, and let `$visualize-data` choose the form, decide whether to render a chart, and align any table or prose to the visual takeaway.

#### Skill Selection

- Pick the smallest useful set of primary/supporting skills.
- For report-mode runs, state the selected route once in a progress update, such as `Route: product-business-analysis + product semantic layer + build-report`.
- Use `user-context` for explicit onboarding/setup/context requests and for durable Data Analytics preferences, source pointers, semantic-layer registry, semantic-layer setup or maintenance, or saved workflow notes.
- Treat a plugin mention as a starting point, not a boundary. Add an installed external skill whenever it is the clearer owner of a complementary subtask, runtime surface, delivery surface, artifact type, or domain-specific method.
- Do not reject an external skill merely because a bundled Data Analytics skill partially overlaps with it.
- Do not maintain worked route recipes here. Once selected, the chosen skills own detailed step order, supporting triggers, and output contracts.
- When a request maps to a primary workflow, load that workflow skill directly. For example, a KPI design prompt must read `$design-kpis`, a dashboard prompt must read `$build-dashboard`, a TAM/SAM/SOM prompt must read `$market-sizing`, a metric movement prompt must read `$metric-diagnostics`, and a recommendation-oriented product or business decision prompt must read `$product-business-analysis`.

If several focused skills apply, sequence them in the order that creates the most useful analyst workflow. For example, metric diagnostics may precede KPI reporting, semantic-layer setup may precede dashboard or report work, and product-business analysis may feed a recommendation-ready report. Keep this index as a router; do not perform focused workflow logic here.

Before finalizing future Data Analytics instruction edits, run `python3 plugins/data-analytics/skills/user-context/scripts/validate_user_context_preflight.py` from the repository root. Treat a missing mandatory pre-answer gate in any `SKILL.md`, including helper skills, as an audit finding to fix before release.

Prefer examples that route to focused skills without extra setup, such as:

```text
@Data Analytics diagnose why subscription ARR moved last week.
@Data Analytics build a KPI framework for the customer onboarding funnel.
@Data Analytics analyze paid workspace retention and recommend what to investigate next.
```

For follow-up messages such as "yes", "walk me through it", "what happened?", or "show the steps" immediately after a completed guided workflow offers a walkthrough, route to `user-context` and use `../user-context/references/onboarding.md#workflow-walkthrough-on-request`. Explain the observable steps, tool/app calls, retrievals, source gaps, and artifact assembly at a beginner-friendly level without revealing hidden reasoning.

### Broad Orientation And Help Requests

For broad orientation and help requests:

- Handle open-ended Data Analytics asks from this index before choosing a focused workflow.
- Route requests such as `what can you do?`, `help`, `orient me`, `what should I try first?`, `how do I use Data Analytics?`, setup-adjacent capability questions, and similar plugin-level requests here when the user needs orientation more than a specific artifact.
- Before using this index-level help answer, check the preflight onboarding status. If onboarding is missing or active and the user asks `what can you do?`, `orient me`, `what should I try first?`, `how do I use Data Analytics?`, or another setup-adjacent capability question, route to `user-context` and render the current onboarding step from `../user-context/references/onboarding.md` instead of this default skill-map answer.
- Use this index-level help answer when onboarding is complete or quiet, or when the user explicitly asks for a compact capability summary without resuming setup.
- Answer from the skill map in this file using the default shape below.
- Include concrete low-friction next prompts that start with `@Data Analytics`, name the analytics job, and use a realistic anchor.
- Include a short setup context section from the `data_analytics_preflight.context.connector_setup_summary` envelope when any source is not active, needs a user choice, was skipped, or is otherwise unresolved.
- Keep setup context analyst-facing: name the practical source, use model judgment to explain the likely user-experience impact from the source label, configured preferred routes, setup action, and suggested next prompts, then give the smallest next action or fallback.
- Show at most three highest-impact gaps by default, and never more than five setup-context bullets total. Prioritize gaps in the order most relevant to the examples you are suggesting rather than following a hard-coded impact catalog.
- If all sources are active, keep setup context to one sentence such as `Your core Data Analytics sources look ready; I'll still try each source only when a workflow needs it.`
- When the current context or available sources identify a real metric, product area, dashboard, table, SQL query, semantic layer, experiment, funnel, cohort, or decision question, use the relevant focused skill's inline first-run and next-step guidance to make the suggested prompt contextual.
- For setup context wording, be direct and practical, for example: `You won't be able to properly validate a metric from live tables until a warehouse or SQL source is available, but you can paste SQL, schema details, or exported query results for now.`
- Use static examples only when no suitable context is available.
- Do not expose raw status names, onboarding state fields, connector ids, or implementation terms.
- Do not perform connector reads merely to answer a capability question; use the preflight setup summary and any current session app or tool availability already visible in context.

Use this default answer shape for broad orientation and help requests:

```md
Data Analytics can help with:
- Metric diagnostics and source-backed explanations for movement
- KPI design, metric definitions, and measurement frameworks
- Product and business analysis for funnels, retention, adoption, pricing, and strategic decisions
- KPI reports, dashboards, notebooks, and reusable semantic layers
- Market sizing, opportunity sizing, and decision-ready recommendations

Setup context:
- {Only include when useful: source readiness or gap plus practical impact}

Good first prompts:
- `@Data Analytics diagnose why subscription ARR moved last week.`
- `@Data Analytics build a KPI framework for the customer onboarding funnel.`
- `@Data Analytics analyze paid workspace retention and recommend what to investigate next.`
```

# Plugin Purpose

Data Analytics turns connected or provided business data, source-of-truth context, dashboards, docs, chats, notebooks, spreadsheets, SQL, and semantic layers into source-backed analytical work products. It can define KPIs, diagnose metric movement, size markets, analyze product or business questions, validate data quality, gather context, build reproducible notebooks, design visualizations, create dashboards, produce polished reports, and convert those outputs into shareable Docs, Slides, spreadsheets, or other durable handoff surfaces.

## Semantic Layers

Semantic layers are source-backed local skills for product, business, metric, source, or reporting areas. They encode canonical metrics, tables, grains, joins, filters, query patterns, caveats, source precedence, and validation gaps.

Before answering questions about a named product area, metric, table, dashboard, SQL query, source choice, join, caveat, or recurring business question, inspect the `semantic_layers` registry returned by user-context preflight and installed skills whose name or description matches `<area>-semantic-layer`, `<area>-data-semantics`, or equivalent semantic-layer wording. If a relevant semantic-layer skill exists, read it before selecting tables, writing SQL, reconciling dashboards, or giving metric definitions. Treat it as the domain-specific semantic map, then consult the connected or provided apps and verify high-stakes claims against the layer's cited sources.

When no relevant semantic layer exists and the user is asking a repeatable domain question, offer semantic-layer setup through `user-context`. Users can create multiple semantic layers for multiple product or business areas. Do not merge unrelated product areas into one broad layer unless the user explicitly asks for a cross-product semantic layer.

## Evidence And Handoff

Data Analytics plugin files use lane placeholders such as `~~structured_data` for whatever tool, connector, MCP server, plugin skill, pasted result, uploaded file, or schema description is available in that category. See [DEPENDENCIES.MD](../../DEPENDENCIES.MD) for provider options. When a required connector, plugin, MCP server, or source-of-truth lane is unavailable, follow the Source Access Guardrail. When an optional lane is unavailable, continue from pasted query results, uploaded files, SQL snippets, screenshots, schema descriptions, or other reviewed evidence and label the gap when it materially affects the answer.

Source rules:

- Gather source-of-truth context before writing SQL, notebook code, dashboards, reports, or conclusions.
- Prefer reproducible notebooks for fresh SQL, Python, statistics, modeling, source reconciliation, or non-trivial metric computation when a notebook materially improves auditability.
- Preserve relevant SQL, scripts, query permalinks, outputs, source links, and caveats in the final artifact or supporting notes.

Delivery surface boundary:

- Startup must work when the user does not want MCP widget or MCP artifact rendering. In that case, continue through the selected chat, notebook, SQL, HTML, BI, Streamlit, spreadsheet, slide, or other non-MCP surface and keep source notes in that surface's normal supporting artifacts.
- Use MCP inline widgets or the unified MCP artifact app only when that delivery surface has been selected, is safe, and has not been waived by the user. Before shaping widget/app-specific artifacts, read `../../src/analytics-app-core.md`; keep MCP mechanics out of this startup router.
- Do not expose hidden reasoning, credentials, secrets, direct personal contact/payment identifiers, or unvalidated calculations in any user-facing surface. Reviewed customer, account, or company names may be included when they are needed for the analysis.
- Once the analysis commits to a source table in an inline or dashboard route, expose a small deterministic preview when safe through the selected surface's normal preview mechanism.
- If a preview is unsafe, unavailable, or blocked by access limits, record that briefly and continue from schema, documentation, or other reviewed evidence.

## Completion Gates

Report completion:

- The report run must choose exactly one report delivery mode through `$build-report`.
- Choose a non-MCP delivery mode when the user asks for HTML, file/blob sharing, Docs/Slides conversion, offline portability, no MCP app/widget rendering, or when MCP artifact rendering is unavailable, unsafe, or over bounds.
- Do not end with only an inline/chat summary or a localhost URL. Treat chat summaries as progress updates.
- If a required deliverable is skipped, include the explicit omission reason in the final handoff.
- HTML report charts must be Seaborn-generated PNG images.
- If the report includes charts, evidence tables, or custom visualizations, satisfy $visualize-data's chart contract and QA before embedding them.

Final review:

- Verify generated artifacts by opening, reading, rendering, or otherwise inspecting them.
- Check source-backed claims against the controlling sources used for the analysis.
- Call out unresolved gaps or caveats when they materially affect the conclusion.
- Verify that every selected primary workflow skill was read and followed. If a primary workflow was skipped, record why in the final handoff. Do not treat a semantic-layer lookup, notebook, validation pass, visualization, or report artifact as satisfying the primary workflow contract.
- If the run was classified as `report`, do not finalize until the downstream $build-report contract has either passed or been explicitly blocked.
- If a selected rendering surface is unsafe, unavailable, too large, or fails after a targeted retry, continue the analysis through another appropriate surface and briefly note the reason in the progress update or final handoff.

## Skills

### design-kpis

Use $design-kpis for goals, primary KPIs, driver metrics, guardrails, scorecards, measurement plans, and launch or experiment success criteria.

### kpi-reporting

Use $kpi-reporting for KPI updates, scorecards, business reviews, executive metric summaries, target or pacing readouts, and leadership-ready performance narratives. Add $metric-diagnostics when the update must explain why a KPI moved.

### market-sizing

Use $market-sizing for TAM/SAM/SOM, opportunity, spend or revenue pool, customer count, unit volume, commercial upside, and sensitivity models.

### metric-diagnostics

Use $metric-diagnostics to identify what drove a metric over a defined time period, baseline, or segment comparison, rule out measurement artifacts, label findings by certainty, and route the final report through $build-report.

### product-business-analysis

Use $product-business-analysis to analyze product or business data and context for recommendation-oriented decisions. Add $metric-diagnostics when the recommendation depends on validated metric movement.

### analyze-data-quality

Use $analyze-data-quality for freshness, grain, row counts, nulls, duplicates, schema drift, broken joins, outliers, backfills, and source or dashboard disagreement.

### build-dashboard

Use $build-dashboard for analytical dashboards, scorecards, monitoring pages, BI views, Streamlit dashboards, MCP artifact dashboards, BI platform dashboards, and dashboard QA.

### build-report

Use $build-report to build exactly one durable report surface selected for the user request, such as an MCP app report or an HTML report with Seaborn-generated PNG charts.

### report-to-google-doc

Use $report-to-google-doc to convert an existing local HTML report into a polished native Google Doc.

### report-to-google-slides

Use $report-to-google-slides to convert an existing local HTML report into a polished native Google Slides deck.

### report-to-pdf

Use $report-to-pdf to convert an existing static Data Analytics report export into a verified PDF artifact.

### gather-business-context

Use $gather-business-context for docs, dashboards, chats, planning notes, launch or experiment material, source-of-truth pages, owners, incidents, roadmap, GTM or customer context, and prior decisions.

### jupyter-notebooks

Use $jupyter-notebooks to create, edit, and verify reproducible notebooks for SQL, Python, statistics, modeling, cohort or funnel analysis, data-quality checks, experiments, market sizing, diagnostics, and report support.

### spreadsheets

Use $spreadsheets to create, edit, inspect, render, verify, export, or Google Sheets-handoff spreadsheet artifacts.

### validate-data

Use $validate-data to QA methodology, source selection, SQL or query logic, calculations, visualization integrity, caveats, and whether conclusions are supported by evidence.

### visualize-data

Use $visualize-data to design, implement, and QA charts for reports, dashboards, decks, notebooks, scorecards, trends, decompositions, funnels, cohorts, distributions, uncertainty, and executive KPI readouts.

### user-context

Use `user-context` as the Data Analytics durable context, setup, onboarding, semantic-layer registry, and saved preference owner. Route explicit onboarding, setup, customization, remember or save requests, saved-context inspection, and reset requests here.
