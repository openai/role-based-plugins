---
name: find-customer-quotes
description: Retrieve theme-specific customer or prospect quotes from transcripts, call notes, or exported recordings using transcript-first evidence and explicit speaker-confidence rules.
---

# Find Customer Quotes

Use this skill to pull theme-specific exemplar customer or prospect quotes from transcripts, call notes, exported recordings with transcript text, or pasted transcript-like evidence.

This is a transcript-first workflow. Prefer `meeting_notes` search and fetch when the connector is available; otherwise use user-provided transcript exports, pasted transcript text, or grounded call notes. Do not use public web search, CRM summaries, memory, or generic notes as substitutes for customer quote evidence.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the quote output also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits quote retrieval or confidence.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided, connector-visible, or explicitly inferable context to identify the quote theme and at least one transcript-like evidence lane.

The skill can still produce a limited quote set from pasted transcripts, uploaded/exported transcripts, call-note exports, or user-linked transcript text when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] `theme_or_narrative`: feedback theme, objection, product area, use case, narrative, customer pain, buying criterion, or other quote topic
- [required] `transcript_evidence`: live `meeting_notes` access or user-provided transcript-like material that preserves enough speaker or context evidence to judge customer/prospect likelihood

Accept when provided:

- company, account segment, product, date range, source set, or call list filters
- `quotes_per_theme`; default `5`
- output format; default readable Markdown, JSON only when requested or needed downstream

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- When company, account, segment, or source-set filters are ambiguous, include a bounded CRM lookup when `crm` is available to resolve account identity or segment candidates, but do not use CRM as quote evidence.
- Before asking the user to paste transcript exports or call notes, first try the source category that can own quote evidence: `meeting_notes`. Use `crm` only to resolve ambiguous account, company, or segment filters, never as quote evidence. Manual transcript material is the fallback after `meeting_notes` is unavailable, empty, or lacks relevant transcript-like evidence.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

If neither live transcript access nor user-provided call material is available, stop and ask for transcript exports, pasted transcript text, or call notes. Do not fabricate quotes from memory, CRM summaries, public web research, or account notes.

**Input Request Format Example:**

```md
Which feedback theme, objection, product area, or transcript set should I use?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when a recent call-follow-up, product-feedback, planning thread, pasted transcript, or uploaded/exported call material clearly names the theme and evidence source.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `meeting_notes`: transcript search, fetched transcripts, call metadata, call/transcript URLs, speaker labels, participant context, dates, companies, and connector-specific refetch handles.
- `crm`: account identity, customer/prospect status, and segment filters that narrow transcript search. Never use CRM as quote evidence.
- user-provided context: pasted transcripts, uploaded/exported transcripts, recording exports with transcript text, grounded call notes, theme labels, company or segment filters, and quote-format preferences.

Source obligations by intent:

- Quote extraction requires transcript-like evidence from `meeting_notes`, exported transcripts, pasted transcript text, recording exports, or grounded call notes that preserve speaker/context confidence.
- `crm`, account summaries, docs, public web, and saved memory may suggest filters, account context, or segment labels, but they are not quote evidence and must not be used to invent or paraphrase customer language.
- If `meeting_notes` is available, search and fetch the narrowest relevant transcript set before asking for manual transcript material. If checked and no relevant transcript is found, say so and ask for transcript exports or pasted text.

Authority and gaps:

- Evidence lane order:
  1. `meeting_notes` search and fetch when available.
  2. Uploaded/exported transcripts, pasted transcript text, recording exports with transcript text, or grounded call notes that clearly distinguish customer/prospect language.
- Use grounded call notes only when they contain transcript-like direct quotes or enough context to preserve speaker-role confidence.
- Do not treat CRM fields, account summaries, public web pages, internal notes, or memory as quote evidence.
- Use CRM, account context, docs, and saved memory only to narrow transcript search or explain scope; if those lanes are unavailable, continue when the transcript-like evidence and user theme are sufficient.
- Default bias is precision over recall. Return fewer than `quotes_per_theme` when customer-speaker confidence is weak.
- When no high-confidence customer/prospect quotes pass threshold but transcript-like sources contain relevant internal, vendor-eval, partner-readiness, or implementation evidence, the skill may return that material only in a separate fallback section. Do not count it toward `quotes_per_theme` or present it as customer/prospect language.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the find-customer-quotes experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Find Customer Quotes
This skill helps pull customer or prospect language for a feedback theme, objection, product area, use case, or sales narrative. It can use transcripts, call notes, pasted excerpts, meeting notes, docs, or exported recordings. It produces quote candidates with speaker/context, source links when available, theme fit, confidence, and safe usage notes.

Definitions:
- Quote candidate: a verbatim snippet that may be useful, but still needs speaker, context, and usage checks before being treated as customer evidence.
- Customer confidence: the confidence that the speaker is actually a customer or prospect rather than an internal teammate, partner, or unknown speaker.
- Fallback evidence: relevant non-customer or lower-confidence material that may explain a gap but should not be presented as a customer quote.
- Safe usage notes: guidance on attribution, sensitivity, confidence, and where the quote can responsibly be reused.

```

Starter prompts:

- Primary default prompt: `Find customer quotes about a feedback theme.`
- `@Sales find customer quotes about setup friction from recent enterprise calls.`
- `@Sales pull prospect quotes about data residency from the last month of call notes.`
- `@Sales find quotes that support the "faster account research" story from these transcripts.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Find Customer Quotes next-step behavior and action text. Onboarding, artifact creation, draft creation, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the quote-finding continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `find-customer-quotes` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/saving/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the quote set** | The first substantive quote set has just been produced. | `Anything you'd change in the quote filters, confidence bar, or usage notes before we package these?` |
| **2. Review the revised quote set** | The user asked for any change to themes, filters, quote selection, confidence, usage notes, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If these are the right quotes, want me to package them into a customer-evidence snippet, proof-point note, enablement blurb, or internal post?` |
| **3. Prepare the quote package** | The user accepts the quote set, says no changes are needed, says a revision looks good, or asks to operationalize the quotes. | Offer to produce the most useful next artifact or draft action, prioritizing customer-evidence snippet, proof-point note, enablement blurb, internal post, or shareable quote package over broad suggestions. |
| **4. Review the quote package or draft** | A snippet, proof-point note, enablement blurb, internal post, or quote package exists, or the user asks to change it. | `Anything you'd change before I save, post, or share this quote package?` |
| **5. Save, post, or share approved quote package** | A reviewed quote package or draft exists and does not need edits. | Offer the specific supported action, such as saving the package, posting the approved internal note, or sharing the enablement blurb. Do not post or send messages unless the user explicitly asks for that action or approves the reviewed draft. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the quote set, treat a lightweight acknowledgement as acceptance and move to `Prepare the quote package`. If the previous continuation offered to prepare a package or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post or send externally. If the previous continuation offered to save, post, or share a specific reviewed package, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Procedure

### 1. Parse and normalize themes

- Convert single or many themes into a list.
- Preserve the user's theme and segment labels.
- Process large theme sets in small batches.
- Default `quotes_per_theme` to `5`.
- Normalize time filters:
  - if the user supplied `date_range`, use it;
  - if the user supplied a natural-language recency window, convert it to an absolute `date_range`;
  - treat `last month` as ambiguous; default to trailing `30` days unless the user explicitly says `last calendar month`;
  - prefer calendar interpretations for phrases like `last quarter` or `this quarter`; prefer trailing windows when the user says `last N days/weeks`;
  - if the phrase is too ambiguous to convert responsibly, ask one brief clarifying question unless the user clearly signals flexibility.
- For each theme, derive a short search phrase: include the theme itself and one or two intent words like `pain point`, `blocker`, `request`, `limitation`, or `need`.
- Do not overstuff search queries with instructions.

### 2. Search transcript evidence per theme

Use `meeting_notes` search with a concise topical query when available.

Recommended starting parameters per theme:

- `query`: theme-focused phrase
- `company`: only if the user explicitly wants a specific company
- `account_segment`: only if explicitly requested
- if the selected `meeting_notes` exposes an account-segment filter with a known enum, use the connector-visible value that matches the user's wording
- `date_range`: only if the user supplied one
- `limit`: `10` to `15`
- `score_threshold`: `0.7`

Fallbacks if sparse results:

1. Retry with a simpler query: theme plus the single strongest keyword.
2. Lower `score_threshold` modestly, for example to `0.6`.
3. Increase `limit` toward `20` to `40` only when the first pass is thin and the requested quote count or coverage needs it.

Do not invent additional user intent. If the user asks only for a theme, keep the query theme-centric.

### 3. Fetch or parse transcripts

- Fetch top-ranked search result ids first; expand only until there is enough high-confidence coverage or the first pass is clearly thin.
- For manual/export inputs, parse only transcript-like material that preserves enough speaker or context evidence to classify customer/prospect likelihood.
- Keep a mapping of theme, search result metadata, fetched transcript content, connector-specific id or internal refetch handle, and call/transcript URL from the fetch response when available.
- Do not assume a fixed transcript schema. Inspect the fetched payload shape and adapt.

### 4. Extract candidate quotes

Run a theme-specific extraction pass over each transcript.

Include candidates that:

- directly express a pain point, blocker, constraint, concern, unmet need, request, or purchase condition;
- are relevant to the theme;
- are substantial enough to be useful, not generic praise;
- appear to be spoken by an external participant or are ambiguous but promising.

Exclude:

- obvious internal seller-side statements;
- paraphrases that are not direct quotes unless the user explicitly asks for paraphrases;
- concatenated or garbled fragments that combine multiple thoughts;
- extremely short fragments with no clear meaning.

Keep quotes verbatim. Do not clean up wording beyond preserving readable punctuation around the quoted text.

### 5. Verify speaker likelihood and rank

Run a second pass over extracted candidates with local transcript context.

For each candidate, provide:

- `speaker_role_guess`: `customer`, `prospect`, `internal_seller`, or `unknown`
- `customer_confidence`: `0.0` to `1.0`
- `theme_relevance`: `0.0` to `1.0`
- `evidence`: concise explanation grounded in transcript text or labels

Default thresholds:

- Keep only `customer_confidence >= 0.8`.
- Keep only `theme_relevance >= 0.75`.
- If fewer than `quotes_per_theme` remain, prefer returning fewer quotes over lowering `customer_confidence`. You may lower `theme_relevance` slightly, for example to `0.65`, if speaker evidence stays strong.
- If no candidates pass the customer-confidence threshold, preserve that result as `0/{quotes_per_theme}`. Do not backfill the quote list with internal or unknown-speaker snippets.
- If relevant non-customer snippets were found, classify them separately as `internal_evidence`, `vendor_eval_evidence`, `partner_readiness_evidence`, or `unknown_non_customer_evidence`. Keep only snippets with strong theme relevance and enough context to explain why they are useful but excluded from the customer/prospect quote set.

Ranking priorities:

1. `customer_confidence`
2. `theme_relevance`
3. diversity across calls/customers
4. specificity and actionability of the pain point
5. clarity/readability while staying verbatim

Use [references/extraction-and-output.md](references/extraction-and-output.md) when transcript parsing is ambiguous, speaker-role confidence is hard to judge, quote ranking/deduplication needs the full rules, the user asks for JSON, or failure handling needs the exact response shape.

### 6. Deduplicate and select exemplars

- Normalize whitespace and punctuation for comparison only.
- Drop exact duplicates.
- Drop quotes that are near-identical with trivial wording changes.
- Default to one quote per call.
- Use two quotes from the same call only when needed to reach the requested count with strong quotes or when the second quote adds materially different evidence.
- Prefer breadth across customers when customer/account identity is available.
- If a theme has insufficient high-confidence quotes, return fewer quotes and include a short gap note.

### 7. Render quote output

Default to a readable grouped Markdown summary. Use JSON only when the user explicitly asks for JSON, the results will be consumed downstream by another tool/workflow, or a machine-readable artifact is needed for comparison/review.

Readable summary per theme:

- theme name;
- number of quotes returned over target;
- one-line coverage quality note, such as `strong spread across 8 calls`;
- quote list, each quote on its own bullet, with quote text, customer/company when available, speaker name when known, compact confidence, and transcript link when available.

Minimum fields per quote:

- `theme`
- `quote` verbatim
- `speaker_name`, using `unknown` if unavailable
- `speaker_role_guess`
- `customer_confidence`
- `theme_relevance`
- `evidence`
- `transcript_url` or a clear note when no useful link is available

Optional footer:

- `Gaps` for themes with weak coverage
- `Internal / Non-Customer Evidence` when no customer/prospect quotes pass threshold but relevant transcript evidence exists from internal, vendor-eval, partner-readiness, or otherwise non-customer speakers
- `Method Notes` when transcript formatting, sparse results, repeated calls, or speaker-label quality reduced confidence

Fallback evidence rules:

- Keep the main theme result explicit, for example `Theme: sales plugin setup friction (0/{quotes_per_theme} customer/prospect quotes)`.
- Render fallback snippets under a heading such as `Internal / Non-Customer Evidence`, not under `Quote Candidates` or the customer quote list.
- For each fallback snippet, include the verbatim text, speaker/context when known, `speaker_role_guess`, customer confidence, theme relevance, source link, and a short `usage note` such as `Useful for an internal product brief; do not present as a customer quote`.
- Prefer a compact set of the strongest, most actionable fallback snippets over an exhaustive dump. Do not include garbled or bracket-reconstructed text unless the uncertainty is clearly noted.
- When both high-confidence customer/prospect quotes and fallback evidence exist, omit fallback evidence unless the user explicitly asked for internal evidence too or the fallback materially explains a gap.

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Guardrails

- Do not fabricate quotes, speaker names, titles, roles, companies, transcript links, or call metadata.
- Do not treat every quote in a relevant call as theme-relevant.
- Do not treat every relevant quote as customer-spoken.
- Do not treat no-speaker-label transcripts as high confidence unless surrounding context clearly supports external speaker likelihood.
- Keep quotes verbatim.
- Prefer fewer, high-confidence exemplars over a padded list.
- Prefer diverse call/customer coverage over taking multiple quotes from the same call.
- If transcript formatting is poor, say so explicitly and surface uncertainty.
- This skill is not for exhaustive call analytics, exact speaker identity verification when transcripts lack evidence, or legal/compliance review.
