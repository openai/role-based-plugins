# Analytics App Core

Use this shared foundation for generated Data Analytics dashboard and report artifacts. Public skills should keep separate intent contracts, but reuse this core for bounded snapshots, source safety, app runtime behavior, and validation helpers.

Use this file after the selected delivery surface is an MCP Apps inline chart/table widget or a Data Analytics MCP report/dashboard artifact. Root skills remain delivery-mode neutral: if the user asks for chat, notebook, HTML, BI, Streamlit, slides, or no rendered artifact, do not apply MCP widget/app mechanics except for the general safety principles.

## Shared Contract

- Use `render_artifact` as the default in-Codex reader handoff for generated dashboard/report manifests with bounded snapshots.
- Keep generated artifacts snapshot-first.
- Store source-backed data in `snapshot.datasets` and keep rows bounded and aggregate unless a detail table is explicitly needed.
- Use the canonical snapshot shape: `snapshot.datasets` is an object keyed by dataset id, and each value is a plain array of reviewed row objects. Keep column metadata in the manifest, not inside `snapshot.datasets`.
- Declare source artifacts in the manifest when the reader needs provenance,
  query text, or citation metadata.
- Native chart specs are defined by MCP tool descriptions and enforced by artifact validation. Shared guidance should not duplicate field-level chart schema.
- Use `ready`, `partial`, `blocked`, and `fixture` snapshot statuses across dashboard and report artifacts.
- Reports must expose a visible in-report title. Set `manifest.title` to the reader-facing title, and make the first report markdown block a matching `#` heading.
- Treat `partial` and `blocked` as first-class states with visible access notices, not buried caveats.
- Reserve snapshot-level access issues for missing required data in `partial`
  or `blocked` artifacts. Optional source limitations in an otherwise `ready`
  artifact belong in caveat sections, source metadata, or report notes.
- Every native chart block must expose the actual SQL or source path used to generate its chart dataset through the current MCP artifact schema.
- Native chart source datasets should remain useful beyond visible encodings when safe reviewed context is available. Preserve candidate grouping fields, numerators, denominators, ranks, baselines, comparison periods, and adjacent measures for auditability and realistic chart switching.
- Use the same canonical `source` structure for inline charts, inline tables, artifact charts, artifact tables, and `manifest.sources[]`: put runnable SQL/code in `source.query.sql`, put the human-readable query summary in `source.query.description`, and put durable query metadata in `source.query.engine`, `source.query.id`, `source.query.url`, `source.query.executed_at`, and `source.query.language`.
- Source metadata must be specific enough to validate: use actual table identifiers such as `example.analytics.fact_revenue`, not query nicknames or semantic labels, and put those identifiers in `source.query.tables_used` when they cannot be inferred from SQL.
- Declare static source predicates in `source.query.filters`, including date windows, cohort/population rules, material exclusions, and sampling/limit rules. Use artifact `manifest.filters` only for interactive viewer controls.
- Metric definitions must describe calculations, not only source columns. For ARR, include the aggregation/window, currency/unit, date grain, and material exclusions such as internal orgs, test traffic, true-up rows, or other accounting adjustments.
- KPI and metric cards must use accurate display semantics and scale. Set `format` to the value type being rendered, such as `percent` only for rates/shares and `currency` only for money. Prefer passing unscaled numeric values and using compact formatting so the artifact renders `K`, `M`, or similar scale suffixes accurately. When a query intentionally pre-scales a value, make that scale visible in the metric label, such as `B tokens` or `revenue, $M`; do not rely on SQL aliases, field names, or query comments to imply it. Do not use a percent or currency format just because the metric is a change; format the actual value's unit and label the comparison separately.
- Reader-facing numbers in cards, chart labels, axes, tooltips, headings, and narrative text should use compact shorthand for large values, such as `1.2k` instead of `1,201`, unless the surface is an exact lookup table or audit detail where precise values are the point.
- KPI and metric cards must be interpretable without reading the SQL. If a metric label depends on business logic rather than a plain count or sum, define the metric in reader-facing terms and preserve the exact calculation in `source.query.metric_definitions`.
- Definitions should clarify the population being measured, the event or state being counted, the time window, the aggregation method, and any important thresholds, exclusions, numerator/denominator logic, or source-specific meaning. This is especially important for rates, averages, shares, lifecycle or stage metrics, eligibility or activity metrics, quality outcomes, and version/source-attribution metrics.

## Inline Widgets

- Inline widgets are for compact, reviewed intermediate or final values in non-report runs. Do not render inline chart or table widgets during report-mode work; report charts, tables, and previews belong in the selected report surface.
- Use `render_chart` for compact inline visuals from reviewed query results in non-report runs when the widget surface is available, safe, and useful for the user. Use `render_table` for row previews, exact lookup tables, or table-shaped data.
- Chart and table widget payloads are query-shaped and pass the same canonical `source` object. The source query must contain the durable original SQL used to materially produce the reviewed rows, plus any durable query ID or URL as metadata. If a later query only reshapes, sorts, limits, or reselects from already computed rows for widget rendering, keep that later query out of `source.query.sql`; record it as transformation context instead of replacing the original provenance.
- The source query text must be runnable SQL in the named engine. Do not pass prose such as "Revenue bridge SQL executed in Databricks..." as `source.query.sql`; put that prose in `source.query.description`.
- The chart subtitle should add a reader-facing insight not already covered by the title. Put source names, query IDs, table names, SQL intent, metric definitions, and provenance in source metadata or notes instead.
- Make widget tables exploration-ready with useful dimensions, measures, time columns, candidate grouping fields, ranks, benchmarks, comparison-period values, or adjacent measures from reviewed results. Customer, account, company, segment, and product names are valid analytical dimensions when they are relevant. For scatter widgets, prefer one row per meaningful observation rather than a handful of broad aggregates; retain a stable point label, numeric x and y measures at the same grain, denominator or sample-size fields, one volume/size candidate, and one interpretable grouping or filter field when safe. Retaining a field for exploration does not mean the shipped chart should bind it as color, series, or grouping.
- Use tidy long-form rows when that keeps chart switching understandable.

## MCP Safety And Rendering

- If the user explicitly waives MCP widgets or app rendering, continue through the selected non-MCP surface and preserve SQL, source notes, and visual QA in that surface's normal supporting artifacts.
- Do not send hidden reasoning, credentials, secrets, direct personal contact/payment identifiers, or unvalidated calculations into widget or artifact payloads. Reviewed customer, account, or company names may be included when they are needed for the analysis.
- Keep exposed rows compact, reviewed, and at a clear analytical grain. Use deterministic samples for larger results, set the full reviewed row count, and mark truncation when applicable.
- After running a durable source query, expose the first 10 reviewed rows, or a deterministic 10-row sample when the query result is too large or naturally unordered, so the user can validate the grain and columns behind the chart/table.
- Preserve the actual SQL, source file path, or reproducible transformation that materially produced exposed rows. Do not replace query text with a prose source description, metric definition, filter summary, or query ID list.
- Validate MCP artifacts with `validate_artifact` before the first visible `render_artifact` call. Iterate on validator errors with the validator only.
- Call `render_artifact` once validation succeeds. If rendering fails after validation, stop, record the blocker, and choose another delivery path instead of repeated visible retries.
- If an inline chart/table widget fails after one targeted retry, continue the analysis through another appropriate surface and note the omission reason.

## Hosted MCP Artifact Publishing

- Use `export_artifact_package` when a validated MCP app report or dashboard needs a hosted Site Creator link.
- The exported package must preserve the canonical `datascience-artifact-widget.html` runtime and its shared chart detail widget. It should bootstrap the hosted page with the validated payload while also serving `/api/manifest`, `/api/snapshot`, `/api/package`, `/api/source-file`, and `/api/inline-chart-widget` for the runtime.
- Do not rebuild the report as standalone HTML, inline CSS charts, or a separate one-off viewer. Hosted sharing is a packaging step for the current artifact, not a second rendering implementation.
- Treat Site Creator exports as read-only reader surfaces by default: hide artifact editing controls and remove `Publish to Sites` from hosted export menus. Authoring should happen in the MCP artifact, followed by a new export/deploy.
- Keep static HTML and PDF exports content-only: include the report or dashboard title, narrative, charts, tables, and source details, but omit the interactive top bar and app-only controls.
- Keep Site Creator access at `workspace_all` by default unless the user explicitly requests narrower access.

## Encoding Rules

- Bind color, series, grouped, or stacked behavior only when there is a meaningful second categorical dimension beyond the x/y category, such as segment, product line, period plus component, or observed series.
- Treat `by <dimension>` in a chart title, subtitle, or visible header as an encoding contract. An x/y axis dimension already satisfies that contract. If `<dimension>` is not on an axis and is not otherwise visibly encoded through color/series, grouped or stacked marks, faceting, or direct labels, remove `by <dimension>` from the visible text. For `render_chart`, a time or category x-axis chart titled `... by segment` or `... by market` must bind that second dimension through `chart.fields.color.field` or an equivalent visible grouping rather than only retaining it in the source table.
- When a grouped chart uses color, series, grouped, stacked, or faceted behavior, make the group names visible with a legend or direct labels. A chart does not satisfy a `by <dimension>` title if the reader cannot identify the rendered groups from the chart itself.
- Do not bind color, series, grouped, or stacked behavior to the same category already used for x or y just to color bars. A bar chart whose x-axis is `modality` and y-axis is `delta` should not also color by `modality`; use palette styling, direct labels, or a single mark color instead.
- Hide legends for single-series charts. Prefer direct labels when the axis or table labels already name the categories.

## Surface Split

- Dashboard skills own monitoring and exploration: KPI hierarchy, chart-first canvas, dashboard-wide filters, neutral markdown cell headers, and operational QA.
- Report skills own answer-first synthesis: audience, findings,
  insight-led markdown cell headers, markdown narrative cells, section evidence, recommendations, citations, caveats, export, and reproducibility.
- Shared code owns mechanics: manifest normalization, JSON IO, markdown page/cell header rendering, source safety, sensitive payload checks, and reusable validation primitives.
- Shared chart support lives in `src/analytics-app/scripts/chart_contract.py`. Dashboard and report validators should import the same supported type list, palette roots,
  series-shape checks, mixed-metric checks, and mixed-scale checks so newly added or removed native chart types do not drift between surfaces.
- Shared chart presentation support lives in `src/analytics-app/charting/chart-contract.ts`, `src/analytics-app/charting/chart-capabilities.ts`, and `src/analytics-app/scripts/chart_contract.py`. Keep palette kind, legend behavior, value label,
  and reference-line options declared in the manifest and validated in both dashboard and report artifacts before adding one-off renderer behavior.
- Shared design support lives in `src/analytics-app/scripts/design_contract.py`. Validators should require a structured `DESIGN.md` without freezing users out of artifact-level customization.

## Report Mode Boundary

MCP app reports and HTML reports are separate delivery modes. An MCP app report should use `render_artifact` for the in-Codex reader handoff and should not also generate a canonical static `report.html` as part of the same report run. When Google Docs conversion or Google Slides conversion is required, choose the HTML report mode in $build-report instead. HTML report charts should be generated through the Seaborn template workflow and embedded as PNG images.
