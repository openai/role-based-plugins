# Dependencies

## How tool references work

Data Analytics plugin files use lane placeholders such as `~~structured_data` for whatever source the user connects or provides in that category. For example, `~~structured_data` might mean a warehouse connector, SQL runner, API/CLI result, pasted query output, uploaded file, or schema description.

The plugin is tool-agnostic. It describes workflows in terms of analysis lanes rather than one required stack. Direct connectors give the best experience, but the workflows should still be useful with pasted results, SQL snippets, screenshots, exports, or uploaded files.

## Dependencies for this plugin

| Category | Placeholder | Providers | Purpose |
| --- | --- | --- | --- |
| Data warehouse | `~~structured_data` | Databricks, BigQuery, Snowflake, Redshift, PostgreSQL, MySQL | Query tables, explore schemas, and produce result sets. Databricks, BigQuery, and Snowflake are declared in `.app.json` as app-backed connector choices. |
| Notebook lab | `~~notebook_lab` | Hex, Deepnote, Jupyter | Iterate, preserve reusable code, and support richer exploratory work. Hex and Deepnote are declared in `.app.json` as app-backed connector choices. |
| Behavior signals | `~~behavior_signals` | Amplitude, Mixpanel, Mixpanel Headless | Analyze product event trends and funnels. Amplitude and Mixpanel are declared in `.app.json`; Mixpanel Headless is a companion plugin/skill path when installed. |
| Dashboards and BI | `~~dashboards_or_bi` | ThoughtSpot, Omni Analytics, Metabase, dashboard/BI app | Inspect dashboard metadata, metric definitions, widget SQL, and BI answers. ThoughtSpot, Omni Analytics, and Metabase are declared in `.app.json` as app-backed connector choices. |
| Team communication | `~~team_communication` | Slack, Microsoft Teams | Search recent decisions, blockers, owner confirmations, and links to durable artifacts |
| Email context | `~~email_context` | Gmail, Outlook Email | Inspect relevant message threads, stakeholder context, and follow-up history |
| Calendar context | `~~calendar_context` | Outlook Calendar | Check meeting timing, attendees, and operating cadence context |
| Company docs | `~~company_docs` | Google Drive, SharePoint, Google Docs, Google Slides, Notion | Read workspace knowledge, PRDs, metric docs, strategy docs, and source caveats |
| Sheet workspace | `~~spreadsheet_workspace` | Google Drive, SharePoint, Google Sheets | Review small exports, manual QA, and stakeholder-friendly tables |
| Presentation surface | `~~presentation_surface` | Google Drive, SharePoint, Google Docs, Google Slides | Create final charts, dashboards, and share-ready narratives |
| Code repository | `~~code_repository` | GitHub, local checkout | Inspect source logic, model SQL, lineage, tests, and repo context |
| Files, notebooks, or spreadsheets | `~~files_and_notebooks` | Google Drive, SharePoint, local files, uploaded files, notebooks, spreadsheets | Use local or uploaded analysis inputs, notebooks, CSVs, and spreadsheets |
| Application hosting | `~~application_hosting` | Site Creator | Host reports, deployed app links, and previewable interactive artifacts |
| Planning tracker | `~~planning_tracker` | Atlassian, Linear, Asana, Jira | Track analysis requests, owners, deadlines, and dependencies |
| Data operations | `~~operations_logs` | Airflow | Check pipeline freshness, model ownership, lineage, and outage context |
