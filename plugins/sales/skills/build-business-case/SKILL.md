---
name: build-business-case
description: Build customer-led business cases, ROI narratives, value models, executive summaries, and customer-ready value stories from uneven customer context, metrics, transcripts, notes, and public evidence.
---

# Build Business Case

Use this skill for customer-led business cases, ROI narratives, value models, executive summaries, customer-ready value stories, and follow-up question sets tied to a specific customer, workflow, or decision context.

Do not use this skill for generic product positioning with no customer angle.

Core invariant: start with the customer, not the product. Follow this chain on every run:

`customer context -> account-native anchor -> workflow -> use case -> value drivers -> metrics -> quantified impact -> narrative -> public research when useful`

If evidence is sparse, produce a clearly labeled structural hypothesis or follow-up question set instead of fake specificity or fake math.

## Skill Configuration

### User Context

Mandatory pre-answer gate:

- Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`.
- Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance.
- Apply hard `final_obligations` unless the response is clarification-only. If an obligation is an onboarding reminder and the business-case output also needs a skill-owned final continuation, satisfy both in one final natural continuation instead of rendering a standalone onboarding reminder plus a second CTA.
- Apply `context_gap_note` only when missing setup or inaccessible sources materially limits the business case.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Resolution

Use `context.sources` from the `sales_preflight` envelope to resolve each attempted semantic source category to available apps, connectors, and helper skills. Defer connector fallback, source preferences, durable source rules, and helper-skill loading mechanics to `sales:user-context`. Do not prompt about categories this skill does not attempt.

### Required Inputs

This skill needs enough user-provided, connector-visible, public, or explicitly inferable context to identify the customer angle and the business workflow or decision context.

The skill can still produce a limited structural case from pasted notes, uploaded/exported account context, discovery notes, customer metrics, public-company context, or user-linked materials when that context is sufficient. Connectors add significant value and reduce manual work, but do not stop solely because connectors are unavailable.

**Inputs:**

Require:

- [required] `customer_or_context`: customer, account, company, segment, or clearly described customer scenario
- [required] `workflow_or_decision_context`: workflow, initiative, use case, decision, pain, metric goal, or provided notes that anchor the value case

Accept when provided:

- buyer role, industry, solution scope, customer metrics, current tools, known constraints, source materials, strategic priorities, proof points, analogous wins, output mode, and public-research preference

**Context Rules:**

- If a required input is missing or ambiguous, use Fast Candidate Resolution: make at most 3 total tool calls before asking the user to choose, including mandatory Sales preflight. Search only to produce useful concrete defaults, then ask the user to confirm or supply that required input before drafting.
- Treat ambiguous company-like proper nouns, partner names, and account shorthands as possible customer/account anchors unless the request clearly indicates an internal-only person, product, or topic. When `crm` is available, include a bounded CRM lookup before relying on docs, notes, messages, public research, or third-party enrichment alone. If CRM returns one high-confidence account match, use it as the primary customer candidate; if multiple plausible account matches remain, ask the user to choose from concrete candidates.
- Before asking the user to paste customer context, metrics, or discovery notes, first try the workflow source categories that can identify the missing customer or value-motion anchor: `crm`, `meeting_notes`, and `document_store`, then public research only when an account-native source is unavailable or too thin. Manual input is the fallback after those categories are unavailable, empty, or insufficient for a stable candidate.
- User confirmation is required for any required input inferred from sources rather than provided by the user.
- When asking, present up to 5 concrete candidates with one-line rationale. Make lettered options usable as reply targets, but omit a separate reply-with-letter footer when the choices are already clear.

When a required anchor is ambiguous, do the minimum source lookup needed to produce concrete choices within the Fast Candidate Resolution budget, then ask immediately. Do not gather enrichment evidence before the user selects the anchor.

If customer, workflow, and decision context are all too weak to form a stable first-pass hypothesis, ask only the minimum clarifying question needed.

**Input Request Format Example:**

```md
Which customer and workflow, initiative, or decision context should I build the business case around?

a. **{actual candidate}** - {short source-derived context}
b. **{actual candidate}** - {short source-derived context}
```

Proceed with a sensible default when the active thread, recent meeting, CRM opportunity context, account docs, discovery notes, pasted metrics, or public-company prompt clearly names the customer and value motion.

### Workflow Sources

When this skill uses a source category, use it for the following information. Do not use indirect or mirrored sources, browser UI, or Computer Use as substitutes for the authoritative category.

Source categories:

- `crm`: account identity, opportunity context, stage, amount, close timing, account owner, activity history, deal notes, and opportunity-linked value or decision context.
- `meeting_notes`: discovery notes, transcripts, stakeholder language, workflow pain, buyer priorities, objections, quantified claims, decision process, and validation gaps.
- `document_store`: account plans, discovery docs, prior business cases, customer notes, proof points, value frameworks, internal account strategy, and source-of-truth context.
- `data_enrichment`: company profile, fit signals, stakeholder background, tech stack, funding, and org context when those details sharpen the value story.
- user-provided context: pasted notes, customer metrics, public or internal excerpts, uploaded/exported materials, account context, current tools, known constraints, and explicit assumptions.
- public research: company-controlled public materials, investor relations, annual reports, 10-Ks, quarterly filings, earnings commentary, company website pages, and recent material news.

Source obligations by intent:

- Start with the highest-signal account-native anchor: user-provided metrics/notes, discovery notes, source-pack docs, `crm` opportunity context, or account documents. Do not begin with broad public research when an account-native anchor exists.
- Use `meeting_notes` when value claims depend on discovery evidence, stakeholder language, customer pain, quantified claims, objections, or decision process. If checked and no relevant discovery evidence is found, label the validation gap instead of inventing customer-confirmed value.
- For customer/account business cases, `crm` is required when CRM is available and a customer/account anchor is supplied, inferred, or confirmed. Use CRM for account identity, opportunity posture, commercial anchors, close timing, decision context, owner, activity history, and deal notes. Use `document_store` when account strategy, source packs, or prior business-case materials materially affect the case. If either source is unavailable, continue from sufficient account-native or user-provided evidence and name the gap.
- Use `data_enrichment` only as optional background for fit, company, contact, and market context. It must not substitute for customer-confirmed pain, metrics, decision process, CRM truth, or meeting-note evidence.
- Use public research only as optional enrichment for strategic priorities, external operating pressure, and public-company context. It must not substitute for customer workflow metrics or account-native truth.

Authority and gaps:

- Prioritize evidence in this order when sources conflict or completeness varies:
  1. customer-provided metrics;
  2. product telemetry or usage data;
  3. discovery notes or `meeting_notes`;
  4. `crm`, `document_store`, or internal account notes;
  5. public filings, earnings materials, website, investor materials, and recent material company news;
  6. analogous wins or directional benchmarks.
- Public research is useful for strategic priorities, executive wording, operating pressure, and "why now" context. It must not replace account-native truth.
- Do not let public research, docs, notes, messages, or third-party enrichment override CRM-owned customer/account truth.
- Use `meeting_notes` and account-native docs for customer-confirmed pain, metrics, decision process, and ROI validation; public or analogous evidence can frame hypotheses but cannot make them customer-confirmed.
- Do not use public research to invent baseline workflow metrics, internal tooling certainty, economic buyer certainty, workflow owners, or customer-confirmed ROI.
- If public sources are unavailable, thin, or low-signal, continue with internal or user-provided evidence and label the gap.

Commercial anchor preservation:

- Preserve commercial anchors from account-native sources, including pilot amount, expansion path, target contract value, budget range, close timing, forecast status, and paid-pilot terms.
- Label commercial anchors as `Known` when they appear in customer-provided context, CRM, opportunity snapshots, source-pack documents, account-native docs, or meeting notes.
- Do not drop commercial anchors merely because CRM search is noisy, empty, or missing adjacent opportunity fields. Instead, say which source supplied the commercial fact and separately name the CRM gap.
- Example: `Known from document_store source pack: SGD 420K pilot target and SGD 1.8M expansion path. Missing from CRM connector search: opportunity stage, owner, and close date.`

### Context Gathering Principles

Optimize for marginal value, not absolute speed.

- Start with the canonical source and narrowest scope.
- Gather evidence that materially improves the answer.
- Take the 80/20 path when it gives a useful, grounded result.
- Broaden only when the first pass is empty, thin, or misleading.
- Answer once the core artifact is supported; name limitations and offer expansion options.

For ordinary business-case requests, optimize for the highest-value first artifact, not exhaustive enrichment. Find the highest-signal account-native anchor, draft the decision-useful case, and offer targeted deepening only when the next decision needs it.

Default route:

- Prefer the highest-signal canonical anchor over broad shallow search. If one source contains the customer, workflow, decision audience, commercial stakes, metrics, urgency, and caveats, fetch it first.
- Use adjacent sources only to validate material gaps such as approval path, budget ownership, workflow risk, decision timing, or customer-facing follow-up.
- Treat optional enrichment as conditional. Public research, broad meeting enumeration, generic account search, and inbox search should run only when they can change the strategic framing, confidence level, customer-facing artifact, or next step.
- Stop the first pass once enough authoritative data exists to produce the core business case and name evidence gaps. Do not continue low-yield searches merely because more connectors are available.
- If source retrieval is slow or repeatedly noisy, draft from the best available account-native anchor and label the missing source, rather than spending the ordinary path on broad reconstruction.


### First-Run Banner

If Sales preflight says the build-business-case experience has not been introduced and this skill is the primary user-facing skill, render a compact first-run intro before the normal output:

```md
## Build Business Case
This skill helps turn customer context, workflow pain, metrics, discovery notes, transcripts, CRM evidence, docs, and public context into a customer-led business case. It produces a clear view of the workflow, value drivers, assumptions, quantified or structural impact, proof points, and open validation questions for a seller or account team to use.

Definitions:
- Value hypothesis: a directional claim about potential customer impact that still depends on assumptions or missing inputs.
- Finance-ready case: a version of the business case with enough sourced inputs to support quantified ROI or scenario math.
- Analogous win: evidence from a similar customer or situation that can support a hypothesis without pretending it is proof for this customer.

```

Starter prompts:

- Primary default prompt: `Build a business case for a customer.`
- `@Sales build a business case for Acme's support automation initiative.`
- `@Sales turn these discovery notes into a value case for reducing manual sales operations work.`
- `@Sales create a structural business case for Globex even though we are missing exact metrics.`

When invoked by guided Sales onboarding:

- Suppress the final CTA unless this skill intro is the active onboarding step.
- Return status and next-step candidates for onboarding to arbitrate.
- Mark whether this skill was introduced, tried, skipped, blocked, or accepted.

### Next Step Guidance

This section is the single owner for Build Business Case next-step behavior and action text. Onboarding, artifact creation, spreadsheet creation, draft creation, posting or sharing, and follow-up turns may route into this journey or wrap its selected action in their own presentation frame, but they must not redefine the business-case continuation states elsewhere.

#### Final Continuation Invariant

Every final assistant response while `build-business-case` is the active workflow must end with exactly one user-visible next action, phrased as a natural sentence or question in the ordinary prose of the response. This is a final-response gate, not a journey preference. It applies even when the response is only a short answer, local rewrite, one-paragraph summary, confirmation, readback, source-gap note, partial result, status after creating/updating/posting/saving/linking an artifact, or explanation of what changed. Before sending, inspect the final visible assistant-written content: if it does not end with a concrete next action, add the earliest valid continuation below or explicitly choose one of the allowed omission reasons.

Omit the continuation only when the user explicitly asks for no follow-up, the workflow is explicitly closed by the user, a scheduled automation correctly returns `DONT_NOTIFY`, or another active parent flow owns the final CTA. Required-input and clarification responses are not omission cases; make the unresolved question the final natural continuation.

If Sales onboarding is active and the `sales_preflight` final obligations include a core-onboarding reminder, fold the reminder into this same final natural continuation. Do not render a separate onboarding reminder plus a second CTA.

#### Journey States

Use the earliest state whose condition matches the current artifact. Do not end with only a bare confirmation, source link, or "done" message while a valid next step remains.

| State | Use when | Final continuation |
| --- | --- | --- |
| **1. Review the business case** | The first substantive business case has just been produced. | `Anything you'd change in the business case before we make it customer-ready?` |
| **2. Review the revised business case** | The user asked for any change to value framing, numbers, confidence labels, audience, customer language, source treatment, or formatting. Make the change in chat first. | `Anything else you'd change? If that looks right, want me to turn it into a customer-ready executive summary, champion talk track, value table, or spreadsheet model?` |
| **3. Prepare the value artifact** | The user accepts the case, says no changes are needed, says a revision looks good, or asks to operationalize it. | Offer to produce the most useful next artifact or draft action, prioritizing executive summary, champion talk track, value-model table, spreadsheet model, customer-ready note, or internal account-team note over broad suggestions. |
| **4. Review the artifact or draft** | An executive summary, talk track, value table, spreadsheet, customer-ready note, or internal note exists, or the user asks to change it. | `Anything you'd change before I save, share, or draft this where it belongs?` |
| **5. Save, share, or draft approved business-case action** | A reviewed artifact or draft exists and does not need edits. | Offer the specific supported action, such as saving the spreadsheet, sharing the executive summary, creating the customer-facing draft, or saving the internal note. Do not post or send messages unless the user explicitly asks for that action or approves the reviewed draft. |

#### Acceptance Handling

For follow-up turns after a visible continuation, treat short affirmative replies such as "yes," "ok," "okay," "sure," "sounds good," "looks good," "do it," or "go ahead" as acceptance of the offered journey step unless the user clearly declines, changes topic, or closes the workflow. If the previous continuation asked for review of the business case, treat a lightweight acknowledgement as acceptance and move to `Prepare the value artifact`. If the previous continuation offered to prepare an artifact or draft, produce that artifact or draft for review; do not interpret the acknowledgement as approval to post or send externally. If the previous continuation offered to save, share, or draft a specific reviewed action, a lightweight affirmative can authorize that specific action when the available tool supports it. Execute the accepted action, then render the next valid natural continuation.

## Reference Loading

`SKILL.md` owns the normal execution path, evidence order, guardrails, and default output shape. Load references selectively:

- Use [references/input-and-output.md](references/input-and-output.md) when inputs are especially uneven, the user names an output mode, or you need the full required-content contract.
- Use [references/workflow.md](references/workflow.md) when a complex request needs the expanded step-by-step workflow or you are checking behavior against the full workflow detail.
- Use [references/value-model-and-evidence.md](references/value-model-and-evidence.md) when quantification, confidence labeling, evidence conflict, or value-bucket logic needs more detail.
- Use [references/output-and-presentation.md](references/output-and-presentation.md) only for final response/output pattern details, formatted artifact presentation guidance, or behavior tests.

## Procedure

### 1. Resolve customer and decision context

Determine:

- who the customer is;
- what industry or segment they are in;
- what they are trying to achieve;
- what pressure makes the work urgent;
- which buyer, team, or stakeholder matters;
- what constraints are visible.

Anchor the narrative in the customer objective and business pressure. Do not jump to product recommendations before this step is complete.

### 2. Find the account-native business-case anchor

When the request names a customer, account, pilot, or workflow but does not include pasted source material, look for the highest-signal business-case anchor before broad enrichment.

Search the preferred `document_store` first when available, then CRM, meeting notes, and email only as needed. Use narrow exact-match queries before broad account searches:

- `{customer} business case`
- `{customer} value case`
- `{customer} CFO value case`
- `{customer} ROI`
- `{customer} pilot target`
- `{customer} expansion path`
- `{customer} {workflow} pilot`
- known shorthand or acronym variants when visible or user-provided

High-signal anchors include pages, docs, records, or source-pack items whose title or snippet contains terms such as `business case`, `value case`, `CFO value case`, `ROI`, `pilot target`, `expansion path`, `paid pilot`, `value model`, `executive case`, or `source pack`.

If a high-signal anchor is found, fetch it first and use it as the primary account-native source. Then fetch only the few adjacent records needed to validate workflow, risks, approvals, budget ownership, and customer follow-up. Do not enumerate broad meeting lists, public research, generic CRM records, or inbox results before checking whether the anchor already contains the required business-case facts.

Use the backed-up skill or baseline run as a behavioral reference for this retrieval pattern: the strongest OPB baseline selected `OPB: Build CFO value case` first because it contained the named customer, executive audience, pilot amount, expansion path, workflow metrics, urgency, and explicit caveats. Preserve that anchor-first behavior while applying this skill's stricter evidence labeling and source-provenance rules.

### 3. Run public research when useful

For public companies, or when public context can materially sharpen strategic priorities, executive wording, operating pressure, or "why now" context, run public research when it improves the business case enough to justify the source read. For private, low-public-signal, or account-native requests, treat public research as conditional and do not let it delay the first useful business case.

Gather and synthesize, when available:

- investor relations materials;
- 10-K, annual report, or quarterly filings;
- earnings call commentary;
- shareholder letters or quarterly results decks;
- company website, product pages, and corporate pages;
- recent material news that changes priorities or urgency.

Use concrete dates for recent developments when they materially affect urgency. Do not let public evidence override stronger customer, system, or conversation evidence. Do not bloat the output with generic company background.

### 4. Identify the business workflow before the use case

Before identifying use cases, understand the actual workflow, business process, or functional motion the customer is trying to improve.

For each workflow, inspect:

- actors and teams involved;
- major steps and handoffs;
- bottlenecks, manual work, delays, or quality breakdowns;
- tools or systems involved;
- KPIs and what "good" looks like.

Name the workflow in business language, not product language.

### 5. Prioritize use cases

Prioritize one to three use cases tied to the customer's goals and workflow constraints. Do not list attractive but weakly supported use cases.

For each use case, explain:

- the workflow problem it addresses;
- why it matters now;
- which buyer or team cares;
- what evidence supports it;
- what still needs validation.

### 6. Map value drivers

Use these value buckets exactly. Inline the logic rather than inventing new categories:

- `Enhanced Productivity`
- `Cost Reduction`
- `Risk Reduction`
- `Revenue Acceleration`
- `Time to Market`

Map each use case to the fewest value buckets needed. Make the causal chain explicit. Do not treat "value" as a vague synonym for "better."

### 7. Identify required metrics

For each use case, identify the minimum metrics required for credible quantification, separating known inputs from missing inputs.

Common metrics include:

- number of users or workflows;
- task volume and frequency;
- time per task and time saved per task;
- labor cost and adoption rate;
- cycle time, defect rate, error rate, or incident cost;
- conversion rate, revenue influenced, launch speed, tool spend, or contractor spend.

Do not imply quantifiability when required inputs are missing.

### 8. Quantify only when inputs support it

Build directional or quantified value hypotheses only when the evidence supports them.

When credible, show:

- formula logic;
- known inputs;
- assumptions;
- low, base, and high scenarios;
- caveats.

If inputs are too weak for quantified scenarios, keep the case structural and state exactly what data would be required to move from structural case to finance-ready case.

### 9. Draft the customer-led narrative

Translate operational impact into business outcomes, then write the narrative in customer-led, seller-ready language.

The narrative must connect:

- customer priority;
- customer challenge;
- relevant workflow;
- relevant use case;
- expected business impact;
- why the seller solution fits;
- what assumptions matter;
- what still needs validation.

The narrative should sound consultative, outcome-oriented, grounded, and tailored. It should not sound like a product datasheet.

### 10. Render the default package

Unless the user asks for a different shape, return a decision-useful package with these sections:

1. `Executive Summary`
2. `Strategic Initiatives`
3. `Key Challenges`
4. `Priority Workflows`
5. `Priority Use Cases`
6. `Value Hypothesis by Use Case`
7. `Metrics and Assumptions`
8. `ROI or Value View`
9. `Solution Differentiators`
10. `Proof Points or Analogous Wins`
11. `Caveats and Open Questions`

Output expectations:

- `Executive Summary` must include what the customer is trying to achieve, why it matters now, the most relevant workflows and use cases, the likely value story, and why the seller solution is relevant.
- `Metrics and Assumptions` must include required inputs, known data, assumptions, and confidence level.
- `ROI or Value View` should include low, base, and high cases only where possible.
- `Solution Differentiators` must tie differentiators to the workflow, buyer need, and expected business effect.
- `Proof Points or Analogous Wins` should keep public-company statements separate from account-native proof.
- `Caveats and Open Questions` must name what still needs validation and what public research could not determine.

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

## Evidence And Assumption Rules

- Label important claims as `Known`, `Inferred`, `Assumed`, or `Missing` whenever evidence is mixed.
- Label public-derived insights clearly when they materially shape strategic context or "why now" framing.
- Keep public strategic context separate from account-native proof.
- If public evidence conflicts with stronger internal evidence, prefer internal evidence and call out the tension when it materially changes the case.
- Use analogous wins and benchmarks to shape hypotheses, not to pretend customer proof exists.
- If confidence is low, say why. Do not soften uncertainty into polished prose.

Never:

- invent customer numbers without labeling them as assumptions;
- blur customer facts and directional assumptions;
- convert public strategic language into fake ROI;
- use earnings-call or public-company rhetoric as proof of company-specific business impact;
- use public statements to infer exact internal workflow owners unless supported;
- write generic hype language disconnected from customer value;
- hide missing data.

Always:

- anchor the case in customer business reality;
- make workflow explicit before use cases or seller solution fit;
- prioritize one to three value drivers when several could apply;
- distinguish known facts, inferences, assumptions, and missing evidence;
- say when the case is structural rather than finance-ready;
- show sources for key facts when available;
- tie use cases back to strategic priorities;
- explain caveats openly;
- keep the output auditable and decision-useful.

## Presentation Artifacts

If no presentation artifact is requested, ignore presentation styling and return strong plain Markdown.

If the user asks for a formatted artifact, load [references/output-and-presentation.md](references/output-and-presentation.md) and keep presentation rules subordinate to the workflow, evidence hierarchy, assumptions handling, value-model logic, and output content requirements.
