# Connector Playbook

Use this reference to choose source-specific tools, handle missing connectors, and keep evidence collection safe.

## Connector Resolution

For every user-supplied link, table, channel, repo, or artifact:

1. Identify the source type and the most specific connector or tool that can read it.
2. When `tool_search` is available, search for that connector or tool by product and action, such as `table metadata`, `query history`, `team communication search`, `document read`, `code repository`, or `wiki page`.
3. Prefer installed first-party connectors and dedicated source tools over generic web or browser access for private workspace sources.
4. If the relevant connector is not installed or not callable, ask whether to install or connect it when an install flow exists. If no install flow is available, ask for an export, pasted excerpt, local checkout, SQL text, or alternate source.
5. Record skipped or manually substituted sources in the source inventory.

Do not use `request_plugin_install` unless a single exact connector or plugin is known installable in the current environment. If the user explicitly asked for a connector that is not available and no install tool can install it, say that and give the closest manual fallback.

## Source-Specific Guidance

### Tables And Query History

Use the available data warehouse connector, metadata API, or SQL/query-history tool for table metadata, schema comments, owners, lineage, and query history. Use the plugin manifest to identify declared warehouse connector choices when the user has not named a specific source. Crawl namespaces from broad to narrow: catalog and schema first, then specific table metadata and representative query patterns.

Capture:

- full table names and aliases;
- table purpose from comments, docs, owners, and usage;
- grain, primary entities, join keys, partitions, freshness, and update cadence;
- common filters, dimensions, date columns, and aggregation patterns from query history;
- evidence of deprecation, replacement tables, or owner warnings.

Avoid selecting raw data rows unless the user asks and the data is safe to inspect. Metadata, SQL text, and aggregated query-history patterns are usually enough.

### Verified Dashboards

Use the dashboard's native connector or relevant BI/dashboard tool when available. Inspect dashboard metadata, widget titles, query text, parameters, filters, metric naming, dimensions, and linked source tables.

Prioritize dashboards the user identifies as verified, canonical, owner-reviewed, or launch-critical. Treat dashboard SQL as high-signal usage evidence, but verify business definitions against transformation code or docs when possible.

### Raw SQL Queries

Use user-supplied SQL text, saved query links, query files, notebook SQL, report SQL, or exported query history as a source lane. Prefer parsing or reading the SQL before executing it. Capture referenced tables, joins, filters, grouping dimensions, metric formulas, time windows, parameters, comments, owner or author context, and the business question the SQL was meant to answer.

Treat raw SQL as implemented usage evidence unless it is tied to an authoritative dashboard, owner-reviewed report, transformation repository, or data documentation. If SQL conflicts with docs, transformation code, or verified dashboards, record the conflict and prefer the higher-precedence source. Do not copy sensitive literals, customer identifiers, credentials, raw row samples, or long proprietary snippets into generated skill files; summarize the semantic pattern and preserve a source path or link.

### Team Communication Channels

Use the relevant team communication connector for named channels, threads, canvases or shared notes, files, and search. Start with pinned material, channel descriptions, recent announcements, and threads matching table names, metric names, dashboard names, or owner names.

Capture concise summaries with links. Do not paste long message transcripts into generated skills. Distinguish announcements and owner clarifications from speculative debugging chatter.

### Data Documentation

Use the connector that matches the link or artifact: document store, wiki, code-hosted markdown, local files, or another installed document connector. Extract definitions, owners, metric formulas, inclusion and exclusion criteria, example queries, table glossary entries, and freshness notes.

If docs disagree with dashboards or code, record the conflict and inspect recency, owner, and downstream usage before choosing a canonical definition.

### Code Repositories And Local Code

Use the relevant code repository connector, repository CLI, or local filesystem when the repo is already checked out. Search for transformation models, SQL, pipeline jobs, notebooks, tests, schema files, README docs, exposures, lineage configs, and table-producing jobs.

Prefer structured project tools when available, such as transformation metadata commands or repo-specific lineage docs. Use `rg` for local text search. Inspect enough surrounding code to understand table grain and filters before summarizing a model.

### Existing Local Skills

Search installed and workspace skill locations for data-area context before creating a duplicate semantic layer. Useful locations often include user-installed skill directories, active plugin skill directories exposed by the current runtime, repository `skills/` directories, and any user-supplied skill path.

Search by area name, table names, metric names, dashboard slugs, namespaces, and terms such as `metric`, `dashboard`, `transformation`, `table`, `semantic`, and `analytics`. Treat existing skills as helpful hints unless they cite durable sources or the user confirms they are current.

## Permission And Safety Boundaries

- Reading user-supplied sources is usually in scope; posting, editing, deleting, exporting broadly, changing dashboards, modifying repos, or installing connectors requires explicit approval.
- Do not store credentials, secrets, raw personal data, row-level customer examples, or long private messages in generated skill files.
- When a source contains sensitive details, summarize the semantic fact and link to the source instead of copying the content.
- If a connector returns more data than needed, reduce it to table names, query patterns, metric definitions, and provenance before writing artifacts.
