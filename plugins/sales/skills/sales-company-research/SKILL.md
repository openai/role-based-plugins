---
name: sales-company-research
description: Explicit-only Sales workflow for scheduled or index-routed company research that finds durable internal resources, saves high-confidence Sales plugin memory, and asks focused follow-up questions.
---

# Sales Company Research

Run deep company-context research that finds durable, non-obvious resources future Sales workflows should reuse. This skill owns the research workflow: dynamic source discovery, source mapping, candidate ranking, save-versus-review decisions, focused follow-up questions, and the final research response. It uses `sales:user-context` for preflight, memory write policy, state-file structure, and readback.

Use this skill only when it is explicitly invoked, routed by the Sales index, or launched by the Sales Company Research automation. It is not an implicit catch-all for ordinary internal-source lookup, customer question routing, or one-off source finding; those usually belong to `find-key-internal-sources` or the focused Sales workflow that needs the source.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, saving memory, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. In scheduled research mode, do not append onboarding reminders or onboarding CTAs to the completed research response; this pinned research thread should end with the research result and any `Where you can help` questions. If an onboarding obligation matters, leave it to the onboarding thread or fold the underlying source gap into a research question only when it would improve future Sales research.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the research result.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

### Invocation Modes

Use `scheduled research mode` when the request comes from the Sales Company Research automation, heartbeat, or one-time onboarding kickoff. Treat the automation prompt as a thin launcher for this skill; do not require the prompt to repeat source families, ranking rules, save gates, output copy, model, or reasoning instructions.

Use `manual research mode` when the user directly asks Sales to run company research, discover useful Sales resources, fill missing company context, audit available Sales setup sources, or rerun the research after new sources become available.

### Workflow Sources

Resolve source access dynamically from the current tools, available plugins/connectors/apps, `sales_preflight.context.sources`, saved source preferences, current thread context, and any user-provided seeds. The configured Sales source categories are search hints, not an exhaustive provider list and not a readiness claim.

Do not hard-code a customer's connector stack into the workflow or automation prompt. Search across source families that are both available and authorized in the current environment, such as:

- company docs, wikis, knowledge bases, drives, pages, and shared folders;
- internal messaging channels, pinned posts, files, source-of-truth threads, and approved private-channel searches when the user explicitly authorizes or the workflow policy permits them;
- CRM, GTM, forecast, pipeline, territory, account-plan, and book-of-business sources;
- dashboards, BI tools, reporting hubs, data dictionaries, and metric-definition docs;
- email, calendar, meeting notes, transcripts, call recordings, account rooms, and customer handoff spaces;
- issue trackers, project trackers, launch hubs, approval trackers, legal/procurement/security paths, and deal governance sources;
- positioning, competitive, customer-facing asset, customer-story, enablement, and sales-planning libraries.

When a source family is unavailable, unauthorized, rate-limited, or not exposed through tools, turn that gap into a `Where you can help` question only when a pointer or access change would materially improve future Sales workflows.

Use `find-key-internal-sources` as a helper only when ordinary source search is likely to miss the maintained owner, source-of-truth route, channel, or doc family. Keep this skill responsible for final ranking, save decisions, and output.

## Research Workflow

1. Read the Sales preflight payload and current saved user context. Identify unresolved template categories from `../user-context/plugin-author-config/user-context-config.md`, stale or overly generic saved entries, source families already saved, and entries already flagged or saved in the recurring Sales Company Research thread.
2. Build a source-family map before saving. For each target category, name the most plausible source families, likely owner/team or operating terms, candidate resource types, and any available tools or connectors that can search them. Use saved resources and user-provided links as optional seeds, not as anchors that constrain the search path.
3. Search broadly enough to compare authority across source families. Follow source trails from promising hits: linked docs, pinned posts, related hubs, dashboards, tracker references, owner pages, account folder indexes, approval pages, and canonical examples. Do not stop after the first few obviously relevant docs; keep going until each core Sales memory area has either a credible candidate, an already-saved source, or a concrete reason it could not be found.
4. Prefer authoritative interpretation layers over raw connector facts. High-value resources explain how the company operationalizes common Sales concepts: pipeline stage definitions and exit criteria, forecast category usage, close-date norms, new-logo versus expansion distinctions, AE/AM/CSM/SA/overlay responsibilities, approval ownership, territory and segment rules, named-account exceptions, priority-account definitions, deal desk or launch-readiness governance, canonical CRM reports/views, process pages, and tracker definitions.
5. Check the saved set for coverage across core Sales memory areas before finalizing. At minimum, look for credible candidates or concrete gaps for CRM/forecast process, sales planning/data lineage, account/customer docs, deal governance and approval paths, legal/comms/customer-facing claims guardrails, approved positioning or core narrative, GTM/customer-facing asset and enablement hubs, competitive enablement, and customer-story/use-case libraries. If a category has no high-confidence saved source, do a second-pass search using adjacent terms, linked hubs, owner/team names, and source-family synonyms before asking a focused question. Do not treat one saved source as covering adjacent categories unless its contents actually help that workflow family.
6. Track every meaningful source as a walkable source record with label, source family, owner or location when known, stable link or connector-visible reference, what it represents, relevant memory category, freshness or access caveat, and why it was found through a non-obvious route when applicable. A bare title, channel name, meeting name, or go-link is not enough when a stable link or connector reference is available.
7. Rank and dedupe candidates before writing memory. Score candidates against authority, criticality, future Sales workflow impact, company-unique semantics, freshness, non-obviousness beyond ordinary search, durability/revisitability, accessibility, specificity to the user or team, and sensitivity/safety. Keep multiple resources when they serve distinct authority lanes, such as process rules, data lineage, customer-facing assets, positioning, competitive enablement, legal/comms guardrails, customer proof, or deal governance; do not collapse them into one hub merely because titles overlap.
8. Save high-confidence, source-backed, non-obvious, low-risk resources by default. Do not save broad, sensitive, ambiguous, lower-confidence, unsupported, surprising, account-specific, volatile, or policy-like entries until the user has seen them and explicitly says `save`, `apply`, `update`, `keep these`, or otherwise clearly approves writing those entries.
9. For broad hubs, save only when they are clearly useful durable starting points. The saved memory and `What was found` bullet must include the safe-use caveat, such as "use as a starting point for account-specific artifacts, not as policy truth" or "refresh before relying on live dashboard values."
10. Extract concise usage rules, source links, names, aliases, source priorities, and workflow hints. For every saved resource, write a one-sentence utility description that explains what future Sales workflows should use it for. Redact sensitive details and summarize only what future Sales workflows need. If a candidate mostly restates what a connector can retrieve directly, drop it or turn it into a question asking for the missing convention or authoritative source.
11. When saving, use `../user-context/references/plugin-memory.md` and the `Write` rules in `../user-context/SKILL.md`: update `user-context.md` directly, replace `status: not provided` only in touched scaffold categories, append or merge resources under `## Saved Links And Context`, preserve category descriptions, update `onboarding-state.json` only for status-only onboarding bookkeeping that changed, and run the Sales preflight readback after writing. Do not duplicate saved resource lists, category lists, source URLs, counts, or research-output details into onboarding state. Never run parallel writes against Sales state files.
12. Identify the five highest-value unresolved asks. Prefer questions that would unlock source authority, book-of-business/account ownership, account-plan sources, approval/governance preferences, customer-facing claims guardrails, customer-story libraries, access gaps, or source freshness. Future automation runs can ask more questions later, so do not exhaustively list every gap.

## Save And Review Rules

Discovery-derived memory may be saved by default only when it is high-confidence, source-backed, non-obvious, low-risk, and useful for future Sales workflows. Discovery authorization is not blanket save authorization.

Do not save:

- raw CRM field metadata, picklist inventories, live values, or ordinary object reads;
- sensitive deal desk, private legal, commercial, security, account-room, or private-channel details unless the user approves the exact memory entry;
- generic search results, incidental chatter, duplicate hubs, or easy-to-find account folders without a durable usage reason;
- dashboard values, tracker statuses, account ownership, or live book facts unless the saved entry is a durable source pointer with a refresh-before-use caveat.

When entries are review-only, ask the concrete question that would make the candidate saveable. Fold review-only candidates into `Where you can help`.

## Output

Start every completed research response with exactly one of:

```text
Sales company research is complete. {N} new resources saved.
```

```text
Sales company research is complete. No new resources saved.
```

Use this output shape when resources were saved:

```md
Sales company research is complete. {N} new resources saved.

**What was found**
- [{Resource title}]({stable URL})
  {One-sentence user-value description explaining what future Sales workflows should use this for}. {Safe-use caveat when the source is broad, dynamic, account-specific, or not policy truth.}
- **{Connector-visible resource title}** (no useful link available)
  {Why this helps future Sales workflows}. Source: {durable connector-visible reference}. {Safe-use caveat when needed.}

**Where you can help**
1. {Question that would unlock better future Sales workflows, with why it matters.}
```

Do not include coverage notes or operational research bookkeeping in the completed response. Keep searched source families, source-family depth, connector availability, prior saved-memory state, pinned-thread history, review-only bookkeeping, and reasons non-saved findings were excluded out of the user-facing output unless the user asks for debugging or audit details. Convert material limitations into concrete `Where you can help` questions instead.

Use this output shape when no resources were saved:

```md
Sales company research is complete. No new resources saved.

**What was found**
{Briefly explain the strongest blockers or why no candidate cleared the high-confidence, low-risk save bar.}

**Where you can help**
1. {Question that would make the next run materially better.}
```

Output rules:

- `N` counts newly saved resources only, not reviewed candidates or already-saved resources.
- `What was found` lists only high-confidence saved resources. Do not include review-only candidates there.
- Include one concise bullet per saved resource. Start each bullet with the resource title as a Markdown link whenever a stable URL exists, then put the user value on the next line in plain language. Do not include category labels such as `saved under`, memory category names, or implementation bookkeeping in the user-facing result.
- Every saved resource must explain why it helps the user, using concrete downstream Sales value such as better meeting prep, stronger follow-ups, cleaner CRM updates, sharper account prioritization, safer customer-facing claims, faster competitive briefs, or more credible business cases. Do not output bare link bullets. If you cannot explain a resource's utility in one sentence, do not count it as saved until you have enough evidence.
- Add safe-use caveats for broad hubs, dynamic dashboards, customer/account folders, account rooms, or sources that should not be treated as policy truth.
- Do not append onboarding reminders, onboarding status, or onboarding CTAs to completed Sales Company Research output. Keep the final visible action inside `Where you can help`.
- If the saved set lacks legal/comms/customer-facing claims guardrails, approved product positioning/core narrative, or another high-risk customer-facing source category, ask for it in `Where you can help`.
- Include up to five `Where you can help` questions. Each question should ask for a concrete link, channel, tracker, report, owner, example, preference, access fix, or source-of-truth choice, and say why the answer would be valuable.
- Use the output shapes above by default. Mention implementation details or readback status only when the user asks for them or when readback failed.
