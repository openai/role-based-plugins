---
name: get-rep-call-feedback
description: Compare one rep’s call history against peer examples to extract repeatable best practices and produce evidence-backed coaching feedback.
---

# get-rep-call-feedback

## Goal
Produce high-signal coaching feedback for a target rep by benchmarking their recent `meeting_notes` calls against peer reps' calls, extracting **repeatable best practices**, and translating them into **very specific moments** where the target rep can apply those patterns in future calls.

This skill optimizes for:
- **Great examples from peers** (what “good” sounds like in practice)
- **Specific coaching moments** for the target rep (exact spots to apply those moves)
- **Evidence-led** excerpts and observable patterns (no invented content)

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

This skill needs enough user-provided, connector-visible, or explicitly inferable context to identify a target rep and a call set, transcripts, notes, or coaching theme.

The skill can still produce limited coaching feedback from pasted transcripts, uploaded/exported call notes, manager-provided examples, or user-linked transcript text when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] target rep or clearly supplied target call set
- [required] call evidence: transcripts, call notes, meeting-note access, exported calls, or pasted transcript-like material

Accept when provided:

- peer exemplar reps, time window, call type, product focus, coaching theme, manager notes, output audience, and requested depth

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Before asking the user to paste transcripts, call notes, rep names, or peer examples, first try `meeting_notes` for target-rep call candidates, peer-example candidates, call metadata, and transcript access. Manual transcript-like material is the fallback after `meeting_notes` is unavailable, empty, or too thin for evidence-backed coaching.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
Which rep and call set should I review?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when the user supplies transcripts or a clear rep/time window.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `meeting_notes`: call search, transcript fetches, call metadata, call/transcript URLs, speaker labels, participant context, dates, companies, and refetch handles.
- user-provided context: pasted transcripts, uploaded/exported call notes, manager notes, coaching themes, rep/call lists, and peer exemplar examples.

Authority and gaps:

- Use transcript/call-note evidence for behavioral claims. Do not infer coaching moments from memory or CRM summaries alone.
- Treat CRM outcomes, manager notes, scorecards, and peer examples as coaching context only; do not use them as substitutes for transcript-backed or call-note-backed observed behavior.
- Prefer live transcript/call URLs over raw connector ids in final output.
- If transcript access is missing, continue only from transcript-like manual material that preserves enough context to support coaching claims.
- If the call set is too small or uneven, produce a limited feedback memo and name the coverage gap instead of padding recommendations.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the get-rep-call-feedback experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Get Rep Call Feedback
This skill helps compare a rep's call behavior with evidence from their calls and, when available, peer examples. It can use transcripts, call notes, scorecards, manager notes, CRM context, or pasted examples. It produces strengths, coaching opportunities, concrete examples, and practical next practice steps without overclaiming beyond the evidence.

Definitions:
- MAP: mutual action plan, a shared customer-and-seller plan with owners, milestones, and dates.
```

Starter prompts:

- Primary default prompt: `Give feedback on a rep's calls.`
- `@Sales give feedback on Jamie's last three discovery calls.`
- `@Sales compare this rep's demo calls with strong peer examples and suggest coaching points.`
- `@Sales review these transcripts for talk-listen balance, qualification, and next-step clarity.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Get Rep Call Feedback next-step behavior and action text. Onboarding, coaching artifact creation, draft creation, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the call-feedback continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `get-rep-call-feedback` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/saving/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the coaching feedback** | The first substantive call-feedback output has just been produced. | `Anything you'd change in the coaching feedback before we turn it into something the rep or manager can use?` |
| **2. Review the revised feedback** | The user asked for any change to coaching points, examples, peer moves, tone, audience, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to draft the rep-facing note, practice plan, manager summary, or enablement snippet?` |
| **3. Prepare the coaching artifact** | The user accepts the feedback, says no changes are needed, says a revision looks good, or asks to operationalize it. | Offer to produce the most useful next artifact or draft action, prioritizing rep-facing coaching note, practice plan, manager summary, enablement snippet, or rep-facing action list over broad suggestions. |
| **4. Review the artifact or draft** | A coaching note, practice plan, manager summary, enablement snippet, or action list exists, or the user asks to change it. | `Anything you'd change before I save, post, or share this coaching artifact?` |
| **5. Save, post, or share approved coaching action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the practice plan, sharing the manager summary, or posting the approved rep-facing note. Do not post or send messages unless the user explicitly asks for that action or approves the reviewed draft. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the coaching feedback, treat a lightweight acknowledgement as acceptance and move to `Prepare the coaching artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post or send externally. If the previous continuation offered to save, post, or share a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Operating rules
- **Be evidence-led**: Ground everything in call excerpts, transcript moments, or repeated patterns. If you can’t find enough calls, say so and propose a tighter search strategy.
- **Never invent** call content, attendees, outcomes, metrics, or deal context.
- **Use inline numbered markdown links to live transcript/call URLs in final user-facing output.** Keep raw connector ids only for retrieval/refetch logic.
- `SKILL.md` owns the normal collection loop and output format. Use `references/call-transcripts-connector-playbook.md` only when date-window conversion, attendee-filter limitations, score-threshold fallback, or sparse-result recovery needs more detail. State the absolute coverage window in `Dataset coverage`.

---

## Optional product focus (use only when helpful)
Many reps sell one product area; don’t overcomplicate this. Only apply product focus when:
- the user explicitly asks (e.g., “focus on API calls”), or
- the dataset mixes motions/products and comparisons would be noisy, or
- you need to hone in on one area to find better peer exemplars.

**If product focus is not requested and not needed:** skip it.

**If product focus is needed:** pick **one** product area, or a small set the user specifies, and add keywords from the user's wording, account context, provided product taxonomy, or call evidence. Do not run placeholder-only product searches.

---

## Workflow

### 1) Parse the user request
Extract:
- **Target rep email** (required)
- **Peer rep emails** (optional but strongly recommended)
- Optional scope: date range, company/account, call type/motion, topics (pricing/security/procurement), and **optional product focus**

If peers are omitted:
- Proceed only if the user explicitly names “top performers” to use as peers.
- Otherwise, ask for **at least 2 peers** (or propose a peer list if the user provides team/segment constraints).

---

### 2) Collect calls (repeat until sufficient)

Use `meeting_notes` search and fetch tools. Search from the most reliable rep/timeframe filters first, convert relative windows to absolute dates before retrieval, put rep names or emails directly in search queries when attendee filters are unreliable, and use only a few bounded query variations when results are sparse.

#### Dataset targets (strongly encouraged)
- **Target rep**: find **at least 15 calls**
- **Peers**: find **at least 15 calls total** across peers (or **~15 per peer** if the user requests strict peer-by-peer benchmarking)

If you can’t reach these targets after a bounded first pass:
- State the shortfall clearly (e.g., “Found 9 target calls in the last month”)
- Expand date ranges or broaden keywords only when that is likely to change the coaching quality; otherwise proceed with a smaller sample, name the limitation, and offer to run a deeper collection pass.

Collect target and peer calls with the same bounded search discipline, aiming for a comparable call mix by motion, segment, and product focus only when product focus is enabled. If the user gave a company/account, include it in the query string and any available structured filter, but do not rely on structured filters alone.

---

### 3) Find strong peer exemplars
Search for the moment you want, not just the meeting motion: objection handling, agenda control, next steps, stakeholder mapping, value framing, security review, pricing, procurement, or business case. Prefer best practices that repeat across multiple peer calls or multiple moments in one clearly strong call.

---

### 4) For each fetched call, capture “coachable moments”
For every call you fetch, extract:
- Call title, date, company/account if available, and live transcript/call URL
- Raw call id or `file-*` id for internal retrieval only
- Motion/type (best-effort from transcript cues)
- **Optional product focus flag** (only if enabled/needed)
- 3–8 key moments, e.g.:
  - Opening / agenda
  - Discovery depth and sequencing
  - Value framing and proof
  - Objection handling
  - Stakeholder mapping / buying process
  - Next steps / MAP

Tag moments as:
- **Peer exemplar** (keep as a “great call” example)
- **Target opportunity** (a moment where applying a peer move would help)
- **Target strength** (keep/scale)

---

### 5) Synthesize best practices (no formal rubric)
Do **not** create a formal rubric or scorecard.

Instead, produce:
- **A short list of best practices that show up repeatedly in peer calls**
- For each best practice:
  - What the rep does (behavior)
  - Why it works (observable effect)
  - 1-3 peer examples (readable title/date/company context + inline numbered transcript links + short excerpt)
  - A “stealable” line or mini-script (if transcript supports it)

Then map to the target rep:
- Identify **specific moments** in target calls where the peer move would apply
- Write: **“In target call X, when Y happened, do Z instead. Here’s how it would sound.”**

---

## Output format (what to deliver)

1) **TL;DR** (3–6 bullets)

2) **Dataset coverage**
   - # target calls reviewed (goal ≥15)
   - # peer calls reviewed (goal ≥15 total; note peers included)
   - Date ranges used + any scoping notes (e.g., product focus enabled)

3) **Peer exemplars: the best calls + why they’re great**
   - 5–10 “stealable moments,” each with call citations + excerpts

4) **Target rep: specific upgrade opportunities**
   - 5–10 coaching points formatted as:
     - **Moment observed** (readable title/date/company context + inline numbered transcript links + excerpt)
     - **Peer exemplar move** (same citation style + excerpt)
     - **Apply it like this** (very specific, with suggested language)

5) **Next-call “steal sheet”**
   - 10–15 practical behaviors + example lines

6) Optional (only if requested): **30-day practice plan**

---

## Output constraints
- Quote short excerpts (1–3 lines) when available and useful.
- Attribute examples with readable title/date/company context plus inline numbered markdown links to the live transcript/call URL.
- Keep recommendations practical and behavior-based.
- If dataset targets aren’t met, explicitly state limitations and provide next search moves.
- Prefer the live transcript/call URL over raw connector ids.
- If a call URL is missing unexpectedly, use readable title/date/company context only and note that a direct link was unavailable. Do not print the raw id.

## References
- See `references/call-transcripts-connector-playbook.md` for detailed search iteration patterns, attendee-filter limitations, and date-range defaults when the compact rules above are not enough.
