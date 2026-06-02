---
name: metric-diagnostics
description: "Diagnose why a metric changed or differs from expectation by reproducing the metric, choosing the right comparison, validating likely drivers, and producing a calibrated explanation. Use when the user needs to understand what drove a metric movement, anomaly, gap, or discrepancy."
---

# Metric Diagnostics

Use this skill to diagnose why a metric changed or differs from expectation. Reproduce the metric, define the comparison, quantify the movement, validate likely drivers, and state what is verified, likely, unresolved, and useful to do next.

Clarify with the user when a missing input would materially change the analytical frame or recommendation. Otherwise make a reasonable assumption, state it, and proceed.

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

### 1. Define The Diagnostic Question

Frame the diagnostic so it is clear what changed and what comparison would prove it.

Define:

- what the metric means in business terms
- the time window and comparison that make the change measurable
- the population and grain that determine what counts
- the source that owns the metric definition
- the diagnostic question being answered, for example movement, concentration, or reconciliation

Use $gather-business-context when business context is needed to understand what the metric means, what changed around the analysis period, or which explanations are plausible.

### 2. Validate The Metric Definition And Source

Before explaining the movement, confirm that the metric is defined correctly and that the source data can measure it reliably.

Confirm the metric definition, grain, aggregation logic, filters, joins, exclusions, freshness, lineage, and any disagreement between trusted surfaces. Keep this source check focused on issues that could change the answer.

Treat memory, saved context, semantic-layer notes, and familiar table names as source candidates, not source selection. For broad metric questions, run live source discovery against available tables, dashboards, metric docs, semantic registries, or other source-of-truth surfaces before choosing the controlling source. When both are available, inspect at least one business-facing or top-line surface and one lower-level source surface, then state why the selected source owns the answer.

Use $analyze-data-quality when freshness, grain, joins, missingness, schema drift, outliers, unexpected categories, or distribution shifts could affect trust.

Use $jupyter-notebooks when fresh SQL, Python, statistical modeling, reusable calculations, or multi-step decomposition need an inspectable analytical record.

### 3. Establish The Metric Pattern

Before looking for drivers, establish the metric pattern the diagnostic needs to explain. Quantify the metric over the relevant period and scope. If the question includes a comparison, reproduce that comparison.

Do not search for causes until the size, timing, and scope of the pattern are verified or explicitly marked uncertain.

### 4. Choose The Diagnostic Plan

Choose the smallest set of cuts and checks likely to explain the pattern or strengthen confidence.

Choose driver dimensions from the metric's operating logic, business context, and source shape. Prioritize drivers the business usually monitors or can act on, not every field available in the source. If the relevant drivers are unclear, use saved context or $gather-business-context to understand how the business explains the metric and what changed around the analysis period.

When using a lower-level table, do not limit the driver analysis to fields surfaced by the first query. Recreate or join the business grouping needed to answer the question, such as model family, model superfamily, segment, region, cohort, product taxonomy, or customer hierarchy. If the grouping cannot be reconstructed, say so before simplifying the analysis.

Use the explanation mode that fits the question. Common examples:

- **Metric change**: compare the focal window with a baseline, rank segment contributions, check peer or historical context, and test mix shift versus within-segment movement.
- **Spike, regression, or incident**: pin down onset, peak, recovery,
  distribution shape rather than only averages, affected slices, broad versus localized degradation, and whether traffic or failure behavior changed.
- **Largest contributors or concentration**: define "largest", rank entities,
  compare total share and change, and look for major movers, entrants, and exits.
- **Reconciliation or difference analysis**: align definitions, filters, grain,
  numerator, denominator, and exclusions; quantify the components explaining the gap and state any residual.

### 5. Decompose And Validate Drivers

Quantify the main drivers and validate whether they explain the pattern.

Size each major driver with the strongest readily available evidence. Show whether it explains the pattern, how large it is relative to the relevant base, trend, or gap, whether it is broad or concentrated, and whether it holds under the right comparison or scope.

Iterate on driver hypotheses until the explanation answers why in a way that is relevant to the business. Follow promising cross-cuts and drill-downs when they could reveal the key explanation, and stop when additional cuts are unlikely to change the conclusion or materially improve confidence.

Interpret driver results in context:

- Use the relevant base, comparison, or share of total to make the driver meaningful.
- For rates, check whether the numerator, denominator, or both explain the change.
- For additive metrics, calculate contribution share when it sharpens the story.
- Separate composition effects from within-segment performance effects when that distinction changes the explanation.
- Prefer mutually exclusive driver buckets when additive contributions need to be interpreted; reconcile the decomposition exactly or size and explain the residual.

Treat measurement issues as possible explanations, not just cleanup details. For example, the pattern may come from logging changes, incomplete recent data, duplicated rows, or a shifted denominator rather than an underlying business change.

Calibrate the explanation to the evidence, and make important uncertainty visible. Use context when it changes interpretation, such as whether the pattern is ordinary, unusual, expected, or tied to a known change.

Use $visualize-data when a chart would make the diagnostic claim easier to understand or verify.

### 6. State Implications And Follow-Up

Lead with the answer to the diagnostic question, then state the practical implications when the evidence supports them.

The answer should make clear:

- the pattern being explained
- the strongest driver explanation and supporting evidence
- why it matters for the business
- how much confidence to place in the explanation
- the implication, next action, or follow-up that matters most

Keep implications distinguishable from verified factual reporting so a reader can tell where evidence ends and interpretation begins. Do not claim causality from timing alone; state when an explanation is only a plausible hypothesis.

Use $gather-business-context when the metric result is clear but business context is needed to interpret the `so what` or identify realistic next actions.

Use $validate-data when methodology, calculations, caveats, or the evidentiary support for the diagnostic conclusion need review before sharing.

Do not treat artifact or report validation as analytical validation. Before handing off, confirm the analysis has the headline metric movement, driver contribution shares or effect sizes, source/window reconciliation, exact executed SQL or query references when queries were used, and caveats that would change interpretation.

Pass the diagnostic substance and supporting evidence to $build-report. Let $build-report own the report surface, presentation polish, reproducibility treatment, and sharing handoff.
