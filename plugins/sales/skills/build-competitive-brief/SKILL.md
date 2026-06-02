---
name: build-competitive-brief
description: Build a multi-competitor build-competitive-brief report, comparison matrix, and battlecard-style objection package using user-provided materials, optional connector-assisted research, and public evidence.
---

# Build Competitive Brief

## Overview

Produce a durable competitive brief for strategy, product marketing, enablement, or sales teams. Default to a concise evidence-backed brief that can support downstream messaging, account prep, and objection handling.

This workflow accepts manual materials, but it should use active source categories before asking for manual input. It must work with:

- a seller company, product scope, or workflow scope
- competitor names
- competitor discovery when the user does not name competitors
- user-provided notes, decks, or transcripts
- optional account context
- public web research

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

This skill needs enough user-provided, connector-visible, public, or explicitly inferable context to identify a competitor set, named account/deal with competitor context, or clear market category to compare.

The skill can still produce a limited competitive brief from pasted notes, uploaded/exported materials, prior battlecards, public evidence, or user-linked context when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require one anchor:

- [required] competitor names or a competitor set
- [required] named account/deal with competitor context
- [required] product, workflow, segment, or market category to compare

Accept when provided:

- seller company, account, product scope, buyer context, industry, region, customer segment, known objections, existing materials, output mode, and shareable artifact request

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- When an ambiguous company-like proper noun could be either a competitor or a customer/account, include a bounded CRM lookup when `crm` is available before drafting. If CRM returns a high-confidence customer/account match and the prompt did not clearly ask for that company as a competitor, treat it as account/deal context or ask the user to choose from concrete candidates.
- Before asking the user to paste battlecards, competitor lists, or account context, first try the source categories that can resolve the missing anchor: `crm` for account/deal context, `document_store` for competitive docs and prior briefs, and `internal_messaging` for field signals when the user wants internal context. Use public research for public competitor facts after the anchor is resolved or when no internal/account source can supply candidates.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
Which competitors, account, or market category should I compare?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when the account, meeting context, prior brief, source pack, or user-provided notes clearly name the competitor set or category.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: account context, opportunity status, known competitor fields, active deal motion, and account-specific competitive pressure.
- `document_store`: competitive docs, battlecards, account plans, enablement notes, product positioning, prior briefs, and proof points.
- `internal_messaging`: field signals, account-team observations, competitive chatter, objection examples, and source-of-truth routing when the user wants internal context.
- user-provided context: pasted notes, decks, transcripts, prior briefs, account context, objection lists, and uploaded/exported materials.
- public research: official competitor pages, product docs, pricing pages, customer stories, public filings, launch posts, investor materials, and reputable public coverage.

Authority and gaps:

- Prioritize user-provided and internal competitive materials over generic public research for sales posture.
- For named account/deal competitive briefs, `crm` is required when CRM is available and an account/deal anchor is supplied, inferred, or confirmed. Use CRM for account context, opportunity status, known competitor fields, active deal motion, and account-specific competitive pressure; do not let public research, docs, messages, or third-party enrichment override CRM-owned account/deal truth.
- Use public research to validate current positioning, launches, pricing, partnerships, and public proof; do not use it to invent private account status or deal presence.
- Treat internal docs and messaging as sales-context and field-signal sources; do not present them as current competitor facts when public product, pricing, release, or customer-proof evidence is needed and unavailable.
- Treat internal field signals as directional unless they are corroborated by account evidence or source-of-truth docs.
- If a source is unavailable, blocked, stale, or thin, continue with the strongest remaining evidence and label the limitation.

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

### First-Run Banner

If Sales preflight says the build-competitive-brief experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Build Competitive Brief
This skill helps compare competitors, alternatives, or market options for a deal, segment, or sales motion. It can use user-provided competitor names, CRM/deal context, internal docs, customer notes, public research, Slack, and prior battlecards. It produces a grounded competitive brief with comparison points, likely objections, proof, caveats, and talk tracks.

Definitions:
- Battlecard: a compact seller guide for how to position against a competitor, including where they win, where they are weaker, and what to say.
- Defensive prep: preparation for a competitor that may be relevant even when there is not enough evidence to say the competitor is active in the live deal.

```

Starter prompts:

- Primary default prompt: `Build a competitive brief for a competitor set.`
- `@Sales build a competitive brief for Acme comparing OpenAI, Anthropic, and Gemini.`
- `@Sales prep battlecard-style objections for the vendors showing up in my Globex deal.`
- `@Sales compare the competitor set in this account plan and highlight traps for the sales team.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Build Competitive Brief next-step behavior and action text. Onboarding, artifact creation, draft creation, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the competitive-brief continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `build-competitive-brief` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/saving/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the competitive brief** | The first substantive competitive brief has just been produced. | `Anything you'd change in the competitive framing before we turn it into something reusable?` |
| **2. Review the revised competitive brief** | The user asked for any change to positioning, matrix details, objection handling, proof points, uncertainty notes, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If that looks good, want me to draft the customer-safe response, internal battlecard note, objection talk track, or account-team update?` |
| **3. Prepare the competitive action** | The user accepts the brief, says no changes are needed, says a revision looks good, or asks to operationalize it. | Offer to produce the most useful next artifact or draft action, prioritizing customer-safe response, battlecard note, objection talk track, account-team update, or enablement snippet over broad suggestions. |
| **4. Review the artifact or draft** | A customer-safe response, battlecard note, talk track, account-team update, or enablement snippet exists, or the user asks to change it. | `Anything you'd change before I save, post, share, or draft this where it belongs?` |
| **5. Save, post, share, or draft approved competitive action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the battlecard, posting the account-team update, sharing the enablement snippet, or creating the customer response draft. Do not post or send messages unless the user explicitly asks for that action or approves the reviewed draft. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the competitive brief, treat a lightweight acknowledgement as acceptance and move to `Prepare the competitive action`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post or send externally. If the previous continuation offered to save, post, share, or draft a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Reference Loading

`SKILL.md` owns the normal modes, source order, workflow, output defaults, and artifact behavior. Load references selectively:

- Use `references/request-schema.yaml` only when structured input validation, YAML normalization, or machine-readable field shape matters.
- Use `references/source-priority.md` when source conflicts, public-proof downgrade behavior, or connector/source selection needs more detail than the workflow below.
- Use `references/output-contract.md` when exact section ordering, compressed brief variants, or machine-readable compatibility matters.

## Modes

Choose the narrowest mode that satisfies the request.

- `brief`: default mode; produce a canonical competitive brief with evidence and response guidance
- `objections`: focus on objection handling, proof points, and do-not-say guidance
- `positioning`: focus on comparison framing, where the competitor is dangerous, and how to respond
- `account_overlay`: focus on account-specific implications when the user supplies a target account

If the user does not specify a mode, use `brief`.

## Inputs

Normalize the request using the fields and defaults below.

Accept when provided:
- `seller_company_name`
- `account_name`
- `product_scope`
- `workflow_scope`
- `buyer_context`
- `competitor_scope`
- `max_matrix_competitors`
- `competitor_names`
- `industry`
- `region`
- `customer_segment`
- `mode`
- `known_objections`
- `existing_materials`

Normalization rules:
- If `seller_company_name` is missing, infer it from the prompt, uploaded materials, or available business context; otherwise ask one targeted clarification.
- Accept either one competitor or a list, and normalize to `competitor_names`.
- If the user does not name competitors, discover likely competitors from seller context, buyer context, product scope, and public evidence.
- Support zero to many discovered competitors, but render at most five competitors in one comparison matrix by default.
- Preserve exact competitor, seller, and account names from the user.
- Use neutral placeholders in examples, such as `MyCompany`, `Competitor Alpha`, and `ExampleCorp`, instead of assuming the seller is the current company.

## Workflow

Run these steps in order.

### 1. Normalize the request

- Map singular competitor input to `competitor_names`.
- Set `brief` as the default mode.
- Preserve the user’s exact seller names, competitor names, account names, and objection wording.

### 2. Gather seller context

- Identify `seller_company_name`, product or workflow scope, buyer context, and optional account context.
- Use public seller-company sources first for positioning, product lines, target segments, customer proof, recent launches, and comparison language.
- Treat this as the baseline for the seller side of the brief or matrix.
- If the seller cannot be inferred, ask for it instead of assuming the current company.

### 3. Gather the source corpus first

Prioritize:
1. user-provided notes, decks, transcripts, and prior briefs
2. `document_store` knowledge-base or competitive-doc sources when available
3. `internal_messaging` field signals only when the user asks for internal context
4. public web validation and public-proof sweep when relevant
5. public research or user-provided market intelligence only when it materially sharpens the story

Do not let generic web research replace stronger user or internal materials when those exist.

Minimum evidence coverage:
- competitor-only runs should use multiple distinct evidence units when available
- account-scoped runs should add account evidence when the user provided it or the connectors make it easy to fetch
- if a source lane is unavailable, state that directly and continue with the strongest remaining evidence path

Required public-proof sweep when relevant:
- if the brief relies on current competitor positioning, launches, pricing, partnerships, or customer proof, explicitly validate those claims
- search official company pages first
- then use primary-source public materials such as investor relations pages, earnings materials, official launch posts, product pages, or public customer stories
- use secondary coverage only when those primary sources are insufficient

Source-extraction rules:
- do not compress every source into the same vague reframe
- for each high-priority source, extract at least one concrete nugget into:
  - `what_they_are_claiming`
  - `what_is_confirmed`
  - `why_buyers_find_it_compelling`
  - `how_to_counter_or_reframe`
  - `what_not_to_overclaim`

### 4. Build competitor dossiers before synthesis

For each in-scope competitor, capture the most relevant available facts:

- profile and target market
- what they sell
- positioning versus alternatives
- pricing and pricing talk track when supported
- recent launches, releases, or news
- customer proof or review themes
- where they win
- where the seller can separate
- objections, talk tracks, and landmines

Example dossier labels:

- `Seller`: `MyCompany`
- `Primary competitor`: `Competitor Alpha`
- `Watchlist competitor`: `Competitor Beta`
- `Account`: `ExampleCorp`

### 5. Run account-context lanes when account context matters

- When `account_name` is present, use user-provided account notes first.
- If `crm`, `document_store`, or `internal_messaging` can sharpen the account context materially, use those lanes selectively instead of broad retrieval.
- If direct competitor evidence is not found in the account context, label the result as `defensive prep` instead of implying the competitor is confirmed in the live deal.

### 6. Gather supporting evidence only when it sharpens the brief

- Use `internal_messaging` only for field-signal evidence that changes the talk track or next move.
- Use public research or user-provided market intelligence only to validate claims, gather public proof, or close a concrete evidence gap.
- Keep field signals labeled as directional rather than durable proof.
- Keep unsupported or conflicting facts in an uncertainty note instead of smoothing them into the narrative.

### 7. Build the comparison matrix when useful

Always include the seller company in comparison logic when it is known.

Use the shape that fits the request:

- `1-v-1`: one seller column, one competitor column, and one `Readout` or `Winner` column
- `1-v-many`: `Area`, seller read, `Status`, and `Main pressure`

Example `1-v-1` row:

| Area | MyCompany | Competitor Alpha | Readout |
| --- | --- | --- | --- |
| Deployment fit | Strong for governed enterprise rollout | Strong for fast team-level adoption | Mixed; clarify buyer governance needs |

Example `1-v-many` row:

| Area | MyCompany read | Status | Main pressure |
| --- | --- | --- | --- |
| Buyer simplicity | Strong if the buyer values one accountable platform | Pressure from Competitor Beta | Competitor Beta may look simpler for a narrow departmental use case |

Status examples should stay generic:

- `Lead`
- `Pressure from Competitor Alpha`
- `Mixed`
- `Not determined`

### 8. Apply tone and framing guardrails

- Keep the tone factual and calm.
- Do not turn the artifact into a feature bakeoff unless the user explicitly asks for that style.
- Do not trash competitors or overstate confidence.
- Always include what to say, what to clarify, and what not to overclaim where relevant.

### 9. Build the structured package

- Build the brief from evidence units, not generic opinion.
- The package should answer:
  - what the competitor is doing
  - where they are dangerous
  - why they win
  - why they lose
  - how to compete
  - what the seller or strategist should say next
- If the user asks for a reusable artifact, format the response so it can be copied into a document or wiki. Do not assume a renderer script is available.

### 10. Optionally produce a shareable HTML artifact

If the user explicitly asks for a shareable artifact, HTML brief, battlecard page, or executive page, write a self-contained HTML file directly and return its path plus a short chat summary.

HTML artifact conventions:

- filename pattern: `{seller-company}-compintel-{YYYY-MM-DD}.html`
- create the file in the current workspace unless the user provides a destination; sanitize the seller-company filename segment and ask before overwriting an existing file
- top-level sections or tabs: `Overview`, `Competitors`, `Guidance`, `Sources`
- include source provenance and connector-lane status in `Sources`
- use a restrained, deck-inspired corporate layout
- use the user's provided brand conventions when available; otherwise use neutral, public web-safe styling
- do not hardcode the current company's brand, palette, product names, or visual system
- after writing, read the file back to verify it contains the required sections and source provenance; when a browser or Playwright-style renderer is available, render the local HTML once to catch blank pages, broken layout, or missing embedded CSS before returning the path

Useful generic tooltip labels:

- `Trigger`
- `Discovery questions`
- `Positioning`
- `Verified signals`
- `Where they win`
- `Where MyCompany can separate`
- `Why this works`
- `Proof`
- `Use when`
- `Landmine / do not say`

### 11. Handle conflicts and sparse evidence

- If sources conflict, say so and explain which source categories are more trustworthy.
- If evidence is sparse, narrow the brief, label weak spots, and end with the smallest useful set of follow-up questions.

## Output Rules

- Default to a concise brief with explicit source provenance. Use these sections unless the user asks for a narrower shape: `Context`, `Seller Baseline`, `Competitive Landscape Summary`, `Competitor Snapshot`, `Comparison Matrix Takeaways`, `Response Strategy`, `What Not To Overclaim`, and `Sources`.
- Include uncertainty notes when claims depend on limited or fast-changing public evidence.
- If `mode=account_overlay`, add account implications without implying direct competitive presence unless it is evidenced.
- Preserve useful examples by replacing internal company/product names with `MyCompany`, seller, product, account, or competitor placeholders. Do not delete examples just because they originally named an internal company.

## Example Prompts

- `Build a competitive brief for MyCompany vs Competitor Alpha.`
- `Create a battlecard for MyCompany against Competitor Alpha and Competitor Beta in financial services.`
- `Compare MyCompany's enterprise workflow platform against the top three alternatives for regulated buyers.`
- `Build an account-specific defensive prep brief for ExampleCorp where Competitor Alpha may be in the deal.`
- `Create a shareable HTML competitive brief for MyCompany vs Competitor Alpha.`

## Failure Handling

- If no reliable evidence exists beyond the competitor name, return a minimal brief structure plus the exact evidence gaps that block a stronger output.
- If a connector lane fails, continue with manual inputs and public evidence instead of stopping.
