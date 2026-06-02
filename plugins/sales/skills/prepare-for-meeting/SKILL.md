---
name: prepare-for-meeting
description: Create concise pre-meeting briefs and daily prep for customer meetings or the user's most important meeting of the day, using authoritative internal context plus supplementary public web enrichment.
---

# Prepare For Meeting

Prepare a seller or account director for an upcoming customer meeting, or for the most important meeting of the day in scheduled mode. Optimize for the meeting in front of the user: agenda, decisions, high-priority topics, likely blockers, and next actions. Keep broader account context short and subordinate.

A single-meeting brief must use the provided `Output Shapes` format exactly. Fold broader account, product, deal, support, partnership, or public-company context into `Background Context` only when it changes how the user should handle the meeting.

Use this skill primarily for customer-facing or account-related meetings. In scheduled mode, prefer customer/account meetings; if none qualify, choose only the most important non-routine work meeting where prep would materially help. Do not choose routine internal team meetings, 1:1s, interviews, performance conversations, or generic meetings unless the user explicitly asks or the evidence shows clear business stakes.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the brief.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided context to identify the required information. Source access can suggest concrete candidates, enrich, or verify the information, but do not draft the full brief until a specific meeting/account anchor is selected or clearly inferable, supplied, or confirmed by the user.

The skill can still produce a limited brief from user-provided details alone, but connectors add significant value and reduce burden on the user to manually provide context. Do not stop solely because connectors are unavailable.

**Inputs:**

- [required] Company, account, key attendee, meeting title, invite, or date/time
- [required] Meeting attendees or attendee organizations
- [required] Meeting goal, agenda, topic, or meeting type
- Past context, transcripts, notes, emails, docs, or CRM context when available

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. When `crm` is available, include a bounded CRM lookup before relying on calendar, docs, internal messages, meeting notes, or public context alone. If CRM returns one high-confidence account match, use it as the primary account candidate; if multiple plausible account matches remain, ask the user to choose from concrete candidates.
- Before asking the user to name a meeting, paste an invite, or provide attendee/agenda details, first try the workflow source category that owns the missing meeting anchor: `calendar` for meeting candidates, titles, attendees, timing, invite body, and agenda. For customer/account ambiguity, try `crm` before relying on `document_store`, `internal_messaging`, `meeting_notes`, or public context alone. Manual meeting details are the fallback after those categories are unavailable, empty, or insufficient.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

If required inputs remain missing or ambiguous, first attempt a bounded candidate pass through the source category that owns the missing input, within the Fast Candidate Resolution budget. Ask one friendly clarification only after that pass. Ask only for unresolved inputs; for each question, include up to 5 concrete lettered options from source-backed or user-provided candidates when available. Never present a generic instruction as a default. If no concrete candidates are available, briefly say why and ask free-form.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
{Natural clarification question, e.g. "Which meeting should I prepare?"}

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `calendar`: meeting existence, meeting title, time, attendees, invite body, stated agenda, and first-pass meeting focus.
- `crm`: account status, opportunity/deal context, contacts, owner, recent activity, and account records that materially change meeting prep.
- `meeting_notes`: prior calls, internal prep calls, objections, stakeholder language, commitments, decisions, follow-ups, and transcript-backed continuity.
- `document_store`: account plans, implementation docs, mutual action plans, relevant assets, account notes, and team guidance.
- `external_messaging`: recent customer questions, commitments, attachments, tone shifts, scheduling context, and promised next steps.
- `internal_messaging`: account-team strategy, risks, blockers, internal coordination context, and discussion history that changes how the meeting should be handled.
- `data_enrichment` / public web search: company/contact enrichment, attendee roles, firmographics, official company context, recent news, filings, announcements, funding, earnings, leadership changes, and first-time account ramp-up. Use public web only after a meeting/account anchor exists, keep searches targeted to the anchored company, attendees, and topic, and skip it when internal sources already provide enough context.

These are semantic source categories, not fixed connector names. Resolve each attempted source to the specific available app, connector, or helper skill through Sales preflight `context.sources` before using connector-specific logic.

Source obligations by intent:

- For `next`, `upcoming`, `today`, `tomorrow`, scheduled, daily-digest, or invite-dependent meeting prep, `calendar` is required to resolve the meeting title, time, attendees, invite body, and stated agenda unless the user supplied equivalent meeting details. For vague prompts such as "prep me for a meeting" or "prep me for my next meeting," stop after calendar candidate discovery and return options; enrichment starts only after user selection. If `calendar` is unavailable but user-provided details are sufficient, continue with a clear limitation; if the meeting anchor remains ambiguous, ask with concrete calendar-backed candidates when available.
- Do not infer a calendar-selected meeting from `crm`, `external_messaging`, `internal_messaging`, `document_store`, `meeting_notes`, public web, or enrichment. Those sources may suggest candidate context, but selected meeting evidence still needs `calendar`, user-provided details, or user confirmation.
- For customer/account meetings, `meeting_notes` is conditional but expected when accessible and likely to contain prior customer or internal prep context. Search by account, attendee, meeting title, and opportunity/topic terms. If checked and no relevant prior context is found, say so briefly instead of implying transcript-backed continuity.
- For customer/account meetings, `crm` is required when CRM is available and a customer/account anchor is supplied, inferred, or confirmed. Use CRM for account status, opportunity/deal context, owner, contacts, recent activity, and records that materially change the agenda, risks, recommended close, or broader account posture. When multiple opportunities or solutions exist, prefer the one that matches the meeting title/topic, user ask, attendees, product or solution aliases, and recency. If CRM is unavailable or yields no relevant account/deal context, name the gap.
- Do not run every source by default. Stop once the meeting anchor is resolved and the brief has enough high-value evidence; name unchecked or unavailable optional sources as limitations or expansion opportunities when they could matter.

Authority and gaps:

- Use each source category for the facts it owns; do not substitute mirrored sources, browser UI, Computer Use, or web search for authoritative connector evidence.
- Do not treat calendar, docs, Slack/internal messaging, email, meeting notes, public context, or third-party enrichment as substitutes for CRM-owned customer truth.
- Treat public web as lower-authority enrichment after a meeting/account anchor exists; do not use it to invent private account status, commitments, objections, support posture, or deal facts.
- If a source is unavailable, blocked, stale, ambiguous, or missing required fields, name the gap and either ask for access/input, proceed with a clear limitation, or omit the unsupported claim.
- Do not wait on optional enrichment once the meeting is anchored and the available evidence is enough for a useful prep brief; continue with a labeled limitation.
- If continuity is thin, say so and use public/company context only as first-time ramp-up, with `Inference:` for synthesis.
- If evidence is weak or only broadly sourced, omit it or place it in background rather than turning it into tactical guidance.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the prepare-for-meeting experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Prepare For Meeting
This skill creates a concise brief for an upcoming customer or high-value sales-adjacent meeting using calendar, account context, CRM, meeting notes, transcripts, docs, email, internal messaging, saved plugin memory, and user-provided guidance.

```

If this is the first prepare-for-meeting demo from guided Sales onboarding, onboarding owns the framed CTA presentation. Return the `Review the brief` action text from `Next Step Guidance` for onboarding to place in its common frame, and do not add a second direct-run continuation.

### Next Step Guidance

This section is the single owner for Prepare For Meeting next-step behavior and action text. Onboarding, automation readbacks, document creation, calendar linking, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the meeting-prep continuation states elsewhere.

#### Final Continuation Invariant

The next-step flow is mandatory and opt-out. While `prepare-for-meeting` is the active workflow, every turn must either advance the journey, offer the earliest valid next step, or explicitly match one of the allowed exit reasons below. This applies across the whole turn, including after tool calls, connector writes, document updates, Slack/email handoffs, readbacks, short answers, local rewrites, one-paragraph summaries, confirmations, FYI/source cards, partial results, source-gap notes, status updates, explanations of what changed, and answers to "what's next?".

Before sending any final response, inspect the visible assistant-written content. If it does not end with exactly one concrete journey next action, add the earliest valid continuation from `Journey States` or name the specific exit reason. Generic advice, bare confirmations, source links, "done" messages, and "next best step" summaries do not satisfy this invariant when a concrete journey state remains available.

Exit the next-step flow only when one of these reasons applies: the user explicitly asks for no follow-up, the user clearly declines the offered path, the user explicitly closes the workflow, the user starts a new unrelated intent, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not exits; make the unresolved question the final natural continuation. Each Sales skill may define its own allowed omission reasons, but if a skill is silent, the next-step flow is mandatory by default.

After every accepted action or successful tool call in this journey, recompute the current artifact state and move to the earliest next valid continuation. Treat follow-up prompts such as "what's next?", "continue", "next", and "go on" as requests to resume the current journey, not as new intent, unless the user names a different goal. Do not replace the journey continuation with generic next-best advice while a concrete journey state remains available.

#### Journey States

Use the earliest state whose condition matches the current artifact.

| State | Use when | Final continuation |
| --- | --- | --- |
| **Review the brief** | The first substantive prep output for a selected meeting has just been produced. | `Anything we should expand on, or anything you'd change?` |
| **Review the revised brief** | The user asked for any change to the brief, including a small rewrite, added question, one-paragraph summary, source adjustment, or formatting tweak. Make the change in chat first. | If Daily Meeting Prep is eligible, use `Anything else you'd change? If that looks good, want me to set up Sales Daily Meeting Prep for weekday morning calendar checks?` Otherwise use `Anything else you'd change? If that looks good, want me to move it into a dedicated meeting doc?` |
| **Offer Daily Meeting Prep** | The user has tried meeting prep, accepted the brief or a revision, and `sales_preflight` does not show `daily_meeting_prep` active, installed, ready, verified, declined, skipped, or deferred. This is especially important during guided Sales onboarding after the first Prepare For Meeting demo is accepted. | Offer to set up Sales Daily Meeting Prep so Sales checks the calendar each weekday, prepares one high-value qualifying meeting when useful, and returns `DONT_NOTIFY` when no meeting is worth prepping. |
| **Create a meeting doc** | The user accepts the brief, says no changes are needed, says a revision looks good, or asks to operationalize the prep after Daily Meeting Prep is already active, installed, ready, verified, declined, skipped, deferred, unavailable, not applicable, or explicitly bypassed by the user. | Offer to create a lightweight meeting doc from the accepted non-empty brief, with space for decisions, owners, and follow-ups. |
| **Iterate the meeting doc** | A meeting doc exists and the user asks to change it, or readback shows a content/formatting issue. | Offer the specific doc edit or cleanup needed. |
| **Link or draft share note** | A meeting doc exists and does not need edits. | Offer to link it to the calendar event or draft a short Slack/email note for review with the doc, goal, open questions, and decisions needed. Do not offer to post or send the note directly unless the user explicitly asks for posting/sending or approves a reviewed draft. |
| **Set post-meeting reminder** | The doc handoff step has been completed or declined, follow-up has not been handled, and notes/transcript availability is not already confirmed. This still applies after the meeting has ended when a future check can be scheduled for notes/transcript availability. | Offer an event-aware automatic follow-up that starts checking at the event-derived time, or a small post-end buffer when the meeting has already ended, and cancels itself after meeting notes/transcript are found and follow-up is handled. |
| **Post-meeting follow-up** | The meeting has ended and notes, transcript, or recap evidence is already available, or the user explicitly asks to check available notes now and draft the follow-up. | Offer or run `follow-up-after-call` for the recap, customer/internal follow-up, action tracker, and CRM-ready next steps. |

Daily Meeting Prep is the primary accepted-brief continuation owned by this skill. Treat `daily_meeting_prep` as ineligible when `sales_preflight.context.automations.daily_meeting_prep.status` is `active`, `installed`, `ready`, `verified`, `declined`, `skipped`, `skipped_for_now`, `deferred`, `deferred_environment_api_limitations`, `unavailable`, or `not_applicable`, or when other readback clearly shows the user already has a matching Sales Daily Meeting Prep automation. Do not offer meeting doc creation as the accepted-brief default while Daily Meeting Prep remains eligible, unless the user explicitly asks for the doc instead.

#### Post-Meeting Reminder

When offering `Set post-meeting reminder`, include the automatic trigger behavior and the exact proposed schedule derived from the meeting event, for example: `Want me to automatically start checking 5 minutes before the meeting ends, at {date/time/timezone}, then pull the notes/transcript when they show up and draft the recap plus action tracker?` Use the selected calendar event's scheduled end time minus a default 5-minute lead buffer in the event timezone. The proposed first run must be in the future; if the lead-buffer time has already passed, use the next future event-aware time before the scheduled end when possible, otherwise use a small future post-end buffer. If the meeting end time is unknown, ask for it in the final continuation instead of guessing. If the meeting already ended and notes/transcript evidence is available, use `Post-meeting follow-up` instead of scheduling; if availability is unknown or not yet found, still offer the event-aware check/reminder instead of generic next-step advice.

When the user accepts `Set post-meeting reminder`, create the narrowest event-aware reminder or automation the available tool supports. Prefer a one-time future wakeup when it can reliably run after notes are available; otherwise create a short-lived heartbeat whose first run is the exact event-aware start time above and whose prompt says to return `DONT_NOTIFY` until notes/transcript are found. The reminder instructions must name the meeting, meeting date/time, prep doc or calendar link when available, sources to check for notes/transcript, and intended follow-up action: pull notes/transcript, summarize decisions and action items, and run or offer `follow-up-after-call`. They must also say that once notes/transcript are found and the follow-up has been drafted or offered, the automation should cancel/delete itself so it does not keep running. Do not create a daily, weekly, generic 7 PM, arbitrary long-interval, or untethered recurring automation unless the user explicitly asks for that recurrence. If the tool cannot schedule a future event-aware first run, report the limitation and ask for an explicit fallback time instead of creating a generic schedule. After creating the reminder, read back the exact first-run date/time, cadence if any, and self-cancel condition as the final natural continuation.

#### Daily Meeting Prep Automation

When the user accepts `Offer Daily Meeting Prep`, load `[$sales:user-context](../user-context/SKILL.md)` and its `references/automation.md` plus `plugin-author-config/automation-config.md`. Use the `daily_meeting_prep` entry from the later journey automation section, not the default onboarding automation list. Create or repair a dedicated `Sales Daily Meeting Prep` heartbeat automation only after user approval, with its configured weekday 9:00 AM local cadence and launcher instructions. Read back the automation and target thread before claiming it is set up. If the user declines, skips, or defers this offer, record that disposition under `automations.daily_meeting_prep` when the state file is available so future accepted briefs do not keep re-offering the same automation. If the environment cannot persist the automation, say that plainly and continue the meeting-prep journey; do not mark initial Sales onboarding incomplete because this later journey automation was skipped or deferred.

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. Also treat "what's next?", "continue", "next", and similar prompts as requests to advance the current journey unless the user names a different goal. If the previous continuation was `Review the brief`, treat a lightweight acknowledgement as accepting the brief as-is; if Daily Meeting Prep is eligible, move to `Offer Daily Meeting Prep`, otherwise move to `Create a meeting doc`. If the previous continuation was `Review the revised brief`, treat a lightweight acknowledgement such as "okay looks good" as accepting the revision; if the visible continuation already offered Sales Daily Meeting Prep, treat the acknowledgement as approval to create or repair that automation, otherwise move to `Offer Daily Meeting Prep` when eligible and `Create a meeting doc` only when the automation is ineligible or explicitly bypassed. If the previous continuation was `Offer Daily Meeting Prep`, treat a lightweight acknowledgement as approval to create or repair the automation. After resolving the accepted action or resume request, apply the `Final Continuation Invariant`.

Keep the continuation separate from the brief format so it does not rename, reorder, or add sections inside the provided shape.

### Context Sufficiency

Gather enough relevant context to make the brief grounded and correct:

- Do not stop after the first available source when another accessible source could materially change the agenda, risk framing, account posture, recommended close, or next action.
- Prefer high-value evidence gathering during research and tighter synthesis in the final brief.
- Use as much direct, high-signal context as is helpful for confidence, but include only the highest-leverage facts, gaps, and inferences in the user-facing output.
- When time, access, or source availability limits context gathering, name the limitation and its likely impact.

### Search Discipline And Yielding

Use bounded, direct searches rather than exhaustive retrieval:

- Start with the source categories most likely to change the meeting objective, agenda, risks, close, or next action.
- For each attempted source, use targeted queries and stop after useful evidence, a clear no-result, or two failed attempts.
- Do not chase indirect, mirrored, or convoluted paths to reconstruct unavailable source truth; use `Authority and gaps`.
- If repeated errors, auth gaps, rate limits, ambiguity, or missing access block reliable prep, stop searching and tell the user the core issue, what evidence is available, and the shortest unblock option.
- Prefer a limited brief with `Known Limitations` or a concise clarification over long-running retrieval.


## Prep Modes

Prep modes decide what job the skill is doing before output formatting begins:

1. `Single Meeting Prep`: use when the user asks for prep for one specific customer meeting, account, invite, attendee, or topic.
2. `Daily Prep Digest`: use when the user asks for a day-based summary or morning prep digest. Start from `calendar`, keep meetings with at least one external attendee, and produce one chronological digest.
3. `Scheduled Meeting Selection`: use only for system-triggered automations, heartbeats, recurring check-ins, or scheduled runs. Start from `calendar`, prepare exactly one meeting where prep would materially help, briefly say why it was selected, and return `DONT_NOTIFY` if no qualifying meeting exists. Choose among candidates using the strongest available impact signals:

- customer or prospect importance;
- executive or buyer attendance;
- late-stage opportunity or renewal context;
- explicit agenda urgency;
- unresolved risk or decision topics;
- strategic account status;
- recent customer-facing activity;
- high-stakes internal decision-making;
- launch or product dependencies;
- leadership visibility;
- whether a prep brief would improve the user's next action.

## Procedure

Use this lifecycle as the normal operating model: resolve the meeting and gather high-value context, draft the prep, iterate in chat, create or draft the accepted artifact only after the user is happy with the content, then help drive the next operational step. Do not jump straight from the first draft to document/deck creation unless the user asked for an artifact up front or the accepted output already exists.

1. Start from the meeting source.
   Use `calendar` for day-based, scheduled, invite-dependent, or user-requested calendar selection, including `next`, `upcoming`, `today`, `tomorrow`, or latest scheduled meeting prompts. Read title, timing, attendee list, description, and invite body before adding narrative unless the user supplied equivalent meeting details.
2. Qualify the meeting for the active prep mode.
   For `Single Meeting Prep` and `Daily Prep Digest`, keep the customer/account anchor and stop if the meeting is not clearly customer-facing or account-related. For `Scheduled Meeting Selection`, customer/account meetings win; otherwise choose only a high-impact non-routine work meeting.
   For non-customer meetings selected only by `Scheduled Meeting Selection`, do not add customer-specific objections, CRM facts, public account research, customer-facing assets, or `Broader Account Context` unless the meeting evidence actually names a customer or account.
3. Define a one-sentence focus hypothesis before gathering supporting context.
   Use the invite title/body, user-supplied target, attendee roles, recent scheduling or email context, internal discussion that references this meeting or a same-day call, and current account workstreams. Use the hypothesis to prioritize sources, not to exclude strong contrary evidence.
4. Explain attendee relevance for single-meeting briefs.
   Identify external attendees first; include sourced roles or history when reliable. Group internal attendees by role or relevance when individual titles are not sourced. Do not guess titles; say when only email identity is known.
5. Pull current account or workstream state.
   For customer/account meetings, use `crm` and `document_store` for account state and broader context. Match the active opportunity or deal to the meeting topic before using deal facts; if another same-account opportunity appears unrelated, exclude it or label the conflict instead of letting it drive the brief. Capture account-level facts for `Broader Account Context`; promote them into `Upcoming Meeting` only when they directly affect the objective, agenda, risks, questions, or close. For non-customer meetings selected by `Scheduled Meeting Selection`, use internal sources for workstream decisions, blockers, owners, and dependencies instead of forcing account context.
6. Pull continuity and recent context.
   Search `meeting_notes` by exact external attendee emails or names, account name and aliases, opportunity or solution names, invite title terms, and focused topic terms. If no direct prior external customer call is found, say so and use relevant internal meeting records only as internal continuity. Then pull `external_messaging` for unanswered questions, scheduling shifts, tone changes, and promised next steps. Then pull `internal_messaging` and `document_store` for internal strategy that changes the agenda, decision framing, likely objections, or next actions.
7. Run a concise public web enrichment pass only when it materially improves preparation.
   Useful targets include high-confidence external attendee title/company matches, official company or product pages, public customer pages, product or partnership announcements, filings, earnings, funding, leadership changes, and reputable news. If internal continuity is thin, label the brief as first-time or low-context and add public ramp-up context with `Inference:` where needed. If public evidence conflicts with internal sources, defer to internal source truth and mention the discrepancy in `Known Limitations`.
8. Focus the agenda.
   Use invite agenda when present; otherwise recommend a short agenda based on the focus hypothesis and strongest current signals. Broad account-plan items enter the focused agenda only when another strong signal ties them to this meeting, such as the invite, attendee roles, recent message context, prior continuity, a same-day customer call, or a recent note assigning owners.
9. Add a light two-sided alignment frame when needed.
   Use one when a topic involves disagreement, unclear ownership, incompatible expectations, or negotiation around pricing, capacity, data retention, support, roadmap commitments, co-sell, procurement, security, implementation ownership, or executive sensitivity. Use the compact shape `Problem`, `Customer side`, `Seller side`, and `Goal for this meeting`; name people only when sourced and label inferred motives or constraints.
10. Recommend up to 3 existing customer-facing assets to bring.
    Explain why each helps. Do not fabricate, generate, or rewrite assets in this skill.
11. Cite tactical claims and separate facts from synthesis.
    For normal single-meeting briefs, put citations inline on the `Background Context` bullets instead of collecting them in a separate sources section. Each factual `Background Context` bullet should end with the source title, record name, channel/thread, or meeting/date label as visible Markdown link text when a source exposes a useful URL. Use plain labels with `(no useful link available)` when needed. Do not link to meeting join URLs, generic room links, or opaque connector refetch IDs.
12. Assemble the final answer against `Output Shapes` before sending.
    Select the applicable provided shape after the prep mode and meeting type are known, then fill that shape directly. The selected output shape is the only user-facing structure for the brief body; after it, apply `Next Step Guidance` unless an explicit exception applies.

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

Use [references/meeting-selection-and-agenda-rules.md](references/meeting-selection-and-agenda-rules.md) when qualification, domain resolution, agenda selection, attendee enrichment, public enrichment, or asset selection is ambiguous.

## Output Shapes

Use this output shape for normal single-meeting briefs, including customer/account meetings and high-value internal workstream meetings:

```md
# [Meeting Name]

**Date:** [Date / Time]
**Attendees:** [Names + roles]

## Summary

* [Core meeting objective]
* [Current account, opportunity, or workstream signal]
* [Top implication, risk, or source gap for this meeting]

## Goal

[The specific outcome to achieve: decision, feedback, alignment, commitment, or next step.]

## Open Questions

* [Most important unresolved question]
* [Question this meeting should answer, tied to CRM, transcript, or invite gaps when relevant]
* [Decision or clarification needed]

## Proposed Agenda

1. [Topic or question to discuss]
2. [Topic or decision to resolve, tailored to meeting type and deal/workstream stage]
3. [Confirm next steps / owners]

## Background Context

* [Compact account/deal or workstream snapshot with inline source citation]
* [Relevant attendees, prior-call/internal-prep continuity, or customer/team context with inline source citation]
* [Useful assets, constraints, and material source gaps with inline source citation when factual]
```

Clarification and digest requests are not normal single-meeting briefs and still use their specialized shapes:

- `Clarification Stop`: end with only the unresolved required input question.
- `Daily Prep Digest`: use `**Today's External Meetings**`, one compact chronological brief per meeting, and `**Priority Watchouts**`.

For normal single-meeting briefs, use only the provided single-meeting output shape for the brief body. Fill the placeholders with the best available sourced facts. Do not add, rename, reorder, or omit headings inside the brief body. After the brief body, end with the natural continuation selected by `Next Step Guidance`.
