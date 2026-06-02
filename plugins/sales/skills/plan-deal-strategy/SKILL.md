---
name: plan-deal-strategy
description: Build a post-discovery deal strategy pack with a deal map, buying committee map, procurement risk register, and prioritized next actions from grounded deal evidence.
---

# Plan Deal Strategy

Use this skill for post-discovery deal strategy, not first-call prep.

This skill turns grounded deal evidence into a practical strategy pack for moving an active account forward. It is for situations where deal evidence likely exists in CRM, meeting notes, external or internal messaging threads, docs, calendar milestones, or user-provided notes, and the user needs a concrete plan to advance or unblock the deal.

Do not use this skill for:

- first discovery calls with no prior account context
- generic prospecting
- meeting prep that only needs an agenda and attendee context

For those requests, route to `prepare-for-meeting` when there is a customer meeting anchor, or ask for basic account/context notes and produce lightweight manual prep instead.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the strategy pack.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided or explicitly inferable context to identify an active account, opportunity, renewal, buying process, or deal. Source access can suggest concrete candidates, enrich, or verify the information, but do not draft the full strategy pack until a specific deal/account anchor is selected, clearly inferable, or sufficiently supplied by the user.

The skill can still produce a limited strategy pack from pasted notes, uploaded/exported context, or user-linked context alone when that context is sufficient. Connectors add significant value and reduce the burden on the user, but do not stop solely because connectors are unavailable.

**Inputs:**

- [required] Active account, opportunity, renewal, buying process, or sufficiently detailed deal notes
- [required] Enough evidence to identify the current deal motion, blocker, stakeholder question, or next-action need
- CRM account or opportunity identity when available
- Time window, defaulting to the last 90 days unless the user provides a narrower or broader window
- Output mode, defaulting to `Full Strategy Pack`

Supported modes:

- `Full Strategy Pack`
- `Deal Map Only`
- `Buying Committee Only`
- `Procurement Risk Only`
- `Next Actions Only`

Use [references/request-schema.yaml](references/request-schema.yaml) when structured input validation, YAML normalization, or machine-readable field shape matters. Preserve `sfdc_account_id` as a legacy alias for `crm_account_id`.

If required inputs remain missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. First attempt a bounded candidate pass through the source category that owns the missing anchor. Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. For account and opportunity selection, start with `crm` when available, then use user-provided context, `calendar`, `meeting_notes`, `document_store`, `external_messaging`, or `internal_messaging` as supporting evidence only when that fits the budget. Before asking the user to paste deal notes or name an account/opportunity manually, either offer concrete candidates from those source categories or say which attempted categories were unavailable or empty. Ask one friendly clarification only after that pass. Ask only for unresolved inputs; for each question, include up to 5 concrete lettered options from source-backed or user-provided candidates when available. If no concrete candidates are available, briefly say why and ask free-form.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
Which account or active deal should I build the strategy around?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Stop the workflow only when no account, deal, renewal, buying process, or sufficiently detailed user-provided deal context can be identified, or when the user requests write actions without giving the needed destination and permission.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: authoritative account and opportunity identity, stage, close date, amount, known contacts, owner, account status, recent CRM activity, customer-health context, and other opportunity metadata.
- `meeting_notes`: transcript-backed stakeholder language, objections, commitments, decisions, follow-ups, procurement/security/legal signals, and call continuity.
- `external_messaging`: customer-facing thread progression, approvals, negotiation movement, procurement/legal exchange, unanswered asks, tone shifts, attachments, and promised next steps.
- `internal_messaging`: internal blocker visibility, owner alignment, deal coordination, execution risk, escalation paths, and confidence shifts. Do not use it to override `crm` truth.
- `document_store`: account strategy docs, mutual action plans, implementation docs, risk logs, team planning artifacts, relevant assets, and account notes.
- `calendar`: upcoming decision forums, executive meetings, procurement/legal milestones, timing pressure, and near-term follow-up moments.
- user-provided enrichment exports or public research: optional structured company, contact, usage, market, or public context that can sharpen committee hypotheses. Never treat this as a blocker for completion.

These are semantic source categories, not fixed connector names. Resolve each attempted source to the specific available app, connector, or helper skill through Sales preflight `context.sources` before using connector-specific logic.

Authority and gaps:

- Use each source category for the facts it owns.
- For active account/deal strategy, `crm` is required when CRM is available and an account, opportunity, renewal, or buying-process anchor is supplied, inferred, or confirmed. Keep CRM truth authoritative for account/opportunity metadata, ownership, commercial posture, customer status, and recent CRM activity; do not let docs, messages, notes, public context, or third-party enrichment override CRM-owned deal truth.
- Use `meeting_notes`, `external_messaging`, `internal_messaging`, `document_store`, and `calendar` to sharpen risks, stakeholders, timing, and next actions; do not use them to invent opportunity status, ownership, stage, amount, close date, renewal posture, or active deal presence.
- When a specific opportunity, renewal, product, or solution is selected, supporting evidence must match that deal motion before it shapes the plan. Account-level evidence is useful background, but same-account transcripts, threads, docs, or meetings that point to a different active opportunity should be skipped or labeled as a gap.
- Treat user-provided notes, uploads, exports, and linked context as valid working evidence; label limitations when they cannot be verified against connector sources.
- If a source is unavailable, blocked, stale, ambiguous, or missing required fields, name the gap and either ask for access/input, proceed with a clear limitation, or omit the unsupported claim.
- If evidence conflicts, lower confidence and add an evidence gap rather than forcing a false resolution.
- If discovery yields sparse evidence, continue with a low-confidence output when the user-provided or discovered anchor is sufficient.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the plan-deal-strategy experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Plan Deal Strategy
This skill helps turn grounded deal evidence into a practical strategy pack for moving an active account forward. It can use CRM, meeting notes, transcripts, account docs, email, Slack, competitive context, and user-provided deal notes.

Definitions:
- Buying committee map: a view of the people who influence, approve, use, block, or sign off on the purchase, including their role in the decision.
- Economic buyer: the person with budget authority or final business accountability for the purchase.
- Champion: a customer-side advocate who wants the solution to succeed and can help navigate the organization.
- Procurement risk register: a list of process, legal, budget, security, commercial, or timing issues that could slow or stop the deal.
- Mutual action plan: a shared customer-and-seller plan with owners, milestones, and dates for reaching a decision or launch.

```

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.
- Do not offer doc creation, CRM updates, plugin memory setup, or weekly discovery in that same response.

### Next Step Guidance

This section is the single owner for Plan Deal Strategy next-step behavior and action text. Onboarding, artifact creation, draft creation, CRM writeback, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the deal-strategy continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `plan-deal-strategy` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/writing/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the strategy pack** | The first substantive strategy pack has just been produced. | `Anything you'd change in the strategy pack before we make it operational?` |
| **2. Review the revised strategy pack** | The user asked for any change to the strategy pack, including a small rewrite, added risk, source adjustment, shorter summary, or formatting tweak. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to turn it into an owner/action tracker, MAP outline, internal recap, or CRM-ready update?` |
| **3. Prepare the action artifact** | The user accepts the strategy, says no changes are needed, says a revision looks good, or asks to operationalize the plan. | Offer to create the most useful downstream artifact or draft action, prioritizing an owner/action tracker, MAP outline, internal recap, customer follow-up draft, or CRM-ready update over broad suggestions. |
| **4. Review the artifact or draft** | The tracker, MAP outline, recap, follow-up draft, or CRM-ready update exists, or the user asks to change it. | `Anything you'd change before I save, share, post, or write this where it belongs?` |
| **5. Post, share, save, or write approved action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the tracker, posting the internal recap, drafting the customer note in the external messaging tool, or writing the approved CRM update. Do not post, send, or write CRM changes unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the strategy pack, treat a lightweight acknowledgement as acceptance and move to `Prepare the action artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post, send, or write externally. If the previous continuation offered to post, share, save, or write a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Procedure

Run these steps in order.

### 1) Qualify the request

- If the user asks for prep for an upcoming first call with little/no prior evidence, do not run this skill.
- Return a one-line reason and route to `prepare-for-meeting` when there is a customer meeting anchor, or ask for basic account/context notes and produce lightweight manual prep instead.
- If the user asks for a partial artifact, use the matching mode and keep the rest of the workflow scoped to that artifact.

### 2) Resolve account and deal anchor

- Resolve account identity from `account_name`, `crm_account_id`, user-provided notes, linked context, or a source-backed candidate.
- Accept `sfdc_account_id` as a legacy alias for `crm_account_id` when older inputs use it.
- Resolve the best opportunity anchor when possible from `opportunity_id`, `opportunity_name`, ranked CRM candidates, or clearly supplied user context.
- When the user names both an account and opportunity, product, solution, renewal, or initiative, use the named deal motion to choose among same-account CRM opportunities before gathering supporting evidence.
- Build a small alias set from the selected opportunity name, product or solution terms, CRM activity titles, and user wording. Use those aliases to validate related meetings, transcripts, threads, and docs.
- Pull `crm` truth first when available for stage, amount, close date, known contacts, and recent account activity or customer-health context that materially changes deal strategy.
- If CRM is unavailable but the user has provided sufficient deal context, continue and record the CRM gap in coverage.

### 3) Pull evidence lanes

Start from account identity and the selected opportunity or deal motion when available. For each enabled lane, proactively search or fetch relevant artifacts inside the requested time window. Treat user-provided links and notes as accelerators, not prerequisites.

Expected lane behavior:

- `crm` establishes deal truth and commercial context when available.
- Recent account activity or customer-health context can sharpen blockers, urgency, and risk when directly relevant to the active deal.
- `meeting_notes` contributes transcript-backed stakeholder language, objections, and commitments.
- `external_messaging` contributes customer-facing thread progression, approvals, and procurement/legal motion.
- `internal_messaging` contributes internal blockers, owner alignment, and execution risk.
- `document_store` contributes account plans, MAP artifacts, and strategy docs.
- `calendar` contributes near-term milestones and decision forums.
- User-provided enrichment exports, public research, or market intelligence can add optional structured commercial context.

Discovery requirements:

- Do not require the user to provide transcript links, thread links, or document links upfront.
- Use the account plus selected opportunity, product, solution, or initiative aliases to discover relevant artifacts in `meeting_notes`, `external_messaging`, `internal_messaging`, `document_store`, and `calendar` for the selected time window when sources are available.
- If the first same-account artifact is about a different opportunity, do not use it as deal-plan evidence. Continue with the next targeted result when available; otherwise continue with a clear source gap or ask the user to choose among concrete candidates.
- If a lane is unavailable or returns nothing relevant, continue and record the lane as unavailable, empty, or unverified in coverage.
- Do not chase indirect, mirrored, or convoluted paths to reconstruct unavailable source truth.

### 4) Build the deal map

Produce a concise map with:

- business initiative and target outcome
- current stage and timeline posture
- key active workstreams
- recent account or service context that materially changes deal execution, when evidenced
- top blockers and dependencies

Every material claim must be source-backed or explicitly labeled `Inference:`.

### 5) Build the buying committee map

For each material stakeholder, capture:

- person, title, and org area
- role in deal (`economic_buyer`, `decision_maker`, `champion`, `influencer`, `blocker`, `procurement`, `legal`, `security`, `unknown`)
- stance (`supportive`, `neutral`, `skeptical`, `blocking`, `unknown`)
- influence (`high`, `medium`, `low`, `unknown`)
- confidence (`high`, `medium`, `low`) with source evidence

If role or stance is inferred rather than directly stated, label it `Inference:`.

### 6) Build procurement risk register

Cover at minimum:

- risk summary
- risk type
- severity and likelihood
- source evidence
- owner
- mitigation step
- target date or `TBD`

Use [references/risk-rubric.md](references/risk-rubric.md) when risk classification, severity/likelihood, confidence, prioritization, or mitigation fields are ambiguous.

Owner and timeline precision rules:

- Use `Owner:` only when ownership is explicitly supported by evidence.
- If customer-side ownership is inferred or unconfirmed, label it `Suggested owner:`.
- Use exact calendar dates only when tied to explicit evidence such as a calendar event, stated deadline, or documented commitment.
- If no explicit date exists, use relative timing (`this week`, `next week`, `this month`) or `TBD`.

### 7) Generate prioritized next actions

Create actions that are concrete and owner-bound.

Each action must include:

- action statement
- owner
- due date or `TBD`
- expected outcome
- linked stakeholder(s) and/or linked risk(s)
- source reference

Owner and due-date precision rules:

- For customer-side actions without explicit ownership confirmation, use `Suggested owner:` instead of asserting ownership.
- Prefer relative due windows over exact dates unless there is direct date evidence.
- Avoid exact-day precision when confidence is `low` or when evidence is sparse.

Prefer 5 to 7 high-signal actions by default. Prefer fewer strong actions over broad advice.

### 8) Optional public or user-provided market context

Treat public research or user-provided market intelligence as optional context, not a hard dependency or assumed source category.

When available and useful, use it to:

- enrich company firmographics and context
- validate or refine stakeholder hypotheses
- add external context that sharpens committee mapping

If unavailable, continue with internal evidence, user-provided context, or both, and keep confidence explicit.

### 9) Cite and separate evidence from inference

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

Do not link to meeting join URLs, generic room links, or opaque connector refetch IDs.

## Output Shapes

Use human-readable labels in Title Case for normal output. Use `snake_case` keys only when the user explicitly asks for JSON, YAML, or machine-readable output.

Return sections in this exact order for a full strategy pack:

1. `Deal Snapshot`
2. `Deal Map`
3. `Buying Committee Map`
4. `Procurement Risk Register`
5. `Prioritized Next Actions`
6. `Evidence Gaps`
7. `Inference Notes`

For partial modes, return only the requested artifact plus `Evidence Gaps`, `Inference Notes`, and `Sources` when useful.

### Deal Snapshot

Include:

- Account
- Opportunity
- Stage
- Close Date
- Time Window
- Run Mode
- Coverage Summary, including which source lanes were available, unavailable, empty, or user-provided-only

### Deal Map

Keep this compact and execution-oriented:

- Initiative
- Target Outcome
- Current Motion
- Active Workstreams, 3 to 6 bullets
- Top Blockers or Dependencies, up to 5 bullets

### Buying Committee Map

Return a table with these columns:

- Stakeholder
- Title
- Org
- Role
- Stance
- Influence
- Last Signal
- Confidence
- Source

### Procurement Risk Register

Return a table with these columns:

- Risk ID
- Risk Summary
- Risk Type
- Severity
- Likelihood
- Owner or Suggested Owner
- Mitigation
- Target Date
- Confidence
- Source

### Prioritized Next Actions

Return a numbered list. Each action must include:

- Action
- Owner or Suggested Owner
- Due
- Linked Risk IDs
- Linked Stakeholders
- Expected Outcome
- Source

### Evidence Gaps

List only material gaps that lower confidence or block execution:

- Gap
- Impact
- Smallest Next Collection Step

### Inference Notes

List only claims that were inferred rather than directly stated. Prefix each with `Inference:`.

## Rules

- Do not fabricate stakeholders, approvals, blockers, owners, commitments, amounts, stages, close dates, or exact dates.
- Keep `crm` truth authoritative for opportunity metadata when available.
- Use supporting lanes to sharpen risk and action decisions, not to override authoritative CRM facts.
- Keep facts and inference separate.
- If evidence is conflicting, lower confidence and add an evidence gap.
- If discovery yields sparse evidence, continue with a low-confidence output and explicit evidence gaps when the account/deal anchor is sufficient.
- Use human-readable labels in Title Case in normal output.
- Keep this skill read-only unless the user explicitly asks for write actions in downstream systems.
