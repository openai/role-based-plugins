---
name: find-key-internal-sources
description: Find the best internal experts, documents, and chat channels for a customer question, product topic, objection, implementation issue, account task, or other internal topic using user-provided context, optional connector-assisted search, and evidence-backed ranking.
---

# Find Key Internal Sources

Use this skill to locate the people, docs, channels, source-of-truth pages, decision forums, and escalation paths that can answer a customer question or unblock a sales task.

This skill produces a practical routing map from grounded internal evidence. It is useful for customer questions, product topics, objections, implementation issues, account tasks, launch/rollout questions, and source-of-truth gaps. The initial routing map is read-only: it may draft a question or handoff, but it does not post, message, assign, or update systems. After a reviewed ask or handoff exists, it may offer supported posting or sharing only after explicit user approval of that reviewed action.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the routing map also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the routing map.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

For ownership or source-of-truth routing requests, prefer the source that most directly owns the requested fact before broad search. A company knowledge base, people directory, team directory, wiki owner field, go-link index, verified routing page, or maintained source-of-truth hub should be treated as the first-pass source when available, even if it resolves through the same `document_store` category as ordinary docs. Use `internal_messaging` as supporting evidence for recent practice, escalation texture, or active contributors; do not make message search the default authority for stable ownership when a canonical routing source can answer the question.

### Required Inputs

This skill needs enough user-provided or explicitly inferable context to identify the customer question, account blocker, product topic, initiative, implementation issue, or source-of-truth gap to route.

The skill can still produce a limited routing map from pasted notes, call follow-up output, meeting prep context, uploaded/exported context, or user-linked context alone when that context is sufficient. Connectors add significant value and reduce the burden on the user, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] `topic_or_task`: the core customer question, product topic, account blocker, initiative, implementation issue, or internal source-of-truth gap

Optional:

- `output_depth`: `quick` for top 3 each, or `deep` for top 5 to 8 each. Default to `quick`.
- account, customer, team, product, source, or urgency context when provided

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. When `crm` is available, include a bounded CRM lookup to resolve account identity, owner, or opportunity context before relying on docs or internal messages alone for a customer/account-specific routing map.
- Before asking the user to provide a customer question, topic, or source pointer, first try to infer concrete candidates from the active thread or prior Sales output, then the workflow source categories that can cheaply own the missing route: `crm` for customer/account context, `document_store` for canonical docs and owner metadata, and `internal_messaging` for channels, active contributors, and escalation texture.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

If `topic_or_task` remains missing or ambiguous, first attempt a bounded candidate pass through the active thread, recent Sales workflow context, saved team hubs, and only the source categories that can cheaply produce concrete choices, within the Fast Candidate Resolution budget. Ask one friendly clarification after that pass. Ask only for the unresolved topic; include concrete lettered options from source-backed or user-provided candidates when available.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

**Input Request Format Example:**

```md
What customer question, product topic, or internal source-of-truth gap should I route?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when call follow-up, meeting prep, account docs, Slack, saved team hubs, or the active thread clearly surfaced a specific blocker, question, or topic.

### Internal Ownership

Treat internal ownership as broader than "one person who knows the answer." Useful ownership can include DRIs, approvers, SMEs, maintainers, accountable teams, launch or rollout owners, recurring decision forums, canonical docs, escalation channels, support channels, and feedback channels. Rank ownership signals by how directly they help the seller get a reliable answer or next action.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, web search, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: customer/account identity, owner, opportunity/account context, and CRM-visible account blockers that clarify the customer question or implementation issue.
- `document_store`: canonical docs, wikis, pages, databases, source-of-truth hubs, decision records, runbooks, launch docs, owner metadata, recency signals, and linked artifacts.
- `internal_messaging`: public channels, threads, messages, recurring contributors, active expert signals, escalation channels, support channels, feedback channels, decision forums, and source-of-truth routes.
- user-provided context: pasted notes, prior Sales outputs, account context, customer question wording, uploaded/exported docs, and linked context that can seed or constrain the search.

Authority and gaps:

- Prefer sources that directly help the seller get a reliable answer or next action.
- For customer/account-specific routing, use CRM when available to resolve CRM-owned account truth before internal docs/messages; CRM does not replace source-of-truth docs/channels for who owns the answer.
- Do not present a CRM owner, account field, or opportunity note as the internal expert or source-of-truth route unless `document_store`, `internal_messaging`, user context, or explicit user-provided evidence supports that route.
- Search multiple source categories in parallel only when the requested answer shape needs them, or when parallel reads reduce elapsed time without widening scope. Do not use broad `internal_messaging` plus `document_store` fanout as the default for simple owner, doc, or channel routes.
- If one source is unavailable, continue with the other when it can produce useful routing evidence and record the gap.
- Default to public `internal_messaging` channels only. Include private channels only when the user explicitly asks.
- Exclude private channels, group DMs, direct messages, and externally shared channels unless the user explicitly asks and access is appropriate.
- Exclude deactivated or inactive `internal_messaging` users from expert recommendations.
- Use company-specific terminology only from user-provided context, connector-visible source truth, or Sales plugin-scoped user context. Do not hardcode company-specific process names, channel patterns, product names, URLs, or boost rules into this skill.

### Context Gathering Principles

Optimize for marginal value, not exhaustive coverage.

- Classify the requested answer shape before searching: `owner route` for experts/POCs/approvers, `doc route` for source-of-truth or approved wording, `channel route` for where to ask, and `full map` only when the user asks for people, docs, and channels together.
- Start with the source category that owns that answer shape and the narrowest query that could answer it. For owner routes, start with canonical ownership, directory, or routing sources when available; for doc routes, start with source-of-truth docs; for channel routes, start with channel/topic search or saved escalation routes.
- In default `quick` mode, spend a small bounded first pass before answering: one canonical source attempt, one narrow fallback attempt when the first pass is empty/thin/misleading, and at most one fetch or thread read per top candidate unless the user asked for `deep`.
- Treat roughly three to five minutes of active retrieval, two slow connector calls, or one timeout/rate-limit on a non-required enrichment source as the practical quick-mode budget. When that budget is reached, yield back to the user instead of continuing silent retrieval: return the best supported routing map or checkpoint, name limitations in `Coverage Gaps`, and make the final natural continuation one concrete choice to clarify or give a steer, continue deeper, or act on the current best route.
- Broaden only when the first pass is empty, thin, misleading, or the user's requested output explicitly needs multiple source types. Do not fan out across docs and messages merely because both are available.
- Answer once the core artifact is supported by a direct source. Use optional sources to improve confidence only when they materially change who to ask, what to read, where to ask, or what wording is safe to reuse.

### First-Run Banner

If Sales preflight says the find-key-internal-sources experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Find Key Internal Sources
This skill helps locate the people, docs, Slack channels, source-of-truth pages, decision forums, and escalation paths that can answer a customer question or unblock a sales task.

Definitions:
- Source-of-truth page: the maintained doc, wiki, tracker, or page that should be treated as the most authoritative answer source.
- DRI: directly responsible individual, the person accountable for a topic, decision, or follow-through.
- SME: subject matter expert, someone with practical depth on the topic even if they are not the accountable owner.
- Decision forum: the recurring meeting, channel, doc, or group where tradeoffs and approvals are handled.

```

Starter prompts:

- Primary default prompt: `Find the key internal sources for a customer question.`
- `@Sales find who owns the Enterprise SSO rollout path for Acme.`
- `@Sales find the docs and channels for answering a customer's security review question.`
- `@Sales route this implementation blocker to the right internal people and source of truth.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Find Key Internal Sources next-step behavior and action text. Onboarding, draft creation, posting or sharing, source-list creation, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the internal-routing continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `find-key-internal-sources` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/posting/saving/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the routing map** | The first substantive routing map has just been produced. If quick-mode retrieval stopped at the retrieval budget, make the next action the most practical recovery path: ask for a narrow steer, offer a deeper search, or suggest using the current best route when it is good enough. | `Does this routing map look good enough to use, or should I dig one level deeper?` |
| **2. Review the revised routing map** | The user asked for any change to owners, docs, channels, confidence, scope, wording, or search depth. Make the change in chat first. | `Anything else you'd change? If that looks good, want me to draft the first Slack ask, internal handoff note, source-of-truth reading list, or customer-safe response?` |
| **3. Prepare the routing action** | The user accepts the map, says no changes are needed, says a revision looks good, or asks to act on the route. | Offer to produce the most useful next artifact or draft action, prioritizing a Slack ask, internal handoff, escalation note, source-of-truth reading list, or customer-safe response over broad suggestions. |
| **4. Review the ask, handoff, or response** | A Slack ask, handoff note, reading list, escalation note, or customer-safe response exists, or the user asks to change it. | `Anything you'd change before I save, post, or share this?` |
| **5. Post, share, or save approved routing action** | A reviewed ask, handoff, response, or reading list exists and does not need edits. | Offer the specific supported action, such as posting the approved Slack ask, saving the reading list, or sharing the handoff note. Do not post or send messages unless the user explicitly asks for that action or approves the reviewed draft. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the routing map, treat a lightweight acknowledgement as acceptance and move to `Prepare the routing action`. If the previous continuation offered to prepare an ask, handoff, response, or list, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post or send externally. If the previous continuation offered to post, share, or save a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Procedure

### 1. Normalize the request

- Extract `topic_or_task` from the user request, prior call follow-up output, meeting prep, account docs, internal messaging context, saved team hubs, or the active thread when safe.
- Default `output_depth` to `quick`.
- Keep user-provided customer/account context, urgency, and desired audience as prioritization context.
- If no usable topic can be identified, ask the clarification in `Required Inputs` instead of producing a generic source map.

### 2. Choose the answer route and build search facets

Choose the smallest route that satisfies the user's request:

- `owner route`: the user asks who owns the topic, who knows, who approves, who to contact, or which expert/POC/lawyer/specialist to ask. Start with canonical ownership or routing sources, then use docs or `internal_messaging` only to fill gaps.
- `doc route`: the user asks what to read, what the source of truth is, or what approved wording exists. Start with verified or maintained source-of-truth docs and fetch only the most relevant top result before ranking.
- `channel route`: the user asks where to ask, where discussion happens, or which escalation/support channel to use. Start with channel/topic/source-of-truth route search and use message search only when it changes confidence.
- `full map`: the user asks for experts, docs, and channels, or the request clearly needs multiple answer paths. Use the full workflow and search the necessary source categories.

Do not produce every section at full depth when the user asked for only one route. Keep required output sections, but mark unsearched or low-value sections as `Not searched in quick pass` or `No high-confidence candidate found in quick pass` when appropriate.

Build query facets from:

- primary terms from `topic_or_task`
- aliases, abbreviations, product/team/system names, and legacy/current names when available
- task-shape terms such as troubleshooting, incident, RFC, approval, compliance, runbook, playbook, owner, rollout, escalation, or support
- user-provided account/customer context when it helps disambiguate the route
- route-shape terms that identify the answer path, such as field guide, GTM, specialist, enablement, FAQ, source of truth, security, policy, exception, approval, implementation, support, or escalation

Use [references/search-patterns.md](references/search-patterns.md) for query construction details when fan-out quality, source-specific search behavior, or stopping rules are ambiguous.

For compound topics that combine a product or account surface with a policy, security, retention, implementation, pricing, launch, or support question, split the search into at least two tracks:

- the underlying control/process track, such as the policy, approval, exception, enablement, or implementation process;
- the product or GTM routing track, such as the product field guide, launch hub, specialist team, seller FAQ, customer-facing collateral, or support channel.

Keep both tracks in the candidate pool until ranking. Do not let a strong process result crowd out product-specific seller routes, and do not let product launch/GTM hits replace policy or implementation ownership when the question needs both.

### 3. Expand search only as needed

- Start with exact or canonical topic terms per source.
- Add synonym and contextual variants only when the first pass is empty, thin, ambiguous, or the compound topic needs both process and product routing tracks.
- Search `internal_messaging` and `document_store` in parallel only when it reduces elapsed time without widening scope and the selected answer route needs both categories.
- For `internal_messaging`, search public channel names/descriptions and public messages/threads by default. Prefer server-side visibility filters when available; otherwise post-filter by visibility metadata.
- For `document_store`, search both exact topic wording and route-shape variants for central hubs, field guides, FAQs, playbooks, and source-of-truth pages. Prioritize title and heading matches before body-only matches. Prefer pages linked from central hubs/wikis and pages with active updates.
- When a source result points to a central guide, channel topic, channel purpose, linked doc, thread, or source-of-truth hub, fetch or inspect that result before final ranking when the connector exposes a readable link or object id.
- Stop expansion when the core answer is supported, top results stabilize across two or more query variants, additional variants add low-confidence duplicates, or the quick-mode retrieval budget is reached.

### 4. Pull source candidates

Pull candidates from:

- `internal_messaging`: candidate channels, channel topics/purposes, thread/message evidence, recurring contributors with recent participation, decision forums, escalation paths, specialist-team routes, and support/feedback channels.
- `document_store`: candidate docs, pages, databases, field guides, playbooks, source-of-truth hubs, owner signals, recency, linked docs, and listed support or specialist routes.

For people recommendations derived primarily from `internal_messaging`, require at least one ownership or expertise signal from the last `90 days`; down-rank or omit stale chat-derived candidates. Canonical owner pages, maintained directories, verified routing docs, or current policy/source-of-truth docs can satisfy ownership without recent message evidence, but label stale or unverified owner metadata when freshness affects confidence.

### 5. Apply organization-specific context safely

Apply organization-specific behavior only from user-provided context, connector-visible source truth, or Sales plugin-scoped user context read through `sales:user-context`.

Do not add org-specific channel patterns, product names, boost rules, account data, URLs, or private process names to bundled plugin files. Use [references/company-context.md](references/company-context.md) only for generic rules about how to apply Sales plugin-scoped terminology safely.

Apply company context after generic candidate retrieval:

1. Use it to add source-specific query expansions.
2. Use it to boost or down-rank candidates.
3. Keep generic scoring as the base and cap context-based boosts.

### 6. Aggregate, score, and rank

Normalize all candidates into a shared structure:

- `type`
- `title_or_name`
- `url`
- `source`
- `evidence`
- `owner_signals`
- `timestamps`

Deduplicate near-identical entries.

Score using:

- relevance
- authority
- freshness
- cross-source confirmation
- practical seller route quality, including whether the item gives a clear place to ask, a team to tag, an owner to contact, or approved customer-facing wording

For ownership recommendations, include the ownership type when inferable, such as DRI, approver, SME, maintainer, accountable team, decision forum, launch owner, escalation channel, support channel, or feedback channel. Prefer fewer high-confidence items over long noisy lists.

Ranking tie-breakers:

- Prefer direct evidence links over profile-only or channel-only matches when recommending experts.
- Prefer verified or recently maintained field guides, playbooks, FAQs, and source-of-truth hubs over one-off notes when the user needs seller routing or approved wording.
- Prefer channels whose topic, purpose, central guide, or recent threads show an ownership path over channels that merely mention the topic.
- Keep distinct answer paths when a topic spans multiple ownership surfaces, such as product/GTM guidance plus policy/implementation approval. Do not collapse them into a single generic owner.

### 7. Render the routing map

Return `Experts`, `Docs`, `Channels`, `Recommended First Ask`, and `Coverage Gaps` sections.

For every item, include:

- one-line rationale
- direct source link when available
- ownership or answer-path type
- evidence or signal that supports the recommendation
- freshness or confidence when it affects trust

Explain what kind of ownership or answer path each recommendation appears to provide, not only why it matched the query. If a source has no useful URL or stable connector-visible link, use a plain text label and say `(no useful link available)` when that absence matters.

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL.

When the evidence suggests the user's phrasing may conflate two surfaces, such as a product surface and an API/process/policy control, include a short framing note before the ranked sections. Keep it practical: name the split, explain why it affects the answer path, and continue with the routing map instead of stopping for clarification unless the distinction changes which sources are safe to use.

## Output Shapes

Use compact Markdown headings and bullets. Keep the result focused on the routing decision, not a full research memo.

Required sections:

1. `Experts`
2. `Docs`
3. `Channels`
4. `Recommended First Ask`
5. `Coverage Gaps`

For `quick` output, return up to 3 items each for experts, docs, and channels, and use the quick-mode retrieval budget from `Context Gathering Principles`. For `deep` output, return 5 to 8 items each when the evidence quality supports that many.

`Recommended First Ask` should give the seller one concrete next message or question to send to the best owner/channel. Keep it draft-ready, but do not post it.

`Coverage Gaps` should name unavailable or weak sources, how that affects confidence, and the smallest useful next step.

## Rules

- Keep the routing-map phase read-only. Do not post to `internal_messaging`, send messages, assign owners, or update docs unless the user has explicitly approved a reviewed ask, handoff, or update in a separate action step.
- Do not fabricate owners, experts, channels, docs, source-of-truth paths, or links.
- Rank ownership signals by practical usefulness for the seller's next action.
- Default to public channels only; include private channels only when the user explicitly asks.
- Exclude deactivated/inactive `internal_messaging` accounts from expert recommendations.
- Keep facts and inference separate. Label uncertain ownership as `Likely` or `Possible`.
- Prefer fewer high-confidence routes over long noisy lists.
