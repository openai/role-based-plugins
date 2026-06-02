# Data Analytics Connectors

This plugin is tool-agnostic at the skill layer, but it declares these concrete analytics connectors so Codex can request the app-backed path when the user's analysis needs a connected source.

| Lane | App key | App/template or connector id | Connector id | Source of truth |
| --- | --- | --- | --- | --- |
| Structured data | `databricks` | `templated_apps_Databricks` | `Replace with the target workspace Databricks connector id if needed` | `plugins/databricks/CONNECTORS.md` |
| Structured data | `bigquery` | `REPLACE_WITH_BIGQUERY_APP_OR_CONNECTOR_ID` | `REPLACE_WITH_BIGQUERY_APP_OR_CONNECTOR_ID` | `BigQuery connector schema documentation` |
| Structured data | `snowflake` | `templated_apps_Snowflake` | `Replace with the target workspace Snowflake connector id if needed` | `plugins/snowflake/CONNECTORS.md` |
| Notebook lab | `deepnote` | `REPLACE_WITH_DEEPNOTE_APP_OR_CONNECTOR_ID` | n/a | target workspace app registry |
| Behavior signals | `mixpanel` | `REPLACE_WITH_MIXPANEL_APP_OR_CONNECTOR_ID` | n/a | target workspace app registry |
| Behavior signals | n/a | Mixpanel Headless companion plugin | n/a | Mixpanel Headless companion plugin bundle |
| Dashboards or BI | `thoughtspot` | `REPLACE_WITH_THOUGHTSPOT_APP_OR_CONNECTOR_ID` | n/a | target workspace app registry |
| Dashboards or BI | `metabase` | `templated_apps_Metabase` | n/a | templated app registry |

Use these connectors for source discovery, schema or event inspection, query or dashboard reads, query provenance, notebook context, and semantic-layer source crawling when they are available and authorized. If the relevant connector is unavailable, the skills should continue from exported query results, SQL snippets, schema descriptions, dashboards, notebooks, or manual source material when that is sufficient for the user request.
