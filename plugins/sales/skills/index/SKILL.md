---
name: index
description: "Use to discover specific skills for the Sales plugin, when it is at-mentioned directly, or for any mentions of potentially relevant work, including: meeting prep or call follow-up; account research, monitoring, or prioritization; internal source finding; competitive briefs; deal strategy; pipeline or forecast review; company or contact enrichment; customer quote retrieval; rep coaching; business cases; sales company research; and CRM or data enrichment workflows."
---

# Skill Purpose

Route broad Sales requests to the right focused workflow. Treat invocation of this index as strong intent to use this plugin; default to loading and following any relevant focused skill for related sales work.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `sales:user-context` in preflight mode by loading `[$sales:user-context](../user-context/SKILL.md)` and running its preflight script before answering, searching connectors, retrieving evidence, or drafting output. Do not look for a callable MCP tool named `sales:user-context`. Use the returned `sales_preflight` envelope as authoritative for saved context, source-category mapping, final obligations, and conditional guidance. Do not read or reinterpret raw Sales state files unless preflight fails, local shell access is unavailable, or the user explicitly asks for raw state inspection.

Route direct context requests to `user-context` as the primary workflow. This includes remember/save/recall/inspect/customize/setup requests and broad future-facing instructions or corrections that may be reusable after Sales work. Route requests to run Sales Company Research, learn how the user's team sells from available company context, discover useful Sales resources, or fill missing company-context setup to `sales-company-research`; that skill uses `user-context` for save/update policy. Let `user-context` own direct state reads/writes, confirmation wording, action-oriented continuation, and successful-run learning; this index should only identify and route those cases.

### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details.

### Source Links

When referencing sources inline, prefer clickable Markdown links over plain bracket labels whenever the source exposes a useful URL. Use the source title, record name, channel/thread, or meeting/date as the link text, for example a clickable Markdown link whose visible text is `Meeting notes: May 19` or `Slack thread: May 15-21`. Use plain text labels only when no useful URL or stable connector-visible link is available, and say `(no useful link available)` when that absence matters.

### Broad Orientation And Help Requests

For broad orientation and help requests:

- Handle open-ended Sales asks from this index before choosing a focused workflow.
- Route requests such as `what can you do?`, `help`, `orient me`, `what should I try first?`, `how do I use Sales?`, setup-adjacent capability questions, and similar plugin-level requests here when the user needs orientation more than a specific artifact.
- Answer from the skill map in this file using the default shape below.
- Include concrete low-friction next prompts that start with `@Sales`, name the sales job, and use a realistic anchor.
- Include a short setup context section from the `sales_preflight.context.sources` envelope when any source category is not active, needs a user choice, was skipped, or is otherwise unresolved.
- Keep setup context seller-facing: name the practical source category, use model judgment to explain the likely user-experience impact from the category label, preferred apps, setup action, and suggested next prompts, then give the smallest next action or fallback.
- Show at most three highest-impact gaps by default, and never more than five setup-context bullets total. Prioritize gaps in the order most relevant to the examples you are suggesting rather than following a hard-coded impact catalog.
- If all categories are active, keep setup context to one sentence such as `Your core Sales sources look ready; I'll still try each source only when a workflow needs it.`
- When the current context or available sources identify a real meeting, call, account, deal, forecast, account list, customer question, or feedback theme, use the relevant focused skill's inline first-run and next-step guidance to make the suggested prompt contextual.
- For setup context wording, be direct and practical, for example: `You won't be able to properly use meeting follow-up until a transcript or meeting-notes provider is connected, but you can paste call notes or a transcript export for now.`
- Use static examples only when no suitable context is available.
- Do not expose raw status names, onboarding state fields, connector ids, or implementation terms.
- Do not perform connector reads merely to answer a capability question; use the preflight setup summary and any current session app/tool availability already visible in context.

Use this default answer shape for broad orientation and help requests:

```md
Sales can help with:
- Meeting prep and daily customer-meeting briefs
- Follow-up packages after calls, demos, or discovery notes
- Internal source-finding for customer questions and objections
- Deal strategy, account prioritization, forecast review, and account-signal briefs
- Competitive briefs, customer quote pulls, rep coaching, enrichment, and business cases

Setup context:
- {Only include when useful: source category readiness or gap plus practical impact}

Good first prompts:
- `@Sales prepare me for my next customer meeting.`
- `@Sales follow up from my latest customer call.`
- `@Sales prioritize my accounts for pipeline focus this week.`
```

### Routing And Skill Selection

If several focused skills apply, sequence them in the order that creates the most useful seller workflow. For example, meeting prep may precede deal strategy, and customer-call follow-up may feed a forecast or account-intelligence update. Keep this index as a router; do not perform focused workflow logic here.

Before finalizing future Sales instruction edits, run `python3 plugins/sales/skills/user-context/scripts/validate_user_context_preflight.py` from the repository root. Treat a missing mandatory pre-answer gate in any `SKILL.md`, including helper skills, as an audit finding to fix before release.

Prefer examples that route to focused skills without extra setup, such as:

```text
@Sales prepare me for my next customer meeting.
@Sales follow up from my latest customer call.
@Sales prioritize my accounts for pipeline focus this week.
```

For follow-up messages such as "yes", "walk me through it", "what happened?", or "show the steps" immediately after a completed guided workflow offers an agent-journey walkthrough, route to `user-context` and use `../user-context/references/onboarding.md#agent-journey-walkthrough`. Explain the observable steps, tool/app calls, retrievals, source gaps, and artifact assembly at a beginner-friendly level without revealing hidden reasoning.

# Plugin Purpose

Sales provides portable, evidence-grounded sales workflows for account research, competitive intelligence, meeting prep, deal strategy, pipeline and forecast review, customer follow-up, product-feedback evidence, internal navigation, business case, and rep coaching. It uses active workflow source categories such as CRM, calendar, meeting notes provider, external customer messaging, internal messaging, and document store tools when they can reduce manual input; pasted notes, uploaded files, exports, or public research remain supported fallback and enrichment paths.

# Skills

## analyze-account-signals

Build a single-account intelligence brief or ranked owner/watchlist summary from recent account signals. Route here for account views, account monitoring, "what changed with this customer?", or portfolio-watchlist requests. It is read-only and must not create tasks, post digests, or store schedule state.

## build-competitive-brief

Build multi-competitor competitive research, comparison matrices, and battlecard-style objection packages from user materials, optional connector-assisted research, and public evidence. Route here for vendor comparisons, market-landscape questions, competitive positioning, and objection preparation.

## follow-up-after-call

Turn a customer call transcript or grounded call notes into a seller-ready follow-up package with recap, next steps, follow-up email draft, CRM-ready note text, and internal recap draft. Route here after calls, discovery notes, demos, or transcript uploads.

## enrich-company-and-contact-data

Clean up sparse go-to-market inputs into sales-ready company lists, contact candidates, firmographic or technographic completion, segmentation, signal scans, and enrichment-backed comparison tables. Route here when the request is data-first rather than meeting, deal, forecast, narrative, or coaching-first. If the selected enrichment provider is ZoomInfo, also load `zoominfo` before provider-specific connector work.

## plan-deal-strategy

Build a post-discovery deal strategy pack with a deal map, buying committee map, procurement risk register, and prioritized next actions. Route here when the user needs to decide how to move an active deal forward from grounded deal evidence.

## hubspot

HubSpot connector guide for Sales workflows that use HubSpot as the selected `crm`. Route here only as a helper after another focused sales workflow has selected HubSpot, or when the user explicitly asks for Sales HubSpot CRM connector rules. Do not route here for non-HubSpot CRM use.

## find-key-internal-sources

Find the best internal experts, documents, and team-chat channels for a customer question, product topic, objection, implementation issue, account task, or other internal topic. Route here for "who knows about this?", "what should I read before answering this customer?", "where is the source of truth?", or "which internal channel/doc should I use?" sales-support requests.

## sales-company-research

Run explicit or scheduled Sales Company Research to discover durable internal resources, save high-confidence Sales plugin memory, and ask focused questions for missing links, access, or source-of-truth choices. Route here for company research, resource discovery, filling missing Sales context, recurring Sales Company Research automation runs, or broad questions about which company resources would materially improve future Sales workflows. Do not route ordinary customer questions or one-off owner/doc/channel lookup here; use `find-key-internal-sources` for those.

## prepare-for-meeting

Create concise customer meeting briefs, daily customer-meeting digests, and scheduled most-important meeting prep from invite context, prior interactions, account notes, likely objections, internal workstream context, and asset suggestions. Route here for upcoming customer meetings, daily customer-facing schedules, or recurring meeting prep automation runs that should prefer customer/account meetings when available and otherwise help with the day's most important qualifying meeting.

## suggest-sales-next-step

Run scheduled or manual Sales check-ins that summarize what the user has been doing with Sales, inspect timely calendar/source signals, and recommend one next Sales workflow to try, defaulting to an untried Sales workflow when no stronger context exists. Route here for recurring weekday sales check-in or daily check-in automation runs, manual "run my sales check-in" requests, plugin adoption reviews, or questions about how to get more value from Sales. Do not use this skill for ordinary sales artifacts; route those to the focused workflow that owns the artifact.

## prioritize-accounts

Prioritize rep-ready pipeline by ranking accounts, suppressing in-flight motion, selecting reachable contacts, and drafting planning-only action packages. Route here for "which accounts should I work now?", territory planning, pipeline creation, or ICP/account-list prioritization.

## find-customer-quotes

Retrieve theme-specific customer or prospect quotes from transcripts, call notes, or exported recordings with speaker-confidence and provenance rules. Route here for voice-of-customer quote pulls, theme validation, or product-friction evidence requests. If live transcript connectors are unavailable, use the skill's manual/export lane when the user supplies transcript or call-note material.

## review-forecast

Generate forecast reviews with risk analysis, recommendation posture, and change detection from CRM truth, account notes, and optional call or chat evidence. Route here for seller-book reviews, forecast risk checks, commit/pipeline hygiene, or deal-by-deal forecast recommendations.

## user-context

Preflight, manage, or answer from Sales plugin user context. Route here before Sales workflows to load saved context, and for direct remember, save, recall, inspect, setup, customization, context-maintenance, or approved Sales Company Research save requests. This skill owns Sales plugin-scoped user context and memory policy.

## salesforce

Salesforce connector guide for Sales workflows that use Salesforce as the selected `crm`. Route here only as a helper after another focused sales workflow has selected Salesforce, or when the user explicitly asks for Sales Salesforce CRM connector rules. Do not route here for non-Salesforce CRM use.

## get-rep-call-feedback

Compare one rep's call history against peer examples to extract repeatable best practices and evidence-backed coaching feedback. Route here for peer-benchmark coaching requests that name a target rep and peer set or ask to derive peer exemplars.

## review-rep-call-trends

Analyze one rep's recent calls over time to detect improvement, regression, and stable patterns with objective evidence and practical coaching actions. Route here for trend-oriented coaching, progress checks, or "how has this rep changed?" requests.

## build-business-case

Build customer-led business cases, ROI narratives, value models, executive summaries, customer-ready value stories, and follow-up question sets from uneven customer context, metrics, transcripts, notes, and public evidence. Route here when the user needs credible customer-value reasoning rather than generic positioning.

## zoominfo

ZoomInfo provider guide for Sales enrichment, company/contact research, lookalikes, contact recommendations, intent signals, and result-quality recovery. Route here only as a helper after `enrich-company-and-contact-data` or another focused workflow has selected ZoomInfo, or when the user explicitly asks for Sales ZoomInfo connector rules.
