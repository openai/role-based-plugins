---
name: review-rep-call-trends
description: Analyze a sales or customer-facing rep’s recent calls to detect improvement, regression, and stable patterns with objective evidence and practical coaching actions.
---

# Rep Trend Coach

## What this skill does
Given a target rep, pull a representative sample of their `meeting_notes` calls across the last few months, analyze summaries (and selectively fetch full call content), and produce an evidence-backed coaching report highlighting:
- what improved
- what regressed
- what changed (behaviors, patterns, outcomes)
- concrete coaching actions tied to specific call moments

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

This skill needs enough user-provided, connector-visible, or explicitly inferable context to identify a target rep and a time window, call set, transcripts, notes, or coaching dimension.

The skill can still produce a limited trend readout from pasted transcripts, uploaded/exported call summaries, manager-provided call sets, or user-linked transcript text when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] target rep or clearly supplied target call set
- [required] comparison basis: time window, older/newer call sets, transcripts, call summaries, or coaching dimension

Accept when provided:

- call type, focus area, peer examples, manager notes, product focus, date range, and output audience

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Before asking the user to paste transcripts, call summaries, rep names, time windows, or coaching dimensions, first try `meeting_notes` for target-rep call candidates, time-window candidates, summaries, metadata, and transcript access. Manual transcript-like material is the fallback after `meeting_notes` is unavailable, empty, or too thin for trend evidence.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
Which rep and time window or call set should I review?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when the user supplies transcripts or a clear rep/time window.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `meeting_notes`: call search, transcript fetches, summaries, call metadata, call/transcript URLs, speaker labels, participant context, dates, companies, and refetch handles.
- user-provided context: pasted transcripts, uploaded/exported call summaries, manager notes, rep/call lists, coaching dimensions, and prior feedback artifacts.

Authority and gaps:

- Use transcript/call-summary evidence for trend claims. Do not infer behavior changes from memory or generic rep impressions.
- Treat CRM outcomes, manager notes, scorecards, and rep/call lists as context for sampling or interpretation only; do not use them as substitutes for call evidence when claiming behavior trends.
- Make true change claims only from a comparison basis: older/newer call sets, time slices, repeated summaries, or explicit user-provided comparison context.
- Prefer live transcript/call URLs over raw connector ids in final output.
- If the dataset is too small or skewed, produce a limited trend readout and name confidence limits instead of overgeneralizing.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the review-rep-call-trends experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Review Rep Call Trends
This skill helps analyze how a rep's call behavior is changing over time. It can use transcripts, call notes, scorecards, manager context, CRM outcomes, or pasted call sets. It produces improving, regressing, and stable patterns with evidence, caveats, and practical coaching actions.

```

Starter prompts:

- Primary default prompt: `Review a rep's call trends.`
- `@Sales review Jamie's call trends over the last month.`
- `@Sales compare this rep's recent discovery calls to their earlier calls and flag changes.`
- `@Sales find improvement and regression patterns across this rep's demo calls.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Review Rep Call Trends next-step behavior and action text. Onboarding, coaching artifact creation, spreadsheet or tracker creation, draft creation, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the call-trend continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `review-rep-call-trends` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/saving/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the trend readout** | The first substantive call-trend readout has just been produced. | `Anything you'd change in the trend readout before we turn it into a coaching artifact?` |
| **2. Review the revised trend readout** | The user asked for any change to trend language, evidence, categories, date window, audience, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to turn it into a coaching tracker, manager-ready summary, rep-facing feedback note, or spreadsheet for tracking change over time?` |
| **3. Prepare the trend artifact** | The user accepts the readout, says no changes are needed, says a revision looks good, or asks to operationalize it. | Offer to produce the most useful next artifact or draft action, prioritizing coaching tracker, manager-ready summary, rep-facing feedback note, enablement follow-up, or spreadsheet over broad suggestions. |
| **4. Review the artifact or draft** | A coaching tracker, manager summary, rep-facing note, enablement follow-up, or spreadsheet exists, or the user asks to change it. | `Anything you'd change before I save, post, or share this coaching artifact?` |
| **5. Save, post, or share approved trend action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the tracker or spreadsheet, sharing the manager summary, or posting the approved feedback note. Do not post or send messages unless the user explicitly asks for that action or approves the reviewed draft. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the trend readout, treat a lightweight acknowledgement as acceptance and move to `Prepare the trend artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post or send externally. If the previous continuation offered to save, post, or share a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Hard rules
- **Do not make anything up.** If the data is missing, say so.
- **Be evidence-first.** Every claim about improvement/regression must reference at least one call using readable context in prose plus an inline numbered markdown link to the live transcript/call URL.
- **Stay objective.** No mind-reading; infer only from what is said/done in the calls.
- **Quote sparingly.** Keep verbatim quotes short (<=25 words per source).
- **Do not expose raw connector ids in final user-facing prose.** Raw ids are for retrieval only.
- Convert all default or user-provided relative date windows to concrete absolute `date_range` values before calling `meeting_notes`. Use the current date from runtime context as the anchor, prefer trailing windows unless the user explicitly requests calendar boundaries, and show the absolute analyzed window in `Coverage`.
- `SKILL.md` owns the normal trend-analysis path and output format. Use `references/rubric.md` only when the compact category defaults below are insufficient for classifying evidence.

## Workflow

### 1) Resolve the target rep
1. If the user names a rep (e.g., “analyze Alex Example”), use that exact display name for `attendee`.
2. If the user clearly asks about their own calls using wording such as `my calls`, `me`, or `how am I doing`, default to the current user name from system context.
3. If the user asks a manager-style or ambiguous request without naming the rep, ask one brief clarification for the target rep's exact display name or email before searching.
4. If the attendee-filtered search returns **zero** results, try small, grounded variations:
   - First/last name only
   - Common nickname if obvious from context
   - If still zero, ask the user for the rep's exact display name in the `meeting_notes` system.

### 2) Collect a representative call sample (multiple searches)
Use `meeting_notes`:
- search with:
  - `attendee = <resolved rep display name>`
  - `score_threshold = 0`
  - `limit = 25`

Default time slicing (if user doesn’t specify):
- last ~90 days split into **three** slices: 0–30d, 31–60d, 61–90d (inclusive; use date_range)
- Run **at least 3 searches** (one per slice). If results are sparse in a slice, expand that slice window by ~30 days and rerun once.

Resolve each slice to absolute start/end dates before searching. For example, if the current date is `YYYY-MM-DD`, derive three non-overlapping absolute windows that cover the trailing 90 days, then pass those exact dates to `meeting_notes`. If the user supplies a natural-language range, convert it first; if the phrase is ambiguous enough to change the sample materially, ask one brief clarification.

Query strategy:
- If the user specifies focus (e.g., “discovery calls”, “objections”, “renewals”, “technical troubleshooting”), encode that into `query` as a short keyword phrase.
- If the user does **not** specify focus, use `query = ""` to avoid biasing results.

Sampling guidance:
- Aim for 30–60 total calls if available (dedupe by id).
- If there are hundreds, keep it manageable by:
  - prioritizing the most recent calls and a smaller older baseline
  - ensuring you include a mix of call types/companies when the summaries indicate variety

### 3) Build a trends view from call summaries
From the search results, create a working table (internal to your reasoning) with:
- date
- company
- call title (if present)
- brief topics from the snippet/summary
- call url
- raw call id or file id for internal retrieval only

Then analyze for trends across time slices using the core categories: opening/agenda, discovery depth, qualification/prioritization, positioning/narrative, objection handling, next steps, technical accuracy, clarity/concision, executive presence, and listening/turn-taking.
- Look for **directional shifts** (e.g., more consistent agenda setting, clearer next steps, better objection handling).
- Track **recurring misses** (e.g., vague next steps, weak qualification, too much feature-dumping).

### 4) Fetch deep context for a small set of calls
Use `meeting_notes` fetch for deeper inspection when:
- summaries are ambiguous
- you need to validate a claimed trend
- you want to extract 2–6 concrete “moments” to coach

Pick calls intentionally:
- 1–2 recent calls that look strong
- 1–2 recent calls that look weak / had friction
- 1–2 older calls (baseline)

When reviewing full content:
- capture brief “moment” notes (what happened + why it mattered)
- keep quotes short
- tie back to rubric categories
- carry forward the live transcript/call URL for user-facing citations

### 5) Produce the coaching report (required format)
Output must be concise, scannable, and evidence-backed.

#### A) Coverage
- Target rep: <name>
- Window analyzed: <start> → <end>
- Calls reviewed: <N summaries>, <M full fetches>

#### B) What improved (evidence)
For each improvement:
- Behavior change
- Evidence: readable context such as `(date, company, call title)` followed by inline numbered markdown links to supporting transcript/call URLs
- Why it matters

#### C) What regressed / risk signals (evidence)
Same structure as above.

#### D) What’s unchanged / consistent pattern
- One or two bullets with evidence.

#### E) Top 3 coaching actions (next 2 weeks)
Each action must include:
- the skill to practice
- an “if/then” play (what to do in the moment)
- a quick drill (5–10 minutes)
- what to look for on the next calls

#### F) Calls to re-listen
List 3–8 calls with a one-line reason each.

### Citation format
- Use compact inline numbered markdown links such as `[1](https://us-43929.app.gong.io/call?id=123456789)`.
- Keep the human-readable context in prose, for example: `2026-03-24, Blue Yonder, Pilot & Pricing [1]`.
- When one statement is supported by multiple calls, append multiple numbered links inline.
- Prefer the live transcript/call URL from the connector response over raw connector ids.
- If a result unexpectedly lacks a call URL, cite it by readable title/date/company only and note that a direct link was unavailable. Do not print the raw id.

## Notes
- Prefer higher-reliability signals (explicit language, structure, next steps) over speculative ones.
- When data is limited (few calls, sparse summaries), be explicit about confidence and avoid overgeneralizing.
