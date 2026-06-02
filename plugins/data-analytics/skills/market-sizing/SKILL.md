---
name: market-sizing
description: "Estimate a market or opportunity size, such as TAM/SAM/SOM, by defining scope, choosing a sizing model, checking connected context and public sources, and presenting transparent assumptions, sensitivity, uncertainty, and validation priorities. Use for market or opportunity sizing; not for KPI reporting or metric diagnostics."
---

# Market Sizing

Use this skill to produce a defensible estimate of a market or opportunity from connected context, public sources, transparent assumptions, and auditable calculations. The job is to define the market, choose a sound sizing method, distinguish evidence from assumptions, test sensitivity, and state what would most improve confidence.

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

Clarify with the user when a missing input would materially change the estimate or recommendation. Otherwise make a reasonable assumption, state it, and proceed.

## Workflow

### 1. Frame The Market Or Opportunity

Define the market or opportunity boundary before estimating:

- What is being sized, for example a product category, workflow, problem, use case, or category of activity.
- Where and when it applies, for example geography, segment scope, time horizon, or market maturity.
- Who or what counts as part of the market, for example the relevant population, unit of demand, transaction type, or included activity.
- How the opportunity is measured, for example spend, revenue, volume, value created, or another unit that fits the question.
- What kind of sizing answer the user needs, for example TAM/SAM/SOM, market entry, expansion upside, spend pool, revenue pool, population count, or unit volume.

### 2. Choose A Starting Sizing Approach And Inputs

Pick the simplest sound sizing approach for the question, then sketch the calculation chain and the major inputs the estimate will depend on.

A top-down model works when reliable aggregate market data exists; a bottom-up model works when the market can be built from observable units and assumptions; a value-based model works when the estimate should start from the value created rather than a published market total. Use a mixed approach only when cross-checking would materially improve confidence. If more than one approach fits, briefly explain which one you trust most and why.

Expect the first approach to change if source checks show that another model would be more defensible.

### 3. Gather Sources For The Inputs

Choose sources based on the inputs the estimate depends on most.

Start with user-named sources when provided. Then use the strongest available evidence for each major input from the starting approach. Use `~~structured_data` when an input should come from the user's data warehouse or another structured data source. Use context lanes such as `~~company_docs`, `~~team_communication`, or `~~dashboards_or_bi` when an input needs business meaning, source-of-truth guidance, or assumptions that are not captured in structured data alone. When an input depends on the outside market, use public sources for benchmarks, population estimates, comparable markets, or proxy assumptions.

Use $gather-business-context to resolve context lanes when the right source of truth, business meaning, or assumption set is unclear.

If the strongest source is unavailable or thin, continue with a transparent proxy assumption only when the estimate is still useful. Label the gap and explain how it affects confidence.

### 4. Separate Facts From Assumptions

Keep sourced facts, inferred estimates, and judgment calls distinct in the model. When exact data is unavailable, use a defensible proxy, explain why it is reasonable, and note the confidence level. Ground assumptions in evidence about how the market actually behaves, what can realistically change, and what determines the size of the opportunity.

### 5. Build The Model

Make the model easy to inspect and adjust.

The model should make these elements easy to audit or revise:

- market definition and measurement unit
- assumptions and source context
- calculation chain and derived values
- base case, material ranges, and sensitivity logic
- validation priorities

For each major input, make the source path visible: structured data, context lane, public source, user-provided input, or proxy assumption.

Keep derived values traceable to formulas or code rather than hardcoded outputs.

Use $jupyter-notebooks when code is needed for source harmonization, calculations, sensitivity analysis, or reusable modeling logic. Keep formulas, inputs, intermediate calculations, and sensitivity logic inspectable.

Use $spreadsheets when the user requests a spreadsheet, workbook, or Google Sheets deliverable, or when a market-sizing model would materially benefit from editable assumptions, sensitivity tables, charts, or polished workbook formatting.

### 6. Test Sensitivity

Identify the assumptions that move the estimate most.

Show how the estimate changes when those assumptions move up or down. Prefer simple, decision-useful sensitivity analysis over exhaustive scenario sprawl.

Use ranges when uncertainty is material. Do not hide uncertainty behind a single point estimate when the inputs are thin.

### 7. State The Estimate And Validation Priorities

End with the estimate, method, key assumptions, uncertainty, and next validation priorities.

Close with the market definition, estimate or range, method, main uncertainty drivers, sensitivity takeaways, validation priorities, and practical interpretation for the user's decision.

If source coverage is thin, say which major inputs rely on proxy assumptions and what source would most improve them.

Use $validate-data when methodology, calculations, assumptions, caveats, or source support need review before sharing.
