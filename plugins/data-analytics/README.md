# Data Analytics

Answer product and business questions with data, explain why metrics changed, and turn analysis into reports, dashboards, and clear decisions.

## When to use this plugin

Use Data Analytics when you need to understand product or business performance, explain why a metric changed, define a success measurement plan, assess whether data is trustworthy, or package analysis for stakeholders. You can start from connected data in a data warehouse, dashboards, notebooks, spreadsheets, uploaded files, or pasted context.

## Onboarding

Ask Codex:

`@Data Analytics Help me get started and set up reusable data context for future data work`

Data Analytics has a guided onboarding flow that helps confirm the right data sources, save reusable metric and source-of-truth context you provide, and build a context-specific first analysis prompt.

Onboarding is an interactive, step-by-step conversation. Codex will guide you through setup, ask for approval before making changes, and help you try a first workflow.

Already have a focused task? Start directly with one of the workflows below.

## Example workflows

The primary hero workflow is bolded.

| Workflow | Try this | Skill | Result |
| --- | --- | --- | --- |
| **Analyze a product or business question** | `Analyze activation and recommend where the team should focus next` | `product-business-analysis` | A decision-ready analysis with evidence, measurable opportunities, and a clear recommendation |
| Diagnose a metric movement | `Diagnose why weekly active users dropped last week` | `metric-diagnostics` | A calibrated explanation of verified drivers, likely contributors, unresolved questions, and next actions |
| Design KPIs | `Design a KPI framework for this new product area` | `design-kpis` | A measurement plan with outcome metrics, drivers, guardrails, targets, and validation priorities |
| Prepare a KPI readout | `Turn this month's metrics into a leadership-ready operating update` | `kpi-reporting` | A concise KPI update with actuals, comparisons, validated drivers, and operating implications |
| Build a dashboard | `Build a dashboard for monitoring activation, retention, and conversion` | `build-dashboard` | A source-backed dashboard with metrics, filters, visual hierarchy, QA, and handoff |
| Size a market | `Estimate the market opportunity for this product and show the assumptions` | `market-sizing` | A transparent market or opportunity sizing estimate with sensitivity, uncertainty, and validation priorities |
| Build an analytical report | `Create an executive report explaining the biggest growth drivers this quarter` | `build-report` | A polished report with answer-first narrative, charts, tables, caveats, and source metadata |
| Improve or render a chart | `Turn this analysis into a clear chart for the product review` | `visualize-data` | A production-ready visual with the right chart type, labels, hierarchy, and accessibility checks |
| Create a notebook | `Build a reproducible notebook for this experiment readout` | `jupyter-notebooks` | A clean SQL or Python notebook that can be skimmed, rerun, and extended |
| Work with spreadsheets | `Analyze this workbook and add a polished summary tab` | `spreadsheets` | A verified spreadsheet artifact with formulas, formatting, charts, tables, and a clear readout |
| Validate an analysis | `Review this analysis before I share it with leadership` | `validate-data` | A QA pass covering methodology, sources, calculations, analytical pitfalls, caveats, and conclusion strength |
| Assess data quality | `Check whether this table is reliable enough for our retention analysis` | `analyze-data-quality` | A source-backed quality assessment covering grain, freshness, missingness, duplicates, joins, and material risks |

## Integrations

Data Analytics can use available tools when they are connected:

| Source | Supported integrations | What they unlock |
| --- | --- | --- |
| Warehouses and query tools | Databricks, Databricks Genie, BigQuery, Snowflake | Schema inspection, query-backed analysis, and source-grounded metric investigation |
| Product analytics and BI | Amplitude, Mixpanel, Omni Analytics, Metabase, ThoughtSpot, Statsig | Behavior analysis, dashboard context, experiment evidence, and reusable reporting inputs |
| Notebooks and analytical workspaces | Hex, Deepnote | Reproducible analysis, notebook handoff, and shared analytical context |
| Docs and collaboration | Google Drive, SharePoint, Notion, GitHub, Slack, Microsoft Teams | Business definitions, source-of-truth documents, implementation context, and stakeholder evidence |
| Email and calendar | Gmail, Outlook Email, Outlook Calendar | Supporting context for stakeholder questions, operating cadence, and analytical handoff |

You can also start with spreadsheets, uploaded files, pasted query results, schema descriptions, or manually provided business context.

## Local development

The published plugin does not require users to install Node.js dependencies. For local development of the Data Analytics MCP server and widgets, install dependencies from the plugin directory:

```sh
npm ci
```
