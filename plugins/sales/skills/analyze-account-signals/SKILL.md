---
name: analyze-account-signals
description: Analyze fresh signals for a named account, owner portfolio, or watchlist and turn them into evidence-backed account intelligence using active Sales source categories and user-provided context.
---

# Analyze Account Signals

Use this skill for account intelligence workflows that need either:

- `adhoc` single-account signal analysis
- `monitor` owner-portfolio or watchlist signal analysis

This skill turns fresh account evidence into a concise view of what changed, why it matters, and what to do next. The initial signal analysis is stateless and read-only: it can run directly from a user prompt or by an external automation, but the skill itself does not own standing monitoring state or recurring digests. After a reviewed signal action exists, it may offer supported posting, sharing, saving, or CRM writeback only after explicit user approval of that reviewed action.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the signal brief or monitor summary.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided or explicitly inferable context to identify one account, account owner, owner portfolio, watchlist, territory, or provided signal set. Source access can suggest concrete candidates, enrich, or verify the information, but do not draft the full signal output until the account or monitor scope is selected, clearly inferable, or sufficiently supplied by the user.

The skill can still produce a limited signal brief or watchlist summary from pasted notes, uploaded/exported context, or user-linked context alone when that context is sufficient. Connectors add significant value and reduce the burden on the user, but do not stop solely because connectors are unavailable.

**Inputs:**

- [required for `Adhoc Account Brief`] One target account by company name, CRM account id, or sufficiently detailed user-provided account context
- [required for `Monitor Summary`] Watchlist accounts, owner id/email, territory, portfolio, or sufficiently detailed user-provided account list
- Time window, defaulting to `14d`
- Focus areas when provided, such as expansion, churn, rollout blockers, or stakeholder movement
- Output style, defaulting to `brief` for adhoc and `inbox_summary` for monitor

Supported modes:

- `Adhoc Account Brief`: use for prompts like `give me an account view on Stripe`, `account intelligence for Datadog`, or `what changed with Snowflake`.
- `Monitor Summary`: use for prompts like `monitor my accounts`, `daily account watchlist`, or `which accounts need attention today`.

If the user does not explicitly provide mode, infer `Monitor Summary` for owner-, watchlist-, portfolio-, territory-, or daily-monitor phrasing. Otherwise default to `Adhoc Account Brief`.

Use [references/request-schema.yaml](references/request-schema.yaml) when structured input validation, YAML normalization, or machine-readable field shape matters. Structured input wins over conflicting prompt wording. Preserve `sfdc_account_id` as a legacy alias for `crm_account_id`.

If required inputs remain missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. First attempt a bounded candidate pass through the source category that owns the missing anchor. Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. For account selection, start with `crm` when available, then use user-provided context, `calendar`, `meeting_notes`, `document_store`, `external_messaging`, `internal_messaging`, or saved book-of-business context as supporting evidence only when that fits the budget. Before asking the user to paste an account list, name an account, or manually define a watchlist, either offer concrete candidates from those source categories or say which attempted categories were unavailable or empty. Ask one friendly clarification only after that pass. Ask only for unresolved inputs; for each question, include up to 5 concrete lettered options from source-backed or user-provided candidates when available. If no concrete candidates are available, briefly say why and ask free-form.

**Input Request Format Example:**

```md
Which account, owner portfolio, or watchlist should I analyze?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

If the user says `okay` from guided exploration without naming an anchor, pick a suitable account from Sales context instead of skipping. Prefer a recent, important-looking, or high-signal account from CRM, calendar, recent calls, saved book-of-business context, or the current thread. If no suitable account, owner portfolio, or watchlist is visible, ask one concise clarification.

Stop the workflow only when no account, owner portfolio, watchlist, territory, or sufficiently detailed user-provided signal set can be identified, or when a monitor scope is too broad to bound safely and cannot be narrowed by user input or source-backed candidate selection.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: default company-name-to-account resolver when available; authoritative account, opportunity, ownership, recent activity, customer-health, support, and account-status fields.
- `document_store`: account plans, account notes, briefs, prior account context, implementation docs, and artifacts that explain what changed or what workstream is active.
- `meeting_notes`: recent customer-call evidence, customer language, commitments, objections, decisions, follow-ups, and stakeholder movement.
- `external_messaging`: customer-facing thread progression, unanswered asks, rollout chatter, tone shifts, attachments, and promised next steps.
- `internal_messaging`: internal coordination, follow-up, stakeholder alignment, blocker context, and escalation signals.
- `calendar`: recent or upcoming customer sessions, near-term commitments, external meetings, and monitor scope reduction for overly broad portfolios.
- user-provided context: pasted notes, uploads, exports, account lists, CRM snippets, call notes, docs, and linked context that can serve as working evidence.

These are semantic source categories, not fixed connector names. Resolve each attempted source to the specific available app, connector, or helper skill through Sales preflight `context.sources` before using connector-specific logic.

Source obligations by intent:

- For `latest`, `what changed`, account-monitoring, or watchlist prompts, use `crm` or sufficient user-provided/exported account truth as the account anchor, then check at least one recency source when available: `meeting_notes`, `calendar`, `external_messaging`, or recent account documents.
- For `Adhoc Account Brief`, `crm` is required when CRM is available and an account anchor is supplied, inferred, or confirmed. Use CRM as the account resolver and source of account/opportunity truth. If `crm` is unavailable but manual account context is sufficient, continue with a limitation; if both are missing, stop.
- For `Monitor Summary`, keep the account universe bounded by the provided watchlist, owner, territory, portfolio, or resolved `crm` scope before enrichment. Do not broaden to arbitrary accounts unless the user asks or the first pass is empty and the user confirms a broader scope.
- If a recency source is checked and has no relevant result, say `checked/no match` in source notes or evidence gaps when that absence materially affects confidence. Do not imply fresh customer evidence exists when only CRM current-state fields were available.

Authority and gaps:

- Treat recent `crm` account activity, user-provided context, and supporting communication sources as the recency anchor on every run.
- Treat `crm` as the system of record for account and opportunity fields when available.
- Treat `meeting_notes`, `calendar`, `external_messaging`, `internal_messaging`, and `document_store` as recency or explanation sources, not replacements for CRM-owned account, opportunity, owner, stage, amount, close-date, or commercial-posture truth.
- Do not let document, messaging, public, or third-party enrichment context override CRM-owned account truth.
- Treat `document_store` and communication sources as supporting context for what changed, what is active, and what needs attention soon.
- Treat user-provided notes, uploads, exports, and linked context as valid working evidence; label limitations when they cannot be verified against connector sources.
- If `crm` and manual account context are both unavailable for a target account, say the recency anchor is unavailable and do not pretend the result is current.
- If optional sources fail, continue with the strongest available evidence and explicitly note material evidence gaps.
- Do not use public web research, external news search, external enrichment, or task trackers in v1 unless the user explicitly extends the workflow and provides the source, export, or matching connector.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the analyze-account-signals experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Analyze Account Signals
This skill helps turn fresh customer, account, product, market, meeting, email, CRM, and internal-message signals into a concise view of what changed and what to do next.

```

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Analyze Account Signals next-step behavior and action text. Onboarding, draft creation, CRM writeback, posting or sharing, tracker creation, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the account-signal continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `analyze-account-signals` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/writing/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the signal brief** | The first substantive account-signal brief has just been produced. | `Anything you'd change in the signal brief before we act on it?` |
| **2. Review the revised signal brief** | The user asked for any change to signal selection, priority, interpretation, confidence, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to draft a seller follow-up, account-team update, escalation note, CRM note, or tracker?` |
| **3. Prepare the signal action** | The user accepts the brief, says no changes are needed, says a revision looks good, or asks to operationalize the signal. | Offer to produce the most useful next artifact or draft action, prioritizing seller follow-up, account-team update, escalation note, CRM-ready note, or tracker over broad suggestions. |
| **4. Review the artifact or draft** | A follow-up, account-team update, escalation note, CRM-ready note, or tracker exists, or the user asks to change it. | `Anything you'd change before I save, post, share, or write this where it belongs?` |
| **5. Post, share, save, or write approved signal action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as posting the account-team update, sharing the escalation note, saving the tracker, or writing the approved CRM note. Do not post, send, or write CRM changes unless the user explicitly asks for that action or approves the reviewed draft/update. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the signal brief, treat a lightweight acknowledgement as acceptance and move to `Prepare the signal action`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post, send, or write externally. If the previous continuation offered to post, share, save, or write a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Procedure

### 1) Normalize the request

Normalize the prompt, pasted YAML, or attached YAML using the input model.

Rules:

- Use explicit fields from structured input when present.
- If both `company_name` and `crm_account_id` are present, trust the account id.
- Accept `sfdc_account_id` as a legacy alias for `crm_account_id`.
- If both `watchlist_accounts` and `owner_id`/`owner_email` are present in monitor mode, use the watchlist and skip owner lookup.
- Accept `watchlist_accounts` as a list of names, ids, or mixed entries.
- Preserve user-provided `focus_areas`.

### 2) Select the account scope

For `Adhoc Account Brief`, operate on exactly one account.

For `Monitor Summary`:

- Use `watchlist_accounts` as the full scope when present and non-empty.
- Otherwise select the available `crm` connector, apply any relevant helper skills returned for that source category, discover the provider's owner/account fields or filters, and query accounts owned by the requested seller or owner with a bounded result set.
- Keep the first pass primary-owner scoped; paginate only while the provider indicates more results and until `50` accounts are collected.
- If the primary-owner lookup returns zero accounts and the user explicitly asked for account-team, territory, role, collaborator, or go-to-market-linked coverage, retry once with the selected `crm` connector's supported filters and the same cap.
- If the broader retry times out or fails, continue with primary-owner results when present; otherwise stop and ask for a watchlist or narrower owner scope.
- If the resulting scope has more than `50` accounts, use `calendar` to find upcoming external customer meetings in the next `14` days and reduce to at most `50` meeting-linked accounts.
- If the scope is larger than `50` and `calendar` is unavailable or yields no upcoming meeting-linked accounts, stop and ask for a watchlist or narrower scope instead of picking an arbitrary slice.
- Resolve each final account individually and collect bounded recent evidence.
- If parallel execution is available, run up to `10` independent single-account evidence lookups in parallel. Otherwise process sequentially with the same per-account shape.

### 3) Resolve account identity

Resolution order for each account:

1. Provided `crm_account_id`
2. `crm` account resolver when available
3. User-provided domain, account notes, or `document_store` account-plan context as a tie-breaker when `crm` resolution is ambiguous, low-confidence, or inconsistent with the requested company

Rules:

- Do not trust the top ranked resolver result blindly when there are multiple plausible matches.
- Prefer exact company-name or domain-aligned matches.
- Note ambiguity handling in the final output when it affects confidence.

### 4) Collect primary evidence

Always collect, when available:

- `crm` account, opportunity, ownership, recent activity, and open customer-health or support signals
- user-provided account context
- `document_store` account plans, account notes, briefs, or prior context

For monitor mode:

- Apply the same bounded evidence pass once per selected account.
- Prefer exact account id lookups and parallelize only across independent single-account calls.
- Treat a timeout or schema error on a multi-account request shape as a call-shape failure, not as proof that `crm` or `document_store` is broadly unavailable.
- Retry only failed accounts once, preferring exact `account_id`.
- If a specific account still fails after the retry, mark it as `primary_evidence=unavailable` and continue with surviving accounts.
- Do not deepen every account with heavier sources before the per-account primary evidence pass completes.

Deepen with `document_store`, `meeting_notes`, `external_messaging`, or `internal_messaging` when:

- the run is adhoc;
- primary evidence is too thin to support interpretation;
- identity resolution required notes or communications context.

### 5) Collect supporting evidence

Use supporting sources only to strengthen, corroborate, or refine the account story. Do not let weaker sources override stronger account truth.

Supporting source order:

1. `external_messaging`
2. `document_store`
3. `meeting_notes`
4. `internal_messaging`
5. `calendar`

For portfolios larger than `50`, `calendar` moves earlier and acts as the required scope-reduction source before enrichment begins.

Use supporting sources for corroboration, richer context, stakeholder movement, blocker details, and near-term commitments. Do not use supporting sources for overriding clear CRM account or opportunity truth, inventing account metrics, or replacing account resolution logic.

### 6) Normalize signals

Convert collected evidence into the fixed signal taxonomy. Use only these default signal types unless the skill is explicitly extended later:

- `momentum`
- `expansion_opportunity`
- `churn/risk`
- `blocker/dependency`
- `stakeholder_movement`
- `upcoming_commitment_or_deadline`
- `evidence_gap`

For each signal, preserve:

- `signal_type`
- `summary`
- `source`
- `recency`
- `confidence`
- `evidence`
- `citation`
- `recommended_next_step`

Use [references/signal-taxonomy.md](references/signal-taxonomy.md) when signal classification, confidence, recency, monitor ranking, delta classification, or user-facing label mapping is ambiguous.

Rules:

- Multiple pieces of corroborating evidence may support one signal.
- Do not create duplicate signals when several sources describe the same event.
- If evidence is weak, stale, or contradictory, lower confidence and add an evidence-gap note.
- Distinguish actionable account risks from hygiene-style context such as ownership gaps, missing routing fields, or ambiguous associations; surface the latter only when they affect monitoring confidence or the recommended next step.
- Preserve source identifiers internally, but prefer user-actionable links in the final output over raw ids.

### 7) Score and rank

For adhoc mode:

- Do not rank the account against others.
- Sort signals by importance to the account story: risk/opportunity first, then dependencies, then supporting context.

For monitor mode:

- Rank accounts by fresh, high-confidence, action-relevant change.
- Prioritize accounts with strong `churn/risk` or `expansion_opportunity` signals.
- Rank corroborated multi-source signals above single-source weak signals.
- Down-rank stale or speculative signals.
- Omit or compress accounts with no material delta.
- When monitor scope was filtered by upcoming meetings, rank within that filtered set only.
- Assign an attention score (`high`, `medium`, or `low`) per ranked account.
- Assign a directional posture per ranked account: `expansion_ready`, `expansion_blocked`, `retention_risk`, or `execution_risk`.
- Classify each material signal change as `new`, `updated`, `worsened`, `resolved`, or `unchanged`.

### 8) Cite and separate evidence from inference

Keep raw evidence separate from interpretation. Every recommendation must be traceable to explicit evidence and, when the source exposes a usable URL, a clickable citation.

Citation rules:

- When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL.
- In `Account Snapshot` and `Ranked Accounts Requiring Attention`, render the company name as a Markdown link to the resolved CRM account when a link can be built.
- For CRM evidence, prefer connector-provided record URLs. If only a CRM record id is available, construct a record URL only when trusted connector metadata exposes the CRM instance base URL; otherwise use the record name and object label without inventing a URL.
- For Google Docs, Drive files, Slack messages, calendar events, meeting notes, or files, use connector-provided document URLs, file URLs, permalinks, event links, or meeting links when available.
- Put citations close to the claim they support.
- If a source has no usable URL, use a plain-language provenance label such as `CRM activity`, `Drive account plan`, or `Slack search result`; do not expose a naked id unless the user asks for ids or ambiguity requires it.

## Output Shapes

Use concise Markdown headings and bullets. Use plain-English labels instead of raw enum tokens in user-facing output. Internal enum tokens may be preserved for machine parsing, but they should not be the primary displayed label.

### Adhoc Account Brief

Return these sections in order:

1. `Account Snapshot`
2. `Key Recent Signals`
3. `Strategic Interpretation`
4. `Recommended Actions`
5. `Open Questions / Missing Evidence`

`Account Snapshot` includes the linked account name when available, time window used, and one or two lines on current account posture.

`Key Recent Signals` lists normalized signals ordered by importance. Each signal should state what changed, sources, citation links when available, recency, and confidence.

`Strategic Interpretation` explains what the signals likely mean for land, expand, retention, or execution risk, making high-confidence conclusions distinct from tentative conclusions.

`Recommended Actions` is a short, prioritized action list. Each action must cite the signal or evidence it is based on.

`Open Questions / Missing Evidence` lists unresolved unknowns, missing sources, and the follow-up evidence that would reduce uncertainty.

### Monitor Summary

Return these sections in order:

1. `Ranked Accounts Requiring Attention`
2. `Material Deltas`
3. `Run Metadata`
4. `No Major Delta`, optional

For each ranked account, include:

- linked account name when a CRM record link is available
- what changed
- why it matters
- recommended next step
- confidence / evidence note
- attention score (`high`, `medium`, or `low`)
- directional posture (`expansion_ready`, `expansion_blocked`, `retention_risk`, or `execution_risk`)

For `Material Deltas`, include only material changes from the selected time window. Each row or bullet must include date, signal, status, delta summary, impact, next step, and confidence.

For `Run Metadata`, include time window used, data freshness cutoff, account scope size, accounts checked, accounts ranked, and a concise `delta_since_last_run` note when prior-run context is provided by the caller.

Use these user-facing labels in monitor output:

- `momentum` -> `Momentum`
- `expansion_opportunity` -> `Expansion opportunity`
- `churn/risk` -> `Churn or retention risk`
- `blocker/dependency` -> `Blocker or dependency`
- `stakeholder_movement` -> `Stakeholder movement`
- `upcoming_commitment_or_deadline` -> `Milestone or deadline`
- `evidence_gap` -> `Evidence gap`
- `new` -> `New this period`
- `updated` -> `Updated this period`
- `worsened` -> `Worsened this period`
- `resolved` -> `Resolved this period`
- `unchanged` -> `No change this period`

## Fallback Behavior

- If account resolution fails, stop that account and say what identifier is missing or ambiguous.
- If `crm` and manual account context are both unavailable for a target account, say the recency anchor is unavailable and do not pretend the result is current.
- If optional sources fail, continue with the strongest available evidence and explicitly note any material evidence gaps.
- If a monitor scope is larger than `50` and `calendar` cannot reduce it to meeting-linked accounts, stop and ask for a watchlist or narrower scope.
- If a monitor run returns no accounts with a material delta, return a concise summary saying no accounts currently require prioritization based on the available evidence.

## Rules

- Keep evidence and interpretation visibly separate.
- Every recommendation must be traceable to evidence.
- Degrade cleanly when optional connectors are unavailable.
- Do not use public web research or news enrichment in v1 unless the user explicitly asks for it.
- Do not create task issues, `internal_messaging` posts, `crm` updates, or other writebacks in v1.
- Do not present raw CRM ids as the main user-facing way to act on an account.
- Do not imply certainty that the sources do not support.
- Rewrite unsupported claims as questions, risks, or evidence gaps instead of assertions.
- Do not expose internal tool names in user-facing prose unless the user is explicitly asking about the workflow itself.
