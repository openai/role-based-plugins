---
name: hubspot
description: HubSpot CRM connector guide for Sales workflows that use HubSpot for CRM reads, drafts, notes, or proposed record changes.
---

# HubSpot User Guide

Use this as the HubSpot-specific user guide whenever the user or workflow is using HubSpot as the CRM connector, including drafting HubSpot-backed updates, summaries, notes, or proposed record changes. Keep the surrounding workflow skill authoritative for the sales task itself; this guide adds HubSpot-specific access checks, object lookup patterns, pagination, URLs, and write safety.

Do not use this guide when the workflow uses another CRM connector or no CRM connector.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before answering, searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`. Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance. Do not read or reinterpret raw Sales state files unless preflight fails, local shell access is unavailable, or the user explicitly asks for raw state inspection.

Use returned user context as lookup hints and drafting guidance. Always verify HubSpot object, property, and enum metadata before querying or writing; saved user context does not replace `get_user_details`, `search_properties`, `get_properties`, or write-safety confirmation.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Rules

1. Call `get_user_details` first; check object read/write availability.
2. Clarify scope: object type, owner/team, pipeline, timeframe, stage, and whether writes are requested.
3. Use `search_properties` for fields, max 5 `keywords`; use `get_properties` for enum values.
4. Use `search_crm_objects` for records, counts, filters, pagination, and associations; use `get_crm_objects` for known IDs. Do not use deprecated `search` or `fetch`.
5. Include clickable HubSpot URLs with UTM params for returned records. State filters, totals, pagination, and whether analysis is sampled.

## Writes

Before `manage_crm_objects`, show exact proposed changes and get approval:

| Object Type | ID | Property | Current Value | New Value |
|---|---:|---|---|---|

For repeated writes, the user may approve a specific reviewed batch after seeing the exact proposed changes. Do not offer a blanket confirmation bypass for the chat.

Batch at most 10 objects. Confirm associations explicitly. Do not write inferred data or overwrite user-entered context without clear consent.
