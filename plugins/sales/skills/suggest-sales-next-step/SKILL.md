---
name: suggest-sales-next-step
description: Run scheduled or manual Sales check-ins that summarize recent Sales work and recommend one next Sales workflow to try.
---

# Suggest Sales Next Step

Run a Sales check-in that turns the user's visible recent Codex conversations, sales-adjacent work, calendar signals, and saved Sales state into one practical next step. This skill owns scheduled check-in behavior so automations can stay thin and durable.

Done well, a Sales check-in is a short natural-language note, not a generic usage report or feature tour. It should answer two questions quickly: what has the user been doing with Sales, if anything, and what is worth trying next. Prefer a timely workflow grounded in a real meeting, account, customer question, deal, or recent Sales output. If no concrete target emerges, default to a Sales workflow the user has not tried yet by reading `skill_experience` and `next_skill_candidates`, excluding helper/provider skills. Keep tips, setup notes, and source gaps subordinate to the one recommended workflow.

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

This skill needs enough visible context to inspect recent Sales work, saved Sales context, calendar opportunities, or a user-supplied timeframe.

The skill can still produce a limited next-step recommendation from the current thread, pasted context, visible recent Sales work, saved context, or user-provided priorities when connector context is unavailable. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require one anchor:

- [required] recent Sales context, calendar context, saved plugin context, visible thread context, or timeframe

Accept when provided:

- timeframe, preferred workflow family, quiet/notification preference, specific source gaps, and scheduled heartbeat mode

**Context Rules:**

- If a required anchor is missing or ambiguous, use the last 7 days as the default timeframe when the user asks for a next step without a timeframe.
- If multiple materially different scopes are plausible, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce concrete defaults, then ask the user to confirm before drafting.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. When `crm` is available, include a bounded CRM lookup before recommending a customer/account-specific workflow from docs, calendar, messages, notes, or public context alone.
- Before asking the user to provide priorities, recent context, or a timeframe, first try the source categories that can produce a concrete next-step candidate: visible thread history and saved context, then `calendar` for upcoming/recent meeting opportunities, `meeting_notes` for follow-up opportunities, `crm` for customer/account-specific workflow fit, `data_enrichment` for account/contact research or prioritization gaps, and `document_store`, `external_messaging`, or `internal_messaging` when they can cheaply surface a practical source gap or next action. Manual priorities are the fallback after those categories are unavailable, empty, or too ambiguous.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous and cannot be safely defaulted, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `calendar`: upcoming and recent customer/account meetings, meeting titles, dates, attendees, external domains, invite descriptions, and first-pass workflow opportunities.
- `crm`: account or opportunity context that materially changes the recommended Sales workflow.
- `meeting_notes`: recent call evidence, transcript/notes availability, follow-up opportunities, and customer/account topics.
- `document_store`: source-of-truth docs, saved team resources, account docs, and onboarding/setup resources that materially affect next-step recommendations.
- `data_enrichment`: contact, company, fit, and trigger gaps that suggest enrichment, account prioritization, or research workflows.
- `external_messaging`: recent customer asks, unanswered threads, promised follow-ups, and evidence of needed follow-through.
- `internal_messaging`: internal blockers, team coordination, account-channel context, and source gaps when relevant to the recommendation.
- user-provided context: visible thread history, pasted priorities, prior Sales outputs, saved preferences, and explicit next-step constraints.

Authority and gaps:

- Use visible recent Sales work and calendar/meeting evidence for the recommendation; do not invent usage history or upcoming customer work.
- For customer/account-specific recommendations, use CRM when available for CRM-owned account or opportunity truth before treating other sources as sufficient context.
- Use `meeting_notes`, `external_messaging`, and `internal_messaging` to identify concrete prep, follow-up, or source-gap opportunities; do not recommend transcript-backed or CRM-backed workflows when the required source is absent unless the prompt is framed as manual/pasted-context.
- Use `data_enrichment` only to identify account/contact research or prioritization opportunities; do not treat enrichment as proof of CRM state, upcoming meetings, or transcript-backed follow-up work.
- Treat saved context as a relevance hint, not proof that a workflow has current evidence.
- If source access is partial, make the recommendation from available context and name what would improve confidence.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the suggest-sales-next-step experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Suggest Sales Next Step
This skill runs a short Sales check-in: what you've been doing, what looks quiet or blocked, and one Sales workflow worth trying next. If there is no timely meeting or account signal, it recommends a Sales workflow you have not tried yet.

```

Starter prompts:

- Primary default prompt: `Suggest my next best Sales step.`
- `@Sales suggest my next best Sales step for today.`
- `@Sales review my recent Sales work and tell me the highest-leverage thing to do next.`
- `@Sales check my calendar and recent Sales context for the next useful workflow to run.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Suggest Sales Next Step next-step behavior and action text. Onboarding, check-in readbacks, recommended workflow launch, draft creation, automation setup or repair, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the recommendation continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `suggest-sales-next-step` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/linking an artifact or automation, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation. In scheduled heartbeat mode, `Worth Trying Next` owns the direct user-facing CTA and the final response must still end with the heartbeat XML block.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, heartbeat readback, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the recommendation** | The first substantive recommendation or check-in card has just been produced. | `Want me to run that next step now, or draft the exact message/update so you can review it first?` |
| **2. Review the revised recommendation** | The user asked for any change to focus, target, evidence, suggested prompt, source-gap wording, or check-in copy. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to run the recommended action or turn it into a reviewed draft?` |
| **3. Prepare the recommended action** | The user accepts the recommendation, says no changes are needed, says a revision looks good, or asks to act on it. | Prefer running the recommended focused action when enough context exists; otherwise draft the exact prompt, message, update, artifact, or automation setup/repair step that the recommendation calls for. |
| **4. Review the prepared action** | A draft prompt, message, update, artifact, or automation setup/repair proposal exists, or the user asks to change it. | `Anything you'd change before I run, save, or set this up?` |
| **5. Run, save, or set up the approved action** | A reviewed action exists and does not need edits. | Offer the specific supported action, such as running the recommended workflow, saving the reusable prompt, setting up or repairing the weekday check-in automation, or creating the reviewed update. Do not post, send, or write externally unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the recommendation, treat a lightweight acknowledgement as acceptance and move to `Prepare the recommended action`. If the previous continuation offered to prepare a prompt, message, update, artifact, or automation proposal, produce that item for review; do not interpret the acknowledgement as approval to post, send, write, or set up an automation unless that exact action was offered. If the previous continuation offered to run, save, or set up a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

### Suggested User Prompts

Any suggested user prompt in a Sales check-in must be short, simple, and realistic. When the audit finds a real target, keep the prompt to the invocation only: `Use Sales <workflow> for <actual target>.` When the default fallback is an untried workflow and no concrete target is visible, use a runnable input-lane prompt such as `Use Sales prioritize-accounts with a pasted account list.` Do not include the work the focused workflow already knows how to do, such as `pull together`, `draft`, `give me`, output lists, source instructions, missing-input handling, or step-by-step constraints. Explain expected outputs in the surrounding check-in text, not inside the suggested prompt.

### State

Inspect `$CODEX_HOME/state/plugins/role-specific-plugins/sales/onboarding-state.json` when it exists for guided workflow progress, Sales check-in status, company selling-context learning status, quiet/complete state, onboarding gaps, `skill_experience`, and `next_skill_candidates`. Use `skill_experience` plus `next_skill_candidates` as the default workflow inventory when no timely meeting, account, customer question, or deal signal is available. Exclude `suggest-sales-next-step`, `index`, `user-context`, and provider/helper skills such as `salesforce`, `hubspot`, and `zoominfo` from the default untried-workflow recommendation. Use `user-context.md` for source preferences, source-of-truth links, and "do not use" rules. Do not use `onboarding-state.json` as the weekday sales check-in tip ledger; scheduled weekday sales check-ins run in the same recurring thread, so use the current thread's prior check-in messages and any visible recent check-ins as the primary dedupe source. Do not store private customer details, account facts, transcripts, user-facing sales preferences, previous prompts, or prior tip history in `onboarding-state.json`; those belong in source systems, confirmed `user-context.md` entries, or the recurring thread history.

### Invocation Modes

Use `scheduled mode` when the request comes from an automation, heartbeat, recurring check-in, or weekday sales check-in reminder. Use `manual mode` when the user asks to run a Sales check-in, weekday sales check-in, daily check-in, review usage, inspect adoption, or identify where they could get more value from the plugin.

In scheduled mode, treat the automation prompt as a launcher for this skill. If the automation prompt says to "load and follow the skill" or to avoid duplicating daily check-in rules in the prompt, execute this skill's full workflow; do not interpret thin-prompt language as a request to skip the check-in.

Scheduled mode must re-run the check-in and produce user-facing value even when the last check-in was recent, the user has not used Sales, or no new meeting notes are visible. Treat quiet periods as useful signal: say what did not change, then recommend a workflow the user has not tried yet unless a stronger calendar, source-gap, or recent-work signal exists. Use `DONT_NOTIFY` only for true execution failure or an explicit user preference for quiet/paused check-ins, not merely because there was no new plugin usage, no new meeting notes, no connected-source signal, or a recent prior check-in. Do not return a one-line "no action needed" explanation.

Manual mode should answer directly and can be more explicit about evidence gaps, such as inaccessible thread history or missing onboarding state.

## Workflow

1. Establish the audit window. Use a rolling 7-day window ending at the current run time in the user's timezone. For scheduled runs, state the concrete date range only when it prevents ambiguity. The audit target is the highest-signal accessible recent Sales context in that window, plus calendar and Sales state. Use broader conversation history when it is accessible without a reconstruction pass, but do not spend the ordinary path exhaustively enumerating every surface.

2. Gather recent usage from the highest-signal accessible surfaces first: current-thread context, prior check-in outputs in the recurring thread, Sales state, calendar, recent visible Sales activity, and then Codex thread/history/search tools when available. Look for Sales invocations, adjacent sales-support work, customer/account context, launch or GTM work, saved preferences, connector checks, recent artifacts, onboarding progress, and relevant cases where the user did sales-like work without Sales. Stop once you can say what the user has been doing and recommend one useful next action; name visible-source limits instead of continuing into low-yield history searches. Treat the current thread as the primary source for daily check-in dedupe, but not as the boundary of the broader usage audit when recent history is readily available. If cross-thread history is unavailable or partial, say which usage surfaces were visible and avoid claiming precise adoption counts.

3. Build a conversation-level usage map. Track:
   - recent conversations that used Sales;
   - explicit invocation events, such as `@Sales`, `[@sales](plugin://sales@...)`, `$sales`, `sales:<skill>`, or named Sales skill requests;
   - likely implicit invocations from clear sales-task wording;
   - recent conversations that were relevant to Sales but did not use the plugin.

4. Interpret usage as a level-set and diagnostic signal. Do not foreground invocation counts in user-facing output. Instead, summarize the recent workflow patterns the user has been doing, such as meeting prep, follow-up, onboarding or saved-context setup, internal navigation, launch or GTM support, forecast review, pipeline work, customer evidence, or account research. Track breadth internally by naming the distinct Sales skills or workflow families used in the audit window, such as `suggest-sales-next-step`, `prepare-for-meeting`, `follow-up-after-call`, `find-key-internal-sources`, `plan-deal-strategy`, `review-forecast`, `prioritize-accounts`, `find-customer-quotes`, `build-business-case`, coaching, or account/competitive intelligence. Also name relevant sales-like conversations that did not use the plugin when visible. If cross-thread history is partial, prefer language such as `from what I could inspect` over a precise total.

5. Search calendar for timely sales work. Use `calendar` to inspect upcoming calls and recent calls, not just static onboarding state. Default to the next 7 days for prep opportunities and the prior 7 days for follow-up opportunities; widen to 14 days only when the next 7 days has no customer/account-relevant calls. Read event titles, dates, attendees, external domains, invite descriptions, and visible agenda text. Prefer external customer, prospect, partner, or account-related meetings; skip obvious 1:1s, interviews, internal staff meetings, and no-account internal planning unless the title or attendees make the sales value concrete. Name specific events in the check-in, such as `Prep Tuesday's Acme security review` or `Follow up on Friday's Contoso implementation sync`. If calendar access is missing or returns no qualifying calls, say that briefly and do not substitute generic calendar advice.

6. Pair calendar events with concrete value. For upcoming calls, suggest the highest-leverage Sales workflow that would help before the meeting, usually `prepare-for-meeting`, `find-key-internal-sources`, `plan-deal-strategy`, `build-competitive-brief`, or `build-business-case`. For recent calls, suggest `follow-up-after-call`, CRM-ready next steps, internal recap drafts, or product-feedback evidence extraction when a transcript, notes provider, or follow-up source is available. When `meeting_notes` is available, search recent call titles, account names, attendee names, and topic keywords to verify whether follow-up evidence exists before recommending a transcript-backed package. Name the specific call and the concrete artifact the user would get; do not say only that Sales "could help with calls."

7. Identify contextual missed leverage moments. Prefer one or two concrete moments from prior workflows or calendar evidence over generic capability lists. Name the workflow moment, the targeted follow-up or improved prompt, and the value unlocked. Useful patterns include:
   - a prepare-for-meeting draft that could become follow-up scaffolding;
   - call notes that could become CRM-ready notes plus an internal recap;
   - a customer or product question that could use find-key-internal-sources;
   - a prompt that would improve by naming account, source, date, owner, or desired artifact constraints;
   - a repeated CRM/source convention that should be saved;
   - product-feedback evidence that should come from transcripts instead of memory;
   - deal-risk discussion that could become deal strategy or forecast review.

8. Choose the best next usage. Compare recent conversations, calendar opportunities, and onboarding state, then choose the single Sales workflow most likely to create near-term value for the user's actual work. Prioritize an action the user can run right now from available context over a future-only meeting or later follow-up. A future event can still be the topic only when the prompt does useful immediate work, such as drafting prep questions, finding internal sources, creating a notes template, or preparing a follow-up scaffold from already available context. Do not make the best next usage depend on notes, transcripts, meetings, or outcomes the user does not have yet. If there is no new usage or qualifying calendar event, choose the first useful untried workflow from `next_skill_candidates` and `skill_experience`, skipping helper/provider skills and workflows the user dismissed. Use a lightweight prompt that can run from pasted or user-named context when no real target is visible. Explain why this recommendation matters for the user's workflow and what the user would get.

9. Decide whether a source note is warranted. Include `Source Note` only when the audit finds a concrete connector or connected-source gap that affects the recommended workflow, confidence, completeness, or ability to act. Good candidates include connecting, authorizing, or checking `calendar`, `crm`, `meeting_notes`, `document_store`, `external_messaging`, or `internal_messaging`; a connector that appears installed but cannot return useful data; or a missing source category that would unlock the named workflow. Do not use this section for saved preferences, user-context memory, source-of-truth docs that are already reachable, routing advice, broad setup discovery, or general "make the plugin better" coaching. If no clear source improvement is available, omit the section entirely.

10. Decide whether one tip belongs in the check-in. Only include a tip when it directly supports the recommended workflow and is fresh relative to prior visible Sales check-ins. Treat tips as duplicates when they teach the same workflow family, feature, connector/source habit, or prompt tactic even if the wording differs. Good tips are contextual: chaining `prepare-for-meeting` into `follow-up-after-call`, asking `find-key-internal-sources` before drafting, using transcript-backed `find-customer-quotes`, naming the account/date/source when routing is weak, trying an untried workflow family, or asking Sales to remember a reusable format after iterating on an output. Fold the tip into `Worth Trying Next`; do not create a separate feature-tour section.

11. Choose one CTA. The direct action should live in the final `Worth Trying Next` section unless a connector issue is clearly blocking or weakening the recommendation. Make the CTA a short prompt the user can run immediately in the current thread, not a future-dependent offer. Apply the Suggested User Prompts rule: use an actual context target found during the audit when one exists; otherwise use a concrete input lane for the untried workflow, such as a pasted account list, customer question, recent call notes, forecast export, or deal notes. Do not include extra task instructions. Do not emit generic targets such as `latest customer meeting`, `next customer-facing meeting`, `recent external conversation`, or `whatever context is available` when a concrete target was visible. When you include a starter prompt, follow the relevant focused skill's inline first-run and next-step guidance: anchor the prompt in the real meeting, call, account, deal, forecast, account list, customer question, or feedback theme found during the daily check-in audit without overfitting the prompt to incidental details.

## Output

Use these short markdown sections by default. `Worth Trying Next` must be the final user-facing section before the heartbeat XML so the check-in ends on the action the user can take now. Include `Source Note` only when step 9 found a real workflow-time connector or source gap; otherwise omit it. Do not include a separate feature menu, usage report, or standalone `One Tip` section.

```md
**Check-In**
...

**Source Note**
...

**Worth Trying Next**
...
```

`Check-In` should read like a short note, not a report. In one compact paragraph or two bullets, say what the user has been doing with Sales or that things look quiet from the visible sources. Mention likely implicit Sales work and distinct workflow families only when that helps explain the recommendation. Do not include invocation counts or lower-bound totals by default; mention count-like evidence only if the user asks for usage metrics or the count materially changes the recommendation. If broader history is partial, add one short caveat such as `From the visible Sales context...` instead of narrating every source searched. Avoid internal or tool-facing language such as `history surfaces`, `bypass`, `artifact`, `guided workflow`, `runtime`, or `state`; use plain language such as `I found`, `missed opportunity`, `follow-up package`, `meeting prep`, `docs`, `notes`, and `next steps`.

`Worth Trying Next` is the decision section: name one Sales workflow, why it is the right next try, and the output the user would get. Prefer a real meeting, account, customer question, deal, forecast, account list, or feedback theme from the audit. If none exists, explicitly frame the recommendation as a workflow they have not tried yet and use a runnable pasted-context prompt. End this section with exactly one runnable prompt that follows the Suggested User Prompts rule. Put expected outputs in the explanatory sentence or short bullets above the prompt, not inside the prompt. Do not overfit the prompt to incidental dates or every source found during the audit. Do not end with a future-only recommendation such as waiting for tomorrow's meeting or drafting from notes that do not yet exist.

`Source Note` should appear only when there is a concrete connector or connected-source issue for the workflow the check-in is recommending. Name the one missing, unauthorized, stale, or failing source, explain the practical sales impact, and say the workflow can still proceed with manual input when true. Keep the suggestion action-sized and user-invokable. If the only available improvement is saved context, a source preference, routing advice, or broad setup discovery, omit this section and handle the coaching inside `Worth Trying Next`.

Avoid usage counts in scheduled check-ins unless the user asks for metrics or a count materially changes the recommendation, confidence, routing advice, or workflow-time connector suggestion. Speak to recent workflow patterns instead.

For proactive suggestions, be specific. Name the event, account or external domain when visible, date, suggested Sales workflow, and potential value, such as `a two-minute meeting brief`, `CRM-ready next steps`, `a customer follow-up email draft`, `an internal recap for the account team`, or `transcript-backed product feedback evidence`. Keep setup recommendations to the next smallest useful action, not the full downstream checklist. Do not present a broad capability menu unless no concrete usage or calendar evidence is available.

Do not include a generic `Practical rule:` paragraph or a broad definition of explicit versus implicit invocation unless the user directly asks for definitions. Teach invocation behavior through the evidence instead.

Avoid generic usage-report and low-effort framing. Prefer plain sales language such as `next value to unlock`, `stronger meeting prep`, `better follow-through`, `cleaner CRM notes`, `the connected source that would help most`, or `a deeper workflow to try`.

End with exactly one direct CTA unless the user explicitly asks for options.

### Scheduled Heartbeat Output

In scheduled mode, preserve the heartbeat automation response format in the final answer. The final response must end with a `<heartbeat>` XML block containing a `NOTIFY` or `DONT_NOTIFY` decision.

When there is a useful check-in, write the markdown sections above as the user-facing notification text, then append:

```xml
<heartbeat>
  <decision>NOTIFY</decision>
  <message>One-sentence summary of the check-in value.</message>
</heartbeat>
```

Only use this path for true execution failure or explicit quiet/paused preference. Do not use it just because the last check-in was recent or no new Sales usage, meeting notes, or connected-source signal is visible. When this path applies, do not include markdown prose outside the XML block. Return only:

```xml
<heartbeat>
  <decision>DONT_NOTIFY</decision>
  <message>No useful Sales check-in suggestion right now.</message>
</heartbeat>
```
