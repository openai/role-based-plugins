# Data Analytics Plugin

Data Analytics is a Codex plugin for analytics, product strategy, KPI reporting, metric diagnostics, notebooks, visualization, market sizing, validation, and narrative report building. It routes external dependencies through analysis lanes.

It packages data analytics workflows as Codex skills. Bundled public skill folders keep stable frontmatter `name:` values and are discovered recursively under `skills/`. Primary workflow and support skills live at `skills/<skill-name>/SKILL.md`, and report conversion skills live under `skills/build-report/`.

## What's In This Plugin

- `.codex-plugin/plugin.json` - plugin manifest and display metadata.
- `.app.json` - connector mappings for related apps such as Databricks, BigQuery, Snowflake, Deepnote, Mixpanel, ThoughtSpot, Metabase, Slack/Teams, Notion, GitHub, Google Drive/SharePoint, Gmail/Outlook Email, and Outlook Calendar.
- `CONNECTORS.md` - concrete app keys and connector/template IDs for the app-backed analytics connectors this plugin can request.
- `.mcp.json` and `mcp/server.cjs` - MCP tools for Data Analytics chart and table widgets.
- `package.json`, `vite.config.ts`, and `src/` - Vite single-file MCP widget app sources plus the canonical `src/analytics-app/` report artifact runtime. These use `@modelcontextprotocol/ext-apps` for MCP Apps host integration and build back into the HTML files under `assets/`.
- `assets/*.html.gz.b64.part*` - generated compressed self-contained widget resources used by those MCP tools. The small `assets/*.html` files are local browser-test redirects into `src/`.
- `DEPENDENCIES.MD` - analysis lane placeholders and configured dependency notes.
- `src/analytics-app/` - canonical analytics artifact runtime plus supporting scripts, docs, and reference contracts for dashboard/report manifests, snapshots, source files, and package safety checks.
- `skills/` - the data analytics skill library.

## How Codex Should Start

Codex should read $index before doing Data Analytics plugin work. That entrypoint tells Codex how to gather context, then route to the right workflow and deliverable skills.

The README is intentionally a short human-facing inventory. Keep detailed agent instructions in skill files, not here.

## Dependencies

Data Analytics plugin files use lane placeholders such as `~~structured_data` for whatever tool, connector, MCP server, plugin-provided skill, pasted result, uploaded file, or schema description is available in that category. The plugin can request app-backed Databricks, BigQuery, Snowflake, Deepnote, Mixpanel, ThoughtSpot, and Metabase access when those connectors are available and authorized. Mixpanel Headless remains a companion plugin/skill path rather than an app-backed connector mapping.

The plugin is tool-agnostic. It describes workflows in terms of analysis lanes rather than one required stack. See [DEPENDENCIES.MD](DEPENDENCIES.MD) for the provider options for each lane. Site Creator is the application hosting lane for previewable prototypes, hosted dashboards, and analytical apps.

## Data Widgets

The plugin includes widget tools:

- `render_chart` renders reviewed query results as a compact chart. Use it only when an MCP widget surface is selected and safe. The Vite source lives in `src/`; run `npm run build` from this plugin directory after editing widget source so the compressed generated assets stay in sync with the MCP resources. Multiple chart instances keep targeted payload and display-mode updates isolated from one another; after a chart receives its payload it does not keep polling shared host globals that may point at a later chart result.
- `render_table` renders reviewed query preview rows or lookup rows as a compact sortable table. After running a durable query, use it to show a small deterministic preview of the rows that support the analysis. Follow the current MCP table schema.
- `render_artifact` renders a complete report or dashboard manifest with a bounded snapshot inside the MCP Apps host. Use it as the default in-Codex viewer/handoff instead of asking the user to run a localhost server or open a static HTML file. Pass the reviewed manifest, bounded snapshot, inline-safe sources, and package metadata directly to the tool. Native artifact charts follow the MCP artifact tool schema and must be validated before rendering.
- `validate_artifact` runs the same report/dashboard artifact normalization and validation without attaching a widget output template. Use it while iterating on artifact manifests and snapshots, then call `render_artifact` once validation succeeds. Do not use repeated render attempts as validation; invalid renders can leave broken placeholder cards in the host UI. Use the canonical artifact snapshot shape: `snapshot.datasets` is an object keyed by dataset id, and each dataset value is a plain array of reviewed row objects. Do not put `{columns, rows}` table objects inside `snapshot.datasets`; that shape is only a compatibility fallback. Use `source.query` when query provenance, an execution timestamp, or query text should travel with the visual. Shared widget and app payload rules live in [`_shared/analytics-app-core.md`](_shared/analytics-app-core.md). Keep root skills delivery-mode neutral; apply those rules only after MCP widget or artifact rendering is selected.
- `export_artifact_package` materializes a validated artifact payload as a Site Creator-ready Cloudflare Worker package. Use it for hosted sharing of MCP app reports and dashboards so the deployed site preserves the real artifact runtime, `/api/manifest`, `/api/snapshot`, `/api/package`, `/api/source-file`, `/api/inline-chart-widget`, and the inline-safe source text. Do not hand-roll a separate standalone HTML renderer for MCP artifact publishing.

The compact chart and table widgets do not generate per-widget detail pages or ask Codex to open external URLs. Chart expansion stays inside the MCP Apps host. Use `tests/widget-render-harness.html` to smoke-test multiple chart instances side by side.

These tools are for presentation of already-produced analysis results or small query-backed result slices. Include reviewed analytical dimensions such as customer, account, company, segment, and product names when they are relevant to the analysis. Do not send hidden reasoning, credentials, secrets, or direct personal contact/payment identifiers to a widget. Use durable reports, dashboards, notebooks, Site Creator, or shared HTML when the result needs broad sharing, larger data, filters, or longer narrative context.

## Public Skills

### $index

Required entrypoint and routing skill for the plugin. It tells Codex how to start, how to gather context, how to route the request, and how to finish with a validated answer or artifact.

### $gather-business-context

Gather enough business and product context to frame an analysis correctly. Use it to find source-of-truth docs, owner context, launch history, decision history, experiments, incidents, customer context, and metric or workflow background.

### $analyze-data-quality

Evaluate whether a dataset is reliable enough to use. Use it for freshness, grain, duplicates, missingness, outliers, schema drift, broken joins, temporal anomalies, distribution shifts, unexpected categories, and referential-integrity checks.

### $metric-diagnostics

Investigate metric movement. Use it for spikes, drops, regressions, anomalies, segment concentration, contribution analysis, mix-shift questions, waterfall/bridge analysis, source reconciliation, and root-cause analysis, then route the final report or memo artifact through $build-report.

### $jupyter-notebooks

Create, scaffold, edit, and validate Jupyter notebooks for reproducible data analytics work. Use it for analysis scaffolds, experiment readouts, modeling, data-quality checks, notebook handoff, and SQL/Python analysis behind reports.

### $visualize-data

Design and QA quantitative charts. Use it to choose chart types, refine chart narrative, reduce clutter, improve labels and annotations, apply visual hierarchy, check accessibility, and make report/dashboard/notebook visuals production-ready.

### $validate-data

QA an analysis before sharing. Use it to review methodology, source selection, SQL/query logic, calculations, analytical pitfalls, chart integrity, required caveats, and whether stakeholder-facing conclusions are supported by evidence.

### $build-report

Build report app artifacts with a full report grid and canonical static `report.html` export. Use it for executive, product, business, and technical reports; it loads executive or technical report specifications based on the audience and auditability needs. The MCP artifact app is the default in-Codex reader handoff when payload bounds allow; the static export is the compatibility surface for Google Docs and Google Slides conversion.

### $build-dashboard

Build analytical dashboards, scorecards, monitoring pages, BI views, MCP artifact dashboards, BI platform dashboards, Streamlit dashboards, Site Creator app dashboards, durable BI dashboards, and static HTML dashboards. Use it to define dashboard structure, hero metrics, sections, filters, drill-downs, chart inventory, data-source shape, summary-first hierarchy, delivery mode, and dashboard QA. Generated dashboard apps share the same analytics-app foundation as generated report apps while keeping dashboard-specific intent and validation. Use the MCP artifact app as the default generated-dashboard viewer when payload bounds allow.

### $report-to-google-doc

Convert an existing local or blob-hosted HTML report into a polished native Google Doc while preserving structure, tables, charts, links, and source notes.

### $report-to-google-slides

Convert an existing HTML analytics report into a polished native slide deck while preserving core claims, charts, tables, caveats, and sources.

### $report-to-pdf

Convert an existing static Data Analytics report export into a verified PDF artifact while preserving report content and omitting app-only controls.

### $design-kpis

Design compact success frameworks. Use it to recommend goals, primary KPIs, driver metrics, guardrails, metric definitions, and measurement plans for launches, experiments, initiatives, models, or operating programs.

### $market-sizing

Estimate market or commercial opportunity. Use it for TAM/SAM/SOM, spend pools, revenue pools, customer counts, unit volume, market-entry opportunity, sensitivity analysis, and assumption-led sizing models.

### $kpi-reporting

Prepare leadership-ready KPI updates, scorecards, business reviews, MBR/QBR summaries, and recurring performance readouts. Use it to lock definitions, present status, explain trends, validate drivers, and separate KPI health from noise.

### $product-business-analysis

Analyze product or business data to inform decisions. Use it to frame the question, develop hypotheses, combine quantitative evidence with connected context, and recommend a practical path.
