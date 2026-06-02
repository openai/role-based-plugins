---
name: enrich-company-and-contact-data
description: Build portable sales enrich-company-and-contact-data outputs for company and contact discovery, firmographic or technographic completion, ICP list building, segmentation, trigger analysis, market scans, and enrichment-backed comparison work using configured source categories and user-provided inputs.
---

# Enrich Company And Contact Data

Use this skill for data-first go-to-market enrichment: company/contact lookup, firmographic or technographic completion, ICP discovery, record enrichment, market segmentation, signal scans, similar-company research, and enrichment-backed comparison tables.

Use another focused Sales workflow when the user's real goal is primarily meeting prep, pipeline prioritization, deal strategy, competitive narrative, business case, or forecast review. Those skills may still use this skill as a bounded enrichment lane, but they stay authoritative for the seller task itself.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the output also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the output.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided, connector-visible, public, or explicitly inferable context to identify the entity set and enrichment task shape.

The skill can still produce a limited enrichment table from pasted lists, CSV/exported rows, explicit domains, user-provided ICP notes, or public context when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because enrichment connectors are unavailable.

**Inputs:**

Require:

- [required] entity scope: companies, contacts, account list, ICP, territory, segment, or pasted/exported rows
- [required] task shape: discover, enrich, compare, segment/score, or scan signals

Accept when provided:

- requested fields, ranking or segmentation criteria, result limit, provider preference, geography, industry, company size, technology, title/seniority, funding/growth/intent signals, and output format

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible existing customer/account anchors unless the request clearly asks for external discovery only. When `crm` is available, include a bounded CRM lookup to resolve account identity, customer status, duplicate candidates, or account-list scope before relying on enrichment providers, public research, or docs alone.
- Before asking the user to paste a list, CSV, ICP, or field set, first try the source categories that can resolve the missing entity scope or task shape: `data_enrichment` for provider-native company/contact discovery, `crm` for existing account/customer scope, and `document_store` for ICP, territory, segmentation, or target-account lists. Manual/exported rows are the fallback after those categories are unavailable, empty, or not specific enough.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
Which company, contact list, account list, or ICP should I enrich?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when the user has supplied a list, export, ICP, or onboarding/check-in context clearly names the list to work.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `data_enrichment`: company/contact lookup, firmographics, technographics, intent signals, similar-company discovery, contact recommendations, and provider-native enrichment fields.
- `crm`: account identity, customer status, ownership, lifecycle stage, open opportunity context, duplicate resolution, and internal account truth.
- `document_store`: ICP definitions, target-account lists, territory docs, segmentation rules, enrichment conventions, and saved source-of-truth guidance.
- user-provided context: pasted lists, CSV/exported rows, domains, emails, company/contact names, ICP notes, ranking criteria, and requested fields.
- public research: narrow validation of facts not covered by configured enrichment providers when the user asks or the first pass would otherwise be misleading.

Authority and gaps:

- Do not treat enrichment providers as CRM systems of record.
- For customer/account enrichment or account-list cleanup, use CRM when available for account identity, customer status, ownership, lifecycle stage, open opportunity context, duplicate resolution, and internal account truth. Do not let enrichment providers, public research, docs, or user-provided guesses overwrite CRM-owned account truth.
- Treat public research as validation or gap-fill for external facts only; do not use it to overwrite provider-native enrichment or CRM-owned account status when those sources are available.
- User-provided records define the working set unless the user asks for discovery.
- Use public research only for narrow validation or when no configured provider/manual evidence can answer the requested field.
- If configured enrichment access is missing, continue from manual/exported context when sufficient and label provider gaps.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the enrich-company-and-contact-data experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Enrich Company And Contact Data
This skill helps complete sparse company, account, and contact inputs with useful sales context. It can use a list, territory, ICP, CSV/export, CRM data, enrichment connectors, docs, or public research when appropriate. It produces a cleaned and ranked table with filled fields, confidence, sources, gaps, and recommended next actions.

Definitions:
- ICP: ideal customer profile, the criteria that define what a strong-fit company or contact looks like for the sales motion.
- Firmographic context: company attributes such as industry, size, geography, revenue band, funding, or business model.
- Technographic context: evidence about the tools, platforms, infrastructure, or technology choices a company uses.

```

Starter prompts:

- Primary default prompt: `Enrich a company or contact list.`
- `@Sales enrich this account list with firmographics and likely buying teams.`
- `@Sales clean up these contacts and flag which ones are worth pursuing first.`
- `@Sales find missing company details for the top accounts in my territory.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Enrich Company And Contact Data next-step behavior and action text. Onboarding, spreadsheet creation, draft creation, CRM writeback, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the enrichment continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `enrich-company-and-contact-data` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/writing/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the enrichment table** | The first substantive enrichment table has just been produced. | `Anything you'd change in the fields, scoring, rows, or confidence thresholds before we act on this table?` |
| **2. Review the revised enrichment table** | The user asked for any change to columns, ranking criteria, confidence thresholds, rows, filters, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If the table looks right, want me to move it into a spreadsheet, segmentation artifact, contact-selection guide, or CRM update draft?` |
| **3. Prepare the enrichment artifact** | The user accepts the table, says no changes are needed, says a revision looks good, or asks to operationalize the enrichment. | Offer to produce the most useful next artifact or draft action, prioritizing spreadsheet, segmentation artifact, contact-selection guide, outreach input, or CRM-ready update text over broad suggestions. |
| **4. Review the artifact or draft** | A spreadsheet, segmentation artifact, contact-selection guide, outreach input, or CRM-ready update exists, or the user asks to change it. | `Anything you'd change before I save, share, or write the approved enrichment updates?` |
| **5. Save, share, or write approved enrichment action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the spreadsheet, sharing the contact-selection guide, creating reviewed outreach drafts, or writing approved CRM update text. Do not post, send, or write CRM changes unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the enrichment table, treat a lightweight acknowledgement as acceptance and move to `Prepare the enrichment artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post, send, or write externally. If the previous continuation offered to save, share, or write a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Operating Modes

Choose the narrowest mode that matches the user's request.

- `discover_companies`: build a company list from an ICP, market description, trigger, or comparison seed
- `discover_contacts`: find relevant stakeholders or buyers for named companies or a defined segment
- `enrich_records`: complete or improve a supplied company/contact set
- `compare_accounts`: contrast known companies using requested attributes or research dimensions
- `segment_or_score`: cluster, tier, or prioritize a bounded set using explicit criteria
- `signal_scan`: surface companies or accounts matching defined external signals

If the user does not specify a mode, infer it from the request. Do not broaden the task beyond what the prompt requires.

## Inputs

Normalize the request into the smallest useful working shape:

- `mode`
- `entity_scope`: companies, contacts, or mixed
- `input_records`: names, domains, emails, companies, contacts, or source list when supplied
- `search_criteria`: industry, region, company size, business model, technology, title, seniority, hiring, funding, growth, intent, or other explicit filters
- `requested_fields`: fields the user wants returned or completed
- `ranking_or_segmentation_rule`: the criterion for ordering or grouping results, when requested
- `result_limit`
- `provider_preference`, when the user names a provider

Ask a concise clarification only when the request is impossible to execute responsibly, such as:

- the desired entity type is unclear in a way that changes the workflow
- the user asks for a ranked or filtered list without enough criteria to know what qualifies
- the task requires a named provider or account scope that cannot be inferred from the prompt

Otherwise, choose a conservative reasonable interpretation and proceed.

## Workflow

Run these steps in order.

### 1. Lock the task shape

- Identify the smallest mode that satisfies the request.
- Separate hard constraints from softer preferences.
- Preserve exact user wording for company names, titles, industries, and priority rules.
- Decide whether the output should be a shortlist, a comparison table, an enriched record set, or a compact narrative with supporting rows.

### 2. Resolve the working set

Use the request type to choose the path:

- For discovery work, start from the search criteria or seed companies.
- For enrichment work, start from the supplied records and normalize obvious duplicates before lookup.
- For comparison work, preserve the full named set and avoid silently dropping difficult matches.
- For signal scans, define the exact signal or proxy before retrieving data.

When identity ambiguity matters, surface it. Do not quietly merge two companies, two contacts, or two competing interpretations into one row.

### 3. Choose the evidence lane

- Prefer user-supplied rows when they already define the scope.
- Use a configured `data_enrichment` app when the task needs external lookup, structured enrichment, topic research, lookalikes, or provider-native signals.
- Use `crm` or `document_store` only as a supporting lane for disambiguation or account framing, not as a replacement for provider-native enrichment when the task is explicitly external-data-first.
- Use public research sparingly and label it clearly when present.

If no configured provider is available, continue from user-provided inputs and public sources only when the task still remains useful. State the missing lane plainly when it materially limits quality.

### 4. Retrieve only what materially improves the answer

- Narrow first, then deepen.
- For broad candidate discovery, search before heavier enrichment.
- Enrich only the final shortlist or the provided record set unless the user explicitly wants exhaustive batch treatment.
- For company/contact discovery, return the fields the user asked for plus only the minimum context needed to interpret quality.
- For comparisons, gather comparable fields for every entity before synthesizing winners or rankings.
- For signal scans, keep the signal definition visible and avoid converting a weak proxy into a stronger claim.

Be credit-aware when the selected provider makes cost material. Do not add ceremony to a small, clearly requested call, but avoid wasteful wide enrichments when a narrower pass would answer the question well.

### 5. Verify before summarizing

Before calling something a match, verify the hard constraints that matter:

- geography
- company size or revenue band
- public versus private status when requested
- seniority, role, or company assignment for contacts
- industry, technology, or other qualifying fields when surfaced
- any explicit ranking or segmentation criterion

If a candidate is close but not qualified, move it to `Near Matches`, `Unclear`, or `Excluded` instead of presenting it as a clean hit.

### 6. Render the right output shape

Use the smallest structure that preserves decision value.

For discovery:

- `Qualified Matches`
- `Near Matches` when useful
- `Why These Fit`
- `Gaps / Caveats`

For enrichment:

- `Input Record`
- `Resolved Entity`
- requested enriched fields
- `Confidence / Notes`
- `Missing or Unresolved`

For comparison:

- comparison table with one row per company or contact
- explicit ranking or readout only when the underlying criterion is supported
- `What Is Still Unclear`

For segmentation or scoring:

- segment or tier labels
- the visible rule used to assign each label
- concise rationale
- `Evidence Gaps`

For signal scans:

- returned entities
- the precise signal or proxy observed
- confidence or caveat
- the smallest next check that would improve trust

## Quality Rules

- Keep sourced facts separate from `Inference:`.
- Do not invent missing fields, emails, phones, titles, technologies, funding, hiring signals, or account intent.
- Do not claim exhaustiveness from a bounded provider query.
- Do not overstate a provider-specific result as universal market truth.
- Rank only by explicit criteria or returned provider signals that the user can understand.
- If a request is blocked by unavailable source access, weak matching, or partial provider output, say so directly.
- Prefer compact, inspectable tables over long prose when the task is data-first.
- Make provider limitations visible when they affect confidence, coverage, cost, or rerun quality.

## When To Hand Off

- Route to `prioritize-accounts` when the user wants "which accounts should I work now?" rather than a data list.
- Route to `prepare-for-meeting` when the user wants a meeting brief or attendee prep.
- Route to `plan-deal-strategy` when the user wants a buying committee, risk register, or next-action plan for an active deal.
- Route to `build-competitive-brief` when the user wants a positioning brief, objection map, or market narrative rather than structured enrichment.
- Route to `build-business-case` when the user wants a business case, ROI structure, or quantified value story.
