# Source Intake

Use this reference to gather enough information to build a source-backed semantic-layer skill without turning intake into a long questionnaire.

## Minimum Viable Intake

Proceed when the user gives:

- target product, feature, business area, or team;
- at least one seed source, such as a table namespace, verified dashboard, raw SQL query, data doc, code repository, team communication channel, or existing local skill;
- permission to read the supplied sources, when permission is not already implied by the user's request and available connectors.

Ask a concise follow-up only when the missing answer changes the crawl or destination materially. Good first follow-ups are: "What product or business area should this semantic layer cover?", "Which source should I treat as canonical if these disagree?", or "Where should the generated skill live?"

## Multiple Areas

Create separate semantic-layer skills for separate product or business areas by default. If the user asks for multiple areas, collect a target area and seed inventory for each one, then run the crawl and synthesis separately so each output stays compact and triggerable. Use a shared/common semantic layer only when multiple areas depend on the same substantial set of canonical metrics, tables, joins, or caveats.

## Seed Item Menu

Ask for any seed items the user has and explain why each kind can help. Tailor the menu to source lanes they have not already supplied instead of repeating known inputs. Do not imply that all inputs are required.

Use or adapt this intake prompt:

```text
Send any seed items you have. Even one is enough to start; more just improves coverage:

- Tables, namespaces, catalogs, or schemas: helps identify core tables, grain, joins, freshness, and query history.
- Verified dashboards or dashboard links: helps identify canonical metrics, dimensions, filters, and reviewed SQL.
- Raw SQL queries, query files, or report/notebook SQL: helps recover implemented table choices, joins, filters, aggregations, time windows, and metric formulas.
- Team communication channels or threads: helps find data questions, announcements, metric clarifications, and known gotchas.
- Data docs, glossaries, PRDs, or launch docs: helps anchor metric definitions, table meanings, owners, and caveats.
- Code repositories or local repo paths: helps inspect transformation code, tests, model docs, lineage, and source-of-truth logic.
- Existing local skills or data documentation skills: helps reuse prior semantic context and avoid duplicate work.
- Core metric names or business questions: helps prioritize the crawl around the decisions the skill should support.
```

If the user supplies only the area name and no seed items, ask for one or more seed items from this menu before crawling. If they already supplied some seed items, ask once for any missing high-value lanes that could improve coverage, then proceed from the available inventory. If they cannot provide any seed items, offer a draft-only semantic-layer skill skeleton and label it as unseeded.

## High-Value Inputs

Request these inputs when available, and record unknowns explicitly when they are not available:

| Input | What To Ask For | Why It Matters |
| --- | --- | --- |
| Area and audience | Product or business area, intended users, common data questions | Sets skill scope and trigger language |
| Tables and namespaces | Catalog, schema, namespace, table names, data warehouse, or workspace | Seeds table metadata, lineage, query history, and table-choice guidance |
| Verified dashboards | Links or IDs, owner, verified status, metric panels to prioritize | Identifies core metrics, dimensions, filters, and reviewed SQL patterns |
| Raw SQL queries | Pasted SQL, query files, notebook/report SQL, saved query links, author, and intended business question | Reveals implemented joins, filters, aggregation logic, date windows, dimensions, and metric formulas |
| Team communication channels | Channel names, threads, time window, announcement or data-question focus | Captures ambient context, corrections, deprecations, and open metric debates |
| Data docs | Docs, PRDs, metric dictionaries, table docs, glossaries, launch docs | Supplies authoritative metric and table definitions |
| Code repositories | Repo names, local paths, model directories, transformation packages, pipeline code | Reveals transformation logic, tests, owners, and source-of-truth grain |
| Local skills | Skill names, plugin names, or permission to search local skills | Reuses existing data documentation and avoids duplicating local context |
| Destination | Standalone local skill by default, existing plugin only if requested, sharing needs | Determines where the generated semantic-layer skill should live |
| Freshness window | Recent query-history or team communication window, expected update cadence | Prevents stale usage patterns from overriding current definitions |
| Automation preference | Whether to poll sources weekly, preferred day or time, and review versus auto-update boundary | Keeps the semantic-layer skill current without surprising recurring writes |
| Permission boundaries | Allowed sources, private channels, sensitive data rules, install approval | Keeps crawling and generated files within the user's intent |

## Source Coverage Levels

Use these labels in final output:

- `Seeded`: one useful source was crawled, but important lanes are missing.
- `Directional`: two or more lanes agree on core tables or metrics, but gaps remain.
- `Strong`: authoritative docs or transformation code plus dashboard or table evidence support the key facts.
- `Conflicted`: important definitions disagree and need user or owner resolution.
- `Blocked`: required connector, permission, source, or destination is unavailable.

## Intake Defaults

- Prefer direct links, table names, repo paths, and channel names over broad descriptions.
- Treat verified dashboards and transformation code as higher-value starting points than team communication discussion.
- Use recent query history and team communication discussion as observed behavior, not as canonical definitions by default.
- If the user says "build what you can", produce a partial skill and name the missing source lanes.
- After a direct creation or refresh with a usable source inventory, offer weekly polling as an optional follow-up instead of assuming the user wants a recurring automation.
- If the user asks only for a source audit, stop before creating files and return a crawl plan plus coverage assessment.
