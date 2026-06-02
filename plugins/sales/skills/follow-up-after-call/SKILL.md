---
name: follow-up-after-call
description: Turn a recent customer, partner, or important internal call transcript or grounded call notes into a seller-ready follow-up package with a recap, next steps, external comms when applicable, CRM next steps when applicable, and an internal follow-up draft.
---

# Follow Up After Call

Use this skill for seller post-call follow-up after an external customer meeting, partner call, or important internal call with sales follow-through value.

It produces a seller-ready follow-up package from grounded call evidence:

- call summary
- customer and seller next steps
- external follow-up copy when applicable
- CRM-ready next-step text for customer/account calls
- internal team recap draft when useful

Default behavior:

- draft-only output unless the user explicitly asks for private draft creation
- copy/paste CRM output only; never write to `crm`
- draft-only `internal_messaging` team recap output under `Internal Follow-Up`
- private `external_messaging` email draft creation only when requested or clearly appropriate, supported by the selected App, and never sent without explicit approval
- explicit placeholders for unknowns

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the package also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the follow-up package.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided context to identify the required information. Source access can suggest concrete candidates, enrich, or verify the information, but do not draft the package until grounded call evidence is supplied or confirmed by the user.

The skill can still produce a limited follow-up package from pasted transcripts, grounded notes, uploaded/exported context, or user-linked context alone when that context is sufficient. Connectors add significant value and reduce the burden on the user, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] Grounded call evidence, such as a transcript, recording transcript, pasted notes, call notes doc, or message thread

Recommended inputs:

- `account_name`
- `call_date`

Accepted optional inputs:

- `primary_contact_name`
- `primary_contact_email`
- `known_chat_channel`
- `opportunity_name`
- `opportunity_link`
- `account_context_notes`

Defaults:

- `chat_mode=draft_only`
- `crm_mode=copy_paste_only`
- `unknown_marker=Unknown`
- `missing_due_date_marker=TBD`

Use [references/request-schema.yaml](references/request-schema.yaml) when structured input validation, YAML normalization, or machine-readable field shape matters.

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting the package.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. When `crm` is available, include a bounded CRM lookup before relying on calendar, docs, messages, meeting notes, or public context alone. If CRM returns one high-confidence account match, use it as the primary account candidate; if multiple plausible account matches remain, ask the user to choose from concrete candidates.
- Before asking the user to paste a transcript or notes, first try the workflow source categories that can identify or supply call evidence: `calendar` for recent call candidates, `meeting_notes` for transcripts or call notes, `document_store` for exported call notes, and `external_messaging` only when call details plausibly live in a customer-facing thread. Manual pasted evidence is the final fallback after those categories are unavailable, empty, or insufficient.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

If required inputs remain missing or ambiguous, first attempt a bounded candidate pass through the source category that owns the missing anchor, within the Fast Candidate Resolution budget. Ask one friendly clarification only after that pass. Ask only for unresolved inputs; include up to 5 concrete lettered options from source-backed or user-provided candidates when available.

If call evidence is missing, search recent `calendar` or `meeting_notes` candidates first; only ask the user after offering up to 5 defaults or confirming no plausible candidates were found.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
Which call should I use?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Stop only when no recent call, meeting, transcript, note set, customer/account, timeframe, or sufficiently detailed user-provided call evidence can be identified.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `calendar`: recent meeting candidates, titles, attendees, times, and first-pass call selection when the user asks for a recent call without naming a specific transcript or notes source.
- `meeting_notes`: primary transcript, call notes, meeting recording transcript when available, participant language, decisions, commitments, asks, risks, and source links.
- `document_store`: exported transcripts, call notes, account notes, follow-up docs, and account context that sharpens seller action.
- `crm`: account and opportunity context, stakeholder/account history, opportunity candidates, and CRM-ready next-step framing. Never write to CRM.
- `external_messaging`: customer-facing thread context, private email draft creation when allowed, and recovery evidence when call details live in an email/chat thread.
- `internal_messaging`: internal account-channel selection, internal context, and draft-only team recap destination guidance. Never post or send.
- user-provided context: pasted transcripts, grounded notes, uploads, exports, links, and call context that can serve as working evidence.

Source obligations by intent:

- For post-call follow-up, grounded call evidence is required from `meeting_notes`, a meeting recording transcript, exported transcript, pasted transcript, grounded notes, or a customer-facing message thread. CRM, docs, or summaries can enrich the package but cannot substitute for call evidence.
- Do not use `calendar`, `crm`, `document_store`, `internal_messaging`, or public context to produce call recaps, commitments, quotes, objections, or participant language unless those sources contain grounded call notes or customer-facing thread evidence.
- When the user asks for the latest or recent call without naming one, check `calendar` and `meeting_notes` for concrete call candidates before asking. If both are unavailable and user-provided evidence is insufficient, ask for transcript, notes, or the specific call.
- For customer follow-up packages, check `calendar` for upcoming related meetings when available. If a relevant future meeting is found, use it in next-step timing; if checked and no relevant meeting is found, say so briefly only when timing matters.
- For customer/account follow-up packages, `crm` is required when CRM is available and a customer/account anchor is supplied, inferred, or confirmed. Use it for opportunity, account, contact, owner, recent activity, and CRM-ready next-step context when it can materially improve next steps, names, wording, or risk framing. If `crm` is unavailable or yields no useful context, continue from grounded call evidence and label the CRM gap.
- Stop after the follow-up package has grounded call evidence plus the highest-value timing/account enrichment; offer to deepen optional lanes instead of continuing broad searches.

Primary evidence order:

1. `meeting_notes` transcript
2. `meeting_notes` meeting recording transcript when available
3. other exported meeting transcript when available
4. pasted transcript or grounded notes
5. `document_store` meeting notes
6. `external_messaging` thread or message retrieval as a recovery path

Authority and gaps:

- Keep CRM/account context authoritative for CRM-owned customer truth in customer/account packages, but not as a substitute for call evidence itself.
- If a preferred evidence lane is unavailable, continue with the next supported lane before dropping to fallback evidence.
- If no grounded evidence lane is available, stop and explain the missing source.
- If `crm` and `document_store` are unavailable, continue without account enrichment and label the gap.
- If optional account, calendar, email, or internal-message enrichment is slow or unavailable, do not delay a package that already has grounded call evidence; continue and label the missing enrichment.
- If private `external_messaging` or `internal_messaging` evidence requires access not yet authorized, ask for consent before retrieval.
- If meeting recording cannot be retrieved directly, ask for exported transcript text or a linked doc rather than dropping the source from scope.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the follow-up-after-call experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Follow Up After Call
This skill turns a recent customer, partner, or important internal call into a follow-up package. It can use calendar events, call transcripts, meeting notes, CRM, docs, email, Slack, or pasted notes. It can draft customer-facing copy, internal recaps, and CRM-ready updates for review, but it does not send, post, or write into CRM without approval.
```

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Follow Up After Call next-step behavior and action text. Onboarding, draft creation, CRM writeback, posting or sharing, document creation, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the call-follow-up continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `follow-up-after-call` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/writing/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the follow-up package** | The first substantive recap, next steps, and draft package has just been produced. | `Anything you'd change before this becomes the working follow-up?` |
| **2. Review the revised follow-up package** | The user asked for any change to the package, including a shorter recap, edited next step, tone change, recipient change, source adjustment, or formatting tweak. Make the change in chat first. | `Anything else you'd change? If that looks good, want me to draft the customer email, internal recap, CRM next steps, or action tracker for review?` |
| **3. Prepare the follow-through artifact** | The user accepts the package, says no changes are needed, says a revision looks good, or asks to operationalize the follow-up. | Offer to produce the most useful next artifact or draft action, prioritizing customer email, internal recap, CRM-ready next steps, action tracker, or follow-up doc over broad suggestions. |
| **4. Review the artifact or draft** | An email draft, internal recap, CRM-ready update, action tracker, or follow-up doc exists, or the user asks to change it. | `Anything you'd change before I save, post, or write this where it belongs?` |
| **5. Post, save, or write approved follow-through** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as creating or saving the external draft, posting the approved internal recap, saving the follow-up doc, or writing the approved CRM next steps. Do not post, send, or write CRM changes unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the follow-up package, treat a lightweight acknowledgement as acceptance and move to `Prepare the follow-through artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post, send, or write externally. If the previous continuation offered to post, save, or write a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Procedure

### 1. Normalize the request

- Convert the user request into the normalized input shape.
- Keep source provenance for every material fact.
- Treat a request such as `follow up from my call with <company> earlier today`, `this morning`, `yesterday`, or another recent timeframe as a retrievable source request, not as missing evidence.
- Normalize company/account names into `account_name`, normalize relative dates or timeframes into `call_date` when possible, and proceed to source retrieval before asking the user to paste notes.
- If the user provides only vague recollections with no transcript, notes, account/company, date/timeframe, direct link, or retrievable source handle, stop and explain the missing evidence in one line.

### 2. Ingest the best grounded source

Supported production paths:

- `meeting_notes` transcript via a successful connector read
- `meeting_notes` meeting recording transcript when the source exists and a runtime retrieval path or exported transcript is available
- other exported meeting transcript when the source exists and a runtime retrieval path or exported transcript is available
- pasted transcript or pasted notes
- `document_store` notes via a successful docs read
- `external_messaging` thread or message retrieval as a secondary recovery path

Source-specific rules:

- For `meeting_notes`, fetch a provided `file-` call id directly. Otherwise search with `account_name` plus call date/timeframe and 0 to 2 meeting topics, then fetch the best match.
- For prompts like `my call with <company> earlier today`, search today's meeting notes and transcripts for that company/account before asking for pasted notes.
- For meeting recording, accept a direct record link, exported transcript, linked doc, or minimum identifiers: record title, call date/timeframe, customer name, and 1 to 2 keywords.
- For `external_messaging`, use it as a recovery lane when the call evidence lives in chat and transcript systems are not the best available source.
- When a meeting record exposes useful links in metadata or the meeting description, preserve them as supplemental source links. If a link is explicitly labeled source of truth, notes, transcript, or call notes, include it alongside the primary transcript evidence and in the internal draft's `Source` section when relevant.

If multiple meeting recording candidates remain plausible after retrieval, present candidate titles with one-line rationale and ask the user to choose before drafting.

### 3. Pull account context when it sharpens the seller action

When `account_name` is known or can be resolved confidently from the evidence, use `crm` and `document_store` to sharpen account state.

- Prefer `crm` first when the package would benefit from opportunity context, stakeholders, or account history.
- Use `document_store` account plans or notes only when they materially change the recency lane.
- If `crm`/`document_store` context is unavailable or resolution is ambiguous, continue with the source evidence and label the missing account-context lane explicitly.

### 4. Build the seller follow-up package

Always return the package in this order:

1. `Call Summary`
2. `Next Steps`
3. `External Comms`
4. `CRM Next Steps`
5. `Internal Follow-Up`
6. Draft/update status line

Render standard bold section labels, including `**Next Steps**`; do not replace them with loose labels such as `Main blockers / follow-ups`. Keep the package evidence-grounded, use explicit placeholders for unknowns, and never invent attendees, dates, commitments, pricing, or decisions. Verbatim draft content, including the email body and internal follow-up draft, must be formatted as Markdown block quotes.

### 5. Determine whether CRM next steps apply

CRM next steps apply only to external customer or account relations.

- For internal calls, write exactly: `Not applicable: this was an internal call.`
- For external calls, determine the most relevant `crm` opportunity. If no clear opportunity is available, still draft the one-sentence update and label it `(paste into the relevant opp)`.
- Do not claim `crm` was updated.

Use [references/opportunity-and-channel-selection.md](references/opportunity-and-channel-selection.md) when opportunity ranking is ambiguous or internal-channel selection requires more than the safety defaults below.

### 6. Build the Internal Follow-Up draft safely

Default to the `internal_messaging` category for internal follow-up, suggest the safest relevant channel when one can be identified, reject channels that appear externally shared, and return draft text only.

The `Internal Follow-Up` draft should be a single structured team recap for the selected or suggested channel, not a generic internal note or a top-level-plus-thread split unless the user asks for a thread. Use the selected internal messaging app's native formatting, including user mentions for attendees or owners when available. If no useful call-notes link exists, say so rather than inventing one. If internal-only status is unclear, add a short warning to verify the channel before posting.

### 7. Keep the package commercially useful

- Bias toward decisions, risks, next steps, buying process, procurement, technical blockers, and stakeholder movement.
- Keep `External Comms` concise and seller-usable when an external email is applicable.
- For internal calls, mark external email and CRM next steps not applicable instead of drafting external email.
- Keep the CRM sentence to exactly one sentence.
- Keep the internal draft compact, internal-facing, and shaped as a team recap.

## Output Shapes

Use bold section labels, not H1/H2/H3 headings, for the normal package.

### Call Summary

Required subsections:

- `Primary evidence`
- `TL;DR`
- `Context / Goal`
- `Key Points`
- `Decisions / Commitments`
- `Risks / Blockers`

Rules:

- `Primary evidence` should name the source lane and source handle. Render the source handle as a clickable Markdown link when the connector exposes a useful URL; use a plain source label only when no useful link is available.
- If the primary evidence source exposes supplemental source-of-truth notes, call notes, or transcript links, list them in `Primary evidence` after the primary source instead of replacing the primary source.
- `TL;DR` should contain 2 to 4 bullets.
- Do not invent details absent from the source.
- When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL.

### Next Steps

Always include both groups:

- `Customer`
- `Seller`

Line shape:

```md
- [ ] Action - Owner - Due date (or TBD) - Notes
```

If there are no concrete next steps for one side, include one line with `Unknown` or `TBD` markers instead of omitting the section.

### External Comms

Required elements for external calls:

- `Subject options (recommended first):`
- exactly 3 numbered subject lines
- `Recommended subject:`
- email body formatted as block quote text
- `Draft link:` when an email draft was actually created or saved through `external_messaging`

Rules:

- If the selected call was internal, write `Not applicable: this was an internal call.` and do not draft external email content.
- Keep the draft about 150 to 220 words.
- Format the verbatim email body as a Markdown block quote. Do not use a fenced code block for ordinary email copy.
- If names or emails are missing, use placeholders such as `<FirstName>` and `<Team>`.
- Do not include sensitive internal language.
- Draft creation through `external_messaging` is allowed when the user asked for a follow-up package, follow-up email, or post-call follow-through and the selected App supports private draft creation. This does not authorize sending.
- If the user asks for chat-only output or no connector write, do not create a draft.
- If a real draft was created or saved, render `Draft link:` as a clickable Markdown link to the draft URL, message URL, or web URL returned by the App. If multiple drafts were created, list one clickable link per draft.
- If the workflow only produced email copy in chat, write `Draft link: Not created; copy drafted in chat only.`
- If a real draft was created but the App exposes no useful URL, write `Draft link: <recipient or subject> (no useful draft link available)`.
- Never fabricate a draft link from an opaque id or guessed mailbox URL.
- Never send outreach without explicit user approval.

### CRM Next Steps

Rules:

- CRM next steps apply only to external customer or account relations.
- For internal calls, write exactly: `Not applicable: this was an internal call.`
- For external calls, use exactly one sentence.
- For external calls, include call date, next seller action, customer action, and outcome or success criteria.
- If the opportunity is unresolved, append `(paste into the relevant opp)`.
- Do not claim `crm` was updated.

### Internal Follow-Up

Rules:

- Suggest the safest relevant Slack or other `internal_messaging` channel before the draft when one can be identified. If no channel was user-provided, search or resolve likely internal channels from the account name, call title, meeting topic, or saved account-room context when the selected app and permissions allow it.
- Render the suggested channel as a clickable Markdown link when the `internal_messaging` App exposes a stable channel URL or permalink. Never fabricate a channel URL from an opaque id or guessed workspace path.
- Before writing `no verified internal channel link found`, search `internal_messaging` once for the meeting/account/project name and use the best safe destination link if found.
- Default to one consolidated internal message. Split into a top-level message plus thread reply only when the user asks for a threaded format or an identified channel norm clearly requires it.
- Format the verbatim internal follow-up draft as a Markdown block quote when returning it inside the package. Do not use a fenced code block for ordinary chat copy. When creating an actual private draft in `internal_messaging`, write the message content directly rather than wrapping it as a quote.
- The internal follow-up draft is a team meeting recap, not a generic internal note.
- Include a brief summary, next steps, owners or TBDs, and structured sections when source evidence supports them.
- Start with a bold meeting title and one concise summary paragraph that names the launch path, business impact, decision point, or main follow-through theme. Do not repeat the same TL;DR again later in the message.
- Include attendees on one line. Use the selected internal messaging app's native user mention format for attendees when available; otherwise use readable names.
- Use bold section labels in this order when source evidence supports them: `Key Notes`, `Decisions`, `Action Items`, `Open Questions / Risks`, and `Source`.
- De-duplicate content across sections.
- Include owners or `TBD` in action items. Use native user mentions for owners when available.
- Include clickable Markdown source links when available, including a clickable Markdown call-notes link when the meeting record exposes one. Prefer the primary transcript link first, then supplemental source-of-truth notes or call-notes links exposed by the meeting record.
- If no useful call-notes link exists, state `Call notes: no useful link available` or equivalent inside the draft rather than inventing a link.
- Use the selected `internal_messaging` App's markdown/message format.
- Use no `##` headings in draft text.
- Prefer concise bullet lists; keep the draft compact enough for Slack or Teams scanning, but allow the structured sections to run longer than 12 lines when the call has real decisions or action items.
- Always return draft text only, never a sent-message claim.
- If channel safety is unclear, add a short warning line after the draft text.

### Draft / Update Status Line

After `Internal Follow-Up`, include one plain status line describing what was and was not created outside chat. If nothing was created or updated, write exactly: `No email draft, Slack post, or CRM update was created.`

If the workflow created a private email draft or other explicit draft through a connector, name what was created and still state that nothing was sent or posted and CRM was not updated unless the user explicitly approved that action and it actually succeeded. Never claim `internal_messaging`, `external_messaging`, or `crm` was updated unless a tool result proves the exact action.

## Failure Handling

When blocked:

1. State the blocker in one line.
2. Say whether the blocker is hard or degraded.
3. Emit the best partial package you can without fabricating facts.

## Rules

- Keep the package seller-ready, concise, and explicit about missing information.
- Never claim `internal_messaging`, `external_messaging`, or `crm` was updated unless a tool result proves the exact user-approved action succeeded.
- Never send outreach without explicit approval.
- When an actual email draft was created or saved, include its clickable draft link; when only copy was drafted in chat, say no email draft was created.
- After the package, ask for iteration first, and include any onboarding resume or move-on path in the same final natural continuation so the response never has two competing CTAs.
- Once the user accepts the result or asks to move on, offer to create drafts in email and/or the best suggested `internal_messaging` channel as applicable.
- If an iteration introduced a reusable preference, apply `skills/user-context/references/plugin-memory.md`: narrow, low-risk accepted preferences can be summarized and saved automatically; broad, sensitive, ambiguous, or high-risk preferences require explicit save approval.
