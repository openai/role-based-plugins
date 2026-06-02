---
name: salesforce
description: Agentforce Sales connector guide for Sales workflows that use Salesforce for CRM reads, drafts, notes, account plans, Agentforce assignments, or proposed record changes.
---

# Salesforce User Guide

Use this as the Salesforce-specific user guide whenever the user or workflow is using Salesforce as the CRM connector, including drafting Salesforce-backed updates, summaries, notes, account plans, Agentforce assignments, or proposed record changes. Keep the surrounding workflow skill authoritative for the sales task itself; this guide adds Agentforce Sales-specific metadata discovery, SOQL query selection, record reads, links, and write safety.

Do not use this guide when the workflow uses another CRM connector or no CRM connector.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before answering, searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`. Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance. Do not read or reinterpret raw Sales state files unless preflight fails, local shell access is unavailable, or the user explicitly asks for raw state inspection.

Use returned user context as lookup hints and drafting guidance. Always verify Salesforce object and field metadata before querying or writing; saved user context does not replace `describe_global`, `describe_sobject`, record type checks, or write-safety confirmation.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Connector Boundary

The Salesforce CRM app in the Sales plugin is the third-party Agentforce Sales connector, bound in `.app.json` to app id `REPLACE_WITH_SALESFORCE_APP_OR_CONNECTOR_ID`.

Use only the Agentforce Sales surfaces that are actually exposed:

- Metadata and identity: `describe_global`, `describe_sobject`, `get_user_info`.
- Record lookup and reads: `get_record_id_by_name`, `get_record_details`, `get_activity_history`.
- Querying: `soql_query` only.
- Sales-specific reads: `query_calendar_events`, `get_account_plan`, `query_agent_type`, `summarize_conversation_transcript`.
- Writes and mutating sales workflows: `create_record`, `update_record`, `create_account_plan`, `assign_target_to_sdr`.

Do not imply support for SOSL, global text search, query continuation, Bulk API, Composite API, Data 360, Tableau Analytics, Prompt Builder, Flow invocation, arbitrary invocable actions, generic Apex REST calls, delete, or upsert-by-external-id unless a future installed app explicitly exposes those tools. For cross-object keyword search, large exports, high-volume write jobs, delete/upsert needs, or analytics surfaces outside the exposed Agentforce Sales actions, state the missing connector surface and ask for a narrower Salesforce scope, exact object/field, exact identifier, or another approved tool.

## Discovery And Identity

1. Prefer discovery over guessing. Use `describe_global` for object matching and `describe_sobject` for field matching before non-obvious queries or writes.
2. Use `get_user_info` for requests involving "my", "me", or the current Salesforce owner.
3. In `describe_sobject`, check field API names, labels, data type, filterability, createability, updateability, nullability, picklist values, references, relationship names, and record type details when those properties affect the task.
4. Use record type fields when record type changes defaults, picklist choices, required fields, or layout-sensitive behavior.
5. For relationship queries, do not guess relationship names. Use metadata for relationship field paths and child relationship names.
6. Use user-facing labels in final answers when known, and API names only when needed for precision or follow-up.

## Record Disambiguation

1. Prefer exact name or id matches before broad text matching when locating records.
2. Treat broad `LIKE '%...%'` filters as candidate discovery, not proof of the canonical record.
3. Account names can match regions, subsidiaries, brands, domains, and email-like records. Do not silently pick the first result when multiple plausible records remain.
4. Use available business context such as country, website, industry, owner, active opportunities, recent tasks, or the user's wording to disambiguate.
5. If one additional targeted filter will not clearly disambiguate the result, present the candidate records to the user before taking write actions or using the record as the basis for a deal summary.

## Reads And Queries

1. Before authoring non-trivial SOQL, identify the target object, fields needed, filters, sort or limit requirements, whether the query is for display or analysis, and whether selectivity is a concern.
2. Use `soql_query` for structured reads, relationship fields, ordering, aggregation, semi-joins, anti-joins, and filters on fields Salesforce marks as filterable.
3. Generate the simplest correct query: select only fields needed for the sales task, include `Id` whenever records may be shown, linked, or used for follow-up, and add a reasonable `LIMIT` unless the user asked for a complete scoped result.
4. Prefer filtering in SOQL rather than post-filtering. Use aggregates for counts and grouped summaries instead of loading unnecessary records.
5. Confirm relationship names before querying. Use child-to-parent traversal for parent data from child rows, parent-to-child subqueries for child rows from parent records, and aggregate queries for rollups.
6. Evaluate wildcard usage carefully. Broad `LIKE '%...%'` filters are candidate discovery, can defeat indexes, and are not proof of the canonical record.
7. This connector does not support SOSL. If the user asks for keyword search, object-unclear search, cross-object search, or text search in fields that are readable but not SOQL-filterable, say that Agentforce Sales only exposes SOQL and ask for a narrower object, field, or exact identifier.
8. This connector does not expose a separate query continuation tool. Use a SOQL `LIMIT` when total rows must be capped, tighten filters for high-volume requests, and state the connector limit when the user needs complete export-style coverage.

## Reads And Display Context

- Prefer explicit field projections for business facts and exports.
- Use `get_record_id_by_name` for exact or near-exact name-to-id lookup when the next step needs a Salesforce id.
- Use `get_record_details` when the task needs presentation-ready context such as layout fields, optional fields, display values, child relationships, or record-type-sensitive UI metadata. Pass both `Compact` and `Full` layout types unless the user asks for a narrower UI read.
- Use `get_activity_history` for Account, Contact, Lead, or Opportunity activity summaries.
- Use `query_calendar_events` for Salesforce calendar or meeting questions.
- Use `get_account_plan` for account strategy, plan, relationship, challenge, or status context.
- Use `summarize_conversation_transcript` only after resolving a specific VoiceCall or VideoCall id. If the call is unknown, query VoiceCall and VideoCall separately with `soql_query`, then ask the user which call to summarize.
- If a requested field is absent from a UI/layout-oriented response, retry with explicit fields before concluding the field is unavailable.

## Query Traps And Recovery

- Do not use `WHERE` filters on fields that Salesforce reports as not filterable.
- Long text and rich text fields are common traps: they may be readable in `SELECT` but rejected in `WHERE`.
- A key example is `Task.Description`: do not use `WHERE Description LIKE ...`. Because Agentforce Sales does not expose SOSL, ask for a narrower filterable field, exact record, date/owner/status filter, or another approved search surface.
- If a field or object is unknown, call `describe_sobject` or use a narrow `FieldDefinition` SOQL query before retrying.
- If the first result set is too broad, tighten by object, date, owner, status, or another confirmed filterable field rather than adding unsupported text filters.
- Prefer standard, commonly present fields on `Account`, `Opportunity`, `Contact`, `Task`, and `Event` before optional org-specific fields or relationship-heavy objects.
- Do not assume optional fields or objects exist, including `CurrencyIsoCode`, `AnnualRevenue`, `OpportunityTeamMember`, `AccountTeamMember`, `Opportunity.Contact`, `OpportunityContactRole.Name`, `PricebookEntry` SOSL, or `FieldDefinition.IsCustom`. Describe the object/field first, or omit the optional enrichment when the standard record data is enough.
- Cap recovery from invalid schema/query errors. After two focused schema or query-shape failures for the same fact, fall back to safer standard fields, SOSL, exact record reads, or a clear evidence gap instead of continuing exploratory retries.
- Distinguish connector auth/runtime failures from schema misses. A message that explicitly says reauthentication is required should produce a re-auth CTA; MCP startup, handshake timeout, transport, or availability errors should be described as connector readiness/runtime issues and should not be framed as proof that the user must reconnect.

## Writes

Write only when the user explicitly asks to create or update Salesforce data, create an account plan, or assign a Contact or Lead to Agentforce Lead Nurturing.

- Confirm object API name, record id, and field API names before writes.
- For `update_record`, send only changed fields in `fields`. For Agentforce AI-generated text updates on core sales objects, only use fields the tool permits, especially `Description` when that is the documented allowed target.
- For `create_record`, send only intended create fields and include record type fields only when record type affects defaults, picklists, or createability.
- Use `create_account_plan` for account plan creation instead of generic record creation. Its body must include `AccountId`, `Name`, the challenge, competitive, relationship, and strategy fields, `StartDate`, and `Status`; resolve the account and gather, derive from grounded Salesforce/source evidence, or ask for any missing required values before calling the tool.
- Before `assign_target_to_sdr`, call `query_agent_type` to list available Agentforce Lead Nurturing or SDR agents, present the choices, and get the user's selection. The target must be a Contact or Lead id.
- Stop if the user asks to delete, upsert by external id, call Apex REST, invoke Flow, or run arbitrary custom Salesforce automation; those operations are outside this Agentforce Sales connector surface.
- After any write, inspect the response and, when the response does not prove the outcome, verify with returned fields, `get_record_details`, or a narrow `soql_query` before summarizing the result.

## Agentforce Sales Workflows

- Use `create_account_plan` and `get_account_plan` for account planning requests, but report Salesforce or connector errors plainly if the org does not support the AccountPlan object or the action returns unsupported-object errors. If the user only provides an account name or id, treat that as the target account, not as enough input to create the plan; first resolve `AccountId`, propose or collect the required plan body, and proceed only when the required fields are present.
- Use `query_agent_type` and `assign_target_to_sdr` for Agentforce Lead Nurturing assignment only when the user asks for that assignment. Treat assignment as a mutating workflow.
- Use `query_calendar_events` for Salesforce Event records tied to calendar or meeting questions.
- Use `summarize_conversation_transcript` for voice or video call summary requests after resolving the call id with SOQL or user input.

## Output

Return concise, business-facing results. Include clickable Salesforce record links only when a runtime source provides the org base URL, record URL, or instance URL.

Link rules:

- Prefer a record URL returned by the connector.
- If connector metadata exposes an org or instance base URL, construct links with that base: `https://<org-or-instance-base>/lightning/r/<ObjectApiName>/<Id>/view`.
- If only `Id` is known and no trusted base URL is available, show the object label and id instead of inventing an org-specific URL.
