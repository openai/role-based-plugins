---
name: prioritize-accounts
description: Prioritize rep-ready pipeline by ranking accounts, suppressing in-flight motion, selecting the best reachable contact, and producing a connector-grounded account action view plus a concise planning-only action package from CRM, user-provided lists, saved context, and optional enrichment evidence.
---

# Prioritize Accounts

Use this skill to help an individual sales rep decide which accounts to work now, why now, and what to do next.

This is a rep-facing, account-first workflow. It prioritizes accounts before contacts, branches clearly across `net_new`, `expansion`, or `mixed`, suppresses accounts already in motion, and returns a small set of executable Suggested Focus rows. Its primary output is a connector-grounded account action view that can be opened in Codex when connected source records or useful source links are available. It plans and drafts only: it does not execute outreach, create records, update CRM, or send messages unless the user explicitly asks for that in a separate step.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the account-prioritization output also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the prioritization.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided, connector-visible, or explicitly inferable context to identify the account universe and the ranking basis.

The skill can still produce a limited ranking from pasted account lists, CRM exports, uploaded enrichment tables, saved book-of-business context, or user-provided ICP notes when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] `account_set`: candidate accounts, owner scope, territory, ICP, segment, pipeline view, or other account universe to prioritize
- [required] `ranking_basis`: what "best" means for this run, such as deal value, likelihood to close soon, product or usage signal, expansion potential, named-account priority, or mixed rep actionability

Accept when provided:

- `motion_goal`: `net_new`, `expansion`, or `mixed`; default `mixed`
- `batch_size`; default `5`
- `capacity_window`; default to `batch_size`
- `signal_preference`
- `product_focus`
- `exclude_accounts`
- `uploaded_examples`

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible account-set or account-list anchors unless the request clearly asks for external discovery only. When `crm` is available, include a bounded CRM lookup to resolve account identity, ownership, customer status, or candidate-list scope; this does not replace confirmation of `account_set` and `ranking_basis` for broad "best accounts" prompts.
- Before asking the user to paste an account list, CRM export, ICP, or ranking basis, first try the source categories that can resolve the missing account universe or source-scope default: `crm` for account truth, owner scope, open opportunities, and CRM-backed lists; `document_store` for territory, ICP, named-account, and prioritization guidance; and `calendar`, `meeting_notes`, `external_messaging`, or `internal_messaging` only when they can cheaply produce concrete suppression or active-motion candidates. Manual/exported lists are the fallback after those categories are unavailable, empty, or insufficient.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

Proceed with assumptions only when the prompt or saved Sales context clearly resolves account set, ranking basis, and source scope. In that case, state assumptions in `Scope` instead of blocking.

### Input Parameter Confirmation

Use when the user's request is ambiguous or underspecified enough that materially different prioritize-account runs are plausible.

Hard gate: if the request uses broad ranking language such as "best accounts", "top accounts", "go after", "prioritize", "who should I work", or "next accounts" and the prompt or saved Sales context does not resolve both account set and ranking basis, ask confirmation questions before searching connectors, reading sources, or drafting an answer.

Do not treat connector/source availability, including Salesforce availability, as enough to skip confirmation. Source availability may set the default for the source-scope question, but it does not answer what "best" means or which account universe the user wants.

When clarification is needed, ask at most three high-impact, high-uncertainty questions. Prefer defaults from saved Sales context and explicit prompt clues. Use connected-source availability only for the source-scope default.

When asking, use this lead-in:

```md
Before I dig in, a couple of quick questions so I find the right "best" for you.
```

Parameters to confirm:

| Parameter | Ask When | Question | Default | Options | Affects |
| --- | --- | --- | --- | --- | --- |
| Account set | User asks for "best accounts", "top accounts", "who should I work", or "go after" without a candidate list, territory, ICP, owner scope, or pipeline scope | What kind of accounts should I surface? | Open pipeline deals | Open pipeline deals; Existing customers for expansion; Net-new target accounts | Candidate sourcing, branch selection, and suppression |
| Ranking basis | User says "best", "top", "right", or similar without defining the success criterion | What signals should weigh most heavily? | Deal value / ACV | Deal value / ACV; Likelihood to close soon; Product or usage signal | Ranking posture and why-now evidence |
| Source of truth | Multiple plausible source paths exist and no saved or prompt-explicit source is clear | Where should I pull data from? | Saved CRM preference if available; otherwise Salesforce/CRM when available; otherwise uploaded/exported list or manual context | Salesforce/CRM; Uploaded or exported list; CRM plus recent meetings and notes | Source selection, confidence, and evidence gaps |

Render questions as concise Markdown:

```md
Before I dig in, a couple of quick questions so I find the right "best" for you.

1. **What kind of accounts should I surface?**
   Default: Open pipeline deals

2. **What signals should weigh most heavily?**
   Default: Deal value / ACV

3. **Where should I pull data from?**
   Default: Salesforce/CRM
```

If the compact first-run intro is rendered, show input parameter confirmation immediately after the intro. Suppress any extra skill-owned final continuation when the clarification questions are already the next step.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: account truth, owner scope, territory or book, customer status, open opportunities, stage, amount, forecast posture, recent activity, contacts, account hierarchy, suppression signals, and CRM-backed account lists.
- `calendar`: recent or upcoming external meetings that suppress, down-rank, or explain active motion.
- `meeting_notes`: recent customer-call context, objections, decision process, urgency, stakeholder coverage, and continuity signals that materially change ranking or next action.
- `document_store`: account plans, territory docs, named-account lists, ICP guidance, sales plays, saved team priorities, or source-of-truth ranking/suppression conventions.
- `data_enrichment`: account fit, contact availability, tech stack, funding, hiring, and other account trigger context when CRM or user-provided truth is thin.
- `external_messaging`: recent customer engagement, timing, objections, stakeholder continuity, or duplicate-motion signals.
- `internal_messaging`: active seller/team motion, internal blockers, owner ambiguity, deal-desk or account-team signals, and suppression evidence when the user wants internal context.
- user-provided context: pasted account lists, CRM exports, enrichment tables, ICP notes, named-account lists, prior Sales outputs, examples, and explicit ranking criteria.

Source obligations by intent:

- `crm` or sufficient user-provided/exported account truth is required for the candidate account universe. If neither exists, stop and ask for a CRM scope, exported list, territory, ICP, or account list.
- Use `data_enrichment` only after the account universe or ICP is anchored. It can improve fit, contactability, and why-now context, but it must not create the candidate universe by itself or overwrite CRM/user-provided account truth.
- Use `calendar`, `meeting_notes`, `external_messaging`, or `internal_messaging` only when they materially affect suppression, active-motion detection, timing, contact choice, or sequence angle. If checked and no relevant suppression or why-now evidence appears, note the no-match only when it affects confidence.
- For "best/top N accounts" prompts, return the requested number of Suggested Focus rows whenever the confirmed candidate universe contains enough viable accounts. Use `Low` confidence or `partial` status for weaker but still actionable rows; return fewer than N only when fewer viable candidates remain after suppression/blocking, and say why.

Authority and gaps:

- Prefer `crm` truth and existing internal motion before enrichment or drafting.
- Prefer known account context before generic web-style personalization.
- Treat `calendar`, `meeting_notes`, `external_messaging`, and `internal_messaging` as timing, suppression, and why-now signals; do not use them to create the candidate account universe or overwrite CRM/user-provided account truth.
- Do not let public research, enrichment exports, docs, messages, or inferred personalization override CRM-owned account truth.
- Use public research, enrichment exports, or user-provided market intelligence only to fill account coverage gaps when CRM or user-provided account truth is thin.
- Do not use lower-confidence lanes to overwrite stronger `crm` or user-provided truth.
- If no account truth is available from `crm`, user-provided inputs, or `document_store`, stop and explain the blocker briefly.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the prioritize-accounts experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Prioritize Accounts
This skill helps decide which accounts to work now and why. It can use account lists, territories, CRM, firmographic/enrichment context, calendar, recent engagement, pipeline data, saved ICP guidance, and user-provided priorities. It produces a source-grounded account action view plus a ranked account list with reasons, confidence, suppressions, key contacts or gaps, and recommended next actions.

Definitions:
- ICP: ideal customer profile, the criteria that define what a strong-fit account looks like for the sales motion.
- Suppression: a reason to deprioritize or exclude an account for now, such as active motion, unclear ownership, or unsafe duplicate outreach.

```

Starter prompts:

- Primary default prompt: `Prioritize accounts for pipeline focus.`
- `@Sales prioritize these target accounts for pipeline focus this week.`
- `@Sales rank my territory accounts by where I should spend time next.`
- `@Sales use this ICP and account list to pick the best ten outreach targets.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Prioritize Accounts next-step behavior and action text. Onboarding, spreadsheet creation, draft creation, CRM writeback, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the account-prioritization continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `prioritize-accounts` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/writing/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the account ranking** | The first substantive ranking or Suggested Focus list has just been produced. | `Anything you'd change in the ranking, suppression rules, or Suggested Focus list before we act on it?` |
| **2. Review the revised ranking** | The user asked for any change to criteria, suppression rules, rows, contact choices, scoring, source weighting, or formatting. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to turn the accepted ranking into outreach drafts, CRM next actions, an owner tracker, or a spreadsheet?` |
| **3. Prepare the activation artifact** | The user accepts the ranking, says no changes are needed, says a revision looks good, or asks to operationalize the list. | Offer to produce the most useful next artifact or draft action, prioritizing outreach drafts, CRM next actions, an owner/action tracker, contact-selection guidance, or a spreadsheet over broad suggestions. |
| **4. Review the artifact or draft** | Outreach drafts, CRM-ready actions, a tracker, contact-selection guide, or spreadsheet exists, or the user asks to change it. | `Anything you'd change before I save, share, or write the approved account actions?` |
| **5. Save, share, or write approved account action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the spreadsheet, sharing the owner tracker, creating reviewed outreach drafts, or writing approved CRM next actions. Do not post, send, or write CRM changes unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the ranking, treat a lightweight acknowledgement as acceptance and move to `Prepare the activation artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post, send, or write externally. If the previous continuation offered to save, share, or write a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

### Account Action View Output

For every substantive ranking run with CRM, another valuable searchable connected source, or stable source-of-truth links in the row payload, make the account action view the primary output. Use the bundled template:

`assets/account-priority-pane.template.html`

The template is standalone UTF-8 HTML with inline CSS and browser JavaScript only. It has no external assets, no script imports, no npm dependencies, no Node dependency, and no helper scripts.

Generate one local file in an OS-appropriate temporary directory:

- macOS/Linux: `${TMPDIR:-/tmp}/prioritize-accounts/index.html`
- Windows: `%TEMP%\prioritize-accounts\index.html`

Return the actual clickable view link first in the final response. Do not hardcode macOS-only `/private/tmp` in Windows-facing output. URL-encode spaces if emitting a `file://` URL.

In user-facing copy, call the output an account action view, account ranking, or priority view. Do not mention templates, JSON, placeholders, Markdown, local files, or HTML mechanics unless the user explicitly asks how the view is built.

Do not generate the account action view when no CRM search, connected source search, or useful stable source links are available for the run. In that case, render the structured ranking directly in chat and say the account action view was skipped because there were no searchable source records or source-of-truth links for the view to open. A purely pasted, unlinked account list can still produce a ranking, but it should not create a local HTML view unless the pasted/exported data includes useful source links or the user explicitly asks for an offline view.

View generation procedure:

1. Build the account action package using the `Suggested Focus`, `Monitor`, `Suppress Or Block`, `Evidence Gaps`, and `Source & Run Details` contracts below. Serialize Suggested Focus rows under the existing `workNow` payload key for template compatibility.
2. Serialize the same package as JSON using the payload shape below.
3. Escape the JSON for safe embedding in a script tag by replacing every `<` with `\u003c`.
4. Replace the exact template placeholder `__PRIORITIZE_ACCOUNTS_DATA_JSON__` with the escaped JSON.
5. Write the resulting HTML as UTF-8 to the local output path.
6. Sanity check that the generated file contains no unresolved placeholder.
7. Final response: put the file link first, then a short summary and the required natural continuation from `Next Step Guidance`.

Do not ask the user to run Node, npm, Python, Salesforce CLI, or any helper script. If local file links do not open in the client, start a tiny local HTTP server yourself only when necessary and return the localhost URL.

Preferred payload shape:

```json
{
  "title": "Prioritize Accounts",
  "generatedAt": "2026-05-29T19:30:00Z",
  "source": {
    "label": "Salesforce/CRM",
    "status": "Connected sources used"
  },
  "scope": {
    "accountSet": "Open pipeline deals",
    "rankingBasis": "Deal value / ACV",
    "sourceOfTruth": "Salesforce/CRM plus recent meetings",
    "sourceScope": "Salesforce/CRM plus recent meetings",
    "actionOwner": "Rep-owned next actions",
    "accountOwner": "Rep-owned next actions",
    "ownershipActionModel": "Rep-owned next actions",
    "motionGoal": "mixed",
    "batchSize": 5,
    "capacityWindow": 5,
    "sourcesChecked": ["crm", "calendar", "meeting_notes"],
    "evidenceLanes": ["crm", "calendar", "meeting_notes"],
    "assumptions": "Assumption-based only when applicable"
  },
  "workNow": [
    {
      "rank": 1,
      "account": "Acme Corporation",
      "accountUrl": "https://example.my.salesforce.com/001000000000000",
      "motion": "expansion",
      "whyNow": "Source-grounded timing reason.",
      "primaryContact": "Dana Price, VP Operations",
      "secondaryContact": "Lee Chen, Director Data Platform",
      "oppRecommendation": "work account before opp",
      "nextStep": "Confirm security reviewer and send pilot success criteria.",
      "sequenceAngle": "Pilot success criteria tied to expansion timeline.",
      "confidence": "High",
      "status": "ready_now"
    }
  ],
  "monitor": [
    {
      "account": "Beta Inc.",
      "accountUrl": "https://example.my.salesforce.com/001000000000001",
      "motion": "net_new",
      "reasonToMonitor": "Good fit, but no immediate trigger.",
      "triggerToRevisit": "New executive hire or product signal.",
      "status": "monitor"
    }
  ],
  "suppressOrBlock": [
    {
      "account": "Gamma LLC",
      "accountUrl": "https://example.my.salesforce.com/001000000000002",
      "motion": "expansion",
      "suppressorOrBlocker": "Recent external meeting already in motion.",
      "evidence": "CRM activity and calendar meeting.",
      "status": "suppressed"
    }
  ],
  "evidenceGaps": [
    "Missing direct contact path for some otherwise strong accounts."
  ]
}
```

The account action view intentionally mirrors the action-package components: `Suggested Focus`, `Monitor`, `Suppress Or Block`, `Evidence Gaps`, and `Source & Run Details`. Keep the view and any chat fallback semantically identical. If local file creation is impossible, or if no useful source search/linking is available, render the structured package directly and state why the account action view could not be created.

## Procedure

### 1. Normalize the rep request

- Resolve whether the user wants `net_new`, `expansion`, or `mixed`.
- Resolve whether the request is account-led, owner-led, territory-led, ICP-led, or pipeline-view-led.
- Set an execution cap from `capacity_window` or `batch_size`.
- Preserve any explicitly supplied candidate accounts as the top evaluation set.
- Use `references/request-schema.yaml` only when structured input validation, YAML normalization, or machine-readable field shape matters.
- If required inputs are missing or ambiguous, follow `Input Parameter Confirmation` instead of running a broad ranking.

### 2. Build the candidate account set

- Prefer user-supplied or owner-scoped account lists before discovery.
- Use `crm` as the default account truth source when available.
- If the default or assumed source returns no owned open pipeline, no matching account list, or no candidate set for the stated scope, stop before broadening the request. Briefly report the empty result and ask whether to broaden to recent account activity, expansion customers, net-new targets, or a user-provided account list or territory.
- Do not silently pivot from "best accounts to go after" to "accounts where the user can help or coordinate" unless the user chooses that broader action model.
- Fetch enough candidates before suppression to satisfy the requested cap when possible, but do not widen beyond the confirmed account set unless the first pass is empty, thin, or misleading.
- If the user requested an explicit count, preserve it as the target Suggested Focus row count throughout selection. Do not demote an otherwise viable Nth account to `Monitor` solely because confidence is lower; use confidence and status labels instead.

### 3. Branch and classify each account

- Classify each account as `net_new`, `expansion`, or `unknown_branch`.
- Prefer `crm`-backed evidence for customer status, current owner, open opportunities, recent or upcoming meetings, and current stage of any existing motion.
- Treat missing owner, weak account identity, or no usable contact path as execution blockers, not minor enrichment gaps.
- Do not blend `net_new` and `expansion` logic in the same row. Pick one branch and state it.
- If branch evidence is weak, mark the row `partial` or `blocked` instead of guessing.

### 4. Apply suppressors before drafting

Always suppress when strongly evidenced:

- active open opportunity;
- recent or upcoming external meeting already in motion;
- clearly active seller, SE, account-team, or internal team motion that would make new outreach duplicative;
- unresolved account ownership or contact-path ambiguity that makes immediate rep action unsafe to recommend.

Do not draft suppressed accounts unless the user explicitly asks to override suppression. Use `references/suppression-and-fallbacks.md` when suppression, blocking, monitoring, or fallback-lane behavior needs more detail than these rules.

### 5. Score for rep actionability

Rank accounts using explicit evidence, not opaque scoring. Prioritize:

- strongest `why_now`;
- reachable stakeholder path;
- clear branch fit;
- absence of suppressors;
- fit with the rep's capacity window.

Favor fewer, higher-confidence executable rows over broad list generation.

### 6. Select contacts and next action

- Resolve one primary contact per account row.
- Prefer `crm` contact truth first.
- If `crm` is thin, use user-provided contacts, `document_store` account context, public research, or user-provided market intelligence as fallback.
- Use `meeting_notes`, `external_messaging`, and `internal_messaging` only as corroboration or continuity lanes, not as the sole source of contact fit.
- Add a secondary contact only when it materially supports multithreading.
- Never fabricate a contact. If the path is weak, keep the row out of Suggested Focus.

### 7. Gather why-now and message-angle evidence

- Use `crm`, user-provided account context, and `document_store` first.
- Prefer known account context over generic personalization tactics.
- Use `calendar` to suppress or down-rank accounts with meetings already in flight.
- Use `external_messaging`, `internal_messaging`, and `meeting_notes` only when they materially change timing, urgency, contact choice, or the sequence angle.
- Keep sourced facts separate from inference.

### 8. Render the account action package

Build the account action package with these components:

1. `Suggested Focus`
2. `Monitor`
3. `Suppress Or Block`
4. `Evidence Gaps`
5. `Source & Run Details`

Put `Suggested Focus` first in the account action view. Sellers should see the priority accounts, why-now evidence, contacts, recommendations, and suggested next steps before run metadata. Put source of truth, sources checked, account set, ranking basis, counts, assumptions, and last-updated details at the bottom in `Source & Run Details`.

In `Source & Run Details`, name the resolved account set, ranking basis, source of truth, action owner, batch size or capacity window, and main sources checked. If the run used assumptions, label the result as assumption-based. If the source was broadened after a no-results guard, label it as partial rather than a definitive "best accounts" result.

In the account action view, Suggested Focus rows must show explicit priority order. Set `rank` to `1`, `2`, `3`, and so on in the serialized view payload, where `1` is the highest-priority account to work first. The chat fallback can rely on table order, but the view should display the priority number as plain text.

Use this exact Suggested Focus row schema for the account action view and for any chat fallback:

```md
| Account | Why Now | Primary Contact | Secondary Contact | Opp Recommendation | Suggested Next Step | Sequence Angle | Confidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Rules:

- Classify motion internally as `net_new` or `expansion`, but do not render Motion as a column in the account action view or chat fallback.
- Include `accountUrl` when a CRM, document, spreadsheet, or other source-of-truth record URL is available. In Salesforce, prefer the UI record URL for the Account. The account name renders as a clickable link when this field is populated.
- Use human-readable dates in all user-visible row text, for example `Jun 1` or `Jun 1, 2026` instead of `2026-06-01`. Machine fields such as `generatedAt` may remain ISO because the view formats them for display.
- `Why Now` must be source-grounded. If it is not well supported, the row should not be in Suggested Focus.
- `Secondary Contact` may be `None` when multithreading is not supported by evidence.
- `Opp Recommendation` should be concise and practical, for example `work account before opp`, `create opp after discovery`, or `expand existing motion later`.
- `Suggested Next Step` must be an immediate rep action and should be populated from `nextStep` or `suggestedNextStep` in the serialized payload. This is an assistant recommendation, not a CRM field value.
- `Sequence Angle` should summarize the outreach hook, not render a full sequence.
- `Confidence` should be a plain-language rating such as `High`, `Medium`, or `Low`.
- `Status` must be `ready_now` or `partial` in Suggested Focus; move `blocked` and `suppressed` rows to later sections.

Use this `Monitor` row schema:

```md
| Account | Reason To Monitor | Trigger To Revisit | Status |
| --- | --- | --- | --- |
```

Use this `Suppress Or Block` row schema:

```md
| Account | Suppressor Or Blocker | Evidence | Status |
| --- | --- | --- | --- |
```

Use `Evidence Gaps` for a flat list of the most important missing inputs, connector truth, or account gaps that limited the run.

After building these rows, fill `assets/account-priority-pane.template.html` using `Account Action View Output` only when useful source search/linking is available. The account action view is the primary presentation in that case. In the chat response, return the view link first and then a concise readout of the ranking, source of truth, and evidence gaps. Render the full chat tables only when the user asks for plain text, when no useful source search/linking is available, when local file creation is impossible, or when a parent flow explicitly requires chat-only output.

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Output Rules

- This is a prioritization and activation workflow, not a generic lead list.
- For substantive ranking runs, make the account action view the primary output and put its link first.
- Keep the account row as the primary unit of work.
- Prefer account-level prioritization over contact sprawl.
- Show evidence gaps that prevented action.
- Do not claim urgency, contact fit, or motion status without evidence.
- Do not fabricate contacts, urgency, opportunity posture, or account facts.
- Prefer smaller, more executable Suggested Focus output over larger noisy output.
- When the user requested a specific count, prefer exactly that many executable Suggested Focus rows over a smaller polished list unless suppression, blocking, or insufficient account truth leaves fewer viable candidates.
- If the user explicitly asks for email drafts in a separate execution step and a real draft is created or saved through `external_messaging`, include a clickable Markdown link to each created draft using the URL returned by the app. If only copy is drafted in chat, say no email draft was created.
