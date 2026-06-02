---
name: zoominfo
description: ZoomInfo connector guide for Sales workflows or explicit ZoomInfo requests involving company search, contact search, enrichment, intent signals, similar-account discovery, contact recommendations, and company or contact research.
---

# ZoomInfo User Guide

Use this as the ZoomInfo-specific guide whenever the user or workflow is using ZoomInfo for market intelligence, data enrichment, prospect discovery, company/contact research, intent signals, lookalikes, or recommendation workflows. Keep the surrounding Sales workflow authoritative for the seller task itself; this guide adds ZoomInfo-specific routing, identifier resolution, query hygiene, enrichment sequencing, and result-quality guardrails.

Do not use this guide when the workflow uses another enrichment provider or no ZoomInfo connector.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before answering, searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`. Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance. Do not read or reinterpret raw Sales state files unless preflight fails, local shell access is unavailable, or the user explicitly asks for raw state inspection.

Use returned user context only as a relevance hint for ICP, territory, persona, terminology, and preferred output style. Do not let saved context replace ZoomInfo identifiers, supported lookup values, connector-returned facts, or explicit user constraints.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Connector Boundary

ZoomInfo supports several distinct lanes. Choose the narrowest lane that fits the request.

- Discovery: `lookup`, `search_companies`, `search_contacts`, `search_intent`
- Structured enrichment: `enrich_companies`, `enrich_contacts`, `enrich_intent`
- Narrative research: `account_research`, `contact_research`
- Similarity and recommendation: `find_similar_companies`, `find_similar_contacts`, `get_recommended_contacts`
- Connector feedback only when the user asks for it: `submit_feedback`

Do not blur these lanes:

- Use `search_*` to discover candidates.
- Use `enrich_*` when the user wants stronger structured fields or a verified detail check.
- Use `account_research` or `contact_research` when the user wants a narrative brief, meeting prep, or broader situational readout.
- Use similarity or recommendation actions for "more like this", account expansion, or stakeholder discovery, not as a substitute for precise search filters.

Do not present ZoomInfo as CRM ground truth. If a research response includes relationship or engagement context, label it as connector-surfaced context unless it is independently grounded by the surrounding workflow.

## Default Resolution Pattern

Run these steps in order.

1. Classify the target:
   - company set
   - contact set
   - one known company
   - one known person
   - buyer intent topic
   - lookalike or recommendation request
2. Normalize hard filters before searching:
   - geography
   - management level
   - department or job family
   - employee or revenue bands
   - industry or company type
   - technology filters
   - intent topics
3. Use `lookup` before search or intent flows whenever the connector expects standardized values.
4. Resolve canonical company or contact identity before enrichment, research, or recommendation actions that depend on IDs.
5. Verify that returned rows actually satisfy the user's hard constraints before summarizing them as matches.
6. State what was not found, weakly supported, or connector-limited instead of smoothing gaps away.

## Lookup Discipline

Use `lookup` to retrieve supported values instead of guessing connector-specific categories.

- Use it for `management-levels`, `metro-regions`, `industries`, `employee-count`, `departments`, `job-functions`, `company-types`, `revenue-ranges`, `tech-vendors`, `tech-products`, and `intent-topics` when those constraints matter.
- Use the standardized identifier returned by `lookup` where the downstream action expects an identifier, not a prettified display label.
- For technology-stack searches, resolve the vendor first, then resolve products for that exact vendor, then pass the returned product identifiers into search.
- For intent workflows, retrieve exact supported intent topics first. If the requested concept does not map cleanly to a supported topic, present the closest supported topic only when it is genuinely close; otherwise say the request is not precisely expressible through the current topic taxonomy.

Do not invent lookup values or silently swap in an adjacent category without saying so.

## Identifier Resolution

Resolve entities carefully before ID-dependent actions.

### Companies

- Prefer `companyId`, domain, website, or ticker over company name alone.
- If the user provides only a company name and the next step requires enrichment, research, or a target-company ID, first use `search_companies` to find the canonical company row when identity is not obvious.
- If multiple plausible companies remain, use domain, headquarters, industry, or the user's surrounding context to disambiguate. If ambiguity still matters, present the candidate set instead of picking one quietly.
- For company enrichment, prefer `companyId`, `domain`, or `companyWebsite` over vague name-only input when available.

### Contacts

- Prefer `personId`, business email, or an exact full-name-plus-company combination over a name alone.
- If the user asks for contact research, similar contacts, or another person-ID-dependent workflow from a name, first use `search_contacts` to resolve the target person.
- If the same name maps to multiple plausible people, keep the candidate list explicit and do not fabricate a single match.
- For contact enrichment, use the strongest supported identifier available; avoid broad name-only enrichment when a search pass can make the identity less ambiguous.

### Runtime Shape

- Pass connector-returned identifiers in the runtime-compatible primitive shape the action accepts.
- When the connector surfaces a numeric ZoomInfo identifier and the destination action requires a numeric identifier at runtime, preserve it as numeric rather than rewriting it into prose or guessing a new value.
- If an action rejects an apparently valid identifier shape, retry only once with the directly corresponding connector-returned primitive when the target is unambiguous. If that still fails, report a connector contract mismatch and continue only with lower-risk available evidence.

## Search Discipline

### Company Search

- Translate the user's ICP into explicit filters before searching.
- Prefer structured filters for geography, headcount, revenue, company type, funding, growth, and tech usage when the connector supports them.
- If the user asks for "US companies", "California companies", or another hard geography requirement, verify that each surfaced result matches the requested region before calling it a qualified match.
- If search returns close but imperfect rows, separate `Matches` from `Near Matches` rather than hiding the distinction.
- Do not claim exhaustive market coverage from a bounded result page.

### Contact Search

- Use management level, department, function, company, and title filters together when that improves precision.
- For role-family requests such as "VP, Director, or Head of RevOps", start with the narrowest structured interpretation that is likely to work.
- If a single broad title query returns sparse, clearly incomplete, or off-target results, split the role family into a small number of targeted searches, merge duplicates, and summarize the deduped shortlist.
- Prefer directly returned business fields. Do not infer private email addresses, personal phones, or missing professional profiles.

### Intent Search

- Always resolve exact intent topics with `lookup` before `search_intent` or `enrich_intent`.
- Keep topic meaning visible in the answer so the user can see what was actually searched.
- If returned intent topics are materially narrower, broader, or adjacent to the user's concept, say so.
- If the topic lookup or search path cannot support the requested concept faithfully, report that limitation instead of overstating the result.

## Enrichment And Research Sequencing

Use cheap narrowing steps before expensive or less precise actions when practical.

- Use search first when the entity itself is unclear.
- Use structured enrichment when the user wants firmographic fields, contactability fields, or batch-ready tabular output.
- Use narrative research when the user wants a briefing, situational awareness, or prepare-for-meeting style synthesis.
- For top-N discovery requests, do not enrich every raw candidate by default. Narrow first, then enrich only the shortlisted set that materially improves the answer.
- When a similarity or recommendation workflow returns sparse person or company detail, add a targeted enrichment pass only when the user asked for actionable detail or when the surrounding workflow needs it.

## Similarity And Recommendation Flows

### Similar Companies

- Use `find_similar_companies` when the user asks for competitor-like, lookalike, or adjacent-account discovery.
- If the reference company is ambiguous, resolve it before the similarity call.
- If the user wants a usable market list rather than raw similarity results, enrich the final shortlist just enough to supply requested basics such as website, location, employee range, or a concise description.

### Similar Contacts

- Resolve `referencePersonId` with `search_contacts` when the user gives a name.
- Resolve `targetCompanyId` with `search_companies` when the user wants lookalike contacts inside a specific account.
- Explain recommendations using returned metadata rather than making up a similarity rationale.

### Recommended Contacts

- Resolve the target company first.
- Choose the recommendation use case that matches the user intent:
  - `PROSPECTING`
  - `DEAL_ACCELERATION`
  - `RENEWAL_AND_GROWTH`
- Explain what the use case means in the final readout when it affects interpretation.
- Treat recommendation scores as ranking signals, not response probabilities or guaranteed success.

## Credit-Aware Behavior

Prefer free or lower-cost discovery steps before credit-consuming enrichment or AI research when the workflow permits it.

- Use `lookup`, `search_companies`, `search_contacts`, and `search_intent` to narrow scope first when appropriate.
- Use `enrich_companies`, `enrich_contacts`, `enrich_intent`, `account_research`, and `contact_research` when the user has asked for the stronger result those actions provide.
- For broad batch requests, make the action scope visible in the answer and avoid unnecessary enrichment of obviously weak candidates.

Do not add friction for a small, clearly requested enrichment task. Do be explicit when the connector result may have consumed meaningful credits or when a narrower rerun would be materially cheaper.

## Failure Handling

- If the connector returns no results, say `no clear ZoomInfo match returned` rather than inventing one.
- If results violate a hard filter, exclude them from the qualified set and mention the mismatch.
- If a required lookup value is unavailable, say which constraint could not be represented cleanly.
- If a research response is thin or generic, preserve the useful parts but label coverage as limited.
- If a recommendation or similarity call yields weak actionability, say what extra enrichment or user context would be needed.
- If the connector behavior appears inconsistent with its own action contract, describe the inconsistency plainly in the answer when it affects completeness or confidence.

## Output Rules

- Prefer compact tables for candidate lists, enrichment outputs, similar-company lists, and contact recommendations.
- Separate:
  - `Qualified matches`
  - `Near matches` when useful
  - `Gaps / connector limitations`
- Keep sourced facts separate from `Inference:`.
- Do not guess emails, phone numbers, exact intent, or confidence levels not surfaced by the connector.
- When the answer depends on connector-reported fields or recommendation metadata, say so directly.
- If the user's request asked for a ranked list, rank by explicit connector signal or stated criteria, not by invisible model preference.
