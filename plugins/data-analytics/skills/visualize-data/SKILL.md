---
name: visualize-data
description: "Design, specify, implement, revise, and QA quantitative visuals and chart choices. Use when an analytical answer needs visual judgment; for example comparing values, showing how a total breaks apart, reading concentration in a ranking, or understanding movement over time. This may mean rendering a chart for a report or dashboard, or simply choosing, rendering and QAing the right chart form for an inline answer."
---

# Data Visualization

Create quantitative visuals that are analytically sound, immediately readable, and polished enough to ship in a report, memo, slide, dashboard, notebook, widget, or HTML artifact. Treat charts as evidence for a takeaway. Redesign charts that are visually attractive but analytically weak, and revise charts that are technically correct but hard to interpret.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `data-analytics:user-context` in preflight mode by loading [data-analytics:user-context](../user-context/SKILL.md) and running its preflight script before answering, searching connectors, retrieving evidence, creating artifacts, or drafting output. Do not look for a callable MCP tool named `data-analytics:user-context`. Use the returned `data_analytics_preflight` envelope as the source of truth for saved context, source-category mapping, semantic-layer registry, onboarding/final-response obligations, and conditional guidance; use saved context and semantic layers as source-selection inputs, not as substitutes for workflow-time reads from connected or provided sources. Do not read or reinterpret raw plugin state files unless preflight fails, declares required content omitted, local shell access is unavailable, or the user explicitly asks for raw state inspection.

## Chart Selection

Common surface forms should be named in the chart contract when the final surface is a report, dashboard, slide, notebook, widget, or HTML artifact.

| Data relationship | Best chart | Use it well |
|---|---|---|
| Trend over time or ordered axis | `line` | Show enough points to reveal shape; use `area` only when filled magnitude helps, and `sparkline` only in dense KPI cards |
| Composition over time | `stackedArea` | Use when parts should read as one total; switch to `line` when comparing component trajectories matters more |
| Comparison across categories | `bar` | Sort when order is not semantic; use horizontal bars for long labels; avoid redundant legends |
| Ranking or top-N | `leaderboard` | Keep it compact and single-measure; switch to ranked `bar` when comparison needs more chart context |
| Part-to-whole composition | stacked `bar` | Keep the denominator explicit; use `pie` only for a rough read with few slices |
| Distribution or spread | `histogram` | Use numeric bins that reveal shape; switch to `boxPlot` when comparing groups is the point |
| Distribution across groups | `boxPlot` | Use when median and spread matter more than full shape; switch to `histogram` when shape needs space |
| Relationship between two numeric variables | `scatter` | Use numeric x and y at a meaningful observation grain with enough distinct points to show a pattern; retain point labels, sample/volume fields, and one useful grouping candidate when safe |
| Dense two-dimensional pattern or cohort matrix | `heatmap` | Use for matrix shape or intensity; switch to `scatter` when point-level variation matters |
| Additive bridge from start to end | `waterfall` | Use only when drivers sum cleanly to the end value; otherwise use ranked `bar` |
| Ordered stage progression or drop-off | `funnel` | Use only for ordered single-series stages; prefer stage `bar` when funnel geometry distorts comparison |

## Workflow

1. Define the analytical question and one-sentence takeaway before choosing a chart. Identify the final surface, the intended comparison, and the context needed to make the visual honest.
2. Choose the simplest defensible family and variant from `Chart Selection`. Coordinate with `$build-dashboard` or `$build-report` when the visual belongs to those artifacts, and use `$validate-data` when the supporting analysis needs validation.
3. Write a compact chart contract before plot code, dashboard configuration, or renderer-specific implementation work. Include:
   - analytical question and takeaway
   - canonical family and concrete variant
   - data sufficiency for the chosen visual: expected row count, temporal point count for trend views, scatter observation count and grain, requested date range and grain, and fallback if the first query is too sparse
   - surface-native chart type or Seaborn template variant when a concrete renderer has been selected
   - delivery-specific constraints only after the delivery surface is chosen; for MCP widgets or app artifacts, use the shared MCP specification
   - palette policy, approved palette roots, and non-color distinction plan
   - output footprint, final container, export paths or delivery target, and the final QA surface
4. Select the delivery path that matches the final surface.
   - Use MCP inline widgets or the Data Analytics MCP artifact app only when that surface has been selected and the user has not waived widget/app rendering. Before shaping MCP-specific artifacts, read `../../src/analytics-app-core.md`.
   - Use the selected report, dashboard, BI, notebook, slide, or static HTML surface's native chart primitives when they can communicate the point.
   - Read `references/seaborn-templates.md` during the current task before every static Python implementation, revision, review, QA pass, or HTML report visual. Adapt the closest template and export the format expected by the selected delivery surface. Portable static HTML reports use PNG chart images.
- Use governed BI or dashboard-native widgets when that surface owns rendering; this skill should supply the visual spec and QA bar.
- Implement local HTML/CSS/SVG/canvas/JavaScript visuals only when the final surface truly requires local rendering, custom interaction, offline portability, or a larger artifact than a widget can carry.
5. Build in this order: format, structure, color, then QA. Choose the family, variant, and delivery surface first; decide labels, annotations, benchmarks, and retained information second; choose palette policy and explicit colors last.
6. Render or export the chart in its real context. Save the image format the selected delivery surface expects. For delivered portable static HTML artifacts, use PNG chart images.
7. Inspect the visual in the final report, slide, dashboard, notebook, widget, or HTML layout. Revise before delivery when the chart, labels, color system, or container fails final-context QA.
8. For shipped reports or dashboards with multiple visuals, maintain a compact chart map in notes or source material. Name the section, analytical question, selected family and chart type, fields, supported takeaway, palette policy, and delivery artifact, image path, or provenance source.

## Standards

### Selection Rules

Start from the analytical question and comparison the reader needs to make, not from a favorite chart type. Keep the top-level set small:

- `Tables & Scorecards`
- `Trend`
- `Comparison & Ranking`
- `Composition`
- `Distribution`
- `Relationship`
- `Uncertainty & Benchmark`
- `Matrix & Cohort`
- `Decomposition & Progression`

Concrete forms such as `highlighted multi-series line`, `Likert`, `pie`, `Pareto`, `waterfall`, `faceted dot & interval`, and `cohort heatmap` are variants inside these families, not peer families.

- Use charts for shape and comparison; use tables for exact lookup. If a table would show 3-8 comparable entities with one dominant numeric measure, prefer a bar, dot, lollipop, leaderboard, or other chart unless exact row lookup is the point.
- When reviewed evidence contains many comparable values, rows, categories, segments, or time points, default to rendering a simple chart on the selected delivery surface when that surface is available and safe. Skip rendering only when exact row lookup is the main task, the data is too sparse for an honest chart, the user asked for table/prose only, or the selected surface cannot support a useful visual.
- Do not choose `line` merely because the prompt says "trend" or "trending". Decide first whether the reader needs current status, movement, variance to plan, mix, concentration, drivers, progression, or distribution.
- Do not ship underpowered trend charts. For line, area, sparkline, indexed-trend, or other time-series views, first try to expose either a finer time grain or a longer date range so the displayed series has enough observed points to show shape. As a default, aim for at least 8-12 temporal points for a trend visual; if the available evidence has only a few anchor periods, query daily or weekly rows, extend the lookback, or add a meaningful segment/comparator before rendering. Use a KPI strip, grouped bar, slope chart, table, or narrative callout instead when the question is really a small set of discrete period comparisons.
- Do not ship underpowered scatter charts. A useful scatter needs enough comparable observations to reveal shape, clustering, outliers, or exceptions; as a default, aim for at least 12-20 meaningful points and treat fewer than 8 points as a likely table, bar, dot/lollipop, or narrative comparison unless each point is intentionally important and labeled. If the first result only has a few segment aggregates, make one targeted attempt to query a finer analytical grain such as account, workspace, user cohort, customer, model, endpoint, route, geography, or segment-by-period. Keep all plotted rows at the same grain, and do not mix totals, averages, and detail rows in one scatter.
- For scatter charts, choose x and y measures that can plausibly vary independently and share the same denominator, time window, population, and filters. Include the denominator, sample size, or volume metric used to judge reliability, and use a size encoding only when that third metric materially changes interpretation. Add a point-label field for small or executive-facing scatters, and retain a meaningful categorical field such as segment, plan, route, product line, model family, or region for optional color or filtering. Avoid coloring by a unique row id; use labels or the table for exact identity instead.
- Use horizontal bars for long labels and sorted bars when order has no semantic meaning.
- Use compact leaderboard-style ranked bars only for top-N previews with one numeric value and 3-8 visible rows. Default to 5-6 rows in compact dashboard cards. Use a paginated table for long-tail browsing or exact lookup, Pareto for cumulative concentration, and waterfall for additive start-to-end driver bridges.
- Do not use leaderboards to rank KPI definitions or time-window definitions against each other, such as latest DAU versus WAU versus MAU. Use KPI cards or a compact table for latest values; use trends, indexed trends, share trends, or ratio charts for movement or relationship questions.
- When a bar chart compares one measure across categories, use one categorical axis and one quantitative axis. Do not set a `color`, `series`, or grouped-bar encoding to the same category field just to color each bar; that creates a redundant legend and implies an extra grouping dimension. Use a palette/style option or direct labels if the surface supports per-category color without a legend; otherwise use a single mark color.
- When a bar chart compares same-unit movement across distinct KPI categories, such as latest week-over-week percent change by metric, categorical bar colors can help scanning, but they should be styling, not a visible grouping/legend, unless a second categorical dimension is present.
- When a bar chart compares unrelated business entities or components, such as products, model families, segments, or seat-support areas, do not encode every row with one fixed color when category identity matters. Prefer categorical styling and direct labels; reserve a single color for one measure repeated across a single semantic entity. Avoid adding a color legend when the axis labels already name the categories.
- For active-user dashboards, use KPI cards for latest DAU, WAU, MAU, Plus DAU, and Plus WAU values; trend or indexed-trend charts for movement over time; share or stickiness views when the question is mix or ratios; and categorical horizontal bars for unrelated week-over-week metric movements.
- Prefer variant escalation inside a family before inventing a new chart type: line to small multiples, bar to dot/lollipop, scatter to density, stacked bar to pie only when the circular read is explicitly useful.
- Keep pie, Pareto, waterfall, and Likert as variants, not defaults.
- Avoid bubble charts unless the third variable materially changes the interpretation.
- Include volume, denominator, sample size, or cohort context when omission could mislead.
- In multi-area executive reports, repeated line charts are a smell. Use line charts only where the main question is continuous movement over time. Consider dot/lollipop or bar with reference for plan variance, stacked area or 100% stacked bar for mix, ranked bars or leaderboards for category comparisons, waterfall for additive drivers, heatmaps for cohort or matrix structure, and stage bars for ordered progression.
- For one-slide-per-area executive reports, do a chart-family pass before writing the visual plan. Audit repeated families and require a rationale when multiple sections use the same family despite asking different questions.
- If every visual in a report uses the same family, document the reason in the chart map and verify that no section is actually asking for status, mix, variance, or drivers.
- Four or more all-line visuals fail the multi-chart report contract unless the report is redesigned with data-compatible alternatives or fewer visuals.

### Surface And Implementation

- Do not treat "route through visualize-data" as "always write chart HTML." This skill may produce a visual spec and QA bar rather than local chart code.
- Do not assume widgets or the MCP artifact app are required. If the user wants chat, notebook, HTML, BI, Streamlit, slides, static files, or no rendered artifact, keep this skill's output to chart selection, data planning, implementation guidance, and QA for that surface.
- When the selected delivery surface is an MCP Apps widget or Data Analytics MCP report/dashboard artifact, read `../../src/analytics-app-core.md` after selecting the chart family. Do not let an MCP-supported type list drive general chart selection for non-MCP surfaces.
- Any table that powers a chart must be richer than the minimum fields needed to draw that chart. Do not ship source-data tables containing only `x`, `y`, and optional series/color fields when the reviewed result can safely include contextual dimensions, numerator/denominator fields, date or cohort fields, ranks, benchmarks, comparison-period values, or adjacent measures. If privacy, query cost, source limits, or metric definitions prevent a richer table, state that limitation in the chart/report notes.
- Before rendering or exporting, inspect the reviewed result table for information density. If the chart would render fewer than 8 temporal points, fewer than 4 meaningful categories, fewer than 8 scatter observations, or a nearly straight two/three-point path, make one targeted attempt to improve the supporting data by querying a finer grain, extending the time range, or adding a relevant breakdown that supports the same claim. If that is blocked by source limits, query cost, privacy, or metric definition, record the limitation and switch to a more honest form such as KPI cards, grouped bars for discrete periods, a table, or prose with exact values.
- Include more than one meaningful quantitative field when the user may reasonably compare measures, swap axes, inspect target versus actual, or choose a relationship view. Do not fabricate auxiliary measures or ship raw detail rows merely to make extra chart types appear possible.
- Shape chart-ready data for realistic alternatives, not arbitrary ones. A trend chart should usually retain its temporal field, value field, and meaningful segment/comparator fields; a category comparison should retain the category, value, useful grouping candidates, and rank/sort context; composition charts should retain the denominator or share context when available. A scatter chart should retain a stable point identity or label, numeric x and y measures, any denominator or sample-size fields, a useful volume/size candidate, and one or two interpretable grouping or filter fields. Do not promote a retained grouping candidate into a color/series encoding unless it adds information not already carried by the axis, facet, or table labels.
- Treat custom local visual implementations as report-complete only after they match the selected delivery mode and pass final-context QA.
- Use the selected surface's native chart block when one is available. Do not add an extra decorative outline shell around charts.
- For HTML reports, keep portable static delivery on PNG chart images. For portable static HTML reports, static report-adjacent doc prep, or other static Python chart paths, use Seaborn templates and export PNG files; SVG may remain as supporting source material, and the HTML report should use PNG chart images.
- If `references/seaborn-templates.md` cannot be read when needed, do not claim template compliance or delivery readiness for a static Python chart. Surface the blocker or label the result rough/exploratory.
- When revising the template library itself or auditing multiple charts at once, fix shared helper stack, palette-root, and layout drift before chart-specific exceptions.
- Assume local environments can be minimal or offline. When needed before importing Seaborn, establish a writable cache such as `MPLCONFIGDIR=/tmp/matplotlib`. Expect Python with Seaborn plus writable temp and output directories; do not assume network installs will succeed.

### Visual Design

- Match chart titles to the surface. Report and dashboard visual headers should stay neutral and descriptive, with takeaways in adjacent narrative text. Standalone static charts may use takeaway-led titles when there is no surrounding narrative block.
- Put metric details, units, denominator, date range, cohort, filters, sample size, or volume in the subtitle when needed. Notes can add caveats, but do not replace the subtitle.
- Use a single font family across charts and surrounding output when possible. Prefer white or near-white backgrounds, quiet grey grid lines, deep charcoal text, and restrained approved palette roots centered on blue, gold, orange, olive, and pink.
- Do not rely on color alone. Use tone, open fill, marker fill, line style, direct labels, ordering, or faceting when series or states need separation.
- Only set color or series encodings for meaningful grouping dimensions such as `segment`, `product_line`, or `series` when they are not already the sole axis category. Omit color for single-series charts and do not manufacture or duplicate a grouping field just to produce a legend.
- Choose one palette policy before plotting:
  - `single-root preferred`: one non-neutral root plus shades, open fills, and neutral references for simple trends, ranks, distributions, relationships, matrices, and repeated panels.
  - `hard two-root cap`: at most two non-neutral roots plus neutrals for binary, signed, focal-vs-context, benchmark, comparator, waterfall, Pareto, diverging, highlighted trend, and ordered line-dot charts.
  - `relaxed multi-category`: up to five approved roots when category identity is the point, such as pie, stacked bars, stacked area, grouped bars, and stage bars. If more are needed, group to top-N plus Other or change forms.
- Use each selected root's `base` tone as the default non-neutral mark color. Reserve `mid` for deliberate higher-contrast exceptions, use `dark` for keylines, outlines, labels, or reference strokes, and use `light`, `xlight`, or `open` for supporting fills.
- Generate explicit palette maps from declared colors. Do not let plotting library categorical defaults choose shipped chart colors.
- For signed values, avoid green/red by default. Use dark versus open/light fills, direct signed labels, and clear zero-line context unless documented domain semantics require an exception.
- For waterfall charts, use matched neutral start and end anchors plus exactly two non-neutral delta colors: one positive and one negative. Do not introduce extra hues or darker/lighter non-neutral keylines for individual drivers.
- Keep one stroke-width system for marks, keylines, guides, and reference lines. Use dark-neutral styling for benchmark, calibration, or ideal lines.
- Keep left and bottom axis anchors visible when labels depend on them. Remove ticks, guides, or connectors that do not improve the intended comparison.
- Prefer direct labels when they reduce legend lookups; use a compact top legend when direct labels create clutter.
- Reserve explicit left and right space for horizontal or diverging bars with long labels or negative values. Do not shrink typography to force a narrow card.
- Do not use gradients inside chart marks, arbitrary colored chart backgrounds, inconsistent or ad hoc corner radii, or thickness as an emphasis channel.
- For HTML artifacts, keep standalone charts on real grid footprints: `8 columns` by default, `6` minimum, `10` or `12` for complex charts, stacked vertically on mobile. Align multi-chart rows from the left/start edge.
- Match HTML chart containers, legends, KPI strips, and notes to the same Data Viz System tokens as the surrounding report or dashboard. Remove unused multi-hue CSS variables when they are not rendered.
- Use dark chart variants only when the containing artifact is dark. Inspect both light and dark variants for shipped branded web outputs.
- For research charts, lock the blossom to the header's top-right corner. Omit it for third-party, partnership, and non-research charts.

### Quality Bar

- Chart choice should follow `Chart Selection`.
- Choose and honor an explicit delivery surface. Use MCP widgets only when that surface is available, safe, useful, and not contrary to the user's requested output mode.
- Keep chart contracts, omitted-chart explanations, validator notes, and QA rationale out of visible executive report bodies unless the user asks for methodology or the detail changes the reader-facing takeaway.
- Static plotting code should visibly adapt the relevant Seaborn template or a minimal skeleton. Generic ad hoc snippets are acceptable only for exploratory charts.
- The form must match the analytical comparison, and scales must stay honest and consistent across comparable charts.
- Data grain, filters, date range, denominator, and units must match the claim the chart supports.
- Every shipped chart must have a visible title appropriate to its surface and a subtitle that carries needed units, time/cohort context, denominator, sample size, or volume.
- Labels, ticks, titles, legends, callouts, benchmark labels, and annotations must not collide, clip, or detach from the evidence in the exported chart or final container.
- Long labels, negative values, outside-end labels, zero-line context, and direct value labels need explicit layout space.
- Multi-series filled marks need distinct tones, open fills, keylines, marker fills, line styles, direct labels, or faceting. Visually identical adjacent or overlapping fills fail QA.
- Line styles, marker fills, open fills, keylines, ordering, faceting, and direct labels should remain legible in grayscale when they carry distinction.
- Positive and negative states should use tone, open fill, zero-line context, and signed labels rather than default green/red semantics unless the exception is documented.
- Exported SVG or HTML colors should match declared palette roots plus neutrals; remove unused multi-hue tokens unless documenting an intentional exception.
- Chart scaffolding should stay quiet: no arbitrary colored backgrounds, gradients, decorative guides, inconsistent stroke widths, or decorative mark fills. Filled marks should keep keylines, and benchmark, calibration, and reference lines should use dark-neutral styling.
- Titles, legends, and primary labels should use dark ink and share a clear header anchor. Numeric ticks and direct value labels should use mono styling where the template system calls for it.
- Research charts should use the locked top-right blossom placement; third-party, partnership, and non-research charts should omit it.
- Before handoff, inspect the visual in the artifact readers will open and verify that it answers the stated analytical question, signs and scales are honest, labels fit at laptop and mobile widths, the color and non-color encoding is understandable, and the caption states metric, time window, and source when those are part of the visual.
- Inspect the final report, slide, dashboard, notebook, widget, or HTML layout before handoff. Revise before delivery when any requirement above fails.
